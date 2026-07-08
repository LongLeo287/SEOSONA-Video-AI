# HyperFrames block palette → the FACTORY (what we learned from 5_FRAMEWORK/hf_core+hf_engine)

The vendored HyperFrames kit ships a **97-block + 25-component** professional effect library (canonical
source: `5_FRAMEWORK/hf_engine/registry/{blocks,components}`, catalogued in `catalog/CATALOG_INDEX.md`,
installable with `npx hyperframes add <name>`). **The factory underuses it**: `native_composer._component()`
only renders ~14 hand-built components (bignum/stats/steps/compare/tip/…). This doc connects the rich
palette to the factory so generated videos can use it — the "load into system + factory" step.

## Palette by use-case (pull with `npx hyperframes add <name>`)
**Code / tech (33 blocks)** — ideal for SEO/dev tutorials & the course pipeline:
`code-3d-extrude` · `code-diff` · `code-highlight` · `code-morph` · `code-particle-assemble` ·
`code-scroll` · `code-shader-dissolve` · `code-snippet-*` (Apple-terminal themes: homebrew/ocean/pro/
novel/grass…, dark-modern/dark-plus/high-contrast…). → show real code/terminal instead of plain text.

**Cinematic / transition** — richer than the hand-built crossfade:
`cinematic-zoom` · `chromatic-radial-split` · `cross-warp-morph` · `domain-warp-dissolve` ·
`flash-through-white` · `glitch` · `gravitational-lens` · `light-leak` · `parallax-zoom` /
`parallax-unzoom` · `shimmer-sweep` · `motion-blur` · `grain-overlay` · `vignette` · `morph-text`.

**UI-mockup / showcase** — great for talking-head b-roll + product/news:
`app-showcase` · `instagram-follow` · `macos-notification` · `macos-tahoe-liquid-glass` ·
`liquid-glass-notification` / `-media-controls` / `-widgets` / `-context-menu` · `ios26-liquid-glass` ·
`logo-outro` · `data-chart` · `flowchart` / `flowchart-vertical`.

**Caption components (25)** — richer karaoke/emphasis than the ASS hand-render:
`caption-pill-karaoke` · `caption-kinetic-slam` · `caption-matrix-decode` · `caption-neon-glow` ·
`caption-gradient-fill` · `caption-particle-burst` · `caption-editorial-emphasis` · `caption-emoji-pop` ·
`caption-glitch-rgb` · `caption-highlight` · `caption-parallax-layers` · `caption-weight-shift` …

## How the factory uses a block (integration path)
1. The script planner (video_engine / scene_writer) picks a block by use-case from the palette above.
2. `npx hyperframes add <block>` installs its HTML into the composition's `compositions/` dir.
3. `native_composer` assembles the scene referencing the block (it already renders via
   `node_modules/hyperframes` cli), keeping brand colours (light-mode, #2A5BDA/#E2724D).
4. Render as usual. Don't hand-write what a block already provides (operator-skill rule).

## Mapping to our video types
- **News (faceless scene-slides):** cinematic-zoom + light-leak transitions; data-chart/flowchart for stats;
  caption-pill-karaoke for the bottom line.
- **Course / tech (talking-head + SEO):** the `code-*` family for showing code/terminal; macos/liquid-glass
  mockups as b-roll; caption-kinetic-slam for hooks.
- **Product/launch:** app-showcase + logo-outro + liquid-glass UI.

## Status — BRIDGE BUILT ✅ (2026-06-30)
- **`4_BRAIN/hf_blocks.py`** renders ANY registry block to a clip: `render_block("cinematic-zoom", out)`
  + `list_blocks(tag)`. Reuses the HyperFrames CLI + ffmpeg native_composer renders with. Verified
  (cinematic-zoom → a valid 4s 1080p clip).
- **Wired into the course/talking-head pipeline:** a segment's `broll` can be `{"block": "<name>", "mode": "full|pip"}`
  → `course_video` renders the block on the fly and overlays it as b-roll/cutaway (e.g. a `code-snippet-*`
  block while explaining code, `cinematic-zoom` as a transition). `{"src": "<file>"}` still works for screenshots.
- `hf_core/registry` (identical duplicate) + the whole `hf_core` (84M) were REMOVED; `hf_engine/registry`
  is canonical. video_integration_audit updated.

### NEWS scenes — DONE ✅
`native_composer._overlay_blocks()` (gated, additive): a NEWS scene can carry `scene["block"]="<name>"`
or `comp=("block",{"name":...})` → the block is rendered + overlaid onto the final video at the scene's
time window (scaled to 90% width, upper-third). NO-OP when no scene uses a block, so normal news renders
are byte-identical. Verified (cinematic-zoom overlaid correctly).

→ Both pipelines use the 97-block palette: **course/talking-head** via `broll:{block}`, **news** via `scene.block`.

### Auto brand-skin — DONE ✅ (blocks are on-brand)
`hf_blocks._brand_skin()` (always on, opt out `SEOSONA_BLOCK_BRAND=0`) remaps each block's recurring
ACCENT colours to the SEOSONA palette before render — gold/purple/cyan/MS-blue → blue `#2A5BDA` / coral
`#E2724D`, while LEAVING code-syntax greys/darks + macOS traffic-light dots alone (structural). So a
rendered block matches the brand instead of fighting it. Verified: cinematic-zoom's gold+purple → SEOSONA
coral+blue. (Best-effort string remap, since the kit hardcodes hex colours, not CSS variables.)

### Planner auto-selection — DONE ✅ (automatic)
**`4_BRAIN/block_picker.py`** `pick_block(text)` maps content → a block ONLY where the 14 components fall
short (code → `code-snippet-dark-modern`, UI/notification → `macos-notification`, liquid-glass/widget →
`liquid-glass-widgets`). Wired into `video_engine.plan_scenes`: conservative (strong keyword only),
**capped at 2 blocks/video**, **ON by default** (opt OUT with `SEOSONA_USE_BLOCKS=0`). Verified: auto→code/UI
scenes get the right block; opt-out→none.

### The design split (per the brand owner)
- **14 components = a CASE LIBRARY** — proven patterns, the default scaffold for every scene, and where you
  add a NEW case when a new content shape appears. They stay the backbone (light-mode, brand, inline, fast).
- **97 blocks = the BEAUTY layer** — auto-selected + auto-brand-skinned, layered on top to make the fitting
  case look better (real code, UI mockup, cinematic beat). Never a replacement, always an enhancement.
