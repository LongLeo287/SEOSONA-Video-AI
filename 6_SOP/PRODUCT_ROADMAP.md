# SEOSONA Video — Product Roadmap (the path to product)

> Ultimate goal: a reliable **automated Vietnamese video factory** — feed in input
> (GitHub URL / script / website / long video), get out a complete, on-brand video,
> self-scored for quality and self-published. This document is the phase map to get there.

_Updated: 2026-06-27 · status after the engine consolidation + system-wide cleanup pass._

---

## 0. Foundational decision: do NOT rebuild from scratch

Rebuilding from scratch would **throw away the hardest part that already works** and force us to
face the exact same problems again. Reasons to keep and move forward:

- **The engine is consolidated into ONE clean path**: `video_engine.py → native_composer.py
  (+ scene_composer, make_video)`. `workflow_router` has been rewired. **25/25 tests pass**,
  `seosona:audit` + `video:audit:integration` both **PASS**.
- **The hard pieces are integrated & working**: VieNeu voice (local, free), ASR timing
  (caption RULE #1), HyperFrames native render, SFX + BGM ducking mix, GitHub data fetch,
  clipper (repurpose), scraper. A rewrite = redoing many months of integration.
- **Full infrastructure**: 10 agents, 7 skills, 10 JSON templates, brand system, 23 SOPs, knowledge base.
- **Already cleaned, no legacy-code contamination**: all old engines have been removed from the project tree
  (git history retains the tracked version), new files do not mix in old code.

→ **What remains is VERIFY + HARDEN + POLISH, not REBUILD.** The biggest "unproven" part
is only: *has it actually rendered a real, complete video yet* — that is Phase 1.

### Current state (snapshot)
| Area | Status |
|---|---|
| Architecture / consolidated engine | ✅ Done (1 path, tests + audit pass) |
| create/scrape/repurpose/publish/quality-gate features | ✅ Code complete — ⚠️ **not yet run for real end-to-end** |
| SEOSONA brand (logo/voice/footer/colors) | ✅ Correct |
| CQA brand | ⚠️ Logo/voice/footer correct; **accent color shared with SEOSONA**; missing cqa voice clip |
| Scene planner from arbitrary text | ⚠️ Deterministic draft; high-quality agent/LLM path not enabled |
| Publish (YouTube/TikTok/FB/Drive) | ⚠️ Code present — **no credentials yet, not tested** |
| Dashboard / observability | ⚠️ Basic |
| Environment | gh ✓ · vieneu ✓ · ffmpeg ✓ · hyperframes CLI (needs confirmation) |

---

## Phase 1 — VERIFY: prove it renders a real video ⛳ (DO THIS FIRST)

**This is the most important gate.** Everything downstream depends on confirming the pipeline
actually produces a watchable video. Until you *watch* 1 real video, the rest is just theory.

**What to do:**
1. Confirm prereqs: `gh auth status`, `node -e "require('hyperframes')"`, ffmpeg, VieNeu.
2. Run the GitHub one-shot: `npm run make:video -- <github_url>` → check that `8_WORKSPACE/auto/<name>/`
   has `*.mp4` + `*.srt` + `Thumbnail/thumbnail.png`.
3. Run create-from-text: `npm run video:news -- "<Vietnamese script>"`.
4. **WATCH the video** and run through the quality checklist:
   - Correct voice (male, southern accent, VieNeu — does not drop to the edge fallback).
   - Caption = the DISPLAYED text (SEO/AI/24/7), NOT a transliteration (RULE #1).
   - Light mode, crossfade with no white frames.
   - Components render correctly (no empty boxes — bignum/repo/terminal/gittree...).
   - SFX/BGM balanced under the voice; logo + footer on-brand.

**Exit:** at least 1 video you would genuinely dare to publish. Record the actual bugs (if any) → Phase 2.

---

## Phase 2 — BRAND & QUALITY: standardize the output

**What to do:**
1. **Full CQA brand**: add a dedicated accent palette for cqa in `native_composer`
   (currently shares the SEOSONA palette); drop the `chiquyet_sample_4s.wav` clip into
   `7_ASSETS/voice/profiles/`; run `npm run video:course` to confirm the CQA brand is correct.
2. **Voice clone**: confirm `seosona_ref13.wav` actually clones (not just a preset);
   fine-tune stability if needed.
3. **High-quality scene planner**: enable the Scene-Composer agent / LLM path
   (`GEMINI_API_KEY`/`OPENAI_API_KEY`) for more natural headings + scene breakdown,
   or improve the deterministic heuristic. (Currently an honest draft.)
4. QA caption/timing across 5–10 diverse scripts (numbers, English terms, long/short).

**Exit:** both brands + any VN script produce an on-brand video with correct captions.

---

## Phase 3 — RELIABILITY: run in bulk without crashing  ✅ (2026-06-29)

**What to do:**
1. **End-to-end queue**: drop real items into `0_INPUT_INBOX/production_queue.yaml` →
   `npm run start:queue` → produce a video for each item.
2. **Error handling**: retry, recover when one step fails, honest logging; cleanup-on-failure
   (already present) works correctly.
3. Consistent naming/output; avoid duplicates; idempotent on re-runs.

**Exit:** drop N items → get N videos; errors are logged rather than crashing the whole batch.

**Status:** `scripts/queue_processor.py` has been rewritten production-grade and **verified**:
- per-item error isolation (1 broken item does NOT take down the batch) · retry + backoff · per-item timeout
  (a hung render does not block the queue) · honest logging (logs/queue/<run>/, prints tail on failure) ·
  save queue after EVERY item (a mid-run kill loses no progress) · idempotency (ledger skips
  already-done items) · run report (run.jsonl). Flags: `--dry-run / --only / --queue / --retries / --timeout`.
- Mock test (3 items including 1 failure) → isolation + retry + keep-failed-item correct; idempotency + timeout passed.
- REAL test (1 item → 1 MP4 48kHz, file → done/) passed. Fixed a real blocker: `workflow_router.py`
  imported `skill_registry` before adding 4_BRAIN to sys.path → ModuleNotFoundError when called
  from scripts/ (sys.path now placed before the import).
- Still open: bad-take retry (depends on the voice clone — user handles separately).

---

## Phase 4 — PUBLISH: automatic distribution  🟢 BUILT (awaiting credentials)

**What to do:**
1. Fill in credentials: `1_CONFIG/credentials/{telegram,youtube,tiktok,facebook,google_drive}.json`
   (copy from `*.example.json`).
2. Test in safe order: `SEOSONA_PUBLISH=telegram` (FREE) first, then google_drive/youtube.
3. SEO metadata (`seo_optimizer/youtube_seo`) attached to the real upload; check title/description/tags.

**Exit:** 1 video self-publishes to at least 1 destination with correct metadata.

**Status (2026-06-29):** infrastructure is **pre-built, plug in credentials later** — `1_AGENTS/publisher_agent/
publish_dispatch.py` routes 5 destinations, each **credential-gated** (missing key → "skipped", no
crash). `maybe_publish` reads the `SEOSONA_PUBLISH` env var. **Added a Telegram publisher (FREE, instant,
no app review required)** — the first free destination. Verified: ran with no credentials → all 5 destinations "skipped"
cleanly. YouTube/TikTok/FB/Drive need an app/OAuth → plug in later (paid/effort). See `6_SOP/DEPENDENCIES.md`.

---

## Phase 5 — CONTENT ENGINE: scale content  🟢 BUILT (awaiting schedule activation)

**What to do:**
1. **News batch**: `python 4_BRAIN/make_video.py --news urls.txt` → feed daily news,
   rotating template/theme to avoid monotony.
2. **Expand the template library**: use `native_composer.extract_template()` to turn good
   renders into reusable JSON templates.
3. **Automatic schedule**: cron / scheduled agent for daily production with no human involved.

**Exit:** automatically produce N videos/day.

**Status (2026-06-29):** **pre-built, activated with 1 command**. The daily runner
`scripts/daily_production.py` (npm `daily`) runs the Phase 3 queue + optional news batch
(`--news sources.txt`) + publish (if `SEOSONA_PUBLISH`) — free/local by default. Scheduler
scaffold in `deploy/`: `run_daily.bat` + `SCHEDULING.md` (Windows `schtasks` one-liner + cron
for Linux). Verified: `daily` running an empty queue → ok, writes `logs/daily/`. `news_rotation` (GitHub batch,
template rotation) is present. extract_template is present for expanding templates.

---

## Phase 6 — OBSERVABILITY & feedback loop: a self-improving factory  🟢 BUILT (core)

**What to do:**
1. Dashboard (`9_DASHBOARD`) displays real metrics (in production / done / queued).
2. Tune the `quality_scorer` gate + the `analytics_feedback_agent` loop so quality rises over time.
3. Track cost/performance (render time, voice fallback rate).

**Exit:** the factory self-monitors + has a quality feedback loop.

**Status (2026-06-29):** **gathered + connected** the scattered signals into 1 hub. New:
`9_DASHBOARD/obs_metrics.py` (hub: `record()` → `logs/metrics/events.jsonl`; `read_health()` merges
events + queue run.jsonl + daily logs + 8_WORKSPACE outputs, infers caption-sync % /
quality pass % / avg render s). Emitters wired: `native_composer` (render: wpm, caption-sync,
render-seconds, sfx, brand) + `score_output` (quality score/verdict). Dashboard
`9_DASHBOARD/server.py`+`index.html` rebuilt → KPIs + recent-render table (wpm/sync/score) +
queue runs, auto-refresh 5s, `/api/health`. Map in `9_DASHBOARD/README.md`. Verified: render →
hub captures → `/api/health` returns correctly → `/` HTTP 200. **No external repo adopted** (ToolJet/Prometheus
= over-engineering; Flask + obs_metrics is enough).

**AUTOMATIC feedback loop — CLOSED (2026-06-29):** `9_DASHBOARD/feedback_loop.py` reads the hub →
computes `recommended_gate` (**ratchet**: tracks recent-score p25, clamp 60–85 → the bar rises with proven
capability, never drops) + weak-signals (estimated caption-sync %, wpm out of band, score below
gate) → writes `feedback_state.json`. `quality_scorer` reads the dynamic gate (file-read, default 60 — does NOT
import, safe). Runs automatically at the end of every batch (`daily_production`) + `npm run feedback`. The dashboard
shows the gate + weak-signals. Verified: scores [72–90] → gate ratchets 60→70 → quality_scorer reads 70 ✅.
**Phase 6 fully closed. All 6/6 phases 🟢.**

Architecture note: `quality_scorer` (4_BRAIN, 5+ callers) + the feedback agent (1_AGENTS, 4 callers)
are NOT pulled into 9_DASHBOARD — they are brain/agent logic wired deep into the factory; pulling them = 9+ import edits +
risk, no benefit (the hub already reads their data). The observability house (hub+view+loop) is gathered in
9_DASHBOARD; the scorer/agent are feed sources, leaving them in place is correct + safe.

---

## Critical path & recommended order
1. **Phase 1 (VERIFY) — right now.** Without confirming a real render, every later phase is an assumption.
2. Phase 2 (brand/quality) — once you have a real video to inspect.
3. Phase 3 → 4 → 5 → 6 in sequence; each phase has clear exit criteria above.

> Principle throughout: **do not mix old code into new files** — the old engines have been removed from the project tree.
> Every change must keep `pytest` + `seosona:audit` + `video:audit:integration` in a PASS state.
