# 🎬 SEOSONA Video Factory

SEOSONA Video Factory is an advanced, fully-automated multi-brand video production pipeline. Built deeply into the SEOSONA OS ecosystem, it handles everything from researching topics, writing SEO-optimized scripts, generating voiceovers, extracting perfectly-synced subtitles, dynamically recording headless browser B-Roll, to composing high-end cinematic visuals using **HyperFrames**.

## 🌟 Core Features

- **End-to-End Automation**: Input a raw text script or a simple URL, and receive a fully rendered MP4, SRT subtitle file, and 9:16/16:9 Thumbnail.
- **Smart Web Scraping & B-Roll**: Uses `crawl4ai` and `Playwright` to extract content from websites and automatically capture authentic scrolling footage or dashboard UI screenshots to use as B-Roll.
- **Cinematic Rendering**: Driven by **HyperFrames** HTML-based composition. Features fluid GSAP spring animations, glassmorphism UI cards, code diff mockups, and dynamic theme switching.
- **Perfect A/V Sync**: Features *Character-Threshold Matching* to align visual scene cuts perfectly with the AI TTS voice word boundaries. 
- **Flawless Pronunciation**: Employs an extensive internal `PRONUNCIATION_LEXICON` to allow the Vietnamese TTS engine to flawlessly pronounce complex English tech terms (like *Playwright*, *Next.js*, *Framework*) while keeping the on-screen text in professional English.

## 🏗️ Architecture

SEOSONA Video Factory operates on a highly modular architecture divided into several subsystems:

* `1_AGENTS/`: AI Roles (Scraper, Writer, Repurposer, Publisher).
* `2_SKILLS/`: Technical tools (TTS Generator, Voice Cloner, Visual Fetcher, Thumbnail Maker).
* `4_BRAIN/`: The Core Orchestrator (`workflow_router.py`, `pipeline_manager.py`).
* `5_FRAMEWORK/`: HyperFrames HTML renderer and legacy media tools.
* `6_SOP/`: Operational Guidelines and Brand Rules.
* `7_ASSETS/`: Media assets, SFX, BGM, Fonts, and Logos.

### Workflow Modes

1. **Create Mode**: `Text -> TTS -> Sync SRT -> Scene Planning -> HyperFrames Render -> Output`
2. **Scrape Mode**: `URL -> Scraper -> LLM Script Writer -> Playwright B-Roll -> HyperFrames Render -> Output`
3. **Repurpose Mode**: `Raw Video/SRT -> LLM Highlights -> Clipper -> HyperFrames Overlay -> Output`

## 🚀 Quick Start

Ensure that the Python environment is set up and `npx` (Node.js) is available on the PATH for HyperFrames.

```bash
# Activate Virtual Environment
.venv\Scripts\Activate.ps1

# Run the Workflow Router (Example: Create a video from a GitHub Repo URL)
python 4_BRAIN\workflow_router.py "https://github.com/DeusData/codebase-memory-mcp" seosona 9:16 "DeusData_News_Sync" create
```

## 🛠️ Requirements & Dependencies

- **Python 3.10+**
- **Node.js 18+** (for `npx` and HyperFrames)
- **FFmpeg 8.1+** (Must be in System PATH)
- **Playwright** (for Headless Browser B-Roll)
- **Edge-TTS / VieNeu / Fish Audio** (Voice Generation)
- **Gemini / OpenAI API Keys** (for Script Generation)

## 📌 Development Guidelines

- **HyperFrames Master Templates**: The system relies on templates stored in `5_FRAMEWORK/hf_cards/master_template_9_16`. All new UI designs must strictly extend from these standardized HTML/Tailwind components.
- **Animation Rules**: All animations MUST be done via GSAP Timelines (`window.__timelines["main"]`) for deterministic rendering. No CSS transitions or `setTimeout` should be used.
- **Pronunciation Engine**: Never write phonetic Vietnamese directly onto the video text. Update `4_BRAIN/news_video_standards.py` (`PRONUNCIATION_LEXICON`) to fix TTS mispronunciations.

---
*Powered by SEOSONA OS.*
