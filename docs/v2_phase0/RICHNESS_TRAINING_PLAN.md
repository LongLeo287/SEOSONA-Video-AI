# Richness Training Plan — SEOSONA Video AI V2

**Date:** 2026-07-17 · **Status:** research + plan only, nothing built
**Question this answers:** *"tôi thấy các video chưa phong phú… Hiện tại video quá đơn điệu"* — why do theirs feel
rich and ours feel monotone, and what do we train to fix it (how many hours, what exactly).

> Written to the **legacy** docs folder by instruction. Nothing here was written into the V2 repo.

---

## ⚠️⚠️ CORRECTION #2 — **my ALIVE% metric was broken.** R1 is NOT dead. (read this first)

A second agent measured v7 at **53.5% frozen**; I measured **0.8%**. ~50× apart, same artefact. Resolved:

**Nobody measured the wrong file** (`store/promo-v7-procedural/FINAL.mp4` **does not exist** — the only v7 file is
`promo-v7-procedural.mp4`, 24fps, 160.3s; both of us hit it). **It is a definitional artefact, and I reproduced
their number exactly:**

| definition (same file, same 0.5/255 threshold) | frozen% |
|---|---|
| **THEIRS** — 24fps, 64×36 gray | **53.5%** ← reproduced their figure exactly |
| theirs, corrected to 9:16 aspect (36×64) | 43.3% |
| theirs @4fps (isolates *resolution*) | 17.5% |
| mine @24fps (isolates *sample rate*) | 32.9% |
| **MINE** — 4fps, 96×171 gray | **0.8%** |

Adjacent-frame delta is violently sensitive to **sample rate** (at 24fps a step is 42ms — sub-pixel drift
quantises to zero) and **downscale** (64×36 box-averages small motion away; it is also the *wrong aspect* for a
9:16 film, decimating 1920 rows→36, i.e. destroying the vertical motion that dominates a portrait film).
**Neither number should ever have been quoted without its sampling parameters.**

**Then I did the check that settles it — I extracted their frames and looked:**
- **Their claim "t=40/42/44/46 are four indistinguishable frames": FALSE.** Frame-exact extraction shows
  *"3 NHÓM DÙNG AI"* → *"Thợ săn Prompt"* → *"SĂN MUA PROMPT"* → same words scaling up. Different text, size and
  background; mean |Δ| 14–26/255, 92.8% of pixels changing t=42→44. That stretch is highly kinetic.
- **Their claim "9.6s motionless at t=109.4 in s33_bento": CORRECT — and my metric missed it completely.**

**The root cause is mine: adjacent-frame delta measures PIXEL CHURN, not aliveness.** A slow opacity/position
settle on a *completely static layout* produces churn while the viewer sees nothing new. Measuring **novelty**
(each frame vs the frame 2s earlier) instead, per scene:

| scene | dur | churn | **novelty(2s)** | reads |
|---|---|---|---|---|
| `s33_bento` | **10.0s** | 1.20 | **5.50** | **FROZEN** ← they found this; I called it alive |
| `s36_bento` | **9.8s** | 1.17 | **5.17** | **FROZEN** ← *a second one they missed* |
| `s32_statement` | 2.5s | 24.39 | 207.14 | alive |
| all other 24 scenes | — | — | 6.3 – 198 | alive |

**Verdict: both aggregates were wrong; their per-stretch detector was right.**
- Their **53.5%** is inflated ~4× by quantisation (it labels the demonstrably kinetic t=40–46 "frozen").
- My **0.8% / 90.8% alive** is wrong in exactly the way suspected — it is a churn meter. **A metric reporting
  0.0% dead for a film of type cards deserved the suspicion it got, and I should have applied it myself.**
- **The truth: 2 of 41 scenes (~20s of 160s ≈ 12.5%) are perceptually frozen — both `bento`, both ~10s holds.**
  Reference craft (`template_library.md`) puts a comparable card's hold at **4.5–6.5s**. **We hold ~10s — ~2×
  the reference maximum, with no new information.** Real, precise, citable defect.

**So: did the coordinator nearly cut the most important module? No — but I was wrong to cut it outright.**
R1 as I originally wrote it (6h, "all our films are static cards + transition slams") is **still dead** — that
describes the legacy engine. But a **narrow, real R1 survives**: two 10s bento holds with zero novelty.
**R1 returns, rescoped: ~1.5h**, not 6h. See §4.

**Consequence for R0:** the ruler must measure **novelty (2s lag), never adjacent churn**, and must report its
sample rate + scale with every number. `richness_measure.py` has been corrected and carries this warning.
**The coordinator's diagnosis of the shared root cause is exactly right: both my errors were measuring something
and not verifying it was the thing I meant to measure.** R0's own guard against inheriting that flaw: it must be
validated against *frames a human looked at* — which is how this was caught, and is now written into R0's
acceptance test.

---

## ⚠️ CORRECTION #1 (same day, after coordinator challenge)

