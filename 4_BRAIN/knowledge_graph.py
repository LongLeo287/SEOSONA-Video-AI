# -*- coding: utf-8 -*-
"""SEOSONA's queryable knowledge graph — the "second brain" agents traverse instead of re-reading the
whole repo. Pattern harvested (REFERENCE-only) from Karpathy's "LLM Wiki" idea + tirth8205/code-review-graph
(claims 6.8-49x fewer tokens by giving an agent a local graph instead of re-scanning the codebase) — see
2_KNOWLEDGE/INGESTION_LOG.md 2026-07-01.

Reads `2_KNOWLEDGE/knowledge_graph.json` (built by `scripts/gen_knowledge_graph.py` — re-run that after
any structural change; this module is READ-ONLY, it never edits the graph).

  from knowledge_graph import find, neighbors, related_to, stats
  find("effect_library")                  # -> matching nodes (id, label, group)
  neighbors("b_effect_library")            # -> directly-connected nodes
  related_to("b_effect_library", depth=2)  # -> everything within 2 hops (what touches this, transitively)
  stats()                                  # -> counts per group

CLI:
  python 4_BRAIN/knowledge_graph.py find effect_library
  python 4_BRAIN/knowledge_graph.py neighbors b_effect_library
  python 4_BRAIN/knowledge_graph.py stats
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAPH_PATH = os.path.join(ROOT, "2_KNOWLEDGE", "knowledge_graph.json")
NOTES_PATH = os.path.join(ROOT, "2_KNOWLEDGE", "knowledge_notes.json")

_cache = None
_notes_cache = None


def _load():
    global _cache
    if _cache is None:
        if not os.path.exists(GRAPH_PATH):
            raise FileNotFoundError(
                f"{GRAPH_PATH} not found — run `python scripts/gen_knowledge_graph.py` first")
        _cache = json.load(open(GRAPH_PATH, encoding="utf-8"))
    return _cache


def reload():
    """Force a re-read from disk of BOTH graph + content notes
    (call after re-running gen_knowledge_graph.py / gen_knowledge_notes.py in a long-lived process)."""
    global _cache, _notes_cache
    _cache = None
    _notes_cache = None
    return _load()


def _adjacency(data):
    adj = {}
    for n in data["nodes"]:
        adj.setdefault(n["id"], set())
    for e in data["edges"]:
        adj.setdefault(e["from"], set()).add(e["to"])
        adj.setdefault(e["to"], set()).add(e["from"])
    return adj


def find(query, limit=20):
    """Substring search (case-insensitive) over node labels/ids. Returns matching node dicts."""
    data = _load()
    q = query.lower()
    hits = [n for n in data["nodes"] if q in n["label"].lower() or q in n["id"].lower()]
    return hits[:limit]


def get(node_id):
    """Fetch one node dict by id, or None."""
    data = _load()
    for n in data["nodes"]:
        if n["id"] == node_id:
            return n
    return None


def neighbors(node_id):
    """Direct (1-hop) neighbors of node_id. Returns node dicts."""
    data = _load()
    adj = _adjacency(data)
    by_id = {n["id"]: n for n in data["nodes"]}
    return [by_id[nb] for nb in adj.get(node_id, []) if nb in by_id]


def related_to(node_id, depth=2):
    """BFS out to `depth` hops from node_id — 'everything that touches this, transitively'.
    This is the practical query for 'what would be affected if I change X' or 'what feeds into X'."""
    data = _load()
    adj = _adjacency(data)
    by_id = {n["id"]: n for n in data["nodes"]}
    seen = {node_id}
    frontier = [node_id]
    for _ in range(depth):
        nxt = []
        for cur in frontier:
            for nb in adj.get(cur, []):
                if nb not in seen:
                    seen.add(nb)
                    nxt.append(nb)
        frontier = nxt
    seen.discard(node_id)
    return [by_id[i] for i in seen if i in by_id]


def subgraph(group):
    """All nodes belonging to a given group (e.g. 'sopVideo', 'skill', 'template', 'repoBacklog')."""
    data = _load()
    return [n for n in data["nodes"] if n["group"] == group]


def stats():
    """Counts per group + overall totals — a fast 'what does the system contain' snapshot."""
    data = _load()
    from collections import Counter
    counts = Counter(n["group"] for n in data["nodes"])
    return {"nodes": len(data["nodes"]), "edges": len(data["edges"]),
            "generated": data.get("meta", {}).get("generated"), "by_group": dict(counts)}


# ---------------------------------------------------------------- structural health (dreamgraph pattern)
_LEAF_GROUPS = {"sop", "sopVideo", "sopVoice", "sopRender", "sopLearning", "sopMaps", "sopPublish", "sopDesign",
                "sopInfra", "skill", "template", "component", "asset", "domainskill", "persona", "agent",
                "fxTransition", "fxTextEffect", "fxOverlay", "fxExit", "repoBuilt", "repoRef", "repoSkip",
                "repoRej", "repoBacklog", "repoOwn"}


def orphans():
    """Nodes with degree 0 — connected to NOTHING. Real bugs (a scan step forgot an edge) show up here;
    leaf-type nodes (SOP/skill/template/...) are EXPECTED to have exactly one edge (to their hub), so
    degree-0 among those is the actual anomaly to chase, not a false alarm."""
    data = _load()
    adj = _adjacency(data)
    return [n for n in data["nodes"] if not adj.get(n["id"])]


def dead_end_hubs():
    """AGGREGATING hubs (sopcat/repocat — groups that scan MULTIPLE items into one category) with too
    few children. NOTE: 'dir'/'brain'/'pipeline' nodes are legitimately single-edge by design (a plain
    brain module just links to d_4brain; only container modules like native_composer/effect_library
    have their own children) — only categories that are SUPPOSED to fan out are checked here, to avoid
    false-positive noise on nodes that are correctly leaf-like."""
    data = _load()
    adj = _adjacency(data)
    hub_groups = {"sopcat", "repocat"}
    return [n for n in data["nodes"] if n["group"] in hub_groups and len(adj.get(n["id"], [])) <= 1]


# ---------------------------------------------------------------- learned effect performance (accumulates
# over time from real renders — see 3_MEMORY / logs/metrics/events.jsonl; small-sample early on, honest
# about it rather than pretending confidence before there's enough data)
def effect_usage_stats(min_samples=3):
    """Cross-reference logs/metrics/events.jsonl render→quality pairs against which transitions were used
    (native_composer's `effects=` field, "name+name+...") to see which recipes correlate with higher
    quality scores. This is the 'system learns from its own knowledge' piece — accumulates as more videos
    render; HONEST about small samples (won't claim confidence below min_samples)."""
    events_path = os.path.join(ROOT, "logs", "metrics", "events.jsonl")
    if not os.path.exists(events_path):
        return {"note": "no events.jsonl yet — render some videos first", "effects": {}}
    events = [json.loads(l) for l in open(events_path, encoding="utf-8") if l.strip()]
    by_output = {}
    for e in events:
        out = e.get("output")
        if not out:
            continue
        by_output.setdefault(out, {})[e["event"]] = e
    from collections import defaultdict
    agg = defaultdict(list)
    n_with_effects = 0
    for out, evs in by_output.items():
        r, q = evs.get("render"), evs.get("quality")
        if not r or not r.get("effects") or not q:
            continue
        n_with_effects += 1
        for name in set(r["effects"].split("+")):
            agg[name].append(q.get("score"))
    result = {}
    for name, scores in agg.items():
        scores = [s for s in scores if s is not None]
        if not scores:
            continue
        result[name] = {"n": len(scores), "avg_score": round(sum(scores) / len(scores), 1),
                         "confident": len(scores) >= min_samples}
    return {"renders_with_effects_data": n_with_effects, "effects": result}


# ---------------------------------------------------------------- recall: answer FROM accumulated knowledge
# The "second brain" query — retrieve what SEOSONA has LEARNED about a topic (lessons + rationale, in our
# own words) instead of re-deriving it. Content notes are built by scripts/gen_knowledge_notes.py.
_WORD = None


def _tokens(s):
    global _WORD
    if _WORD is None:
        import re as _re
        _WORD = _re.compile(r'\w+', _re.UNICODE)
    # str(s or "") — a note with a null title/text, or a None query, must not AttributeError-crash all of
    # recall (one malformed note in the JSON would otherwise take the whole "check recall first" workflow down).
    return [t for t in _WORD.findall(str(s or "").lower()) if len(t) > 1]


def _load_notes():
    global _notes_cache
    if _notes_cache is None:
        if not os.path.exists(NOTES_PATH):
            raise FileNotFoundError(
                f"{NOTES_PATH} not found — run `python scripts/gen_knowledge_notes.py` first")
        _notes_cache = json.load(open(NOTES_PATH, encoding="utf-8"))
    return _notes_cache


def recall(query, limit=6, kind=None):
    """Retrieve accumulated SEOSONA knowledge relevant to `query` — the lessons + rationale we've built up
    (from INGESTION_LOG, VIDEO_CRAFT_RULES, domain_skills, SOPs, flywheel). Keyword-scored (title matches
    weigh 3x). Optional `kind` filter: lesson|craft|domain|sop|flywheel. Returns notes with a matched
    snippet + the structure-graph nodes each links to (so you get 'what we learned' + 'where it lives')."""
    data = _load_notes()
    qtoks = set(_tokens(query))
    if not qtoks:
        return []
    scored = []
    for note in data["notes"]:
        if kind and note.get("kind") != kind:
            continue
        title_toks = _tokens(note["title"])
        text_toks = _tokens(note["text"])
        score = sum(3 for t in title_toks if t in qtoks) + sum(1 for t in text_toks if t in qtoks)
        if score:
            scored.append((score, note))
    scored.sort(key=lambda kv: -kv[0])
    out = []
    for score, note in scored[:limit]:
        # snippet: window around the first query-token hit in the text
        low = note["text"].lower()
        pos = min([low.find(t) for t in qtoks if low.find(t) >= 0] or [0])
        snippet = note["text"][max(0, pos - 60):pos + 200].strip()
        out.append({"title": note["title"], "source": note["source"], "kind": note.get("kind"),
                    "verdict": note.get("verdict"), "links": note.get("links", []),
                    "score": score, "snippet": snippet})
    return out


def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "find":
        for n in find(sys.argv[2]):
            print(f"  {n['id']:32} [{n['group']:12}] {n['label']}")
    elif cmd == "neighbors":
        for n in neighbors(sys.argv[2]):
            print(f"  {n['id']:32} [{n['group']:12}] {n['label']}")
    elif cmd == "related":
        depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        for n in related_to(sys.argv[2], depth):
            print(f"  {n['id']:32} [{n['group']:12}] {n['label']}")
    elif cmd == "stats":
        s = stats()
        print(f"nodes={s['nodes']} edges={s['edges']} generated={s['generated']}")
        for g, c in sorted(s["by_group"].items(), key=lambda kv: -kv[1]):
            print(f"  {g:14} {c}")
    elif cmd == "orphans":
        o = orphans()
        print(f"{len(o)} orphan node(s) (degree 0):")
        for n in o:
            print(f"  {n['id']:32} [{n['group']:12}] {n['label']}")
    elif cmd == "health":
        o, d = orphans(), dead_end_hubs()
        print(f"orphans: {len(o)}  dead-end hubs: {len(d)}")
        for n in o:
            print(f"  ORPHAN     {n['id']:32} [{n['group']:12}] {n['label']}")
        for n in d:
            print(f"  DEAD-END   {n['id']:32} [{n['group']:12}] {n['label']}")
    elif cmd == "learned":
        r = effect_usage_stats()
        print(f"renders with effects data: {r.get('renders_with_effects_data', 0)}")
        for name, v in sorted(r["effects"].items(), key=lambda kv: -kv[1]["avg_score"]):
            flag = "" if v["confident"] else "  (few samples — not confident yet)"
            print(f"  {name:16} n={v['n']:3}  avg_score={v['avg_score']}{flag}")
    elif cmd == "recall":
        for r in recall(" ".join(sys.argv[2:])):
            links = ("  → " + ", ".join(r["links"])) if r["links"] else ""
            v = f" [{r['verdict']}]" if r.get("verdict") else ""
            print(f"• {r['title']}  ({r['source']}, {r['kind']}{v}, score {r['score']}){links}")
            print(f"    {r['snippet']}")
    else:
        print(f"unknown command: {cmd}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
