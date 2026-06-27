# 5_FRAMEWORK — Render Engine & Scaffolds Map

This tier is the **rendering layer** (HyperFrames engine + SEOSONA render-project
scaffolds). Unlike `7_ASSETS` (reusable data — freely reorganizable), everything here
is **load-bearing code** for the render. The current engine `4_BRAIN/native_composer.py`
builds the composition HTML programmatically and renders via the local `hyperframes`
CLI; it pulls fonts/logo from `7_ASSETS` and loads GSAP from CDN. The old HTML-template
render scaffolds (`news_spatial_hyperframes`, `news_loop_path_hyperframes`,
`loop-source-seosona-clone`, `hf_cards`) were retired (removed).
What remains here is the live engine source + catalog. Large videos here are gitignored.

## What each thing is

### Engine (the renderer itself)
- **`hf_engine/`** — vendored HeyGen HyperFrames monorepo source (cli, core, engine,
  producer, player, sdk, shader-transitions, studio, lambda, cloud-run). Reference
  only; **gitignored**. The actual render uses the local `node_modules/.bin/hyperframes`
  binary (or the Producer API), NOT this checkout. Knowledge: `2_KNOWLEDGE/hyperframes/`.
- **`hf_producer_render.mjs`** — Node Producer-API render helper (streaming progress,
  reuses an existing Chrome). *Legacy old-engine opt-in; the current engine renders via
  the local `hyperframes` CLI directly.*

### Catalog source
- **`hf_core/`** — base HyperFrames project (`.skills/`, vendored assets, catalog blocks).
  Still the source for HyperFrames **catalog blocks**.
- **`hyperframes/`** — HyperFrames toolkit (`docs/`, `scripts/`, `templates/`).

*(Retired (removed): `news_spatial_hyperframes`, `news_loop_path_hyperframes`,
`loop-source-seosona-clone`, `hf_cards` — old HTML-template scaffolds the new engine doesn't use.)*

### Fallback renderers (non-primary)
- **`html_renderer/templates/`** — legacy HTML templates (the `html_renderer.py` module
  is retired (removed); the `templates/` dir is kept for the thumbnail
  maker + preview scripts).
- *(`moviepy_wrapper/` was the old MoviePy muxing path — retired (removed).)*

## Rule of thumb
- Add a new **reusable video template** → `7_ASSETS/templates/*.json` (consumed by
  `native_composer.fill_template`), not here.
- The HyperFrames **catalog blocks** are pulled on demand from `hf_engine/registry/`
  / `hf_core/` via `npx hyperframes add <name>`.

See also: `2_KNOWLEDGE/hyperframes/README.md` (full engine knowledge) and
`6_SOP/RENDER_ENGINE_DECISION.md`.
