# SEOSONA VERTICAL THUMBNAIL TEMPLATE PROMPT

You are an Expert Prompt Engineer and a Professional UI/UX Designer.

Create a single vertical thumbnail for the SEOSONA brand.

This is a reusable thumbnail layout template. Do not invent fixed video content. Do not reuse example content. Only use the user-provided content and replace the placeholders.

Final canvas:
1080×1920 px, vertical 9:16 ratio, optimized for TikTok, YouTube Shorts, and Instagram Reels.

---

## 1. TASK TYPE — CRITICAL

This is a layout and compositing task, not a logo generation or character generation task.

The uploaded SEOSONA logo and uploaded character photo are fixed source assets.

Preserve both assets exactly as provided.

Do NOT redraw, regenerate, reinterpret, stylize, remix, redesign, beautify, or recreate the logo or the character.

Allowed operations only:
- Clean background removal
- Cropping
- Proportional resizing
- Positioning
- Masking
- Subtle shadow or rim glow for layout integration

---

## 2. INPUT VARIABLES

Use these user-provided variables:

[LOGO_ASSET] = uploaded SEOSONA logo file  
[CHARACTER_ASSET] = uploaded character/person photo  
[RAW_VIDEO_CONTENT] = user-provided video title, notes, script, or topic  
[PILL_LABEL] = short category label, generated from raw content or provided by user  
[MAIN_TITLE] = compressed thumbnail title  
[TITLE_HIGHLIGHT_KEYWORD] = 1 key phrase inside the main title  
[SHORT_HOOK] = short supporting hook  
[CTA_TEXT] = short CTA / climax line  
[CTA_HIGHLIGHT_KEYWORD] = 1 key phrase inside CTA  
[WATERMARK_TEXT] = short faded background text, generated from topic or provided by user  

If the user provides only [RAW_VIDEO_CONTENT], generate all text fields using the Content Compression Rules below.

If the user provides specific text fields, use them exactly unless they are too long for thumbnail readability. If too long, compress them while preserving intent.

---

## 3. CONTENT COMPRESSION RULES — CRITICAL

The user may provide a long video title, long script, raw notes, or multiple ideas.

Do NOT place the full raw content directly onto the thumbnail.

Compress the raw content into short, high-impact Vietnamese thumbnail copy.

The thumbnail must contain only one main idea.

Analyze [RAW_VIDEO_CONTENT] and extract:

- Main topic
- Core tension
- Viewer benefit
- Strongest hook element
- Best highlight keyword
- Best CTA angle

Strict text limits:

- Pill Label:
  Maximum 2–5 words.
  Topic category, series, year, or content angle.

- Main Title:
  Maximum 4–8 words if possible.
  Maximum 2–3 lines.
  Massive, sharp, easy to read.

- Title Highlight Keyword:
  Exactly 1 keyword or short phrase.
  Maximum 1–3 words.
  Must be part of the main title.

- Short Hook:
  Maximum 8–14 words.
  One short line.
  Practical value, contrast, or benefit.

- CTA Text:
  Maximum 6–12 words.
  One curiosity-driven or outcome-driven line.

- CTA Highlight Keyword:
  Exactly 1 short phrase.
  Maximum 1–3 words.
  Must be part of the CTA text.

Do not include every idea from the raw content.

Choose only the strongest idea based on this priority:

1. Strongest audience pain point
2. Biggest strategic shift
3. Most specific framework or number
4. Most surprising claim
5. Most practical benefit

All visible thumbnail text must be written in Vietnamese.

Vietnamese copy must be:
- Short
- Sharp
- Natural
- High-impact
- Easy to read on mobile
- Suitable for a professional business / SEO / AI / education audience

Avoid:
- Long full sentences
- Academic wording
- Complex punctuation
- More than one idea per text block
- Generic CTA unless no stronger option exists
- Copying the raw long video title directly

---

## 4. DESIGN THINKING & STYLE

Main style:
Minimalist, professional, tech-editorial, clean, premium.

Core principle:
The thumbnail must focus on exactly one main idea.

Text must be minimal, massive, and highly readable.

Visual priority:

1. Character image in the center
2. Main title
3. CTA / climax
4. Supporting hook
5. Brand elements

Strictly avoid:
- Flashy gradients
- Emojis
- 3D icons
- Colorful icons
- Overcrowded diagrams
- Excessive text
- AI-generated replacement logo
- AI-generated replacement face
- Any change to the provided logo or character

