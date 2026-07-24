# 02 — TECH STACK & SERVICES

> No secret values are printed anywhere — ENV VARS are listed by NAME only.
> Legend: **IMPL** = implemented · **STUB** = adapter present but non-functional · **KEYLESS** = works with no key · **NOT INTEGRATED** = key declared, no code.

## (A) Tech stack (CONFIRMED)

| Layer | Choice | Evidence |
|---|---|---|
| Languages | Python 3.11 (primary), Node.js ≥20 (render/CLI bridge) | `requirements.txt`, `package.json`, `0_SETUP/ENVIRONMENT.md:7` |
| Package managers | npm; pip + **uv** (venvs) | `0_SETUP/ENVIRONMENT.md:35` |
| Python envs | 3 isolated venvs: inference (torch 2.5.1+cu121), OmniVoice GPU (torch 2.8+cu128), training (obsolete) | `0_SETUP/ENVIRONMENT.md:11-16` |
| Render engine | **HyperFrames** `0.7.24` (Chromium/Puppeteer render) + **`native_composer.py`** (ffmpeg-static direct) | `package.json:59-67`, `4_BRAIN/native_composer.py` |
| Node deps | `hyperframes`, `@hyperframes/producer`, `@hyperframes/shader-transitions`, `ffmpeg-static`, `ffprobe-static`, `playwright@1.61`, `puppeteer-core@25` | `package.json` |
| Media libs | moviepy, Pillow, faster-whisper/ctranslate2, sherpa-onnx, underthesea, vietnormalizer, deep-translator, markitdown | `requirements.txt` |
| Web framework | **Flask** (dashboard only, port 5050) | `9_DASHBOARD/server.py` |
| Database | **NONE** — no SQL/ORM/DB. State = JSON/JSONL/YAML on disk | (no DB deps) |
| Queue | **File/process-based** — `scripts/queue_processor.py` with `_kill_tree` subprocess bounding; no Redis/Celery/RabbitMQ | `queue_processor.py` |
| Storage | Local filesystem (`8_WORKSPACE`, `7_ASSETS`); optional Google Drive (service account) | `1_CONFIG/credentials_manager.py` |
| Auth/secrets | `1_CONFIG/credentials_manager.py` (env-first → `1_CONFIG/credentials/<platform>.json`); `python-dotenv` loads root `.env` | `credentials_manager.py:1-88` |
| Deployment | Windows-first `.bat`/`.ps1` + Task Scheduler (`deploy/`). **No Docker/compose** (absent) | `setup.bat`, `0_SETUP/bootstrap.ps1`, `deploy/SCHEDULING.md` |
| Config | `system_config.yaml`, `seosona.project.json`, `1_CONFIG/factory_policy.yaml` | — |

**No container/orchestration layer, no database, no message broker.** This is a single-machine, file-driven Python + Node factory.

## (B) Provider integrations

### LLM (core cascade — `4_BRAIN/llm_engine.py`)
| Provider | Role | Status | Evidence | Env name(s) |
|---|---|---|---|---|
| Google Gemini | primary | IMPL | `_gemini_scenes` L921 (`google-genai`) | `GEMINI_API_KEY`, `GEMINI_API_KEY_2..10`, `GEMINI_API_KEYS` |
| Z.ai GLM | free cloud | IMPL | `_zai_scenes` L976 | `ZAI_API_KEY`, `SEOSONA_ZAI_MODEL` |
| NVIDIA NIM (Llama-3.3-70B) | free cloud | IMPL | `_nvidia_scenes` L997 | `NVIDIA_API_KEY`, `SEOSONA_NVIDIA_MODEL` |
| OpenAI GPT-4o-mini | fallback | IMPL | `_openai_scenes` L961 | `OPENAI_API_KEY` |
| Ollama (local) | keyless floor | IMPL/KEYLESS | `_try_ollama_json` L827 | `SEOSONA_OLLAMA_MODEL`, `OLLAMA_HOST` |
| Anthropic Claude | dormant tier | IMPL (dormant) | `_anthropic_scenes` L1018 | `ANTHROPIC_API_KEY`, `SEOSONA_ANTHROPIC_MODEL` |
| Offline NLP router | deterministic floor | IMPL/KEYLESS | `_smart_offline_router` L638 | none |

