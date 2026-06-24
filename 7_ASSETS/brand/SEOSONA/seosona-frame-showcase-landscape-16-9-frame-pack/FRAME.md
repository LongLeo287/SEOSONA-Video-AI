---
source: design.md
brand: SEOSONA
register: Premium B2B Light · clean SaaS/agency · trustworthy, technical, data-driven
primary_aspect: 16:9 (1920×1080)

colors:
  canvas:
    base: "#FFFFFF"          # Pure white — primary ground
    surface: "#F8FAFC"       # slate-50 — elevated ground
    elevated: "#F1F5F9"      # slate-100 — second elevation
  ink:
    header: "#04091A"        # NEVER pure black
    body: "#64748B"          # slate-500
    muted: "#94A3B8"         # slate-400
  signal:
    primary: "#1D4ED8"       # blue-600 — sole primary accent
    hover: "#2B8FD4"
  accent:
    indigo: "#6366F1"        # indigo-500 — micro-icon only
    amber: "#F59E0B"         # amber-500 — micro-icon only
  border:
    standard: "#E2E8F0"      # slate-200
    soft: "#F1F5F9"          # slate-100

typography:
  fontFamily:
    display: "var(--font-poppins), 'Poppins', system-ui, sans-serif"
    sans: "var(--font-inter), 'Inter', system-ui, sans-serif"
  # --- Reading ramp (px from source, cqw added for frame-relative authoring) ---
  reading:
    micro:        { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 500, fontSize: "13px / 0.68cqw",  lineHeight: 1.4,  letterSpacing: "0.04em" }
    body-sm:      { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 500, fontSize: "15px / 0.78cqw",  lineHeight: 1.6,  letterSpacing: "0" }
    body:         { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 500, fontSize: "17px / 0.88cqw",  lineHeight: 1.65, letterSpacing: "0" }
    label:        { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 600, fontSize: "14px / 0.73cqw",  lineHeight: 1.3,  letterSpacing: "0.08em", textTransform: "uppercase" }
    title-sm:     { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "26px / 1.35cqw",  lineHeight: 1.15, letterSpacing: "-0.01em" }
    title-md:     { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "40px / 2.08cqw",  lineHeight: 1.1,  letterSpacing: "-0.02em" }
  # --- Display / hero ramp (frame-native) ---
  display:
    wordmark-mega:  { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "22cqw", lineHeight: 0.86, letterSpacing: "-0.05em" }
    display-hero:   { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "11cqw", lineHeight: 0.92, letterSpacing: "-0.035em" }
    display-claim:  { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "7.2cqw", lineHeight: 0.96, letterSpacing: "-0.03em" }
    section-head:   { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "4.4cqw", lineHeight: 1.05, letterSpacing: "-0.02em" }
    stat-mega:      { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "18cqw", lineHeight: 0.86, letterSpacing: "-0.045em" }
    stat-ledger:    { fontFamily: "{typography.fontFamily.display}", fontWeight: 900, fontSize: "3.6cqw", lineHeight: 1.0,  letterSpacing: "-0.02em" }
    kicker:         { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 600, fontSize: "1.1cqw", lineHeight: 1.3,  letterSpacing: "0.18em", textTransform: "uppercase" }
    caption:        { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 500, fontSize: "1.4cqw", lineHeight: 1.45, letterSpacing: "0" }
    pill-giant:     { fontFamily: "{typography.fontFamily.sans}",    fontWeight: 600, fontSize: "1.5cqw", lineHeight: 1.0,  letterSpacing: "0.02em" }

rounded:
  pill: "9999px"          # buttons, chips
  card-sm: "28px"         # card minimum
  card-lg: "40px"         # card maximum / hero cards
  hair: "4px"             # micro-chips, sparkline ticks

spacing:
  hair: "1px"
  micro: "8px"
  card-pad-1: "24px"      # p-6
  card-pad-2: "32px"      # p-8
  card-pad-3: "40px"      # p-10
  section-y: "96px"       # py-24
  frame-pad: "5cqw"       # safe area inset for every frame
  frame-gutter: "2.2cqw"  # inter-element gap default

