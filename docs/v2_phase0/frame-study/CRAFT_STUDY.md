# CRAFT_STUDY — Master frame-by-frame craft spec (62 reference videos)

**Synthesis of** `GROUP1.md` (idx 1–14), `GROUP2.md` (idx 15–28), `GROUP3.md` (idx 29–42), `GROUP4.md` (idx 43–56 + Course C1–C6).
**Corpus:** 62 Vietnamese faceless AI/tech motion-graphics shorts, `D:\SEOSONA AI\data\Video Template` (57) + `Video Course` (5). Almost all 9:16 @30fps, 1080×1920 (a few 720×1280 / 24fps / one 16:9).
**Purpose:** one de-duplicated craft spec our engine can be built from — **glow-on-LIGHT, self-drawn (HTML/CSS/SVG), brand-locked navy `#003BA6` + green `#00AA00`, Be Vietnam Pro.**
**Provenance discipline:** load-bearing claims cite `group · file · timestamp`. Carry each group's confidence limits: montages were sampled at **1fps / 1-per-2s**, so beat maps are ±1–2s and easing/cadence are **inferred, not curve-fit**; a handful of moments were re-sampled at **10–30fps** and those timings are frame-accurate (flagged "measured"). **No audio was analyzed** — "karaoke/VO-synced" is inferred from the caption's moving highlight. Colour hexes are eyeballed (±10). All 4 groups state these limits independently.

> **The single most important reframing:** these are not 62 hand-crafts. They are outputs of **~6–8 "URL→video" template engines** (YupVid, escbase.xyz, sockseo, @aidailyone, trạm ai, Lạch Cạch AI, KNG/Eric Trần AI). Several outros literally advertise "Biến một URL thành video" (G1·v14·91s; G3·v31/v42 outro; G4·T46 CTA) — i.e. **the exact product we are building**. So we extract the *template grammar*, not surface skin. And the corpus default is DARK; only a few are light (G2·v16, G2·v28, G3·v41, G4·T53, G4·T54) — **our light-brand mandate makes us the deliberate outlier**, and those few light files are our north stars.

---

## 1. THE STRUCTURAL LAWS

Rules true across nearly all 62. Confidence = how many groups independently confirmed it + how many videos.

### LAW 1 — Near-ZERO hard cuts. One continuous timeline; ELEMENTS animate enter/hold/exit on the caption beat. **[confidence: VERY HIGH — all 4 groups, scdet-confirmed]**
`scdet` (thr 0.3) found **0 hard cuts in the large majority**: G1 "0 cuts in 10 of 14"; G2 "≈0, only v19 & v27"; G3 "8 of 14 have zero"; G4 "almost all 0–3, most 0". The perceived pace is *fast* not from cutting but from **captions re-highlighting every ~0.4s over one continuously-building focal graphic**. **Rebuild consequence:** the engine must think in **element-level ENTER / HOLD / EXIT keyframes synced to caption beats**, never in scene cuts (G4 explicit; G2·"central finding"; G3·"element-level progressive reveal over long holds").

### LAW 2 — The universal scene skeleton: `kicker/eyebrow → 2-line headline (accent on line 2) → ONE continuously-animating focal graphic → running bottom caption`. **[VERY HIGH — all 4 groups]**
Four stacked bands (G1·A1 clean in v2/v4/v5/v7/v8/v14; G2·"universal spine"; G3·"eyebrow→title→underline"; G4·"persistent chapter-heading zone + eyebrow micro-label"):
- **Kicker/eyebrow** — tiny UPPERCASE letter-spaced label, often a leading dot or step-icon (`· ZERO DEPS`, `REVEAL`, `WALKTHROUGH`, `FEATURES`). G1·v4·24s; G3·v41·33s pill; G4·T49.
- **Headline** — usually **two lines, line 2 in the section accent colour**. G1·v2·0-8s "Giao việc khó."(white)/"Rồi đi ngủ."(green); G1·v14·91s "Biến một URL"/"thành video."(green); G4·T49 "Không cần"/"**card đồ hoạ**".
- **ONE focal graphic** — exactly one hero object per beat, always mid-build while on screen (§3 vocabulary).
- **Bottom caption** — persistent, phrase-swap or karaoke (LAW 4).

Model a scene as `{kicker?, headline{line1, accentLine2}, focal{type,data}, caption}` — this one struct covers ~80% of the corpus.

