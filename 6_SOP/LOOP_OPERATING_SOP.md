# SOP — Operating the SEOSONA Video loop safely

Applies Loop Engineering's three disciplines + first-loop checklist to SEOSONA's
queue → daily → feedback loop. Knowledge: `2_KNOWLEDGE/loop-engineering/README.md`.
Goal: run unattended **without letting the loop amplify errors**.

## Before any unattended run — set the ceilings (circuit breaker)
The guard (`scripts/loop_guard.py`) is wired into `queue_processor`. Defaults bound risk;
override per environment if needed:
| Env var | Default | Meaning |
|---|---|---|
| `SEOSONA_MAX_ITEMS_RUN` | 20 | stop after N items in one run |
| `SEOSONA_MAX_ITEMS_DAY` | 100 | stop after N items in a day (persists in `logs/loop_guard_state.json`) |
| `SEOSONA_MAX_WALL_SECONDS` | 7200 | stop after 2h wall-clock per run |
| (per-item) `--timeout` | 1800s | a hung render can't block the queue |
| (per-item) `--retries` | 2 | bounded retry, not infinite |

**Kill switch:** create the file `0_INPUT_INBOX/STOP` → the loop halts before the next item
(remaining items stay in the queue). Delete it to resume. Use this to abort a runaway batch.

## The three disciplines (do these, not optional)
1. **Read a sample daily.** Don't watch every video — open the dashboard
   (`http://localhost:5050`), read the *recent renders* table, and actually WATCH one
   representative output. If you can't explain why it looks/sounds the way it does →
   comprehension rot; investigate before scaling.
2. **Ceilings before shipping.** Never launch an unattended batch without the guard limits
   above being sane for that run. They are circuit breakers (bound risk), not cost-saving.
3. **Leave a door open.** Publishing is opt-in (`SEOSONA_PUBLISH`); nothing auto-publishes.
   Keep at least this one human checkpoint — review on the dashboard before turning publish on.

## First-loop checklist — SEOSONA status (all ✅)
- ✅ Discovery source: `discovery.py` (sources.txt → queue) + queue / `--news` file
- ✅ State file: ledger + events.jsonl + feedback_state.json
- ✅ Evaluator that can say "no": independent `4_BRAIN/evaluator.py` (skeptical, inspects the
  real MP4) gating publish, plus `quality_scorer` (metadata) and `content_moderation` (pre-render)
- ✅ Token/run ceiling: `loop_guard` (run/day/wall + STOP kill-switch)
- ✅ Human review: publish opt-in
- ✅ Isolation per parallel task: renders → `queue_processor --concurrency N` (each render is its
  own subprocess + project_dir); code edits → `scripts/worktree.py` (one git worktree per task)

## Parallel rendering
`npm run daily` honors `SEOSONA_CONCURRENCY` (default 1). Raise it only after confirming a single
render is reliably gated by the evaluator (Loop Engineering: add parallelism last). Each parallel
render is isolated; the queue commits results in the main thread so state never corrupts.

## Daily operating procedure
1. Feed work: add items to `0_INPUT_INBOX/production_queue.yaml` (or `pending_files/`), or keep
   a `sources.txt` for `--news`.
2. Run / schedule: `npm run daily` (auto-starts the dashboard + runs the guarded queue +
   recomputes the feedback gate). Schedule via `deploy/SCHEDULING.md`.
3. Watch: dashboard KPIs + recent renders. Investigate any `caption-sync=estimated` cluster
   (clone instability) and any quality FAIL.
4. If something looks wrong: `touch 0_INPUT_INBOX/STOP` to halt; fix; delete STOP to resume.

## What's intentionally kept opt-in (the open doors)
- Auto-publish stays opt-in (`SEOSONA_PUBLISH` unset by default) — the human-review door.
- Parallel rendering defaults to 1 (`SEOSONA_CONCURRENCY`) — raise deliberately, never blindly.
- Discovery reads a maintained `sources.txt` — fully automatic feed ingestion (RSS/trending)
  is left off until the content-moderation + evaluator gates are trusted at scale.
