# SEOSONA Video — Project Structure (where everything lives)

The autonomous Vietnamese video factory. Tiers are numbered 0→9 by role. Each tier
has its own map/README for detail — start here to find the right folder fast.

```
SEOSONA Video/
├── 0_INPUT_INBOX/     ← inputs: production_queue.yaml (what to produce)
├── 1_CONFIG/          ← credentials & secrets (API keys/tokens for publish + remote) → README.md
│   └── credentials/     real secrets (gitignored) + *.example.json templates
├── 1_AGENTS/          ← 10 AI agents (scraper, seo_writer, repurposer, publisher, ...) → ROSTER.md
├── 2_KNOWLEDGE/       ← knowledge base  → README + INGESTION_INDEX.md
│   ├── hyperframes/      full HyperFrames docs (guides/reference/catalog) → README.md
│   └── repos/           distilled ingested repos (OmniVoice, OpenMontage, ...)
├── 2_SKILLS/          ← 7 active Python skills (voice_cloner, tts, srt, clipper, thumbnail, yt, carousel) → README.md
│                         (legacy unwired skills removed from the project)
├── 3_MEMORY/          ← memory/state → README
├── 4_BRAIN/           ← the engine: video_engine.py (unified entry) → native_composer.py
│                         (renderer) + scene_composer.py (content) + make_video.py (1-shot);
│                         workflow_router.py, quality_scorer, news_video_standards (THE core)
├── 5_FRAMEWORK/       ← render layer (HyperFrames) → README map
│   ├── hf_engine/        vendored HyperFrames source (gitignored)
│   ├── hf_core/         base render project (gsap, skills)
│   └── news_*/loop-*    render-project scaffolds
├── 6_SOP/             ← 23 standard operating procedures → README index
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
└── (root)             AGENTS.md, ARCHITECTURE.md, system_config.yaml,
                        seosona.project.json, package.json, requirements.txt
```

## Quick "where do I…?"
| I want to… | Go to |
|------------|-------|
| Queue a video to produce | `0_INPUT_INBOX/production_queue.yaml` |
| Edit how videos are built | `4_BRAIN/video_engine.py` → `native_composer.py` |
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
- **A tier number can be SHARED by two folders ON PURPOSE** — it groups by role, it is
  not a unique key. Intentional pairs: `1_` = AGENTS + CONFIG (the "who acts" layer),
  `2_` = KNOWLEDGE + SKILLS (the "what it knows / can do" layer), `9_` = DASHBOARD +
  PROMPTS (the "human-facing" layer). NOT a mistake — do NOT renumber: the tier prefix
  is hard-coded as a string in 100+ places (imports like `2_SKILLS.voice_cloner`, paths
  like `7_ASSETS/...`, npm scripts), so renaming a tier breaks the system. The number is
  a label, not an address to change.
- Reusable inputs live in `7_ASSETS/`; transient outputs in `8_WORKSPACE/`.
- HyperFrames is the sole render engine (Apache-2.0) — see `6_SOP/RENDER_ENGINE_DECISION.md`.
- Connected to SEOSONA OS via `~/.seosona` (`seosona.project.json`).

## Output placement rules (anti-litter — enforced 2026-07-14)
Every writer (script `__main__` demo, CLI default, agent, test) MUST follow these; two root-litter
bugs were fixed the day this section was written (carousel demo `./test_carousel_v2`,
talking_head_transcribe default `./selfshot`):
1. **Job/video outputs** → `8_WORKSPACE/<job-name>/` only (gitignored). Never the repo root,
   never the CWD.
2. **Default `--out` values** must be ANCHORED to the repo root (`os.path.dirname(__file__)/..`),
   never bare relative names — a bare name litters whatever directory the caller happens to be in
   (this is the known stray-folder bug class: D:\d, D:\LongLeo, parent-level 2_KNOWLEDGE).
3. **Demo/self-test outputs** → `8_WORKSPACE/_demo/<skill>/`.
4. **Scratch/temp** → `tempfile.mkdtemp()` (system temp), cleaned or abandoned there — never
   inside the repo. Per-job temp inside the job's own `8_WORKSPACE/<job>/` dir is OK if prefixed
   `_` (e.g. `_captions_upload/`) so sweeps can identify it.
5. **Evidence that must persist** (benchmarks, audits) → `8_WORKSPACE/benchmarks/<date>/` or a
   dated root-level `audit_*/` dir with a REPORT.md.
6. **Logs** → `logs/<area>/` only; rotate/clean freely — nothing may depend on them.
7. **New model weights/caches** → HF hub cache or `7_ASSETS/models/` + an entry in
   `0_SETUP/MODELS.md` (fetch + license + delete rules). No stray weight dirs.
