# SEOSONA Unified BrandKit Design

**Status:** approved design direction

## Purpose

Create one canonical SEOSONA BrandKit for social carousels, Content Factory visuals, and Video scenes. It must resolve the current disagreement between the Video design contract and the frame-pack contract, while preserving the visual evidence in the existing SEOSONA carousels.

## Evidence reviewed

- All 15 square assets in `7_ASSETS/brand/SEOSONA/carousel SEOSONA/`.
- All 5 square assets in `7_ASSETS/brand/SEOSONA/carousel Chí Quyết Academy/`.
- The primary logo in `7_ASSETS/brand/logos/Seosona_Logo.png`.
- The complete Be Vietnam Pro family in `7_ASSETS/brand/fonts/`.
- The existing Video `DESIGN.md`, frame-pack `FRAME.md`, mascot pose catalog, and social asset inventory.

All reviewed carousel exports are square. The Academy set is 1065 by 1065. The SEOSONA set is primarily 1080 by 1080 with later high-resolution 1800/2048 exports.

## Source hierarchy

1. **Identity source:** the SEOSONA logo asset. Its dominant opaque colors are `#003CA6` blue and `#00FF00` green.
2. **Social visual source:** the SEOSONA carousel collection. It determines social composition, hierarchy, light/dark cover behavior, footer, pagination, and cards.
3. **Typography source:** local Be Vietnam Pro font files. They are the only canonical production typeface.
4. **Structural reference only:** Chí Quyết Academy carousel collection. Its sequence and comparison patterns may inspire layouts; its logo, coral palette, copy style, and mascot must never enter SEOSONA output.
5. **Legacy documents:** the existing `DESIGN.md` and frame pack must conform to this specification. When they conflict, this specification wins.

## Brand tokens

### Identity

- Name: `SEOSONA`.
- Tagline: `Share to be shared more`.
- Primary logo: `7_ASSETS/brand/logos/Seosona_Logo.png`.
- The logo must remain intact; no generated lookalikes, recoloring, crop, outline, or replacement wordmark.

### Color roles

| Token | Value | Role |
|---|---:|---|
| `identity.blue` | `#003CA6` | Logo and authoritative brand signal. |
| `hero.blue.start` | `#182FB3` | Cobalt cover and CTA field. |
| `hero.blue.end` | `#1F31B7` | Cobalt cover and CTA field depth. |
| `identity.green` | `#00FF00` | Logo/tagline detail only; never a large field. |
| `canvas.white` | `#FFFFFF` | Primary light canvas and card surface. |
| `canvas.mist` | `#F6F8FD` | Light canvas variation, card surround, and number watermark. |
| `ink.primary` | `#111B3F` | Headline and high-emphasis copy on light ground. |
| `ink.secondary` | `#667085` | Supporting copy, metadata, and subdued UI. |
| `line.subtle` | `#E2E8F0` | Hairlines, tables, and card dividers. |
| `status.positive` | `#3A9B5A` | Verified/keep/pass states in data views only. |
| `status.caution` | `#B88416` | Review states in data views only. |
| `status.negative` | `#C84A4A` | Reject/error states in data views only. |

`#E2724D`, broad green panels, cyan neon, purple gradients, and arbitrary new accents are not canonical SEOSONA visual tokens.

### Typography

- Family: `Be Vietnam Pro` for every Vietnamese or Latin string.
- Headlines: 800 or 900; tight line-height; sentence case; maximum four lines on a square social slide.
- Kicker, step label, or taxonomy: 600 or 700; uppercase; expanded tracking.
- Body: 500; shorter than the headline; no paragraph walls.
- Data/table labels: 600; numbers may be 700/800.
- Do not use Poppins, Inter, Druk, Anton, or an AI-generated substitute in production output.

## Visual modes

### Light editorial mode (default)

Use a white/mist canvas with a faint dot grid, light blue ambient geometry, blue headline emphasis, a short blue underline, white cards, subtle hairline rules, and soft elevation. This is the default for explainers, processes, data tables, comparison cards, and educational posts.

