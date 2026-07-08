# Craft Study — 45 reference short-videos (2026-07-01)

Distilled from a scene-by-scene analysis of 45 SEOSONA/tram-AI 9:16 shorts in `D:\SEOSONA AI\Video Template`
(storyboards in `8_WORKSPACE/template_study/sheets/`, 6 parallel analyst passes). Source videos are dark-neon;
**we render LIGHT**, so the palette is dropped and only the *brand-agnostic craft* + *semantic color ROLES* are kept
(map roles → SEOSONA light palette: see §3). Goal: enrich the template/block/component libraries with what these
proven videos do that the factory doesn't yet.

## 0. Two engines (tag every output as one)
- **A — card-explainer (motion-graphics):** built rounded cards on a dot-grid field — the SEOSONA `native_composer`
  path. ~40 of 45. This is where the archetype/motion enrichment below applies.
- **B — footage / essay:** real screen-capture or talking-head footage + burned-in VN subtitle + one English
  keyword-pop + persistent source-credit line (videos 16, 22, 24, parts of 21/31). Maps to the talking-head engine
  ([[talking-head-engine]]). Different craft — keep separate; its signatures: karaoke keyword highlight, chapter
  color-wash backgrounds (essay), stat re-slam over b-roll.

## 1. Scene-archetype catalog (frequency across 45 → have/GAP)
Ordered by how often it carries a scene. "Have" = a `native_composer` scene-comp or an `hf_blocks` block already
covers it; **GAP** = build it.

| Archetype | Freq | Status |
|---|---|---|
| **title-hook** (question / bold-tech / serif-hype / mono-filename / brutalist) | 45/45 | Have (hero) — add the 5 named *variants* + "screenshot-behind-title" |
| **progressive-reveal list / checklist** (rows in one-by-one, ✓ or ①②③) | ~40 | Have (steps/list) — **GAP: the reveal cadence + ✓/number-badge variants as first-class** |
| **compare-2col / VS / before→after** (winner side glows) | ~30 | Have (compare) — **GAP: VS-badge center, winner-glow, per-entity color-hold, before→after arrow** |
| **bignum-stat** (one giant number, radial-glow) | ~35 | Have (bignum) — **GAP: radial-glow pulse + count-up + delta-chip + "strike-through false number"** |
| **browser / repo / file-tree mockup** (real screenshot, expands line-by-line) | ~25 | Partial — **GAP: github-repo-card + file-tree-reveal + screenshot pan/zoom doc-tour** |
| **terminal-mockup** (`$ install…`, ✓ log states) | ~18 | Have (terminal + 20 code-snippet blocks) — add live-command ✓ step states |
| **node-diagram / hub-and-spoke** (center + orbiting satellites) | ~15 | Partial (flowchart) — **GAP: hub-and-spoke + orbit-loop + the traveling-dot progress line (§4)** |
| **icon / pill category grid** (2×2/2×3/cloud, color-per-tile) | ~15 | **GAP** |
| **alert / danger callout** (bordered/red, "Lưu ý / rủi ro") | ~12 | **GAP** (dashed-border danger card + amber caution card) |
| **status-badge list** (green done / amber in-progress / grey locked) | ~6 | **GAP — high value** |
| **data-viz** (grouped bars, donut, line-chart, gauge/score-bar) | ~8 | Partial (data-chart) — **GAP: gauge/score-bar + XY line-chart + donut** |
| **summary / recap** (2-col or 3-color-card, pre-CTA payoff) | ~12 | Have (feature) — add the color-coded 3-card recap |
| **quote / authority pull-quote** (oversized “ glyph + attribution) | ~6 | Have (quote) — add big-glyph + attribution row |
| **chip-row reveal** (compat/tool chips one-per-frame) | ~15 | **GAP** (as a reusable atom) |
| **CTA** (subscribe-stack / star-repo / URL-pill / comment-bait / follow-lower-third) | 45/45 | Have (cta) — add the 5 named variants |
| **prompt/recipe carousel** (templated card ×N, copy-button, numbered badge) | 2 | **GAP — niche but strong for "N tips" content** |
| **framed-media reel** (glow-border clip + source-credit footer, montage body) | 2 | **GAP** (engine-B-ish) |
| **radial-selector menu** (circular orbit menu, active dot) | 1 | GAP (low priority) |
| **chat-bubble / social-proof mockup** (iMessage / tweet / reply stack) | 4 | **GAP** (reddit-post/x-post exist; add chat-thread + tweet-quote) |

