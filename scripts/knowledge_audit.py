# -*- coding: utf-8 -*-
"""Knowledge-graph INTEGRITY AUDIT — use the second brain to find what's broken/missing/duplicate/stale.

The payoff of having a knowledge graph + content notes (gen_knowledge_graph.py / gen_knowledge_notes.py):
we can now MECHANICALLY detect the rot a growing system accumulates — broken links, disconnected nodes,
undocumented code, overlapping docs, stale files. Runs against the live repo + the generated graph/notes.

Checks (each conservative — explained so a finding is actionable, not noise):
  1. BROKEN PATH REFS   — a doc points to a file/module path that no longer exists on disk (doc drift)
  2. BROKEN GRAPH LINKS — a content note links to a structure-node id that isn't in the graph
  3. ORPHAN NODES       — graph nodes connected to nothing (a scan step missed an edge)
  4. UNDOCUMENTED CODE  — a 4_BRAIN module never mentioned in any SOP / note / doc
  5. OVERLAP / DUPLICATE— pairs of knowledge notes with high token overlap (candidate merge/dedupe)
  6. STALE FILES        — knowledge/SOP files untouched for > N days (informational)

  python scripts/knowledge_audit.py                 # full report
  python scripts/knowledge_audit.py --strict        # exit 1 if any BROKEN finding (for CI)
  python scripts/knowledge_audit.py --stale-days 45
Writes 3_MEMORY/knowledge_audit.json for agents (factory_brain / capability-analyst) to read.
"""
import argparse
import glob
import json
import os
import re
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAPH = os.path.join(ROOT, "2_KNOWLEDGE", "knowledge_graph.json")
NOTES = os.path.join(ROOT, "2_KNOWLEDGE", "knowledge_notes.json")
OUT = os.path.join(ROOT, "3_MEMORY", "knowledge_audit.json")

# Dirs whose .md we treat as SEOSONA-authored (skip ingested external repos — their paths aren't ours).
DOC_GLOBS = ["6_SOP/*.md", "2_KNOWLEDGE/*.md", "docs/*.md", ".agents/skills/*/SKILL.md",
             "*.md", "1_AGENTS/*.md", "1_AGENTS/personas/*.md"]
# Internal path patterns that should resolve to a real file on disk. Require a REAL file extension
# (avoids catching method calls like `native_composer.make_video` as a "path.make" false positive).
_EXT = r'(?:py|md|json|jsonl|js|cjs|mjs|ts|tsx|html|css|yaml|yml|txt|png|jpg|svg|wav|mp3|mp4|ps1|xlsx|csv)'
PATH_RE = re.compile(
    r'(?<![\w./])((?:0_SETUP|0_INPUT_INBOX|1_AGENTS|1_CONFIG|2_KNOWLEDGE|2_SKILLS|3_MEMORY|4_BRAIN|'
    r'5_FRAMEWORK|6_SOP|7_ASSETS|8_WORKSPACE|9_DASHBOARD|9_PROMPTS|scripts|docs)/[\w./-]+\.' + _EXT + r')\b')

# Paths legitimately not on disk — NOT drift (don't flag):
#  • 1_CONFIG/credentials/*.json — gitignored secrets (only .example.* committed)
#  • 2_KNOWLEDGE/repos/*.md       — repo-digest notes decluttered to archive (see INGESTION_INDEX header)
#  • 8_WORKSPACE/*                — per-render transient output, not committed
def _expected_missing(p):
    if "1_CONFIG/credentials/" in p and not p.endswith(".example.json"):
        return True
    if p.startswith("2_KNOWLEDGE/repos/"):
        return True
    if p.startswith("8_WORKSPACE/"):
        return True
    if re.match(r"3_MEMORY/[\w./-]+\.jsonl$", p):        # runtime append-logs (studio_jobs/metrics/angles) — created on first run, not drift
        return True
    return False


def _placeholder(p):
    return any(c in p for c in "<>*{}") or "..." in p or p.endswith("/")


def _docs():
    seen = set()
    for g in DOC_GLOBS:
        for path in glob.glob(os.path.join(ROOT, g)):
            rp = os.path.relpath(path, ROOT)
            if rp in seen:
                continue
            seen.add(rp)
            yield path, rp


def check_broken_path_refs():
    """Docs that reference an internal file path which doesn't exist (drift after rename/delete)."""
    findings = []
    for path, rel in _docs():
        try:
            text = open(path, encoding="utf-8").read()
        except Exception:
            continue
        for m in set(PATH_RE.findall(text)):
            p = m.strip("`").rstrip(".,;:)")
            if _placeholder(p) or _expected_missing(p):
                continue
            if not os.path.exists(os.path.join(ROOT, p)):
                # skill-doc refs = ingested skills' OWN toolchain scripts (heygen/hyperframes/etc),
                # never SEOSONA files → separate them from core-doc drift so the count is honest.
                findings.append({"doc": rel, "missing_path": p,
                                 "skill_doc": rel.replace("\\", "/").startswith(".agents/skills")})
    return findings


def check_broken_graph_links(graph, notes):
    node_ids = {n["id"] for n in graph["nodes"]}
    findings = []
    for note in notes["notes"]:
        for link in note.get("links", []):
            if link not in node_ids:
                findings.append({"note": note["title"][:60], "source": note["source"], "dangling_link": link})
    return findings


