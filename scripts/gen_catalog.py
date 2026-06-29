# -*- coding: utf-8 -*-
import json, glob, os
os.chdir(r"D:\SEOSONA AI\SEOSONA Video")
files = sorted(glob.glob("7_ASSETS/templates/*.json"))
L = []
A = L.append
A("# Template Catalog (HyperFrames · renderer: native_composer)")
A("")
A("Auto-generated from `7_ASSETS/templates/*.json` (regen: `python scripts/gen_catalog.py`).")
A("Each template is a scene sequence; the template owns visual design — you only write")
A("text (`segments` + 2-tone `headings`). Content is validated by `4_BRAIN/script_schema.py`")
A("before render.")
A("")
A("> **RULE #1**: on-screen text (`h1`/`h2`/`kicker`) keeps formatting (\"5.5\", \"82%\") and")
A("> may use 0–1 emoji; the spoken `segments` (voiceText) must be CLEAN — no emoji / URL /")
A("> `→ % $ #`. Numbers in voiceText are spelled out (handled by news_video_standards).")
A("")
A("## Char budgets (poster discipline — checked as warnings)")
A("")
A("| Field | Budget | Note |")
A("|---|---|---|")
A("| `kicker` | ≤24 chars | small uppercase pill label |")
A("| `h1` | ≤24 chars | heading line 1 — punchy |")
A("| `h2` | ≤24 chars | the accent-highlighted word/phrase |")
A("| each `segment` | ≤45 words | one idea per scene; longer → split into more scenes |")
A("")
A("## Templates (%d)" % len(files))
A("")
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    sc = d.get("scenes", [])
    comps = [(s.get("component") or "—") for s in sc]
    A("### `%s`" % d.get("name", os.path.basename(f)))
    desc = (d.get("description") or d.get("when_to_use") or "").strip()
    if desc:
        A("*%s*" % desc)
    A("")
    A("- **aspect:** %s · **scenes:** %d · **theme:** %s"
      % (d.get("aspect", "9:16"), len(sc), d.get("theme", "light")))
    A("- **scene flow:** %s" % " → ".join(comps))
    accents = list(dict.fromkeys([s.get("accent") for s in sc if s.get("accent")]))
    if accents:
        A("- **accents:** %s" % ", ".join(accents))
    A("")
open("7_ASSETS/templates/CATALOG.md", "w", encoding="utf-8").write("\n".join(L))
print("CATALOG.md written:", len(files), "templates,", sum(len(x) for x in L), "chars")
