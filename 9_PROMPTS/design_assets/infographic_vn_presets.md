# Infographic / Thumbnail design presets (Vietnamese-safe)

Distilled from `tuanminhhole/openclaw-skill-infographic` (MIT). Use these for any
Vietnamese infographic, thumbnail, carousel, or poster — they prevent the #1 failure
(Vietnamese glyph clipping / Unicode breakage) and give consistent on-brand styles.

## 🇻🇳 Vietnamese typography (MANDATORY)
1. **Fonts — use ONLY Unicode-complete sans**: `Inter, Montserrat, Roboto, Plus Jakarta Sans, Be Vietnam Pro, Fredoka`. (SEOSONA brand font = **Be Vietnam Pro**, already in `7_ASSETS/brand/fonts/`.)
2. **NEVER use** decorative / script / handwritten / gothic / calligraphy / futuristic fonts — they lack Vietnamese diacritics and clip or drop glyphs.
3. When prompting an image model, wrap every Vietnamese passage **in single or double quotes** so the model treats it as literal text and renders the diacritics correctly.

## 🎨 Three design strategies (pick one per piece)
| Strategy | Layout | Colors | Type | Use for |
|----------|--------|--------|------|---------|
| **Editorial News** | multi-column grid, thin dividers, flat vector icons | professional/corporate | serif headers + sans body | tech-news explainers, data |
| **Warm Pastel Guide** | 3×3 numbered rounded cards, cute 2D mascots | cream / light-green / pale-yellow | friendly rounded sans | how-to / tutorial carousels |
| **Neo-Brutalism** | thick dark solid borders, hard black drop shadows, high-contrast cards | yellow / cyan / lime / orange | bold non-serif, flat 2D | punchy social / attention thumbnails |

## 📐 Aspect ratio presets
- **1:1** square — feed / carousel (`1080×1080`)
- **2:3** vertical poster — stories / pin (`1080×1620`)
- **16:9** landscape — YouTube thumbnail / banner (`1920×1080`)
- **9:16** vertical — Shorts / TikTok / Reels (`1080×1920`) *(SEOSONA default for video)*

## Branding
Footer / watermark = SEOSONA brand (logo from `7_ASSETS/brand/logos/`), not any third-party tag.

## Optional image-gen backend
The source skill generates PNGs via image models (Recraft v3 / Flux Ultra / Ideogram)
through the **9Router** gateway. To use that path, set `9router` credentials in
`1_CONFIG/` (`NINE_ROUTER_API_KEY`), then call the model with one of the strategy
prompts above. SEOSONA's default thumbnail path is HTML (`2_SKILLS/thumbnail_maker/`) —
these presets apply to both.
