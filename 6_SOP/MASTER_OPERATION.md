# STANDARD OPERATION DOCUMENTS (MASTER OPERATION)
*Updated: 2026-06-19 — Version v3.0 (HyperFrames Engine)*

The system operates in a **Linear Pipeline** going from Router (`4_BRAIN/workflow_router.py`) to Workspace (`8_WORKSPACE/`).

## ENTRY POINT

```
python 4_BRAIN/workflow_router.py "<input>" [brand] [ratio] [project_name]
```

The router automatically detects the input:
- **YouTube URL** → Mode `download` (yt-dlp → repurpose)
- **Website URL** → Mode `scrape` (scraper_agent → TTS → render)
- **File .srt/.mp4** → Mode `repurpose` (clipper → shorts)
- **Text/Script** → Mode `create` (TTS → render)

---

## GENERAL ORDER OF OPERATION (END-TO-END)

### STEP 1: SCRIPTING / DATA INTAKE
- **Mode `create`:** Receive script text directly.
- **`scrape` mode:** `1_AGENTS/scraper_agent/scraper.py` scrapes content from URL.
- **Mode `repurpose`:** `1_AGENTS/repurposer_agent/srt_analyzer.py` parses SRT/MP4 files.

### STEP 2: VOICE SYNTHESIS (TTS)
- **Display/Pronunciation Split:** `4_BRAIN/news_video_standards.py` keeps the visible script and subtitles unchanged while creating a separate pronunciation script for TTS.
- **English Term Pronunciation:** Approved terms such as `AI`, `SEO`, `GitHub`, `Obscura`, `OpenAI`, and `YouTube` are pronounced via lexicon, but remain correctly spelled on screen.
- **Required Voice:** News videos require a male Southern Vietnamese profile. Use an approved VieNeu reference/preset when configured; otherwise fallback to Edge-TTS `vi-VN-NamMinhNeural`.
- **Engine:** `2_SKILLS/voice_cloner/fish_audio_api.py`.
- **Output:** `8_WORKSPACE/<ProjectName>/.temp/voice.mp3`

### STEP 3: IDENTIFY TIMESTAMPS
- Priority: TTS native word boundaries remapped back to exact display words.
- Fallback: `_estimate_word_level_data_from_script()` (word weight attribution).
- Fallback: `2_SKILLS/srt_maker/whisper_engine.py` (ASR).
- **Output:** `8_WORKSPACE/<ProjectName>/SRT/<ProjectName>.srt`

### STEP 4: ASSET GATHERING & SCENE GENERATION
- `_make_news_scene_copy()` parse sentence → optional component mode:
  - `dashboard`: When detecting numbers/percentages.
  - `source-card`: When mentioning the report source.
  - `screenshot`: Default (Browser mockup frame).
- Required SFX: real assets from `7_ASSETS/sfx/transitions/` and `7_ASSETS/sfx/pops/` when available; generated fallback only if the asset library is empty.
- Required BGM: real assets from `7_ASSETS/bgm/` when available; generated fallback only if the music library is empty.

### STEP 5: VIDEO RENDER (HyperFrames Core)
- `_write_hyperframes_render_project()` generates all HTML/CSS/GSAP.
- Render: `npx hyperframes@0.6.112 render --format mp4 --output <path>`
- **Frame 0 Hook:** Kicker + H1 always has 100% opacity at 0 second.

### STEP 6: THUMBNAIL
- `2_SKILLS/thumbnail_maker/thumbnail_generator.py` → HTML → Playwright → PNG.
- Text takes the verb `script_text`, not hardcode.
- **Output:** `8_WORKSPACE/<ProjectName>/Thumbnail/<ProjectName>_Thumbnail.png`
- Thumbnail generation is part of the production gate. Do not set `SEOSONA_SKIP_THUMBNAIL=1` for final delivery.

---

## OUTPUT STRUCTURE

```
8_WORKSPACE/<ProjectName>/
├── <ProjectName>.mp4 → Main video
├── SRT/<ProjectName>.srt → Subtitles
├── Thumbnail/<ProjectName>_Thumbnail.png → Cover image
└── .temp/ → Temp file (voice, hf_render/)
```

## SECURITY MECHANISM

- API Keys: Stored in `.env` (root), loaded by `python-dotenv`.
- Config: `system_config.yaml` uses `${VAR}` placeholder.
- `.gitignore`: Block `.env`, `8_WORKSPACE/*`, `3_MEMORY/*`, media files.
