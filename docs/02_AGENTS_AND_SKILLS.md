# List of Agents and Python Skills

This document lists the cognitive brain (Agents) and the execution hands and feet (Skills) of SEOSONA Video.
Source of truth: `1_AGENTS/ROSTER.md` and `2_SKILLS/README.md`.

## 🤖 Cognitive Layer: 10 AI Agents (`1_AGENTS/`)
All 10 agents below have real code and are called from the pipeline/workflow.
(The `personas/` directory contains the original personality definitions — it does not count as an agent.)

<details>
<summary><b>1. Orchestration & Remote Control Group (2 Agents)</b></summary>
<br>

- 👑 **`hermes_agent`**: Remote control bot via Telegram (`telegram_remote.py`) — `/news`, `/publish`, `/trend`, `/status`. Standalone entry point, not part of the pipeline dispatch.
- 🔥 **`trend_jacking_agent`**: Watches for trends (`trend_tracker.py`) then triggers the pipeline to make trend-following videos. Runs via `/trend` or cron.

</details>

<details>
<summary><b>2. Research & Data Ingestion Group (1 Agent)</b></summary>
<br>

- ⛏️ **`scraper_agent`**: Parses HTML/JSON, scrapes content from websites/news (`scraper.py`, `news_scraper.py`) to build scripts.

</details>

<details>
<summary><b>3. Content Creation & Scripting Group (4 Agents)</b></summary>
<br>

- 🎯 **`seo_writer_agent`**: Writes video scripts aligned with search behavior (`writer.py`).
- 🎠 **`carousel_writer_agent`**: Slide-style (carousel) content for LinkedIn/Instagram.
- 💬 **`social_media_agent`**: Social media captions following the PAS framework (clickbait, hooks).
- ✂️ **`repurposer_agent`**: Cuts long videos/podcasts into shorts/reels (`srt_analyzer.py`, `localizer.py`).

</details>

<details>
<summary><b>4. Optimization & Social Media Group (2 Agents)</b></summary>
<br>

- 📈 **`seo_optimizer`**: Optimizes YouTube metadata — title/tags/description + JSON-LD (`youtube_seo.py`).

</details>

<details>
<summary><b>5. Moderation & Publishing Group (3 Agents)</b></summary>
<br>

- 📊 **`analytics_feedback_agent`**: Analyzes retention, generates post-mortems (`feedback_generator.py`).
- 🚀 **`publisher_agent`**: Holds the publishing APIs (YouTube/TikTok/FB/Drive) — `publish_dispatch.py`. **Publishing requires explicit User permission.**

</details>

---

## 🛠️ Execution Layer: 7 Python Skills (`2_SKILLS/`)
Each skill below is wired into the pipeline/workflow (`2_SKILLS.<name>.<module>`).
9 unused skills have been removed from the project (see the README there).

<details>
<summary><b>🔊 Audio & Voice (2 Skills)</b></summary>
<br>

- 🗣️ **`voice_cloner`**: the ONLY voice router (`voice_router.synthesize_voice`) — **OmniVoice, the ONLY engine** (k2-fsa, local, VN-native, clones the CQA brand voice; runs in `7_ASSETS/voice/.venv-omnivoice`). NO backup: a failed synth returns None honestly. VieNeu / edge-tts / F5 / kokoro / sherpa / LoRA / fish all removed (2026-07-14).

</details>

<details>
<summary><b>📝 Subtitles (1 Skill)</b></summary>
<br>

- 📝 **`srt_maker`**: Generates SRT via `asr_router.py` — ONE engine ONE model: PhoWhisper-large-ct2 on faster-whisper/CTranslate2, cuda auto-detect (word-level timestamps for Karaoke).

</details>

<details>
<summary><b>🎞️ Image & Video (3 Skills + templates)</b></summary>
<br>

- ✂️ **`video_clipper`**: Cuts/formats clips (including vertical 9:16 shorts).
- 🖼️ **`thumbnail_maker`**: Generates HTML thumbnails.
- ⬇️ **`yt_downloader`**: Downloads source videos from YouTube (yt-dlp) — called from `workflow_router`.
- 🎨 **`hf_blueprints`**: HyperFrames scene blueprints/templates (HTML, not a Python skill).

</details>

<details>
<summary><b>✍️ Content & Processing (2 Skills)</b></summary>
<br>

- 🎠 **`carousel_maker`**: Turns text into a sequence of carousel images (called from `workflow_social_post`).

</details>

<details>
<summary><b>🗄️ Quarantined (9 Skills — not wired into the pipeline)</b></summary>
<br>

`audio_cleaner`, `audio_mixer`, `b_roll_fetcher`, `llm_processor`, `metadata_extractor`,
`script_writer`, `sfx_mixer`, `srt_parser`, `visual_fetcher` — moved to
(removed). They have real code but nothing calls them yet; restore when needed.

</details>