components:
  # --- Surfaces ---
  surface-canvas:
    backgroundColor: "{colors.canvas.base}"
    textColor: "{colors.ink.header}"
  surface-tint:
    backgroundColor: "{colors.canvas.surface}"
    textColor: "{colors.ink.header}"
  surface-elevated:
    backgroundColor: "{colors.canvas.elevated}"
    textColor: "{colors.ink.header}"
  surface-ink:
    backgroundColor: "{colors.ink.header}"
    textColor: "{colors.canvas.base}"

  # --- Buttons (source: design.md §5) ---
  button-primary:
    backgroundColor: "{colors.ink.header}"
    textColor: "{colors.canvas.base}"
    typography: "{typography.reading.body}"
    rounded: "{rounded.pill}"
    padding: "14px 24px"
    hoverBackgroundColor: "{colors.signal.primary}"
  button-primary-giant:
    backgroundColor: "{colors.ink.header}"
    textColor: "{colors.canvas.base}"
    typography: "{typography.display.pill-giant}"
    rounded: "{rounded.pill}"
    padding: "1.4cqw 2.6cqw"
  button-secondary:
    backgroundColor: "{colors.canvas.surface}"
    textColor: "{colors.ink.header}"
    typography: "{typography.reading.body}"
    rounded: "{rounded.pill}"
    padding: "14px 24px"
    border: "1px solid {colors.border.standard}"
  button-signal:
    backgroundColor: "{colors.signal.primary}"
    textColor: "{colors.canvas.base}"
    typography: "{typography.display.pill-giant}"
    rounded: "{rounded.pill}"
    padding: "1.4cqw 2.6cqw"

  # --- Cards (source: §5 — slate-200 hairline, sm shadow, soft radius) ---
  card-soft:
    backgroundColor: "{colors.canvas.base}"
    textColor: "{colors.ink.header}"
    rounded: "{rounded.card-lg}"
    padding: "{spacing.card-pad-3}"
    border: "1px solid {colors.border.standard}"
    shadow: "0 1px 2px 0 rgba(4,9,26,0.04)"
  card-tint:
    backgroundColor: "{colors.canvas.surface}"
    textColor: "{colors.ink.header}"
    rounded: "{rounded.card-lg}"
    padding: "{spacing.card-pad-3}"
    border: "1px solid {colors.border.soft}"
  card-stat:
    backgroundColor: "{colors.canvas.base}"
    textColor: "{colors.ink.header}"
    rounded: "{rounded.card-sm}"
    padding: "2.2cqw 2.6cqw"
    border: "1px solid {colors.border.standard}"

  # --- Chrome atoms ---
  chip-eyebrow:
    backgroundColor: "{colors.canvas.surface}"
    textColor: "{colors.ink.header}"
    typography: "{typography.display.kicker}"
    rounded: "{rounded.pill}"
    padding: "0.55cqw 1.1cqw"
    border: "1px solid {colors.border.standard}"
  chip-status-signal:
    backgroundColor: "rgba(29,78,216,0.08)"
    textColor: "{colors.signal.primary}"
    typography: "{typography.display.kicker}"
    rounded: "{rounded.pill}"
    padding: "0.55cqw 1.1cqw"
  rule-hair:
    height: "1px"
    backgroundColor: "{colors.border.standard}"
  dot-signal:
    backgroundColor: "{colors.signal.primary}"
    width: "0.7cqw"
    height: "0.7cqw"
    rounded: "{rounded.pill}"
  icon-indigo:
    color: "{colors.accent.indigo}"
    size: "1.8cqw"
  icon-amber:
    color: "{colors.accent.amber}"
    size: "1.8cqw"

  # --- Frame-scale composed units ---
  wordmark-lockup:
    typography: "{typography.display.wordmark-mega}"
    textColor: "{colors.ink.header}"
  hero-claim:
    typography: "{typography.display.display-hero}"
    textColor: "{colors.ink.header}"
  stat-numeral:
    typography: "{typography.display.stat-mega}"
    textColor: "{colors.ink.header}"
  ledger-cell:
    backgroundColor: "{colors.canvas.base}"
    border: "1px solid {colors.border.standard}"
    rounded: "{rounded.card-sm}"
    padding: "1.6cqw 1.8cqw"
    typography: "{typography.display.stat-ledger}"
  sparkline:
    color: "{colors.signal.primary}"
    height: "3.2cqw"
    strokeWidth: "0.18cqw"
