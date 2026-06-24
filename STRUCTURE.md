# SEOSONA Video — Project Structure (where everything lives)

The autonomous Vietnamese video factory. Tiers are numbered 0→9 by role. Each tier
has its own map/README for detail — start here to find the right folder fast.

```
SEOSONA Video/
├── 0_INPUT_INBOX/     ← inputs: production_queue.yaml (what to produce)
├── 1_CONFIG/          ← credentials & secrets (API keys/tokens for publish + remote) → README.md
│   └── credentials/     real secrets (gitignored) + *.example.json templates
├── 1_AGENTS/          ← 12 AI agents (scraper, seo_writer, editor, repurposer, ...) → ROSTER.md
├── 2_KNOWLEDGE/       ← knowledge base  → README + INGESTION_INDEX.md
│   ├── hyperframes/      full HyperFrames docs (guides/reference/catalog) → README.md
│   └── repos/           distilled ingested repos (OmniVoice, OpenMontage, ...)
├── 2_SKILLS/          ← 17 Python skills (tts, srt, clipper, thumbnail, voice_cloner, ...) → README.md
├── 3_MEMORY/          ← memory/state → README
├── 4_BRAIN/           ← the engine: pipeline_manager.py (render), workflow_router.py,
│                         quality_scorer, news_video_standards (THE core)
├── 5_FRAMEWORK/       ← render layer (HyperFrames) → README map
│   ├── hf_engine/        vendored HyperFrames source (gitignored)
│   ├── hf_core/         base render project (gsap, skills)
│   └── news_*/loop-*    render-project scaffolds
├── 6_SOP/             ← 24 standard operating procedures → README index
├── 7_ASSETS/          ← reusable assets → ASSETS_MAP.md
│   ├── brand/           SEOSONA logos, fonts, icons, brand kit
│   ├── voice/           models, reference audio, voice profiles
│   ├── audio/           bgm, sfx
│   └── templates/       reusable video templates
├── 8_WORKSPACE/        ← render outputs + _cache/ (transient; gitignored)
├── 9_DASHBOARD/       ← dashboard
├── 9_PROMPTS/         ← prompt library (design/manual/social/video_scripts)
├── scripts/           ← CLI tools + npm-run workflows → README index
├── .agents/skills/    ← agent slash-command skills (incl. 18 hyperframes* + operator)
├── docs/ tests/       ← documentation, tests
└── (root)             AGENTS.md, ARCHITECTURE.md, system_config.yaml, voices.json,
                        seosona.project.json, package.json, requirements.txt
```

## Quick "where do I…?"
| I want to… | Go to |
|------------|-------|
| Queue a video to produce | `0_INPUT_INBOX/production_queue.yaml` |
| Edit how videos are built | `4_BRAIN/pipeline_manager.py` |
| Add a voice / brand asset / music / template | `7_ASSETS/` (see `ASSETS_MAP.md`) |
| Author a composition (as an agent) | `.agents/skills/hyperframes*` + `2_KNOWLEDGE/hyperframes/` |
| Pull a ready-made block/transition/caption | `npx hyperframes add <name>` (catalog in `2_KNOWLEDGE/hyperframes/catalog/`) |
| Change a TTS engine / voice routing | `system_config.yaml` + `2_SKILLS/voice_cloner/` + `6_SOP/VOICE_TTS_ENGINE_ROUTING.md` |
| Find an SOP | `6_SOP/README.md` |
| Run a workflow / add a CLI tool | `scripts/README.md` + `package.json` |
| Add an API key / token (YouTube, TikTok, FB, Drive, Telegram) | `1_CONFIG/` (see `README.md`) |
| Publish a finished product | `SEOSONA_PUBLISH=google_drive,youtube` env, or publisher_agent.publish() |
| Control the factory remotely | `python 1_AGENTS/hermes_agent/telegram_remote.py` |

## Folder maps (single source of truth per tier)
- `1_CONFIG/README.md` — credentials & secrets (publish + remote)
- `1_AGENTS/ROSTER.md` — agent roster (wired vs orphan)
- `2_SKILLS/README.md` — skills index
- `7_ASSETS/ASSETS_MAP.md` — assets
- `5_FRAMEWORK/README.md` — render engine & scaffolds
- `6_SOP/README.md` — SOP index
- `scripts/README.md` — scripts index
- `2_KNOWLEDGE/hyperframes/README.md` — HyperFrames knowledge
- `2_KNOWLEDGE/INGESTION_INDEX.md` — ingested repos

## Conventions
- Numbered tiers 0→9 = role order (input → agents → knowledge/skills → memory →
  brain → framework → SOP → assets → workspace → dashboard/prompts).
- Reusable inputs live in `7_ASSETS/`; transient outputs in `8_WORKSPACE/`.
- HyperFrames is the sole render engine (Apache-2.0) — see `6_SOP/RENDER_ENGINE_DECISION.md`.
- Connected to SEOSONA OS via `~/.seosona` (`seosona.project.json`).
