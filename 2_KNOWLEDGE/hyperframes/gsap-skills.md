# GSAP for HyperFrames — techniques, plugins, seek-render rules

Source: [greensock/gsap-skills](https://github.com/greensock/gsap-skills) (MIT). Deep-analysed
for SEOSONA Video (HTML/CSS + GSAP → MP4 via headless Chrome, single PAUSED timeline seeked
frame-by-frame). Install the upstream agent skills with:
`npx skills add https://github.com/greensock/gsap-skills` — but install only **gsap-plugins,
gsap-core, gsap-timeline, gsap-utils** (+ trimmed gsap-performance). Ignore gsap-scrolltrigger /
gsap-react / gsap-frameworks (web-runtime, irrelevant to a deterministic seek render).

## 🔓 ALL plugins are free (Webflow) — and SEOSONA loads them in EVERY render
No Club GSAP / auth token. `4_BRAIN/pipeline_manager.py` vendors gsap 3.13.0 +
9 plugins from `5_FRAMEWORK/hf_core/vendor/gsap/` into each render and registers them:

| Plugin | Unlocks for video |
|--------|-------------------|
| **SplitText** | per-char/word/line + `mask` → kinetic & karaoke captions |
| **MorphSVGPlugin** | logo/icon/shape morphs, shape-wipe scene transitions |
| **DrawSVGPlugin** | line-draw reveals (title underlines, map routes, line art) |
| **MotionPathPlugin** | fly a logo/icon/b-roll along a curve (`autoRotate`) |
| **ScrambleTextPlugin** | numbers/text scramble-then-settle (stats, prices, dates) |
| **CustomEase** | the branded ease — **`ease: "seosona"`** is pre-registered every render |
| **EasePack** | RoughEase (glitch), ExpoScaleEase (punch-in zoom), SlowMo |
| **CustomBounce / CustomWiggle** | branded bounce drop-in / shake accents |

(ScrollTrigger was intentionally NOT loaded — a paused/seeked timeline never scrolls.)

## 🥇 Top techniques to use (with snippets)
**1. SplitText kinetic captions** (split ONCE, after fonts — see gotchas):
```js
const s = SplitText.create(".heading", { type: "words, chars", mask: "lines" });
gsap.from(s.chars, { yPercent: 100, opacity: 0, stagger: 0.03, duration: 0.4, ease: "seosona" });
```
**2. Label-anchored master timeline = VO sync** (the core orchestration model):
```js
const tl = gsap.timeline({ paused: true, defaults: { duration: 0.5, ease: "seosona" } });
tl.add(titleScene(), "s1").add(dataScene(), "s1+=3.2").to(".lowerThird", { autoAlpha: 1 }, "<");
// position tokens: 3.2 (abs) · "+=0.2"/"-=0.2" (rel) · "label+=0.3" · "<" ">" (sync to prev)
```
**3. Data-driven reveals** — `distribute` + grid stagger (bar charts, stat grids):
```js
gsap.to(".bar", { scaleY: gsap.utils.distribute({ base:0.2, amount:2.5, from:"center" }),
  transformOrigin:"bottom", stagger:{ each:0.05, grid:"auto", from:"edges", axis:"x" } });
```
**4. Number counter / data→visual mapping** (utils):
```js
const pctToH = gsap.utils.mapRange(0,100,0,480);          // reusable
gsap.to(o,{ val:1250000, duration:1.5, ease:"seosona",
  onUpdate:()=>el.textContent=Math.round(o.val).toLocaleString() });
```
**5. DrawSVG underline · ScrambleText stat · MotionPath fly · MorphSVG logo:**
```js
gsap.fromTo("#underline",{drawSVG:"0% 0%"},{drawSVG:"0% 100%",duration:0.8,ease:"seosona"});
gsap.to(".stat",{duration:1,scrambleText:{text:"1,250,000",chars:"0123456789",revealDelay:0.3}});
gsap.to(".drone",{duration:2,motionPath:{path:"#route",align:"#route",autoRotate:true,alignOrigin:[0.5,0.5]}});
gsap.to("#logoA",{morphSVG:{shape:"#logoB",type:"rotational",shapeIndex:2},duration:1});
```

## ⚠️ SEEK-RENDER GOTCHAS (these silently break a frame-by-frame render — follow strictly)
1. **NEVER `SplitText({autoSplit:true})`** — it re-splits on font load / width change → different frame each run. Split ONCE.
2. **Split AFTER fonts load:** `await document.fonts.ready` before `SplitText.create()` — critical for Vietnamese diacritic fonts (char positions shift otherwise). Add CSS `font-kerning:none` on split text.
3. **No real-time constructs:** `gsap.quickTo`, `Observer`, `Draggable`, `Inertia(auto)` are event/RAF-driven → useless when seeking. All motion must live on the paused master timeline.
4. **Dev-only — never ship in render:** `GSDevTools`, `MotionPathHelper` (inject UI/RAF). Tune locally, hardcode the result.
5. **`matchMedia` / reduced-motion won't fire** in headless — never gate required animation behind it; bake the branch.
6. **4K crispness = transforms only:** animate `x/y/scale/rotation/opacity` (+ `xPercent`/`yPercent` for resolution independence). NEVER `width/height/top/left/margin` (layout thrash). Use `autoAlpha` not `opacity`.
7. **Determinism:** `stagger`/`distribute` resolve to fixed offsets → seek-safe (preferred). Avoid per-frame `random()` unless seeded. Resolve MorphSVG `shapeIndex:"log"` + `precompile:"log"` at author time and paste the values back.

## Branded ease
`ease: "seosona"` (a confident smooth ease-out) is registered in every render via
`CustomEase.create("seosona", "M0,0 C0.22,1 0.36,1 1,1")` in `pipeline_manager.py`. Use it
as the default for title/hero reveals to keep one motion signature across all videos. Tune
the curve there to change the brand feel.

> Deeper authoring: `.agents/skills/hyperframes-animation`. Catalog blocks: `npx hyperframes add`.