### LAW 3 — Single-accent discipline; colour carries MEANING and switches per chapter, not per video. **[VERY HIGH — all 4 groups]**
Each video commits to ONE dominant accent driving title-keyword, chips, active-states, gauges, karaoke (G3·"single accent discipline"; G4·"one accent, hard discipline"). But the accent is **semantic and can switch per chapter**: **red = error/problem/danger, green = good/success/featured-topic, gold/amber = highlight/active-word/caution, brand accent = neutral structure** (G1·A2). Cleanest proof: G1·v8 whole "Skills" topic is green, but the "Sai Lầm Phổ Biến" (mistakes) chapter switches to **RED** (74–92s); G1·v1 is four colour chapters (cyan/red/gold/green). **For us:** navy `#003BA6` = structural ink; green `#00AA00` = the single "active / positive / highlight" accent; gray = inactive; **one reserved warm tint (amber/red) for genuine alarm only** (G3·v34 semantic outline colour; G4·T47 amber caveat chip against green).

### LAW 4 — A persistent bottom caption is ALWAYS present, in one of two modes; it is the engagement spine. **[VERY HIGH — all 4 groups, 14/14 in G2]**
- **Karaoke recolor** (most common): full phrase shows, **one word recolors to the accent** and steps left→right as spoken, **~0.15–0.25s/word, colour-only, NO scale/bounce** (measured G1·v13·3s; G2·v28·0-3.9s; G4·T54·44-46.5s). Often a **two-tier** caption: dim full-sentence context line under the bright active phrase (G1·v13). Variants: boxed-keyword (thin accent rounded outline, G2·v17/v19); one-word-at-a-time kinetic centre-screen (G3·v40).
- **Phrase-swap / phrase-append**: whole phrase holds then swaps, **~0.7–1.3s/phrase tracking the voice, ~1-frame gap** (measured G1·v4·0s ~0.9s calm, ~0.6s dense). The Course/doodle set uses **all-caps phrase-append** with red emphasis words (G4·C1–C6).

### LAW 5 — Transitions = ~0.3–1.0s colored glow-bloom + crossfade, NOT cuts. **[HIGH — G1 measured, G2 confirmed]**
Between chapters, a **full-screen radial glow flood in the section accent** ramps up over ~5–6 frames, peaks, decays ~10 frames under a content cross-fade — **total ~0.7–1.0s** (measured G1·v1·99.3s). Within a scene, elements just cross-fade (~0.3–0.4s, G2). sockseo's richer variant: **glow-bloom + particle-sparkle + focus-resolve** — element enters blurred+low-opacity+glow → sharpens over ~0.35–0.5s with a brief sparkle burst at resolve (measured G2·v24·18.1-18.5s & 20.8-21.3s). Bridge device seen once: a scrolling ghost-text marquee band spanning old→new (G2·v15·15.7s). **For light bg:** the bloom becomes a soft navy/green tint wash on white, not a black-to-neon flash.

### LAW 6 — Backgrounds are a slowly-moving MOOD, never a flat fill. **[HIGH — G2 explicit "12/14", all groups note it]**
Radial glow/orb that breathes (G2·v18 blue orb, v15, v20), bokeh (G2·v16), starfield (G2·v21, G4·T46), spotlight cone (G2·v17), dotted-grid canvas (G3·v33), graph-paper (G3·v41), narrative colour-zones that shift hue per chapter (G3·v30; G4·T51 blue→green→purple; G4·T56 shifting gradient). Plus **ghost/texture layers**: giant low-opacity background word (G1·v6 "BEAUTIFUL"/"VIBE CODE"; G1·v11 "MANY"), faint tech-logo cloud (G3·v29), ghost section numerals 01–07 (G2·v16/v17/v21), giant ghost countdown numerals behind a step list (G2·v15·43-49s). **For light:** faint navy dot-grid or graph-paper + soft drifting green/navy radial bloom, never a static white fill.

### LAW 7 — Composition: content in the middle ~60%, big platform-safe margins, contained cards not full-bleed. **[HIGH — G1·A7]**
Content lives mid-frame; top ~15% and bottom ~20% stay clear (platform UI + caption band). Cards are centered rounded rectangles ~80–90% width with generous negative space; headlines often left-aligned/top-anchored while the focal card sits centered below. Exceptions are deliberate: big-word backgrounds and full-bleed photo/screenshot scenes. **9:16 letterbox safe-zone + persistent corner chrome** (watermark/eyebrow/handle) is near-universal (G3·"build a standard frame chrome").

### LAW 8 — Every video closes on a mandatory CTA/follow outro. **[VERY HIGH — all 4 groups]**
~5–12s: follow-card (avatar + handle + accent button — G1·v4/v7/v9/v10, G4·T49), install/terminal CTA (`git clone`/`brew`/`npm` — G1·v2/v4/v14), brand-wordmark reveal (G1·v12), or a native-platform engagement hook ("Comment 'AI'" — G2·v16, G4·T50; "^^ to pinned comment" — G2·v15). Several end on a waveform synced to the outro VO (G1·v3/v13).

