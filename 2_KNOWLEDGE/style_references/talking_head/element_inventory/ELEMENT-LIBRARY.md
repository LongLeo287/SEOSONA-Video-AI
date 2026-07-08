# Talking-head ELEMENT library — master taxonomy (2026-07)

What actually makes a talking-head reel watch: a **dense layer of small visual elements popped over
the footage, synced to each phrase** — icons, emojis, stickers, images, cards, text-effects. Cataloged
element-by-element from all 9 reference reels (`V1..V9_elements.md`) and turned into a **real, reusable,
on-brand element library** (not ASS text). Direction: keep the craft, keep the SEOSONA **light** brand
(source is dark/neon → white/frosted glass + soft shadow + one semantic role colour, never neon).

## The library (built + verified)

- **Renderer:** `2_SKILLS/element_maker/element_maker.py` — `render_element(spec, out_png)` /
  `render_many(pairs)`. HTML/CSS + inline-SVG on a **transparent** background via Playwright/Chromium
  (same engine as native_composer/thumbnail_maker) → tight-bbox transparent PNG. Icons tinted to a
  semantic ROLE via `currentColor`. Colour emojis render natively.
- **Icons:** `7_ASSETS/brand/icons/` — **95 vendored Lucide SVGs** (ISC license), single-colour →
  tintable. Concept→icon alias map (VN/EN) in the module (137 aliases) so a caller asks by MEANING
  ("thời gian"→clock, "chi phí"→coins, "seo"→search).
- **Emojis:** native colour emoji via Chromium (47 concept aliases: "cảnh báo"→⚠️, "tiền"→💰, …).
- **Manifest:** `2_SKILLS/element_maker/element_library.json` — the catalogue the pipeline/LLM picks
  from (types + params + icon/emoji aliases + role colours).
- **Integration:** `talking_head_edit` spec key **`elements:[{type, ..params.., t, dur, x, y, w?}]`** →
  each rendered to PNG → ffmpeg overlay with a fade-in/out at its beat (over footage, under captions).
  Frame-verified over real footage: a 3-tile ✕ problem-set + ⚠️ + a green ✓ solution tile + a chip.

## Element types (render now)

| type | what | key params | ref |
|---|---|---|---|
| `icon_tile` | glassy rounded tile + line-icon + optional corner **badge** (✓/✕/!/number) + label — THE core motif | icon, role, badge, label | V5/V2/V6/V9 |
| `chip` | rounded pill: icon + text (tag/label) | icon, role, label | V2/V7/V8 |
| `badge` | standalone big circle badge ✓/✕/!/? | kind, role | V5 |
| `emoji` | native colour emoji (functional punctuation) | name / char | V8 |
| `sparkle` | 4-point star glint | role | V1/V5 |
| `arrow` | hand-drawn dashed curved arrow | role | V4/V5 |
| `ring` | proof highlight ring (dashed rounded-rect) | role, w, h | V7 |
| `big_stat` | big number/stat pop (money/speed) | value, label, role | V1/V5 |
| `tile3d` | glossy pseudo-3D app-tile (iso-cube look) + icon + label | icon, role, label | V5/V1 |
| `phone` | phone bezel, optionally wrapping a screenshot | src (opt) | V7 |
| `bracket` | HUD corner brackets around a region | role, w, h | V2/V6 |
| `marker` | marker highlight-swipe bar behind bold text | role, label | V5 |

## Cross-reel element taxonomy (from the 9 catalogs)

- **Icons (line/filled):** time/clock, money/coins, people/users, work/briefcase-laptop-wrench,
  folder/file/box, tech/ai (bot·brain·code·plug·zap·database), comm (chat·mail·bell·share),
  SEO/marketing (search·globe·chart·target·megaphone·rocket·trophy·star·flame·lightbulb·key·link·tag·eye),
  status (check·x·alert·info·lock·shield), life (umbrella·sun·dumbbell·utensils). → **icon_tile / chip** ✓
