# 05 — EXECUTION TRACE

> Evidence of real runs. Read-only. ffprobe used for probing (no video re-rendered).
> Legend: **CONFIRMED** = direct file/log evidence · **INFERRED** = deduced · **UNKNOWN** = no evidence.

## Where the factory records runs (CONFIRMED)

| Store | Path | Content |
|---|---|---|
| Render metrics | `3_MEMORY/factory_metrics.jsonl` | 30 render records, 2026-06-30 → 07-06 (28 of 30 `ok:true`) |
| Event bus | `logs/metrics/events.jsonl` | 1219 events (≈1020 moderation, 129 render, 67 quality, 3 evaluation); newest activity 2026-07-11 15:41 |
| Quality reports | `3_MEMORY/reports/*.json` | per-project QA report (score + notes) |
| Learning ledger | `3_MEMORY/learning/ledger.json` | aggregated signal (currently near-empty: `total_videos: 1`) |
| Feedback | `9_DASHBOARD/feedback_state.json` | avg_score 99.1 over 52 samples |
| Daily loop log | `logs/daily/20260629-093347.log` | `overall=ok` |
| Publish receipts | `logs/publish/receipts.jsonl` | only `"dry-run ok"` — no real publish |

## (A) Last 5 job/run records (CONFIRMED)

| Job / run | Time | Input | Stages ran | Output | Failed stage | Record | Root error |
|---|---|---|---|---|---|---|---|
| TOBY_TEMPLATE_TEST | 2026-07-06 17:08 | footage/template test | render→quality | `8_WORKSPACE/TOBY_TEMPLATE_TEST/FINAL.mp4` (63.8s, score 97) | none | events.jsonl | — |
| TOBY_LABS_NEWS (good) | 2026-07-06 16:48 | news → 9:16 talking-head | scrape→script→voice→render→QA | `8_WORKSPACE/TOBY_LABS_NEWS/FINAL.mp4` (45.4s, 21 SFX, score 100) | none | events.jsonl | — |
| TOBY_LABS_NEWS (report) | 2026-07-06 15:11 | `https://labs.toby.vn/` | scrape (aborted) | none | **scrape** | `3_MEMORY/reports/TOBY_LABS_NEWS_20260706_151121.json` | "Scrape produced no usable script from https://labs.toby.vn/" — **input/research stage**, never reached render |
| prompts.chat | 2026-07-06 15:01 | `github:f/prompts.chat` | script(llm)→render→lint | `prompts.chat - SEOSONA.mp4` (55.3s, 14.8 MB) | none (5 lint warns) | factory_metrics.jsonl | prior 14:55 attempt rejected: 115.8s > 95s length gate |
| n8n | 2026-06-30 10:04 | `github:n8n-io/n8n` | full pipeline + eval_judge | `n8n - SEOSONA.mp4` (100 PASS) | none | `3_MEMORY/reports/n8n_20260630_100459.json` | — |

**Failure pattern:** only 2 hard failures across all records — both the **length gate** rejecting an already-rendered file (98.3s, 115.8s > 95s band). The render itself never crashed. The one FAILED report was an **upstream scrape** failure (site yielded no script), not a render fault. No Python tracebacks found in any `.log`.

## (B) Video-output inventory — ffprobe-verified (CONFIRMED)

| Path | Size | Duration | Resolution | Audio | Notes |
|---|---|---|---|---|---|
| `8_WORKSPACE/TOBY_LABS_NEWS/FINAL.mp4` | 17.7 MB | 47.0s | 1080×1920 | aac 48k stereo | h264 3.0 Mbps — valid, complete |
| `8_WORKSPACE/NEWS_SELFSUFF/FINAL.mp4` | 15.0 MB | 82.8s | 1080×1920 | aac 48k stereo | valid |
| `8_WORKSPACE/NEWS_TEST_FRAMEKHO/FINAL.mp4` | 7.4 MB | 25.7s | 1080×1920 | aac 48k stereo | valid |
| `8_WORKSPACE/prompts.chat/prompts.chat - SEOSONA.mp4` | 14.8 MB | 55.3s | 1080×1920 | aac 48k stereo | valid (matches metrics `ok:true`) |
| `8_WORKSPACE/adsbootcamp_11_07/_reasm_cache.mp4` | 73.0 MB | 96.3s | 1080×1920 | **none** | video-only intermediate of the STANDALONE `cinematic_reel.py` editor (not the factory engine) |
| `8_WORKSPACE/lipsync_demos/mascot_talking_PRODUCTION.mp4` | 0.53 MB | 8.4s | 842×1280 | aac 24k mono | lip-sync engine demo — valid |