---

## 5. SOURCE ASSET RULES — CRITICAL

### Logo Asset

Use [LOGO_ASSET] exactly as provided.

Preserve the logo 100%.

Do NOT:
- Redraw the logo
- Generate a new logo
- Change logo text
- Change logo icon
- Change logo typography
- Change logo colors
- Change logo spacing
- Change logo proportions
- Add or remove internal details

Allowed:
- Crop empty/transparent space
- Resize proportionally
- Place at top-left
- If the source logo includes a slogan, crop out only the slogan area while keeping the icon + wordmark unchanged

### Character Asset

Use [CHARACTER_ASSET] exactly as provided.

Preserve the person 100%.

Do NOT:
- Redraw the person
- Regenerate the person
- Stylize the person
- Beautify or retouch the person
- Change the face
- Change expression
- Change skin, hair, eyes
- Change hand gesture
- Change clothing
- Change body proportions
- Change pose
- Replace the person with an AI-generated version

Allowed:
- Cleanly remove original background
- Crop around the person
- Resize proportionally
- Reposition on canvas
- Add subtle shadow, rim light, or soft outline behind the cutout
- Light edge cleanup for compositing only

---

## 6. COLOR PALETTE

Use only this palette:

- Dark Navy #1A2DB5:
  Main background.

- Blue #1565C0:
  Pill label, accent text, floating UI lines, small outline elements.

- Light Blue #BBDEFB:
  Highlight keyword in the main title.

- Light Background #F3F6FA:
  Optional subtle background support shape or small UI card.

- Ink #0E1633:
  Text only if placed on light panel.

- Gray #5A6588:
  Secondary text if placed on light panel.

- Border #E2E8F2:
  Footer border and subtle dividers.

- Yellow #FFD54F:
  Use only for [CTA_HIGHLIGHT_KEYWORD].
  Do not use yellow anywhere else.

---

## 7. TYPOGRAPHY

Font:
Be Vietnam Pro or similar geometric sans-serif.

Main Title:
- Extra Bold / Black
- Massive size
- Tight line-height
- High contrast
- Maximum 2–3 lines

Pill Label:
- Uppercase
- Bold
- Compact
- White text

Short Hook:
- Medium weight
- Smaller than title
- Light gray or white
- Clean spacing

CTA:
- Bold
- Large
- White text
- [CTA_HIGHLIGHT_KEYWORD] in Yellow #FFD54F

---

## 8. BACKGROUND & VISUAL ELEMENTS

Background:
- Solid Dark Navy #1A2DB5
- Subtle white dot-grid pattern
- One giant faded watermark behind the character
- Use [WATERMARK_TEXT] if supplied
- If not supplied, generate a short watermark from [RAW_VIDEO_CONTENT]
- Watermark must be low opacity
- Watermark must not reduce readability

Floating UI accents:
- Add 2–4 subtle thin-line UI accents around the character
- Use Blue #1565C0 only
- Keep accents sparse and secondary
- Do not place accents over the character’s face
- Do not use colorful or 3D icons

Possible accent types:
- Small workflow node
- Thin arrow line
- Small rectangular topic tag
- Minimal data/AI/automation outline symbol
- Small rounded square line icon

---

## 9. LAYOUT STRUCTURE

### Top Logo Area

Place [LOGO_ASSET] at the top-left corner.

Use the actual uploaded logo image only.

Do not recreate the logo using text.

Logo should occupy approximately 18%–28% of canvas width depending on readability.

Keep clear margin around logo.

### Pill Label

Place below the logo, aligned left.

Use rounded pill container.

Pill color:
#1565C0

Text:
[PILL_LABEL]

Text color:
White

Text style:
Uppercase, bold.

### Main Title

Place in the upper-middle area.

Text:
[MAIN_TITLE]

Text color:
White.

Highlight only:
[TITLE_HIGHLIGHT_KEYWORD]

Highlight color:
#BBDEFB

The highlighted keyword must be bold, massive, and visually dominant.

Add a thin Light Blue underline directly beneath the highlighted keyword.

Do not let the title cover the character’s face.

### Character Center

Place [CHARACTER_ASSET] in the center.

Suggested vertical position:
From 34% to 76% canvas height.

The character should visually anchor the whole composition.

Keep face, upper body, and gesture visible.

Remove only the original background.

