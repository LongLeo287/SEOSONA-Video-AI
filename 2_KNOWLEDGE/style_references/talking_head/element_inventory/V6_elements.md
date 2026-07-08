# V6 — Visual Element Inventory

**Video:** V6 "Test hiệu quả AI agent" — *"Mình test xem hiệu quả đến đâu rồi share cho ae thử"*
**Runtime:** ~105s · 40 scenes (contact-sheet interval)
**Source sheet:** `8_WORKSPACE/talking_head_study/elements/sheets/06_Mình_test_xem_hiệu_quả_đến_đâu_rồi_share_cho_ae_thử.jpg`
**Frames referenced:** `8_WORKSPACE/talking_head_study/elements/_tmp/f_0000.jpg … f_0039.jpg`

**Scope:** every small visual element layered over the footage — icons, cards/panels, text-effects, screen-recordings, decoratives. The overall 3-zone layout (top card zone / middle rounded-video zone / bottom caption) is documented elsewhere and is NOT re-catalogued here.

**Palette observed (source, neon-on-dark):** deep purple→indigo gradient background; card borders switch semantic colour per topic — **violet/blue** (structure/generic), **cyan/teal** (departments/people), **amber/gold** (dev-team & big-number stats), **green/lime** (cost, goals, process/agent flow). Captions = white text with brand-yellow keyword highlight on a translucent black pill.

---

## 1. CARD / PANEL (the dominant element family)

This reel's identity is a family of **glassy dark rounded-rectangle cards** floating in the top zone, all sharing: semi-transparent dark fill (glass), a thin coloured 1–2px border with soft outer glow, **L-shaped corner-bracket accents** at all four corners, a soft diagonal sheen/highlight sweep across the top-left, and rounded ~16–20px corners. They differ by (a) border colour = semantic role and (b) internal layout. They **persist** for the duration of a talking point (several seconds), sitting above the rounded video.

