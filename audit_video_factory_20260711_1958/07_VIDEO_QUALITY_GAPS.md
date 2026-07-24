# 07 — VIDEO QUALITY GAPS

> Scorecard against Video-Factory standards. Scale:
> **0** = none · **1** = idea/UI only · **2** = disjoint logic · **3** = runs but unstable/not-good-enough · **4** = production-ready.
> Scores reflect what is **wired into the automated one-command video**, not standalone engines that exist but aren't reachable.

| # | Criterion | Score | Evidence & reasoning |
|---|---|---|---|
| 1 | **Video Intelligence** (frame/audio/timecode analysis) | **3** | ASR word-timestamps (`asr_router`→`words.json`), `frame_scorer` (Laplacian/entropy best-frame), `evaluator` black/silent/short checks, ffprobe streams. But no shot/scene detection, no per-frame visual QA, no face/occlusion analysis in the main path. |
| 2 | **Creative planning** (brief→script→scene plan) | **3** | Real 6-stage `script_writer` (fetch→analyze→reason→plan→write→verify) + traceability gate; `plan_scenes`→scenes with components. Unstable: topic path discards the verified plan (HIGH-3); moderation can over-thin scripts (MEDIUM-4). |
| 3 | **Asset intelligence** (know assets & fit to scene) | **2** | `image_sourcer` (Pexels/scrape), `broll_sourcer` (Pixabay), `element_maker` (icons), `bgm_sourcer` (CC) all exist and are wired, but selection is keyword/lexicon-based, not a managed asset library with scene-fit scoring. No dedup/reuse ledger of what's already been used. |
| 4 | **TTS / STT** (word-level, lexicon, brand spelling) | **3** | OmniVoice→VieNeu router, PhoWhisper word-level ASR, pronunciation lexicon + VN normalizer + brand-correct (celsona→SEOSONA). Downgraded because production ran on **off-brand VieNeu** (HIGH-2) and WPM 212–228 is out of band (HIGH-1). |
| 5 | **Caption craft** (sync, safe-zone, avoid face/mic, keyword emphasis) | **3** | RULE#1 display↔spoken alignment, tail-anchor rescale, ASS karaoke keyword highlight, `caption_segment` natural breaks, `_cc.srt` sidecar. But **no dynamic face/mic-aware safe zone** in the main animated path (that logic lives in the talking-head engine, not the news path). |
| 6 | **Talking-head** (lock footage, palette extract, text-behind-subject, dynamic safe zone) | **2** | Fully built (`talking_head_edit`, rembg text-behind-speaker, palette, autocut EDL, `cinematic_reel.py`) but only reachable via the **course path / standalone tool**, not the primary factory command; newest work (`adsbootcamp_11_07`) is the standalone editor producing a video-only cache. Not integrated as a first-class factory output. |
| 7 | **Timeline editing** (cut, B-roll, motion gfx, SFX, music ducking, transitions) | **3** | Strong: `director` motion, `effect_library` (transition/text-effect/SFX/motion recipes), 13–21 SFX cues per video, BGM sidechain-duck, `alimiter`+`loudnorm -14 LUFS`, block/scroll overlays, beat-snap. Style is single-archetype (animated cards); limited real-footage B-roll on the auto path. |
| 8 | **Seedance / generative video** (prompt, reference role, continuity, retake) | **1→2** | `seedance_director` grammar-encoded prompts + shotlist; keyless local **LTX-Video ready** (weights present). But it's **CLI-only, not wired**, paid providers keyless-absent, BytePlus adapter is a STUB, and there is no clip-to-clip continuity or retake protocol in an automated flow. |
| 9 | **Render / QA** (preview, frame inspection, loudness, black-frame, subtitle/occlusion QA) | **3** | Loudness normalized; `evaluator` catches black/silent/short; `quality_scorer` + Gemini-vision `eval_judge`; thumbnail frame scoring. But QA is **lenient/inflatable** (HIGH-1: bare ffprobe, no craft metrics), no occlusion QA on the auto path, no human-in-the-loop preview gate before "PASS". |
| 10 | **Operations** (queue, retry, status, logs, artifacts, cost, versioning) | **3** | Real `queue_processor` (per-item isolation, retry, `_kill_tree` timeout, idempotent ledger), `daily_production` scheduler, `loop_guard` circuit-breaker + STOP kill-switch, JSONL flight recorder, Flask dashboard, `production_manifest` variant tags. Gaps: **no real cost tracking** (`render_seconds` corrupted, MEDIUM-1), **publish never real** (BLOCKER-1), no artifact versioning store (8_WORKSPACE is transient/gitignored). |

## Aggregate

- **Average ≈ 2.6 / 4** — a genuinely functional factory that renders valid videos, held below "good" by three things, in priority order:
  1. **Lenient, inflatable QA with no external truth signal** (criteria 9 + the missing feedback loop) — it can't tell a good video from a passable one.
  2. **Off-brand voice + out-of-band pacing** (criteria 4) — the single most audible quality defect.
  3. **The premium layers (talking-head, generative b-roll, avatar) are built but not wired** (criteria 6, 8) — so the auto output is capped at one animated-card style.

## What "good" would require (evidence-driven)
- Replace/augment `quality_scorer` with **craft metrics** (WPM comfort, caption legibility/coverage, visual-variety, audio LUFS/true-peak, occlusion) and make ffprobe use the bundled binary. → lifts #9, #1.
- Engage **OmniVoice brand voice** and enforce the 130–180 WPM band pre-render. → lifts #4.
- **Wire the talking-head engine and LTX b-roll** into the main pipeline as selectable archetypes. → lifts #6, #8, #7.
- **Close the loop**: implement `performance_ingest` real analytics + a real (human-gated) publish, so learning uses audience signal. → lifts BLOCKER-1, enabling every other score to actually improve over time.
