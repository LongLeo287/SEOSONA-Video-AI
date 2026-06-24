# hermes_agent — remote brain

Hermes is the remote-control brain for the factory + a pre-render script reviewer.

## Files
- `telegram_remote.py` — control the factory from Telegram (produce, list, publish, review).
- `hermes_local.py` — `ask_local_hermes(text)` script review via OpenAI (needs `openai.api_key`).

## Run the Telegram remote
1. Configure credentials (see `1_CONFIG/README.md`):
   - `telegram.bot_token` — from @BotFather
   - `telegram.chat_id`  — your chat id (the bot answers ONLY this id)
2. Start it:
   ```bash
   python 1_AGENTS/hermes_agent/telegram_remote.py
   ```
3. From Telegram:
   | Command | Does |
   |---------|------|
   | `/news <topic>` | produce a Vietnamese tech-news video, sends the mp4 back |
   | `/list` | list finished products in `8_WORKSPACE` |
   | `/status` | last job status |
   | `/publish <name> <dests>` | e.g. `/publish MyProj google_drive,youtube` |
   | `/review <text>` | Hermes reviews a script snippet |

Security: stdlib-only long-polling; the bot ignores every chat except the configured
`chat_id`. Unconfigured → prints how to set it up and exits (no hang).
Publishing is credential-gated through `1_CONFIG` — missing keys are skipped, not fatal.
