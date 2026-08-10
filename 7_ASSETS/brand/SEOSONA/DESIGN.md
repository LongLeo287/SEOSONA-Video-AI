# SEOSONA Unified Design Contract

**Version:** 1.0.0

**Canonical machine source:** [`brand-kit.v1.json`](brand-kit.v1.json)

**Asset provenance:** [`asset-manifest.v1.json`](asset-manifest.v1.json)

This document is the human-facing guide for SEOSONA social posts, carousels,
and compatible Video scenes. The JSON BrandKit is authoritative whenever a
generator, validator, or older design note disagrees with this guide.

## Identity

- Brand name: **SEOSONA**.
- Tagline: **Share to be shared more**.
- Use the intact primary logo identified by `identity.logoAsset`.
- Never redraw, crop, recolor, outline, or generate a replacement logo or
  wordmark.

## Color roles

| Role | Token | Value |
|---|---|---:|
| Identity blue | `identityBlue` | `#003CA6` |
| Cobalt hero start | `heroBlueStart` | `#182FB3` |
| Cobalt hero end | `heroBlueEnd` | `#1F31B7` |
| Logo green | `identityGreen` | `#00FF00` |
| Main canvas | `canvasWhite` | `#FFFFFF` |
| Alternate canvas | `canvasMist` | `#F6F8FD` |
| Primary ink | `inkPrimary` | `#111B3F` |
| Secondary ink | `inkSecondary` | `#667085` |
| Subtle line | `lineSubtle` | `#E2E8F0` |

Status colors in `brand-kit.v1.json` describe verified data state only. Coral,
arbitrary accent rotation, broad green panels, neon cyan, purple gradients,
and generic cyberpunk palettes are not SEOSONA identity colors.

## Typography

Use **Be Vietnam Pro** for every Vietnamese and Latin string. Production font
files and allowed weights are identified in the asset manifest.

- Headlines: weight 800 or 900, sentence case, tight line height, no more than
  four lines on a square slide.
- Kicker or taxonomy label: weight 600 or 700, uppercase, expanded tracking.
- Body: weight 500 and concise.
- Data labels: weight 600; verified numbers may use 700 or 800.

Do not substitute Poppins, Inter, Druk, Anton, or AI-generated lettering.

## Visual modes

### Light editorial

This is the default mode for explanations, processes, data, comparisons, and
educational content. Use white or mist canvas, subtle blue ambient geometry,
white cards, hairline dividers, controlled elevation, and restrained dot-grid
texture.

### Cobalt hero

Cobalt is allowed only for a cover, CTA, or one decisive emphasis slide. Use
white headline text, at most one pale-blue emphasized phrase, a subtle dot
texture, and a small intact logo. A carousel normally contains no more than one
cobalt hero slide.

This is a branded hero treatment, not permission for black dashboards, neon,
or generic dark mode.

## Square social composition

- Canvas: 1080 by 1080 with a 72px quiet edge.
- Logo: small, top-left, with clear whitespace.
- Metadata or pagination: compact marker at top-right or bottom-right.
- Headline: left-aligned in the upper half.
- Proof: cards, rows, or one diagram in the lower half.
- Footer: `SEOSONA · Share to be shared more`.
- Oversized translucent numbers are reserved for real sequences.

## Approved components

- `cover_dark`
- `explain_light`
- `numbered_principle`
- `process_steps`
- `data_table`
- `comparison_split`
- `proof_cards`
- `mascot_callout`

Detailed component contracts are stored in `componentRules` inside the
canonical JSON. Do not invent a new visual family silently; version the
BrandKit when a new family is approved.

## Mascot

Use only named pose assets allowlisted by the BrandKit. The mascot is optional
and may appear once as an explanatory accent or CTA anchor. It never replaces
the primary logo and never implies an unverified claim.

Choose poses semantically: thinking for diagnosis, talk-explain for a
framework, thumbs-up for verified completion, and celebrate for a real
milestone.

## Reference boundaries

- `carousel SEOSONA` is the canonical social visual reference for hierarchy,
  pacing, covers, CTA slides, cards, footer, and pagination.
- `carousel Chí Quyết Academy` is **reference-only** for sequence and comparison
  structure. Its logo, coral palette, mascot, and copy style are excluded from
  SEOSONA production output.
- Legacy Video and frame-pack notes must conform to this BrandKit when their
  colors, fonts, or light/dark rules conflict.

## Content Factory and Flow boundary

Flow is a pixel worker for text-free scene imagery, editorial atmosphere, or a
bounded visual subject. Flow must not render Vietnamese text, logo assets or
wordmarks, statistics, citations, or UI labels. A deterministic compositor
owns those elements and applies the exact BrandKit tokens after image
generation.

Every visual job must carry the BrandKit version and digest, one approved mode,
one approved component, an explicit asset allowlist, and the complete negative
rules. Receipts must retain that provenance so an exported post can be traced
back to the exact design contract.

## Release gate

Run `npm run brand:manifest` after approved assets change, then run
`npm run brand:validate`. Promotion requires matching hashes and dimensions,
resolvable Be Vietnam Pro files, zero Academy assets in the production
allowlist, and a visual QA sample for each approved component family.