### LAW 9 (secondary) — Retention scaffolding: progress bar + "N points" counter + active-state highlighting. **[MEDIUM — G3 emphasized]**
Top or bottom **progress bar** showing position in the video (G3·v31·30s, v33·41s) and an **"N ĐIỂM NỘI DUNG"** counter (G3·v33). In every list, the **current row/step is filled with the accent while others are muted** (G3·v29 step-03, v35 active-row, v42 step-chain; G4·T54 red-active/gray-inactive nodes).

---

## 2. THE MEASURED MOTION CONSTANTS

Every number the groups reported. **"measured"** = from a dense 10–30fps re-sample (frame-accurate). **"inferred"** = from 1fps/2s montages or count-delta shape (±1–2 frames / ±1s). Easing curves were never curve-fit.

| Behaviour | Value | Confidence | Source |
|---|---|---|---|
| Karaoke per-word recolor | ~3–5 frames (**0.15–0.25s**)/word, colour-only, no scale | measured | G1·v13·3s; G2·v24·20s; G4·T54·44s |
| Caption phrase-swap (calm) | **~0.9–1.0s**/phrase, ~1-frame gap | measured | G1·v4·0s |
| Caption phrase-swap (dense) | **~0.6s**/phrase, tracks voice | measured | G1·v4·31.3s |
| Caption phrase swap (general) | ~1.0–1.3s/phrase | inferred | G2 (all) |
| List-row stagger reveal | **~5–7 frames (~0.2s)** apart, fade + slight slide-up, ease-out, **NO overshoot** | measured | G1·v4·31.3s |
| Card slide-in stagger | ~0.2s apart, edge-slide + fade | measured | G2·v16·8.5-9.3s |
| Word-build headline | each word ghost→black over **~0.15s**, ~0.3–0.4s/word, no overshoot | measured | G2·v16·6.4-10.3s |
| Number count-up | **~1.5–1.6s**, ease-out deceleration, + sparkle particles | measured | G1·v10·91.8s |
| Number count (decrement) | ~3,000–3,500/s, decelerating, **locks on final** | measured | G2·v16·3-7.56s |
| Wordmark specular sweep | **~12 frames (~0.4s)** left→right highlight across letters | measured | G1·v4·0s |
| Connector-line grow | **~0.5s**, eased, source→target | measured | G4·T54·44-46.5s |
| SVG stroke-reveal diagram | branch curves draw ~0.1-0.25s, then nodes pop ~0.3–0.5s apart | measured | G2·v28·0-3.6s |
| Glow-bloom + focus-resolve entrance | blurred+glow → sharp over **~0.35–0.5s**, sparkle burst at resolve | measured | G2·v24·18.1-21.3s |
| Chapter glow-bloom transition | fade ~3f → accent radial flood ramp ~5–6f → decay ~10f; **total ~0.7–1.0s** | measured | G1·v1·99.3s |
| Icon/logo pop-in | ~0.15s pop **with slight overshoot** + one-pass diagonal shine glint | measured | G2·v20·0.33-0.5s |
| Doodle POP-in (Register B) | element appears in **1–2 frames (0.1–0.2s)** on beat — NOT stroke-by-stroke | measured | G4·C1·4-6.5s |
| Doodle "boiling line" wiggle | subtle per-frame outline redraw (2–3 frame loop) | measured | G4·C4·28-30.5s |
| Scan-line sweep across cards | ~1.5s vertical line traverse | measured | G4·T44·7-9.5s |
| Title colour-animation | white→accent over ~4s | inferred | G3·v36·0s, v42·0s |
| Typical scene hold | **~5–6s** (template/review), 8–14s (explainer) | inferred | all |
| Big:small type ratio | **~4–6:1** (hero number/wordmark vs caption) | measured/inferred | G1·v4; G2·v16; G4·T49 |

### ⚠ THE CRUCIAL CORRECTION — NO overshoot/spring, NO motion blur. Ease-out only.
**All four groups independently report the reference craft is calm motion + loud colour/type — NOT bouncy physics.** G1: "I saw **no overshoot/spring** and no motion blur in any of the 14… the reference craft is calm motion + loud colour/typography." G2: "Heavy bouncy overshoot is *absent*; the 'energetic' feel comes from **glow-bloom + particle-sparkle + focus-resolve**, not spring physics." G3/G4 concur (ease-out fades/slides). Energy comes from **colour blooms + big type + count-ups + karaoke recolor + glow**, entrances are **ease-out (settle, no bounce)**. The only overshoot anywhere is a **tiny ~0.15s pop on icons/logos/nodes** (G2·v20, G2·v24) — a hair, not a spring. **This corrects any earlier "make it bouncy / add motion-blur" instinct: match the restraint.**

