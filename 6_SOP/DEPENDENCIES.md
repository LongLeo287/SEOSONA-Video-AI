# SEOSONA Video — Dependencies & APIs status  ·  2026-06-29

> Verdict: **for free/local video production the stack is COMPLETE.** Every engine and
> library needed to make a finished video end-to-end is present, with **zero paid APIs**
> (proven by full renders this session). Paid/optional pieces are wired but OFF — plug
> credentials later, no code change.

## ✅ Engines (all present, free/local)
| Engine | Role | Status |
|--------|------|--------|
| VieNeu (v3turbo) | Vietnamese TTS + voice clone | ✅ |
| HyperFrames (node, `node_modules/hyperframes`) | HTML/CSS+GSAP → MP4 render | ✅ CLI present |
| ffmpeg / ffprobe | mux, mix, atempo, encode | ✅ (bundled binaries) |
| faster-whisper / PhoWhisper | ASR word timing (caption sync) | ✅ |
| moviepy | duration probe / audio helpers | ✅ |

## ✅ Python libs (all present, free)
`yaml · requests · python-dotenv · Pillow · numpy · soundfile · faster_whisper · moviepy` — all OK.

## ⚙️ Optional / paid (wired, OFF by default — plug later)
| Item | Needed for | How to enable |
|------|-----------|---------------|
| `google-generativeai` lib + `GEMINI_API_KEY` | LLM scene-planner path (nicer headings/components) | `pip install google-generativeai` + key. **Not required** — deterministic planner is the free default and falls back automatically. |
| `OPENAI_API_KEY` | alt LLM path | optional |
| Telegram `bot_token`+`chat_id` | **FREE publish** (instant, no app review) | fill `1_CONFIG/credentials/telegram.json` |
| YouTube / TikTok / Facebook | publish | approved app/OAuth — paid/effort, later |
| `google_drive` service account | publish to Drive | later |
| `pexels` api_key | stock images | ✅ already set (free tier) |
| `9router` | image-gen gateway (posters) | paid, later |

## How publish stays safe without keys
`SEOSONA_PUBLISH` (e.g. `telegram,youtube`) drives `publish_dispatch`; every destination is
**credential-gated** → missing key = "skipped", never a crash. With nothing set, the system
is render-only. Check any time: `python 1_CONFIG/credentials_manager.py`.

## Bottom line
- **Make videos (free): ready now.** Nothing else to install.
- **Publish free (Telegram): ready** — just add a bot token when you want it.
- **LLM planner / paid publish: scaffolded** — add lib+key later, zero code change.
