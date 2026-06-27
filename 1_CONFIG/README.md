# 1_CONFIG — credentials & secrets (the only place keys live)

Central management of every API key, token, password, OAuth file, and account id
the factory needs to **upload finished products** (YouTube, TikTok, Facebook Fanpage,
Google Drive) and to run **remote control** (Telegram). Split out here so secrets are
in one auditable place, never scattered through the code.

## Layout
```
1_CONFIG/
├── credentials_manager.py     ← the loader (committed). import: `from credentials_manager import creds`
├── credentials/
│   ├── *.example.json         ← templates (committed) — what each platform needs
│   └── *.json                 ← REAL secrets (gitignored — never committed)
└── README.md
```
Root `.env` still works (backward compatible) — the manager loads it automatically.

## How secrets resolve (first hit wins)
1. **Environment variable** (root `.env`, auto-loaded)
2. **`1_CONFIG/credentials/<platform>.json`** (structured per-platform file)
3. default / `None` → caller skips + warns (never crashes)

## Use it
```python
from credentials_manager import creds
creds.get("telegram", "bot_token")                  # value or None
creds.has("google_drive", "service_account_file")   # bool — gate an upload
creds.require("facebook", "page_token", "page_id")  # dict, or actionable error
```
Check what's configured:  `python 1_CONFIG/credentials_manager.py`

## Configure a platform
Pick ONE of:
- **env**: set the var in `.env` (see `.env.example` for names), or
- **file**: `cp 1_CONFIG/credentials/<platform>.example.json 1_CONFIG/credentials/<platform>.json` and fill it.

| Platform | Fields | Where to get it |
|----------|--------|-----------------|
| `youtube` | `oauth_file`, `data_api_key` | Google Cloud OAuth client_secret.json (used by `yutu` CLI) |
| `tiktok` | `access_token` | TikTok Content Posting API |
| `facebook` | `page_token`, `page_id` | Graph API long-lived Page token + Fanpage id |
| `google_drive` | `service_account_file`, `folder_id` | Google service-account JSON + target folder id |
| `telegram` | `bot_token`, `chat_id` | @BotFather + your chat id |

Env-only keys (read from `.env`, no JSON file): `openai` (`OPENAI_API_KEY`),
`pexels` (`PEXELS_API_KEY`), `9router` — see `_ENV_MAP` in `credentials_manager.py`.

## Adding a new platform
Add its `(platform, field) → ENV_VAR` rows to `_ENV_MAP` in `credentials_manager.py`,
drop a `<platform>.example.json`, and the gitignore rule already protects the real file.

> ⚠️ Never commit a real `*.json` (only `*.example.json`) or paste a key into tracked
> code. The gitignore enforces this, but treat it as a hard rule.