- **Emojis:** ⚠️ 💡 🔥 💰 📊 ⚙️ 🌐 ⚖️ 👉 ✅ ❌ ⭐ 🚀 🎯 ✨ 🤖 🔒 (functional, sparse). → **emoji** ✓
- **Badges/marks:** ✕ (negation, coral) · ✓ (affirm, green) · ! · ? · number. → tile badge / **badge** ✓
- **Stickers/graphics:** sparkle · dashed hand-drawn arrow · proof ring · highlight-swipe bar ·
  HUD corner-brackets · progress bar. → **sparkle/arrow/ring** ✓ (brackets/swipe = easy next adds)
- **Text-effects:** two-tone keyword karaoke caption (DOMINANT, every reel) · big numeral · money-stat ·
  marker-highlight box. → already in the ASS caption engine + **big_stat** ✓
- **Cards/panels:** glass icon-tile · spec-list · step-badge · org-panel · label pill. → element_maker
  tiles/chips + the ASS card types (checklist/header/badge/section) built earlier.
- **Decorative:** neon-glow → **soft shadow** (brand law); radial glow; duotone wash. → CSS in the tiles.

## Asset-needed (not code — supplied or pre-rendered), noted honestly

- **Real screenshots / screen-recordings** (tool demos, chat proof, dashboards) — user-supplied, shown via
  the `broll` `full`/`split`/`frame`/`pip` modes (already built).
- **Device bezels** (phone/browser frame) — a small PNG asset set to add to `7_ASSETS/brand/` next.
- **3D iso-cubes · orbit rings · particle bursts · photo-cutouts** — pre-rendered PNG/clip assets or an
  SVG-3D pass; flagged per-reel in the `V*_elements.md` files. Low frequency; deferred.

## Auto-grow (the library enriches itself — `element_resolver.py`)

When the factory hits a NEW word/concept with no element yet, `resolve_icon(concept)` / `resolve_emoji(concept)`
resolve it and GROW the pool: **curated alias → learned cache → fuzzy Lucide name-match → local LLM (translate
concept→English → match the 1744-icon catalog)** → **auto-fetch** that SVG into `7_ASSETS/brand/icons/` → **learn**
the mapping (`_learned_icons.json` / `_learned_emoji.json`). So any new word gets an on-brand element and the
resource pool grows as the factory runs. Fully offline-degradable (LLM optional; falls back to fuzzy then a
neutral dot); each concept resolved ONCE then cached → negligible GPU. `element_maker` calls it automatically in
the render path, so `icon_tile`/`chip`/`tile3d`/`emoji` accept ANY concept word. Catalog cached in
`_lucide_names.json` (1744 icons). Started at 95 vendored icons → grows on demand (110+ and counting).

## Auto-PLACE from narration (`element_picker.py`) — the loop that makes elements get used

`pick_elements(words, W, H)` scans the word-level transcript (which the talking-head engine already
produces) and emits a timed `elements:[...]` plan: an icon-tile / emoji popped in a top-band slot exactly
when its concept word is spoken, with **role + badge inferred from nearby cues** — a "mất/tốn/không/tránh"
phrase → coral ✕ tile (problem), a "miễn phí/nhanh/tự động/hiệu quả" phrase → green ✓ tile (solution),
urgency → caution. Deterministic + alias-driven (reliable, no LLM); density-capped + slot-rotated so it never
clutters or covers the face/caption. **Wired into `talking_head_edit`: runs by default when no elements were
hand-authored** (opt out `auto_elements:false`; merge with explicit ones via `auto_elements:true`). So a plain
talking-head auto-gets the dense element layer. Verified over footage (SEO tile · coral-✕ "thời gian" ·
💰 · green-✓ "AI" all auto-placed from a sentence). Grow the cue lists / concept vocabulary in `element_picker.py`.

## Grow the library (manual)
Add a curated mapping: an entry in `element_maker.ICON_ALIASES` / `EMOJI_ALIASES` (deterministic, keeps common
concepts off the LLM). Add an element type: a branch in `element_maker._element_html` + CSS + a manifest entry.
Per-reel evidence: `V1..V9_elements.md`.

Related: [[talking-head-craft-study]] · [[talking-head-engine]] · [[brand-colors-light-only]] ·
[[design-system-and-craft]] · [[library-growth-pipeline]]
