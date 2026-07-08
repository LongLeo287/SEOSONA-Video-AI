# SKILL AUTO — learnings + adoption plan (2026-07)

Deep analysis of the professional YouTube video-edit skill in `D:\SEOSONA AI\SKILL AUTO` (Luuk Alleman /
build-loop.ai): a **Remotion (React→MP4)** footage/talking-head editor with 50 template components, 11 craft
docs, a 118KB orchestration SKILL.md, and ~14 pipeline scripts. Analysed by 6 parallel agents (SKILL.md ·
craft/workflow · visual/template · audio/QA · Remotion templates · scripts).

**Direction (same as every ingestion):** learn the CRAFT + MECHANISMS; keep our engines (HyperFrames HTML→MP4
`native_composer` + footage `talking_head_edit`) and our **LIGHT brand** (blue #2A5BDA / coral #E2724D — remap
their dark raisin-black + neo-lime). No duplication, connect, native/headless/free. **Do NOT adopt:** the Remotion
runtime (we have 2 engines), their palette, paid AI-gen (gpt_image_2 / Higgsfield / Seedance), CC-BY tracks (KMC).

## The meta-learning (biggest structural takeaway)
**Everything is LINT-GATED before render, and the LLM authors intent while deterministic code handles timing.**
The LLM writes *content + `reason` + `speech_anchor`*; Python passes snap timing to spoken words, close gaps,
compute durations, and a hard linter refuses to render on missing reason / blank fields / bad density. Small,
auditable plan JSON; idempotent chainable passes. This gate mechanism matters as much as any single rule.

## Adoption backlog (tasks A1–A10, priority order)

