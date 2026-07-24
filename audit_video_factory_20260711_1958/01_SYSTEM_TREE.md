# 01 — SYSTEM TREE (curated)

> Tiered `0→9` layout. The repo is **two parts sharing one codebase**: THE SYSTEM (brain/infra) and THE FACTORY (production line). See `ARCHITECTURE.md`.
> There is **no separate frontend app, no backend service, no database, no container** — it is a single-machine Python + Node factory driven by CLI/npm scripts, with one read-only Flask dashboard.

```text
SEOSONA Video/
├── 0_INPUT_INBOX/            Batch intake + kill-switch
│   ├── production_queue.yaml   ← queue (currently empty placeholders)
│   ├── STOP                    ← loop kill-switch (PRESENT/locked → autonomous loop paused)
│   ├── sources.txt, feeds.txt  ← news feed inputs
│   └── done/, pending_files/
├── 0_SETUP/                  Environment hub
│   ├── bootstrap.ps1           ← fresh-machine venvs + npm install (npm run env:setup)
│   ├── check_env.py            ← env status (npm run env:check)
│   └── ENVIRONMENT.md, MODELS.md
├── 1_AGENTS/                 AI role modules ("the limbs") — all wired except personas
│   ├── ROSTER.md
│   ├── scraper_agent/          web article → structured content  (called: video_engine.py:787)
│   ├── seo_writer_agent/       scraped → 5-part script (LLM)     (video_engine.py:792)
│   ├── repurposer_agent/       SRT hook analysis                 (video_engine.py:819)
│   ├── carousel_writer_agent/  carousel copy (LLM+safety)        (workflow_social_post.py:66)
│   ├── social_media_agent/     PAS captions                      (workflow_social_post.py:69)
│   ├── seo_optimizer/          YT/TikTok title/desc/tags         (video_engine.py:672)
│   ├── publisher_agent/        upload dispatch (cred-gated, dry-run only)  (video_engine.py:666)
│   ├── analytics_feedback_agent/  post-mortem + metrics ingest   (⚠ live YT pull is a STUB)
│   ├── hermes_agent/           Telegram remote brain (TOKEN missing)
│   ├── trend_jacking_agent/    RSS trend → trigger news video
│   └── personas/               reference docs (NOT loaded at runtime)
├── 1_CONFIG/                 Config + secrets resolution
│   ├── credentials_manager.py  env-first → credentials/<platform>.json
│   └── factory_policy.yaml
├── 2_KNOWLEDGE/              Knowledge base, craft studies, ingestion logs, second-brain JSON
│   ├── knowledge_graph.json / knowledge_notes.json   ← second-brain content
│   ├── domain_skills/          17 SEO/marketing/design SKILL.md
│   ├── hyperframes/craft/       motion + template craft studies
│   └── VIDEO_CRAFT_RULES.md, INGESTION_LOG.md, REPO_WATCHLIST.md
├── 2_SKILLS/                 Technical skill modules ("the hands")
│   ├── voice_cloner/           TTS router: OmniVoice→VieNeu   (native_composer.py:2405)
│   ├── srt_maker/              asr_router: PhoWhisper word-timing (video_engine.py:97)
│   ├── thumbnail_maker/        content→NLP→PNG + frame_scorer  (video_engine.py:604)
│   ├── video_clipper/          long→9:16 short (moviepy)        (video_engine.py:820)
│   ├── yt_downloader/          yt-dlp engine                    (workflow_router.py:71)
│   ├── image_sourcer/          Pexels + URL scrape per scene    (native_composer.py:2337)
│   ├── element_maker/          icon/emoji/badge → PNG layer     (native_composer.py:570)
│   ├── bgm_sourcer/            Openverse/Jamendo CC music       (native_composer.py:444)
│   ├── broll_sourcer/          Pixabay stock b-roll             (image_gen.py:4)
│   ├── carousel_maker/         social carousel slides           (workflow_social_post.py:95)
│   ├── hf_blueprints/          HTML composition scaffolds (assets, not Python)
│   └── os_*                    4 external OpenClaw SKILL.md packages (NOT wired)
├── 3_MEMORY/                 Runtime memory + flight recorders
│   ├── factory_metrics.jsonl   ← 30 render records
│   ├── reports/*.json          ← per-project QA reports
│   ├── learning/ledger.json    ← learning signal (near-empty: total_videos:1)
│   └── evaluation/
├── 4_BRAIN/                 ⭐ Unified engine + routing + scoring (50 .py files)
│   ├── workflow_router.py      ⭐ entry: detect → SuperGraph
│   ├── video_engine.py         ⭐ run_pipeline, plan_scenes
│   ├── native_composer.py      ⭐ THE render chokepoint (make_video, 3279 lines)
│   ├── scene_composer.py       github fetch + compose
│   ├── make_video.py           ⭐ github URL one-shot + --news batch
│   ├── script_writer.py        6-stage verified narration + render gate
│   ├── scene_writer.py, component_picker.py, director.py, spec_lint.py,
│   │   effect_library.py, beat_timing.py, frame_study.py, frame_synth.py,
│   │   block_picker.py, block_forge.py, hf_blocks.py, template_picker.py,
│   │   template_generator.py, brand_kit.py, news_video_standards.py
│   ├── content_moderation.py   pre-render brand-safe / real-data gate
│   ├── quality_scorer.py       ⭐ 0-100 QA gate      evaluator.py  independent maker-checker
│   ├── llm_engine.py           ⭐ 6-tier LLM cascade + offline NLP floor
│   ├── researcher.py, angle_finder.py, script_schema.py, production_manifest.py
│   ├── graph_executor.py       SuperGraph state machine
│   ├── knowledge_graph.py      second-brain query API (dashboard only)
│   ├── factory_brain.py / factory_ledger.py / learn_flywheel.py  autonomous-batch layer
│   ├── factory_metrics.py      one-JSONL-line flight recorder
│   ├── eval_judge.py / eval_run.py   Gemini-vision QA judge (eval flywheel)
│   ├── seedance_engine.py / seedance_director.py   Engine #6 (standalone, not wired)
│   ├── lipsync_service.py / dub_align.py           Engine #3/4 (standalone, not wired)
│   ├── course_planner.py       course path only
│   ├── image_gen.py            NVIDIA FLUX (optional)
│   └── capcut_export.py, discovery.py, caption_segment.py, transcript_fix.py
├── 5_FRAMEWORK/             HyperFrames render layer
│   ├── hf_engine/              vendored engine (gitignored)
│   ├── hf_producer_render.mjs  producer render bridge
│   └── publish/publisher.py    Playwright human-gated upload
├── 6_SOP/                   40 SOP documents (production, script, render, publish, ops)
├── 7_ASSETS/               Brand + models
│   ├── models/                phowhisper-medium-ct2/, ltx.ready (LTX weights marker)
│   ├── voice/                 .venv-omnivoice, CQA ref, profiles
│   ├── audio/                 sfx/, bgm/
│   ├── brand/                 logos, icons (95 Lucide), fonts
│   └── templates/*.json       scene STRUCTURE templates + CATALOG.md
├── 8_WORKSPACE/            Generated outputs (gitignored/transient) — 45 videos on disk
│   ├── TOBY_LABS_NEWS/FINAL.mp4  (verified 47s 1080×1920 H.264+AAC)
│   ├── prompts.chat/, NEWS_*/, lipsync_jobs/, lipsync_demos/
│   └── adsbootcamp_11_07/     standalone cinematic_reel.py editor (newest work)
├── 9_DASHBOARD/           Flask observability dashboard (port 5050, read-only)
│   ├── server.py              28 API routes (/api/health, /api/metrics, /api/studio/*)
│   ├── obs_metrics.py         event bus → logs/metrics/events.jsonl
│   ├── feedback_loop.py, feedback_state.json, autostart.py
│   └── templates/index.html, static/
├── 9_PROMPTS/             Centralized LLM prompt templates (AIDA/PAS/carousel/thumbnail) + MASTER_VIDEO_SPEC.md
├── scripts/               Orchestration + tooling (workflow_*.py, queue_processor, daily_production,
│                          talking_head_*, course_video, seedance/ltx, portrait_avatar, lipsync_*, etc.)
├── packages/cli/          Desktop CLI build (dist/)
├── deploy/                open_dashboard.bat, run_daily.bat, SCHEDULING.md (Task Scheduler)
├── docs/                  01–08 encyclopedia + SYSTEM_MAP.html (marketing-toned, some drift)
├── logs/                  metrics/events.jsonl, daily/, publish/receipts.jsonl (dry-run only)
├── tests/                 pytest suite (offline-forced; ~43 tests)
├── package.json           40+ npm script entry points (all via scripts/seosona-python.cjs)
├── requirements.txt, system_config.yaml, seosona.project.json
├── ARCHITECTURE.md, STRUCTURE.md, README.md, AGENTS.md, GEMINI.md
└── .env / .env.example    secrets (names only in this audit)
```

