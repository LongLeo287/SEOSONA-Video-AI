---
name: seedance-prompt-director
description: >
  Turn a script, scene idea, or beat list into Seedance 2.0 cinematic AI-video prompts — standalone
  15-second prompts (each carrying the global Style Prefix, copy-and-run) plus an editable shotlist
  HTML. Use when the user wants to generate photoreal cinematic b-roll/scene footage for a video (not
  a talking head), asks to "make a shotlist", "write Seedance prompts", "break this script into
  prompts", or wants to run Seedance as Engine #6. Backed by 4_BRAIN/seedance_director.py (authoring)
  and 4_BRAIN/seedance_engine.py (access-gated provider render). Knowledge: 2_KNOWLEDGE/seedance/.
---

# Seedance 2.0 Prompt Director (SEOSONA Engine #6)

Seedance 2.0 GENERATES cinematic footage from text — different from the talking-head / portrait /
lipsync engines that animate a photo or footage. This skill authors the prompts (the craft) and,
when a provider key exists, renders + stitches them into a reel.

## The law (never break)
- **1 prompt = one self-contained ~15s clip.** The Style Prefix is pasted verbatim at the TOP of every
  prompt so a copied prompt runs standalone in Seedance. Longer scenes split into Na/Nb/Nc.
- **Block order is fixed:** SUBJECT → LOCATION → [LAYOUT] → ACTION(timed SHOTs, HARD CUTs) →
  CAMERA(per-shot: shot-size + FOV° + move + motivation) → STYLE(60:30:10 for this shot) →
  CONSTRAINTS(aspect + slow-mo + scale + continuity + **NO eye glow**).
- **@tag every recurring element** ("matches input 100%"); **@location is a STYLE REFERENCE ONLY**, not
  a fixed keyframe. **FOV in discrete degrees** from the anchor table (180/107/84/63/47/29/18/12/8).
- **Positive-only phrasing**, camera always motivated, continuity lives in the SUBJECT/ACTION language,
  avoid IP/real people/brands. Full grammar: `2_KNOWLEDGE/seedance/README.md`.

## How to run
```bash
# one idea → a single standalone prompt (stdout)
python 4_BRAIN/seedance_director.py --idea "a founder demos an AI SEO tool" --aspect 9:16

# a beat list (JSON: strings or {text,subject,subject_tag,location,palette,...}) → shotlist HTML + prompts.txt
python 4_BRAIN/seedance_director.py --script beats.json --title "Toby Labs" --out out/shotlist.html

# Engine #6 — render (needs a key) or degrade to prompt-only
python 4_BRAIN/seedance_engine.py --status
python 4_BRAIN/seedance_engine.py --script beats.json --title "Toby Labs" --out out/reel.mp4
```

## Render backends
- **Paid API** (any ONE key): `FAL_KEY` (fal.ai) · `REPLICATE_API_TOKEN` (Replicate) · `ARK_API_KEY`
  (BytePlus, stub).
- **`local` — LTX-Video, keyless** (Apache-2.0, runs on the factory GPU). One-time setup:
  `python scripts/ltx_video.py --setup` (~15GB). Then the engine auto-uses it — no key, no cost.
- No backend → PROMPT-ONLY: writes shotlist HTML + prompts.txt, reports how to enable. Never fake an mp4.

## Programmatic
```python
import seedance_director as d
doc = d.author_from_script("Toby Labs", ["beat one", {"text":"beat two","subject_tag":"editor"}])
print(d.build_prompt(doc["scenes"][0]))     # standalone prompt
open("shotlist.html","w",encoding="utf-8").write(d.shotlist_html(doc["title"], doc["scenes"]))
d.lint_prompt(prompt)                        # -> list of consistency-law checks it fails ([] = clean)
```