### Tier 1 — quality gates + alignment (highest ROI, zero deps, both engines)
- **A1 · reason-field + per-kind lint gate** (`lint_plan.py`): every scene/element needs a one-line `reason`
  (names what's said + what the visual adds); per-kind required-field contract; asset-exists; first-beat floor;
  text-never-over-face; density cap. Blocks render. → new `spec_lint` for both engines' specs.
- **A2 · speech_anchor alignment** (`align_to_speech.py`): author a beat by its exact spoken phrase → fuzzy-locate
  in words.json (exact → ≥70% in-order → substring) → snap `start=word−0.10`, `end=word+0.80`; guards: 1.5s
  cold-open floor, 5s clamp (SEQUENCE_KINDS exempt), never-shorten. "Author by meaning, machine derives frames."
- **A3 · reading-time durations + density governor**: dwell = `max(3.5, char/READING_CPS + 1.5)` (VN CPS lower
  than 12); density ≤4 beats/12s, ≥1/60s, no back-to-back same-kind, last list item ≥1.5s. + `close_gaps` (bridge
  sub-1.5s dead-air, 6s ceiling, partial-overlay exempt) + `sync_list_items` (reveal each item when spoken).

### Tier 2 — concept-viz + missing components (native, light brand)
- **A4 · `concept_build` explainer canvas** ⭐ (flagship gap): free-form VO-synced canvas — labeled box/chip/
  tile/frame/note at x,y + connectors; nodes launch-from-center + idle-float; connectors stroke-wipe + spawn-
  pulse. + **concept-viz doctrine**: shape-of-idea classifier (SEQUENCE/NETWORK/CONTRAST/STRUCTURE/MAGNITUDE/
  POINT-AT/ABSTRACTION → component) + "does it TEACH?" gate + **≥1 concept-visual per 60s** of explanation.
  Into `component_picker` + `VIDEO_CRAFT_RULES`.
- **A5 · missing archetypes**: `comparison_grid` (feature matrix + winner col) · `split_reveal` (before/after
  clip-wipe + glowing divider — pairs with image_sourcer) · `annotated_screenshot` (corner-brackets draw-in +
  dim-outside + zoom-to-bbox) · `ratio_dots` (X-of-Y kill/win) · `network_spread` (hub + value-tokens streaming) ·
  `layer_stack` (architecture slabs) · `ticker_feed` (rows slide down) · `stat_grid` · `quote_pull`. All → picker.
- **A9 · auto-logo fetcher** (`fetch_logo.py`): keyless Wikipedia (disambiguation candidates + logo-likelihood
  scoring blocks CEO photos/chrome, SVG>PNG, magic-byte validate) → new image_sourcer provider + `logo` element;
  text-tile fallback for VN-local brands.

### Tier 3 — motion + audio craft, hygiene
- **A6 · motion.ts port ⭐ + emphasis zoom-punch**: port the ~10 motion primitives to GSAP ONCE (ENTRANCE_EASE
  `cubic-bezier(.16,1,.3,1)`, EXIT_EASE `(.7,0,.84,0)`, `useLivingHold` never-freeze drift ≤1.02, `useChoreographed
  Exit` dissolve-forward w/ blur, `useWordReveal` mask-rise, `useEmphasisPunch` spring 1.06, `useSettleZoom`
  1.0→1.025, **`useTypeBase` = font on min(w,h)** for cross-aspect) → upgrades EVERY component pop-freeze→
  entrance/hold/exit. + `zoom_plan.py` emphasis scoring (numbers+3/brands+2.5/pivots+2/loaded-pause) → punch 1.06
  (+0.02 numbers), cap 1.15. + sub-element reveal on spoken word (`appear_sec`).
- **A7 · intro 4-slot hook recipe + ending gate**: hook-claim→proof→promise(callout)→roadmap(timeline)→closer
  (caption-only); ending = exactly one of {loop-back, hard CTA}, ban soft closers. Into script_writer/verify.
- **A8 · audio craft**: **closer-suppression** (mute SFX sting on final CTA beat, keep visual pop) · verify
  two-stage sidechain ducking (control-signal from voice, release~400ms, no mid-sentence pump) · **BGM swell arc**
  (trapezoid rise/hold/fall into climax) · sustained-swell for long data-viz reveals · **cornyness reject-filter**
  + loop-safety (≥30s, no hidden vocal) in BGM sourcer · add public-domain classical (Satie/Bach/Pachelbel) to a
  calm-shorts mood pool. Two-register mix by format (shorts near-subliminal / longform audible).
- **A10 · hygiene**: 720p preview-proxy for footage engine · `extract_stills` one-PNG-per-scene contact sheet →
  eval flywheel · deterministic ASR brand/VN correction table matched vs our own `script_writer` script
  (`align_transcript_to_script` difflib brand-token repair) · frozen-source restore before in-place mutation ·
  QA loop = defect → per-render fix **+ codify a rule into VIDEO_CRAFT_RULES** + global re-sync.

## VN adaptation caveat (applies to every text/word heuristic)
The algorithms transfer; the **lexicons/constants do NOT**. Re-author for Vietnamese: stopword list, pivot words
("nhưng/thực ra/khoan/vấn đề là"), number words, brand-like token detection, and READING_CPS (VN reads slower
on-screen → lower than 12). Diacritics: normalise NFC consistently on both sides of any fuzzy match.

## Image doctrine (adopt the RULE, not the paid tool)
We source real photos (Pexels/scrape, free) — do NOT adopt gpt_image_2/Higgsfield/Seedance (paid, hosted). DO
adopt: one recognisable concrete subject per frame; map abstractions → universal symbols (funnel→hourglass,
guardrail→shield); consistent brand backdrop so all image beats feel unified (our dominant-colour harmony already
starts this). Bank the Seedance decision-boundary for any future local i2v: never ask diffusion for numbers/text/
logos/precise-stagger/state-flips — render exact layout as a still, use diffusion only for breathing/parallax.

Related: [[design-system-and-craft]] · [[element-library]] · [[image-sourcing]] · [[template-craft-study]] ·
[[talking-head-craft-study]] · [[effect-library]] · [[self-improvement-loop]]. Log verdict in INGESTION_LOG.

---

## TIER 4 — full re-mine ("đào hết", 2026-07-03)

A1–A10 skimmed the surface; a 3-agent deep re-scan found the folder is bigger than first measured (68 template
components, 22 scripts, +2 root files) and that several deterministic mechanisms + non-negotiable rules were NOT
yet adopted. Built the real gaps (native/free/light-brand, no new deps):

**Rules encoded (spec_lint.py)** — from `knowledge/non_negotiables.md` + `editing_rules.md`:
- `coverage_ratio` / `coverage_warnings`: a visual must be on screen **≥70%** of runtime (the #1 non-negotiable) —
  partial overlays (speaker still visible) don't count as coverage.
- hook-visual **@0.0s** (the thumbnail frame), beat-duration **ceiling ≤5s** (`_duration_warnings`), icon **safe-zone
  Y≤80%** (`_safezone_warnings`), micro-gap **flicker** flag. New `lint_broll(beats, total)` entry + `PARTIAL_KINDS`.

**Mechanisms ported (NEW 4_BRAIN/beat_timing.py)** — VN-adapted lexicons:
- `close_gaps` — bridge sub-1.5s flicker gaps / fix overlaps; two partial overlays left alone.
- `sync_list_items` — reveal each list row **when the speaker says it** (keyword → word-timing window), not evenly
  front-loaded (kills the spoiler). Wired into talking-head bullet cards.
- `zoom_plan` — **score** which spoken word earns an emphasis punch (numbers +3, brand +2.5, pivot +2, loaded pause
  +1.2) → greedy top-N windows. This was the *real* A6 gap (A6 only hardcoded a zoom). Wired to auto-highlight punchy
  words in the talking-head captions (reuses the ASS highlight — no new render path).

**Components added (native_composer + component_picker + spec_lint _REQUIRED)** — the 5 genuinely-missing archetypes:
`stat_grid`, `ratio_dots`, `layer_stack`, `ticker_feed`, `org_diagram`. All `.ritem` seek-safe, reuse existing
color-mix / reveal primitives; LLM menu lines + render-safe validators + blank-risk contract.
**Verified by a real GPU-free Node/Chromium render** → 1080×1920 mp4, Quality Scorer 100/100; stat_grid + ratio_dots
render perfectly in SEOSONA light brand.

**SKIP (15, Remotion-specific/redundant):** ColorGrade, Backgrounds, PortraitBurst, AgentAvatarBurst, followcam,
segment_speaker (rembg+PyAV, no per-frame pan in our stack), polish_transcript (LLM ASR — our deterministic table
suffices), Captions/SubscribeButton/etc. (already native). **Deferred:** captions_plan (we don't render on-screen
captions in the faceless engine), align_to_speech cold-open-floor extras. Status: all built items compile + render
clean; UNCOMMITTED (git deferred).
