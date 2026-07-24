# 09 — EVIDENCE INDEX

All paths are relative to the repo root `D:\SEOSONA AI\SEOSONA Video\` unless absolute. No secret values were copied into this audit.

## Captured artifacts (in this audit folder)

| File | Source | What it proves |
|---|---|---|
| `screenshots/api_health.json` | live `GET http://127.0.0.1:5050/api/health` | 45 videos on disk, avg quality 97.2, 100% pass, WPM 212–228, `render_seconds` corruption |
| `screenshots/api_metrics.json` | live `/api/metrics` | recent renders table, queue runs, totals |
| `screenshots/api_factory-metrics.json` | live `/api/factory-metrics` | per-render flight records |
| `screenshots/api_system-stats.json` | live `/api/system-stats` | system stats snapshot |
| `screenshots/api_process-status.json` | live `/api/process-status` | process status snapshot |
| `screenshots/dashboard_index.html` | live `/` (142 KB) | rendered dashboard markup (in-app browser could not screenshot — JS hung) |
| `screenshots/dashboard_server.log` | Flask stdout | server started clean, served HTTP 200 |

## Source evidence referenced (in repo)

### Config / stack
- `package.json`, `requirements.txt`, `system_config.yaml`, `seosona.project.json`
- `0_SETUP/ENVIRONMENT.md`, `0_SETUP/MODELS.md`, `0_SETUP/bootstrap.ps1`, `0_SETUP/check_env.py`
- `1_CONFIG/credentials_manager.py`, `1_CONFIG/factory_policy.yaml`
- `.env` / `.env.example` (NAMES only — no values read into this report)

### Core engine (4_BRAIN)
- `workflow_router.py:55,118,130-137,157,190`, `graph_executor.py`
- `video_engine.py:56,360,369,374,533,604,624,645,657,672,787,792,819-820`
- `native_composer.py:178,570,2177,2192,2337,2405,2483,2924,2946,2992,3042,3049,3084-3096,3242,3246`
- `make_video.py:498,629-661,738-745`, `scene_composer.py`, `script_writer.py:157,298,556,580`
- `component_picker.py`, `director.py`, `spec_lint.py`, `effect_library.py`, `content_moderation.py`
- `quality_scorer.py:13,24,58-62,117-118`, `evaluator.py`, `eval_judge.py`
- `llm_engine.py:638,722,827,921,961,976,997,1018,1045,1051`
- `image_gen.py:24`, `seedance_engine.py:24-27,48-49,86-107,136-209`, `seedance_director.py`
- `lipsync_service.py`, `dub_align.py`, `knowledge_graph.py`, `factory_brain.py`, `factory_metrics.py`
- `script_schema.py:1-60`, `production_manifest.py`

### Skills / agents
- `2_SKILLS/voice_cloner/voice_router.py:38-74`, `omnivoice_engine.py:136-188`, `vieneu_engine.py`
- `2_SKILLS/srt_maker/asr_router.py:22-30,33,49,65,80,117-138`, `sherpa_vn_engine.py`
- `2_SKILLS/thumbnail_maker/thumbnail_maker.py:90-199`, `frame_scorer.py:30`
- `2_SKILLS/video_clipper/clipper.py:21-39`, `yt_downloader/yt_dlp_engine.py:8-38`
- `2_SKILLS/image_sourcer/image_sourcer.py:28-70,124`, `broll_sourcer/broll_sourcer.py:35,38`
- `2_SKILLS/element_maker/element_maker.py:159-475`, `bgm_sourcer/bgm_sourcer.py:92`, `carousel_maker/carousel_generator.py`
- `2_SKILLS/README.md` (stale — lists nonexistent tts_generator)
- `1_AGENTS/ROSTER.md`, `scraper_agent/scraper.py:17-45`, `seo_writer_agent/writer.py:29-45`
- `1_AGENTS/analytics_feedback_agent/performance_ingest.py:47` (STUB), `feedback_generator.py:71`
- `1_AGENTS/publisher_agent/publish_dispatch.py:39-159`, `youtube_uploader.py`, `hermes_agent/telegram_remote.py:136`

### Talking-head / lipsync / seedance (standalone)
- `scripts/talking_head_transcribe.py:42`, `talking_head_edit.py:514,552-594`, `talking_head_analyze.py`, `talking_head_autocut.py`
- `scripts/course_video.py:317,514`, `course_planner.py`
- `scripts/lipsync_musetalk.py`, `portrait_avatar.py`, `liveportrait_motion.py`, `mascot_talk.py`, `avatar_motion.py`
- `scripts/ltx_video.py`, `7_ASSETS/models/ltx.ready`

### Execution evidence (logs / jobs / outputs)
- `3_MEMORY/factory_metrics.jsonl` (30 records), `3_MEMORY/reports/*.json` (incl. `TOBY_LABS_NEWS_20260706_151121.json` FAILED, `n8n_20260630_100459.json` PASS)
- `3_MEMORY/learning/ledger.json` (`total_videos:1`), `3_MEMORY/evaluation/`
- `logs/metrics/events.jsonl` (1219 events), `logs/daily/20260629-093347.log`, `logs/publish/receipts.jsonl` (dry-run only)
- `9_DASHBOARD/feedback_state.json` (avg 99.1 / 52 samples)
- Output MP4s (ffprobe-verified): `8_WORKSPACE/TOBY_LABS_NEWS/FINAL.mp4`, `NEWS_SELFSUFF/FINAL.mp4`, `NEWS_TEST_FRAMEKHO/FINAL.mp4`, `prompts.chat/prompts.chat - SEOSONA.mp4`, `lipsync_demos/mascot_talking_PRODUCTION.mp4`, `adsbootcamp_11_07/_reasm_cache.mp4`
- Contract samples: `8_WORKSPACE/TOBY_LABS_NEWS/_pacing.json`, `8_WORKSPACE/adsbootcamp_11_07/words.json`, `8_WORKSPACE/lipsync_jobs/38b0fcd5763a.json`

### Docs / SOP
- `README.md`, `ARCHITECTURE.md`, `STRUCTURE.md`, `AGENTS.md`, `docs/01–08`, `docs/SYSTEM_MAP.html`
- `6_SOP/README.md` (40 SOPs), `6_SOP/{SCRIPT_WRITING_PIPELINE,PRODUCT_ROADMAP,AUTONOMOUS_FACTORY_LOOP,LOOP_OPERATING_SOP,EFFECT_LIBRARY_PLAN}.md`

### State at audit time
- `0_INPUT_INBOX/production_queue.yaml` (empty placeholders), `0_INPUT_INBOX/STOP` (present, locked)
- `git HEAD 87c6bb7` on `main` (EDL auto-cut commit landed just before STOP)

## Runtime versions verified
- Node v22.22.3 · npm 10.9.8 · Python 3.11.15 · ffprobe 8.1.1 (Gyan build, on PATH)
