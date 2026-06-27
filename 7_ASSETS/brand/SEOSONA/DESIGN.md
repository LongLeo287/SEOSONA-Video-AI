# SEOSONA Video — Design System (brand contract)

Machine-readable brand law for every SEOSONA faceless video. Modeled on the
Open Design `DESIGN.md` format (150 brand systems, Apache-2.0) and adapted for
**9:16 motion**, not web pages. Any agent or generator producing a SEOSONA frame
MUST obey this file. It is the single source of truth that lets an LLM write HTML
per request while staying on brand. Pairs with the motion vocabulary in
`2_KNOWLEDGE/hyperframes/craft/` and the playbook in `9_PROMPTS/MASTER_VIDEO_SPEC.md`.

---

## 1. Visual Theme & Atmosphere

Professional, reputable, market-leading SEO/Marketing brand. Clean, bright,
confident — an authority that teaches. **100% Light Mode. Dark mode is forbidden.**

**Key Characteristics:**
- Bright, airy surfaces; generous whitespace; one decisive accent per scene.
- Vertical 9:16 (1080×1920, 30fps) for TikTok / Shorts / Reels.
- Calm structure + lively micro-motion. Content reveals progressively, in sync
  with narration — never dumped all at once.
- Crossfades that never blank (old scene exits before next mounts).
- Real content and real data only — no lorem ipsum, no fabricated numbers/stars.

---

## 2. Color Palette & Roles

### Primary
- **Brand Blue** (`#2A5BDA`): primary accent, default headings/CTA, trust.
- **Coral** (`#E2724D`): secondary accent, energy/highlight, "important" beats.
- **Green** (`#16A34A`): tertiary accent, success/positive, logo dot.

### Accent rotation (do not hardcode one accent)
Each scene gets a rotated accent so a template never renders identical twice:
`blue → green → orange`, derived from a stable hash of the output name
(`_auto_shift` / `_rotate_acc` in `native_composer.py`). Within a scene, ONE accent hue.

### Surface & Background
- **Pure White** (`#FFFFFF`): primary canvas, cards.
- **Mist** (`#F8FAFC`): secondary surface, subtle zone separation.
- **Hero gradient** (heroes only): `linear-gradient(157deg, {accent} 0%, #16224A 165%)`
  with white text — the one place white-on-color is allowed.

### Text / Ink
- **Ink** (`#0F172A`): all body + headings on light surfaces.
- **Slate** (`#475569`): secondary copy, labels, footer meta.
- White (`#FFFFFF`): only inside a hero gradient or on an accent-filled pill.

### Semantic
- Positive → green `#16A34A`. Caution/energy → coral `#E2724D`. Info → blue `#2A5BDA`.
- No new colors per element. Tint neutrals toward the scene accent, never dead gray.

---

## 3. Typography Rules

### Font Family
- **Display + Text:** `Be Vietnam Pro` (full Vietnamese diacritics — non-negotiable).
  Weights on disk: `BVP-Black` 900, `BVP-XBold` 800, `BVP-Bold` 700,
  `BVP-SemiBold` 600, `BVP-Medium` 500.
- Never substitute Latin-only display fonts (Druk/Anton/Inter) — they break diacritics.

### Hierarchy (9:16, 1080px wide)
- **Hero / big number:** 900, 120–220px, tight leading.
- **Scene heading (2-tone h1/h2):** 800, 64–88px. h1 ink, h2 accent (or reverse in hero).
- **Kicker pill:** 700, 24–28px, uppercase, tracked +2–4%.
- **Body / list item:** 500–600, 30–40px. Sub-label: 500, 22–26px slate.
- **Karaoke caption:** 600, 36px (single track, bottom pill). Never larger.
- **Footer:** 500, ~24px slate.

### Principles
- Weight ladder does the emphasis; avoid more than 3 sizes per scene.
- One sentence per beat — headlines are short, never paragraphs in a frame.

---

## 4. Component Stylings

14 brand components (`native_composer.py`): bignum, repo, compare, terminal, steps,
badges, gittree, cta, stats, quote, tip, feature, chart, mockup.

- **Cards / tiles:** white on mist, radius 20–28px, soft shadow
  `0 8px 40px rgba(15,23,42,.10)`. No left-edge accent stripes (AI tell).
- **Pills (kicker / CTA / badge):** accent-filled or accent-outline, radius 999px,
  padding 12–18px × 22–38px. CTA pill uses accent fill + white text.
- **Big number:** tabular-nums, paired with an accent-tinted radial glow or fill bar
  (a number must never float alone — see `craft/data-in-motion.md`).
- **Chart:** GSAP + CSS/SVG bars only. No pie charts, no gridlines/legends,
  no 6-panel dashboards, no chart-library output. 2–3 related bars max.
- **Karaoke:** single bottom pill, **navy background** (`#16224A`), white text; the
  active (spoken) word flips to the scene accent + weight 800, passed words go light
  gray `#E5E7EB`. One track only — never two subtitles at once.