## Entry points & who calls what (CONFIRMED)

| Entry | npm command | Calls |
|---|---|---|
| `4_BRAIN/workflow_router.py` | `video:run` | → `video_engine.run_pipeline` via SuperGraph |
| `4_BRAIN/make_video.py` | `make:video` | github → `scene_composer.fetch_github` → `auto_content` → `native_composer` |
| `scripts/workflow_video_news.py` | `video:news` | → `workflow_router.route` |
| `scripts/topic_to_video.py` | `video:discover` | `discovery` → `script_writer` → `route` |
| `scripts/workflow_video_course.py` | `video:course` | → `course_video.py` → `talking_head_edit` |
| `scripts/queue_processor.py` | `start:queue` | batch over `production_queue.yaml` |
| `scripts/daily_production.py` | `daily` | queue + optional news + optional publish; autostarts dashboard |
| `4_BRAIN/factory_brain.py` | `factory` | autonomous plan→produce→QA→publish→learn |
| `9_DASHBOARD/server.py` | `start:dashboard` | Flask, port 5050 |

All npm targets route through `scripts/seosona-python.cjs` (resolves the correct Python interpreter). The single render chokepoint every video path funnels through is **`native_composer.make_video`** (`4_BRAIN/native_composer.py:2177`).

## Notable tree facts
- **`4_BRAIN/pipeline_dag.py` does NOT exist** — the `MEMORY.md` note referencing it is stale; the active graph engine is `graph_executor.SuperGraph`. (CONFIRMED)
- `2_SKILLS/README.md` is stale: lists a nonexistent `tts_generator/` (folded into `voice_cloner`) and omits 6 present folders.
- `5_FRAMEWORK/hf_engine/` is vendored and gitignored.
