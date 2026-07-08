# -*- coding: utf-8 -*-
"""Data-defined pipeline graph — the factory's stages as DATA, not hardcoded call order.

Clean-room of the ONE durable idea from Dify's `api/core/workflow/` (INGESTION_LOG 2026-07-06,
REFERENCE): a typed node registry + topological-sort execution, so the production stages
(discover -> script -> render -> quality -> publish) are described as a rearrangeable graph
instead of a fixed sequence buried in code. No Dify code, no Flask, no Docker, no new deps —
~1 file of plain Python. Two payoffs:

  1. `default_pipeline().to_graph()` feeds the dashboard's Pipeline view (an interactive node
     graph of the OODA loop — the ReactFlow-canvas UX nugget from Sim, realized in our vis-network).
  2. `run(ctx, enable=...)` executes stages in dependency order, DELEGATING to the existing
     entrypoints (topic_to_video, workflow_router) — this is a thin orchestration description,
     NOT a reimplementation of the pipeline. render/publish are opt-in so a bare run is a dry plan.

    python 4_BRAIN/pipeline_dag.py graph            # emit vis-network {nodes,edges} JSON
    python 4_BRAIN/pipeline_dag.py list             # print the stage table (topo order)
    python 4_BRAIN/pipeline_dag.py run --seed AI --hot          # discover + write (dry, no render)
    python 4_BRAIN/pipeline_dag.py run --seed AI --hot --render  # + render the winning topic
"""
import os
import sys
import json
import datetime
import argparse
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# Where a run records its per-stage outcome, so the dashboard Pipeline view can show last-run status.
LAST_RUN_PATH = os.path.join(ROOT, "3_MEMORY", "pipeline_last_run.json")


def load_last_run():
    """The most recent run's per-stage status ({ts, seed, topic, status:{node:state}}), or {} if never run."""
    try:
        return json.load(open(LAST_RUN_PATH, encoding="utf-8"))
    except Exception:
        return {}


class Node:
    """One pipeline stage. `run(ctx)->dict` is optional: a node with no runner is descriptive-only
    (e.g. a sub-step that executes inside another stage) — it still appears in the graph."""
    def __init__(self, nid, title, kind, deps=None, run=None, note=""):
        self.id = nid
        self.title = title
        self.kind = kind                       # research | write | render | gate | publish
        self.deps = list(deps or [])
        self.run = run
        self.note = note


