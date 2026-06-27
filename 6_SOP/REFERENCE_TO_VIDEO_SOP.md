# SOP: REFERENCE → VIDEO (clone a reference video's style into a SEOSONA HyperFrames video)

Turn a reference video (e.g. a competitor's faceless scene-slide video) into a new
SEOSONA-brand video in the **same style/structure**, rendered by HyperFrames.

> ⚠️ **"Clone" = style/structure, NOT a pixel-perfect copy.** The pipeline re-BUILDS the
> video in HyperFrames: same scene structure, component types, kicker/heading/footer/
> karaoke chrome, pacing, accent rhythm — re-rendered with SEOSONA brand + the locked
> VieNeu voice. Bespoke illustrations (e.g. a git-commit-tree animation) are NOT copied;
> they need a new component (see "Custom components"). Think *re-skin the template*, not *photocopy*.

## Pipeline (5 steps)

```
[1] ANALYZE   scripts/analyze_reference.py <video> [out_dir]      (deterministic)
      → meta (aspect/fps/duration/LUFS), scene candidates, frames/, contact_sheet,
        transcript (words+timing) → analysis.json
[2] COMPOSE   Scene-Composer (vision agent)                       (AI)
      → look at frames/ + contact_sheet + transcript → author a scenes spec:
        per scene { kicker, h1/h2 (2-tone heading), accent, component+data, } in the
        native_composer format. Pick component per scene from the available library.
[3] (review)  human reviews the scenes spec (fix data, wording, components)
[4] GENERATE  4_BRAIN/native_composer.make_video(segments, scenes)
      → VieNeu voice (locked Trọng Hữu) → RULE #1 display captions → HyperFrames render
        → SFX + loudnorm. SEOSONA brand chrome (logo, footer, CTA) is built in.
[5] VERIFY    RULE #8 — extract frames (YAVG>12), loudness ~-14..-16 LUFS, duration, captions.
```

## Run

```bash
# Step 1
node scripts/seosona-python.cjs scripts/analyze_reference.py "<reference.mp4>" 8_WORKSPACE/<name>_analysis
# Step 2: open 8_WORKSPACE/<name>_analysis/contact_sheet.png + analysis.json,
#         write a scenes driver (see 8_WORKSPACE/HOCGIT_analysis/scenes_hocgit.py as the template)
# Step 4: render
node scripts/seosona-python.cjs 8_WORKSPACE/<name>_analysis/scenes_<name>.py
```

## Two modes
- **CLONE** — same topic + same style as the reference (re-skin 1:1).
- **ADAPT** ⭐ — keep the reference's *structure/style*, swap in a NEW topic + real data →
  mass-produce videos in a proven style. This is the high-value mode.

## Component library (native_composer) — map each scene to one
`bignum` · `repo` (GitHub card: stars/tags/button) · `terminal` · `compare` (2-col ✓/✕) ·
`steps` (numbered) · `badges` · `cta` (logo + button) · or `None` (heading-only transition).
Accents rotate: SEOSONA `BLUE` / `GREEN` / `ORANGE`.

## Custom components (when the reference has a bespoke visual)
If the reference relies on a signature graphic the library lacks (e.g. an animated
git-commit-tree), add a renderer in `native_composer._component(kind, d, acc)` + CSS,
then reference it as `("<kind>", {...})` in the scenes spec. Until then, map that scene
to the closest existing component or a heading-only transition.

## Notes / gotchas
- **Scene detection**: smooth-transition faceless videos have no hard cuts, so the analyzer
  falls back to transcript-pause segmentation (coarse). The vision step (2) sets the real
  scenes by looking at the frames — trust the contact sheet over the auto scene count.
- **Voice**: single locked brand voice (`voice_router.APPROVED_VOICE`). No voice on poster/ads.
- **Brand**: SEOSONA logo (persistent), footer, CTA outro are built into native_composer.
- **Aspect/loudness**: match the reference (`analysis.json.meta`) — e.g. 9:16, ~-14 LUFS.

## Worked example
`8_WORKSPACE/HOCGIT_analysis/` — analysis of "HỌC GIT QUA GAME" (9:16, 72s, -14.2 LUFS,
transcript 234 words) + `scenes_hocgit.py` (step-2 output: 8 scenes — hook → repo →
terminal → steps → badges → bignum → cta).