**My first draft measured the wrong corpus and drew a wrong headline.** My 15-film "OURS" control was entirely
`SEOSONA Video\8_WORKSPACE\*` — the **legacy engine**, dated **2026-06-30 → 2026-07-15**. The **current V2 films
live in the V2 repo** (`seosona-video-os\store\`) and I never measured them. Re-measured with the same ruler:

| film | CONC% | DEAD% | ALIVE% | verdict |
|---|---|---|---|---|
| REF Template (target) | 35.4 | 40.8 | 56.6 | — |
| **legacy OURS (my §3)** | **60.6** | **56.3** | **40.1** | the diagnosis below |
| `promo-v4` | 40.6 | 15.8 | **76.4** | beats ref |
| `promo-v5-kinetic` | **18.3** | 0.0 | **59.7** | beats ref |
| `promo-v6-kinetic` | **17.7** | 0.2 | 55.8 | at target |
| `promo-v6-asset` | 20.2 | 5.2 | **77.5** | beats ref |
| `promo-v7-procedural` | **27.9** | 0.8 | **90.8** | crushes ref |

**CAUSE #1 (static cards + transition slams) is LARGELY fixed in V2** — but see **CORRECTION #2 above: the
ALIVE%/DEAD% columns in this table are churn, not aliveness, and overstate the win.** Re-measured by novelty,
**2 of v7's 41 scenes (both ~10s `bento`) are perceptually frozen.** So R1 is **rescoped to ~1.5h, not cut.**
§3.1 remains true *of the legacy engine* and is retained as the record of how the ruler was built — and of how
it was wrong.

**But the study's value survives, and sharpens.** `promo-v7-procedural` is **90.8% alive** — it out-moves the
reference by a wide margin — and the user still calls it *"quá đơn điệu."* **Therefore the complaint cannot be
about motion. It is entirely about sameness**, and §3.2 (one chassis) is now confirmed on **current V2 output**
with hard evidence, not the 2-video visual inference I had:

> **`promo-v7-procedural`, 41 scenes: `statement` = 22 scenes (53.7%). Longest same-kind run = 9 in a row.
> Only 7 distinct kinds across 41 scenes.** (Sequence read from `store/promo-v7-procedural/work/s*.mp4`.)

Three independent references say *never repeat the same kind 3× in a row*. **We ship a run of 9.** Over half the
film is one archetype. That is the whole complaint, and **Module R2 is now the entire plan.**

**Net effect: the plan shrinks from ≈25.5h to ≈13h**, and targets a defect proven on current output.
See §4 for the corrected costing. §3.6's two "defects" are **legacy artefacts — not live** (see §3.6).

---

## 0. Coverage — examined vs sampled (read this before trusting anything below)

| Folder | Size | What I actually did |
|---|---|---|
| `data\Video Template` | 56 mp4, 285 MB | **Measured all 56** (decoded every file at 2–4 fps). **Looked at frames from 1** (`Agency Agents…`). Name-diffed all 56 vs the prior 54-file study list. |
| `data\video talking heads` | 22 mp4, 93 MB | **Measured all 22.** Viewed **0** frames. Names only. |
| `data\Video Course` | 18 mp4, 15 MB | **Measured all 18.** Viewed **0** frames. Names only. |
| `SKILL TEMPLATE` | 21,715 files, 2.5 GB | Surveyed by ext/size. Prior docs covered the 12 top-level files. Delta (`repos/`, `SKILL AUTO`, `talking-head-video-editor`, 9 unread text files) covered by two delegated agents — see §2. `repos/heygen-com__hyperframes` (1,067 MB) **not** re-read; already adopted. |
| **Ours — LEGACY (control)** | 15 mp4 | **Measured all 15.** Looked at frames from 1 (`agency-agents - SEOSONA.mp4`). **⚠ This is the legacy engine, Jun 30–Jul 15 — NOT current V2.** |
| **Ours — CURRENT V2** | 5 mp4 | **Measured all 5** (added after the correction). Viewed **0** frames. Scene sequence read from `promo-v7-procedural/work/s*.mp4` filenames. |

**Honest gaps:**
- I viewed frames from exactly **2 videos** (one theirs, one legacy-ours). Every *visual* claim in §3.2–§3.4 rests
  on that one pair plus corpus numbers. **See the note below on what that does and does not support.**
- **I viewed 0 frames of current V2 output.** The v7 finding (53.7% one kind, 9-run) is from **scene manifests +
  motion metrics**, not from looking. It is hard data, but nobody has *looked* at v7 in this study.
- Talking-heads and Course: measured, never watched — statistical only.
- I did not read the 1 GB HyperFrames repo.

**On the 2-video basis (asked directly by the coordinator):** the **corpus numbers carry the argument
independently of the viewing, and should be quoted instead of the frames.** The load-bearing claim — *V2 is alive
but repetitive* — now rests on `promo-v7`'s 41-scene manifest (53.7% `statement`, 9-long run, 7 kinds) and its
motion metrics (ALIVE 90.8), **neither of which involves my 2-video viewing at all**. The 6-frame strip was the
*hypothesis generator*, not the evidence; it pointed at the right axis, but it pointed at it in the **wrong
(legacy) engine**. Represent the frames as illustration, the manifests and metrics as proof. **The
"one chassis repeated 6×" phrasing should NOT be presented as a finding about current V2** — it was observed in a
2026-07-03 legacy film. The *current* V2 equivalent is the run-length/kind-share data, which is stronger.

---

## 1. Folder deltas

### 1.1 `data\Video Template` — **content delta ≈ nil; the delta is the lens**
Name-diff vs `8_WORKSPACE/template_study/video_list_54.txt`: **54 → 56. Exactly 2 new files**
(`Agency Agents- Framework tối ưu hóa…`, `NVIDIA đang cho bạn dùng hàng chục model AI…`). Nothing removed.
The old path `D:\SEOSONA AI\Video Template` no longer exists — the corpus **moved** into `data\`.

So: **no meaningful content delta.** The 2026-07-01 craft study already catalogued the archetypes. Re-examining
with the richness lens is where the value was — and it produced §3, including a lucky break: `Agency Agents` is
one of the 2 new files **and we have our own video on the same topic**, giving a true A/B.

### 1.2 `data\Video Course` — **new folder, and it is the outlier that proves the thesis**
18 VN SEO/GEO talking-head shorts, never studied. Statistically they are the **most continuously alive corpus
measured**: `ALIVE 99.3%`, `DEAD 0.0%`, motion concentration only `16.9%`. Never freeze. (Caveat: real camera
footage is *trivially* always-moving — this is not a craft achievement, it's a property of the medium. Its value
is as the **upper bound** on the alive-ness scale, not as a technique to copy.)

### 1.3 `data\video talking heads` — **thin delta**
22 mp4. Statistically unremarkable for our problem (`mean change 27.6`, `still 0.0%` — again, footage). Mixed bag:
some are editing-preset promos, some AI-news shorts. **No delta** on the monotony question beyond confirming that
footage-based engines don't have our problem. Not watched.

### 1.4 `SKILL TEMPLATE` — **large delta, in `repos/` and `SKILL AUTO`**
Prior docs covered only the 12 top-level files. See §2.

---

## 2. SKILL TEMPLATE delta findings

### 2.1 Repos (`SKILL TEMPLATE\repos\`, 19 repos) — 3 were never vetted
| Repo | License | Verdict |
|---|---|---|
| `Orkas-AI__Orkas-VideoStudio` | **MIT** | **ADOPT-CRAFT** — quantified rhythm numbers + a slideshow-risk gate |
| `chanktb__any2video` | **MIT** | **ADOPT-CRAFT (highest value)** — near-twin of our stack (9:16, Be Vietnam Pro, VN, karaoke) |
| `calesthio__OpenMontage` | **AGPL-3.0** | **ADOPT-CRAFT, clean-room only** — richest artifact found; ideas only, zero code |
| `webadderallorg__Recordly` | **AGPL-3.0 + UI-attribution rider** | **SKIP** — craft is cursor-telemetry-bound; we have no cursor |
| `Agent-Field__reels-af` | **Apache-2.0** | ADOPT-CRAFT (moderate) — role→motion policy, hook/payoff duration bias |

**The strongest signal in this whole study is convergence.** Repos with no shared lineage independently landed on
the same rules:

1. **Never repeat 3× in a row** — shot length (OpenMontage `skills/creative/cinematic.md`), shot size
   (OpenMontage `lib/variation_checker.py`, longest-run check), scene type/transition (Orkas
   `packages/skills/video-craft/SKILL.md` §12). *Three independent sources.*
2. **Motion without intent is decoration, and decoration reads as monotone** — OpenMontage `_score_weak_motion`
   ("movement without `shot_intent` = arbitrary"), Orkas ("motion that carries no meaning"), reels-af
   (`src/reel_af/agents/visual.py`: "never a decorative camera move"). *Three sources.* **Richness is not more
   motion — it is motivated motion.**
3. **Text-first density is the slideshow tell** — OpenMontage `_score_typography` (>60% text cards → 4.0/5),
   Orkas ("text crutch"), any2video ("never ship a scene that is only a headline").
4. **A video needs one visual peak** — OpenMontage `hero_moment` (and it must differ in shot size from its
   neighbours); reels-af (hook = the most arresting visual).
5. **Variety comes from re-deriving structure per scene, not from a template pool.**

The two rules that map most directly onto our defect, verbatim:

> **any2video** `render-remotion/SCENE-DESIGN.md`: *"**Within one video, no two scenes share a layout**… **Never
> ship a scene that is only a headline.** … The main element should keep animating for **60–80% of the scene
> duration; a scene that goes fully static reads as frozen.**"*

> **OpenMontage** `skills/creative/cinematic.md`: *"Long (8s) → Medium (5s) → Short (3s) → Short (2s) → LONG
> (10s) → Medium (6s). **Never use the same shot length 3 times in a row** — it creates monotony."*

**any2video also proves the separation empirically**: `flow-movie-pipeline-tour.tsx` and
`…-repodark.tsx` are the *same narration/audio/data re-skinned* — structures stay, every surface changes.
That is exactly the axis we have collapsed (see §3.2).

### 2.2 `SKILL AUTO\Skill B\video-edit-skill-clean\SKILL.md` — 818 lines, ~70 dated rule-verdicts
The single densest craft source in the folder. Net-new highlights:

- **The "3+ distinct hero kinds" rule** — a 7+ beat plan must use ≥3 different hero kinds. *But variety is a
  tiebreaker, not a goal*: "the ceiling comes first. A 10-beat plan with 8 distinct kinds is still wrong."
  **Richness = more distinct kinds at the same beat count, not more beats.**
- **The slideshow diagnosis (4z)** — "No two image takeovers back-to-back… the cut reads as *'and then another
  picture, and then another picture' — it feels random, like a slideshow.*"
- **Per-archetype hold times** (`template_library.md`) — `stat_punch` 1.5–2.5s · `icon` 0.8–2.0s · `bar_chart`
  4.5–6.5s · `network_diagram` 5.5–8.0s. **Same-length beats are themselves a monotony source.**
- **Follow-cam replaces zoom punches (4ag)** — "a hard centre-lock reads robotic; **a soft lagging drift reads
  alive**" (strength 0.7, double box-smooth win=21).
- **Cloudy grid (4an)** — "Grid backgrounds are **cloudy, not uniform**… crisp in patches, fades to nothing
  between them. It reads as a drifting texture, never as graph paper."
- **Global grade as unifier (4aq)** — one grade over speaker + b-roll "so cutaways never look pasted on…
  **tuned to be felt not seen.**"
- **"Boring" diagnosed 5× — and one fix was surprising**: the *music* was boring because of **level, not
  arrangement** (-38 LUFS → -26). Also: *"A rotating/random bed is not branding; one consistent track is"* —
  which **contradicts our md5-rotating `bgm_sourcer`**. Worth a decision, not an assumption.
- **Negative result worth keeping**: text-behind-subject was **built then retired** — "words get bitten in half
  by the head ('PEOP[LE]')." Salvage rule: behind-subject only for text *wider* than the speaker.
- **Their own negative finding**: the codebase has **no inter-beat variation system at all** — `lint_plan.py`
  (555 lines) has *zero* rules against sameness. All their variety is hand-authored in JSON. **Their prose rules
  are enforced by nothing. Ours would be.** That is our opening.

### 2.3 `premium infographic storyboard poster.txt` — the shot-variety delta
> *"Blend cinematic wide shots, medium shots, close-ups, overhead, POV, low-angle, side profiles, reflections,
> macro, tracking… **Avoid repeating similar framing in consecutive panels.**"*
> *"**THE SIGNATURE SHOT** — feature one visually striking perspective."*

A **structurally reserved pattern-break slot**. We have no equivalent: our archetypes are all picked by semantic
fit, so **nothing ever earns a slot purely for novelty**.

### 2.4 No-delta files (stated, not padded)
`huong-dan-chia-se-ver-b-broll.html` (setup guide, near-zero craft) · `Content.txt` · `edit img.txt` ·
`product post.txt` · `Character Design Board.txt` · `agents/openai.yaml` (2 lines) · `video_repos_list.txt`.
**Recordly: no delta.**

---

## 3. Why theirs feels rich and ours feels monotone — ranked, with evidence

I built a metric over decoded frames (`docs/v2_phase0/richness_measure.py`, 96px greyscale, mean abs inter-frame
difference — preserved next to this doc so every number below is reproducible). Medians per corpus:

| corpus | n | mean chg | p90 | p99 | **CONC%** | **DEAD%** | **ALIVE%** | luma | detail |
|---|---|---|---|---|---|---|---|---|---|
| REF Template | 56 | 2.66 | 5.50 | 22.2 | **35.4** | **40.8** | **56.6** | 29 | 28.6 |
| REF Course | 18 | 5.18 | 8.99 | 15.1 | **16.9** | **0.0** | **99.3** | 85 | 94.9 |
| **OURS** | 15 | **3.79** | 7.84 | **56.5** | **60.6** | **56.3** | **40.1** | 226 | **37.1** |

`CONC%` = share of all visual change packed into the busiest 5% of frames. `ALIVE%` = frames with perceptible
but non-slam motion. Higher ALIVE / lower CONC = continuously alive.

### 3.1 CAUSE #1 — **We are a slideshow: static cards + transition slams.** (measured, corpus-wide)
**This is the finding.** It inverts the intuitive hypothesis and kills three plausible fixes before we spend a
minute on them.

- We **move more on average** than the reference (3.79 vs 2.66). *Not a motion-quantity problem.*
- We are **denser** than the reference (detail 37.1 vs 28.6). *Not a density problem — despite our own prior
  diagnosis "density and structure make a frame read technological".* **That diagnosis was wrong.** We already
  out-densify them and still read as monotone.
- Yet we are **visually dead 56.3% of the time** vs their 40.8%, and **60.6% of all our change is packed into 5%
  of frames** (theirs: 35.4%).
- Our p99 is **56.5 vs their 22.2** — whole-screen slams. Their card videos contain **zero hard cuts**
  (verified: `select='gt(scene,0.05)'` returns 0 across thresholds; showinfo confirmed working). They are
  *continuous motion*. We are cards + cuts.

**Monotone = low variance, not low mean.** They hold, then punch, then keep breathing. We drift mildly, freeze,
then slam the whole frame. This is precisely any2video's independently-derived rule: *"the main element should
keep animating for 60–80% of the scene duration; a scene that goes fully static reads as frozen."*
We measured ourselves at **40.1% alive** — below their floor.

### 3.2 CAUSE #2 — **One layout skeleton, reused for every scene.** (visual, n=1 pair — strong but under-sampled)
Comparing 6 evenly-spaced frames of each `Agency Agents` video:

- **Theirs:** 6 frames, **6 different structures** — a bare title; a giant `140+` bignum with a card stack; a
  **full-bleed real GitHub README screenshot** (white, on a dark film); a 2×2 card grid; a different 2×2 with a
  drawn yellow rule; an app mockup.
- **Ours:** 6 frames, **1 structure repeated 6×** with the payload swapped — logo top-left → pill label
  (`HOOK`/`FEATURE`/`BIGNUM`/`TIP`) → 2-line centred title (line 2 coloured) → middle payload → caption chip →
  footer bar. **Title, caption chip and footer sit at identical y in all six.** The archetype changes the middle
  ~35% and nothing else.

**Our archetypes are payload variants inside one immutable chassis.** That is the structural root of "đơn điệu",
and it is exactly what any2video forbids ("no two scenes share a layout") and what they *proved* is separable
(same data, two skins → "structures stay, every surface changes"). We collapsed the axis they kept open.

### 3.3 CAUSE #3 — **No scale contrast, and dead margins.** (visual, n=1 pair)
Their `140+` is ~4× body height and the frame is **filled**. Every title in our six frames is the **same size**,
and the top ~40% / bottom ~25% are empty in most. Their type scale is an instrument; ours is a constant.

### 3.4 CAUSE #4 — **No register break / signature shot.** (visual + structural)
Their frame 3 is a **full-bleed white screenshot on a dark film** — a total register break that resets the eye.
We never leave the card. Nothing in our director can earn a slot for novelty (§2.3).

### 3.5 CAUSE #5 — **Frozen bottom chrome.** (measured — real but secondary; do not overclaim)
Our bottom 18% is **86.1% frozen pixels** (ref: 56.0%) — the permanent footer + caption chip.
**But our overall frozen-pixel share is *lower* than theirs (18.3% vs 22.9%).** So our *pixels* are not more
frozen than theirs; our **time** is. Chrome is dead weight, not the main driver. Ranked last deliberately.

### 3.6 Two defects found in passing — **both are LEGACY artefacts, neither is live** (corrected)
Both came from **one file**: `SEOSONA Video\8_WORKSPACE\agency-agents\agency-agents - SEOSONA.mp4`, mtime
**2026-07-03 09:36** — two weeks before the brand palette was corrected, in the **legacy** repo. It is **not** in
`store\` and **not** among the five films handed to the user. My glob (`8_WORKSPACE/*/* - SEOSONA.mp4`) *could
not* have matched them. **I did not contradict the other agent's measurement — I measured a different, older
corpus and failed to say so.** That was my error, and it is the same error as the R1 miss above.

- **Coral — real in that file, but expected and not news.** Measured: coral-family pixels in **26 of 58 seconds**,
  peak **4.37% at t=48s**, dominant hex **`#E87848`** (≈ legacy coral `#E2724D`), also `#E87040`. Present at
  t≈4–6s (top dash-bar), 16–20s, 31–34s, and 44–56s (CTA/follow button). **But the file predates the palette fix,
  so this is exactly the "true but not news" case.** The other agent's finding of zero coral in the five
  re-rendered films **stands; mine does not challenge it.**
- **Placeholder text — real, seen in a frame, but in the same legacy file.** At **t ≈ 9.7s** (frame n=290 @30fps,
  2nd panel of my 6-frame strip): a Reddit-card block renders *"Prompt to change this title to whatever you
  want"* / *"Prompt to change this body text, the subreddit, username, and vote count to match your content."*
  **Seen in a rendered frame, not inferred from source.** It is the `registry-blocks-are-demos` trap having
  actually shipped — in the **legacy** engine, on 2026-07-03. **Not in the five current films.**

**Real gap worth naming (flagged by the coordinator, not by me):** `store\v6-stage` was **not** in the re-render
batch, so it is expected to still be coral. I did not measure it. **Unverified — someone should.**

---

## 4. The training plan

**"Train" = teaching the system (director + style library + craft rules), not ML fine-tuning.**
I found **no case for fine-tuning.** Every cause in §3 is a *rules-and-structure* problem with a deterministic
fix; a fine-tune would be slower, unverifiable, and would fix none of them. Recommending against it is part of
the deliverable.

**Throughput grounding (my last estimate was wrong by 14× because I assumed sequential rendering):**
20 cores → 5 concurrent renders → **~6–9 min/film wall-clock**; a 41-scene procedural film ≈ 27 min.
So a **20-film regression batch ≈ 4 batches × ~8 min ≈ 35–40 min machine time**, not 3 hours. Every machine-time
number below uses this.

Time is split: **Claude** (building) · **Machine** (rendering, wall-clock, mostly parallel to Claude) · **User**
(deciding/reviewing — the scarce one, minimised deliberately).

### Module R0 — Instrument the metric (build the ruler before the thing it measures)
**Fixes:** nothing directly. **Unlocks:** every acceptance test below. **Learned from:** own measurement.
Promote `docs/v2_phase0/richness_measure.py` (the research prototype) into a real checker: `ALIVE% · DEAD% · CONC% · p99 · deadpx-by-band`, run on the
**shipped mp4**, with the corpus medians of §3 baked in as reference constants.
**Acceptance:** re-running it on the 56 references reproduces the §3 table (±2%). It must measure the artefact,
never the plan.
**Claude 2.5h · Machine ~15min · User 0h**

> **Guard against our recurring failure** (metrics that guard the PLAN not the PIXELS — 3 instances so far):
> R0 decodes the delivered mp4. R1's gate is the *only* plan-level check in this plan, and it is explicitly
> **paired** with R0 measuring the render. A plan-gate alone would be the fourth instance of that failure.

### Module R1 — **RESCOPED: frozen-hold guard (6h → 1.5h)**
**Not cut.** My original R1 ("all films are static cards + slams", 6h) *is* dead — that was the legacy engine.
But CORRECTION #2 found a narrow, real, current defect that my broken metric hid:

**`s33_bento` (10.0s) and `s36_bento` (9.8s) are perceptually frozen** — novelty(2s) = 5.50 / 5.17, i.e. the
viewer sees no new information for ~10 seconds. Reference craft puts a comparable card's hold at **4.5–6.5s**
(`video-edit-skill-clean` `template_library.md`). **We hold ~2× the reference maximum.**
**Fix:** cap any scene's frozen-hold — either shorten the bento hold toward ~5s, or give it progressive reveal
(the cards already stagger in; they then sit still for the remaining ~7s).
**Acceptance:** **no scene has a novelty(2s) < 6 window longer than 2.5s**, measured on the shipped film.
Currently 2 of 41 scenes fail. **Do not use adjacent-frame churn for this** — it is what hid the defect.
**Claude 1.5h · Machine ~15min · User 0h**

### Module R2 — Break the chassis (layout variety) — **now the entire plan**
**Fixes:** CAUSE #2 + #3 — **the only cause still live on current V2 output**, and now backed by hard evidence
rather than my 2-video inference: `promo-v7-procedural` = **53.7% `statement`, a 9-long same-kind run, 7 distinct
kinds / 41 scenes**, in a film that is **90.8% alive**. Alive but repetitive is precisely "đơn điệu".
**Learned from:** any2video ("no two scenes share a layout"; structure-of-the-sentence → shape);
`video-edit-skill-clean` 4ab (3+ distinct kinds); OpenMontage `variation_checker.py` (longest-run check).
Decouple the frozen skeleton: **anchor sets** (title/payload/caption may sit at different y per scene), a
**type-scale ladder** so bignums can run ~4× body, and a **fill target** so scenes stop floating in dead margins.
Then a `spec_lint` variety gate (`4_BRAIN/spec_lint.py` already exists — extend, don't create):
no layout repeats within a film; ≥3 distinct kinds per 7+ beat plan; no same-archetype 3× run.
**Acceptance (measured on the shipped film + its scene manifest):**
1. **Longest same-kind run ≤ 2** (from **9**) — the rule three independent references share.
2. **No single kind > 30% of scenes** (from **53.7%**).
3. **Distinct kinds ≥ 12 on a 41-scene film** (from **7**) — i.e. ≥1 distinct kind per 3.5 scenes.
4. **No two scenes share an (anchor-set × archetype) signature.**
5. **Type-scale ratio max/min ≥ 2.5** per film (CAUSE #3).
6. **R0 regression:** `ALIVE% ≥ 56` and `CONC% ≤ 40` must **not** regress while doing all of the above.
   *(This is the trap: adding layout variety by adding hard cuts would raise CONC and undo the thing that already
   works. Gate both directions.)*
Re-run on `promo-v7-procedural` specifically — it is the worst offender and the best test case.
**Claude 8h · Machine ~40min · User 1h (approve anchor sets — a taste call, genuinely theirs)**

### Module R3 — Signature-shot slot
**Fixes:** CAUSE #4. **Learned from:** `premium infographic storyboard poster.txt` (SIGNATURE SHOT);
OpenMontage `hero_moment` ("must not share a shot size with its neighbours").
Reserve **one beat per film** whose job is novelty, not semantic fit — full-bleed screenshot, extreme scale,
register/colour inversion (dark is allowed sparingly, per the brand lock).
**Acceptance:** every film has exactly 1 hero beat; its frame differs from both neighbours on structure signature
**and** shows a `p90` change spike ≥2× the film median at its timestamp (measured by R0 on the mp4).
**Claude 3h · Machine ~20min · User 0.5h**

### Module R4 — Texture + grade
**Fixes:** the residual "flat/washed" read (luma 226, near-white). **Learned from:** `video-edit-skill-clean`
4an (cloudy grid), 4aq (global grade, "felt not seen").
Cloudy-masked animated grid (crisp in patches, gradient-out) + one global grade over the whole comp so composited
elements stop looking pasted on. **Light-dominant is retained** — this is contrast and texture, not darkness.
**Acceptance:** `detail` (spatial stdev) rises without `ALIVE%` regressing; a 3-film A/B where the user picks the
graded version blind ≥2/3. *(Honest note: this is the one module whose acceptance is partly taste. I have kept it
small and ranked it 4th for that reason.)*
**Claude 4h · Machine ~25min · User 0.5h (blind A/B)**

### ~~Module R5 — Fix the two defects~~ — **CUT (both are legacy artefacts, not live)**
**Was 2h.** Both the coral and the placeholder text are in a **2026-07-03 legacy file**, not in current V2 output
(§3.6). Nothing to fix in the shipping engine.
**Residue — 0.25h, worth doing:** (a) verify `store\v6-stage`, which was **not** in the re-render batch and is
expected to still be coral; (b) keep a demo-placeholder string scan as a **cheap permanent guard** — the trap is
real and has shipped once, even if not in the current five. **Claude 0.25h · User 0h**

### Totals (corrected)
| | Claude | Machine | User | |
|---|---|---|---|---|
| R0 instrument (**novelty-based**) + regression guard | 3h | 0.25h | 0h | +0.5h: metric was wrong once |
| **R1 frozen-hold guard** | **1.5h** | 0.25h | 0h | **rescoped 6h→1.5h, NOT cut** |
| **R2 break the chassis** | **8h** | 0.7h | 1h | **the dominant module** |
| R3 signature shot | 3h | 0.3h | 0.5h | |
| R4 texture + grade | 4h | 0.4h | 0.5h | **recommend cut** |
| ~~R5 defects~~ | ~~2h~~ **0.25h** | 0.1h | 0h | **CUT — legacy only** |
| **Total (R0+R1+R2+R3+R5residue)** | **≈15.75h** | **≈1.5h** | **≈1.5h** | |
| *(+R4 if taken)* | *+4h* | *+0.4h* | *+0.5h* | |

**The answer to "cần train bao nhiêu tiếng": ≈15–16 hours of my build time, ≈1.5 hours of machine render time,
and ≈1.5 hours of your time** (two decisions: anchor sets, and a final eyeball). Down from my first draft's
25.5h — measuring the *right* corpus deleted the largest module and both "defects"; a broken metric then nearly
deleted 1.5h of real work, which is now restored.

Not a round number because it isn't one: R2 dominates because it touches the chassis every archetype inherits.
**R4 (texture/grade) should probably also be cut** — with motion solved and luma ~207–218 on current films, it is
the only module whose acceptance is partly taste, and nothing in the evidence demands it. **Take R0+R2+R3 = ≈13.5h.**

**Confidence:** R0/R3/R5 are grounded (ruler built and validated; throughput measured on 20 cores).
**R2 remains the least certain — could run to 12h** if the chassis is deeply hardcoded. I would rather say that
now than repeat the 14× miss. Note the miss I *did* make this round was not estimation — it was **measuring the
wrong corpus**, which is why R0 (the ruler) earns its slot: it is what caught it.

### Sequencing (corrected)
```
R0 (ruler + regression guard)  ──►  R2 (layout chassis)  ──►  R3 (signature shot)
                                          │
                                          └──►  R4 (texture) — probably cut
```
- **R0 is a hard gate**, and now doubly so: it must lock in the motion win (ALIVE ≥56 / CONC ≤40) so R2 cannot
  regress it while chasing variety. 2.5h.
- **R2 is the whole job.** It is the only cause proven live on current output.
- **R3 after R2** — a signature shot inside an immutable chassis has nothing to break *from*.

### What NOT to do — cut honestly
| Cut | Why |
|---|---|
| **Any ML fine-tuning** | No cause in §3 is a model-capability problem. All are rules/structure. Would be slow and unverifiable. |
| **Adding density / more elements** | **We already out-densify the reference (37.1 vs 28.6) and still read monotone.** Our own prior diagnosis ("neon is what people reach for when they lack density") is **disproven by measurement**. Adding density makes it worse. |
| **Adding more motion on average** | We already move more (3.79 vs 2.66). The problem is *distribution*, not amount. |
| **MorphSVG** | GSAP is free and it's tempting *because* it's newly available. It fixes no cause in §3. Revisit only if R1–R3 land and something still feels flat. Availability is not a reason. |
| **More archetypes / more templates** | Both any2video and Orkas explicitly say a template pool *causes* sameness. And 4ab: "a 10-beat plan with 8 distinct kinds is still wrong." More archetypes inside one chassis = the same video. **R2 beats a bigger library.** |
| **Recordly** | AGPL + UI-attribution rider; craft is cursor-telemetry-bound. Nothing for us. |
| **Porting the 1,130-SFX pack expansion now** | Audio is not a §3 cause. Note 4u's warning (their "boring" was *level*, not arrangement) — a cheap level check beats a big library. Defer. |
| **Re-studying `Video Template` archetypes** | Content delta = 2 files. The 2026-07-01 study stands. |
| **Chasing the bottom-chrome freeze first** | Real (86.1%) but our overall frozen-pixel share is *lower* than theirs. Fold into R2; don't headline it. |

### Open decision for the user (not mine to make)
`video-edit-skill-clean` 4u asserts *"a rotating/random bed is not branding; one consistent track is"* — which
contradicts our md5-rotating `bgm_sourcer`. Flagging as a **decision**, not a finding. Not in the plan above.

---

## 5. Licence + provenance discipline
- **any2video (MIT)**, **Orkas (MIT)**, **reels-af (Apache-2.0)** — permissive, but per the standing rule
  (*"nếu bạn copy 100% vào thì sẽ lệch hệ thống"*) we **learn the rule and re-author it**. No paste.
- **OpenMontage (AGPL-3.0)** — **ideas only, clean-room.** No code, no prose. Techniques aren't copyrightable.
- **Recordly (AGPL + attribution rider)** — do not touch.
- **bachdyon (PolyForm NC)** — reference forever. **Remotion** — zero code.
- **No third-party names ship in SEOSONA artifacts** (*"chuẩn hóa đừng gắn tên của những người khác vào của
  tôi"*). Provenance lives in `2_KNOWLEDGE/INGESTION_LOG.md` only. Names to strip are enumerated in the agent
  reports (incl. **Ngọc Châu**, **Điện máy Xanh**, **The Weekend Studio**, Hào Lâm/BuildLoop).
- **Flag:** `video-edit-skill-clean` fetches Space Grotesk + Caveat **live from `fonts.googleapis.com` at render
  time** — a network dependency and a licence question. We use Be Vietnam Pro; do not inherit this.

---

## 6. The one-line answer (corrected twice — this is the version to quote)
> **Monotony is ~85% sameness, ~15% frozen holds.**
> `promo-v7-procedural` moves plenty — 39 of its 41 scenes are genuinely animating (verified by looking, not just
> by a metric). Yet the user calls it *"quá đơn điệu"*, and the reason is **repetition, not stillness**:
> **53.7% of its scenes are one archetype (`statement`), the same kind runs 9 times in a row, and there are only
> 7 distinct kinds across 41 scenes** — against a rule three independent references state identically:
> *never repeat the same kind 3× in a row.*
> **Plus a real minority defect:** 2 scenes (`s33_bento`, `s36_bento`) hold ~10s with **zero new information** —
> about **2× the reference's maximum hold** for that kind of card.
>
> **They aren't richer because they have more. They're richer because they never repeat themselves.**
> Fix the run-length, the kind-share, and the two frozen holds. **≈15–16 hours, not 25.**

---

## 7. Metric integrity — what this study got wrong, twice
Both errors share one root, named correctly by the coordinator: **measuring something and not verifying it was
the thing I meant to measure.**
1. **Wrong corpus** — measured the legacy engine, called it "OURS", never checked mtimes. Caught by a challenge.
2. **Wrong quantity** — measured pixel churn, called it "aliveness". Reported 0.8% dead for a film containing two
   10-second frozen cards. Caught by a challenge.

**What actually resolved both: looking at frames, and checking file dates/paths.** Not a better threshold.
The rules this earns:
- **Never quote an adjacent-frame-delta number without its sample rate and scale** — the same file, same
  threshold, gives 0.8% or 53.5% depending only on those.
- **Aliveness = novelty vs ~2s earlier**, never adjacent delta.
- **Any aggregate must be spot-checked against extracted frames a human looked at** before it gates anything.
  This is now R0's own acceptance test — the ruler must reproduce a human's verdict on the `s33_bento`
  (frozen) and `t=40–46` (kinetic) stretches, which are retained as its **fixtures**.
- **A metric that returns a suspiciously clean extreme (0.0% dead, 0 cuts) is probably broken.** This study hit
  that pattern **three** times (zero cuts — real; 0.0% dead — broken; 0.8% dead — broken). Suspicion is cheap;
  extract two frames and look.