---

# frame.md — SEOSONA at frame scale

> **Atoms are sacred · composition is free · numbers come from the script.**

## Overview

SEOSONA at frame scale is a **white-canvas, ink-on-light, single-blue-signal** brand. The web register is "premium B2B, clean SaaS/agency, trustworthy, technical, data-driven" — at frame scale that becomes **a calm, hairline-ruled white frame with one black wordmark or one black-ink claim, a single blue dot or pill that fires the eye, and generous silence around everything**. No dark grounds, no neon, no color blocks. Depth is a 1-px slate-200 line and a barely-there shadow — never a glassmorphic stack.

### Frame Craft Bar
- **Squint** — one element dominates at 3–6× the next: the wordmark, the hero claim, the stat numeral. If two ink elements compete, demote one.
- **Silence** — sparse archetypes (cover, claim, focal-artifact, closer) read **65–75% empty**. White is the brand's confidence. **Named exception:** the ledger/dashboard plate, which is the only dense archetype.
- **Restraint** — the **{colors.signal.primary}** blue fires **once per frame** (one dot, one pill, one sparkline). Two blue elements at full strength is a failure; demote one to tint (8% alpha) or ink.
- **Reference bar** — aim at: a **Stripe keynote slide** (white canvas, oversized ink claim, one blue accent). Failure looks like: a generic SaaS feature grid, three icon-+-headline columns parked side-by-side under a top-left kicker.

## Colors

The palette is unchanged from `design.md`. At frame scale the rules harden:

- **Grounds are white-family only.** Every frame's ground is `{colors.canvas.base}`, `{colors.canvas.surface}`, or `{colors.canvas.elevated}`. Dark grounds are prohibited per source §1, §6. The single dark surface is `{components.surface-ink}` used at **chrome scale** (a pill, a stat token, a button) — never as a full-frame ground.
- **Ink is `{colors.ink.header}`, never `#000`.** Body copy is `{colors.ink.body}`; secondary metadata is `{colors.ink.muted}`.
- **One signal: `{colors.signal.primary}`.** Fires once per frame. Tinted form `rgba(29,78,216,0.08)` is allowed as a status-chip ground; that does not count as the signal "firing."
- **Indigo and amber are micro-icon only.** ≤1.8cqw glyphs inside ledger cells or status icons. They are forbidden at any scale that would read as a color block.
- **Borders are slate-200 hairlines.** Every card, cell, and divider uses a 1px `{colors.border.standard}` line. Hairline rules carry depth — soft shadow is a whisper, never a stack.

## Typography

Two ramps live in the frontmatter; this section is context.

The **reading ramp** carries the source's px hierarchy (micro/body/label/title) with cqw equivalents so the same line works in a card and across a frame. Headers are `{typography.fontFamily.display}` Poppins **900** (font-black, the source weight ceiling — never invent 800 or 950); body is `{typography.fontFamily.sans}` Inter **500**. Tracking tightens with size (-0.02em at title, -0.05em at wordmark).

The **display ramp** is frame-native and far larger than anything in `design.md`. `{typography.display.wordmark-mega}` at **22cqw** owns the cover. `{typography.display.display-hero}` at **11cqw** carries the claim plate, fitted to measure: ≤3 words → top step, 4–6 → step down to `{typography.display.display-claim}`, 7+ → step down to `{typography.display.section-head}`. The text block never exceeds **78cqw** wide and never touches the safe margin.

**Legibility floor: 1.4cqw (~27px @1920).** Anything below that is chrome — eyebrow kickers, captions, index numerals — and may not carry a beat's meaning. `{typography.display.kicker}` is the floor for kickers (1.1cqw, uppercase + 0.18em tracking, by definition decorative).

## Layout — The Frame

