# 5_FRAMEWORK — Render Engine & Scaffolds Map

This tier is the **rendering layer** (HyperFrames engine + SEOSONA render-project
scaffolds + fallback renderers). Unlike `7_ASSETS` (reusable data — freely
reorganizable), everything here is **load-bearing code** referenced by
`4_BRAIN/pipeline_manager.py`. Do NOT move these dirs without updating the code refs
+ running a real render. Large videos here are gitignored (kept on disk).

## What each thing is

### Engine (the renderer itself)
- **`hf_engine/`** — vendored HeyGen HyperFrames monorepo source (cli, core, engine,
  producer, player, sdk, shader-transitions, studio, lambda, cloud-run). Reference
  only; **gitignored**. The actual render uses the local `node_modules/.bin/hyperframes`
  binary (or the Producer API), NOT this checkout. Knowledge: `2_KNOWLEDGE/hyperframes/`.
- **`hf_producer_render.mjs`** — Node Producer-API render helper (streaming progress,
  reuses an existing Chrome). Opt-in via `SEOSONA_HF_PRODUCER=1` in pipeline_manager.

### SEOSONA render-project scaffolds (the templates the pipeline builds from)
- **`hf_core/`** — base HyperFrames project: vendored `gsap.min.js` (under
  `.skills/graphic-overlays/assets/vendor/`), `.skills/`, and template assets.
  `pipeline_manager` reads gsap + uses this as the project base.
- **`news_spatial_hyperframes/`** — "spatial" news render scaffold (selected by
  `_select_news_template` for ≤4 scenes).
- **`news_loop_path_hyperframes/`** — "loop path" news render scaffold (≥5 scenes).
- **`loop-source-seosona-clone/`** — SEOSONA loop video template (clone source).

### Component / card libraries
- **`hf_cards/`** — a HyperFrames card composition project (`compositions/`,
  `hyperframes.json`, `index.html`).
- **`hyperframes/`** — HyperFrames toolkit (`docs/`, `scripts/`, `templates/`).

### Fallback renderers (non-primary)
- **`html_renderer/`** — alternate HTML→video renderer path.
- **`moviepy_wrapper/`** — MoviePy-based muxing/fallback (not the primary authoring model).

## Rule of thumb
- Add a new **reusable video template** → `7_ASSETS/templates/` (not here).
- Add a new **render scaffold variant** → here, next to `news_*`, and register it in
  `pipeline_manager._select_news_template`.
- The HyperFrames **catalog blocks** are pulled on demand from
  `hf_engine/registry/` via `pipeline_manager.add_catalog_block()`.

See also: `2_KNOWLEDGE/hyperframes/README.md` (full engine knowledge) and
`6_SOP/RENDER_ENGINE_DECISION.md`.
