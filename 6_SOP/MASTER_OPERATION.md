# STANDARD OPERATION DOCUMENTS (MASTER OPERATION)
*Updated: 2026-06-23 — Version v4.0 (SEOSONA OS Supergraph & HyperFrames Engine)*

The system operates on a **Supergraph DAG Architecture** going from Router (`4_BRAIN/workflow_router.py`) to `MAIN_PIPELINE`, running through the **OODA Loop** for auto-correction, and ending at `EVALUATE_NODE` for machine learning feedback.

Workflow boundaries are defined in `6_SOP/SEOSONA_WORKFLOW_BOUNDARY_MAP.md`.
Image workflows and video workflows are separate operating lanes.

## ENTRY POINT

```
python 4_BRAIN/workflow_router.py "<input>" [brand] [ratio] [project_name]
```

Canonical production commands:

```bash
npm run template:clone -- <video_path> <template_name>
npm run post:image -- <text_or_file>
npm run thumbnail:create -- <title_or_hook>
npm run video:news -- <script_or_file_or_url> [project_name] [aspect_ratio]
npm run video:course -- <script_or_file> [project_name] [aspect_ratio]
npm run start:queue      # Tự động xử lý hàng đợi từ 0_INPUT_INBOX/production_queue.yaml
npm run start:dashboard  # Khởi chạy Nightingale Dashboard UI tại localhost:5050
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

### STEP 7: EVALUATE & MACHINE LEARNING (SUPERGRAPH)
- `EVALUATE_NODE` catches the output from the main pipeline.
- `1_AGENTS/analytics_feedback_agent/feedback_generator.py` analyzes quality score and OODA retries.
- Output 1 (Human): `Báo_cáo_chất_lượng.md` bundled inside `8_WORKSPACE/<ProjectName>/`.
- Output 2 (Machine): `post_mortem_<id>.json` sent to `3_MEMORY/reports/`.

---

## OUTPUT STRUCTURE

```
8_WORKSPACE/<ProjectName>/
├── <ProjectName>.mp4 → Main video
├── SRT/<ProjectName>.srt → Subtitles
├── Thumbnail/<ProjectName>_Thumbnail.png → Cover image
├── Báo_cáo_chất_lượng.md → Quality score and ML feedback
└── .temp/ → Temp file (voice, hf_render/)
```

**Auto-Cleanup Rule:** If the pipeline fails and aborts before creating the core production files (`.mp4`, `.srt`), the system will automatically rollback and delete the `8_WORKSPACE/<ProjectName>/` directory to prevent empty zombie folders from cluttering the workspace.

## SECURITY MECHANISM

- API Keys: Stored in `.env` (root), loaded by `python-dotenv`.
- Config: `system_config.yaml` uses `${VAR}` placeholder.
- `.gitignore`: Block `.env`, `8_WORKSPACE/*`, `3_MEMORY/*`, media files, `node_modules`, `__pycache__`, and `renders/`.