### 1a. Multi-bullet "topic list" card — *the signature card*
- **name/desc:** header row (icon + ALL-CAPS colored title) + 3–5 bullet rows, each row = small line-icon in a rounded chip + label text. Rows reveal progressively; the active row gets a brighter rounded outline, un-revealed rows are dimmed/greyed.
- **category:** card/panel
- **visual style:** glass dark fill, semantic coloured border + soft glow, corner brackets, diagonal sheen; header title in border colour, body text white; per-row icon chips.
- **concept:** an org/structure breakdown (leadership, departments, dev team, cost model)
- **position zone:** top zone (above video)
- **entrance:** card fades/scales in; bullets reveal one-by-one (staggered), active row highlight slides down the list
- **timing/sync + frequency:** persists per section; **accumulates** — reused across ~5 distinct topics; ~5+ instances
- **asset type:** CSS-drawn glass panel (border-image/box-shadow glow) + SVG corner brackets + SVG line-icons per bullet
- **SEOSONA remap:** glass→light frosted white/very-light-grey card with soft grey shadow; border colour keeps semantic ROLE but light-brand hues (blue #2A5BDA structure, coral #E2724D people/dept, amber goals/dev, green cost); neon glow→soft 8–16px shadow; active-row highlight = light blue tint fill instead of neon outline
- **observed instances (colour = role):**
  - `f_0005` **"BAN LÃNH ĐẠO AI"** — VIOLET/blue border · shield header icon · 3 bullets (star, person, sun/asterisk)
  - `f_0007`/`f_0009` **"CÁC PHÒNG BAN"** — CYAN/teal border · people header icon · **5 bullets** (sun, pencil, chart-arrow-down, tag, chat-bubble) · shows dim/active reveal states
  - `f_0011`/`f_0013` **"ĐỘI NGŨ DEV"** — AMBER/gold border · `</>` code header icon · 3 bullets (lightning, `</>` code, checkmark)
  - `f_0032` **"CHI PHÍ VẬN HÀNH"** — GREEN border · coin/dollar-circle header icon · 3 bullets (coin, lightning, shield)

### 1b. Big-number / stat card
- **name/desc:** large centred numeral ("24/7") with a subtitle strip below (`TỰ CHẠY · ĐỘC LẬP · KHÔNG CAN THIỆP`)
- **category:** card/panel (text-effect emphasis)
- **visual style:** amber/gold glass card, corner brackets, huge condensed white/gold number, small caps subtitle bar with dot-separators
- **concept:** headline stat / always-on claim
- **position zone:** top zone
- **entrance:** scale-pop in
- **timing:** persists for the beat; **once** (~1)
- **asset type:** CSS-drawn card + big webfont numeral + SVG corner brackets
- **SEOSONA remap:** light card, amber accent number, dark-navy text; brackets in amber; drop neon → soft shadow
- **instance:** `f_0030` "24/7"

### 1c. Single-line banner / title card (with subtitle row)
- **name/desc:** one-line ALL-CAPS title preceded by a small **dot bullet**, plus a smaller caps subtitle row (often `VD: …` example or dot-separated tags)
- **category:** card/panel
- **visual style:** wide short glass pill, semantic border + glow, corner brackets, diagonal sheen
- **concept:** section label / example callout / teaser
- **position zone:** top zone
- **entrance:** slide/fade in from top
- **timing:** persists per beat; **accumulates** — reused ~5+ times
- **asset type:** CSS-drawn pill + SVG corner brackets + dot bullet glyph
- **SEOSONA remap:** light frosted pill, coloured left-dot + title in role colour, muted-grey subtitle; soft shadow
- **observed instances:**
  - `f_0001`/`f_0002` **"VẬN HÀNH BẰNG AI AGENT"** — AMBER · subtitle `MỘT MÌNH · TỰ ĐỘNG · 24/7`
  - `f_0016` **"GIAO MỤC TIÊU CHO CEO"** — GREEN · subtitle `VD: THÁNG NÀY RA APP / PHẦN MỀM`
  - `f_0037`/`f_0038` **"SẼ CẬP NHẬT HÀNH TRÌNH"** (teaser) — VIOLET/blue · subtitle `TIẾN ĐỘ · KHẢ NĂNG · CHI PHÍ`
  - intro **"CÔNG TY MỘT MÌNH TẠO"** cards (sheet rows 1) and end **"VIDEO SAU KẾT QUẢ Ở CHI PHÍ"** + **"ƯU TIÊN MIỄN PHÍ"** + **"API TRẢ PHÍ = KHÓ DUY TRÌ"** banners (sheet bottom rows) — same template, violet/amber variants

### 1d. Numbered checklist / process card WITH progress bar
- **name/desc:** header line ("CEO AGENT tự điều phối…") + 4 numbered rows; each row = green rounded **number badge (1–4)** + label + green **checkmark badge** on completed rows; active row highlighted; a **green gradient progress bar** runs full-width beneath
- **category:** card/panel (+ progress decorative)
- **visual style:** dark rows with green accents; filled green number chips; green tick chips; green→lime gradient progress fill on a dark track
- **concept:** the agent's step-by-step workflow executing (analyse→ticket→assign→execute)
- **position zone:** top zone
- **entrance:** rows check off sequentially; progress bar fills L→R in sync with row completion
- **timing:** **accumulates** step-by-step within the beat; ~1 sequence
- **asset type:** CSS-drawn rows + SVG number badges + SVG checkmark + CSS gradient progress bar
- **SEOSONA remap:** light rows, green (#2E9E6B-ish) badges/ticks kept for "done" semantics, blue for active; progress bar = green gradient on light-grey track; soft shadow not glow
- **instance:** `f_0020`

---

## 2. ICON (SVG line-icons — heavily repeated inside cards)

All icons are **thin monoline SVG glyphs**, rendered inside small rounded chips, tinted to the card's semantic colour. They appear as (a) **card header icons** and (b) **per-bullet row icons**. This is the most-repeated element class in the reel.

**Header icons observed (1 per card):**
- shield / verified — `f_0005` (leadership)
- people / group — `f_0009` (departments)
- `</>` code-brackets — `f_0011`/`f_0013` (dev team)
- coin / dollar-in-circle — `f_0032` (cost)
- dot/bullet marker — banner cards `f_0016`/`f_0037`

**Per-bullet row icons observed (repeat pool, reused across cards):**
- ⭐ star (outline) · person/avatar · sun/asterisk — leadership card
- sun · pencil (edit) · chart-arrow-down · price-tag · speech-bubble — departments card (5)
- lightning-bolt · `</>` code · checkmark — dev card
- coin · lightning-bolt · shield — cost card

- **category:** icon (SVG line-icon; a few could be filled-icon chips)
- **visual style:** monoline, ~1.5px stroke, tinted to border colour, inside ~24px rounded chip with faint fill
- **concept:** labels each list item semantically (role, function, cost driver)
- **position zone:** top zone, inside cards
- **entrance:** appears with its bullet row (staggered reveal)
- **timing/sync + frequency:** **accumulates**; very high count — roughly **18–20 bullet-icon instances** + ~6 header icons across all cards; several glyphs (lightning, shield, code, checkmark) repeat 2–3×
- **asset type:** SVG line-icon set (single consistent icon family — Lucide/Feather-style)
- **SEOSONA remap:** same monoline family, recoloured to light-brand role colours; drop glow, keep as flat tinted glyphs on light chips; standardise to ONE brand icon set for the factory library

---

## 3. IMAGE / SCREENSHOT (screen-recording inserts)

- **name/desc:** real **screen-recording of an app dashboard** — an isometric, game-like "AI office/agents" simulation UI (agents moving in a stylised floorplan, side panels, counters like "4 AGENTS"). Also plainer browser/dashboard captures appear in the middle zone in several scenes (task boards, analytics).
- **category:** image (real screenshot / screen-capture footage)
- **visual style:** actual captured pixels, letterboxed into the rounded panel; dark app UI matches the reel's dark theme by luck/design
- **concept:** proof/demo — "here's the agent system actually running"
- **position zone:** middle zone (stacked ABOVE the talking-head video in a split, e.g. `f_0001`/`f_0002`), or filling the top/middle zone in dashboard scenes
- **entrance:** hard cut / slide-in; plays as video insert
- **timing/sync + frequency:** appears during demo beats; **accumulates** — multiple inserts (~6–10 scenes across the middle rows of the sheet)
- **asset type:** real screen-recording / screenshot (cannot be synthesised — must be captured footage)
- **SEOSONA remap:** keep as literal product screen-capture; frame it in the light rounded-panel bezel with soft shadow; if UI is dark, add a subtle light inner border so it reads on light brand background

---

## 4. TEXT-EFFECT

- **name/desc — keyword highlight (caption):** bottom-caption running text is white; **key words are recoloured brand-yellow/amber** (e.g. `mình`, `CEO`, `agent`, `creator`, `API`, `thô`i, `những`) — occasionally green (`CEO` in `f_0005`).
  - **category:** text-effect · **style:** white body + yellow/green highlight word, on a translucent black rounded pill · **concept:** emphasise the operative keyword per line · **zone:** bottom caption band · **entrance:** word-by-word / pop with speech · **frequency:** persists whole video, ~1 highlight per line = **very high count (30+)** · **asset:** styled caption (ASS/SRT karaoke or CSS span) · **remap:** highlight = brand blue or coral instead of neon-yellow; pill = translucent dark or light-grey; keep light overall.
- **name/desc — bullet reveal / dim + active highlight:** inside list cards, un-revealed bullets are greyed, the current bullet gets a brighter rounded outline box (`f_0007`).
  - **category:** text-effect (state) · **style:** dim 40% vs active rounded-outline · **concept:** guide eye to the point being spoken · **zone:** top card · **entrance:** staggered reveal · **frequency:** every multi-bullet card (~5) · **asset:** CSS opacity + outline state · **remap:** active = light-blue tint fill; dim = 45% grey; drop neon outline.
- **name/desc — big condensed numeral:** "24/7" oversized stat type (`f_0030`).
  - **category:** text-effect · **asset:** heavy condensed webfont · **remap:** amber numeral on light card.
- **name/desc — caps title + dot-separator subtitle:** ALL-CAPS titles and `·`-separated tag subtitles on banner cards.
  - **category:** text-effect · **asset:** webfont + `·` glyphs · **remap:** brand type scale, role-coloured title, muted subtitle.

---

## 5. DECORATIVE

- **name/desc — corner-bracket accents (⌐ ¬ L L):** thin L-shaped brackets at all 4 corners of every card.
  - **category:** decorative · **style:** ~1.5px stroke, semantic colour, small glow · **concept:** "HUD/tech frame" feel · **zone:** top-zone card corners · **entrance:** with card · **frequency:** **persists**; 4 per card × ~12 cards = **~48 instances** · **asset:** SVG / CSS-drawn corner brackets · **remap:** keep bracket motif but thinner, role-coloured, no glow — signature of the light brand HUD.
- **name/desc — diagonal glass sheen:** soft light streak sweeping the top-left of each glass card.
  - **category:** decorative · **style:** low-opacity white gradient highlight · **concept:** glass/premium sheen · **zone:** card surface · **frequency:** persists per card (~12) · **asset:** CSS gradient overlay · **remap:** very subtle light sheen or omit (light card already bright).
- **name/desc — dot bullet marker:** small filled dot before banner-card titles.
  - **category:** decorative/icon · **frequency:** ~5 (one per banner) · **asset:** CSS dot / glyph · **remap:** role-coloured dot.
- **name/desc — background purple gradient + soft vignette / glow blooms:** the deep purple→indigo backdrop with coloured light blooms around cards.
  - **category:** decorative (background) · **concept:** mood/neon atmosphere · **zone:** full-frame behind everything · **frequency:** persists entire video · **asset:** gradient + radial glow (CSS/render) · **remap:** **replace with light brand background** (off-white / very-light-blue wash); this is the biggest brand shift — the reel's dark neon mood becomes SEOSONA light.
- **name/desc — rounded video bezel + soft shadow:** the talking-head video sits in a rounded-corner panel with a soft outer glow.
  - **category:** decorative (frame) · **frequency:** persists · **asset:** CSS rounded mask + shadow · **remap:** keep rounded panel, glow→soft neutral shadow.
- **name/desc — split-screen divider:** thin gap/line between stacked screen-rec and talking-head (`f_0001`).
  - **category:** decorative · **frequency:** during split inserts (~few) · **asset:** CSS gap/border · **remap:** thin light divider.

---

## 6. NOT PRESENT (explicit negatives for the library)

- **emoji glyphs:** none as overlay stickers (highlight words are text, not emoji). — *emoji category = empty*
- **sticker/graphic (playful cutouts, arrows, doodles):** none.
- **cursor/pointer overlays:** none (no animated cursor/hand-pointer graphic; the "pointing" is the presenter's real hand in footage).
- **photo-cutouts / device bezel PNGs:** none (screen content is raw screen-rec, not mocked in a phone frame).

---

## Signature elements (the 3–5 that define V6's look)

1. **Semantic-coloured glass HUD cards with corner brackets** — the violet/cyan/amber/green border switching by topic is THE identity; corner brackets + diagonal sheen make every card read as one system.
2. **Per-bullet monoline icon chips (one consistent SVG icon family)** — every list row carries a tinted line-icon; the single biggest repeated element class (~24 instances).
3. **Progressive bullet reveal with dim/active highlight** — un-revealed rows greyed, active row outlined, synced to speech.
4. **Numbered checklist card + green progress bar** — the "agent workflow executing" card (`f_0020`) is the reel's proof-of-process hero.
5. **Screen-recording insert of the isometric AI-agents dashboard** — the live-demo footage that grounds the whole "test hiệu quả" premise.

**Reproduction stack for the factory library:** CSS-drawn glass/light panel + SVG corner-bracket set + ONE monoline SVG icon family (star, person, sun, pencil, chart-arrow, tag, chat, lightning, code `</>`, checkmark, coin, shield) + CSS gradient progress bar + numbered/checkmark badges + styled karaoke caption with brand-highlight + real screen-capture inserts. Remap all neon glow → soft shadow, dark purple bg → light brand wash, keep semantic border ROLES mapped to blue/coral/green/amber.