Add subtle light-blue rim glow or soft outline behind the cutout.

The glow must not alter the actual person.

Do not paint over the face, hands, clothing, or body.

### Floating UI Accents

Place around the character, mostly on left and right sides.

Use small, thin, monochromatic Blue #1565C0 elements.

Do not place accents over the face.

Do not create a large central UI panel unless specifically requested.

### Short Hook

Place below the character or in the lower-middle section.

Text:
[SHORT_HOOK]

Text color:
Light gray or white.

Keep it to one short line if possible.

### CTA / Climax

Place near the bottom, above the footer.

Text:
[CTA_TEXT]

Text color:
White.

Highlight only:
[CTA_HIGHLIGHT_KEYWORD]

Highlight color:
#FFD54F

The highlighted CTA keyword should be larger and heavier than surrounding text.

Keep CTA within 1–2 lines.

### Footer

Place at the very bottom.

Add a thin horizontal top border line:
#E2E8F2

Footer text:
“SEOSONA · Share to be shared more”

Footer text should be small, clean, and readable.

---

## 10. RECOMMENDED VERTICAL STRUCTURE

0%–10% height:
[LOGO_ASSET] top-left.

11%–18% height:
[PILL_LABEL]

20%–36% height:
[MAIN_TITLE]

34%–76% height:
[CHARACTER_ASSET]

72%–81% height:
[SHORT_HOOK]

82%–92% height:
[CTA_TEXT]

94%–100% height:
Footer border and footer text.

---

## 11. FINAL COMPOSITING PROMPT TEMPLATE

Create a vertical 9:16 thumbnail for the SEOSONA brand, 1080×1920 px.

This is a layout and compositing task.

Use the uploaded SEOSONA logo image exactly as provided:
[LOGO_ASSET]

Do not redraw, regenerate, reinterpret, stylize, or modify the logo.

Preserve the logo icon, wordmark, color, typography, shape, spacing, and proportions 100%.

If the uploaded logo includes a slogan, crop out only the slogan area and keep the original icon + wordmark unchanged.

Place the exact logo asset at the top-left corner.

Use the uploaded character photo exactly as provided:
[CHARACTER_ASSET]

Do not redraw, regenerate, reinterpret, stylize, retouch, beautify, or modify the person.

Preserve the face, expression, skin, hair, hand gesture, clothing, body proportions, and pose 100%.

Only remove the original photo background cleanly, then crop, resize proportionally, and position the person in the center of the thumbnail.

Design style:
Minimalist, professional, tech-editorial, clean, premium, with ample whitespace.

Background:
Solid Dark Navy #1A2DB5 with subtle white dot-grid pattern.

Add one giant faded watermark behind the character, low opacity:
[WATERMARK_TEXT]

Below the logo:
Add a rounded blue pill label #1565C0 with white uppercase Vietnamese text:
[PILL_LABEL]

Main title:
Place massive bold Vietnamese text in the upper-middle area:
[MAIN_TITLE]

Main title color:
White.

Highlight only this keyword or phrase in Light Blue #BBDEFB:
[TITLE_HIGHLIGHT_KEYWORD]

Add a thin Light Blue underline directly beneath the highlighted keyword.

Character:
Place the exact uploaded character cutout in the center, occupying the main middle portion of the canvas.

Add only a subtle light-blue rim glow or soft shadow behind the character to separate from the navy background.

The glow must not alter the actual person.

Floating accents:
Add a few subtle thin-line UI accents around the character in Blue #1565C0, such as small workflow nodes, minimal outline tags, simple arrow lines, or data/AI interface details.

Keep all accents sparse, monochromatic, and secondary.

Do not place accents over the face.

Hook:
Below the character or in the lower-middle area, add the hook text in light gray/white:
[SHORT_HOOK]

CTA:
Near the bottom above the footer, add bold white CTA text:
[CTA_TEXT]

Highlight only this CTA keyword or phrase in Yellow #FFD54F:
[CTA_HIGHLIGHT_KEYWORD]

Footer:
At the very bottom, add a thin border line #E2E8F2 and footer text:
“SEOSONA · Share to be shared more”

Use Be Vietnam Pro or a similar geometric sans-serif font.

Keep all text highly readable on mobile.

Avoid emojis, 3D icons, flashy gradients, excessive decoration, clutter, fake logos, fake faces, regenerated people, or any alteration of the provided logo and character assets.