---

## 3. THE CONTENT / SUBJECT VOCABULARY (drawable focal graphics)

The full catalogue of "focal graphic" types seen, each tagged with the beat-type it serves. All are self-drawable in HTML/CSS/SVG on light bg.

| Subject | What it is | Beat it serves | Cites |
|---|---|---|---|
| **Chip / tag grid** | rounded icon+label pills, staggered pop-in | features, ecosystem, "what it supports" | G1·v2/v4/v5/v7; G3·v39/v42; G4·T49 |
| **Numbered list card** | rows `① title / subtitle`, staggered, active-row highlighted | steps, "N reasons", mistakes | G1·v4/v8/v13; G3·v29/v41; G4·T49 |
| **Big-number stat hero + qualifier chips** | huge accent numeral + small unit/label chips | the headline metric of a beat | G3·v36·34s "~22.000"; G4·T49 "0đ", T44 "30 GIÂY" |
| **Stat-pill row** | "**61%** avg / **v2** realtime / **open** code" — colored key + gray unit | outro/summary recap | G3·v36·1:00 |
| **Comparison / VS bars** | two stacked bars/tables, problem-vs-solution, per-column colour | before/after, old-vs-new, tool-vs-tool | G1·v5/v11; G2·v17/v21; G4·T45/T46 |
| **Grouped bar chart + delta badge** | accent vs gray bar pairs, clean axis, "+2.90 ↑" callout, grow-once static-final | benchmark, comparison numbers | G3·v36·1:09; G2·v25·29-40s |
| **Donut / gauge / progress meter** | ring with center %, arc+needle gauge, progress bar fill-to-value | a single percentage or limit | G1·v10·51s donut/78s bar; G2·v20 gauge; G3·v31·30s gauge; G3·v42 |
| **Hub-and-spoke node diagram** | central node + typed icon spokes on a ring, glowing connectors, traveling dot | "ecosystem", "one core → many", capability map | G2·v24·18-37s; G3·v37·24s; G4·T47 |
| **Step-by-step algorithm diagram** | nodes (active-accent/inactive-gray) + growing connectors + doc skeleton-cards w/ rank badges + fusion/merge bars, assembling over runtime | explaining an algorithm/process | **G4·T54 (★ our exact target)**; G2·v24 |
| **Spatial-flow through-line** | one persistent connector path the viewport travels + numbered glowing node markers + progress scaffold | multi-point process/loop journey | G3·v33 (trạm ai "SPATIAL FLOW") |
| **Vertical stepped-flow (how-to)** | steps as a highlighted node chain + terminal chip | install / setup tutorials | G3·v42·34s; G1·v14 |
| **Code / terminal block** | mono font, syntax highlight, lines appear one-by-one, success ✓ | "proof", install CTA, config | G1·v2/v4/v8/v14; G3·v37/v41; G4·T49/T56 |
| **Framed screenshot / screen-rec** | product shot in rounded inset, small margin, persistent tiny header label | real-product demo / "walkthrough" | G1·v4/v5/v12 (55s screen-rec); G2·v19 (Ken-Burns tour); G3·v29/v32 |
| **Pipeline transformation card** | old value **struck-through** → new value in accent, arrow between | "v1→v2", "old way→new way" | G3·v36·20s; G4·T56 |
| **Big-word background typography** | huge low-opacity word bleeding/drifting behind content | mood / chapter emphasis | G1·v6/v11; G2·v16/v17/v21 (ghost numerals) |
| **Notification / chat / repo-card mockup** | IG comment bar, chat bubble, GitHub repo card w/ colored pills | "proof", social CTA, source | G1·v3; G2·v16 (type "AI"); G2·v25 chat→SQL |
| **Metadata / spec chip card** | stars · date · version + feature tags | tool intro | G4·T49; G1·v4 |
| **Timeline / roadmap strip** | horizontal dots with dates/milestones | history, "when", roadmap | G1·v9·54s; G2·v20; G4·C5 milestone |
| **Full-bleed hero imagery under overlay** | real photo/AI b-roll behind navy/green graphics (pairs with image_sourcer) | dramatic hook / chapter divider | G3·v38/v40; G4·T48 |
| **Card-multiplication** | 1 card splits into 3 | "consistency / multi-scene" | G4·T44 |
| **Countdown 3→2→1 big numbers** | giant numerals, step beat | dramatic list/step intro | G1·v13; G2·v15 (ghost) |

---

## 4. THE LIGHT-BRAND NORTH STARS (study these hardest — technique, not skin)

