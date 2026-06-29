# SEOSONA Video — Observability (Phase 6)

The single place that **connects** every health/quality signal that used to be scattered
across the engine, the scorer, the feedback agent, and the queue. No paid API — it just
reads/writes local files.

## The map (who emits what → where → who reads it)

```
 EMITTERS (scattered modules)                 HUB                        VIEW
 ─────────────────────────────               ─────                      ──────
 4_BRAIN/native_composer.make_video ──┐
   → record("render", wpm, sync, …)    │
 4_BRAIN/video_engine.score_output  ───┼─▶ 9_DASHBOARD/obs_metrics.py ─▶ 9_DASHBOARD/server.py
   → record("quality", score, …)       │     • record() → logs/metrics/events.jsonl  (/api/metrics,
 scripts/queue_processor.py ───────────┘     • read_health() merges:        /api/health)
   → logs/queue/<run>/run.jsonl                 events.jsonl + queue       ─▶ templates/index.html
 scripts/daily_production.py                     run.jsonl + daily logs          (auto-refresh 5s)
   → logs/daily/<ts>.log                         + 8_WORKSPACE/*.mp4
 1_AGENTS/analytics_feedback_agent/            (derives: caption-sync %,
   feedback_generator.py  (feedback loop)       quality pass %, avg render s)
```

**`9_DASHBOARD/obs_metrics.py` is the hub** (lives here, next to the server — one home).
Everything connects through it: emitters call
`record(event, **fields)`; the dashboard calls `read_health()`. To add a new signal,
call `record(...)` from wherever it happens — the dashboard picks it up automatically.

## Run it
**Usually you don't have to.** Using SEOSONA Video auto-starts it: `daily_production` and
`queue_processor` call `autostart.ensure_running()` → the dashboard comes up in the background
the first time you run a batch, idempotently (next run says "already live"), and keeps running
after the CLI exits. Opt out with `SEOSONA_DASHBOARD=0`. Then just open http://localhost:5050.

Manual options:
```
deploy\open_dashboard.bat      # ONE double-click: starts server + opens the browser
npm run start:dashboard        # or start manually → http://localhost:5050
python 9_DASHBOARD/obs_metrics.py  # print the health snapshot as JSON (no server)
curl localhost:5050/api/health # the snapshot for external monitors
```
The page auto-refreshes every 5s (near-realtime; it updates when a render/queue/feedback
event is written — a video appears when its render finishes, not mid-render).

### Always-on (auto-start at Windows login — no command ever)
```powershell
schtasks /Create /TN "SEOSONA Dashboard" /TR "\"%CD%\deploy\open_dashboard.bat\"" /SC ONLOGON /F
schtasks /Delete /TN "SEOSONA Dashboard" /F   # to undo
```
After this it launches itself every time you log in; just open http://localhost:5050.

## What the dashboard shows
- **KPIs**: videos on disk · queue pending · caption-sync real % · avg render seconds ·
  avg quality · quality-pass %.
- **Recent renders**: time · name · brand · duration · **wpm** · **caption-sync** (real/estimated)
  · sfx · render seconds · quality score. (wpm + sync are the clone-stability signals.)
- **Queue runs** (Phase 3): ok / failed / skipped per run.
- **Queue & done** counts.

## Feedback loop (remaining Phase 6 depth)
`1_AGENTS/analytics_feedback_agent/feedback_generator.py` + `4_BRAIN/quality_scorer.py`
exist and are surfaced here. Closing the *automatic* loop (scores → tune the quality gate →
next batch improves) is the deeper Phase-6 task; the metrics foundation for it is now in place.

## Why no external repo was adopted
Searched the inventory for dashboard/monitoring repos: the candidates (ToolJet — a whole
low-code platform, Prometheus — a full monitoring stack) would massively over-engineer a
local log-reader and conflict with the free/lean rule. A small Flask page over `obs_metrics`
is the right size. (Same principle as [[no-recreate-deprecated-systems]].)