class Pipeline:
    def __init__(self, name):
        self.name = name
        self.nodes = {}                        # id -> Node (insertion-ordered)

    def add(self, node):
        if node.id in self.nodes:
            raise ValueError(f"duplicate node id: {node.id}")
        self.nodes[node.id] = node
        return self

    def topo_order(self):
        """Kahn topological sort. Raises on a missing dependency or a cycle (fail loud, don't guess)."""
        indeg = {nid: 0 for nid in self.nodes}
        for n in self.nodes.values():
            for d in n.deps:
                if d not in self.nodes:
                    raise ValueError(f"node '{n.id}' depends on unknown node '{d}'")
                indeg[n.id] += 1
        # ready = no unmet deps; keep insertion order among ready nodes for stable output
        ready = [nid for nid in self.nodes if indeg[nid] == 0]
        order = []
        while ready:
            nid = ready.pop(0)
            order.append(nid)
            for m in self.nodes.values():
                if nid in m.deps:
                    indeg[m.id] -= 1
                    if indeg[m.id] == 0:
                        ready.append(m.id)
        if len(order) != len(self.nodes):
            raise ValueError("pipeline has a cycle — cannot topo-sort")
        return [self.nodes[nid] for nid in order]

    def to_graph(self, with_status=True):
        """vis-network shape {nodes,edges} for the dashboard Pipeline view. Same contract as
        /api/graph so the frontend renderer is reused. When `with_status`, each node carries its
        LAST-RUN state (ok|skipped|error|descriptive|None) and the payload carries `last_run` meta."""
        last = load_last_run() if with_status else {}
        statuses = last.get("status", {})
        nodes = [{"id": n.id, "label": n.title, "kind": n.kind, "note": n.note,
                  "runnable": n.run is not None, "status": statuses.get(n.id)}
                 for n in self.topo_order()]
        edges = [{"from": d, "to": n.id} for n in self.nodes.values() for d in n.deps]
        out = {"nodes": nodes, "edges": edges, "name": self.name}
        if with_status and last:
            out["last_run"] = {k: last.get(k) for k in ("ts", "seed", "topic")}
        return out

    def run(self, ctx=None, enable=None):
        """Execute stages in dependency order. `enable` = set of node ids allowed to actually run
        (default: everything that has a runner). A disabled or runner-less node is SKIPPED, not faked.
        Each runner returns a dict merged into the shared ctx. Records per-node status in ctx['_status']."""
        ctx = dict(ctx or {})
        status = ctx.setdefault("_status", {})
        for n in self.topo_order():
            if n.run is None:
                status[n.id] = "descriptive"
                continue
            if enable is not None and n.id not in enable:
                status[n.id] = "skipped"
                continue
            try:
                out = n.run(ctx) or {}
                ctx.update(out)
                status[n.id] = "ok"
            except Exception as e:                 # one stage failing stops the chain, honestly
                status[n.id] = f"error: {e}"
                print(f"[pipeline] stage '{n.id}' failed: {e}")
                break
        self._record_run(ctx)
        return ctx

    def _record_run(self, ctx):
        """Persist this run's per-stage outcome for the dashboard. Best-effort — never breaks a run."""
        rec = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
               "seed": ctx.get("seed"), "topic": ctx.get("topic"),
               "status": ctx.get("_status", {})}
        try:
            os.makedirs(os.path.dirname(LAST_RUN_PATH), exist_ok=True)
            json.dump(rec, open(LAST_RUN_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[pipeline] last-run not saved ({e})")


# ---------------------------------------------------------------- stage executors (DELEGATE, don't reimplement)
def _discover(ctx):
    """Pick the winning demand/recency topic via the existing front-of-loop (topic_to_video.pick_topics)."""
    tv = import_module("topic_to_video")
    topics = tv.pick_topics(ctx.get("seed", "AI"), n=1, hot=ctx.get("hot", False), days=ctx.get("days", 30))
    topic = topics[0] if topics else ctx.get("seed", "AI")
    print(f"[pipeline] discover -> {topic!r}")
    return {"topic": topic}


def _script(ctx):
    """Grounded script pipeline (fetch->analyze->reason->plan->write->verify) via topic_to_video."""
    tv = import_module("topic_to_video")
    text, vr = tv.topic_to_script(ctx["topic"], n_scenes=ctx.get("scenes", 7))
    if not text:
        raise RuntimeError("no script — real LLM unavailable (skipping, not fabricating)")
    print(f"[pipeline] script -> {len(text.split())} words (verify {'ok' if vr.ok else 'warn'})")
    return {"narration": text, "verify_ok": bool(getattr(vr, "ok", False))}


def _render(ctx):
    """Hand the narration to the normal render route (which also runs the quality gate internally)."""
    slug = import_module("topic_to_video")._slug(ctx["topic"])
    import_module("workflow_router").route(ctx["narration"], brand="seosona",
                                           aspect_ratio=ctx.get("aspect", "9:16"), project_name=slug)
    return {"rendered": slug}


def _publish(ctx):
    """Opt-in publish dispatch. Left as a thin hook — dry by default, real dispatch when wired up."""
    print(f"[pipeline] publish (dry) -> {ctx.get('rendered')}")
    return {"published": False}


def default_pipeline():
    """The canonical SEOSONA production line, described as data. Reorder/insert stages HERE and both
    the runner and the dashboard graph follow — nothing else to touch."""
    p = Pipeline("seosona-production")
    p.add(Node("discover", "Discover topic", "research", run=_discover,
               note="demand + recency (HackerNews/GitHub/arXiv, on-domain) -> one grounded topic"))
    p.add(Node("script", "Write grounded script", "write", deps=["discover"], run=_script,
               note="fetch->analyze->reason->plan->write->verify; traceability gate, no fabricated numbers"))
    p.add(Node("render", "Render video", "render", deps=["script"], run=_render,
               note="workflow_router.route -> native_composer (HTML+GSAP -> mp4)"))
    p.add(Node("quality", "Quality gate", "gate", deps=["render"],
               note="runs INSIDE render: scores the mp4, records post-mortem on fail (eval flywheel)"))
    p.add(Node("publish", "Publish", "publish", deps=["quality"], run=_publish,
               note="dispatch to platforms with CC-BY credits (opt-in)"))
    return p


def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["graph", "list", "run"])
    ap.add_argument("--seed", default="AI")
    ap.add_argument("--hot", action="store_true")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--scenes", type=int, default=7)
    ap.add_argument("--render", action="store_true", help="actually render the winning topic")
    ap.add_argument("--publish", action="store_true", help="also run the publish stage")
    a = ap.parse_args()
    p = default_pipeline()

    if a.cmd == "graph":
        print(json.dumps(p.to_graph(), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "list":
        print(f"pipeline: {p.name}  ({len(p.nodes)} stages, topo order)")
        for n in p.topo_order():
            dep = (" <- " + ", ".join(n.deps)) if n.deps else ""
            run = "run" if n.run else "descriptive"
            print(f"  [{n.kind:8}] {n.id:9} {run:11}{dep}")
            print(f"             {n.note}")
        return 0
    # run
    enable = {"discover", "script"}
    if a.render:
        enable |= {"render"}
    if a.publish:
        enable |= {"render", "publish"}
    ctx = p.run({"seed": a.seed, "hot": a.hot, "days": a.days, "scenes": a.scenes}, enable=enable)
    print("\n[pipeline] status:")
    for nid, st in ctx["_status"].items():
        print(f"  {nid:9} {st}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
