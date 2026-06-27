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
npm run make:video -- <github_url_or_owner/name>   # GitHub → branded video (auto template)
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
- **Engine:** `2_SKILLS/voice_cloner/voice_router.py` (`synthesize_voice`) — VieNeu primary (clone > preset) with an honest edge-tts fallback. Single source of truth.
- **Output:** `8_WORKSPACE/<ProjectName>/.temp/voice.mp3`

### STEP 3: IDENTIFY TIMESTAMPS
- Priority: VieNeu native word boundaries remapped to exact DISPLAY words (RULE #1).
- ASR: `2_SKILLS/srt_maker/asr_router.py` (PhoWhisper → faster/openai-whisper) → word timing,
  then `news_video_standards.align_tts_boundaries_to_display_words()`.
- **Output:** sidecar `.srt` written next to the final mp4 by `native_composer`.

### STEP 4: SCENE GENERATION (components + SFX)
- `native_composer` builds each scene from the JSON template's components (bignum, repo,
  compare, terminal, steps, badges, stats, quote, tip, feature, chart, mockup, gittree, cta).
- SFX cues per component via `native_composer._sfx_cues` from the curated library
  `7_ASSETS/audio/sfx/` (manifest.json); BGM by mood from `7_ASSETS/audio/bgm/`.

### STEP 5: VIDEO RENDER (HyperFrames native)
- `native_composer.make_video()` generates the HTML/CSS/GSAP composition inline
  (loads GSAP from CDN; light-mode only).
- Render: local `node node_modules/hyperframes/dist/cli.js render --format mp4`
  (ffmpeg/ffprobe pinned via `HYPERFRAMES_FFMPEG_PATH`/`HYPERFRAMES_FFPROBE_PATH`).
- **Frame 0 Hook:** Kicker + H1 always at 100% opacity at second 0.

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