All factory `FINAL/SEOSONA` outputs are well-formed 9:16 1080×1920 H.264 + AAC videos with real audio. `videos_on_disk: 45` per the live dashboard health endpoint.

## (C) Recent-log error signatures (CONFIRMED)

- `3_MEMORY/reports/TOBY_LABS_NEWS_20260706_151121.json` → `status: FAILED, quality_score: 0`, `"Fatal error: Scrape produced no usable script from: https://labs.toby.vn/"`. **Root = upstream scrape/research, not render.**
- `logs/metrics/events.jsonl` (newest, to 2026-07-11 15:41) → all recent entries are **moderation** events (`block` unsafe-term / off-platform-cta; `flag` unattributed-stat / absolute-claim / social-proof). Content-safety layer gating scripts, not crashes.
- `factory_metrics.jsonl` → 2 `ok:false`, both `"duration NNs out of band [15.0-95.0]"` (length gate).
- Render events @2026-07-06 16:23+ record `render_seconds: 1.78e9` — a **wall-clock timestamp leaked into an elapsed-seconds field** (metrics bug; video rendered fine). Confirmed live: dashboard `totals.avg_render_seconds: 743054812.9` (nonsense) — see [FAILURE_ANALYSIS](06_FAILURE_ANALYSIS.md) MEDIUM-1.
- `3_MEMORY/evaluation` → a `broken.mp4` scored 50 (blank frames + silent audio) = deliberate negative test fixture, not a factory output.

## (D) Has there EVER been a successful end-to-end production?

**CONFIRMED — YES, through render + voice + captions + QA.** Converging evidence:

1. **30 render records** in `factory_metrics.jsonl` (`ok:true` on 28), each with real duration/size/template/script-source.
2. **ffprobe-verified playable files** (e.g. `TOBY_LABS_NEWS/FINAL.mp4` 47s 1080×1920 H.264+AAC).
3. **Independent QA** — quality events 92–100 PASS; Gemini-vision `eval_judge` scored `n8n - SEOSONA.mp4` at 92 PASS.
4. Render logs show the full stack ran: caption-sync "real", 13–21 SFX cues, voice `vieneu:GiaBao`, brand `seosona`, multi-effect transitions.

**Caveats (this is the crux of "not good enough yet"):**
- **Publishing was never real** — only `logs/publish/receipts.jsonl` `"dry-run ok"`; `views_total: 0` everywhere. End-to-end is CONFIRMED only up to a QA-passed file; **publish-to-platform = INFERRED never done**.
- **QA gate is lenient vs. real craft** — every recent render self-scores 97–100 PASS, yet the **WPM is 212–228** (dashboard `recent_renders`), far above the healthy narration band 130–180. Feedback `weak_signals`: *"wpm outside the comfortable band (130-180) on 59% of takes."* The gate passes videos a human would call rushed. See [VIDEO_QUALITY_GAPS](07_VIDEO_QUALITY_GAPS.md).
- **Voice is off-brand fallback** — records show `vieneu:*`, i.e. the VieNeu backup, not the intended OmniVoice brand voice (INFERRED: OmniVoice GPU path not active during these runs).
- **Learning ledger lags** — `learning/ledger.json` `total_videos: 1, signal: "qa-only"`; the flywheel ingested one manifest while 30 renders exist. Feedback loop effectively not closed.
- **Newest work is a separate tool** — 2026-07-11 `adsbootcamp_11_07/` is the standalone `cinematic_reel.py` talking-head editor, distinct from the factory engine; so far only a video-only cache exists.

**Bottom line:** The factory has produced good-enough-to-pass 9:16 MP4s many times (most recent full batch 2026-07-06). It has **never published one** (dry-run only) and has **no view/performance feedback**, and its internal QA does not yet enforce human-perceived pacing/craft quality.
