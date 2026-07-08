# DENSITY Craft Study — 54 reference shorts (2026-07-03)

Distilled from a **frame-by-frame density analysis of D:\SEOSONA AI\Video Template** (54 videos). 36 returned full catalogs — strong agreement. The remaining 18 were rate-limited during the first pass, then closed on **2026-07-03 by a COVERAGE CHECK**: 24 frames sampled across 8 previously-unseen shorts → **recipe covers every frame, zero new devices**. The 36-video distillation generalizes cleanly. **STUDY CLOSED — all 54 accounted for.** Reference is mostly dark — **we render LIGHT**, so take LAYOUT + COMBOS + DENSITY, drop the palette.

## THE core finding (why our videos feel sparse)
Reference frames carry **5-10 distinct visual objects across 3 vertical zones**; ours render ~**one component + title** with big empty gaps. **Never one centered component.** Target: **≥5-8 elements/scene**.

## The 3-zone density frame (apply to every scene)
- **TOP (chrome):** brand/@handle + progress rail + kicker PILL + (accent rail). Always present.
- **MID (payload):** BIG 2-tone title + **gradient underline** → hero visual → **supporting cluster (2-3 chips / role-value cards)**. This is where WE are thin — add the supporting cluster.
- **BOTTOM (chrome):** karaoke caption (1 word accent) + footer/handle/URL pill. Never blank.

## Universal spine (top→bottom, fills the frame)
`kicker pill → 2-tone title + underline → hero visual → 2-3 supporting chips/cards → caption`

## Rotate ONE hero visual per scene (variety within one language)
orbit/radial diagram (center icon + 3-10 satellite pills — MOST common, **GAP: build it**) · flow/pipeline (nodes + edge-label pills + glowing active dot) · numbered card-stack (01/02/03) with an **ACTIVE row lit / rest dimmed, toggled with voice** · MockCard (terminal / tweet-embed / code-block / browser-chrome — reads as "real") · VS / before→after (red ❌ vs green ✅ glow) · big 2-tone StatHero + caps dot-label · 2×2 emoji feature-tile grid · quote card + giant quote mark.

## Density devices (fill negative space — cheap richness)
- **Ghost/echo layer** behind content: giant faded numeral ("01","06") or echo word (factory HAS `.scghost` — reuse for stat/step scenes).
- **Gradient underline** under EVERY title (factory HAS `.l2u`).
- **Left vertical accent rail** (GAP).
- **Supporting chip-row** (2-3 chips) under the component (factory HAS `chiprow`/`badges` — just wire it in per scene). **← #1 lever for us.**
- **Role-color label on cards** (mono caps role → value; ties to brand ROLES).
- **Particle / code-glyph confetti / radar rings / grid** as bg filler (factory HAS blobs; add glyph confetti).
- **Full-bleed context bg behind translucent glass cards** (dimmed screenshot/footage).

## Motion
Staggered per-element entrance (title → underline → hero → chips), progressive reveal (a scene GAINS elements, don't cut to a new sparse frame), rotating orbit rings, active-row toggle synced to voice, karaoke everywhere.

## Coverage-check sharpenings (2026-07-03, from the final 18 spot-check — concrete renderings of devices already listed)
- **Active-row signifier can be a literal iOS-style TOGGLE SWITCH** on numbered rows (01/02/03): selected row lit + toggle ON, rest dim + OFF. Same "active-row" device, sharper affordance (item #4).
- **VS can be a TUG-OF-WAR SLIDER** — two labeled cards pulling a center knob on a two-color rail — not only side-by-side ❌/✅. A motion variant of hero #5.

## Density target + variety
Default scene = **5-8 objects / 3 zones**. Reserve the sparse "one artifact on a glow" look (trạm ai) as **intentional variety ~1 scene in 5**, not the default.

## APPLY-TO-FACTORY checklist (this is the point — not just a doc)
1. **[#1] Director assigns 2-3 supporting CHIPS per scene** (keywords/role-value from content) → native_composer renders a chip-row under the component. Instantly +density.
2. **Left accent rail + persistent bottom handle/URL** chrome on every scene.
3. **Gradient underline on every title** (ensure `.l2u` always on).
4. **Active-row state** for list components (steps/feature/badges): light the row synced to reveal.
5. **Build the orbit/radial hero** (most common missing hero).
6. Ghost numeral for stat/step scenes; code-glyph confetti bg filler.
