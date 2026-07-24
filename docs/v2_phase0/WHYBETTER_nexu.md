# WHY BETTER? — `nexu-io/html-video` deep read (quality lens)

**Question asked:** why does `github.com/nexu-io/html-video` produce *better* finished videos than
our V2, and is it the per-frame animation engine V2's `nativeRenderAdapter` lacks?

**Honest headline (non-defensive):** the premise is only half-right, and the half that's wrong is the
important half. `html-video` is **not** a novel animation engine. It is a thin Apache-2.0 *meta-layer*
that renders the **same HyperFrames-style HTML+CSS+GSAP** our legacy `native_composer.py` already
renders, and its **shipped default engine is actually *less* deterministic than our path** (it uses
Playwright `recordVideo`, a real-time wall-clock recorder, not per-frame seek). It would only look
"better" than a `nativeRenderAdapter` that has been *deliberately down-specced* to "PNG-per-element +
ffmpeg fades" — which is a regression from **both** our legacy system **and V2's own ADR-002**
(`HyperFrames = primary renderer … seekable animation`). So the real finding is: **V2 already decided
to do the right thing; if the adapter is doing ffmpeg-fades, close that gap by honoring ADR-002 — and
`html-video` hands us two clean, adoptable Apache-2.0 patterns to do it with.**

- Source read: full clone, all `packages/*` + templates. License **Apache-2.0 — VERIFIED** (root
  `LICENSE`, every `package.json` `"license":"Apache-2.0"`, clean `ATTRIBUTIONS.md`/`NOTICE.md`;
  templates are MIT/Apache upstreams). **Adoptable clean-room.**
- Repo already in our triage: `docs/v2_phase0/REPO_BATCH_INBOX.md:12` (sibling `open-design` already
  INGESTED as HyperFrames craft).

---

## 1. HOW html-video turns HTML/CSS into video — the exact mechanism (quoted)

There are **two** engines in the repo, and they solve the "capture animated HTML" problem in **opposite
ways**. This distinction is the whole answer.

### (A) SHIPPED DEFAULT — `adapter-hyperframes` = real-time recorder (NOT seek)

File: `packages/adapter-hyperframes/src/render.ts`, function `render()`.

Mechanism = **launch headless Chromium, `recordVideo` the page in real wall-clock time, wait the
duration, close, then ffmpeg the webm to mp4**:

```
const context = await browser.newContext({
  viewport: { width, height },
  recordVideo: { dir: recordDir, size: { width, height } },   // ← wall-clock recorder
});
…
// while (Date.now() - start < totalMs) { await page.waitForTimeout(tick); }   // real-time wait
await context.close();                                          // playwright drops a .webm
…runFfmpeg(['-i', webmPath, '-r', String(fps), '-c:v','libx264', … outputPath])
```

It is **not** a deterministic per-frame renderer. `recordVideo` captures at the browser's own variable
cadence (machine-load dependent, frames dropped/duplicated), then `ffmpeg -r fps` *normalizes* after the
fact. Its cleverness is entirely in **making a real-time recording look clean**, via three tricks worth
stealing (see §4):

