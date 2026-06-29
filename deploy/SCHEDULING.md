# SEOSONA Video — Daily auto-production (Phase 5: SCALE)

Everything below is **built and ready**. Enabling unattended daily output is one
command — no code changes. Free/local by default; publishing turns on only when you
set credentials.

## What runs each day
`npm run daily` → `scripts/daily_production.py`:
1. Processes the inbox queue (`0_INPUT_INBOX/production_queue.yaml`) via the reliable
   Phase-3 processor (retry · per-item isolation · timeout · idempotency · logging).
2. Optional GitHub news batch with `--news sources.txt` (rotates templates so the feed
   isn't repetitive).
3. Publishes each output **iff** `SEOSONA_PUBLISH` is set (else render-only).

Free by default: render = VieNeu (local) + HyperFrames (local); publish target Telegram
is free (bot token only). YouTube/TikTok/Facebook need approved apps/OAuth — wire later.

## Enable on Windows (Task Scheduler) — one command
```powershell
# every day at 08:00, run the launcher
schtasks /Create /TN "SEOSONA Daily Video" /TR "\"%CD%\deploy\run_daily.bat\"" /SC DAILY /ST 08:00 /F
# check / run now / remove
schtasks /Run    /TN "SEOSONA Daily Video"
schtasks /Query  /TN "SEOSONA Daily Video"
schtasks /Delete /TN "SEOSONA Daily Video" /F
```
To also publish (free): `setx SEOSONA_PUBLISH telegram` once, then re-create the task.

## Enable on Linux/macOS (cron)
```cron
# m h dom mon dow   command   (08:00 daily)
0 8 * * *  cd /path/to/SEOSONA\ Video && SEOSONA_PUBLISH=telegram npm run daily >> logs/daily/cron.out 2>&1
```

## Turn publishing on later (free first)
1. `cp 1_CONFIG/credentials/telegram.example.json 1_CONFIG/credentials/telegram.json`
   and fill `bot_token` (from @BotFather) + `chat_id`. **Free, instant, no app review.**
2. `setx SEOSONA_PUBLISH telegram` (add `,google_drive,youtube` once those are wired).
3. Verify wiring any time: `python 1_CONFIG/credentials_manager.py` (shows YES/-- per key).

## Feed it work
- Drop scripts/URLs into `0_INPUT_INBOX/production_queue.yaml` (or `pending_files/`).
- Or keep a `sources.txt` of GitHub URLs and run `npm run daily -- --news sources.txt`.
- Outputs land in `8_WORKSPACE/`; logs in `logs/daily/` and `logs/queue/`.
