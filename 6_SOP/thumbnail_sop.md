# SOP: SEOSONA Thumbnail Design (9:16 & 16:9)

*Updated to align with SEOSONA Tech-Editorial Brand Identity*

## 0. Pipeline (one module, one function, one pipeline)
Every thumbnail goes through **one** module with **one** public function:
`2_SKILLS/thumbnail_maker/thumbnail_maker.py` → `make_thumbnail(content, output_path, aspect_ratio, brand, ...)`.

`content → NLP variables (4_BRAIN/llm_engine, key-normalized) → highlight tuples → HTML render → branded PNG`

- Brand palettes, NLP wiring, highlight logic, and the Playwright render all live in that one module. Everything except `make_thumbnail` is private (`_`-prefixed). One template asset `templates/seosona_thumbnail.html` holds both layouts (portrait + landscape); the `{{ASPECT_CLASS}}` (`is-portrait`/`is-landscape`) on `<body>` selects which renders.
- Callers: `4_BRAIN/video_engine.py` (`_make_thumbnail`, `_repurpose`), `scripts/course_video.py`, `scripts/workflow_thumbnail.py` (npm `thumbnail:create`). They call **only** `make_thumbnail`.
- **Designer PNG = `Thumbnail/thumbnail.png` (canonical).** `native_composer` saves a raw frame grab as `Thumbnail/thumbnail_frame.png` (fallback only — they no longer overwrite each other).

## 0b. Connected skills (copy + design intelligence)
The copy/design step (`_COPY_DIRECTOR_SYSTEM` + `_nlp_variables`) operationalizes the repo's own skills so thumbnails are art-directed, not just rendered:

| Skill / source | Where | How it's used |
|---|---|---|
| Ogilvy, copywriting, copy-editing | `2_KNOWLEDGE/domain_skills/` | promise-first, clarity > cleverness, benefit > feature — encoded in the director system prompt |
| page-cro (3-sec scan), banner-design, `9_PROMPTS/design_assets/thumbnail_prompt_1` | domain_skills + prompts | one idea, word limits (pill ≤5, title 4–8, cta 2–4), single highlight |
| stop-slop | `2_KNOWLEDGE/domain_skills/stop-slop` | bans generic AI filler / clickbait |
| ui-styling (contrast ≥4.5:1) | `2_KNOWLEDGE/domain_skills/ui-styling` | satisfied by brand palette (light text on navy) |
| `_classify_intent`, `_extract_numbers` | `4_BRAIN/llm_engine` | callable grounding: pick the angle + a concrete stat so copy is specific |

These are **connected through the prompt + callable helpers**, not duplicated. To change the copy voice, edit `_COPY_DIRECTOR_SYSTEM` in `thumbnail_maker.py`. No image-generation/cutout capability exists in the repo (portrait images must be supplied via `portrait_path`).

## 1. Design Thinking & Style
- **Main Style**: Minimalism, Professional, "Tech-editorial", prioritizing ample White space.
- **Core Principles**: Focus on exactly 1 main idea. Text must be minimal, massive in size, and highly readable. Strictly NO flashy gradients, NO emojis, NO 3D/colorful icons.
- **Standard Size**: 1080×1920 (9:16 — TikTok/Shorts/Reels) and 1920×1080 (16:9 — YouTube/Facebook). Both render from the same orchestrator.

## 2. Standard Color Palette
- **#1A2DB5 (Dark Navy)**: Primary accent color, used as the main background.
- **#1565C0 (Blue)**: Accent text, Labels, Monochromatic icons.
- **#BBDEFB (Light Blue)**: Text on Navy background to highlight keywords.
- **#F3F6FA (Light Background)**: For internal UI panels or cards over the background.
- **#0E1633 (Ink)**: Main text color (on light panels).
- **#5A6588 (Gray)**: Secondary text color.
- **#E2E8F2 (Border)**: Thin border lines.
- **#FFD54F (Yellow)**: STRICTLY used to highlight max 1-2 critically important keywords (Hook/CTA).

## 3. Typography & Assets
- **Font**: Be Vietnam Pro (or similar Geometric Sans-serif).
- **Hierarchy**: Titles (Bold, tight line-height); Normal text (Regular/Medium, line-height 1.5).
- **Icons**: Thin Line/Outline style (Stroke ~1.7px), monochromatic Blue (#1565C0) inside rounded square containers.
- **Background Pattern**: Subtle dot grid + 1 giant, faded typographic/numeric watermark in the corner.

## 4. Mandatory Layout Structure
### Fixed Elements
- **Top-Left Corner**: SEOSONA Logo.
- **Footer**: Text "SEOSONA · Share to be shared more" separated by a thin top border line (#E2E8F2).

### Visual & Content Arrangement
- **Background**: Solid Navy (#1A2DB5) + Subtle white dot grid pattern.
- **Top Label**: Rounded pill-shaped label containing uppercase text (e.g., "AI SEO TIPS") under the logo.
- **Main Title**: Massive size, White color. Select exactly 1 crucial keyword to change to Light Blue (#BBDEFB).
- **Visual Accents**: Thin accent underline beneath main title. Minimalist UI panel or floating Line/Outline elements in the center.
- **Short Description**: Light gray/white text placed below the title or center visual.
- **Call To Action (CTA)**: Placed near the bottom, just above the footer. Important keywords highlighted in Yellow (#FFD54F).
