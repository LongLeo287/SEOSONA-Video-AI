# Talking-head MOTION & EFFECT — capability plan (2026-07)

The reels' appeal is the MOTION/EFFECT on icons·emoji·text·b-roll — pop/bounce/kinetic/particle, not
static overlays. Plan to level the talking-head element layer up, with the repos vetted for each track.
Brand law unchanged: LIGHT, seek-safe, headless, free for OUR render; CapCut export is an editable handoff.

## Track 1 — Native entrance motion — ✅ DONE (2026-07-01)
`talking_head_edit` element overlays now animate the ENTRANCE (offset decays to rest over ~0.34s) +
alpha fade: `anim` ∈ rise / drop / slide-left / slide-right / pop / fade. `element_picker` rotates the
anim per slot for variety (emoji → pop). Fully ffmpeg-expressed (overlay x/y as functions of t) — headless,
fast, exact placement. Frame-verified (a tile rises into place across its entrance window).

## Track 2 — Rich animated element clips (pop/bounce/spin/…) — ✅ DONE (2026-07-01)
`element_maker.render_element_clip(spec, out.mov, anim=…)`: a seek-safe Web-Animation played frame-by-frame
in Chromium (deterministic) → **transparent `.mov` (qtrle/RGBA)** — VP9 `yuva420p` silently drops alpha through
ffmpeg filters, so qtrle is the reliable alpha codec. Anims: pop/bounce/spin/slide-up/slide-left/rise. Element
rest top-left sits at (CLIP_INSET, CLIP_INSET) so the overlay places at (x−INSET, y−INSET) — exact. Wired into
`talking_head_edit` as **opt-in `rich_motion:true`** (default stays the fast Track-1 ffmpeg motion). Verified
end-to-end over footage (AI bounce + zap spin + 🔥 pop, clean alpha, exact placement). = CapCut-grade element
motion, NATIVE (no CapCut, no human, no computer control).

## Track 3 — Lottie motion-graphics — ✅ DONE (2026-07-01)
LottieFiles = thousands of free animated icons/effects (After-Effects JSON). `element_maker.render_lottie_clip(
name, out.mov, w, h)` renders any Lottie JSON headless to a transparent `.mov` (qtrle) via the vendored
**airbnb/lottie-web** (MIT, `7_ASSETS/brand/lottie/lottie.min.js`), seek-safe frame-by-frame (goToAndStop frame-based).
Wired into `talking_head_edit` as element `type:"lottie"` + `src:"<name>"` (rich_motion path; placed at exact
w×h, no inset). **Verified** (a scale+rotate Lottie animates correctly, centered, clean alpha). Drop-in:
put a free `.json` in `7_ASSETS/brand/lottie/` (see its README) — colours are baked in the JSON. Do NOT
hand-author Lottie (schema is fragile; use real LottieFiles exports). python `lottie` (PyPI) is AGPL → not used.

## Track 4 — CapCut — ✗ DROPPED (2026-07-01, user decision)
CapCut has NO free headless renderer; its only "auto export" drives the app GUI (= controlling the computer).
The user wants a FULLY autonomous factory (no human, no computer control), so **CapCut is off the roadmap** —
all motion/effects are done NATIVE (headless HTML→alpha-clip + ffmpeg). The vendored toolkits (pyCapCut,
capcut-mate, VectCutAPI) + `4_BRAIN/capcut_export.py` remain only as an OPTIONAL manual handoff if a human ever
wants to hand-edit in CapCut; they are NOT invoked on the autonomous path. Do not build the rich-export upgrade.

## Sources (repo research 2026-07-01)
- pyCapCut — https://github.com/GuanYixuan/pyCapCut  · pyJianYingDraft — https://github.com/GuanYixuan/pyJianYingDraft
- capcut-cli — https://github.com/renezander030/capcut-cli  · CapCutAPI — https://github.com/renqingfei/CapCutAPI
- VectCutAPI — https://github.com/sun-guannan/VectCutAPI
- lottie-web — https://github.com/airbnb/lottie-web  · python lottie — https://pypi.org/project/lottie/
- HyperFrames (HTML→transparent WebM, the project's engine) — https://hyperframes.video/developers

Related: [[element-library]] · [[talking-head-craft-study]] · [[effect-library]] (faceless-engine native effects) ·
[[library-growth-pipeline]]. Log vetting verdicts in `2_KNOWLEDGE/INGESTION_LOG.md`.