1. **Freeze-at-frame-0.** An `addInitScript` injects
   `*{animation-play-state:paused !important}` *before parsing*, so CSS `@keyframes` can't run during
   the cold page-load/font-fetch. (Quoted comment: *"Freeze all CSS/SMIL animations the instant the
   document starts parsing, BEFORE any @keyframes can begin counting down."*)
2. **Font-settle gate.** Waits for every stylesheet `<link>` to load, force-`fonts.load()`s each face,
   then `fonts.ready` + one rAF — kills the FOUT/font-swap flash mid-clip. (Comment: *"`document.fonts.ready`
   alone is NOT enough here, and this was the bug in the first cut."*)
3. **Lead-in trim.** Measures `leadInMs` from recorder-start to unfreeze and passes `ffmpeg -ss` to cut
   the dead frozen opening. Also probes the frame's own longest **finite** CSS/GSAP duration to
   auto-extend so animation is never truncated.

Its own header comment admits the upstream engine is not used: *"Upstream Hyperframes was never required
at runtime for this adapter — our generated HTML is plain inline-CSS+JS, chromium runs it as-is."*

### (B) GATED/OPTIONAL — `adapter-remotion` = deterministic per-frame SEEK ⭐

Files: `packages/adapter-remotion/src/render.ts` + `bridge/HtmlFrameDriver.tsx`.

**This** is the deterministic per-frame animation engine. It renders each HTML frame **inside a Remotion
composition via `<iframe srcDoc>`** and *seeks* the iframe's animations to Remotion's virtual clock,
per frame. From `HtmlFrameDriver.tsx`, function `seek(timeMs)`:

```
// (A) CSS Animations / Web Animations API — pure CSS @keyframes.
const anims = doc.getAnimations();
for (const a of anims) { a.pause(); a.currentTime = timeMs; }   // ← WAAPI seek
// (B) GSAP global timeline.
const tl = win.gsap?.globalTimeline;
if (tl) { tl.pause(); tl.time(timeMs / 1000); }                 // ← GSAP seek
```

Driven by `useCurrentFrame()`/`useVideoConfig()`; each frame is held open with a fresh
`delayRender()`/`continueRender()` handle until the doc is `docReady` (body populated **and**
`fonts.status !== 'loading'`) and the seek + one rAF have landed. Header comment states the exact
problem it solves: *"Remotion freezes its clock at frame N, screenshots, jumps to N+1 — but the iframe's
CSS keyframes / GSAP run on the browser's own wall-clock, so each screenshot catches the animation at a
random real-time point → flicker. We pause the iframe's clock and seek every animation to Remotion's
current time per frame."* Plus `neutralizeBlockingResources()` rewrites blocking external
`<link rel=stylesheet>` to `media="print"` async so a slow font CDN can't paint an all-black frame.

**Status honesty:** README lists Remotion as "🗺️ Planned," but the code is real and *is* wired —
`packages/cli/src/context.ts` registers it whenever peer deps exist (`if (remotionInstalled())
engines.register(remotionAdapter)`), and root `package.json` depends on `remotion@^4`. So the seek driver
is present and runnable, just not the default.

---

## 2. Does it solve V2's "wall-clock CSS won't capture headless" problem?

**Yes — but so does our own stack already.** The generic solution (seek every animation to a virtual
clock) lives in `HtmlFrameDriver.tsx` (§1B). And it's the *same trick our legacy renderer already uses*:
`4_BRAIN/native_composer.py` builds a **paused GSAP master timeline** and the HyperFrames CLI seeks it
frame-by-frame:

- `native_composer.py:2884` — `const tl=gsap.timeline({paused:true}); … window.__timelines["main"]=tl;`
- `native_composer.py:2717/2888` — *"fires onUpdate under .seek(), so the counter renders frame-by-frame"*;
  *"drive tweens call goToAndStop under GSAP `.seek` → seek-safe."*
- `native_composer.py:1772` — CSS is authored *"(no @keyframes) so every captured frame is deterministic."*

So the seek concept is not new to us. **The one genuinely broader capability in `HtmlFrameDriver` is
(A): it seeks native CSS `@keyframes` via WAAPI `getAnimations().currentTime`** — exactly the class of
animation our renderer today has to *avoid* (line 1772) and hand-author as GSAP or static-final SVG to
stay seek-safe. That is the single real gap it exposes (see §4.1).

---

## 3. WHY html-video output *can* look better than a fades-only adapter — and the honest cause

If the V2 `nativeRenderAdapter` truly renders **one PNG per graphic element and animates only with
ffmpeg fades/slides**, then yes, html-video output beats it — for reasons that are entirely about
**what animation vocabulary reaches the screen**, not about a superior engine:

| What lands on screen | Fades-only PNG adapter | html-video (either engine runs the live HTML) |
|---|---|---|
| Kinetic typography | none (static PNG cross-fades) | real per-word/char GSAP staggers, `back.out`, `expo.out` |
| Spring / physics motion | none | GSAP eases in the template (Remotion adapter adds true springs) |
| Transitions | ffmpeg xfade only | authored wipes, scale-ins, masked reveals in CSS/GSAP |
| Continuous motion | frozen | count-ups, draw-ons, orbit reveals play live |

Evidence of the craft it captures — `templates/frame-kinetic-type/compositions/main-graphics.html` is a
14.72s GSAP master timeline with `back.out(1.7)`, `expo.out`, `expo.in`, staggered word reveals, a
white-wipe scene cut, glyph rotations — six design-studio scenes choreographed at absolute time
positions. A fades-only adapter throws **all** of that away and shows PNG cross-dissolves.

**But the honest root cause is not "html-video invented motion." It's that our legacy path already plays
exactly this class of timeline** (`native_composer.py` even ports **Remotion's spring solver into GSAP
CustomEase** — `springLand/springSoft/springSnappy/springBouncy`, lines 2906-2917 — and loads SplitText
for per-char kinetic type, line 2900-2902). A fades-only V2 adapter would be *losing motion our own
2900-line legacy renderer produces today*, and would contradict **V2's own ADR-002**
(`docs/v2_phase0/ADR.md:18-24`: *"HyperFrames … HTML-native, agent-friendly, seekable … carried today's
E2E (fx01 quality 100/100) … Deterministic-render rules: seekable animation, seeded random"*). So the
"why better" is really **"why did the adapter drop to fades" — and the answer is to not drop it.**

---

## 4. What's TRANSFERABLE (Apache-2.0 → clean-room adoptable) — concrete integration path

The adapter interface, engine framing, and content-graph IR are architectural **REFERENCE** (they match
plans already in `REPO_ADOPTION_PLAN.md`). The **code-level** takes, ranked by value:

### 4.1 ⭐ Generic WAAPI+GSAP per-frame seek driver → widen V2's animation vocabulary
Port the `seek(timeMs)` core of `HtmlFrameDriver.tsx` (both branch A `getAnimations().currentTime` and
branch B `gsap.globalTimeline.time()`) into V2's Playwright capture loop. Today V2 seek-safety *requires*
GSAP-driven or static-final SVG and **avoids native CSS `@keyframes`**; adopting the WAAPI-seek branch lets
V2 deterministically capture **any** CSS `@keyframes` animation frame-by-frame. Integration against
Playwright+ffmpeg (no Remotion/React needed): per output frame `t`, in the page do
`document.getAnimations().forEach(a=>{a.pause();a.currentTime=t*1000})` **and**
`window.gsap?.globalTimeline.pause().time(t)`, `await one rAF`, `page.screenshot()` → PNG sequence →
`ffmpeg -framerate fps`. This is a strict *superset* of what our renderer seeks today and keeps full
determinism. **~40 lines, highest leverage.**

### 4.2 Capture-robustness discipline (kills three real render defects)
From `adapter-hyperframes/src/render.ts` + `HtmlFrameDriver.docReady`, port as pre-capture gates:
- **Font-settle before frame 0** — wait `<link>` load → `fonts.load()` each face → `fonts.ready` → rAF.
  Eliminates the FOUT/weight-swap flash mid-clip.
- **Freeze-at-frame-0** (`animation-play-state:paused` via init script) so nothing plays during page/font
  load; unfreeze (or start the seek loop) only once fonts are ready — capture and motion start aligned.
- **`neutralizeBlockingResources()`** — rewrite external blocking stylesheet links to `media="print"`
  async; prevents the all-black-frame failure when a font CDN is slow/blocked in headless.
These are directly relevant even to a fades adapter and are pure clean-room utility functions.

### 4.3 Content-graph IR — REFERENCE only
`packages/content-graph` (typed `entity|data|text` nodes + `sequence|contrast|dependency` edges,
topo-sorted to frame order). Clean multi-scene storyboard model, but V2 already has scene planning; note
the *edge-typing* idea (contrast → split layout, dependency → build order) as a planning refinement, not
a port.

**Do NOT adopt:** the `adapter-hyperframes` `recordVideo` real-time recorder itself — it is a
determinism *regression* vs our seek path (§5). Take its font/freeze/trim discipline, leave the recorder.

---

## 5. Where V2 is already EVEN or AHEAD (honest)

1. **Determinism:** V2's HyperFrames-CLI path does true per-frame seek; html-video's *default* engine
   does real-time `recordVideo` (variable fps, machine-load dependent, frames dropped/duped then
   ffmpeg-normalized). On the axis the question cares about, our shipped path is **more** deterministic
   than html-video's shipped path. The seek parity only exists in html-video's *gated* Remotion adapter.
2. **Springs already ported:** `native_composer.py` already carries Remotion's damped-spring solver as
   GSAP CustomEase presets + SplitText kinetic type + MotionPath + seeded value-noise. html-video's
   default engine has no spring layer of its own; only its Remotion adapter gets Remotion physics.
3. **Talking-head-over-footage is entirely ours:** rembg occlusion, face-centered reframe,
   TH-Chest/TopCard/Inset modes, ASR-synced karaoke keyword pops (`native_composer.py:2857-2863`), VN
   text normalization, brand lock (#2A5BDA/#E2724D, light-only). html-video renders *generated graphic
   frames only* — no real speaker footage compositing, no ASR karaoke, no brand contract. This is V2's
   core product and html-video has none of it.
4. **We already own the engine lineage** (`5_FRAMEWORK/hf_engine`, Apache-2.0 `LICENSE`) and drive the
   HyperFrames CLI directly, rather than reimplementing a lossy recorder around it.

*One licensing nugget worth noting:* html-video demonstrates an **Apache-2.0, clean-room way to render
HyperFrames-format HTML with plain Playwright, needing no upstream `hyperframes` runtime at all*
(render.ts header: *"Upstream Hyperframes was never required at runtime"*). If the NC status of the
upstream heygen `hyperframes` package is ever a concern for V2 distribution, this is the pattern that
removes that dependency — combine it with the §4.1 seek driver to get a fully self-owned, Apache-2.0,
deterministic HTML→video core.

---

## Verdict

**Is `html-video` the missing per-frame animation engine V2 needs? No.** It is a sibling meta-layer over
the *same* HyperFrames+GSAP substrate V2's ADR-002 already commits to and our legacy `native_composer.py`
already drives with real per-frame seek. Its default engine is *less* deterministic than ours; it lacks
our entire footage/ASR/brand stack.

**Would its output beat a fades-only `nativeRenderAdapter`? Yes — because that adapter would be
discarding real animation that our own stack already produces.** The fix is not to adopt html-video as an
engine; it is to **honor ADR-002 (seekable per-frame render) in the V2 adapter**, and harvest three
clean-room Apache-2.0 nuggets to do it well:

1. ⭐ **WAAPI+GSAP `seek(timeMs)` driver** (`HtmlFrameDriver.tsx`) — lets V2 seek native CSS `@keyframes`,
   the one animation class our current seek-safety avoids. Highest leverage.
2. **Font-settle + freeze-at-0 + `neutralizeBlockingResources`** (`adapter-hyperframes/render.ts`) —
   removes FOUT flash, black frames, dead lead-in.
3. **Content-graph edge-typing** — planning REFERENCE.

Explicitly **skip** its real-time `recordVideo` recorder (determinism regression).

**License:** Apache-2.0, verified, clean-room adoptable.
**Doc path:** `docs/v2_phase0/WHYBETTER_nexu.md` (this file). No `seosona-video-os` files touched; no git commit.