def check_orphans(graph):
    adj = {n["id"]: 0 for n in graph["nodes"]}
    for e in graph["edges"]:
        adj[e["from"]] = adj.get(e["from"], 0) + 1
        adj[e["to"]] = adj.get(e["to"], 0) + 1
    by_id = {n["id"]: n for n in graph["nodes"]}
    return [{"id": nid, "label": by_id[nid]["label"], "group": by_id[nid]["group"]}
            for nid, deg in adj.items() if deg == 0 and nid in by_id]


def check_undocumented_modules():
    """4_BRAIN modules whose name never appears in any SEOSONA doc — nobody documents them."""
    corpus = ""
    for path, _ in _docs():
        try:
            corpus += open(path, encoding="utf-8").read().lower()
        except Exception:
            pass
    findings = []
    for p in sorted(glob.glob(os.path.join(ROOT, "4_BRAIN", "*.py"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        if stem.startswith("_"):
            continue
        if stem.lower() not in corpus:
            findings.append({"module": f"4_BRAIN/{stem}.py"})
    return findings


def _tok(s):
    return set(t for t in re.findall(r'\w+', s.lower()) if len(t) > 3)


def check_overlap(notes, threshold=0.55):
    """Note pairs with high Jaccard token overlap — candidate duplicates/overlapping coverage."""
    items = [(n["title"], n["source"], n.get("kind"), _tok(n["title"] + " " + n["text"])) for n in notes["notes"]]
    findings = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][3], items[j][3]
            if len(a) < 6 or len(b) < 6:
                continue
            inter = len(a & b)
            union = len(a | b)
            if union and inter / union >= threshold:
                findings.append({"a": f"{items[i][0][:40]} ({items[i][1]})",
                                 "b": f"{items[j][0][:40]} ({items[j][1]})",
                                 "similarity": round(inter / union, 2)})
    findings.sort(key=lambda f: -f["similarity"])
    return findings


def check_stale(stale_days):
    cutoff = time.time() - stale_days * 86400
    findings = []
    for g in ["6_SOP/*.md", "2_KNOWLEDGE/*.md", ".agents/skills/*/SKILL.md"]:
        for path in glob.glob(os.path.join(ROOT, g)):
            try:
                mt = os.path.getmtime(path)
            except Exception:
                continue
            if mt < cutoff:
                days = int((time.time() - mt) / 86400)
                findings.append({"file": os.path.relpath(path, ROOT), "age_days": days})
    findings.sort(key=lambda f: -f["age_days"])
    return findings


def main():
    ap = argparse.ArgumentParser(description="Audit the SEOSONA knowledge graph for rot")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any BROKEN finding")
    ap.add_argument("--stale-days", type=int, default=60)
    a = ap.parse_args()

    if not os.path.exists(GRAPH) or not os.path.exists(NOTES):
        print("[audit] graph/notes not built — run `npm run graph:gen && npm run graph:notes` first")
        return 1
    graph = json.load(open(GRAPH, encoding="utf-8"))
    notes = json.load(open(NOTES, encoding="utf-8"))

    report = {
        "broken_path_refs": check_broken_path_refs(),
        "broken_graph_links": check_broken_graph_links(graph, notes),
        "orphan_nodes": check_orphans(graph),
        "undocumented_modules": check_undocumented_modules(),
        "overlap_pairs": check_overlap(notes),
        "stale_files": check_stale(a.stale_days),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    core_refs = [f for f in report["broken_path_refs"] if not f.get("skill_doc")]
    skill_refs = [f for f in report["broken_path_refs"] if f.get("skill_doc")]
    broken = len(core_refs) + len(report["broken_graph_links"]) + len(report["orphan_nodes"])
    print("=" * 66)
    print("  KNOWLEDGE GRAPH AUDIT — system integrity")
    print("=" * 66)
    print(f"  BROKEN core-doc refs  : {len(core_refs)}  (SEOSONA docs → missing file = real drift)")
    for f in core_refs[:25]:
        print(f"      ✗ {f['doc']}  →  {f['missing_path']}")
    print(f"  Ingested-skill refs   : {len(skill_refs)}  (skills' own toolchain scripts, not SEOSONA — info)")
    print(f"  BROKEN graph links    : {len(report['broken_graph_links'])}")
    for f in report["broken_graph_links"][:15]:
        print(f"      ✗ {f['source']}: {f['dangling_link']}  ({f['note']})")
    print(f"  ORPHAN nodes          : {len(report['orphan_nodes'])}")
    for f in report["orphan_nodes"][:15]:
        print(f"      ✗ {f['id']} [{f['group']}]")
    print(f"  UNDOCUMENTED modules  : {len(report['undocumented_modules'])}")
    for f in report["undocumented_modules"][:20]:
        print(f"      · {f['module']}")
    print(f"  OVERLAP / dup pairs   : {len(report['overlap_pairs'])}")
    for f in report["overlap_pairs"][:12]:
        print(f"      ~ {f['similarity']}  {f['a']}  ≈  {f['b']}")
    print(f"  STALE files (>{a.stale_days}d)   : {len(report['stale_files'])}")
    for f in report["stale_files"][:10]:
        print(f"      · {f['age_days']}d  {f['file']}")
    print("=" * 66)
    print(f"  → {OUT}")
    if a.strict and broken:
        print(f"[audit] STRICT: {broken} broken finding(s) → exit 1")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