## 2. Structure grammar (the shared spine)
`HOOK (0–10s: brand-lockup + provocative title / bignum / question, one highlight word)` →
`BODY (reveal-lists + compares + mockups + bignums, each with a bottom caption)` →
`optional DATA/RISK beat (chart or alert — editorial videos only)` →
`SUMMARY card` → `CTA (URL / subscribe / comment-bait)`.
- **Pacing bands:** repo-hype ≈ 10 scenes/min; card-explainers ≈ 5–7/min; footage/essay ≈ 3–7/min. A new visual beat
  every **~3–5 s** (frames in the sheets are dense samples of slow animations, not distinct cuts).
- **Numbered chapter system** on editorial pieces: kicker like `HỒ SƠ AI / 01`, `PHẠM VI / 02` — a spine to follow.

## 3. Color-semantic ROLE system (the biggest cross-cutting find)
Colors carry FIXED meaning independent of palette. Formalize as named roles; the light render maps each role to the
SEOSONA palette ([[brand-colors-light-only]]) — preserving MEANING, dropping neon (glow → soft drop-shadow):

| Role | Meaning | Light-palette mapping |
|---|---|---|
| `emphasis` | the one highlighted word / hero keyword | brand blue `#2A5BDA` (or coral for warmth) |
| `success` | solution / free / confirmed ✓ / winner / speed | green |
| `danger` | error / cost / pain / deprecated / "not X" / rejected | coral `#E2724D` |
| `caution` | warning / "verify this" / reality-check | amber |
| `info` | neutral data / secondary chips / the losing variant | muted blue / grey |
| `baseline` | human/old reference, locked/absent (grey strikethrough) | grey |
| `entity[n]` | per-competitor identity color, HELD across the whole video (VS bars, chart lines, cards) | a fixed brand-tint per entity |
| `category[n]` | wayfinding hue per icon-grid tile (NOT good/bad) | the categorical 4-set (see V32 brutalist) |

**Hard rules:** exactly ONE `emphasis` word per caption line; ONE hero color per bignum; danger always warm, success
always green/cool; disambiguate amber (hero-stat vs caution) by icon (badge vs warning-triangle).