- **Primary frame:** 1920×1080 (16:9). Secondary: 1080×1920 (9:16), 1080×1080 (1:1).
- **Safe area:** inset every frame by `{spacing.frame-pad}` (5cqw) on all four edges. No load-bearing element crosses that inset.
- **Frame-relative law:** all display sizes, paddings, and gaps in **cqw** (px ÷ 1920 × 100). Fixed px reserved for chrome atoms only: button radius, hairline borders, micro-shadow.
- **cqw, not vw:** the frame is a `container-type: size` element. Sizing in `cqw` resolves against the frame box so a frame can sit at 720px in a contact sheet and still render at true 1920-derived proportions.

## Elevation & Depth

The brand's depth ceiling is **hairline + whisper**. Allowed:
- 1px `{colors.border.standard}` rule (the primary depth signal).
- `shadow: 0 1px 2px 0 rgba(4,9,26,0.04)` — barely visible, present at all (never elevated).
- A single `{components.surface-tint}` block can sit on `{components.surface-canvas}` to read as one elevation step.

Forbidden: stacked shadows, glassmorphism, gradients, neumorphic insets, dark mode, glow. Two elevation steps maximum per frame.

## Shapes

Radius scale, from source §5: pill `{rounded.pill}` for buttons/chips, **`{rounded.card-sm}` (28px) → `{rounded.card-lg}` (40px)** for cards. **No sharp corners** (the source prohibits them) — the smallest radius any rectangular element may have is `{rounded.hair}` (4px), and that is reserved for sparkline ticks and inline index chips. **CTA geometry rule:** every CTA is a pill — full-radius, never a soft-rect.

## Components

Each component is defined as a frontmatter token. Below is intent, when-to-use, and any construction the token set can't carry (borders, surfaces a variant sits on).

- **{components.surface-canvas}** — default white ground. Use unless a frame specifically wants the +1 elevation tint.
- **{components.surface-tint}** — elevated ground for catalog/ledger plates; reads as one step up against canvas.
- **{components.surface-elevated}** — used as a *block within* a tint frame (a featured ledger cell, a soft hero card).
- **{components.surface-ink}** — chrome-scale only: a pill, a stat-numeral token, a button. **Never a full-frame ground.**
- **{components.button-primary}** & **{components.button-primary-giant}** — ink-pill CTA. The giant variant is for cover/claim plates where the button itself is part of the hero composition.
- **{components.button-signal}** — blue-pill CTA. Use when the blue is *the* accent of the frame; do not pair with a sibling blue element on the same frame.
- **{components.button-secondary}** — surface-tint pill with hairline; the quiet second action.
- **{components.card-soft}** — primary content card. Hairline border + whisper shadow + 40px radius is the brand silhouette.
- **{components.card-tint}** — for clustering on a canvas frame without earning a shadow.
- **{components.card-stat}** — compact 28px-radius card for stat readouts and ledger rows.
- **{components.chip-eyebrow}** — top-left/kicker pill; rationed (see Do's and Don'ts — kicker is not a default).
- **{components.chip-status-signal}** — blue-tint pill, the "live/active/now" badge. Counts as the frame's signal firing.
- **{components.rule-hair}** — the brand's primary divider. A horizontal 1px slate-200 line between sections within a frame; never a thicker rule.
- **{components.dot-signal}** — a single 0.7cqw blue dot. The smallest possible voltage; use when a frame wants the signal without a pill.
- **{components.icon-indigo}** / **{components.icon-amber}** — ≤1.8cqw glyphs inside ledger cells/status icons. Micro-only.
- **{components.wordmark-lockup}** — the cover plate's hero element; 22cqw set in display-900.
- **{components.hero-claim}** — the oversized-claim plate's headline.
- **{components.stat-numeral}** — the figure-plate's dominant element.
- **{components.ledger-cell}** — the dense-exception atom: hairline-bordered 28px card carrying one stat-ledger numeral + one micro-label.
- **{components.sparkline}** — a single-stroke blue trendline; never multi-series, never area-filled.

## Motion & Timing

The brand character — *clean, technical, data-driven, trustworthy* — derives a cut grammar of **calm hard cuts** and **patient holds**. Frames feel *placed*, not *animated*.