The few reference files the groups flagged as closest to our light navy/green brand. Copy the *technique/structure/semantic-colour logic*, invert to our palette, author as SEOSONA.

- **T54 `rag fusion.mp4`** — cream `#F2EFE9`, single red-orange accent, black body. **★★ closest to our exact target.** The **entire light-bg step-by-step diagram vocabulary**: accent/gray node states, growing connector lines (~0.5s eased), document skeleton-cards with rank badges, fusion/merge bars, **progressive assembly synced to per-word captions**, continuous soft glow-pulse on the active node. *Copy: the whole diagram grammar; recolor red→green-active/gray-inactive/navy-ink.* (G4·T54)
- **T53 `SAA`** — cream `#F5EFE6`, single orange accent, black heading. **Our exact glow-on-light discipline**: light bg + black heading + single-accent keyword highlight; also a post-composer UI mockup + XP/level gamification chips; and a **hand-drawn doodle element living on a light bg** (the bridge to Register B). *Copy: the cream + black-text + one-keyword-highlight discipline.* (G4·T53)
- **v41 FreeLLMAPI (light neo-brutalist)** — the ONLY light video in its slice. Cream `#EDEAE0` + faint engineering **graph-paper grid**; **outlined flat-colour cards with 3px black border + hard offset drop-shadow**; eyebrow pill (yellow fill + black border); heavy rounded title + short underline bar; **numbered feature rows** (icon-tile + title + subtitle + big index); 2×2 stat grid; colored file-tree; sticker-karaoke with stroke. *Copy: the confident self-drawn "outlined card + hard shadow + graph-paper" language so LIGHT doesn't feel empty; swap playful yellow/mint/red for navy/green + one warm secondary; keep black-border+hard-shadow.* (G3·v41·33s)
- **v28 Học Git (KNG/Eric Trần AI, light)** — **★ our target structure.** Persistent top header (section label + title) + centered **white content card** (soft shadow ~24px radius) + **bottom gray caption pill with green karaoke keyword** + slim credit bar; **SVG stroke-reveal diagrams with node-pop**; lesson/status **table card** with colored status pills; **scoreboard card** with counting numbers. "Almost exactly our target aesthetic." (G2·v28·0-3.9s)
- **v16 Comment "AI" (light, airy bokeh)** — near-white + very desaturated drifting pastel bokeh (no dark). **Live counting number as the hook** (down for waste, up for growth, ease-out lock); **word-build headline** with coral problem-keywords; **ghost outline section numerals 01/02/03**; partial-word accent wordmarks; **semantic stat colour** (gray=bad→green=good); color-coded summary triad matched to 3 cards; rotated "100% FREE" sticker; type-the-keyword IG comment-bar CTA. (G2·v16·6.4-10.3s)
- **v47 System Prompts Leaks (dark but GREEN accent)** — closest *template* to our green: hub-and-spoke orbit diagram for "ecosystem", green check-dot checklist, mind-map node branches, amber caveat chip as the single contrast to green. *Proves our green does the single-accent job natively.* (G4·T47)
- **v35 cc-switch (dark but GREEN YupVid)** & **v42 NVIDIA NIM (green escbase)** — prove the accent is a per-video variable and the **green** variants are the on-brand-closest of those template families (problem-card→feature-list→active-row→summary spine; vertical stepped-flow). (G3·v35, v42)

---

## 5. THE DOODLE / WHITEBOARD MODE (Register B — the capability we lack)

From the Course set (C1–C6) + T53 hybrid. **Highest learning value** because we have nothing like it. Personality-led narrative argument built as a running hand-sketch.

**Frame layout:** outer **dark grid/graph-paper** border → inner **white crumpled-paper center panel** (the "whiteboard", where all doodles play) → **bottom caption band** on the dark area. A **presenter photo-cutout PIP** pinned to one top corner (persistent, real person) + a **comic-lettered thesis title** (hand-drawn outlined red+black lettering) pinned to the opposite corner for the whole video (G4·C1–C6).

**Doodle vocabulary (on the white panel):** stick figures with expressive faces + prop metaphors; **speech/thought bubbles** (pre-exist empty, text fills them); arrows; **comic starburst "POW" stat-badges** (C1 "40% TRUY VẤN", "GIẢM 34%"); **hashtag chips**; **comic-X cross-outs** on obsolete items (C2 crosses out từ khóa·backlink); **yellow-highlighter marker** underline/fill on key words; **real brand logos** dropped straight into the sketch (Google, ChatGPT, Perplexity); **metaphor drawings** (SEO=courting-Google funnel/courtship C5, milestone timeline).