- **Footer (persistent):** `● SEOSONA AI · Share to be shared more` — green dot,
  brand name bold, tagline slate. Sits at bottom ~230px.

---

## 5. Layout Principles

### Frame & Safe Zones (9:16)
- Canvas 1080×1920. Keep all content within ~80px side margins.
- **Bottom UI safe zone ~160px** (platform controls). Karaoke pill at `bottom:300px`,
  footer at `bottom:230px` — never below.
- Persistent logo top-left; kicker pill top area; heading upper-third; component mid.

### Composition
- Anchor content to an edge + add a second focal point (label, data bar, divider).
  Never a single centered block floating in empty space.
- Zone-based layouts (top metadata bar, full-width body) over centered stacks.
- Background is never empty: 2–3 ambient decoratives (accent radial glow breathing,
  oversized ghost word at 4–6% opacity drifting, hairline rule pulsing).

### Border Radius Scale
- Pills 999px · cards/tiles 20–28px · inner chips 12–16px · media frames 16px.

---

## 6. Depth & Elevation

- Light, soft elevation only: `0 8px 40px rgba(15,23,42,.08–.12)`. No harsh drop shadows.
- Decorative depth from accent-tinted radial glows (low opacity) and faded oversized
  type bleeding off-frame — all with slow ambient GSAP motion (breathe/drift/pulse).
- No glassmorphism, no neon glows, no dark vignettes.

---

## 7. Do's and Don'ts

### Do
- Light surfaces, one rotated accent per scene, exact brand hex values.
- Reveal content progressively in sync with the voice; one pop SFX per reveal.
- Vary entrance direction + ease per item (see `craft/motion-recipes-seosona.md`).
- Real data, real screenshots, Vietnamese-correct text via the lexicon.
- Keep captions inside safe zones; single karaoke track.

### Don't
- ❌ Dark mode, neon, cyan-on-black, purple→blue gradients (all forbidden).
- ❌ Gradient text, left-edge accent stripes, identical card grids (AI tells).
- ❌ Latin-only display fonts (breaks Vietnamese diacritics).
- ❌ Pie charts, multi-axis charts, 6-panel dashboards, chart-library output.
- ❌ Two subtitles at once; oversized captions; content below the safe zone.
- ❌ Fabricated numbers, fake star counts, placeholder images.

---

## 8. Platform / Output Behavior

- **Aspect:** 9:16 (1080×1920) primary. Talking-head engine also supports 16:9.
- **Duration:** 45–60s standard (8–12 sentences). Auto-pace atempo if voice > ~64s.
- **Audio:** voice-dominant + BGM sidechain-ducked + per-component SFX.
  Final mix `alimiter → loudnorm (-14 LUFS) → aresample=48000`. **Output MUST be
  48 kHz AAC** (96 kHz silently fails on many players — see [[raw-mp4-path-bug]]
  and the sample-rate fix).
- **Voice:** VieNeu clone of the brand reference (`seosona_ref13.wav`), male, single
  consistent take, English/acronyms via the pronunciation lexicon.
- **Captions:** SRT for upload kept in `_captions_upload/` (not auto-loaded by players).

---

## 9. Agent Prompt Guide (how an LLM generates on-brand HTML per request)

This is the Open Design model: the agent writes a fresh HTML/CSS+GSAP scene per
request; THIS file keeps it on brand. When prompting a generator:

### Quick Color Reference
```
blue   #2A5BDA   coral  #E2724D   green  #16A34A
ink    #0F172A   slate  #475569   white  #FFFFFF   mist #F8FAFC
hero gradient: linear-gradient(157deg, {accent} 0%, #16224A 165%)
```

### Standing instructions to inject into any generation prompt
- "Light mode only. Use the SEOSONA palette above. One rotated accent for this scene: `{accent}`."
- "Be Vietnam Pro for all text. 9:16, 1080×1920, respect the 160px bottom safe zone."
- "Real content, real data. Progressive reveal synced to narration. 2–3 ambient
  background decoratives. Vary entrance direction + ease per item."
- "No dark mode, no neon, no gradient text, no pie charts, no left-edge stripes."

### Iteration Guide
- Too flat? → add background depth (glow + ghost word + hairline), give the big number
  a fill bar, vary the eases (`craft/motion-recipes-seosona.md`).
- Feels off-brand? → re-check accent is one of the three brand hues; kill any neon/dark.
- Feels generic/AI? → break the centered stack, anchor to an edge, add a second focal point.

### Known Gaps
- Lexicon doesn't yet cover every English term (e.g. `content`, `ranking`,
  `Search Console`) — extend `news_video_standards.CORE_PRONUNCIATION_LEXICON` as needed.

Related: [[master-video-spec]] · [[brand-colors-light-only]] · [[render-engine-video-engine]] · `2_KNOWLEDGE/hyperframes/craft/SEOSONA-INDEX.md`
