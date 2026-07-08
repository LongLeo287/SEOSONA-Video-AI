# -*- coding: utf-8 -*-
"""Extract SEOSONA's accumulated KNOWLEDGE (not just structure) into queryable notes — the content half
of the "second brain". Complements `gen_knowledge_graph.py` (which maps STRUCTURE: what modules/SOPs/
skills exist) by capturing WHAT WE'VE LEARNED and WHY, in SEOSONA's own words, so an agent can `recall`
accumulated knowledge instead of re-deriving it.

Pattern: the Karpathy "LLM Wiki" / Obsidian second-brain idea (INGESTION_LOG.md 2026-07-01) — the goal
isn't to STORE notes, it's to make them a system the AI reads/links/answers-from. Sources parsed:
  • 2_KNOWLEDGE/INGESTION_LOG.md   — one lesson per repo (what learned · where built · why + verdict)
  • 2_KNOWLEDGE/VIDEO_CRAFT_RULES.md — one note per craft section (§1-9)
  • 2_KNOWLEDGE/domain_skills/*/SKILL.md — one note per domain skill (SEO/copywriting/design…)
  • 6_SOP/*.md                      — one note per SOP (its purpose = first real paragraph)
  • 3_MEMORY/HOT_LEARNINGS.md       — flywheel learnings

Each note carries `links` = structure-graph node ids it relates to (parsed from file paths in the log's
"Where" column), connecting the CONTENT brain to the STRUCTURE brain. No heavy deps — plain text + a
query-time keyword scorer in `4_BRAIN/knowledge_graph.recall()` (right size for a few-hundred-note vault;
a vector DB would be bloat here).

  python scripts/gen_knowledge_notes.py    ->  2_KNOWLEDGE/knowledge_notes.json
"""
import ast
import glob
import json
import os
import re
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "2_KNOWLEDGE", "knowledge_notes.json")

notes = []


def _links_from_paths(text):
    """Map file paths mentioned in text to structure-graph node ids (connects content <-> structure).
    ONLY emit ids that actually EXIST as graph nodes: 4_BRAIN modules (b_), SOPs (sop_), skills (sk_).
    scripts/*.py are NOT graph nodes (the graph only nodes 4_BRAIN modules) — do not fabricate b_ ids
    for them (that produced dangling links caught by knowledge_audit)."""
    links = []
    for m in re.finditer(r'4_BRAIN/([a-z0-9_]+)\.py', text):
        links.append("b_" + m.group(1))
    for m in re.finditer(r'6_SOP/([A-Za-z0-9_]+)\.md', text):
        links.append("sop_" + m.group(1))
    for m in re.finditer(r'\.agents/skills/([a-z0-9-]+)', text):
        links.append("sk_" + m.group(1))
    for m in re.finditer(r'2_SKILLS/([a-z0-9_]+)/', text):      # 2_SKILLS packages → sm_ graph nodes
        links.append("sm_" + m.group(1))
    return sorted(set(links))


def _add(note_id, source, title, text, kind, **extra):
    text = re.sub(r'\s+', ' ', text).strip()
    # normalize title too: collapse any whitespace incl. stray control chars (e.g. \v from mangled paths)
    title = re.sub(r'\s+', ' ', str(title or '')).strip()
    if not text:
        return
    notes.append({"id": note_id, "source": source, "title": title, "text": text[:1200],
                  "kind": kind, "links": _links_from_paths(text), **extra})


# ---------------------------------------------------------------- INGESTION_LOG (the richest lessons)
def parse_ingestion_log():
    path = os.path.join(ROOT, "2_KNOWLEDGE", "INGESTION_LOG.md")
    if not os.path.exists(path):
        return 0
    n, in_rejected = 0, False
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## Rejected"):
            in_rejected = True
            continue
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if in_rejected:
            if len(cells) >= 2 and cells[0] != "Source":
                src = re.sub(r'\*|`', '', cells[0])
                _add(f"kn_rej_{n}", "INGESTION_LOG", src, f"REJECTED: {cells[1]}", "lesson", verdict="REJECTED")
                n += 1
        elif len(cells) >= 6 and cells[1] != "Source":
            src = re.sub(r'\*|`', '', cells[1])
            what, where, why = cells[3], cells[4], cells[5]
            w = what.upper()
            verdict = ("BUILT" if ("ADOPTED" in w or "BUILT" in w or "ADOPT-PATTERN" in w)
                       else "SKIP" if "SKIP" in w else "REFERENCE")
            # cell[0] is the ingestion date (YYYY-MM-DD) — keep it so recall can cite {source,title,date},
            # the chunk-provenance idea harvested from anything-llm (traceable knowledge, no fabricated claims).
            dm = re.match(r'\d{4}-\d{2}-\d{2}', cells[0])
            extra = {"verdict": verdict}
            if dm:
                extra["date"] = dm.group(0)
            _add(f"kn_log_{n}", "INGESTION_LOG", src, f"{what} — WHY: {why} — WHERE: {where}",
                 "lesson", **extra)
            n += 1
    return n


