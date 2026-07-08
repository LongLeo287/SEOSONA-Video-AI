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
| 🇻🇳 **`OmniVoice` (k2-fsa)** | AI Voice (Local · **PRIMARY engine**) | Vietnamese-native voice model (Apache-2.0, 8482h), clones the CQA brand voice; runs GPU in an isolated torch-2.8 venv. THE brand voice for both brands, via `voice_router.py`. |
| 🇻🇳 **`VieNeu-TTS`** | AI Voice (Local · **backup**) | Vietnamese TTS/clone (CPU/ONNX). Used ONLY when OmniVoice can't run. |
| ⏱️ **`OpenAI-Whisper`** | AI Analysis (ASR) | The `faster-whisper` build. Most critical in the Forced-Alignment step to export the `words.json` file containing millisecond timestamps for Karaoke. |
| 🎬 **`moviepy`** | Video Editor | Joins Video + Audio blocks using static Python code. Used in combination with FFmpeg. |
| 🕵️ **`yt-dlp`** | Download Tool | A cross-platform super-grabber, extracting Video/Audio source from YouTube, TikTok, and X without being blocked. |
| 🐍 **`Pillow` / `BeautifulSoup4`** | Data Manipulation | Processes Pixel Arrays and parses the HTML DOM tree. |
