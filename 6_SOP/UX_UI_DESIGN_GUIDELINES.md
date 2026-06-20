# SEOSONA Video: UX/UI Design Guidelines

> Extracted sources: `SEOSONA Website/DESIGN.md` and `SEOSONA OS/4_AGENTS/personas/ui-ux-designer.md`

## 1. Design Philosophy
SEOSONA Video complies with B2B Premium standards:
- Whitespace: Always use generous whitespace to create a luxurious feeling.
- Display (Typography): Prioritize clear, easy-to-read Typography structure on mobile.
- Consistency: Do not use flashy "Neon", "Cyberpunk" colors. Focus on trust, data, engineering.

## 2. Color Token (Color System)
When creating a Video with Light Theme:
- **Background Base (Pure White):** `#FFFFFF`
- **Background Surface:** `#F8FAFC`
- **Text Headers (Bold Ink):** `#04091A` (Absolutely do not use `#000000`)
- **Text Body:** `#64748B`
- **Primary Accent (Xanh Signal):** `#1D4ED8`

When creating a Video with Dark theme (Navy Theme - Inherited from Video Legacy):
- **Background Base:** `#1A2DB5` (Navy Brand)
- **Primary Accent:** `#FFD54F` (Yellow)
- **Text:** `#FFFFFF`

## 3. Geometry & Layout
- **Border Radius:** Soft, from `16px` to `40px` for card blocks (Cards/Mockups). Absolutely DO NOT use sharp corners.
- **Shadows:**
  - Light shadow for Box Logo: `box-shadow: 0 10px 30px rgba(0,0,0,0.2)`
  - Shading for 3D Mockup: Up to `0 40px 100px rgba(0,0,0,0.3)`
- **Animation Effects (GSAP):**
  - Text & UI appearance: Should use `back.out(1.4)` or `expo.out` to create a natural "bounce" feeling.
  - Multi-layered mockup: The secondary background image is always blurred `filter: blur(2px)` and has its Opacity reduced, while the main image `z-index` is highest and sharpest.

## 4. Typography
- **Heading Font:** `Be Vietnam Pro` (Recommended `font-weight: 800-900`, `letter-spacing: -1.5px` for modern compression).
- **Body Font:** `Be Vietnam Pro` (`font-weight: 500`, `line-height: 1.5`).

## 5. Review Criteria (Interface approval process)
Before Pipeline Render Video, Agent needs to check:
1. Contrast of Text (Text Contrast) compared to Background.
2. Is the Brand Logo submerged? (Required to use `White pill box` if the background is dark).
3. Is the text overflowing over the Mockup Image area? (Separate Container is required).
