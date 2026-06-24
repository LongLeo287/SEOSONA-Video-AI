# HyperFrames — Core Render Engine of SEOSONA Video

HyperFrames (heygen-com/hyperframes, Apache-2.0) is the **core render engine** of
SEOSONA Video: write HTML/CSS + GSAP with timing data-attributes → deterministic
MP4 (seek each frame in headless Chrome + FFmpeg). This module is the full
ingested knowledge base — guides, API reference, and the component catalog.

Ingested 2026-06-24 from the official docs (`hyperframes.heygen.com`, 206-page
`llms.txt` index) + the vendored source. Sole engine — Remotion was ruled out (paid).

## What SEOSONA Video has on disk

| Asset | Location | Notes |
|-------|----------|-------|
| **Agent skills (18)** | `.agents/skills/` | `hyperframes`, `-core`, `-animation`, `-cli`, `-creative`, `-media`, `-registry` + workflow skills (embedded-captions, faceless-explainer, general-video, graphic-overlays, motion-graphics, pr-to-video, product-launch-video, website-to-video, remotion-to-hyperframes). Installed via `npx skills add heygen-com/hyperframes`. |
| **Full engine source** | `5_FRAMEWORK/hf_engine/` | Vendored monorepo: cli, core, engine, producer, player, sdk, shader-transitions, studio, aws-lambda, gcp-cloud-run (reference; gitignored). |
| **Catalog source** | `5_FRAMEWORK/hf_engine/registry/` | 97 blocks + 25 components (real HTML + registry-item.json). |
| **Knowledge base** | `2_KNOWLEDGE/hyperframes/` | This module (guides + reference + catalog). |
| **Render integration** | `4_BRAIN/pipeline_manager.py` STEP 5 | CLI local binary (default) + Producer API opt-in (`5_FRAMEWORK/hf_producer_render.mjs`). |

## Knowledge map

### guides/ — how to build with HyperFrames
- `00_introduction.md` — what HyperFrames is, the model, the package ecosystem
- `01_quickstart.md` — install, project setup, the 3 composition rules
- `02_animation_gsap.md` — the paused-timeline / `window.__timelines` contract
- `03_rendering.md` — render flags, 4K, performance, HDR, GPU, workers
- `04_pipeline.md` — the 7-step multi-beat agent pipeline
- `05_prompting.md` — prompting patterns for AI agents
- `06_timeline_keyframes.md` — timeline editing + keyframe/arc authoring
- `07_video_components.md` — video components + editor cheatsheet
- `08_common_mistakes_troubleshooting.md`
- `09_advanced.md` — html-in-canvas, bg removal, website-to-video, vs-remotion, deploy

### reference/ — the API / library
- `00_concepts.md` — compositions, data-attributes, determinism, frame-adapters, variables
- `01_html_schema_reference.md` — the full authoring schema (every clip attribute)
- `02_packages_core_cli_engine.md` — core exports + full CLI flag reference + engine API
- `03_packages_producer_player_sdk.md` — `createRenderJob`/`executeRenderJob`, player, SDK
- `04_packages_shader_transitions.md` — the 13/14 shaders + `init()` API
- `05_packages_studio.md` — the visual editor
- `06_deployment_cloud_scale.md` — AWS Lambda + GCP Cloud Run + templates-at-scale

### catalog/ — the component menu (from the local registry)
- `CATALOG_INDEX.md` — all 122 items (97 blocks + 25 components) by category, with `npx hyperframes add <name>`
- `TRANSITIONS.md` — the cinematic transition blocks (whip-pan, cinematic-zoom, cross-warp-morph, light-leak, …)
- `CAPTIONS.md` — the 16 caption components (karaoke, kinetic-slam, neon-glow, gradient-fill, …)

## How SEOSONA Video uses this
- **Agents** invoke the `.agents/skills/hyperframes*` slash commands to author compositions.
- **Pipeline** (`pipeline_manager.py`) builds an HTML scene project and renders via the CLI local binary (or Producer API with `SEOSONA_HF_PRODUCER=1`).
- **Blocks/components** are pulled from the catalog with `npx hyperframes add <name>` into a project's `compositions/`.
- Decision + render-config: see `6_SOP/RENDER_ENGINE_DECISION.md`.