### Image generation
| Provider | Status | Evidence | Env |
|---|---|---|---|
| NVIDIA FLUX.1-schnell | IMPL | `4_BRAIN/image_gen.py:24` (returns None w/o key) | `NVIDIA_API_KEY` |
| Stability | NOT INTEGRATED | key in `.env`, no code | `STABILITY_API_KEY` |

### Video generation (Engine #6 — Seedance, standalone)
| Provider | Status | Evidence | Env |
|---|---|---|---|
| BytePlus/ModelArk (official) | **STUB** (raises) | `seedance_engine.py:197`, excluded from `available()` | `ARK_API_KEY`, `ARK_SEEDANCE_ENDPOINT` |
| fal.ai (reseller) | IMPL | `_PROVIDERS` L48, `queue.fal.run` | `FAL_KEY`, `SEEDANCE_FAL_KEY`, `SEEDANCE_FAL_MODEL` |
| Replicate (reseller) | IMPL | `_PROVIDERS` L49 | `REPLICATE_API_TOKEN`, `SEEDANCE_REPLICATE_TOKEN`, `SEEDANCE_REPLICATE_MODEL` |
| LTX-Video (local, Apache-2.0) | IMPL/KEYLESS | `scripts/ltx_video.py`, gated on `ltx_ready()`; **weights marker PRESENT** | `SEOSONA_LTX_*` |

No key + no LTX weights → writes prompts/shotlist, never fakes a render (`seedance_engine.py:24-27`).

### TTS (voice)
| Provider | Status | Evidence | Env |
|---|---|---|---|
| OmniVoice (k2-fsa, GPU brand voice) | IMPL | `omnivoice_engine.py`, `.venv-omnivoice` PRESENT | `SEOSONA_OMNIVOICE_*`, `HF_TOKEN` |
| VieNeu-TTS v3 Turbo (backup) | IMPL | `vieneu_engine.py` | `SEOSONA_VIENEU_VOICE` |
| voice_router (OmniVoice→VieNeu) | IMPL | `voice_router.py` | — |
| F5 / edge-tts / fish_audio | REMOVED | `MODELS.md:21-24`; `FISH_AUDIO_API_KEY` in `.env` is **stale** | (stale) |

**Note:** the 2026-07-06 render records show `vieneu:*` — the factory was running on the **backup** voice, not the OmniVoice brand voice.

### STT / ASR
| Provider | Status | Evidence | Env |
|---|---|---|---|
| PhoWhisper-medium CT2 (primary) | IMPL | `asr_router.py:33`; model PRESENT | `SEOSONA_ASR`, `SEOSONA_PHOWHISPER_MODEL` |
| faster-whisper / openai-whisper (backups) | IMPL | `asr_router.py:49,65` | `SEOSONA_WHISPER_SIZE` |
| sherpa-onnx (VN offline) | IMPL | `sherpa_vn_engine.py:80` | `SEOSONA_SHERPA_*` |

