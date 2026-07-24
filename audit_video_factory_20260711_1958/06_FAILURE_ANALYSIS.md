# 06 — FAILURE ANALYSIS

> Each item: symptom · evidence (file/log/line) · most-likely root cause · stage affected · impact on final video quality · fast read-only verification.
> **Framing correction:** the factory *does* render valid videos end-to-end (see [05](05_EXECUTION_TRACE.md)). The reason output isn't "good enough" is **not a broken renderer** — it is (a) a lenient QA gate that passes craft-flawed videos, (b) an unclosed feedback loop (never published, no analytics), and (c) the newest/most-cinematic capabilities being unwired or dependency-blocked.

## BLOCKER

### BLOCKER-1 — Feedback loop is open: never published, no real analytics
- **Symptom:** Every "success" ends at a QA-passed local MP4. The factory cannot learn what actually performs.
- **Evidence:** `logs/publish/receipts.jsonl` contains only `"dry-run ok"`; `views_total: 0` everywhere. `1_AGENTS/analytics_feedback_agent/performance_ingest.py:47` — live YouTube Analytics pull is `return None  # TODO`. `3_MEMORY/learning/ledger.json` → `total_videos: 1, signal: "qa-only"`.
- **Root cause:** Publish path is env-gated OFF and analytics ingest is a stub; the OBSERVE→LEARN half of the OODA loop is not implemented with real data.
- **Stage:** Publish → Analytics → Learn.
- **Impact:** No ground-truth quality signal ever reaches the system, so "quality" is self-graded. The factory optimizes toward its own lenient gate, not audience response. This is the deepest reason it plateaus.
- **Verify (read-only):** `cat logs/publish/receipts.jsonl`; grep `performance_ingest.py` for `TODO`.