### Cobalt hero mode (limited)

The reviewed SEOSONA carousels use a full cobalt-blue field for covers and closing/CTA moments. This is an intentional branded hero, not a general dark-mode theme.

- Allowed only for cover, CTA, or a single decisive emphasis slide.
- Use white headline copy with at most one pale-blue emphasized phrase.
- Retain the subtle dot texture and a small, intact logo.
- Do not use black, neon, cyberpunk, or a generic dark dashboard.
- A carousel should normally contain at most one cobalt hero slide.

## Composition contract for square social posts

- Target artboard: 1080 by 1080. Preserve a 72px quiet edge around essential content.
- Logo: small, top-left, with adequate whitespace; never dominant over the topic.
- Metadata/pagination: rounded pill or compact marker at top-right or bottom-right.
- Headline: upper half; large, left-aligned, with blue as the principal emphasis.
- Supporting proof: cards, rows, or a single diagram in the lower half.
- Footer: `SEOSONA · Share to be shared more` on light slides; use the approved inverse treatment on cobalt hero slides.
- Use an oversized translucent step number only when the slide belongs to a sequence.

## Approved component families

- `cover_dark`: cobalt hero, one claim, brief support line, one CTA.
- `explain_light`: kicker, large title, underline, three proof cards.
- `numbered_principle`: oversized two-digit index, one principle, evidence or source card, optional cobalt takeaway strip.
- `process_steps`: 3–7 ordered steps with compact numbered markers.
- `data_table`: honest before/after or categorized data; status colors only describe real state.
- `comparison_split`: light-versus-cobalt or two light cards, separated by a single `VS` token.
- `proof_cards`: one to three concise cards with a stated source or evidence reference.
- `mascot_callout`: approved pose used once as an explanatory accent or CTA anchor.

## Mascot rules

- Use only named files in `7_ASSETS/brand/SEOSONA/mascot_poses/named/catalog.json`.
- The mascot is optional; it must not replace the primary logo, make unverified claims, or be placed on every slide.
- Choose a pose semantically: `thinking` for diagnosis, `talk_explain` for a framework, `thumbs_up` for verified completion, and `celebrate` for a real milestone.

## Content Factory and Flow boundary

- Flow generates text-free scene imagery, editorial atmosphere, or a clearly bounded visual subject.
- Do not ask Flow to render Vietnamese copy, logo text, statistics, citations, or UI labels. These must be placed by a deterministic compositor using the BrandKit tokens.
- A `VisualJob` receives the visual subject plus `brandKitRef`, `mode`, `allowedAssets`, and negative rules. It must not receive opaque copied brand content.
- Content packages retain claim evidence and copy provenance. The image receipt retains the BrandKit version, asset references, prompt revision, and quality verdict.

## Machine-readable BrandKit

The implementation will add these files under `7_ASSETS/brand/SEOSONA/`:

- `brand-kit.v1.json`: canonical identity, palette, typography, layout, visual modes, components, mascot catalog, and negative rules.
- `asset-manifest.v1.json`: relative asset references, dimensions, SHA-256 digests, and usage classification.
- Updated `DESIGN.md`: concise human-facing contract aligned with the JSON token source.

SEOSONA OS will reference the BrandKit by relative version and digest. SEOSONA Content will include its visual rule subset in `VisualJob`; it will not copy the asset collection into its repository.

## Validation and release criteria

- Every manifest asset exists under the Video brand root and its hash matches.
- Every typography reference resolves to a local Be Vietnam Pro file.
- No Academy asset appears in the SEOSONA allowlist.
- Every social template passes color-token and layout-rule validation.
- Text-bearing social exports are rendered by the deterministic compositor, not Flow.
- Content Factory unit tests prove that the generated visual prompt includes the BrandKit version and negative rules.
- A visual QA sample contains one slide from each approved component family before the kit is promoted from `v1` to a later revision.
