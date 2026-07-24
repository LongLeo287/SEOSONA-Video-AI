# WHY are bachdyon/video-automator-skills videos BETTER than our V2? — Quality lens

**Date:** 2026-07-16  **Author:** SEOSONA (legacy analysis; does NOT touch `seosona-video-os`)
**Sources analysed (fresh this pass, honest provenance):**
- `https://github.com/bachdyon/video-automator-skills` README + raw `SKILL.md` files fetched OK for:
  `video-visual-aesthetics`, `shot-coverage-planner`, `subtitle-punch-tag-shortform`,
  `video-render-plan-builder`. (Direct raw-file evidence — quoted values below are theirs.)
- `https://vas.bachdyon.com/skills` — still **HTTP 403 bot-blocked** (stated honestly, not fabricated).
- Prior in-repo craft docs cross-checked: `docs/v2_phase0/BACHDYON_REFERENCE_ANALYSIS.md`,
  `SKILL_TEMPLATE_ANALYSIS.md`, `TALKING_HEAD_CRAFT_STUDY.md`.

**License (re-verified):** **PolyForm Noncommercial 1.0.0 → REFERENCE ONLY.** Learn the technique, write
fresh prose against our own stack. Do **not** vendor their code, skills, brand, or toolchain (Remotion /
Gemini / OpenAI / fal / HeyGen — all divergent from our keyless-local doctrine).