# ---------------------------------------------------------------- VIDEO_CRAFT_RULES (craft sections)
def parse_craft_rules():
    path = os.path.join(ROOT, "2_KNOWLEDGE", "VIDEO_CRAFT_RULES.md")
    if not os.path.exists(path):
        return 0
    text = open(path, encoding="utf-8").read()
    parts = re.split(r'\n## ', text)
    n = 0
    for part in parts[1:]:
        head, _, body = part.partition("\n")
        head = head.strip()
        if head.lower().startswith("status"):
            continue
        _add(f"kn_craft_{n}", "VIDEO_CRAFT_RULES", head, body, "craft")
        n += 1
    return n


# ---------------------------------------------------------------- domain_skills (SEO/copy/design knowledge)
def parse_domain_skills():
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "2_KNOWLEDGE", "domain_skills", "*", "SKILL.md"))):
        skill = os.path.basename(os.path.dirname(path))
        raw = open(path, encoding="utf-8").read()
        # pull description from frontmatter if present, else first paragraph after it
        desc = ""
        fm = re.search(r'description:\s*>?\s*(.+?)(?:\n[a-z_]+:|\n---)', raw, re.S)
        if fm:
            desc = fm.group(1)
        body = raw.split("---", 2)[-1] if raw.startswith("---") else raw
        _add(f"kn_dk_{n}", "domain_skills", skill, (desc + " " + body[:600]), "domain")
        n += 1
    return n


# ---------------------------------------------------------------- SOPs (purpose = first real paragraph)
def parse_sops():
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "6_SOP", "*.md"))):
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.upper() == "README":
            continue
        raw = open(path, encoding="utf-8").read()
        # first non-empty, non-heading paragraph
        purpose = ""
        for para in re.split(r'\n\s*\n', raw):
            p = para.strip()
            if p and not p.startswith("#") and not p.startswith("|") and not p.startswith(">"):
                purpose = p
                break
        title_m = re.search(r'^#\s+(.+)', raw, re.M)
        title = title_m.group(1).strip() if title_m else stem
        _add(f"kn_sop_{stem}", "6_SOP/" + stem, title, purpose or title, "sop",
             links=[f"sop_{stem}"])
        n += 1
    return n


# ---------------------------------------------------------------- HOT_LEARNINGS (flywheel)
def parse_hot_learnings():
    path = os.path.join(ROOT, "3_MEMORY", "HOT_LEARNINGS.md")
    if not os.path.exists(path):
        return 0
    raw = open(path, encoding="utf-8").read()
    _add("kn_hot", "HOT_LEARNINGS", "Factory self-learned (flywheel)", raw, "flywheel")
    return 1


def scan_module_docstrings():
    """One note per code MODULE = its top-of-file docstring (the 'what + why' rationale we write there),
    so the factory's OWN engineering reasoning is recall-able — e.g. `recall "why not Katna"` surfaces
    frame_scorer's note. Covers 4_BRAIN/*.py (→ b_<name>) and 2_SKILLS/*/*.py (→ sm_<package>)."""
    paths = glob.glob(os.path.join(ROOT, "4_BRAIN", "*.py")) + \
        glob.glob(os.path.join(ROOT, "2_SKILLS", "*", "*.py"))
    n = 0
    for path in sorted(paths):
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.startswith("_"):                              # skip dunder/private helper files
            continue
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        try:
            doc = ast.get_docstring(ast.parse(open(path, encoding="utf-8").read()))
        except Exception:
            doc = None
        if not doc or len(doc.strip()) < 60:                  # skip thin/absent docstrings
            continue
        _add("mod_" + rel.replace("/", "_").replace(".py", ""), rel, stem,
             f"Module {rel}. " + doc, "module")
        n += 1
    return n


def main():
    n_log = parse_ingestion_log()
    n_craft = parse_craft_rules()
    n_dk = parse_domain_skills()
    n_sop = parse_sops()
    n_hot = parse_hot_learnings()
    n_mod = scan_module_docstrings()
    out = {"notes": notes,
           "meta": {"generated": datetime.now().isoformat(timespec="seconds"), "count": len(notes)}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[gen_knowledge_notes] {len(notes)} notes -> {OUT}")
    print(f"  ingestion-lessons:{n_log}  craft:{n_craft}  domain-skills:{n_dk}  sops:{n_sop}  "
          f"flywheel:{n_hot}  modules:{n_mod}")


if __name__ == "__main__":
    main()