**Caption:** **all-caps, bold, phrase-append** (whole phrase appears, next appends/replaces — NOT per-word karaoke), emphasis words switch to red (G4·C1–C6).

**★ CRUCIAL build insight — it's cheap to fake:** motion is **static pre-drawn SVG doodle assets that POP in on the beat in 1–2 frames (0.1–0.2s)** — **NOT** stroke-by-stroke draw-on. Add an optional **2–3-frame "boiling-line" wiggle** (per-frame outline redraw) for the "alive hand-sketch" feel and an **orbiting sparkle** on callouts (measured G4·C1·4-6.5s, C4·28-30.5s). No real hand-draw/stroke engine required. **For us:** redraw the doodle assets in navy/green line-art, green highlighter instead of yellow, author original metaphors — this is a buildable second mode, not a stretch.

---

## 6. RANKED ENGINE BUILD BACKLOG

Consolidated & de-duplicated across all four groups' ranked lists. **[HAVE]** = memory/engine already has it; **[BUILD]** = must build; **★** = highest impact. Ranked by (frequency × brand-fit × leverage).

**Tier 1 — build first (universal + directly on light brand):**
1. ★ **[HAVE, extend]** **Scene-template struct** `{kicker, headline(line1/accent line2), focal, caption}` as the backbone — the single highest-coverage component (LAW 2). *G1·A1, G2·spine, G4.*
2. ★ **[HAVE, extend]** **Two-mode caption engine.** (a) karaoke keyword-recolor → green, ~0.2s/word, two-tier dim-context line + boxed-keyword variant; (b) phrase-swap ~0.7–1.3s. We have ASS karaoke — add two-tier, boxed, phrase-swap, and the all-caps phrase-append for doodle mode. *LAW 4; G1·A3, G2·#1, G4·#3.*
3. ★ **[HAVE, extend]** **Semantic per-section accent** driven by script tags: `error→red, success/topic→#00AA00, highlight→gold, neutral→#003BA6, inactive→gray`; switch per chapter. Close to existing `ROLES`. *LAW 3; G1·A2.*
4. ★ **[BUILD]** **Light-bg step-by-step DIAGRAM vocabulary** (the T54 grammar): active/inactive node states, growing connector lines (~0.5s eased), doc skeleton-cards with rank badges, fusion/merge bars, hub-and-spoke orbit, mind-map branches — assembled progressively, synced to captions. **The single biggest adopt.** *§4; G4·#1, G3·#8; T54, v47, v24.*
5. **[HAVE, extend]** **Ease-out count-up** stat (~1.5s decelerating, lock-on-final, optional sparkle; down for waste / up for growth; good→green, bad→gray). Maps to data-viz. *§2; G1·#4, G2·#3, G3·#2.*
6. **[HAVE, extend]** **Staggered list-row reveal** (fade + 8–12px slide-up, ~0.2s stagger, ease-out) w/ numbered badges + active-row highlight. *G1·#5.*
7. **[BUILD]** **Kicker/eyebrow label** component (uppercase, letter-spaced, dot/step-icon lead) + eyebrow-pill variant (v41 filled pill). *G3·#6, G4·#5.*
8. **[HAVE, verify]** **CTA/follow outro** (avatar+handle+accent button / terminal-install / native "Comment X" hook). Mandatory close. *LAW 8; G1·#7.*

