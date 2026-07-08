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
- The actual render uses the local **`node_modules/hyperframes/dist/cli.js`** (resolved by
  `native_composer._hf_cli()`), NOT any checkout here. Fonts/logo come from `7_ASSETS`, GSAP from CDN.
- **`hf_producer_render.mjs`** — Node Producer-API render helper (streaming progress,
  reuses an existing Chrome). *Legacy opt-in; the current engine renders via the CLI directly.*

### Catalog source — the 97-block library
- **`hf_engine/registry/{blocks,components}`** — the **canonical** HyperFrames block + component
  library (97 blocks, 25 components), the source the factory pulls from. `4_BRAIN/hf_blocks.py`
  renders any block to a clip (auto brand-skinned to the SEOSONA palette); `block_picker` auto-selects
  one per scene by content; `native_composer._overlay_blocks` / `course_video` b-roll overlay it.
  The seosona-video-operator SKILL also points `npx hyperframes add <name>` here. Catalog +
  use-case map: `2_KNOWLEDGE/hyperframes/{catalog,FACTORY_BLOCK_PALETTE.md}`. The large vendored
  monorepo bits under `hf_engine/` (its own `packages/`, `node_modules/`) were pruned — not used
  at render time (blocks are self-contained HTML + GSAP CDN); the render uses root `node_modules`.

*(Removed: `hf_core/` (84M, identical duplicate registry + upstream docs) and `hyperframes/` (upstream
docs/scripts/templates — the live artifacts are `hf_engine/registry` + `2_KNOWLEDGE/hyperframes/`). Also long retired:
`news_spatial_hyperframes`, `news_loop_path_hyperframes`, `loop-source-seosona-clone`, `hf_cards`.)*

### Fallback renderers (non-primary)
- *(`html_renderer/` (retired engine) was REMOVED 2026-06-30. Its only live artifacts — the 2 thumbnail
  templates `seosona_thumbnail_{16x9,v1}.html` — moved to `2_SKILLS/thumbnail_maker/templates/`, next to
  the code that uses them. The 8 dead layout templates + `engine.js` went with it.)*
- *(`moviepy_wrapper/` was the old MoviePy muxing path — retired (removed).)*

## Rule of thumb
- Add a new **reusable video template** → `7_ASSETS/templates/*.json` (consumed by
  `native_composer.fill_template`), not here.
- The HyperFrames **catalog blocks** are pulled on demand from `hf_engine/registry/` —
  programmatically via `4_BRAIN/hf_blocks.render_block()`, or `npx hyperframes add <name>`.

See also: `2_KNOWLEDGE/hyperframes/README.md` (full engine knowledge) and
`6_SOP/RENDER_ENGINE_DECISION.md`.
