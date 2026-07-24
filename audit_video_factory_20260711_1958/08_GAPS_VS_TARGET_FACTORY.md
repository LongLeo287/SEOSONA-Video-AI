# 08 — GAPS VS TARGET FACTORY

Target architecture:
`Video Intelligence → Creative/Seedance Director → Asset & Generation → Talking-head/Timeline Editor → Render & QA → Publish/Operations`

Mapping of the current system onto each target stage, with a verdict: **KEEP** (works, retain) · **RECONNECT** (built but unwired/blocked — wire it) · **BUILD** (missing) · **REMOVE** (duplicate/wrong-direction).

## Stage-by-stage

### 1. Video Intelligence
- **KEEP:** `asr_router` word-timestamps, `frame_scorer`, `evaluator` (black/silent/short), ffprobe stream checks.
- **BUILD:** shot/scene detection, per-frame visual QA, face/mic occlusion analysis on the auto path.
- **RECONNECT:** talking-head footage analysis (`talking_head_analyze`, palette, dead-air/dup-take detection) exists but only in the course/standalone path.

### 2. Creative / Seedance Director
- **KEEP:** `script_writer` 6-stage + traceability gate; `researcher`, `angle_finder`; `director` per-scene motion/SFX; `seedance_director` prompt grammar.
- **RECONNECT:** none needed for text scripts.
- **REMOVE / FIX:** the **double-write on the topic path** (`topic_to_video`→`route`→re-plan) — pass the verified `Script` structurally instead of re-deriving it (HIGH-3).

### 3. Asset & Generation
- **KEEP:** `image_sourcer` (Pexels/scrape), `broll_sourcer` (Pixabay), `element_maker`, `bgm_sourcer` (CC), `image_gen` (FLUX optional).
- **RECONNECT:** **Seedance/LTX-Video b-roll** — keyless local LTX is *ready* (weights present) but CLI-only and unwired; wire it as an optional b-roll source with continuity + retake.
- **BUILD:** a managed asset library with scene-fit scoring + used-asset dedup ledger.
- **REMOVE:** the BytePlus STUB and NOT-INTEGRATED keys (AWS/Crawl4AI/Browserbase/Stability) or implement them; drop stale `FISH_AUDIO_API_KEY`.

### 4. Talking-head / Timeline Editor
- **KEEP:** `effect_library` (transition/text-effect/SFX/motion), SFX cues + BGM ducking + loudnorm, block/scroll overlays, beat-snap — the timeline layer is strong.
- **RECONNECT (highest-leverage):** the **talking-head engine** (`talking_head_edit`, rembg text-behind-subject, palette, autocut EDL) and the standalone `cinematic_reel.py` craft — make them a first-class factory archetype, not a course-only/standalone tool.
- **RECONNECT:** lip-sync/avatar engines (MuseTalk #3b, SadTalker #3, LivePortrait #5) — install the missing venvs, expose via `lipsync_service` in the pipeline for expert-avatar videos.

### 5. Render & QA
- **KEEP:** `native_composer.make_video` render chokepoint (HyperFrames + ffmpeg), `eval_judge` (Gemini-vision).
- **BUILD / FIX:** replace the lenient `quality_scorer` with **craft metrics** (WPM comfort band, caption legibility/coverage, visual variety, LUFS/true-peak, occlusion) and make ffprobe use the bundled binary (HIGH-1). Add an optional human preview gate.

### 6. Publish / Operations
- **KEEP:** `queue_processor`, `daily_production`, `loop_guard`+STOP, `factory_metrics` recorder, Flask dashboard, `production_manifest`.
- **BUILD (BLOCKER):** real (human-gated) publish + real `performance_ingest` analytics + fix `render_seconds`/cost tracking + artifact versioning. This closes the OODA loop so learning uses audience signal.

## What to keep / reconnect / build / remove — summary

| Verdict | Items |
|---|---|
| **KEEP** | render chokepoint, LLM cascade + offline floor, ASR/pronunciation, effect/SFX/BGM timeline, queue/loop-guard/dashboard, script_writer + traceability |
| **RECONNECT** | talking-head engine → main pipeline · LTX b-roll → asset stage · lipsync/avatar venvs · verified-Script hand-off on topic path |
| **BUILD** | craft-based QA metrics · real publish + analytics (close the loop) · asset library w/ fit-scoring · cost tracking |
| **REMOVE / FIX** | topic-path double-write · BytePlus STUB or implement · unintegrated keys (AWS/Crawl4AI/Browserbase/Stability) · stale FISH_AUDIO · stale docs/index |

## Suggested fix order — shortest path to ONE genuinely good video

1. **Fix the QA gate to measure craft** (bundled ffprobe + WPM band + caption/loudness/variety checks). *Why first: without a truthful gate you can't tell if any later change helped.* — HIGH-1, criterion 9/1.
2. **Engage OmniVoice brand voice + enforce 130–180 WPM pre-render.** *The single most audible defect; cheap to fix.* — HIGH-2, criterion 4.
3. **Wire the talking-head engine as a selectable archetype** (it's the most finished premium capability and already produces cinematic output). — RECONNECT, criteria 6/7.
4. **Fix the topic-path double-write** (pass the verified Script structurally). — HIGH-3.
5. **Wire LTX b-roll** for visual variety on the news/animated path. — criterion 8/3.
6. **Close the loop**: real human-gated publish of one video + real analytics ingest, so the next iterations learn from reality. — BLOCKER-1.

Steps 1–2 are the minimum to *know* a video is good; 3–5 make it *look* good; 6 makes the factory *improve* over time.
