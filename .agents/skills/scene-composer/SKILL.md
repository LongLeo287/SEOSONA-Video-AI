---
name: scene-composer
description: >
  Turn a topic / GitHub repo / news brief into `content` for a SEOSONA video template
  (ADAPT mode). Use when the user wants to auto-make a faceless video from a topic and
  there's a chosen template. Pairs with 4_BRAIN/scene_composer.py + native_composer.
metadata:
  type: skill
  author: SEOSONA AI
  version: "1.0"
---

# Scene-Composer — topic → content (fill a template)

You are the **content brain** of the SEOSONA video factory. Given a topic and a chosen
template, you produce a `content` dict that `native_composer.make_video_from_template`
renders into a finished SEOSONA video. You write the CREATIVE parts; the helper fetches
the REAL data so numbers are never invented.

## 🔴 FOLLOW THE ONE RULEBOOK (do not write from memory)
You are **path A** of the unified script pipeline (`6_SOP/SCRIPT_WRITING_PIPELINE.md`). Write to the
SAME rules as every automated path — do not improvise your own:
1. **Rules** = `9_PROMPTS/MASTER_VIDEO_SPEC.md` (arc, hard rules, how-to-write). Read it before writing.
2. **Craft** = `2_KNOWLEDGE/domain_skills/{copywriting, ogilvy, stop-slop, seo-audit, content-strategy}`
   (Ogilvy hook, anti-AI-slop, SEO intent). Apply the knowledge; don't invent your own rules.
3. **Grounding** = only state numbers/names that come from the REAL fetched data. No fabrication.
4. **VERIFY before render** — run `script_writer.verify(script, script_writer.analyze(script_writer.fetch(url)))`
   and fix any fabricated number/name or repeated line it reports (see the SOP for the one-liner).

## Inputs
- A **topic/brief**: a GitHub repo URL, a news story, a tool, a concept.
- A **template name** (`native_composer.list_templates()` — e.g. `repo-showcase`,
  `tutorial-gittree`). Load it: `load_template(name)` → its scene structure
  (each scene's `component` type + `accent` + `kicker_hint`).

## Steps
1. **Get real data (deterministic).** For a GitHub repo:
   `from scene_composer import fetch_github, repo_data_slots`
   `gh = fetch_github("owner/name")` → real stars/desc/lang/license/topics.
   `slots = repo_data_slots(gh)` → ready-made data for the `repo`, ★ `bignum`, `badges` scenes.
   NEVER hand-type star counts — use the fetched value.
2. **Write the script + headings (creative).** One `segment` per scene (Vietnamese,
   DISPLAY form — write "SEO", "GitHub", "24/7" correctly; add pronunciations to `lexicon`,
   SOP RULE #1). One 2-tone `heading` (h1, h2) per scene. Length: a hook first, a CTA last,
   ~8 scenes / ~30s (scale to the template).
3. **Fill the data components.** For each scene whose template `component` needs data:
   - `repo` → `slots["repo"]`, ★ `bignum` → `slots["stars_bignum"]`, `badges` → `{"items": slots["badges"]}`
   - `terminal` → real install/usage commands `{"title": "~/x", "lines": [("$","..."),("ok","...")]}`
   - `compare` → `{"left": (title,[points]), "right": (title,[points])}` (right = the winner)
   - `steps` → `{"items": [(title, sub), ...]}` ; `bignum` hook → `{"big": "...", "label": "..."}`
   - `gittree` → `{commits, edges, branches, head}` (for git/visual tools)
4. **Compose + render.**
   `content = compose(template, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)`
   `make_video_from_template(template, content, project_dir, output=...)`

## Rules
- **RULE #1**: captions/text = display form; pronunciations go in `lexicon` only.
- **Real data only** — fetch it; do not invent stars/dates/numbers.
- **Voice/brand are automatic** — locked VieNeu voice + SEOSONA chrome; don't set them.
- **Pick the template by topic**: repo/tool → `repo-showcase`; visual/learn tool → `tutorial-gittree`.
  For variety across a batch, ROTATE templates so videos don't look repetitive.
- Hook in scene 0 must be full at frame 0 (the engine handles it); make it punchy.

## Worked example
`8_WORKSPACE/demo_localai.py` — `mudler/LocalAI` (47k★, MIT, Go) → `repo-showcase`
template → `LocalAI - SEOSONA.mp4`. Real stars fetched; script/headings/terminal/compare authored.

## Automated path (no hand-authoring)
For a one-command draft (or a news batch), use `4_BRAIN/make_video.py` — it
fetches real data, auto-classifies the repo → template (+theme by topic), fills
every data slot with REAL data, and writes templated Vietnamese prose:

    python 4_BRAIN/make_video.py https://github.com/owner/name      # one video
    python 4_BRAIN/make_video.py --news 8_WORKSPACE/news_urls.txt   # batch, rotates templates

Use this for speed/scale; hand-author (the steps above) when you want richer prose.
The auto prose is an honest draft — it never invents numbers (only name/desc/stars/
lang/license/topics) — so you can render first, then refine the segments.