### BLOCKER-2 — Cinematic / generative capabilities are unwired or dependency-blocked
- **Symptom:** The most "premium-looking" engines (AI b-roll, talking-head lip-sync, avatar motion) do not participate in the automated video and/or cannot run.
- **Evidence:** `seedance_engine.py` / `lipsync_service.py` have **no caller** in `workflow_router`/`video_engine` (orphaned — [03](03_WORKFLOW_AND_NODE_MAP.md)). `.venv-musetalk`, `.venv-sadtalker`, `.venv-liveportrait` (+weights) are **MISSING** on disk ([02](02_TECH_STACK_AND_SERVICES.md)). `seedance_engine._byteplus_generate` is a STUB; paid keys (FAL/REPLICATE/ARK) absent → only keyless local LTX works, and even that is CLI-only.
- **Root cause:** These were built as standalone engines (#3–#6) and never integrated into the main render, and their heavy venvs were never installed on this machine.
- **Stage:** Asset generation / b-roll / talking-head.
- **Impact:** The automated output is limited to the HyperFrames animated-card style. The richer motion/footage/AI-video layers that would raise perceived production value are not reachable by the one-command pipeline.
- **Verify:** `grep -rn "seedance_engine\|lipsync_service" 4_BRAIN/workflow_router.py 4_BRAIN/video_engine.py` (expect none); `ls 7_ASSETS/voice/.venv-* scripts/.venv-*` for missing venvs.

## HIGH

### HIGH-1 — QA gate passes craft-flawed videos (score inflation + shallow metrics)
- **Symptom:** Every recent render self-scores 97–100 PASS, yet WPM is 212–228 (far above the healthy 130–180 band) — i.e. narration is rushed but "passes."
- **Evidence:** Dashboard `recent_renders` all `verdict:"PASS"` with `wpm` 212–228; feedback `weak_signals`: *"wpm outside the comfortable band (130-180) on 59% of takes."* `quality_scorer.py:58` calls **bare `ffprobe`** (not the bundled `-static` binary like `native_composer._resolve_bin:178`); on a host without ffprobe on PATH → `FileNotFoundError` → `quality_scorer.py:117` still adds 15 partial points → **score inflation**, stream/aspect/duration checks silently skipped.
- **Root cause:** (a) `quality_scorer` measures file mechanics (size, streams, companion files, coarse pacing) not craft (pacing comfort, caption legibility, visual variety, audio quality); (b) ffprobe PATH fragility half-passes the one real media check.
- **Stage:** QA / scoring.
- **Impact:** The gate green-lights videos a human would call rushed/flat. Because BLOCKER-1 removes the external signal, this lenient gate *is* the ceiling on quality.
- **Verify:** `sed -n '55,120p' 4_BRAIN/quality_scorer.py`; check whether `ffprobe` is on PATH (`which ffprobe`); compare WPM in `3_MEMORY/factory_metrics.jsonl` vs 130–180.

### HIGH-2 — Off-brand backup voice used in production
- **Symptom:** Renders ran on VieNeu (backup) not OmniVoice (intended brand voice).
- **Evidence:** metrics/records show `voice: vieneu:GiaBao` / `vieneu:*`. OmniVoice needs the GPU venv `.venv-omnivoice` (present) + `HF_TOKEN` + working GPU; `voice_router` silently falls back to VieNeu on any failure.
- **Root cause:** OmniVoice GPU path not active during the 2026-07-06 batch (GPU/token/model not engaged); fallback is silent.
- **Stage:** Voice / TTS.
- **Impact:** Voice identity is off-brand and, per feedback, pacing/clone variance drives the WPM problem in HIGH-1. Directly degrades perceived quality.
- **Verify:** `grep -o '"voice":[^,]*' 3_MEMORY/factory_metrics.jsonl` (if present) or inspect render logs; `python 0_SETUP/check_env.py` for OmniVoice status.

### HIGH-3 — Topic path discards the verified script and pays twice
- **Symptom:** On `video:discover`, the carefully verified `Script` (headings, component hints, fx, traceability) is thrown away and re-generated.
- **Evidence:** `scripts/topic_to_video.py:121` builds a verified `Script`; `:164` passes only joined narration text to `route()`; `video_engine.plan_scenes:369` re-runs `scene_writer.write_scenes → script_writer.generate_script` again.
- **Root cause:** Interface mismatch — `route()` accepts text, not a structured `Script`; no structured hand-off path exists.
- **Stage:** Script → scene plan.
- **Impact:** Loses the best structural/verification work; doubles LLM spend and latency; introduces variance between the verified plan and the rendered plan.
- **Verify:** read `topic_to_video.py:110-170` and `video_engine.py:360-380`.

## MEDIUM

### MEDIUM-1 — `render_seconds` corrupted by wall-clock timestamp
- **Symptom:** `render_seconds: 1.78e9`; dashboard `avg_render_seconds: 743054812.9` (nonsense).
- **Evidence:** `logs/metrics/events.jsonl` render events @2026-07-06 16:23+; live `/api/metrics`.
- **Root cause:** An epoch timestamp leaked into an elapsed-seconds field (start-time not subtracted).
- **Stage:** Metrics / observability.
- **Impact:** Cost/latency tracking and any learning that uses render time are corrupted (cosmetic to the video itself).
- **Verify:** `grep render_seconds logs/metrics/events.jsonl | tail`.

### MEDIUM-2 — Upstream scrape yields no script → hard abort
- **Symptom:** A URL that produces no usable text fails the whole job before render.
- **Evidence:** `3_MEMORY/reports/TOBY_LABS_NEWS_20260706_151121.json` → `"Scrape produced no usable script from https://labs.toby.vn/"`, `quality_score:0`.
- **Root cause:** Scrape/research extraction is brittle for JS-heavy or sparse pages; no fallback to research-by-topic when scrape is empty.
- **Stage:** Input / research.
- **Impact:** Reduces autonomous throughput; some inputs never become videos.
- **Verify:** read that report JSON.

### MEDIUM-3 — `fill_template` hard length coupling
- **Symptom:** Content/template scene-count mismatch raises `ValueError` (render abort) instead of degrading.
- **Evidence:** `native_composer.py:3246`.
- **Root cause:** Strict equality guard; only the github path pads headings to mitigate.
- **Stage:** Template fill.
- **Impact:** Fragile on the template path; a planning drift kills the render.
- **Verify:** read `native_composer.py:3240-3260`.

### MEDIUM-4 — Content-moderation blocks may silently shrink scripts
- **Symptom:** ~1020 moderation events, many `block`/`flag` (unsafe-term, off-platform-cta, unattributed-stat, absolute-claim, social-proof).
- **Evidence:** `logs/metrics/events.jsonl` (newest activity is nearly all moderation).
- **Root cause:** Aggressive brand-safety/real-data gate; if it strips too much, scripts thin out (contributes to fast pacing / short content).
- **Stage:** Moderation.
- **Impact:** Potentially over-sanitized, thin scripts — a quality lever worth auditing against real transcripts.
- **Verify:** `grep '"kind":"block"' logs/metrics/events.jsonl | tail`.

## LOW

### LOW-1 — Stale docs / index drift
- **Symptom:** `2_SKILLS/README.md` lists nonexistent `tts_generator/`, omits 6 folders; `docs/04` says "23 SOPs" vs `6_SOP/README.md` "40"; `MEMORY.md` references nonexistent `pipeline_dag.py`; `docs/03`/`05` cite retired modules.
- **Evidence:** cross-checks in [01](01_SYSTEM_TREE.md)/[03](03_WORKFLOW_AND_NODE_MAP.md).
- **Impact:** Onboarding confusion; no runtime effect.
- **Verify:** `ls 2_SKILLS/`; `glob **/pipeline_dag.py` (empty).

### LOW-2 — Stale / unintegrated env keys
- **Symptom:** `FISH_AUDIO_API_KEY` stale (engine removed); AWS/Crawl4AI/Browserbase/Stability keys declared but no code.
- **Evidence:** [02](02_TECH_STACK_AND_SERVICES.md) section D.
- **Impact:** Config clutter / false impression of capability.
- **Verify:** `grep -rl FISH_AUDIO .env` (present) vs no code refs.

### LOW-3 — Inconsistent module import paths
- **Symptom:** `4_BRAIN.quality_scorer` vs `quality_scorer` imported in different callers.
- **Evidence:** `workflow_router.py:157` vs `video_engine.py:628`.
- **Impact:** Latent fragility if `sys.path` seeding changes; works today.
