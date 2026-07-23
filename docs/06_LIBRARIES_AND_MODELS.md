# Libraries & AI Models Ecosystem

The SEOSONA Video factory makes maximum use of open source and the most advanced current AI models, combining JavaScript and Python to balance Graphics Processing Speed and Data Processing Power.

## 📦 1. JavaScript Ecosystem (Graphics & Rendering)

| Library | Main Role | Function Analysis |
| :--- | :--- | :--- |
| 🎬 **`hyperframes`** + **`@hyperframes/producer`** + **`@hyperframes/shader-transitions`** | HTML→video render engine | THE render engine — records animated HTML frame-by-frame via headless Chromium → MP4. Driven by `native_composer.py` (`node cli.js render`). Version-locked; bump only with a render smoke-test (`hf_blocks.render_block`). |
| 🌐 **`playwright`** (primary) / **`puppeteer-core`** | Headless browser | Screenshot step (`scripts/capture_shot.js`) for the `shot`/mockup component — Playwright via system Edge/Chrome channel; puppeteer-core is the fallback. |
| 🎞️ **`ffmpeg-static`** / **`ffprobe-static`** | ffmpeg binaries | Bundled ffmpeg/ffprobe used by the render + BGM-duck/SFX mix (invoked via subprocess, not a JS wrapper). |

> **Removed 2026-07-02 (unused JS deps):** `fluent-ffmpeg`, `sharp`, `jimp`, `cheerio`, `axios`, `dotenv`, `music-metadata` — none were imported by any first-party JS. That work lives in **Python**: image = Pillow, scraping = `researcher.py`, network = `requests`, env = `python-dotenv`.

## 🧠 2. Python Ecosystem & AI Models (Audio, Intelligence)

| Model / Library | Category | Capability Assessment |
| :--- | :--- | :--- |
| 🇻🇳 **`OmniVoice` (k2-fsa)** | AI Voice (Local · **the ONLY engine**) | Vietnamese-native voice model (code Apache-2.0; weights CC-BY-NC — owner-accepted risk, see `0_SETUP/MODELS.md`; 8482h), zero-shot + clones the CQA brand voice; runs GPU in the isolated torch-2.8 venv `7_ASSETS/voice/.venv-omnivoice`. THE brand voice for both brands, via `voice_router.py`. NO backup engine (2026-07-14): a failed synth returns None honestly. VieNeu / F5-TTS / edge-tts / kokoro / sherpa were all removed. |
| ⏱️ **`PhoWhisper-large-ct2`** | AI Analysis (ASR · **ONE engine ONE model**) | VinAI PhoWhisper-large (kiendt CTranslate2 build, float16) on `faster-whisper`/CTranslate2, cuda auto-detect, via `2_SKILLS/srt_maker/asr_router.py` (overrides: `SEOSONA_PHOWHISPER_MODEL` / `SEOSONA_ASR_DEVICE`). Most critical in the Forced-Alignment step to export the `words.json` file containing millisecond timestamps for Karaoke. openai-whisper + sherpa-onnx paths removed; the defective phowhisper-medium-ct2 was deleted (2026-07-14). |
| 🎬 **`moviepy`** | Video Editor | Joins Video + Audio blocks using static Python code. Used in combination with FFmpeg. |
| 🕵️ **`yt-dlp`** | Download Tool | A cross-platform super-grabber, extracting Video/Audio source from YouTube, TikTok, and X without being blocked. |
| 🐍 **`Pillow` / `BeautifulSoup4`** | Data Manipulation | Processes Pixel Arrays and parses the HTML DOM tree. |