- **May animate:** a single sparkline drawing in (≤0.6s, ease-out, blue stroke), a stat numeral ticking up to its final figure (≤0.8s), a hairline rule extending across a frame (≤0.5s).
- **Must not animate:** the wordmark, the hero claim, the canvas ground, the kicker chip. They are placed and held.
- **Dwell:** sparse frames hold ≥2.4s; the ledger plate (dense exception) holds ≥3.2s — readers earn the density.
- **Cuts:** hard, frame-aligned. No fades between treatments; the white-on-white continuity carries the eye.
- **Export:** 30 fps; 1920×1080 H.264 master + 1080×1920 and 1080×1080 reflows for stories/square placements.

## Frame Treatments

### 1 · Cover — Wordmark Plate  (identity/cover · move: full-frame wordmark + single dot)
**Ground** `{components.surface-canvas}`, padding `{spacing.frame-pad}`.
**Container** flex column, justify center, align center, gap 2cqw.
**Composes** `{components.wordmark-lockup}`, `{components.dot-signal}`, `{components.chip-eyebrow}`.
**Focal** `{components.wordmark-lockup}`: 22cqw, centered, sits on the optical midline.
**Chrome** one `{components.chip-eyebrow}` 4cqw above the wordmark with the brand sub-mark.
**Accent** one `{components.dot-signal}` at the end of the wordmark (period-as-dot).
**Silence** ~72% empty.
**Fixed** ink color, weight 900, single-dot rule. **Free** wordmark string, eyebrow line.
**Density** sparse.

### 2 · Oversized Claim  (editorial/oversized-claim · move: ink claim fills the frame, one blue pill resolves it)
**Ground** `{components.surface-canvas}`, padding `{spacing.frame-pad}`.
**Container** flex column, justify space-between (claim top-center, CTA bottom-center), align center.
**Composes** `{components.hero-claim}`, `{components.button-signal}`, `{components.rule-hair}`.
**Focal** `{components.hero-claim}` set fit-to-measure (`{typography.display.display-hero}` for ≤3 words → step down per typography rule). Text block ≤78cqw wide, centered.
**Chrome** one `{components.rule-hair}` 1.4cqw beneath the claim, 18cqw wide.
**Accent** one `{components.button-signal}` below the rule.
**Silence** ~68% empty.
**Fixed** centered anchor, single signal pill. **Free** claim string, CTA verb.
**Density** sparse.

### 3 · Focal Artifact — Card on Tint  (focal-artifact · move: one elevated card crops the frame, the brand silhouette announces itself)
**Ground** `{components.surface-tint}`, padding `{spacing.frame-pad}`.
**Container** flex column, justify center, align center.
**Composes** `{components.card-soft}`, `{components.chip-status-signal}`, `{components.sparkline}`, `{components.icon-indigo}`.
**Focal** one `{components.card-soft}` sized **62cqw × 56cqw**, centered, bleeds slightly past safe area on the bottom edge (cropped, not pinned). Inside the card: a `{typography.reading.title-md}` headline, a `{components.sparkline}` 28cqw wide, one `{typography.reading.body}` line of supporting copy.
**Chrome** `{components.chip-status-signal}` top-right inside the card.
**Accent** the sparkline IS the signal firing (counts as the one blue).
**Silence** ~55% empty (the card is the artifact; tint ground breathes around it).
**Fixed** 40px radius, hairline border, whisper shadow. **Free** card title, sparkline shape, status string.
**Density** sparse.

### 4 · Stat Plate  (data/stat · move: a single mega-numeral owns the frame)
**Ground** `{components.surface-canvas}`, padding `{spacing.frame-pad}`.
**Container** grid 12-col, the numeral centered across cols 2–11.
**Composes** `{components.stat-numeral}`, `{components.chip-eyebrow}`, `{components.rule-hair}`, `{components.dot-signal}`.
**Focal** `{components.stat-numeral}` at `{typography.display.stat-mega}` (18cqw), centered.
**Chrome** `{components.chip-eyebrow}` 6cqw above the numeral (the metric label). A `{components.rule-hair}` 22cqw wide sits 2cqw below the numeral.
**Accent** one `{components.dot-signal}` immediately after the numeral (decimal-as-dot).
**Silence** ~70% empty.
**Fixed** centered numeral, single-dot signal. **Free** the numeral (from the script), kicker string.
**Density** sparse.