## 4. Motion recipe library (distinctive, add to [[motion-recipes-seosona]])
1. **one-by-one reveal** — list rows / chips / satellite nodes stagger in (the dominant body motion).
2. **traveling-dot on a progress line** — a glowing dot animates along a horizontal track under a hub ("một đường
   chính / tiến trình"). *The signature node-diagram motion — GAP.*
3. **radial-glow pulse** — breathing glow behind a danger title or hero number.
4. **winner-border draw + ✓** — comparison winner animates a glowing border + check line.
5. **count-up / number scale-in** + **delta-chip** on stats.
6. **strike-through wipe** — red line slashes a false/old value (also version v1→v2 arrow-draw).
7. **bars grow-from-axis / arc-sweep gauge / dashed-connector draw-on** — data-viz + diagram entrances.
8. **toggle-slider state-flip** + **color-temperature ramp** (dark→orange→bright = emphasis build).
9. **dimmed screenshot auto-scroll** as an ambient spine (doc-tour) + **word-by-word caption burn-in** synced to VO.
10. **framed-media autoplay montage** (glow-border clips) · **stat re-slam over b-roll** (engine B).

## 5. Layout grammar (9:16, add to [[house-style]])
- **3-zone stack:** top = channel-lockup watermark + kicker/section chip; center = ONE hero (card / bignum / diagram
  / mockup); bottom = one-line VN caption with a single `emphasis` word + source-credit footer.
- **One idea per frame** — never two competing focal points. **One `emphasis` color per frame.**
- **Rounded-rect cards everywhere** (border color = the role); dashed-border+glow = "special/dangerous" card.
- **Persistent channel-lockup overlay** (logo/@handle every frame) — worth a global overlay component.
- **Light-theme references already in the set:** videos 13, 23, 32 (neo-brutalist: cream bg, thick black border, hard
  offset shadow, 4-color categorical blocks), 42, 43. Use 32 & 43 as the light-render north-stars.

## 6. Prioritized enrichment plan (build order)
Highest reuse × currently-missing first. Each is a light-theme card component for `native_composer` / a new block.
1. **Semantic-role color system** — encode §3 as named roles in the render (biggest leverage; unlocks all below).
2. **compare-2col upgrade** — VS-badge, winner-glow, per-entity color-hold, before→after arrow variant.
3. **bignum-stat upgrade** — radial-glow pulse + count-up + delta-chip + false-number strikethrough.
4. **progressive-reveal list/checklist** — ✓ / ①②③ badge variants + tri-color **status-badge** (done/progress/locked).
5. **hub-and-spoke node-diagram** + the **traveling-dot progress line** motion.
6. **icon/pill category grid** + **chip-row reveal** atom.
7. **alert/danger callout** (dashed-border danger + amber caution).
8. **repo-card + file-tree-reveal + screenshot doc-tour** (proof beats).
9. **data-viz set** — gauge/score-bar, XY line-chart, donut.
10. **CTA + title-hook named variants** (5 each) + **channel-lockup overlay** + **numbered-chapter kicker**.

This doc + the storyboards are the ANALYZE/DECIDE output; grow via `grow_library.py` per [[library-growth-pipeline]].

## 7. DELIVERED — new/upgraded `native_composer` scene components (2026-07-01)
Built + preview-verified (light render, brand-aware; previews in `8_WORKSPACE/template_study/component_previews/`).
Colours come from the semantic role tokens (`brand_kit.ROLES` + THEMES `c_*`/`role_color()`), so meaning drives hue.

1. **Semantic role system** — `brand_kit.ROLES` {emphasis,success,danger,caution,info,baseline} + THEMES `c_emph/c_ok/c_warn/c_bad/c_info/c_base` + `okbg/okbd/warnbg/warnbd/infobg/infobd` + `native_composer.role_color(role, brand)`.
2. **compare** (upgraded) — `{left:(title,[rows]), right:(title,[rows]), mode?:"beforeafter"}` → VS/→ badge + winner-glow.
3. **bignum** (upgraded) — `+ delta, delta_role, strike:True, sub` → radial glow + count-up + delta chip + red strike (false number).
4. **checklist** (new) — `{items:[(text,"done"|"doing"|"locked"), …]}` → tri-state badge ✓/◐/🔒.
5. **hub** (new) — `{center, nodes:[…≤8], line:True}` → hub-and-spoke + dashed connectors + travelling-dot progress line.
6. **icongrid** (new) — `{items:[(emoji,label[,color]), …]}` → 2-col categorical-colour grid.
7. **alert** (new) — `{role:"danger"|"caution", title, items|text}` → dashed(danger)/solid(caution) role-bordered callout.
8. **filetree** (new) — `{title, items:[(icon,name[,meta]), …]}` → window-chrome repo file listing, rows reveal.
9. **bars** (new) — `{items:[(label,pct[,color[,value]]), …]}` → score/compare bars (single=accent, multi=categorical/entity).
10. **chiprow** (new) — `{items:[…], solid?:True}` → compat/tool pill row, reveal one-by-one.

All carry `.ritem` where relevant → the existing reveal tween staggers them in; `_reveal_count` updated for each.
Preview any component with `scripts/preview_component.py::preview(kind, data, out_png, brand=…, kicker=…, title=…)`.

**CONNECTED (2026-07-01) — these now appear in real videos.** `4_BRAIN/component_picker.py` (new; the sibling of
`block_picker`, the single home of the scene→component vocabulary) is called by `video_engine.plan_scenes` for every
middle scene BEFORE its bignum/stats/tip/quote fallbacks. Deterministic + always-on (no LLM): it emits **alert**
(danger/caution cues), **bignum-strike** (a number flagged "chưa kiểm chứng/AI bịa"), and **chiprow** (an explicit
list of ≥3 short items), with a prev-kind guard so no component repeats back-to-back. Grow the vocabulary in
`component_picker.py`. Verified: a cue-laden script → alert + chiprow + bignum surface with correct kickers.

**STRUCTURED path CONNECTED (2026-07-01) — all 10 components can now auto-appear.**
`component_picker.enrich_llm(scenes)` runs ONE LLM pass (the `_COMPONENT_MENU` teaches the vocabulary + JSON
schemas) that assigns **hub / bars / compare / checklist / icongrid / filetree** (+ classics) to the scenes that
fit; `plan_scenes` calls it once and prefers its result for middle scenes. Every assignment goes through
`_validate(kind,data)` → render-safe (bad/short data is dropped, never crashes native_composer). **Auto-on** when a
real LLM is reachable (`SEOSONA_LLM_COMPONENTS=1` default; `=0` to disable); with no LLM it returns `{}` and the
deterministic `pick()` (alert/chiprow/bignum-strike) fills in. Verified: `_validate` accepts bars/hub/compare/
checklist/feature and drops invalid; the no-LLM path still emits chiprow/alert. Caveat: small local models
(gemma3) assign inconsistently — a stronger LLM (Gemini/OpenAI) enriches more scenes; the safety net makes either fine.

§6 tail items — DONE (2026-07-01): **CTA named variants** (subscribe/url/star/comment-bait/follow) built into the
`cta` comp (`d["variant"]`) + connected — `plan_scenes` rotates the variant per-video deterministically.
**Title-hook variant** — `native_composer._hook_style()` renders filename headlines (DESIGN.md, config.yaml) in
monospace (`.head.hk-mono`), auto-applied to every scene. **Channel-lockup** — already present (persistent
`.brandlogo` top-left + `.footer` on every scene); no new element needed.
Visual reference: `references/component-gallery/`. **Grow the vocabulary + LLM menu in `4_BRAIN/component_picker.py`.**