### Lip-sync / avatar / motion (standalone engines, **not auto-wired**)
| Provider | Status | Runtime dep present? | Evidence |
|---|---|---|---|
| MuseTalk (#3b) | IMPL | **`.venv-musetalk` MISSING** | `scripts/lipsync_musetalk.py` |
| SadTalker (#3) | IMPL | **`.venv-sadtalker` + repo MISSING** | `scripts/portrait_avatar.py` |
| LivePortrait (#5) | IMPL | **`.venv-liveportrait` + weights MISSING** | `scripts/liveportrait_motion.py` |
| Unified lipsync service | IMPL (orchestrator) | depends on above | `4_BRAIN/lipsync_service.py` |
| Mascot 2D rig | IMPL | Pillow/numpy (present) | `scripts/mascot_talk.py` |
| HeyGen native API | Vendored `.agents` skill (not core) | — | `.agents/skills/heygen-native-api/` |

### Music / BGM / SFX
| Provider | Status | Env |
|---|---|---|
| Openverse → Jamendo (CC, keyless) | IMPL/KEYLESS | — |
| SFX library (curated `7_ASSETS/audio/sfx`) | IMPL | `SEOSONA_BEAT_SFX` |
| Lyria / ElevenLabs | Vendored `.agents` skills (not core) | `GOOGLE_API_KEY`, `ELEVENLABS_API_KEY` |

### Stock media / research / publishing
| Provider | Category | Status | Env |
|---|---|---|---|
| Pexels | photos | IMPL | `PEXELS_API_KEY` |
| Pixabay | b-roll/music | IMPL | `PIXABAY_API_KEY` |
| yt-dlp | footage | IMPL/KEYLESS | — |
| Firecrawl | search+scrape | IMPL (optional key) | `FIRECRAWL_API_KEY` |
| Google News RSS + DuckDuckGo HTML | research | IMPL/KEYLESS | — |
| Google PageSpeed | CWV data | IMPL | `PAGESPEED_API_KEY` |
| GitHub API (`gh`) | repo fetch | IMPL | `GITHUB_TOKEN` |
| Crawl4AI / Browserbase | scrape | NOT INTEGRATED | `CRAWL4AI_API_TOKEN`, `BROWSERBASE_*` |
| YouTube (yutu CLI) | publish | IMPL (OAuth external) | `YOUTUBE_DATA_API_KEY`, `YOUTUBE_OAUTH_FILE` |
| YouTube/TikTok (Playwright) | publish | IMPL (human-gated, dry-run only in practice) | `SEOSONA_PUBLISH_LIVE` |
| TikTok / Facebook | publish | config-only stub | `TIKTOK_ACCESS_TOKEN`, `FB_PAGE_TOKEN`, `FB_PAGE_ID` |
| Google Drive | storage | IMPL | `GDRIVE_*` |
| Telegram remote | control | IMPL (gated) | `TELEGRAM_BOT_TOKEN` (**MISSING**), `TELEGRAM_CHAT_ID` |
| HuggingFace Hub | model dl | IMPL | `HF_TOKEN`, `HUGGINGFACE_TOKEN` |
| AWS | storage | NOT INTEGRATED | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| `performance_ingest` YouTube Analytics | metrics pull | **STUB (`return None # TODO`)** | — |

## (C) ENV VAR NAMES (names only — no values)

`.env` PRESENT; `.env.example` PRESENT. NAMES declared in `.env`:
`OPENAI_API_KEY, GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3, PEXELS_API_KEY, FIRECRAWL_API_KEY, CRAWL4AI_API_TOKEN, BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID, GITHUB_TOKEN, HF_TOKEN, HUGGINGFACE_TOKEN, YOUTUBE_DATA_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, PAGESPEED_API_KEY, ZAI_API_KEY, SEOSONA_ZAI_MODEL, ANTHROPIC_API_KEY, SEOSONA_ANTHROPIC_MODEL, SEOSONA_OLLAMA_MODEL, NVIDIA_API_KEY, PIXABAY_API_KEY, GOOGLE_API_KEY, ELEVENLABS_API_KEY, HEYGEN_API_KEY, HYPERFRAMES_API_KEY, STABILITY_API_KEY, FISH_AUDIO_API_KEY`.

Documented in `.env.example` but not yet in `.env`: `YOUTUBE_OAUTH_FILE, TIKTOK_ACCESS_TOKEN, FB_PAGE_TOKEN, FB_PAGE_ID, GDRIVE_SERVICE_ACCOUNT_FILE, GDRIVE_FOLDER_ID, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SEOSONA_NVIDIA_MODEL, SEOSONA_REQUIRE_LLM`.

Additional secret NAMES referenced in code: `HEYGEN_WEBHOOK_SECRET, GDRIVE_CREDS, GDRIVE_TOKEN, ARK_API_KEY, FAL_KEY, SEEDANCE_FAL_KEY, REPLICATE_API_TOKEN, SEEDANCE_REPLICATE_TOKEN, GEMINI_API_KEY_4..10`.

Model/endpoint selectors: `SEOSONA_ZAI_MODEL, SEOSONA_ANTHROPIC_MODEL, SEOSONA_NVIDIA_MODEL, SEOSONA_OLLAMA_MODEL, SEOSONA_OLLAMA_VISION, OLLAMA_HOST, ARK_SEEDANCE_ENDPOINT, SEEDANCE_FAL_MODEL, SEEDANCE_REPLICATE_MODEL, SEOSONA_LTX_MODEL/BASE/STEPS/OFFLOAD/TIMEOUT/VAE_TILING, SEOSONA_HIGGS_TOKENIZER, SEOSONA_OMNIVOICE_MODEL/TIMEOUT, SEOSONA_VIENEU_VOICE, SEOSONA_ASR/ASR_DEVICE/PHOWHISPER_MODEL/WHISPER_SIZE/SHERPA_MODEL/SHERPA_TYPE`.

Feature/operational flags (non-secret, SEOSONA_*): `SEOSONA_ROOT, SEOSONA_REQUIRE_LLM, SEOSONA_LLM_COMPONENTS, SEOSONA_LLM_DIRECTOR, SEOSONA_USE_BLOCKS, SEOSONA_TEMPLATE_ROTATE, SEOSONA_DYNAMIC_SCENES, SEOSONA_SCENES, SEOSONA_RENDER_QUALITY/WORKERS/GPU, SEOSONA_X264_PRESET, SEOSONA_TARGET_WPM, SEOSONA_BEAT_SFX, SEOSONA_VERIFY_STRICT, SEOSONA_AUTOFIX, SEOSONA_STRICT_VIETNAMESE_NEWS, SEOSONA_MODERATION, SEOSONA_PUBLISH, SEOSONA_PUBLISH_LIVE, SEOSONA_SKIP_EVAL, SEOSONA_RESEARCH/RESEARCH_TIMEOUT/SEMANTIC_RESEARCH, SEOSONA_CONCURRENCY, SEOSONA_MAX_WALL_SECONDS, SEOSONA_DASHBOARD/DASHBOARD_PORT, SEOSONA_KEY_COOLDOWN_S` (plus many more — full list in agent evidence).

## (D) LLM cascade order (CONFIRMED)

1. **Scripts / course-plan** (`generate_json_strict`, real-LLM-only, `llm_engine.py:1051`):
   Gemini (rotating keys) → Z.ai → NVIDIA → OpenAI → Ollama → Claude → None (caller aborts if `SEOSONA_REQUIRE_LLM=1`). Per-key 429 circuit-breaker.
2. **Thumbnail / carousel / social** (`generate_json_from_prompt`, `llm_engine.py:722`):
   Gemini (+Flash backup, backoff) → OpenAI → Z.ai → NVIDIA → Ollama → **Smart Offline NLP router** (deterministic, keyless).

## Key findings
- **STUBs:** `seedance_engine._byteplus_generate` (raises); `performance_ingest._youtube_metrics` (`return None`).
- **NOT INTEGRATED** (keys declared, no code): AWS, Crawl4AI, Browserbase, Stability. **Stale:** `FISH_AUDIO_API_KEY`.
- **Vendored-only (not in core pipeline):** HeyGen, ElevenLabs, Lyria (live under `.agents/skills/`).
- **Missing runtime deps** blocking avatar/lipsync engines: `.venv-musetalk`, `.venv-sadtalker`, `.venv-liveportrait` (+weights), `TELEGRAM_BOT_TOKEN`, all paid Seedance keys.