### 5 · Ledger — Dashboard (the dense exception)  (data/ledger · move: hairline-ruled grid of stat cells, tight by design)
**Ground** `{components.surface-tint}`, padding `{spacing.frame-pad}`.
**Container** grid 3 cols × 2 rows, gap `{spacing.frame-gutter}`; section head row above.
**Composes** `{components.ledger-cell}`, `{components.sparkline}`, `{components.icon-indigo}`, `{components.icon-amber}`, `{components.rule-hair}`, `{components.chip-eyebrow}`.
**Focal** the **grid as a whole** — six `{components.ledger-cell}` cards, each carrying one `{typography.display.stat-ledger}` numeral, one `{typography.reading.label}` metric, and one icon (indigo or amber, micro-only).
**Chrome** `{typography.display.section-head}` headline left-anchored above the grid with `{components.chip-eyebrow}` to its right; `{components.rule-hair}` separates head from grid.
**Accent** one `{components.sparkline}` lives inside a single featured cell (top-left) — the only blue on the frame.
**Silence** ~25% empty. **Tight by design — the density exception.**
**Fixed** 28px ledger-cell radius, hairline borders, 6-cell grid. **Free** cell figures, metric labels, which cell carries the sparkline.
**Density** dense-exception.

### 6 · Closer — Pill + Wordmark  (closer/CTA · move: a single ink pill, the wordmark beneath as cosign)
**Ground** `{components.surface-canvas}`, padding `{spacing.frame-pad}`.
**Container** flex column, justify center, align center, gap 3.2cqw.
**Composes** `{components.button-primary-giant}`, `{components.wordmark-lockup}` (rendered small, at `{typography.reading.title-md}` scale), `{components.dot-signal}`.
**Focal** `{components.button-primary-giant}` centered, sized large (text inside is `{typography.display.pill-giant}`).
**Chrome** wordmark beneath in `{typography.reading.title-md}`, ink, centered.
**Accent** one `{components.dot-signal}` at the end of the wordmark.
**Silence** ~74% empty.
**Fixed** ink pill, centered. **Free** CTA verb, wordmark string.
**Density** sparse.

### 7 · Editorial Catalog — Three Soft Cards  (chrome/catalog · move: three sibling cards in a hairline rhythm)
**Ground** `{components.surface-canvas}`, padding `{spacing.frame-pad}`.
**Container** grid 3 cols, gap `{spacing.frame-gutter}`; section head row above.
**Composes** `{components.card-soft}` ×3, `{components.chip-eyebrow}`, `{components.rule-hair}`, `{components.dot-signal}`.
**Focal** the **trio**: each card carries an index numeral in `{typography.display.section-head}`, a `{typography.reading.title-sm}` title, two lines of `{typography.reading.body-sm}` body.
**Chrome** `{typography.display.section-head}` left-anchored headline + `{components.chip-eyebrow}` right; `{components.rule-hair}` beneath.
**Accent** one `{components.dot-signal}` inside the middle card's index numeral (decides which card is "the one"). The other two cards carry no blue.
**Silence** ~40% empty (cards breathe with generous internal padding).
**Fixed** 40px card radius, hairline border. **Free** titles, body lines, which card carries the dot.
**Density** standard.

## Do's and Don'ts

**Do**
- Lean centered: cover, claim, stat, closer all center their focal element. Left-anchor is for catalog/ledger only.
- Vary the composition axis between consecutive frames; no two centered claim plates back-to-back.
- One idea per frame; ≤2–3 distinct elements (focal + at most a kicker and one support).
- Bleed the focal-artifact card past the safe area on one edge.
- Use full-bleed ground (white-on-white wordmark) as a *cadence* — every 3–4 frames.
- Ration the kicker: ≤40% of frames carry `{components.chip-eyebrow}`.

**Don't**
- No dark grounds. No neon. No invented hex.
- No headline pinned top-left + graphic pinned bottom-right + thin gutter between (the deck tell).
- No two blue elements at full strength on one frame.
- No decoration overlapping the hero claim or kicker rail (≥2cqw keep-out).
- No stacked shadows or gradient grounds.
- No SaaS-feature-grid frame: three icon+headline columns under a kicker is banned.
- No sharp corners; no rectangular CTA — every CTA is a pill.

