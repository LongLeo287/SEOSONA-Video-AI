# WHY Auto-Create-Video produces better-looking videos than our V2

**Repo:** https://github.com/hoquanghai/Auto-Create-Video (Ho Quang Hai)
**Analyzed:** 2026-07-16 — full deep read of the render/animation path (clean clone, `--depth 1`)
**License:** **MIT** — verified in `LICENSE` (`Copyright (c) 2026 Ho Quang Hai`, standard MIT text). Clean-room adoptable. The one non-trivial dependency (`hyperframes` npm pkg, HeyGen) is a separate runtime we already know from the HyperFrames family; not vendored code, so no license entanglement from reading this repo.
**Verdict up front:** On *motion quality* they are genuinely **better**, and the reason is architectural, not cosmetic — they render **every frame of a live GSAP animation in headless Chromium**, we render **one static PNG per scene and fake motion with ffmpeg fades**. On *content pipeline* (ASR, captions, brand, reframe, auto-analysis) **V2 is ahead** — they don't even have those. So: better on the one axis the task is asking about, behind on several others. Honest bottom line below.

---

## 0. What this repo actually is (so we compare fairly)

It is a **script.json → motion-graphic video** renderer. It is NOT footage-based and has NO ASR. The input is a hand/LLM-authored `script.json` (authored by the bundled Claude skill `.claude/skills/create-news-video/SKILL.md` from a URL/txt). So structurally it sits where our *native* (motion-graphic) engine sits, NOT where our talking-head footage engine sits. The fair comparison is **their renderer vs our `nativeRenderAdapter`**.

Pipeline (`src/pipeline.ts`, 8 steps): load+validate script (Zod) → write `script.txt` → fetch og:image + TTS per scene (parallel, idempotent per-scene mp3 reuse) → concat voice with silence + **mix SFX** → **compose one HTML doc** (`html-composer.ts`) → **render with the real `hyperframes` CLI** (`hyperframes-runner.ts`) → done.

---

## 1. Their render/animation architecture — what produces the motion

**The whole video is ONE HTML document with ONE paused GSAP master timeline, captured frame-by-frame by headless Chromium.** Three files carry this:

### a) `src/render/templates/base.html.tmpl` — the composition contract
A single 1080×1920 `#stage` with `data-composition-id="news-video"`, `data-start`, `data-duration`. It loads **GSAP 3.14** from CDN, one `<audio class="clip">` voice track, and all scenes as `<div class="scene clip" data-start data-duration data-layout>`. This is the HyperFrames "composition" contract — the runtime reads `data-start/duration` on `.clip` elements and the exposed timeline.

### b) `src/render/templates/animations.js` — the **v2 Animation Engine** (their words, line 1)
This is the crown jewel and the exact thing V2 lacks. It builds **one paused GSAP timeline** and hands it to the runtime:
```js
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
window.__timelines["news-video"] = tl;
```
Then it **dispatches per scene by `data-layout`** to a dedicated animator — `animateHook`, `animateComparison`, `animateStatHero`, `animateFeatureList`, `animateCallout`, `animateOutro`. Each schedules real eased tweens at absolute timeline positions (3rd arg = `start + offset`), e.g.:
- Hook headline: `tl.fromTo(headline, {scale:0.5, opacity:0}, {scale:1, opacity:1, duration:0.6}, start+0.15)` then a **shimmer mask sweep** `x:"-120%"→"120%"` over 1.0s.
- Comparison: left card slides `x:-80→0`, "VS" scale-pops, right card slides `x:80→0` — **staggered** at +0.15 / +0.45 / +0.6.
- Feature list: card rises, a rule wipes `scaleX:0→1`, bullets **stagger in** `start+0.6+i*0.15`.
- Outro: CTA drops, channel scale-pops, underline grows `width:0→600px`, then a **TikTok follow-card** slides up `y:300→0`, the button does a press `scale:0.92→1`, "Follow"→"Following" cross-fade, and a slow **hold zoom** `scale:1→1.08` over the remaining outro seconds.

### c) `src/render/hyperframes-runner.ts` + the `hyperframes` npm pkg (v0.4.34) — the renderer
`renderWithHyperframes()` just shells `npx hyperframes render <dir> --output video.mp4 --fps 30 --quality standard`. The engine's real work is in the `hyperframes` package, whose lockfile deps tell the whole story: **`puppeteer-core` + `@puppeteer/browsers`** (headless Chromium), `esbuild` (bundles `animations.js`), `postcss`, `hono` (local server to serve the composition). The runtime **seeks the paused timeline to each frame's time (`tl.seek(t)`), screenshots the Chromium viewport, and pipes the PNG stream to ffmpeg** at 30fps. Because the timeline is *paused and seeked*, playback is **deterministic and frame-exact** — every eased in-between, every shimmer position, every stagger is a real rendered frame.

**How captions/cards/transitions animate frame-by-frame:** they don't use ffmpeg for motion at all. The card entrances, staggers, shimmer sweeps, Ken Burns (`styles.css` `@keyframes kb-zoom-in` etc. bound to `--scene-dur`), grain overlay (`hf-grain-noise` steps animation), and the TikTok card are **all CSS/GSAP animations captured live per frame**. ffmpeg only muxes the final frame stream + audio.