**One inference flagged up front:** their render engine is **Remotion (React)**, confirmed in the README
and in `video-render-plan-builder` ("a data contract consumed directly by Remotion — no intermediate
FFmpeg/ImageMagick directives"). The exact React composition components are not published, so specific
easing curves / component internals below are **inferred** from the visual-aesthetics rules + the render-
plan schema, and I say so where it matters.

---

## TL;DR — top 5 reasons their output is better, each mapped to a V2 fix

| # | Why theirs looks/feels better (evidence) | The V2 gap it exposes | Concrete V2 improvement (our stack) |
|---|---|---|---|
| **1** | **LLM decides content at every stage** — creative-planner assigns each scene a *role* (hook/explain/contrast/proof/CTA); punch-caption keyword is chosen by *"LLM semantic reasoning, not hardcoded keyword rules"*; coverage says *"the agent, not heuristics, makes final selections."* | Our auto path's LLM is a **SEAM, not wired** → deterministic fallback picks **filler words ("ANH/ĐỂ")** and generic layouts. This is the biggest single quality delta. | **Wire the LLM path.** Feed the PhoWhisper word-transcript to an LLM that returns per-scene role + the one keyword to punch + which beats need a card/cutaway. Fall back to deterministic only on LLM failure — never as the default. Add a stop-word/filler blocklist so the fallback never surfaces "anh/để/thì". |
| **2** | **A real per-frame animation engine (Remotion).** Motion is *deterministic, frame-driven* (`slow_push_in`, `animation_in/out`, `transition: soft_cut/fade_slide`), art-directed to the narrative — *"one or two memorable motion moments over many scattered fades."* | Our v1 motion = **ffmpeg fades/slides only**; kinetic frames are **static-simplified (not real animation)**. Overlays pop in flat. | Keep Playwright→PNG, but make it **per-frame**: render N frames of an HTML/CSS keyframe timeline (transform/opacity tweens, spring/ease-out entrances) instead of one static PNG, then ffmpeg-concat. We already prove this pattern in `svg_draw_on.py` (Playwright seek → per-frame). Port that to overlay/card entrances = real motion without Remotion. |
| **3** | **B-roll matched to speech via a semantic asset index + coverage planner.** Explicit gap→strategy table (see below), min-clip **0.8s**, anti-repetition (no two adjacent clips from same asset, reuse cap 3), semantic-relevance-first. | Our auto path has **NO auto b-roll insertion** and no owned-footage index — talking-head just holds on the speaker. | Build a **local semantic footage index** (rembg/CLIP-class embeddings + SQLite, content-hash idempotent — keyless) and a **coverage decider** that ports their gap table. Cut to a matched clip on long holds; hold/Ken-Burns/slowdown otherwise. |
| **4** | **Pacing discipline as hard numbers.** Gap ≤0.5s=keep · 0.5–1.5s=slowdown(0.85–1.0x) · 1.5–4s=cutaway · >4s=2–4 cutaways; **slowdown floor 0.65x**; target cutaway **1.5–3s**; sub-clips **temporally contiguous, sum == scene duration.** This rhythm is why it never drags or flickers. | Our auto path has **limited transitions** and no rhythm model — cuts land on wall-clock, not speech. | Port the gap-table + min-durations into our autocut/EDL pass (`talking_head_autocut.py`). Anchor every cut to a **word boundary** from PhoWhisper (we already have word-level timing). Enforce the 0.8s floor and contiguity check. |
| **5** | **Typed render-plan data contract** (`render_plan.toml`: per-clip `motion/transition/fit/crop_anchor/speed`, subtitle+overlay `animation_in/out`, audio tracks with **ducking flags**). Every stage is debuggable + re-renderable; the renderer just executes intent. | Our native renderer mixes decision + draw; caption segmentation is **raw word-pairs**; music/SFX **not in the auto footage path**. | Adopt a typed `ProductionPlan` between planner and `native_composer` (motion/transition/duck per clip). Replace raw word-pair captions with **~7–8-word breath-segments** + one LLM-chosen punch keyword. Wire the **existing** BGM sourcer + SFX library + ducking (already built in legacy `native_composer`) into the auto path — cheap win. |

---

## 1. What their PIPELINE does that ours doesn't (idea→…→publish)

Their pipeline is **LLM-in-the-loop at every creative decision** and **artifact-passing** (typed
TOML/JSON between stages), not one monolithic render call:

```
job workspace → reference→Design Spec (VDS) → creative_plan.toml (per-scene ROLE + intent + mood)
  → [voiceover-approval GATE] → voice + word-level transcript
  → asset semantic-extract → semantic-asset-mapper (transcript/scene → best clip)
  → shot-coverage-planner (fill gaps: cutaway/hold/kenburns/slowdown, rhythm rules)
  → render_plan.toml (motion/transition/overlay/audio-duck per clip) → Remotion render → QA audit
```

**Where the quality actually comes from (ranked):**
1. **Content intelligence** — an LLM assigns scene roles, picks the punch keyword by *meaning*, and
   chooses/【or rejects】b-roll by semantic relevance. This is the dominant driver of "feels produced."
2. **Real motion** — Remotion per-frame animation with art-directed entrances/transitions.
3. **B-roll matched to speech** — the semantic index + coverage planner cut away to *relevant* footage
   on holds, with anti-repetition and a pacing model.
4. **Caption craft** — 7–8-word breath-segments with an LLM-selected uppercase "punch" line revealed
   word-by-word on Whisper timestamps.
5. **Typed contract + QA gate** — every stage re-renderable; a quality-auditor checks safe-area/readability.

Ours today (per baseline): footage → real PhoWhisper ASR → **deterministic** content/keyword/card plan
(the LLM path unwired) → native render (Playwright PNG + ASS + ffmpeg). The *rendering* is solid; the
**deciding** is where we lose.

## 2. WHY the finished videos specifically look/feel better — ranked

1. **They never show a filler word.** LLM keyword selection means the on-screen punch word is always the
   *conceptual core*; our deterministic fallback surfaces "ANH/ĐỂ". This single thing makes a reel read
   as amateur vs authored, independent of any visual polish.
2. **Things actually move.** Real per-frame entrances/pushes/transitions (Remotion) vs our static-
   simplified kinetic + flat fades. Motion that's *timed to the voiceover* reads as premium.
3. **The picture changes when the voice makes a new point.** Semantic b-roll cutaways on holds keep the
   eye engaged; a static talking-head hold for 6s feels flat by comparison.
4. **The pacing has a heartbeat.** The gap→strategy table + 0.8s floor + word-anchored cuts produce a
   rhythm; wall-clock cuts don't.
5. **Captions breathe.** 7–8-word segments + one punch keyword revealed per word-timestamp vs raw word-
   pairs that strobe.

**Honest caveat on sound:** their render plan carries voice+music tracks with **ducking flags**, but
there is **no dedicated sound-design skill** in the catalogue — sound is a config field, not a craft
strength. This is an area where we are **not** actually behind (see §5).

## 3. What is TRANSFERABLE to V2 (technique, not code — it's noncommercial)

- **Wire the LLM content-director** (our biggest lever). Prompt an LLM with the word-transcript → returns
  `{scene_role, punch_keyword, needs_card, needs_cutaway}` per beat. Deterministic only as failure
  fallback + a filler-word blocklist. Against our stack: reuse the existing `llm_engine` cascade.
- **Per-frame HTML animation** via Playwright *seek* (already proven in `svg_draw_on.py`): render a CSS
  keyframe timeline frame-by-frame → ffmpeg concat. Gives real entrances/pushes without Remotion.
- **Local semantic footage index**: rembg/CLIP embeddings + SQLite + content-hash idempotency (keyless).
- **Coverage decider**: port their gap→strategy table + min-clip 0.8s + anti-repetition into our autocut.
- **7–8-word breath-segment captions** + LLM punch keyword, revealed on PhoWhisper word timings (replace
  raw word-pairs). We already have the word timestamps and ASS pipeline.
- **Typed `ProductionPlan` contract** (motion/transition/duck per clip) between planner and
  `native_composer`, with stale-invalidation (extends our KeepVoice partial re-render).

## 4. What THEY have that we STRUCTURALLY lack (whole capabilities)

**#1 — an LLM shot-director that is actually WIRED end-to-end.** Not a model call bolted on; the *entire*
pipeline defers creative decisions (scene role, keyword, b-roll choice, coverage strategy) to LLM
reasoning with typed I/O. Our equivalent exists as a **seam** and falls back to heuristics. **This is the
single biggest capability gap** — it is upstream of everything else, and it is why our output picks filler
words and static layouts even though our renderer is good.

**#2 — a real per-frame animation engine (Remotion).** We have a static-PNG renderer; we lack a motion
timeline. (Closable via the Playwright-seek per-frame technique — a technique gap, not a doctrine gap.)

**#3 — a reusable semantic asset/footage index.** We fetch a *new* photo per scene (`image_sourcer`) but
have no idempotent index of *owned* footage to cut b-roll from.

## 5. Honest verdict — are they actually better, or just different?

**Better, on the axes that decide perceived quality of a finished short** — content intelligence, real
motion, matched b-roll, pacing rhythm. These are real, not cosmetic. Being non-defensive: our auto path's
deterministic filler-word selection is a genuine quality defect, and our "kinetic" motion being static-
simplified is a genuine capability gap.

**Where we are EVEN or AHEAD:**
- **Keyless / local / free** vs their paid cloud stack (Gemini + OpenAI + fal + HeyGen). Sustainability +
  privacy + zero per-video cost. Strategic advantage, not quality — but real.
- **Voice:** OmniVoice local GPU VN clone is plausibly **better VN narration** than their cloud/unofficial
  TTS, and it's ours.
- **Text-behind-speaker depth:** our rembg occlusion composites captions/keywords *behind* the speaker
  (premium depth). Their `overlay-subject-placement` merely *avoids* the subject — we do something they
  apparently don't.
- **Sound design:** we already have a BGM sourcer (mood-matched, CC-attributed) + curated SFX library +
  per-component ducking in legacy `native_composer`. Their sound is a bare config field. Once we **wire**
  ours into the auto path we're ahead here.
- **Brand/typography discipline & QA-honesty:** Be Vietnam Pro + fixed brand palette + fail-honest VERIFY
  gate are on par with their quality-auditor.

**Net:** they are ahead today because their *decisions* are LLM-driven and their *motion* is real. Neither
requires their toolchain to close — both are technique/wiring problems against our existing stack. Close
gap #1 (wire the LLM director) and #2 (per-frame Playwright animation) and the quality delta largely
collapses, while we keep our keyless-local + voice + sound-design advantages.

---

### The single biggest capability gap (one line)
**A wired, end-to-end LLM shot-director** — it decides scene roles, the punch keyword, b-roll cutaways,
and coverage strategy; ours is an unwired seam that falls back to filler-word heuristics. Everything else
(motion engine, asset index, pacing) is downstream of fixing this.

### License note
PolyForm Noncommercial 1.0.0 → **REFERENCE only**. Techniques adapted to our stack; no code/skill/brand/
toolchain vendored. Provenance belongs in `2_KNOWLEDGE/INGESTION_LOG.md`, never on a shipped skill.

### Doc path
`D:\SEOSONA AI\SEOSONA Video\docs\v2_phase0\WHYBETTER_bachdyon.md`
