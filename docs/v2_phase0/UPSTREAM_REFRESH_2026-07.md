# Upstream Refresh + Scene-Style Library — 2026-07-17

**Task:** check what is genuinely NEW upstream (Remotion, HyperFrames/nexu, the vetted video repos), and
propose a buildable style library that makes our faceless promos richer / more modern / more "AI-tech".

**Method:** GitHub REST API (`/repos`, `/commits`, `/releases`) + docs fetched live on **2026-07-17**.
Prior verdicts cited from `INGESTION_LOG.md`, `REPO_BATCH_TRIAGE.md`, `REPO_BATCH2_TRIAGE.md`,
`WHYBETTER_nexu.md` — so this reports **DELTA, not repeats**. Nothing cloned; no code written; no file
touched outside this doc.

**Brand lock (the whole lock, user's words: "tôi chỉ cần màu + font là của brand SEOSONA"):**
colours **#2A5BDA** + **#E2724D** (+ neutrals/paper), font **Be Vietnam Pro**. Layout/structure/materials/
density/background = FREE. Dark backgrounds allowed but **light stays home base** ("quá nhiều nền tối thì
không nên"); animated grids + gradient fields are first-class.

---

## 0. Headline findings (read this if nothing else)

1. ⭐ **GSAP is now 100% free, including every former paid Club plugin** — SplitText, MorphSVG,
   **DrawSVG**, ScrollTrigger, MotionPath, Inertia. Verified on `gsap.com/pricing` + the Standard License
   text, 2026-07-17. **This invalidates a design decision we already shipped:** our memory records
   `svg_draw_on.py` as a *"free DrawSVGPlugin stand-in"* built specifically because DrawSVG was paid.
   That constraint no longer exists. MorphSVG (shape morphing) is now available to us too — it is the
   single biggest new motion primitive on the table and it costs €0.
2. **Remotion is extremely active and licence-hostile to us** — v4.0.490, published **2026-07-16**
   (v4.0.475 → v4.0.490 in ~5 weeks). Company License required for companies. **We adopt zero code.**
   Craft ideas only, implemented ourselves.
3. **nexu-io/html-video: NO CHANGE since our read.** Last commit **2026-06-21**, which *predates* our
   2026-07-16 deep-read (`WHYBETTER_nexu.md`). Nothing new. Reporting that honestly rather than inventing
   a delta.
4. **The real bottleneck is not upstream.** Nobody upstream is holding richness back. We have 7 visual
   modes, a per-frame seek engine, a data-viz family, 95 icons, 58 SFX, and now a free MorphSVG/DrawSVG.
   The gap is **authored style breadth**, and it is ours to close. See §2.
5. 🚩 **Risk found while grounding the cue map (not asked for, but it will bite):** the promo SRT is raw
   VN ASR and is **full of transcription errors** — `prom`/`brom` (= prompt), `boss kem`/`bot kem`
   (= bootcamp), `phomo` (= FOMO), `tun` (= tool), `nhân viên xấu` (cue 73, = "nhân viên **số**"),
   `ai xe` (cue 24). Voice is fine — but **every style below that puts SRT words on screen (Kinetic,
   karaoke, pull-quote, Bento cell labels) will render those misspellings**. On-screen text must come from
   a **corrected display-text layer**, not from the SRT verbatim. This is a blocker for the type-heavy
   styles, and cheap to fix.

---

## (a) Per-repo DELTA — verified

| Repo / source | Last activity (verified) | Licence (verified) | DELTA vs our record | Verdict |
|---|---|---|---|---|
| **remotion-dev/remotion** | **v4.0.490, 2026-07-16**; v4.0.475 (2026-06-10) → 490 in 5 wks | **NOT free for companies** — Company License; Enterprise $500/mo min | Large. See below. | **Craft REFERENCE only. Never vendor.** |
| **nexu-io/html-video** | **2026-06-21** (c414ecc) | Apache-2.0 | **NO CHANGE since our 2026-07-16 read.** Last commit predates our deep-read. | No action. `WHYBETTER_nexu.md` stands. |
| **nexu-io/open-design** | 2026-07-16 (daily) | Apache-2.0 | Active — but commits are **landing page / careers / Vela CLI / agent-runtime / deploy**, i.e. the repo has become a *product* repo. **No registry/craft-block commits found.** Our HyperFrames craft take is unchanged. | No new craft. Re-check quarterly. |
| **bachdyon/video-automator-skills** | 2026-07-16 | **PolyForm Noncommercial 1.0.0** (LICENSE fetched, verbatim) | New since our analysis: *overlay video preparer* skill, *klipy-meme-search*, *English-learning split-subtitle template*, output-only showcase | **REFERENCE ONLY — NC. Do not adopt code.** Our `cinematic_reel.py` already carries the craft debt correctly. |
| **hoquanghai/Auto-Create-Video** | **2026-05-01** | MIT | **NO CHANGE** since ingestion (memory: MIT HyperFrames VN twin, converged). | No action. |
| **huytranvan2010/AI-auto-generate-video** | 2026-06-29 | MIT | Repo was **re-created 2026-06-28** ("The first commit"); last push 2026-06-29 **predates** our vetting. | No change. |
| **HUANGCHIHHUNGLeo/claude-real-video** | 2026-07-16, 1.67k★ | MIT | Still the Batch-2 **D-shortlist** survivor (scene-change + dedup frame selection). Unchanged verdict. | Still worth the clean-room extraction — **but it is video *analysis*, irrelevant to this richness task.** |
| **romboHQ/tailwindcss-motion** | **2026-02-12** (stale 5 mo) | MIT | **NO CHANGE.** | Roster-covered. No action. |
| **ruvnet/ruflo** | 2026-07-16, 64.6k★ | MIT | Growing fast but **still off-domain** (agent meta-harness, not video). | SKIP — verdict unchanged. |
| **mintdotgg/mint-threejs-skills** | 2026-07-15 | **MIT** ← *correction* | 📌 **Our record was wrong.** `REPO_BATCH2_TRIAGE.md:43` says *"none stated (unverified)"*. It **is MIT**. The SKIP still stands (paid Mint MCP + 3D/WebGL off-substrate) — but the stated *reason* should be corrected. | SKIP (on substrate grounds, not licence). |

### Remotion delta in detail (craft only — we write our own code)

Verified from the GitHub releases API, 2026-07-17:

- **`@remotion/rough-notation`** — brand-new package in **v4.0.490 (2026-07-16)**. It wraps the
  **`rough-stuff/rough-notation`** library — which is **MIT (verified via GitHub licence API)**, last
  pushed 2024-03-18 (mature/stable, not actively developed). **This is the one thing here we can adopt
  directly and legally**, bypassing Remotion entirely: hand-drawn **underline / circle / box / highlight /
  strike-through / bracket** annotations, drawn as SVG paths. Honest framing: *rough-notation is not new
  — it is 5 years old*. What is new is Remotion validating it as video craft in 2026. Ours to take.
- **`@remotion/effects`** grew a large effect set across v4.0.481–490: gradient, progressive blur,
  **progressive pixelate** (v4.0.490), corner pin, light trail, checkerboard, emboss, **gridlines**, zoom
  blur. **Concept only** — all are shader/compositing recipes we can reproduce in CSS/SVG filters. Note
  the honest sting: *gridlines* and *gradient* shipping as first-class effects is upstream converging on
  exactly the background family the user independently asked for.
- **`interpolate()` `output: "perceptual-scale"`** (v4.0.490) — interpolating scale in *perceptual* rather
  than linear space so growth reads evenly to the eye. **The single best pure-craft idea in this batch**;
  ~10 lines in our GSAP layer, applies to every scale-in we already ship.
- **Spring easing / easing presets / keyframe inspector** (v4.0.475–486) — their Studio is becoming an
  interactive editor. **Irrelevant to us** (we are agent-driven, not GUI-driven) and we **already ported
  Remotion's damped-spring solver into GSAP CustomEase** (`native_composer.py:2906-2917`). No gap.

**Licence statement, plainly:** Remotion's own terms make it **not free for companies**; from Remotion 5.0
licence-key telemetry is mandatory for "Remotion for Automators". SEOSONA renders videos as a company →
we would owe a Company License. **We therefore adopt no Remotion code, no Remotion package, and no
Remotion dependency — only ideas we implement ourselves.** (`WHYBETTER_nexu.md:180` already flagged that
html-video's Remotion adapter is the gated path; this is the licence reason to keep it gated forever.)

---

## (b) THE STYLE LIBRARY — ranked, spec-level

**Grounded on the real script.** I read `D:\SRT\SEOSONA bootcamp 2026-2.srt` — **79 cues, ends 00:02:37**.
Verified beat map (this is from the actual file, not inferred):

| Cues | Beat | Emotional charge |
|---|---|---|
| 1–12 | Market context — AI everywhere; lướt FB/TikTok/YouTube; "10 tin thì 9 tin nói về AI" | Rising noise |
| 13–19 | **FOMO → mệt mỏi**; sợ bị bỏ lại / lạc hậu / thay thế; can't find how to apply AI | ⬇ **Trough** |
| 20–21 | "có ba cái nhóm người dùng AI thế này" — the setup | Turn |
| 22–29 | Type 1 — **thợ săn prompt** | Wry |
| 30–35 | Type 2 — **tool chaser** ("AI là công cụ") | Wry |
| 36–45 | Type 3 — **chiến thần FOMO** (buys everything, ships nothing) | Wry → flat |
| 46–51 | Synthesis — all three share one root: **coi AI là công cụ**, không hiểu bản chất | Cold clarity |
| 52–57 | **"trở thành cu li của AI"** — mệt mỏi hơn, bận rộn hơn, lo lắng hơn | ⬇⬇ **Deepest trough** |
| 58–63 | Personal turn — "mình đã trải qua cả ba", đã tìm được con đường đúng | ⬆ Lift |
| 64–68 | Promise — không còn FOMO / chạy theo prompt / tool / công nghệ | ⬆ |
| 69–79 | **CTA** — bootcamp **25/7**, biến AI thành "nhân viên số", click link | ☀ Resolve |

The coordinator's suggested dark ranges (13–17, 52–57, 69–79 light) **check out against the real file**.

**Already built (not repeated):** TH-Chest, TH-TopCard, TH-Inset, Editorial, Kinetic, Broadcast, Stage,
Bignum, News-Stack, Tutorial-Split. (Verified: `nativeRenderAdapter.ts:346` — `VisualMode` = editorial |
kinetic | broadcast | stage | bignum | newsstack | tutorial.)

**Background families:** 🟨 light paper · 🔲 animated grid · 🌫 gradient field · ⬛ dark.
**Provenance for every style below: our own implementation, clean-room.** The only external dependency
proposed anywhere is **rough-notation (MIT)**, in S7.

---

### TIER 1 — ship these; make them permanent factory templates

#### S1 · **BENTO** 🟨 light paper (+ 🔲 grid on cell gaps) · effort **M** · cues **20–45** (+ 69–79 variant)
The modern product-launch grid, and the **best fit in this entire list** for the material.

- **Structure:** a 3-cell asymmetric bento on paper — one tall hero cell (2×1) + two stacked cells. Each
  cell = one user type: `Thợ săn prompt` / `Kẻ săn tool` / `Chiến thần FOMO`. Cell = 24px radius, 1px
  #2A5BDA @ 12% border, white fill, soft neutral shadow. Cell chrome carries a Lucide icon top-left, a
  coral index numeral (`01/02/03`) top-right, a Be Vietnam Pro 600 label, and a one-line trait.
- **The killer move:** **each cell hosts one chroma-keyed 3D render.** 51 renders → this style eats them.
  The magenta key drops out, the render floats on the cell's white, tinted with a #2A5BDA rim.
- **Motion (GSAP timeline):** cells enter on a `stagger: 0.08` with `springSnappy` + `scale 0.94→1`
  (use the **perceptual-scale** trick from Remotion's v4.0.490 note). At cue 46 ("nhìn thì khác nhau…"),
  **all three cells shrink to equal size and snap onto a shared grid** — then at cue 49 ("coi AI là công
  cụ") a coral underline sweeps across all three at once. *The layout itself makes the argument.* That
  transition is the single strongest visual idea in this document.
- **Reuses:** element_maker (cell chrome), Lucide icons, chroma-keyed assets, SFX (soft `tick` per cell).
- **Why "tech" without neon:** density + precision + systematised grid = product-launch modernity.
- **Permanent template: YES.** This generalises to any "N types / N features / N pillars" script — that is
  most of our sales + brand archetypes.

#### S2 · **LATENT-SPACE SCATTER** 🌫 gradient field · effort **M** · cues **46–51**
The most genuinely-AI idea here, and it does **narrative work no other style can**.

- **Structure:** a soft #2A5BDA→white gradient field. ~150 seeded dots. The three user-type clusters sit
  apart… and then the camera pulls back and **all three clusters are revealed to be one cluster** —
  because they share the same embedding: *"coi AI là công cụ"*. A coral convex hull draws around the
  union at cue 49.
- **Motion:** dots drift on seeded value-noise (we already have seeded noise in `native_composer`);
  cluster centroids ease apart 46→48, then the hull draws (**DrawSVG — now free**) 49→51.
- **Reuses:** seeded noise, DrawSVG (newly free), gradient field bg.
- **Why "AI":** it is literally the mental model of an embedding space — legible to the SEO/marketing
  audience as "these people look different but are the same point".
- **Permanent template: YES** (as "cluster/insight reveal").

#### S3 · **COURSE / CURRICULUM** 🟨 light paper · effort **S** · cues **69–79** ← the CTA, the money beat
- **Structure:** a syllabus card — bootcamp title, the **25/7** date as a coral date-chip, then a module
  list (4–5 rows, Lucide icon + module name + a checkbox). Bottom: a progress rail and the CTA button
  ghost pointing at the real link position.
- **Motion:** rows stagger in at 0.12; each checkbox **ticks** as the narration passes it; the date-chip
  does a single `springLand` pop on cue 70 ("hai mươi lăm tháng bảy"). Progress rail fills 0→100% across
  69→79. Final: the CTA pill pulses **twice** (never loops — restraint).
- **Reuses:** timeline + bars from the data-viz family, Lucide icons, SFX (`tick` per check).
- **Effort S** — this is mostly composition of things we already have.
- **Permanent template: YES.** Every bootcamp/webinar/course CTA we will ever make wants this.

#### S4 · **ANNOTATION / MARKER PASS** 🟨 light paper · effort **S** · cues **46–51, 64–68**
Highest craft-per-effort ratio in the document.

- **What:** hand-drawn coral marker annotation over existing type — underline, circle, box, strike-through,
  bracket. **Not a scene — a modifier that upgrades every text-bearing style we already own.**
- **The moment it earns:** cue 49 `coi AI là công cụ` gets **circled**; cues 67–68 strike-through
  `chạy theo prompt` / `chạy theo công cụ` / `chạy theo công nghệ` one by one. That is exactly the
  gesture the script is performing.
- **Motion:** stroke-dashoffset draw-on, seeded roughness so it reads hand-made. **DrawSVG is now free** —
  and our `svg_draw_on.py` stand-in already solved the seek problem the hard way, so either path works.
- **Provenance:** **`rough-stuff/rough-notation` — MIT, verified.** The *only* external dep proposed here.
  Its algorithm (rough SVG path generation) is also small enough to reimplement if we want zero deps.
  Remotion shipping `@remotion/rough-notation` on 2026-07-16 is what surfaced it; we take the MIT upstream,
  not their wrapper.
- **Permanent template: YES — as a modifier layer, not a mode.**

#### S5 · **PHONE-FEED / DEVICE-IN-FRAME** 🟨 light paper · effort **S/M** · cues **10–12**
- **Structure:** cue 10 literally says *"lướt facebook tiktok youtube"* and cue 12 *"mười tin thì hết chín
  tin nói về AI"*. Show it: a phone frame (thin neutral bezel, no vendor logo), a feed of generic post
  cards scrolling past, **9 of every 10 cards flash a coral "AI" chip**. Cue 12 freezes the scroll and the
  9 coral chips fly out into a 3×3 grid.
- **Motion:** continuous scroll (seek-safe: position = f(t), not a CSS loop), freeze + fly-out on cue 12.
- **Reuses:** element_maker cards, Lucide icons, SFX (scroll whoosh, `tick`s).
- **Brand-safety note:** **no vendor logos, no vendor brand names on screen** — generic feed cards only.
  Grep-zero third-party brands, per standing rule. The narration may say the platform names; the frame
  must not draw their marks.
- **Permanent template: YES** (as "social proof / noise" — recurring in our sales archetype).

#### S6 · **ANIMATED GRID + GRADIENT-FIELD BACKGROUND FAMILY** 🔲🌫 · effort **S** · **global**
Not a scene — **the substrate**, and the user asked for it by name.

- **Four backgrounds, one system:** (1) **paper** — flat warm white; (2) **animated grid** — 1px #2A5BDA
  @ 6–10% lines, slow parallax drift, occasional cell highlight; (3) **gradient field** — a slow two-stop
  #2A5BDA→paper mesh; (4) **dark** — #0E1220-ish ink with the grid at 14% and coral as the only accent.
- **Why this is the highest-leverage S in the doc:** it makes **every existing mode** feel new for ~a day
  of work, and it is the honest answer to "more tech" — a moving grid under our current Editorial card is
  *instantly* more technological with zero brand risk.
- **Where a grid/gradient beats BOTH flat light and flat dark:** cues **1–12** (rising noise — flat light
  is inert, dark is too early and would spend the tonal budget before the trough), cues **30–35** (tool
  churn — the drift IS the churn), and cues **58–63** (the lift — a gradient *warming* from ink back to
  paper is the transition itself; a hard cut light→dark→light would read as a mistake). Gradient is how
  you **travel** between light and dark without a jump cut. That is its real job.
- **Permanent template: YES — as a background token set, wired into brand_kit.**

---

### TIER 2 — good, ship after Tier 1

#### S7 · **HUD / TELEMETRY** ⬛ dark · effort **M** · cues **52–57** ("cu li của AI")
Re-ranked **upward** now that dark is allowed — this style *needs* ink and was being contorted before.
- Ink field + 14% grid. Corner tick-marks, a thin coral scan line, small telemetry readouts
  (`LOAD 98%` `TASKS ∞` `REST 0h`) counting **the wrong way** — the machine is fine, the human is redlining.
  Reuses **ring** + **linechart** from the data-viz family (ring at 98%, coral). Cue 57 ("lo lắng hơn"):
  every readout redlines at once, then hard cut to black for 6 frames.
- **Why it earns dark:** this is the one beat about *being consumed by the machine*. The tonal shift is the
  point, and it is followed immediately by the lift (58) — so the dark is paid back within 2 seconds.
- Permanent template: **YES** (as "the trough" — every problem-agitate-solve script has one).

#### S8 · **PROMPT → OUTPUT PANES** 🟨 light paper · effort **S/M** · cues **22–29**
Left pane: a prompt card, mono-ish text, coral caret typing. Right pane: an output card. The joke the
script is making: the hunter collects prompt after prompt (cards stack up, 6 deep, `stagger 0.06`) and
**the right pane never changes**. Reuses the terminal-typing recipe the director stage already has.
Permanent template: **YES** (AI-explainer staple).

#### S9 · **MODEL CARD / EMPLOYEE CARD** 🟨 light paper · effort **S** · cues **72–74**
Cue 73's *"nhân viên **số**"* (ASR wrote "xấu") is begging for this: an **HR-card / model-card hybrid** —
avatar slot (a chroma-keyed 3D render), name `AI`, role `Nhân viên số`, then spec rows: `Giờ làm: 24/7`,
`Nghỉ phép: 0`, `Chi phí: —`. Rows stamp in. It renders the promise literally, and it is *the* AI-native
UI idiom (model cards) repurposed as brand.
Permanent template: **YES**.

#### S10 · **SPLIT-COMPARE (before → after)** 🟨 light + 🌫 · effort **S** · cues **61–68**
Vertical split, coral divider that **wipes** left→right. Left = ink-tinted "chạy theo" chaos; right =
paper-clean "con đường đúng". The divider wipe carries the tonal transition (dark→light) *inside one
scene*. Reuses S6's gradient. Permanent template: **YES**.

#### S11 · **STAT-CARD STACK / DASHBOARD** 🟨 light paper · effort **S** · cues **12, 40–45**
A 2×2 of stat cards, each with a small data-viz (donut/bars/linechart — all already built), staggering in.
Serves cue 12 (`9/10`) and 41–45 (`tool nào cũng mua… nhưng không ra kết quả` → three cards at 100%, the
fourth — `Kết quả` — at 0%). Almost free given the data-viz family exists.
Permanent template: **YES**.

#### S12 · **NODE-GRAPH / AGENT-GRAPH** 🌫 gradient field · effort **M** · cues **30–35, 72–74**
Force-directed nodes + edges. **Two uses, one style:** cues 30–35 = the tool chaser's graph is a *hairball*
(user at centre, 12 tools, no structure); cues 72–74 = the same graph **re-organises into a clean tree**
(user → AI employee → 3 outcomes). Same component, opposite message.
- **Provenance:** hand-roll a ~40-line force sim (seeded, deterministic, seek-safe — `position = f(t)` from
  a pre-solved layout, **not** a live physics loop, which would break per-frame seek). `d3-force` (**ISC**,
  verified) is available as a fallback but a pre-solved layout is better for us — solve once at build time,
  interpolate at render time. Permanent template: **YES**.

---

### TIER 3 — real but optional; build only if the beat asks

| # | Style | Bg | Effort | Cues | Note |
|---|---|---|---|---|---|
| S13 | **Code / terminal** ⬛ | dark | S | 30–35 | We have terminal typing already. Use **sparingly** — it is the laziest "tech" signal and risks reading generic. |
| S14 | **Timeline / roadmap** 🟨 | light | S | 58–63 | Reuses the built `timeline` component. The "mình đã trải qua cả 3 giai đoạn" beat. Solid, unglamorous. |
| S15 | **Kinetic pull-quote** 🌫 | gradient | S | 49, 53 | A variant of built Kinetic, not a new mode. Only worth it for cue 53 (`cu li của AI`). |
| S16 | **Scan / measure overlay** 🔲 | grid | S/M | 22–45 | A *modifier* over the 3D renders — calipers, bounding box, a spec label. Cheap way to make the renders feel analysed rather than decorative. |
| S17 | **Isometric / schematic blueprint** 🔲 | grid | **L** | 72–74 | Beautiful, and genuinely on-brand (blueprint = blue lines on paper). But **L** — hand-authored iso projection. Defer. |
| S18 | **Cut-paper / editorial poster** 🟨 | light | M | 1–9 | Layered paper with soft shadows. Gorgeous, on-brand, but it is a *magazine* signal, not a tech signal — it fights the brief. |

### REJECTED from the style list (fail-honest — not padding the count)

- **Wireframe / 3D mesh** — needs WebGL/Three.js. Off our 2D HTML/GSAP substrate, `mint-threejs` already
  SKIPped on exactly these grounds, and a mesh on light paper without glow reads as *grey spaghetti*.
  The idea's real value is already delivered by S12 (node-graph) at a fraction of the cost.
- **Dataflow pipes** — animated pipes/particles between stages. Honest reason: it is S12 with worse
  legibility, and particle flow is a **seek-safety hazard** (stateful). Not worth it.
- **Attention / token-flow heatmap** — I wanted this one (it is maximally "AI"), but the audience is
  SEO/marketing, not ML. A QKV attention matrix does not communicate to them; it decorates. S2
  (latent-space) delivers the AI-native feeling *and* is legible. Cutting this is the honest call.
- **Glassmorphism / frosted panels** — reads dated in 2026 and muddies the palette.

### Compose into ONE film vs. want their own film

- **Compose into the 2:40 (coherent):** S1 Bento, S2 Latent, S3 Course, S4 Annotation, S5 Phone-feed,
  S6 backgrounds, S7 HUD, S8 Prompt-panes, S9 Model-card, S10 Split, S11 Stat-stack. These share the
  paper/grid substrate and one type system — they cut together.
- **Want a film of their own:** **S12 Node-graph** (needs 8–10s of screen time to read; forcing it into a
  3s beat wastes it), **S17 Isometric** (its own visual world), **S13 Terminal** (a dev-audience film).
- **Hard limit — say this out loud:** a 2:40 film should use **6–8 styles, not 18**. Variety comes from
  *sequencing* + the background family, not from cramming. More than ~8 and the film reads as a showreel,
  not an argument. **Build the library; ration it per film.**

---

## (c) Light ↔ dark distribution plan — mapped to the real 79 cues

**Target ratio: ~80% light / ~8% gradient-transitional / ~12% dark.** Justification: the script has
exactly **two** genuine troughs (13–19, 52–57) and one cold-clarity beat (46–51). Dark is a *rhetorical
device* here, not a look — it should cost something. ~12% ≈ **19 seconds of a 157-second film**, split
across two separated pockets. Below ~8% the dark reads as an accident; above ~20% we contradict
"quá nhiều nền tối thì không nên" and the CTA loses its lift.

**Rule: light = clarity/answer, dark = problem/pressure. Never cluster the dark.**

| Cues | Time | Bg family | Tone | Why |
|---|---|---|---|---|
| 1–9 | 0:00–0:13 | 🔲 **animated grid** | Neutral-bright | Rising noise. Grid drift = the market humming. Flat light would be inert. |
| 10–12 | 0:15–0:20 | 🟨 light | Bright | Phone-feed (S5). Stays light — the noise is *outside*, not yet internal. |
| **13–19** | **0:20–0:36** | **🌫 gradient → ⬛ dark** | ⬇ **DARK #1 (~10s)** | The FOMO trough. `càng bị phomo → càng mệt mỏi → sợ bị bỏ lại`. **Do not hard-cut** — gradient-dip from paper into ink across cue 13, sit dark 14–17, gradient back up on 18–19. |
| 20–21 | 0:37–0:41 | 🟨 light | ☀ **Reset** | "có ba nhóm người" — the turn. Snap back to paper. The relief *is* the beat. |
| 22–29 | 0:41–0:56 | 🟨 light + 🔲 | Bright | Type 1 (S8 Prompt-panes / S1 Bento cell 1). |
| 30–35 | 0:56–1:07 | 🌫 **gradient field** | Bright, drifting | Type 2, tool churn. The drift IS the churn. Gradient beats both flat options here. |
| 36–45 | 1:07–1:26 | 🟨 light + 🔲 | Bright → cooling | Type 3 (S1 Bento cell 3 / S11 Stat-stack). Let the grid creep up in opacity 40→45 as the futility lands. |
| 46–51 | 1:28–1:40 | 🌫 gradient field | **Cold clarity** (NOT dark) | S2 Latent-space + S4 circle-annotation on `coi AI là công cụ`. **Deliberately not dark** — this is the *insight*, and insight is light. Holding light here is what makes 52 hit. |
| **52–57** | **1:40–1:54** | ⬛ **dark** | ⬇⬇ **DARK #2 (~13s) — the deepest** | `trở thành cu li của AI` + `mệt mỏi hơn, bận rộn hơn, lo lắng hơn`. S7 HUD/telemetry. This is the film's floor. Hard cut to black on 57 for ~6 frames. |
| 58–63 | 1:54–2:05 | 🌫 **gradient ink→paper** | ⬆ **The climb** | The personal turn. **The gradient warming back to paper across ~11s is the single most important transition in the film** — do not cut, *dissolve*. S10 Split-compare or S14 Timeline. |
| 64–68 | 2:06–2:16 | 🟨 light | ⬆ Bright | The promise. S4 strike-throughs on `prompt / công cụ / công nghệ`. |
| **69–79** | **2:16–2:40** | 🟨 **light paper, brightest** | ☀☀ **Resolve** | CTA. S3 Course + S9 Model-card. **Zero dark. Zero grid.** Highest key of the whole film — the CTA must feel like daylight after the tunnel. |

**Totals (verified against the SRT timecodes):** dark ≈ 10s + 13s ≈ **23s ≈ 14.6%**; gradient-transitional
≈ 20s ≈ 13%; light ≈ **72%** with the two brightest stretches at the reset (20–21) and the CTA (69–79).
That is slightly darker than the 80/12 target — **trim dark #1 to cues 14–17 (~7s) to land at ~12%.**
I'd ship 12%.

**The arc does narrative work:** bright noise → *dark (FOMO)* → bright reset → bright analysis → **light
insight** → *deepest dark (cu li)* → gradient climb → **brightest CTA**. Two dark pockets, 60 seconds
apart, each ≤13s, each resolved upward within 2 seconds. Light is unambiguously home.

---

## (d) The light-only vs "tech/AI look" tension — honest note

**The tension is now mostly dissolved**, and the user dissolved it themselves. Their instinct — *"technology
có nhiều style, nhiều màu tối sáng khác nhau"* — is correct and is worth recording as the finding.

**Original tension:** the default "AI/tech" grammar in 2026 is dark + neon + glow. Locked to light + 2
colours, we were reaching for a vocabulary we'd banned, so "more tech" kept collapsing into "more editorial".

**What actually resolves it — three things, in order of power:**

1. **Density and precision, not luminance.** What makes a frame read "technological" is *information
   architecture*: tight grids, small type in a second weight, index numerals, tick marks, units, readouts,
   consistent 8px rhythm. **Neon is what people reach for when they don't have density.** We have
   element_maker, 95 icons and a data-viz family — we can afford density. Bento (S1) is this thesis.
2. **The light↔dark axis as a rationed narrative tool** (§c) — not a look, a *cost*. Dark that costs
   something reads as intent; dark everywhere reads as a template.
3. **The gradient/grid mid-ground** (S6) — the user's own suggestion and the real unlock. It is the
   *travel* between the two poles. Most "tech" frames aren't flat black or flat white anyway; they're a
   field with structure in it.

**The honest remaining constraint:** with 2 colours we cannot do categorical data-viz beyond 2 series (+
neutrals). That is a real limit and we should design around it (sequential blue ramps, coral as the single
accent = "the one that matters") rather than quietly smuggling in a third hue. **Coral scarcity is the
brand's best asset** — in a light frame with one coral element, the eye goes exactly where we point it.
Neon can't buy that.

**One warning:** the biggest threat to a "modern" read is **not** the colour lock — it's **type-only
frames**. 8 of our 10 built modes are text-on-background. Bento/Latent/HUD/Model-card matter because they
put *structure* on screen. That, not palette, is the actual gap.

---

## (e) REJECT list — upstream things we should deliberately NOT take

| Reject | Why |
|---|---|
| **Any Remotion package or code** (incl. `@remotion/rough-notation`, `@remotion/effects`) | **Not free for companies** — Company License; from v5.0 licence-key telemetry mandatory for Automators. Take the **MIT rough-notation upstream** directly instead; reimplement effects ourselves. |
| **html-video's `adapter-hyperframes` `recordVideo` recorder** | Determinism regression vs our per-frame seek. Verdict unchanged from `WHYBETTER_nexu.md:180`. |
| **bachdyon/video-automator-skills code** (incl. the new overlay-preparer + meme-search skills) | **PolyForm Noncommercial 1.0.0** — verified verbatim. Craft reference only, forever. |
| **Three.js / mesh / WebGL styles** (`mint-threejs`, MIT) | Off-substrate; needs a renderer we don't have; the payoff is delivered by S12 at 1/10 the cost. *Correct our record: it IS MIT — SKIP on substrate grounds, not licence.* |
| **Bento React component libs** (Magic UI, animata, React Bits) | We hand-author HTML/CSS/GSAP; these are React/Tailwind component kits. **Bento is a layout pattern, not a dependency** — there is nothing to adopt. Build it. |
| **Remotion Studio / interactive-editor direction** | We are agent-driven. A GUI keyframe editor is the opposite of our thesis. |
| **Dark-dominant "AI" aesthetics generally** | Contradicts the standing rule *and* the user's instinct. Dark is a rationed device (§c), never the default. |
| **Particle/physics-loop backgrounds** | Stateful → breaks per-frame seek. Any motion must be `f(t)`. |

---

## (f) Honest notes / limits

- **Verified vs inferred.** Verified: every date, licence and version in §(a) (GitHub API + live docs,
  2026-07-17); the GSAP free-for-commercial terms; rough-notation MIT; d3-force ISC; the 79-cue SRT beat
  map (read from `D:\SRT\SEOSONA bootcamp 2026-2.srt`); the 7 built `VisualMode`s
  (`nativeRenderAdapter.ts:346`). **Inferred (my design judgement, not fact):** every effort estimate; the
  ranking; the 80/12 ratio; which cues "deserve" dark.
- **No delta invented.** nexu/html-video, Auto-Create-Video, huytranvan, tailwindcss-motion → **no change**.
  Said so plainly rather than manufacturing news.
- **Repo record correction:** `REPO_BATCH2_TRIAGE.md:43` lists mint-threejs-skills as unlicensed. It is
  **MIT**. Verdict unchanged, reason corrected.
- **Not checked:** I did not clone anything. Remotion's effect internals were read from release notes +
  docs, not source (deliberate — reading their source is how craft becomes contamination).
- **The SRT display-text blocker (§0.5) is the highest-priority item in this doc that isn't a style.** It is
  cheap and it gates S1/S4/S8/S15.
- **Scope honesty:** I did not touch `store/` or `scripts/` (another agent is rebuilding there). Read-only
  throughout. This file is the only artifact written.
- **Grep-zero third-party brands:** no vendor mark appears in any proposed on-screen artifact. S5's feed
  cards are generic by design (§S5).

**File:** `docs/v2_phase0/UPSTREAM_REFRESH_2026-07.md` (this file). Legacy docs folder only; nothing in the
V2 repo touched.