**Caption note (important):** they render **no on-video captions/subtitles at all**. `script.txt` is written out explicitly "for CapCut auto-caption" (pipeline step 2, SKILL step 8) — the human adds captions later in CapCut. So their polish is card typography + motion, not karaoke captions.

---

## 2. WHY their videos look better — ranked

1. **Real per-frame kinetic motion (THE #1 reason).** A live GSAP timeline rendered at 30fps in Chromium gives true eased entrances, staggers, scale-pops, shimmer sweeps and hold-zooms. V2's native path renders **one static PNG per scene** and simulates motion with **ffmpeg xfade/slide** between stills — so within a scene there is essentially no element-level motion, only a whole-frame fade/slide. This is a categorical gap, not a tuning gap.
2. **Distinct layout archetypes, each with its own choreography.** Six templates (`hook / comparison / stat-hero / feature-list / callout / outro`) each map to a bespoke animator + CSS layout. Variety per scene reads as "produced". V2 has archetypes too, but without per-archetype *motion* choreography they flatten out on screen.
3. **Signature entrance craft: shimmer sweep + staggered reveals.** The `.shimmer-mask` gradient swept across headlines/stat-values (masked, `mix-blend-mode:overlay`) and the `+i*0.15` bullet stagger are exactly the "expensive" touches. Cheap to compute, high perceived quality.
4. **A polished, high-conversion outro (TikTok follow card).** A fully animated follow-card (slide-up → button press → Follow→Following → hold-zoom) with a **3s hold after voice ends** (`OUTRO_HOLD_SEC`) is a finished, platform-native ending. V2's outro is comparatively static.
5. **Cohesive dark "HeyGen-look" visual system + texture.** `styles.css` commits hard to one palette (navy `#0a1628` + cyan `#22d3ee` + purple `#a855f7`), Anton/Inter display type at huge sizes (160px hooks, 220px stats), glass cards, glow shadows, and an animated **film-grain overlay** + persistent brand shell. It's opinionated and consistent.

(SFX also helps — a smart 3-tier semantic selector, `sfx-selector.ts` — but that's audio, and V2 already has a native SFX library, so it's not a *look* differentiator.)

---

## 3. What's transferable into V2's native renderer (MIT → clean-room)

**Yes — the animation approach is adoptable, and it fits our stack with a moderate change, not a rewrite.** Two viable routes:

**Route A (recommended, biggest win): switch the native renderer from "1 PNG/scene + ffmpeg-fade" to "paused-timeline seek + per-frame Playwright screenshot".** We already render HTML/CSS via **Playwright** — Playwright can do exactly what HyperFrames' Puppeteer does:
- Compose the whole video as one HTML doc (like `html-composer.ts`) with a **paused animation timeline** exposed on `window` (GSAP, or even the Web Animations API to avoid a CDN dep — see Route B).
- In our Playwright driver, loop frames `t = 0..duration step 1/fps`, call `await page.evaluate(t => window.__timeline.seek(t), t)` (or `document.getAnimations().forEach(a => a.currentTime = t*1000)`), `page.screenshot()`, and pipe the PNG stream to the **same ffmpeg** we already invoke. We keep ASS captions by burning them in the same ffmpeg pass (or as a DOM caption layer animated on the timeline — even better, it makes captions kinetic too).
- Net: we **delete the ffmpeg-fade motion layer** and gain true element-level motion, reusing our existing Playwright + ffmpeg + rembg + brand-kit machinery. This is the single highest-leverage change for perceived quality.

**Route B (lower risk, no new engine): clean-room port `animations.js` as a per-archetype motion spec** and drive it with our current Playwright, seeking per frame. We do NOT need the `hyperframes` npm package or GSAP — the *pattern* is what's MIT and transferable: `(scene, layout) → list of {target, fromVars, toVars, startSec, durSec, ease}` tweens on a paused clock. Port the six animators' choreography (scale-pop hook, staggered bullets, shimmer sweep, comparison slide-in, outro follow-card) as our own tween table over WAAPI. We already harvested HyperFrames *craft*; this harvests HyperFrames *motion choreography*, which we skipped.

**Against Playwright+ffmpeg specifically:** the only real cost is render time (N frames × screenshot vs 1 PNG/scene). Mitigations they implicitly show: fixed 30fps, `--quality` tiers, and **idempotent caching** (their per-scene mp3 reuse; our KeepVoice/partial-rerender already does this for stages). Per-frame capture at 1080×1920/30fps is well within what a Puppeteer/Playwright pipeline handles — it's literally what HyperFrames ships.

**Directly liftable, low-risk pieces (clean-room, re-authored in our brand):**
- The **shimmer-sweep** mask technique (`styles.css` `.shimmer-mask` + the GSAP `x:-120%→120%` sweep).
- The **staggered reveal** pattern (`start + i*0.15`) for any list/bullet component.
- The **animated TikTok/subscribe follow-card** outro (great for our publish targets) + the **post-voice hold** (`OUTRO_HOLD_SEC`) so CTAs are readable.
- The **animated film-grain overlay** (`hf-grain-noise`) for texture.
- The **semantic 3-tier SFX selector** logic (`sfx-selector.ts`) if our `_sfx_cues` wants a content-keyword tier.

---

## 4. Capability V2 structurally lacks

**A real animation engine.** V2's native path is a *slideshow compositor*: HTML→one PNG per scene, then ffmpeg fades/slides. There is no clock, no timeline, no per-element tween, no per-frame capture — so intra-scene motion cannot exist by construction. Auto-Create-Video has a **paused-timeline + per-frame-seek capture** engine (via real HyperFrames), which is the missing primitive. This is the one thing they have that we cannot approximate by tuning; it requires the Route-A/B change. Everything else they do, we already have equal or better.

---

## 5. Honest verdict — better, or just different? Where V2 is even/ahead

**Better on motion. Behind on almost everything else.** Being non-defensive: their finished 60s news short *looks* more premium because of #1–#5 above, and that gap is real and worth closing. But it's a narrow, specialized tool. Where **V2 is even or clearly ahead:**

- **Auto-analysis / ASR — V2 way ahead.** They have **no ASR and no analysis**; input is an LLM-authored `script.json`. V2 does real PhoWhisper transcription + content planning from actual footage/topic. (V2's weak spot — deterministic keyword fallback / unwired LLM seam — is still a better starting point than "no analyzer at all".)
- **Native captions — V2 ahead.** V2 burns **ASS karaoke captions** in-render. They **punt captions to CapCut** (`script.txt`). Our captions ship in the mp4; theirs don't.
- **Footage / talking-head — V2 ahead.** They have no footage engine, no rembg text-behind-speaker, no face-centered reframe, no TH-Chest/TopCard/Inset modes. Backgrounds are gradient or a single og:image with CSS Ken Burns.
- **Brand system — even/ahead.** Both commit to a palette. Theirs is a fixed dark HeyGen-look; ours is a governed brand contract (DESIGN.md, light-only, exact SEOSONA palette). Different taste, comparable rigor.
- **B-roll / music — mixed.** Neither auto-sources b-roll footage; neither adds native BGM (they do SFX only; V2 has native SFX **and** a BGM sourcer). Slight edge V2.
- **Reliability niceties — even.** Both have idempotent reuse / partial re-render (their per-scene mp3 skip + `rerender.ts`; our KeepVoice + `scripts/rerender.py`).

**So:** adopt their **motion architecture** (the real gap), keep our analysis + captions + reframe + brand. This is "learn their craft, keep our engines + light brand" — the same stance as prior HyperFrames-family studies.

---

## TL;DR — top improvements to land in V2

1. **Replace ffmpeg-fade native motion with a paused-timeline + per-frame Playwright-seek renderer** (Route A). Highest-leverage change; reuses our Playwright/ffmpeg/rembg/brand stack. This is the #1 gap.
2. If Route A is too big now: **clean-room port the six per-archetype animators** (`animations.js`) as a WAAPI tween table driven by per-frame seek (Route B) — no GSAP/HyperFrames dependency needed.
3. Lift the **shimmer-sweep**, **staggered reveals**, **animated follow-card outro + post-voice hold**, and **film-grain overlay** as brand-recolored components.
4. Consider their **semantic SFX tier** for our `_sfx_cues`.
5. Keep V2's advantages intact: PhoWhisper ASR, native ASS karaoke captions, face-centered reframe, talking-head modes, light brand, BGM sourcer.

**License:** MIT (verified). **Doc path:** `D:\SEOSONA AI\SEOSONA Video\docs\v2_phase0\WHYBETTER_autocreate.md`. No git commit; `seosona-video-os` untouched.

### Evidence index (files quoted)
- `src/render/templates/animations.js` — the "v2 Animation Engine": `window.__timelines`, paused GSAP timeline, per-layout animators, shimmer sweep, staggers, TikTok follow-card.
- `src/render/templates/base.html.tmpl` — composition contract (`data-composition-id`, `.clip` `data-start/duration`, GSAP CDN).
- `src/render/templates/styles.css` — visual system, Ken Burns `@keyframes`, `.shimmer-mask`, grain `hf-grain-noise`, TikTok card.
- `src/render/html-composer.ts` — scene→HTML dispatch, timing, injects `animations.js` inline.
- `src/render/hyperframes-runner.ts` — `npx hyperframes render --fps 30`.
- `src/pipeline.ts` — 8-step flow; `script.txt` for CapCut (no native captions); SFX mix; `OUTRO_HOLD_SEC`.
- `package.json` / `package-lock.json` — `hyperframes@0.4.34` → `puppeteer-core` + `@puppeteer/browsers` + `esbuild` + `hono` (per-frame headless-Chromium capture).
- `.claude/skills/create-news-video/SKILL.md` — input is an LLM-authored `script.json` (no ASR/analysis).
- `LICENSE` — MIT.