## Aspect-Ratio Behavior

| Treatment | 16:9 (1920×1080) | 9:16 (1080×1920) | 1:1 (1080×1080) |
|---|---|---|---|
| 1 · Cover | Wordmark 22cqw centered, dot trailing | Wordmark 22cqw on two lines, dot beneath | Wordmark 26cqw, dot trailing |
| 2 · Oversized Claim | Claim centered top-mid, rule + pill bottom-mid | Claim wraps to 3–4 lines, rule shortens to 32cqw, pill below | Claim 9cqw, two-line max, rule 26cqw, pill below |
| 3 · Focal Artifact | Card 62×56cqw, bleeds bottom | Card 78cqw wide, taller (78×88cqw), bleeds bottom; sparkline 60cqw | Card 80×72cqw, bleeds right; sparkline 40cqw |
| 4 · Stat Plate | Numeral 18cqw centered, dot trailing | Numeral 28cqw (one row), kicker above, rule below | Numeral 24cqw centered |
| 5 · Ledger | 3×2 grid | 2×3 grid; head stacks above | 2×2 grid (drop two cells: keep the sparkline cell and three siblings) |
| 6 · Closer | Pill centered, wordmark beneath | Pill 38cqw wide, wordmark beneath at title-md | Pill centered, wordmark beneath |
| 7 · Catalog Trio | 3 cols | 1 col stacked, index numerals reduce to title-md | 2 cols + dropped card (or stack to 1 col) |

Safe-area inset (`{spacing.frame-pad}`) is applied to the short edge in every ratio; no load-bearing line drops below the 1.4cqw legibility floor after re-scale.

## Approved Real Entities & Numerals

Only entities present in `design.md` may appear by name: **SEOSONA**. All other figures (statistics, percentages, dollar amounts, dates) must come from the active script. Treatments use placeholders (`— figure —`, `{metric}`, `{verb}`) — never invent specific numbers or claims. The Cover treatment's wordmark renders as `SEOSONA`; everywhere else, real strings are script-supplied.

## Pre-Render Self-Audit

Before any frame is exported, run every check:
- [ ] **Squint** — one element dominates at 3–6× the next.
- [ ] **Silence** — sparse frame reads 55–75% empty (or it is the named ledger exception, ≥25% empty).
- [ ] **Restraint** — `{colors.signal.primary}` fires exactly once at full strength.
- [ ] **Weight** — display weight is exactly 900 (Poppins); body is exactly 500 (Inter). No 800, no 600 headings.
- [ ] **Depth** — at most one hairline border + one whisper shadow; no second elevation.
- [ ] **Geometry** — every CTA is a pill; every card is 28–40px radius; no sharp corner exists.
- [ ] **Anchor** — focal element is centered (default) or genuinely left-editorial (catalog/ledger); the prior frame's anchor differs.
- [ ] **Element count** — ≤2–3 distinct elements (focal + kicker + one support).
- [ ] **Floor** — no load-bearing line below 1.4cqw.
- [ ] **Ground** — ground is a `{colors.canvas.*}` token; no dark ground anywhere.
- [ ] **Ink** — header text is `{colors.ink.header}`, never `#000`.
- [ ] **Entities** — no invented figure, stat, or claim; placeholders or script-supplied values only.

## Known Gaps

- **cqw stored as string.** The DESIGN.md spec consumer behavior is "accept; store as string" for unit extensions; cqw values in `typography.display.*` and `components.*` are documented authoring values, not parsed to numbers.
- **Aspect-ratio reflows are guidance, not normative.** The 9:16 and 1:1 columns in the Aspect-Ratio table are derived from the primary 16:9 treatment; a script may justify a tighter or looser reflow within the safe-area and floor rules.
- **Motion & Timing is derived.** No motion guidance exists in `design.md`; this section is inferred from the brand's stated character (calm, technical, data-driven) and is overridable by an in-production motion brief.
- **Indigo/amber palette extension.** `design.md §2` names `indigo-500` and `amber-500` as permitted icon accents but does not give hex codes; `#6366F1` and `#F59E0B` are the canonical Tailwind values for those tokens and are pinned here.