**Tier 2 — build next (motion energy + data-viz, re-skinned to light):**
9. ★ **[BUILD]** **DOODLE / whiteboard mode** (Register B, §5): white paper panel + static SVG doodles popping on beat + boiling-line wiggle + starburst stat-badges + X cross-outs + highlighter + phrase-append band + presenter-PIP + comic thesis title. New register, high learning value. *G4·#2.*
10. **[BUILD]** **Chapter glow-bloom transition** — radial accent-tinted wash 0→~0.7→0 over ~25f under a cross-fade; soft navy/green bloom on white. *LAW 5; G1·#8, G2·#5.*
11. **[BUILD]** **Glow-bloom + focus-resolve entrance** for cards/diagrams — blur+low-opacity+glow → sharp over ~0.35s + sparkle at resolve (light re-skin of sockseo's neon bloom). *§2; G2·#5.*
12. **[HAVE, extend]** **Animated data-viz set**: donut/ring center-% (sweep-fill), progress-bar fill, arc+needle gauge, before↔after stat-circles + flow-dot connector, grouped bars **+ delta badge**, stat-pill row. We have ring/donut/bars/linechart — add entrance animations, center-label, gauge, delta badge, stat-pill. *§4; G1·#9, G2·#8-9, G3·#3-5.*
13. **[BUILD]** **SVG connector/flow primitives**: node-then-edge draw (stroke-dashoffset), **dot traveling a path**, spatial-flow through-line + progress scaffold, vertical stepped-flow, stroke-reveal + node-pop. *§4; G2·#6-7, G3·#8/#10.*
14. **[HAVE]** **Chip/tag grids** popping staggered; **comparison idioms** (two-column color card, VS battle card w/ logo tiles, before/after value-pills w/ arrow, color-coded recap tiles). *G1·#10-11, G4·#7.*
15. **[HAVE, extend]** **Framed screenshot/screen-rec as b-roll** (rounded inset, small margin, persistent header label) + Ken-Burns screenshot-tour fallback. *G1·#12, G2·#17.*
16. **[BUILD]** **Retention scaffold**: top/bottom progress bar + "N points" counter + active-state list highlighting. *LAW 9; G3·#8.*
17. **[BUILD]** **Pipeline transformation card** (strikethrough-old → accent-new + arrow). *§4; G3·#9, G4·#6.*
18. **[BUILD]** **Breathing background system**: faint navy dot-grid / graph-paper + slowly-drifting green/navy radial bloom; optional per-chapter cool→green tint shift. *LAW 6; G2·#15, G3·bg, G4·#8.*

**Tier 3 — selective / harder:**
19. **[BUILD]** **Three-"font" hierarchy** approximated in Be Vietnam Pro (ExtraBold display / regular body-chips / **add a mono for code**) + big:small ~4–6:1. *G1·#13.*
20. **[BUILD]** **Specular wordmark sweep** (~0.4s) + **title colour-animation** white→accent + **big-wordmark horizontal text-wipe** as a section break + **scan-line sweep** across cards. Sparingly, as glow-energy. *§2; G1·#14, G3·#15, G4·#11.*
21. **[HAVE, port]** **Marker-strike / highlighter text** (accent bar wipes in behind a bold keyword) — we have a marker-wipe concept (cinematic reel). *G1·#16.*
22. **[BUILD]** **Big-word background typography** (huge low-opacity word, pale navy tint on light) + **ghost outline section numerals 01/02/03** + **giant ghost countdown numerals**. *LAW 6; G1·#15, G2·#12.*
23. **[BUILD]** **Neo-brutalist light card option** (outlined flat-colour card + hard offset shadow + graph-paper) for a confident self-drawn look on white. *§4; G3·#13; v41.*
24. **[BUILD]** **Outline/eyebrow semantic colour-coding** (border colour = meaning: navy neutral / green positive / reserved alert) + **card taxonomy** (quote/pull-quote, profile, data-table, warning/lock/conclusion, terminal-with-success, file-tree, 2×2 stat grid, social-follow, chip-row). *G3·#14/#16.*
25. **[DON'T CHASE]** GPU-rendered 3D spectacle interludes (G1·v9 data-rain/particle-funnel/wireframe-server). High cost, off-brand for a clean light system; SVG HUD/gauge/timeline approximations (item 12/13) capture ~80% of the intent. *G1·D3-20.*

---

## 7. THE EXPLICIT DO-NOT-COPY LIST

We port **technique + structure + semantic-colour logic**, inverted to our light brand, authored as SEOSONA. Do NOT copy:

- **Dark palettes / near-black backgrounds** — 50+ of 62 are dark; our brand **forbids dark mode**. Port their structure, not their value scheme. (all groups)
- **Neon-on-black accents** — cyan/magenta/orange/purple/red neons. Replace with navy `#003BA6` + green `#00AA00` (+ one reserved warm alert tint). (G1, G2, G3)
- **Other creators' watermarks, wordmarks, handles, channel names, seals** — yupvid.com, escbase.xyz, @sockseo, @aidailyone, trạm ai, "CERTIFIED" seal, KNG/Eric Trần AI, Lạch Cạch AI, AIDev Repo, presenter face-cutouts, etc. Provenance goes to the vetting log only; author = SEOSONA. (G3·attribution, G4·PIP)
- **Any specific brand's exact look** — escbase auto-themes its accent to the subject's brand (Kimi=cyan, Meta=blue, NVIDIA=green); we are **brand-LOCKED**, we fix the accent. Copy the "one accent drives everything" discipline, not the per-subject reskin. (G3·headline)
- **Heavy spring/bounce overshoot & motion-blur** — deliberately absent in the references; match their **ease-out restraint** (§2 correction). Copying a "bouncy" feel would diverge from the actual craft. (G1, G2)
- **Yellow highlighter / red comic lettering as literal skin** in doodle mode — redraw in navy/green line-art with green highlighter, original metaphors. (G4·§5)

---

## EXECUTIVE SUMMARY (feeds the live engine rebuild)

### The structural laws (8)
1. **Near-ZERO hard cuts** — one continuous timeline; ELEMENTS enter/hold/exit on the caption beat. Think element-keyframes, not scene cuts. *(all 4 groups, scdet-confirmed)*
2. **Universal scene skeleton**: `kicker → 2-line headline (accent on line 2) → ONE continuously-animating focal graphic → running bottom caption`. Model as one struct.
3. **Single-accent, semantic, per-chapter**: red=problem, green=good/topic, gold=highlight, navy=neutral ink, gray=inactive; accent switches per chapter, not per video.
4. **Persistent bottom caption is the engagement spine** — karaoke keyword-recolor (~0.2s/word) or phrase-swap (~0.7–1.3s); re-highlights every ~0.4s.
5. **Transitions = 0.3–1.0s colored glow-bloom + crossfade**, never cuts (soft navy/green wash on our light bg).
6. **Backgrounds are a slowly-breathing mood** (radial bloom / dot-grid / graph-paper), never a flat fill; + ghost texture layers.
7. **Contained centered cards in the middle ~60%**, big platform-safe margins, persistent corner chrome.
8. **Mandatory CTA/follow outro** on every video.
*(+ secondary LAW 9: retention scaffold — progress bar + "N points" + active-row highlight.)*

### Measured-constants table (frame-accurate unless noted)
| Behaviour | Value |
|---|---|
| Karaoke per-word recolor | 0.15–0.25s/word, colour-only |
| Caption phrase-swap | ~0.9s calm / ~0.6s dense |
| List-row stagger | ~0.2s apart, fade+slide-up, ease-out, no overshoot |
| Number count-up | ~1.5s, ease-out, lock-on-final, + sparkle |
| Connector-line grow | ~0.5s eased |
| Wordmark specular sweep | ~0.4s |
| Glow-bloom / focus-resolve entrance | ~0.35–0.5s + sparkle |
| Chapter glow-bloom | ~0.7–1.0s total |
| Icon pop-in | ~0.15s, slight overshoot + shine glint |
| Doodle POP-in (Register B) | 0.1–0.2s on beat, NOT stroke-by-stroke |
| Scene hold | ~5–6s template / 8–14s explainer |
| Big:small type ratio | ~4–6:1 |
*(inferred from 1fps/2s montages elsewhere: phrase cadence, easings, holds — ±1–2 frames/±1s; no audio analyzed; hexes ±10)*

### Top-10 ranked build backlog
1. ★ **[HAVE, extend]** Scene-template struct (kicker/headline/focal/caption).
2. ★ **[HAVE, extend]** Two-mode caption engine (karaoke + phrase-swap/append), green keyword, two-tier + boxed.
3. ★ **[HAVE, extend]** Semantic per-section accent (navy ink / green active / gray inactive / reserved alert).
4. ★ **[BUILD]** Light-bg step-by-step DIAGRAM vocabulary (T54 grammar) — **the single biggest adopt**.
5. ★ **[BUILD]** DOODLE / whiteboard mode (Register B) — static SVG doodles popping on beat; new capability.
6. **[HAVE, extend]** Ease-out count-up stat + semantic stat colour (gray=bad→green=good).
7. **[HAVE, extend]** Staggered list-row reveal + numbered badges + active-row highlight.
8. **[BUILD]** SVG connector/flow primitives (node→edge draw, traveling dot, spatial through-line, stepped-flow).
9. **[BUILD]** Chapter glow-bloom + focus-resolve entrances (light re-skin).
10. **[HAVE, extend]** Data-viz upgrades: gauge, donut center-%, progress fill, delta badge, stat-pill row.

### The 2–3 biggest corrections to how we've been building
1. **KILL the bounce/spring/motion-blur instinct.** All 4 groups independently confirm the reference craft is **ease-out only** — energy comes from **colour + type + count-ups + glow + karaoke**, not kinetic physics. The only overshoot is a ~0.15s hair on icon pop-ins.
2. **Stop thinking in scene cuts.** The corpus is a **single continuous timeline of element ENTER/HOLD/EXIT keyframes synced to the caption beat**. Cuts are near-zero. Our engine's mental model should be element choreography, not shot changes.
3. **Build the two missing pillars:** (a) the **light-bg progressive diagram vocabulary** (T54) — active/inactive nodes, growing connectors, skeleton doc-cards, fusion bars — and (b) the **doodle/whiteboard register** (cheap: static SVG assets popping on beat, no stroke engine). These are where we have the least and the references have the most transferable value; our north-star light files (T54, T53, v28, v16, v41) prove the whole look lands on navy/green + Be Vietnam Pro without copying anyone's dark neon skin.
