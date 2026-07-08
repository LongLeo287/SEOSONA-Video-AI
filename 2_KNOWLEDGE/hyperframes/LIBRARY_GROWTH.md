# Growing the 3 libraries — TEMPLATE · COMPONENT · BLOCK

How to keep each library growing so videos stay rich and varied. The 3 layers (see
`FACTORY_BLOCK_PALETTE.md`): **template** = the whole plan · **component** = one element in a scene ·
**block** = a full pre-made scene. Each grows from a different source + has a different "add" recipe.

> Rule: every addition is **brand-first** (light-mode, `brand_kit` palette) and **vetted** before it ships
> (log it in `2_KNOWLEDGE/INGESTION_LOG.md`, follow `6_SOP/REPO_VETTING_SOP.md`). No off-brand neon/dark.

---

## 1. TEMPLATE library (`7_ASSETS/templates/*.json`) — 20 archetypes
A template is a **scene-arc plan** (which components, what order, what kicker per scene). Pure data —
`native_composer` consumes it, `template_picker` auto-selects it, `gen_catalog.py` documents it.

**Grow it 3 ways:**
1. **Generate** — `python 4_BRAIN/template_generator.py "Top 7 lỗi SEO" --scenes 7` → a new archetype from a brief
   (deterministic arc from content cues; validates components).
2. **Hand-author** — copy an existing JSON, change the `scenes` arc. Keep 5–8 scenes, always HOOK → … → CTA.
3. **Mine reference videos** — clone a good video's structure (`D:\SEOSONA AI\Video Template`), map its beats to
   our components, save as a new archetype.

**After adding:** add a `template_picker._RULES` keyword→name entry (so it auto-selects) + run
`python scripts/gen_catalog.py` (regenerates `CATALOG.md`). Done.

---

## 2. COMPONENT library (`5_FRAMEWORK/hf_engine/registry/components/`) — 25 + 17 hand-built
Two kinds: **17 hand-built** brand components in `native_composer._component` (bignum/stats/compare…) and
**25 registry components** (16 caption STYLES + 9 visual EFFECTS — `hf_blocks.list_components()`).

**Sources to collect from:**
- **HyperFrames upstream registry** (the same kit) — new caption/effect components ship over time.
- **Repos / cloned videos** — a recurring visual motif → port it as a new hand-built component or a snippet.
- **Web / design systems** — Open Design / Dribbble motion patterns → re-skin to brand, add as a component.

**Add recipe:**
- *Registry component* → drop a `<name>/` dir (snippet `<name>.html` + `demo.html` + `registry-item.json`)
  under `components/`; `hf_blocks.render_component()` + `component_snippet()` pick it up automatically.
- *Hand-built brand component* → add a `kind` branch in `native_composer._component()` returning brand HTML;
  it's then selectable from any template's `scenes[].component`.

---

## 3. BLOCK library (`5_FRAMEWORK/hf_engine/registry/blocks/`) — 97
A block is a **full pre-made scene** (own timeline). `hf_blocks.render_block()` renders any block (auto
brand-skinned); `block_picker` chooses one per scene by content; overlaid in news + course.

**Sources to collect from:**
- **HyperFrames registry / `npx hyperframes add <name>`** — the official block catalog.
- **Repos / cloned videos / web** — a striking transition or mockup → vet it, drop it into `blocks/`.
- **Build custom** — author a new block dir (HTML composition + `registry-item.json`).

**Add recipe:** drop a `<name>/` dir (the `<name>.html` composition + assets + `registry-item.json` with
`tags`/`duration`) under `blocks/`; then add a `block_picker._RULES` keyword→`<name>` entry so it auto-fires.
Verify with `python 4_BRAIN/hf_blocks.py <name>` (renders a clip; confirm it's brand-skinned).

---

## Where the selectors live (so new items get USED, not just stored)
| Layer | Library | Auto-selector | Cap / gate |
|---|---|---|---|
| TEMPLATE | `7_ASSETS/templates` | `4_BRAIN/template_picker.py` | content keyword → archetype |
| COMPONENT | `registry/components` + native `_component` | per-template `scenes[].component` | (captions need text+timing) |
| BLOCK | `registry/blocks` | `4_BRAIN/block_picker.py` | `SEOSONA_BLOCK_BUDGET` (default 4) / video |

Growth loop: **collect → vet (INGESTION_LOG) → add (recipe) → register in the selector → it ships in the next video.**
