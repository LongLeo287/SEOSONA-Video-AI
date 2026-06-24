# HyperFrames — Advanced Guides

Consolidated advanced/operational guides: HTML-in-canvas, background removal, website-to-video, HyperFrames vs Remotion, deployment, and feedback.

**Sources:**
- https://hyperframes.heygen.com/guides/html-in-canvas.md
- https://hyperframes.heygen.com/guides/remove-background.md
- https://hyperframes.heygen.com/guides/website-to-video.md
- https://hyperframes.heygen.com/guides/hyperframes-vs-remotion.md
- https://hyperframes.heygen.com/guides/deploy.md
- https://hyperframes.heygen.com/guides/feedback.md

---

# HTML in Canvas

**Source:** https://hyperframes.heygen.com/guides/html-in-canvas.md

# HTML-in-Canvas

> Render live HTML as WebGL textures — GPU shaders, 3D geometry, and cinematic effects on any DOM content.

# HTML-in-Canvas

The HTML-in-Canvas API (`drawElementImage`) lets you capture live, rendered DOM elements directly into a canvas at GPU speed. This means you can take any HTML — dashboards, forms, landing pages, app UIs — and render them as textures in WebGL scenes with shaders, 3D transformations, and post-processing effects.

<Warning>
  **Chrome flag required.** The `drawElementImage` API is experimental and must be enabled manually:

  1. Open `chrome://flags/#canvas-draw-element` in Chrome or Brave
  2. Set **CanvasDrawElement** to **Enabled**
  3. Restart the browser

  HyperFrames enables this flag automatically during rendering (`--enable-features=CanvasDrawElement`), so rendered videos work without manual setup. The flag is only needed for live preview in the Studio.
</Warning>

## How it works

1. Place HTML content inside a `<canvas layoutsubtree>` element
2. The browser renders the HTML children as normal DOM
3. Call `ctx.drawElementImage(element, x, y, w, h)` to capture the rendered pixels into the canvas
4. Use the canvas as a Three.js texture, apply shaders, map to 3D geometry

```html theme={null}
<!-- 1. HTML content lives inside the canvas -->
<canvas id="capture" layoutsubtree width="1920" height="1080">
  <div class="my-dashboard">
    <h1>Revenue: $4.2M</h1>
    <div class="chart">...</div>
  </div>
</canvas>

<!-- 2. WebGL canvas for 3D rendering -->
<canvas id="theater" width="1920" height="1080"></canvas>
```

```javascript theme={null}
// 3. Capture HTML to canvas
var capCanvas = document.getElementById("capture");
var ctx = capCanvas.getContext("2d");
ctx.drawElementImage(capCanvas.querySelector(".my-dashboard"), 0, 0, 1920, 1080);

// 4. Use as Three.js texture
var texture = new THREE.CanvasTexture(capCanvas);
var material = new THREE.MeshBasicMaterial({ map: texture });
```

## What makes this different

Traditional approaches like `html2canvas` re-parse and re-render the DOM in JavaScript — they're slow, lossy, and miss CSS features like `backdrop-filter`, complex shadows, and web fonts. The `drawElementImage` API uses the browser's own compositor, so:

* **Pixel-perfect** — every CSS feature is supported because the browser renders it natively
* **GPU-accelerated** — captures at 60fps, fast enough for real-time animation
* **Live content** — the HTML can animate, scroll, and change between captures
* **Multiple captures simultaneously** — no nesting restrictions, multiple `<canvas layoutsubtree>` elements can capture different content in the same composition

## Feature detection

Always feature-detect before using the API. Compositions should fall back gracefully for browsers without the flag enabled.

```javascript theme={null}
function isSupported() {
  var tc = document.createElement("canvas");
  if (!("layoutSubtree" in tc)) return false;
  tc.setAttribute("layoutsubtree", "");
  var ctx = tc.getContext("2d");
  return ctx && typeof ctx.drawElementImage === "function";
}

if (isSupported()) {
  ctx.drawElementImage(element, 0, 0, w, h);
} else {
  // Fallback: draw text directly on canvas, use static image, etc.
}
```

## Re-capturing every frame

For animated content (scrolling, transitions, counters), call `drawElementImage` inside your render loop to update the texture every frame:

```javascript theme={null}
function render() {
  // Update HTML state
  scrollContainer.style.transform = "translateY(-" + scrollOffset + "px)";
  counterEl.textContent = Math.round(currentValue);

  // Re-capture
  ctx.clearRect(0, 0, W, H);
  ctx.drawElementImage(htmlElement, 0, 0, W, H);
  texture.needsUpdate = true;

  // Render 3D scene with updated texture
  renderer.render(scene, camera);
}
```

## Catalog blocks

Install all HTML-in-Canvas blocks at once:

```bash theme={null}
npx hyperframes add html-in-canvas
```

Or install individually:

| Block                                                                        | Description                                                            | Install                                         |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------- |
| [iOS 26 Liquid Glass Home Screen](/catalog/blocks/ios26-liquid-glass)        | iPhone home screen with live Liquid Glass notifications and widgets    | `npx hyperframes add ios26-liquid-glass`        |
| [macOS Tahoe Liquid Glass Desktop](/catalog/blocks/macos-tahoe-liquid-glass) | MacBook desktop with liquid glass windows, dock, and notifications     | `npx hyperframes add macos-tahoe-liquid-glass`  |
| [Liquid Glass Notification](/catalog/blocks/liquid-glass-notification)       | Native-feeling glass notification stack with progress and reply states | `npx hyperframes add liquid-glass-notification` |
| [iPhone & MacBook](/catalog/blocks/vfx-iphone-device)                        | Real 3D GLTF devices with live HTML screens                            | `npx hyperframes add vfx-iphone-device`         |
| [Text Cursor](/catalog/blocks/vfx-text-cursor)                               | Dramatic text reveal with chromatic shadows                            | `npx hyperframes add vfx-text-cursor`           |
| [Portal](/catalog/blocks/vfx-portal)                                         | Dimension breach with volumetric light                                 | `npx hyperframes add vfx-portal`                |
| [Shatter](/catalog/blocks/vfx-shatter)                                       | HTML shatters into glass fragments                                     | `npx hyperframes add vfx-shatter`               |
| [Magnetic](/catalog/blocks/vfx-magnetic)                                     | Magnetic field particle visualization                                  | `npx hyperframes add vfx-magnetic`              |
| [Liquid Background](/catalog/blocks/vfx-liquid-background)                   | Organic liquid simulation                                              | `npx hyperframes add vfx-liquid-background`     |

## Rendering

HyperFrames enables the Chrome flag automatically during rendering. No special configuration needed:

```bash theme={null}
npx hyperframes render --output my-video.mp4
```

For Docker renders, the flag is also enabled automatically inside the container.

---

# Remove Background

**Source:** https://hyperframes.heygen.com/guides/remove-background.md

# Remove Background (transparent video)

> Remove the background from a video or image and drop it into any composition as a transparent overlay.

Background removal — also called *matting* in VFX — separates a foreground subject (typically a person) from its background. The output is a video with an alpha channel: fully transparent where the background was, opaque where the subject is. Drop it into any HyperFrames composition as a `<video>` tag and the subject floats over whatever you put behind them.

The CLI ships a built-in `remove-background` command that runs locally — no API keys, no cloud upload, no green screen.

## Quick Start

<Steps>
  <Step title="Verify ffmpeg is installed">
    The pipeline needs `ffmpeg` and `ffprobe` for decode + encode. Most systems already have them; if not:

    ```bash Terminal theme={null}
    # macOS
    brew install ffmpeg

    # Ubuntu / Debian
    sudo apt install ffmpeg
    ```

    Confirm with `npx hyperframes doctor` — both should be green.
  </Step>

  <Step title="Remove the background from your video">
    ```bash Terminal theme={null}
    npx hyperframes remove-background subject.mp4 -o transparent.webm
    ```

    On the first run, the CLI downloads \~168 MB of model weights to `~/.cache/hyperframes/background-removal/models/`. Subsequent runs reuse the cache.

    Output:

    ```
    ◇  Removed background from 240 frames in 38.4s (6.3 fps, CoreML) → ./transparent.webm
    ```
  </Step>

  <Step title="Drop it into a composition">
    The output is a standard VP9-with-alpha WebM. Chrome's `<video>` element decodes the alpha plane natively — no special player needed:

    ```html composition.html theme={null}
    <div class="scene">
      <!-- background layer -->
      <img src="city.jpg" class="bg" />

      <!-- transparent subject floats on top -->
      <video src="transparent.webm" autoplay muted loop playsinline></video>
    </div>
    ```

    Render the composition with the usual `hyperframes render`.
  </Step>
</Steps>

## How it works

The pipeline runs four stages, all locally:

```
ffmpeg decode  →  u²-net_human_seg inference  →  alpha composite  →  ffmpeg encode
   (raw RGB)         (320×320 mask, then upsampled)                    (VP9-alpha)
```

The model is **u²-net\_human\_seg** (MIT license, \~168 MB ONNX). It runs through `onnxruntime-node` with the best-available execution provider on your machine: CoreML on Apple Silicon, CUDA on NVIDIA, CPU otherwise.

The output is encoded with the exact ffmpeg flags Chrome's `<video>` element needs to decode alpha — `-pix_fmt yuva420p` plus the `alpha_mode=1` metadata tag. Get those wrong and the alpha plane is silently discarded by browsers.

## Output formats

| Extension         | Codec                  | When to use                                                      | Size (4s @ 1080p) |
| ----------------- | ---------------------- | ---------------------------------------------------------------- | ----------------- |
| `.webm` (default) | VP9 with alpha         | Drop into `<video>` for HTML5-native transparent playback        | \~1 MB            |
| `.mov`            | ProRes 4444 with alpha | Editing round-trip in Premiere / Resolve / Final Cut             | \~50 MB           |
| `.png`            | PNG with alpha         | Single-image cutout (only when the input is also a single image) | varies            |

```bash Terminal theme={null}
npx hyperframes remove-background subject.mp4 -o transparent.webm        # web playback
npx hyperframes remove-background subject.mp4 -o transparent.mov         # editing
npx hyperframes remove-background portrait.jpg -o cutout.png       # still image
```

## Layer separation: emit the cutout and the background plate together

Pass `--background-output` (alias `-b`) to write a *second* transparent video alongside the cutout. Same source RGB, alpha is the *inverse* mask — opaque where the surroundings were, transparent where the subject is. The result is a clean two-layer separation in a single inference pass:

```bash Terminal theme={null}
npx hyperframes remove-background subject.mp4 \
  -o subject.webm \
  --background-output plate.webm
```

| Output         | Alpha                                     | Use it as                                                                                                    |
| -------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `subject.webm` | Mask — subject opaque                     | Foreground layer (top of stack)                                                                              |
| `plate.webm`   | `255 − mask` — subject region transparent | Background layer; place anything you want **under the subject's silhouette** between this and `subject.webm` |

Both encoders share the source W/H/fps and your `--quality` preset, so the layers are pixel-aligned. Encode cost roughly doubles; segmentation cost is unchanged.

<Tip>
  **This is a hole-cut plate, not an inpainted clean plate.** The subject region in `plate.webm` is fully transparent — you have to composite something opaque under it (a graphic, a blurred copy, a different scene) to fill the hole. If you need an actual filled background where the subject was, use a video inpainter (LaMa, ProPainter, RunwayML Inpaint) — `remove-background` is not the right tool for that.
</Tip>

### Hole-cut vs. clean plate — when does the difference matter?

A **hole-cut plate** keeps the original surroundings and makes the subject region transparent. A **clean plate** fills the subject region with reconstructed background — produced by a separate inpainting model. Display each alone over black:

|                    | Hole-cut plate (this command)               | Clean plate (inpainted)                   |
| ------------------ | ------------------------------------------- | ----------------------------------------- |
| Subject region     | Transparent silhouette                      | Reconstructed background pixels           |
| What you see alone | A person-shaped hole                        | An empty room                             |
| Cost               | One inference pass, one extra ffmpeg encode | A second model (LaMa, ProPainter, E2FGVI) |
| Tool               | `remove-background --background-output`     | Outside this CLI                          |

The line is: **does anything ever need to be visible *through* the subject's silhouette where the subject used to be?**

| Use case                                                                  | What you need                                                     |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Text/graphics live *between* the cutout and the plate (the example above) | **Hole-cut** — the graphics fill the hole.                        |
| Composite the subject onto an unrelated scene                             | Neither. Just use `subject.webm`; the plate is irrelevant.        |
| Show "the room without the person" as a real background                   | **Clean plate** — a hole-cut plate would show a transparent void. |
| Replace the person with a different subject (re-target)                   | **Clean plate** — the new subject needs real pixels under it.     |
| VFX rotoscoping / "remove an extra from this take"                        | **Clean plate** — the canonical inpainting use case.              |

If something opaque always covers the silhouette, hole-cut is sufficient and \~1000× cheaper than running an inpainter.

### The two-layer composition pattern

The two-layer pattern is functionally a drop-in for [text-behind-subject](#text-behind-subject-the-recommended-layout) without needing the original `presenter.mp4` in the project — the plate replaces it as the bottom layer:

```html theme={null}
<!-- z=1 inverse-alpha plate fills everything except the subject's silhouette -->
<video src="plate.webm" data-start="0" data-duration="6" data-track-index="0" muted playsinline></video>

<!-- z=2 anything you want occluded by the subject lives here -->
<h1 style="z-index:2; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);">
  MAKE IT IN HYPERFRAMES
</h1>

<!-- z=3 the cutout puts the subject back on top -->
<div class="cutout-wrap" style="position:absolute;inset:0;z-index:3">
  <video src="subject.webm" data-start="0" data-duration="6" data-track-index="1" muted playsinline></video>
</div>
```

Constraints: the flag requires a video input and `.webm` or `.mov` for both outputs. It's not valid for image inputs (no temporal pairing to do) and won't accept `.png` for the plate.

## Performance

Real-world numbers from the [matting eval](https://www.heygenverse.com/a/0dd5a431-1832-4858-862d-de7fb7d02654), running u²-net\_human\_seg on a 4-second 1080p clip:

| Platform                         | Provider | ms/frame | 30-second clip |
| -------------------------------- | -------- | -------- | -------------- |
| Apple Silicon (M2 Pro / M3 / M4) | CoreML   | \~263    | \~2 min        |
| NVIDIA GPU (T4, A10, RTX)        | CUDA     | \~80–150 | \~30–60 s      |
| Linux x86                        | CPU      | \~1100   | \~16 min       |
| macOS Intel                      | CPU      | \~900    | \~13 min       |

Matting is offline preprocessing — you run it once per asset and reuse the output. CPU-only is slow but always works; if you reuse the same subject clip repeatedly, run it once on a faster machine and check the transparent output into your project.

## Picking a device explicitly

`--device auto` is the default and right for almost everyone. The flag exists for two cases:

* **Force CPU on a GPU box** when you want to keep the GPU free for other work, or are debugging an EP-specific issue:

  ```bash Terminal theme={null}
  npx hyperframes remove-background subject.mp4 -o transparent.webm --device cpu
  ```

* **Opt into CUDA** by setting `HYPERFRAMES_CUDA=1` and providing a GPU-enabled `onnxruntime-node` build (the bundled build is CPU + CoreML only, to keep the install small for the 99% of users who don't have a GPU):

  ```bash Terminal theme={null}
  HYPERFRAMES_CUDA=1 npx hyperframes remove-background subject.mp4 -o transparent.webm --device cuda
  ```

Run `npx hyperframes remove-background --info` to see what providers are detected on your machine and which one `auto` would pick.

## Using the transparent video in a composition

The transparent WebM behaves like any other video element. The two patterns you'll use most:

**Subject over a background image:**

```html theme={null}
<div style="position: relative; width: 1920px; height: 1080px;">
  <img src="background.jpg" style="position: absolute; inset: 0;" />
  <video
    src="transparent.webm"
    autoplay
    muted
    loop
    playsinline
    style="position: absolute; right: 80px; bottom: 0; height: 90%;"
  ></video>
</div>
```

**Subject over a HyperFrames scene:**

```html theme={null}
<!-- scene contents (text, animations, etc.) -->
<div class="title-card">Welcome</div>

<!-- subject layered on top -->
<video src="transparent.webm" autoplay muted loop playsinline class="subject"></video>
```

The cutout inherits the composition's frame rate and timeline — it plays through once during the scene's duration, so match the source clip length to the scene length when possible. If the scene is longer than the clip, `loop` handles it.

<Tip>
  When rendering a composition that contains a `<video>` element, the renderer reads the source via ffmpeg internally. Transparent WebMs are decoded with the alpha plane preserved.
</Tip>

## Compositing patterns and pitfalls

The cutout webm is a **re-encoded copy** of the source mp4's RGB — the matter pipeline decodes the source to raw RGB, runs segmentation, and re-encodes to VP9 with alpha. That choice has consequences depending on what you put behind it.

### The three patterns

| Pattern                                                                                | Behind the cutout                                         | Result                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cutout over a different scene** *(most common)*                                      | Static image, gradient, animated bg, or unrelated footage | Clean. The cutout is the only source of the subject — no doubling, no edge halo. Use any `--quality`.                                                                                                                                                   |
| **Cutout over its own source mp4** *(text-behind-subject, talking-head with overlays)* | The same mp4 the cutout was generated from                | Two RGB sources for the same person. At default `--quality balanced` (crf 18) the doubling is barely visible; at `--quality fast` (crf 30) you'll see a slight color shift / soft edge on the silhouette. Use `--quality best` (crf 12) for hero shots. |
| **Cutout over different footage of the same subject**                                  | Another take of the same person                           | Looks like two overlapping people. Avoid — re-shoot or re-cut the source.                                                                                                                                                                               |

### Text-behind-subject: the recommended layout

Putting a headline *behind* a presenter so their silhouette occludes the text:

```html theme={null}
<!-- z=1 base mp4: full lobby + presenter, plays the whole scene -->
<video
  id="cf-base"
  data-start="0" data-duration="6" data-media-start="0" data-track-index="0"
  src="presenter.mp4"
  muted playsinline
></video>

<!-- z=2 headline -->
<h1 id="cf-headline" style="position:absolute;top:50%;left:50%;
     transform:translate(-50%,-50%); z-index:2;
     color:#fff; text-shadow:0 6px 32px rgba(0,0,0,.55);
     clip-path:inset(0 0 100% 0); font-size:220px; font-weight:900;">
  MAKE IT IN HYPERFRAMES
</h1>

<!-- z=3 cutout: same source, alpha around presenter, hidden until the cut.
     The wrapper carries the opacity, NOT the <video> itself. -->
<div class="cutout-wrap" style="position:absolute;inset:0;z-index:3;opacity:0">
  <video
    id="cf-cutout"
    data-start="0" data-duration="6" data-media-start="0" data-track-index="1"
    src="presenter.webm"
    muted playsinline
  ></video>
</div>
```

```js theme={null}
const tl = gsap.timeline({ paused: true });
const CUT = 3.3;

// Reveal the headline early
tl.to("#cf-headline", { clipPath: "inset(0 0 0% 0)", duration: 0.6, ease: "expo.out" }, 0.25);

// At the cut, flip the cutout wrapper visible — silhouette punches through the headline
tl.set(".cutout-wrap", { opacity: 1 }, CUT);

// Sentinel: extend timeline to the composition's full duration so the renderer
// doesn't bail past the last meaningful tween.
tl.set({}, {}, 6);
```

### Two non-obvious rules

**1. Wrap the cutout video in a non-timed `<div>` and animate the wrapper, not the video.**

The framework forces `opacity: 1` on any element with `data-start`/`data-duration` while it's "active" — that's how it controls clip visibility. CSS `opacity: 0` on the video element is silently overwritten by the framework's clip lifecycle, so an opacity tween on the video element won't do anything. Wrap the video in a `<div>` that has no `data-*` attributes; the wrapper is owned entirely by your CSS/GSAP.

**2. Both videos start at `data-start="0"` and decode in sync from t=0.**

It's tempting to "late-mount" the cutout (`data-start="3.3"` to match the cut). Don't — Chrome does a seek + decoder warm-up at mount, which can land one frame off the base mp4 at the cut moment. With both videos mounted from t=0 and the cutout's wrapper opacity-animated, both decoders advance the same way and stay frame-accurate.

### Quality preset and color match

When the cutout is overlaid on its own source mp4, the encoder's CRF directly affects how visible the doubling is at edges:

| `--quality`            | CRF | File size (12s @ 1080p) | When to use                                                                     |
| ---------------------- | --- | ----------------------- | ------------------------------------------------------------------------------- |
| `fast`                 | 30  | \~2 MB                  | Cutout sits over an unrelated background and file size matters                  |
| `balanced` *(default)* | 18  | \~6 MB                  | Recommended for text-behind-subject and any pattern that overlays on the source |
| `best`                 | 12  | \~12 MB                 | Hero shots, masters, or anything you'll re-encode downstream                    |

The encoder also writes BT.709 + limited-range color metadata so Chrome's YUV→RGB pipeline matches the source mp4's. Without those tags, the cutout would render slightly differently from the underlying mp4 even at lossless quality (visible red/skin shift).

## What u²-net\_human\_seg is and isn't good for

The model is purpose-built for **portrait / human matting**. It excels when:

* ✅ The subject is a person, head-and-shoulders or full-body
* ✅ The framing is reasonably stable (not a wide handheld shot)
* ✅ The background contrasts with the subject

It struggles or fails on:

* ❌ Non-human subjects (products, animals, objects). The model will return a mostly-empty mask.
* ❌ Very fine hair detail on a busy background. The 320×320 inference resolution means hair tips get softened — fine for most use cases, but compositors notice.
* ❌ Frame-to-frame temporal consistency. Each frame is processed independently, so static backgrounds with moving subjects can show subtle edge flicker. For most web playback this is invisible; for high-end VFX it may matter.
* ❌ Live streams or real-time capture. The pipeline is batch-only.

If your use case hits one of these, see the alternatives below.

## Alternatives — when the built-in command isn't the right tool

The CLI ships **one model on purpose** — the one that's MIT-licensed, runs everywhere, and produces production-quality output for person/portrait video. The list below leads with **free, open-source tools** that pair naturally with HyperFrames. Each entry calls out the actual catch — license, install effort, hardware needs — so you can pick the right one for your situation. Full benchmarks are in the [matting eval](https://www.heygenverse.com/a/0dd5a431-1832-4858-862d-de7fb7d02654).

### Free, open-source CLIs and libraries

These all run locally with no account, no upload, no watermark.

| Tool                                                                                                | When to use it                                                                                                                                                                                                                   | Catch                                                                                                               |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [`rembg`](https://github.com/danielgatis/rembg) (Python, MIT)                                       | You need a different subject type — `isnet-general-use` for objects/animals/products, `birefnet-portrait` for a quality ceiling on hair, `silueta` for a tiny \~40 MB footprint. Same family as our default model, more variety. | Requires Python + `pip install rembg`. Some bundled models (`birefnet-*`) need \~4 GB RAM and are CPU-only          |
| [BiRefNet](https://github.com/ZhengPeng7/BiRefNet) (PyTorch, MIT)                                   | Highest-fidelity portrait mattes available — visibly better hair edges than u²-net                                                                                                                                               | Heavy (\~4 GB inference RAM), slow on CPU, broken on Apple CoreML at the time of the eval                           |
| [Robust Video Matting (RVM)](https://github.com/PeterL1n/RobustVideoMatting) (PyTorch, **GPL-3.0**) | The only widely-available model with **temporal consistency** built in — no edge flicker on moving subjects. Best choice when you're matting a long talking-head clip and frame-to-frame stability matters                       | GPL-3.0 license is incompatible with most commercial / proprietary codebases. Read your repo's license before using |
| [Backgroundremover](https://github.com/nadermx/backgroundremover) (Python, MIT)                     | Simple `pip install` wrapper around u²-net; nice if you want a Python API instead of our Node CLI                                                                                                                                | Same model family as ours, no quality difference — pick whichever fits your stack                                   |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (open-source, GPL-3.0 core)                    | Custom workflows: chain a segmentation model + alpha refinement + temporal smoothing. The right tool for tricky cases (multiple subjects, hair against a similar background, sports footage)                                     | Setup is involved (Python, models, node graph). Worth it for repeat specialty work                                  |

After running any of these externally, encode the output as a HyperFrames-compatible transparent WebM with:

```bash Terminal theme={null}
ffmpeg -i frames-%04d.png -c:v libvpx-vp9 \
  -pix_fmt yuva420p \
  -metadata:s:v:0 alpha_mode=1 \
  -auto-alt-ref 0 -cpu-used 4 -b:v 0 -crf 30 \
  transparent.webm
```

### Free desktop / GUI tools

| Tool                                                                                     | When to use it                                                                                                                       | Catch                                                                                                                                     |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| [DaVinci Resolve — Magic Mask](https://www.blackmagicdesign.com/products/davinciresolve) | You're already editing in Resolve, want a brush-based UI with manual refinement, and need to round-trip the alpha into a larger edit | macOS / Windows / Linux desktop install. The free tier covers Magic Mask; paid Studio version unlocks higher resolutions on some features |
| [Backgroundremover.app](https://backgroundremover.app) (web)                             | One-off image cutout, no signup, no watermark                                                                                        | Single images only, not video. Free tier is hosted but the underlying tool is the same `rembg` model family                               |
| [PhotoRoom Background Remover](https://www.photoroom.com/tools/background-remover) (web) | Quick one-off image, polished UI, no signup                                                                                          | Single images only, e-commerce-tuned model                                                                                                |

### Web SaaS tools (free tiers, with strings)

| Tool                                                                                  | When to use it                                                                                          | Catch                                                                                                                       |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [unscreen.com](https://www.unscreen.com)                                              | Quick one-off video, no install, drag-and-drop                                                          | **Free tier is watermarked and capped at short clips** (\~10s preview). Paid removes both. Run by the team behind remove.bg |
| [RunwayML — Green Screen](https://runwayml.com)                                       | Polished UI with brush refinement and time-aware tracking; the closest a SaaS gets to professional roto | Free tier exists but is credit-limited; serious use is a subscription                                                       |
| [Kapwing — Background Remover](https://www.kapwing.com/tools/remove-video-background) | Browser-based, integrates with their video editor                                                       | Free tier is watermarked; paid removes it                                                                                   |

### How to choose

* **Person / portrait video, web playback, MIT-clean** → use the built-in `hyperframes remove-background` (this is what it's tuned for).
* **Non-human subject** (product, animal, object) → `rembg` with `isnet-general-use`.
* **Maximum portrait quality, especially hair** → `BiRefNet` via Python.
* **Long video where edge flicker would be visible**, GPL is OK → `RVM`.
* **One-off marketing clip, no install** → DaVinci Resolve (free) for video, Backgroundremover.app for a still image.
* **Specialty case the off-the-shelf models can't handle** → ComfyUI with a custom graph.

## Troubleshooting

### Model download fails or hangs

The weights live on GitHub Releases (rembg's `v0.0.0` release, \~168 MB). If your network blocks GitHub or the download is interrupted:

```bash Terminal theme={null}
# Manually download and drop into the cache
mkdir -p ~/.cache/hyperframes/background-removal/models
curl -L -o ~/.cache/hyperframes/background-removal/models/u2net_human_seg.onnx \
  https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx
```

Subsequent `remove-background` runs skip the download and use your local copy.

### "ffmpeg and ffprobe are required"

The pipeline shells out to ffmpeg for decode + encode. Install via `brew install ffmpeg` on macOS or `sudo apt install ffmpeg` on Debian/Ubuntu. Verify with `npx hyperframes doctor`.

### The output WebM looks fully opaque in the browser

Chrome only reads the alpha plane when the WebM is encoded as `yuva420p` with the `alpha_mode=1` metadata tag. The CLI sets both. If you re-encode the output yourself (e.g. with another ffmpeg invocation), preserve those flags:

```bash Terminal theme={null}
ffmpeg -i in.webm -c:v libvpx-vp9 \
  -pix_fmt yuva420p \
  -metadata:s:v:0 alpha_mode=1 \
  -auto-alt-ref 0 -cpu-used 4 \
  out.webm
```

To verify a WebM has alpha, extract the first frame and inspect:

```bash Terminal theme={null}
ffmpeg -y -c:v libvpx-vp9 -i out.webm -frames:v 1 -pix_fmt rgba -update 1 frame0.png
```

The decoded `frame0.png` should be RGBA and have non-trivial alpha values.

### CoreML is "available" but inference fails to start

The pipeline auto-falls-back to CPU if CoreML fails to bind, with a warning. If you want to skip the CoreML attempt entirely, force CPU:

```bash Terminal theme={null}
npx hyperframes remove-background subject.mp4 -o transparent.webm --device cpu
```

### The alpha mask has rough or jagged edges

That usually means the source frame is high-contrast against a similar-toned background and the model's 320×320 inference resolution is showing through. Two paths forward:

1. Re-frame or re-shoot to give the subject a more contrasting background.
2. Try `birefnet-portrait` via `rembg` (see [Other open-source models](#other-open-source-models)) — it's higher quality at hair edges but slower and heavier.

## Reference

* CLI: [`hyperframes remove-background`](/packages/cli#remove-background)
* Eval: [Matting eval — v7](https://www.heygenverse.com/a/0dd5a431-1832-4858-862d-de7fb7d02654)
* Source model: [danielgatis/rembg](https://github.com/danielgatis/rembg)
* ONNX runtime: [`onnxruntime-node`](https://www.npmjs.com/package/onnxruntime-node)

---

# Website to Video

**Source:** https://hyperframes.heygen.com/guides/website-to-video.md

# Website to Video

> Capture any website and turn it into a production video with a single prompt.

Give your AI agent a URL and a creative direction. It captures the site, extracts the brand identity, writes a script and storyboard, generates voiceover, builds animated compositions, and delivers a renderable video.

```
"Create a 20-second product launch video from https://linear.app.
 Make it feel like an Apple keynote announcement."
```

## Getting Started

<Steps>
  <Step title="Install skills">
    Skills teach your AI agent how to capture websites and create HyperFrames compositions. Install once — they persist across sessions.

    ```bash theme={null}
    npx skills add heygen-com/hyperframes
    ```

    Works with [Claude Code](https://claude.ai/claude-code), [Cursor](https://cursor.sh), [Gemini CLI](https://github.com/google-gemini/gemini-cli), and [Codex CLI](https://github.com/openai/codex).
  </Step>

  <Step title="Prompt your agent">
    Open your agent in any directory and describe the video you want:

    ```
    Create a 25-second product launch video from https://example.com. Bold, cinematic, dark theme energy.
    ```

    The agent loads the skill when they see a URL and a video request, and runs the full pipeline — capture, design, script, storyboard, voiceover, build, validate.

    <Note>
      Agents also trigger this skill automatically when they see a URL and a video request.
    </Note>
  </Step>

  <Step title="Preview">
    ```bash theme={null}
    npx hyperframes preview
    ```

    Opens the video in your browser. Edits reload automatically.
  </Step>

  <Step title="Render to MP4">
    ```bash theme={null}
    npx hyperframes render --output my-video.mp4
    ```

    ```
    ✓ Captured 750 frames in 12.4s
    ✓ Encoded to my-video.mp4 (25.0s, 1920×1080, 6.8MB)
    ```
  </Step>
</Steps>

<Note>
  You don't need to run `npx hyperframes capture` manually — the skill instructs the agent to capture as the first step. The capture command is documented [below](#capture-command) for advanced use.
</Note>

## How the Pipeline Works

The skill follows the [Hyperframes pipeline](/guides/pipeline): seven steps, each producing a named artifact that feeds the next.

| Step            | Output                              | What happens                                                        |
| --------------- | ----------------------------------- | ------------------------------------------------------------------- |
| **Capture**     | `capture/`                          | Extract screenshots, design tokens, fonts, assets, animations       |
| **Design**      | `DESIGN.md`                         | Brand reference — colors, typography, do's and don'ts               |
| **Script**      | `SCRIPT.md`                         | Narration text with hook, story, proof, CTA                         |
| **Storyboard**  | `STORYBOARD.md`                     | Per-beat creative direction — mood, assets, animations, transitions |
| **VO + Timing** | `narration.wav` + `transcript.json` | TTS audio with word-level timestamps                                |
| **Build**       | `compositions/*.html`               | Animated HTML compositions, one per beat                            |
| **Validate**    | Snapshot PNGs                       | Visual verification before delivery                                 |

See [the pipeline guide](/guides/pipeline) for a detailed walkthrough of each step, the contents of every generated file, and how to iterate without re-running the whole pipeline. The structure is useful for any Hyperframes project, not just website captures.

## Video Types

The prompt determines the format. Include a duration and creative direction:

| Type                 | Duration | Example                                                  |
| -------------------- | -------- | -------------------------------------------------------- |
| Social ad            | 10–15s   | *"15-second Instagram reel. Energetic, fast cuts."*      |
| Product launch       | 20–30s   | *"25-second product launch. Apple keynote energy."*      |
| Product tour         | 30–60s   | *"45-second tour showing the top 3 features."*           |
| Brand reel           | 15–30s   | *"20-second brand video. Celebrate the design."*         |
| Feature announcement | 15–25s   | *"Feature announcement highlighting the new AI agents."* |
| Teaser               | 8–15s    | *"10-second teaser. Super minimal. Just the hook."*      |

<Tip>
  Creative direction matters more than format. *"Playful, hand-crafted feel"* or *"dark, developer-focused, show code"* shapes the storyboard and drives every visual decision the agent makes.
</Tip>

## Enriching Captures with Gemini Vision

By default, captures describe assets using DOM context — alt text, nearby headings, CSS classes. Add a vision API key for richer AI-powered descriptions.

Create a `.env` file in your project root with **either** a [Gemini API key](https://aistudio.google.com/apikey):

```bash theme={null}
echo "GEMINI_API_KEY=your-key-here" > .env
```

…**or**, if you don't have Google access, an [OpenRouter key](https://openrouter.ai/keys) — a single API that fronts many vision models:

```bash theme={null}
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

OpenRouter is used when its key is present (it takes priority if both are set). The default model is `google/gemini-3.1-flash-lite`; override it with `HYPERFRAMES_OPENROUTER_MODEL` (any vision-capable OpenRouter model), just as `HYPERFRAMES_GEMINI_MODEL` overrides the Gemini default.

<Tabs>
  <Tab title="Without Gemini">
    ```
    - hero-bg.png — 582KB, section: "Hero", above fold
    ```

    The agent knows the file exists and where it was on the page, but not what it looks like.
  </Tab>

  <Tab title="With Gemini">
    ```
    - hero-bg.png — 582KB, A gradient wave in purple and blue sweeps
      across a dark background, creating an aurora-like effect.
    ```

    The agent knows what the image actually shows, enabling better creative decisions in the storyboard.
  </Tab>
</Tabs>

| Tier | Rate limit | Cost per image |
| ---- | ---------- | -------------- |
| Free | 5 RPM      | Free           |
| Paid | 2,000 RPM  | \~\$0.001      |

A typical capture with 40 images costs about **\$0.04** on the paid tier.

## Capture Command

The skill runs capture automatically, but you can run it directly for pre-caching, debugging, or using the data outside of video production.

```bash theme={null}
npx hyperframes capture https://stripe.com
```

```
◇  Captured Stripe | Financial Infrastructure → capture

  Screenshots: 12
  Assets: 45
  Sections: 15
  Fonts: sohne-var
```

| Flag                | Default     | Description                                                                                    |
| ------------------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `-o, --output`      | `./capture` | Output directory (auto-suffixes to `./capture-2/`, `./capture-3/`, … if `./capture/` is taken) |
| `--timeout`         | `120000`    | Page load timeout in ms                                                                        |
| `--skip-assets`     | `false`     | Skip downloading images and fonts                                                              |
| `--max-screenshots` | `24`        | Maximum screenshot count                                                                       |
| `--json`            | `false`     | Output structured JSON for programmatic use                                                    |

### What Gets Captured

| Data            | Description                                                                     |
| --------------- | ------------------------------------------------------------------------------- |
| **Screenshots** | Viewport captures at every scroll depth — dynamic count based on page height    |
| **Colors**      | Pixel-sampled dominant colors + computed styles, including oklch/lab conversion |
| **Fonts**       | CSS font families + downloaded woff2 files                                      |
| **Assets**      | Images, SVGs with semantic names, Lottie animations, video previews             |
| **Text**        | All visible text in DOM order                                                   |
| **Animations**  | Web Animations API, scroll-triggered animations, WebGL shaders                  |
| **Sections**    | Page structure with headings, types, background colors                          |
| **CTAs**        | Buttons and links detected by class names and text patterns                     |

## Snapshot Command

Capture key frames from a built video as PNGs — verify compositions without a full render:

```bash theme={null}
npx hyperframes snapshot my-project --at 2.9,10.4,18.7
```

| Flag        | Default | Description                           |
| ----------- | ------- | ------------------------------------- |
| `--frames`  | `5`     | Number of evenly-spaced frames        |
| `--at`      | —       | Comma-separated timestamps in seconds |
| `--timeout` | `5000`  | Ms to wait for runtime to initialize  |

## Iterating

You don't need to re-run the full pipeline to make changes:

* **Edit the storyboard** — `STORYBOARD.md` is the creative north star. Change a beat's mood or assets, then ask the agent to rebuild just that beat.
* **Edit a composition** — open `compositions/beat-3-proof.html` directly and tweak animations, colors, or layout.
* **Rebuild one beat** — *"Rebuild beat 2 with more energy. Use the product screenshot as full-bleed background."*

See the [pipeline guide](/guides/pipeline#iterating) for more re-entry patterns.

## Troubleshooting

<AccordionGroup>
  <Accordion title="Capture times out">
    Increase the timeout for sites with Cloudflare or heavy client-side rendering:

    ```bash theme={null}
    npx hyperframes capture https://example.com --timeout 180000
    ```
  </Accordion>

  <Accordion title="Few assets captured">
    Sites using frameworks like Framer lazy-load images via IntersectionObserver. The capture scrolls through the page to trigger loading, but very long pages may miss images near the bottom. Adding a Gemini key improves descriptions of captured assets, but doesn't increase the count.
  </Accordion>

  <Accordion title="Colors look wrong">
    The capture uses pixel sampling combined with DOM computed styles. Dark sites should show dark colors in the palette. Check the scroll screenshots in `<output>/screenshots/` (default `./capture/screenshots/`) to see what the capture actually saw.
  </Accordion>

  <Accordion title="Agent doesn't find the skill">
    Verify skills are installed:

    ```bash theme={null}
    npx skills add heygen-com/hyperframes
    ```

    Lead your prompt with *"Use the /website-to-video skill"* for the most reliable results. Agents also discover it automatically when they see a URL and a video request.
  </Accordion>
</AccordionGroup>

## Next Steps

<CardGroup cols={2}>
  <Card title="The Pipeline" icon="list-check" href="/guides/pipeline">
    The canonical 7-step structure this workflow follows.
  </Card>

  <Card title="Quickstart" icon="rocket" href="/quickstart">
    New to HyperFrames? Start here.
  </Card>

  <Card title="GSAP Animation" icon="wand-magic-sparkles" href="/guides/gsap-animation">
    Animation patterns used in compositions.
  </Card>

  <Card title="Rendering" icon="film" href="/guides/rendering">
    Render to MP4, MOV, or WebM.
  </Card>
</CardGroup>

---

# HyperFrames vs Remotion

**Source:** https://hyperframes.heygen.com/guides/hyperframes-vs-remotion.md

# Hyperframes vs Remotion

> Why we built Hyperframes, how it differs from Remotion in practice, and where each tool fits.

[Remotion](https://www.remotion.dev) is an awesome project, and we used Remotion in HeyGen's production pipelines for many months. Remotion promoted the idea of using code to orchestrate and animate video production, and it proved that headless Chrome could be a reliable, deterministic video renderer. Several patterns in the Hyperframes source come directly from what the Remotion team pioneered — Chrome launch flags, port selection, image2pipe streaming into FFmpeg, in-order frame buffering. We kept attribution comments in our code on purpose so the lineage stays visible to anyone reading the source.

This guide is the honest breakdown of where Hyperframes and Remotion differ, written by the team that built Hyperframes. We picked different bets; each one has strengths the other doesn't, and this doc walks through both.

## Why we built Hyperframes

As we scaled our code-to-video pipelines at HeyGen, we kept running into the same kinds of limits inside a React-first authoring model. We debated internally whether to keep building on Remotion or write a renderer from scratch. Two factors pushed us to build Hyperframes.

### 1. The agent-native workflow

In our evals, LLMs writing Remotion compositions produced less creative visual outputs and needed a lot more guardrails and prompting than the same LLMs writing HTML + [GSAP](/guides/gsap-animation) compositions directly.

Two related issues compounded it:

* Animation libraries with their own internal clocks (GSAP, Anime.js, Motion One) don't compose cleanly with React's per-frame render.
* Arbitrary HTML or CSS that wasn't written as React doesn't have a clean path into a React composition — you have to rewrite it.

### 2. The human editing workflow

We want the same code to be the render layer *and* the data layer, because we need a UI for humans on top of the agentic experience.

HTML is both the render layer and the editable source of truth — the same DOM is what you see and what you edit. That makes a real visual editor (selection, drag-and-drop, property panels, timeline) much more natural to build, the same way [Paper.Design](https://paper.design) does it. With Remotion, the source of truth is code plus a build step, so round-tripping through a visual editor is painful and fragile. The Remotion team has made progress here, but it's much more difficult to build a real-time editor on top of React than on top of HTML.

We architected Hyperframes to be the most native to agents while making it easy to build a human interface on top.

## At a glance

|                                                       | **Hyperframes**                                                           | **Remotion**                                                                     |
| ----------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Authoring                                             | HTML + CSS + GSAP                                                         | React components (TSX)                                                           |
| Runtime                                               | Browser DOM, no framework                                                 | React reconciliation per frame                                                   |
| Build step                                            | None; `index.html` plays as-is                                            | Required (webpack, bundler)                                                      |
| Library-clock animations (GSAP, Anime.js, Motion One) | Seekable; frame-accurate                                                  | Plays at wall-clock during render                                                |
| Arbitrary HTML / CSS passthrough                      | Paste and animate                                                         | Rewrite as JSX                                                                   |
| Distributed rendering                                 | [AWS Lambda](/deploy/aws-lambda) support                                  | [Remotion Lambda](https://www.remotion.dev/lambda), mature and production-tested |
| [HDR output](/guides/hdr)                             | Supported                                                                 | Documented as unsupported                                                        |
| Visual editor over render source                      | Native; same DOM is editable                                              | Source is code plus a build step                                                 |
| License                                               | [Apache 2.0](https://github.com/heygen-com/hyperframes/blob/main/LICENSE) | [Commercial](https://www.remotion.pro/license)                                   |

The rest of this guide walks through what each row means and where each tool actually wins.

## The core difference: React vs HTML

Hyperframes and Remotion both drive headless Chrome. Both are deterministic. Both ship agent skills. They differ on one decision: what the primary author writes.

Remotion's bet is React. Video compositions are React components. You get typed JSX, the React ecosystem, component reuse, and the whole of React tooling. Remotion's strengths come from committing to that surface: years of production use, Lambda at hyperscale, a large community, careful type-safe APIs.

Hyperframes' bet is HTML. Video compositions are HTML pages. You can paste in a landing page, a design-system component, or a CodePen demo and animate it. We think that's the right surface for two specific use cases: AI agents writing video, and visual editors built directly on the DOM the renderer consumes.

Different bets, different strengths. The rest of this doc breaks down where each shows up.

## What the difference means in practice

### Agents express visuals better in HTML than in React

When an LLM writes Hyperframes, it's writing the medium it was trained on most heavily. The web as browsers see it — HTML, CSS, JavaScript, GSAP idioms from CodePen, 25+ years of accumulated web animation content — is the deepest well in a model's training data. React-specific sources are a much smaller slice.

From running both systems in production: an agent asked to write a Remotion composition spends tokens learning framework rules (which hooks are allowed, which APIs are forbidden, how to scaffold a project) before it can be creative. Output tends to converge on a narrow visual vocabulary — centered titles, stock transitions, conventional typography. The same agent writing HTML with GSAP reaches for a wider creative range, because that's what its training data looks like.

### Animation libraries with their own clocks

Asking an agent to port a GSAP animation or an existing web page into Remotion loses details on the first try: timing nuances, audio level relationships, text sizing. The HTML-first path avoids the translation step entirely.

We gave both tools the same 4-second GSAP timeline: 11 letters of "HYPERFRAMES" enter staggered with a back-out ease, hold for 1.5 seconds, then each letter rotates and falls out of frame. Identical animation code, identical easings, identical stagger. The only thing we changed was the renderer.

**Hyperframes output — what the animation is meant to look like:**

<img src="https://static.heygen.ai/hyperframes-oss/docs/images/comparisons/gsap-hf.gif" alt="Hyperframes GSAP render — letters enter, hold, then fall away over the full 4 seconds" />

All four seconds are used. Letters fly in one by one, the full word holds in the center for about a second and a half, then the letters spin and drop away.

**Remotion output — same timeline, same code:**

<img src="https://static.heygen.ai/hyperframes-oss/docs/images/comparisons/gsap-remotion.gif" alt="Remotion GSAP render — GSAP plays through its entire timeline in the first second, leaving most of the render as an empty stage" />

GSAP plays through its entire 4-second animation in roughly the first second of render wall-clock time. By the time Remotion captures later frames, GSAP's timeline has already completed and every letter has exited — the remainder of the render captures an empty stage.

**Why:** GSAP drives its own timeline via `performance.now()`, which ticks at real-time speed during render. Hyperframes pauses GSAP and seeks it to `frame / fps` before capturing each frame, so the library runs in lockstep with the output. Remotion has no equivalent primitive, so GSAP's internal ticker races through the timeline at wall-clock speed while Remotion captures a handful of frames during the entrance and mostly-empty frames after.

Everything GSAP supports — SplitText, ScrollTrigger, MotionPath, physics, 15 years of snippets on CodePen — works the same way in Hyperframes. The pattern generalizes to Anime.js, Motion One, and any other library with its own clock; any JS library without its own clock just works. Wrapping a library clock in a Remotion component is possible but awkward, and you give up most of what the library is good at.

See the [GSAP animation guide](/guides/gsap-animation) for how this integrates, and [Deterministic Rendering](/concepts/determinism) for how seek-driven capture works under the hood.

### Arbitrary HTML, CSS, JavaScript

Every web page is a potential Hyperframes composition. Landing pages. Claude Design artifacts. Design-system docs. CodePen embeds. You paste in the HTML and render.

Remotion asks you to translate first: rewrite HTML as JSX, convert CSS for React, wrap imperative code (Canvas, WebGL, GSAP) in React components with refs and effects. Every translation step is a chance for an agent or a human to lose fidelity or introduce bugs. The translation is round-tripping work anyway — both frameworks ultimately serve HTML to the browser to render.

The [website-to-video guide](/guides/website-to-video) walks through the full capture-to-render pipeline that the HTML-first model enables.

### Auto-fallback for edge primitives

Hyperframes has two capture modes.

* **BeginFrame mode** (Linux + `chrome-headless-shell`) drives Chrome's compositor atomically via `HeadlessExperimental.beginFrame`, producing byte-for-byte reproducible frames across machines.
* **Screenshot mode** (macOS, Windows, and as an automatic fallback) runs Chrome in real time and takes ordinary screenshots — the same approach Remotion uses.

The renderer inspects each composition at compile time and falls back to screenshot mode when it spots primitives BeginFrame can't handle: inline `<iframe>`s, raw `requestAnimationFrame` loops outside a [Frame Adapter](/concepts/frame-adapters). It injects a virtual-time shim so rAF and iframe content stay frame-driven instead of wall-clock-driven. You get a diagnostic explaining the fallback, and the render produces visibly-correct output. When the composition can run in BeginFrame mode, you get determinism for free.

In practice: GSAP timelines, CSS `@keyframes` (via the Web Animations API adapter), Lottie, Three.js, and the Web Animations API all render deterministically in BeginFrame mode. Raw canvas loops and live-web embeds get screenshot mode automatically.

### React component reuse (Remotion's home turf)

If your team already has a design system in React components, Remotion lets you compose videos from the same primitives you ship in your app. Type safety, IDE completion, cross-file refactoring — everything React brings to developer ergonomics. For teams with existing React investment, this is a real advantage Hyperframes doesn't try to match.

### Distributed rendering

[Remotion Lambda](https://www.remotion.dev/lambda) splits long videos across hundreds of AWS Lambda functions. It's mature, production-tested, and well-documented — a thing teams have used in production for years.

Hyperframes now ships an [AWS Lambda deployment path](/deploy/aws-lambda): one Lambda function behind a Step Functions workflow that fans renders out across chunk workers, stores intermediates in S3, and exposes `lambda render`, `lambda render-batch`, progress polling, and SDK usage. The surface is newer than Remotion Lambda, so the practical tradeoff is maturity versus Hyperframes' HTML-native composition model.

### Visual editing over the render source (Hyperframes' natural bet)

The DOM you render is the DOM you edit. [Hyperframes Studio](/packages/studio) previews compositions in a live iframe, and because the renderer and the editor share one DOM, direct manipulation works against the same source of truth the render pipeline consumes. That UX — click to select, drag to reposition, edit properties in a panel — already ships for captions today, with broader element coverage building out from the same architectural foundation.

Building the same editor on top of React is harder because the source of truth is code plus a build step. Round-tripping a visual edit back to JSX means re-compiling. That's why tools like [Paper.Design](https://paper.design) chose HTML as the editable source in the first place.

### HDR output

Both tools currently render through headless Chrome, which outputs sRGB. Remotion [documents this as unsupported](https://www.remotion.dev/docs/hdr). Hyperframes [supports HDR output](/guides/hdr) via a two-pass compositing pipeline that combines a DOM layer with native HLG/PQ video.

## Open source vs source-available

This is one of the clearest differences between the two projects, and one of the most common reasons teams pick one over the other.

|                 | **Hyperframes**                                                           | **Remotion**                                                |
| --------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Classification  | Open source ([OSI-approved](https://opensource.org/licenses/Apache-2.0))  | Source-available, not open source                           |
| License         | [Apache 2.0](https://github.com/heygen-com/hyperframes/blob/main/LICENSE) | [Custom Remotion License](https://www.remotion.pro/license) |
| Commercial use  | Free at any scale                                                         | Requires a paid company license above small-team thresholds |
| Per-render fees | None                                                                      | Yes, above thresholds                                       |
| Redistribution  | Permitted under Apache 2.0                                                | Restricted by the Remotion License                          |

Both projects publish their source on GitHub, but the licenses work very differently. Apache 2.0 is an [Open Source Initiative-approved license](https://opensource.org/licenses/Apache-2.0) — you can self-host, modify, redistribute, and use Hyperframes commercially at any scale with no per-render fees and no seat caps. The Remotion License is a custom commercial license: you can read the code and self-host for small teams, but commercial use above their thresholds requires a paid company license.

If open-source licensing matters to you — OSI compliance, redistribution rights, no per-use fees, long-term independence from a vendor's pricing decisions — this is a first-order decision point. If your use case fits within Remotion's free tier or your company is comfortable with a commercial license, it's a non-issue. See the [Remotion license page](https://www.remotion.pro/license) for their current terms.

We open-sourced Hyperframes under Apache 2.0 so anyone can build on it — including commercially, at any scale — and so the project can outlive any single company's priorities.

## Recap

The single difference between Remotion and Hyperframes is the choice of React vs HTML (+ CSS + JavaScript). That decision leads to many differences downstream. For our needs — most native to agents, architected to support a UI layer for humans — HTML + CSS + JavaScript was the obvious bet:

1. Agents already "think" in HTML. LLMs have seen massive amounts of web code.
2. True "one file in, video out." No `package.json`, no installs, no bundler config, no composition setup. Fewer moving parts = way fewer random failures in automated and agentic workflows.
3. Highest creative ceiling — anything the browser can render, HTML can represent.
4. HTML is both the render layer and the editable source of truth. The same DOM is what you see and what you edit.

We at HeyGen are all-in on Hyperframes, but we can't do this alone — that's why we open-sourced it under Apache 2.0, so together we can build the foundation for agentic video creation.

## Further reading

* [Deterministic Rendering](/concepts/determinism) — how seek-driven frame capture works
* [GSAP animation guide](/guides/gsap-animation) — library-clock integration in practice
* [Frame Adapters](/concepts/frame-adapters) — the extension point for animation runtimes
* [Website to video](/guides/website-to-video) — the HTML-first capture-to-render pipeline

---

# Deploy

**Source:** https://hyperframes.heygen.com/guides/deploy.md

# Deploy

> Run a Hyperframes preview + render API in the cloud from a one-click template.

Hyperframes ships two official deployment templates that wrap a composition in a small web app: an in-browser preview and a `/api/render` endpoint that produces an MP4 server-side. Both are open source, Apache-2.0, and deploy from a single button.

| Template                                                                    | Compute                                                                                           | Storage                                            | Deploy                                                                                                 |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [Vercel](https://github.com/heygen-com/hyperframes-vercel-template)         | [Vercel Sandbox](https://vercel.com/docs/vercel-sandbox) (Firecracker microVM)                    | [Vercel Blob](https://vercel.com/docs/vercel-blob) | [vercel.com/templates/ai/hyperframes-on-vercel](https://vercel.com/templates/ai/hyperframes-on-vercel) |
| [Cloudflare](https://github.com/heygen-com/hyperframes-cloudflare-template) | [Cloudflare Containers](https://developers.cloudflare.com/containers/) (Workers + Durable Object) | [R2](https://developers.cloudflare.com/r2/)        | One-click button in the repo README                                                                    |

Both templates use the same shape:

* **Preview** the bundled `ui-3d-reveal` composition in the browser via the [`<hyperframes-player>`](/packages/player) web component.
* **Render** to MP4 by POSTing to `/api/render`. The handler ships the composition to a sandboxed runtime that has Chromium, FFmpeg, and `hyperframes` pre-installed, then streams the MP4 back to object storage and returns a public URL.
* **Author locally**, deploy the preview + render API. Compositions are still built on your machine with `npx hyperframes init`, then dropped into the template's `public/compositions/` directory.

## Choosing a template

<Tabs>
  <Tab title="Vercel">
    Pick this if you already deploy on Vercel, want zero-config Blob storage, or want to reuse Vercel's CI/preview environments.

    [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fheygen-com%2Fhyperframes-vercel-template\&stores=%5B%7B%22type%22%3A%22blob%22%2C%22access%22%3A%22public%22%7D%5D)

    **What you get**

    * A Next.js app with `<hyperframes-player>` preview and a `POST /api/render` route.
    * A pre-baked Vercel Sandbox snapshot built during `next build` — cold renders skip the Chromium/FFmpeg install and restore from snapshot in \~100 ms.
    * A Vercel Blob store provisioned automatically on deploy. `BLOB_READ_WRITE_TOKEN` is injected for you.

    **Performance**

    Renders run on `standard-4` (4 vCPU). With `--workers auto`, three parallel Chrome workers cut render time meaningfully vs. single-worker. Concrete render time depends on composition length, complexity, and asset size.

    **Pricing**

    Vercel Pro plans include Sandbox credit each month. See [Vercel Sandbox pricing](https://vercel.com/docs/vercel-sandbox/pricing) for current per-vCPU and per-GB rates and the up-to-date credit allowance.

    <Note>
      Vercel Functions cap at 300s and a 50 MB compressed bundle, which can't fit Chromium + FFmpeg. The template uses Vercel Sandbox specifically because it's the purpose-built primitive for this workload — up to 5 hours of runtime and up to 8 vCPUs per render.
    </Note>
  </Tab>

  <Tab title="Cloudflare">
    Pick this if you're already on Cloudflare Workers, want R2's free egress, or want full control over the renderer image.

    [![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/heygen-com/hyperframes-cloudflare-template)

    **What you get**

    * A Worker that serves preview HTML and forwards `/api/render` requests to a `RenderContainer` Durable Object.
    * A pre-built OCI container image with Chromium + FFmpeg + `hyperframes` baked in — no install at request time.
    * An R2 bucket (`hyperframes-renders`) provisioned automatically on deploy.

    **Performance**

    Renders run on `standard-4` (4 vCPU, 12 GiB). With `--workers auto`, three parallel Chrome workers cut render time meaningfully vs. single-worker. Container instances sleep after 10 minutes of inactivity, so the next request after a quiet period pays a cold-start penalty.

    **Pricing**

    Cloudflare Containers bills per-10ms for memory, CPU, and disk; R2 storage has no egress within Cloudflare's network. Requires a [Workers Paid](https://developers.cloudflare.com/workers/platform/pricing/) plan. See [Cloudflare Containers pricing](https://developers.cloudflare.com/containers/pricing/) and [R2 pricing](https://developers.cloudflare.com/r2/pricing/) for current rates.

    <Note>
      Cloudflare's hosted [Browser Rendering](https://developers.cloudflare.com/browser-rendering/) API can't install FFmpeg — that's why the template uses Cloudflare Containers, which gives you a real OCI container in a Worker-bound Durable Object with up to 4 vCPUs and 12 GiB RAM.
    </Note>
  </Tab>
</Tabs>

## Architecture

Both templates follow the same flow: the browser plays a preview locally, then POSTs to a render endpoint that delegates to a sandboxed runtime with Chromium + FFmpeg.

```
 Browser                    Edge / Function              Sandboxed renderer
┌──────────────────┐       ┌────────────────────┐       ┌──────────────────────────┐
│ <hyperframes-    │ ────▶ │ /api/render        │ ────▶ │ hyperframes render       │
│  player>         │       │  ship composition  │       │  (Chromium + FFmpeg,     │
│ preview iframe   │       │  → renderer        │       │   pre-installed)         │
│                  │ ◀──── │  ← stream MP4      │ ◀──── │                          │
│                  │  url  │  → upload to blob  │  mp4  │                          │
└──────────────────┘       └────────────────────┘       └──────────────────────────┘
                                    │
                                    └─▶ Vercel Blob / Cloudflare R2
```

The key cost-saver in both templates is **pre-baking the renderer**. Installing Chromium system libraries plus `chrome-headless-shell` takes 30–60s, which would dominate every cold render. Vercel's template snapshots the sandbox at build time; Cloudflare's template bakes everything into the container image. Both restore in milliseconds and let you spend the entire request budget on actual rendering.

## Swapping the composition

Both templates ship with one bundled composition (`ui-3d-reveal`). To use your own:

<Steps>
  <Step title="Author locally">
    Compositions are HTML — author them on your machine with the [CLI](/packages/cli):

    ```bash Terminal theme={null}
    npx hyperframes init my-video
    cd my-video
    npx hyperframes preview
    ```
  </Step>

  <Step title="Drop the bundle into the template">
    Copy your composition into `public/compositions/<your-name>/`.
  </Step>

  <Step title="Point the template at it">
    * **Vercel**: edit `PREVIEW_COMPOSITION_DIR` at the top of `lib/preview.ts` and the dimensions in `app/page.tsx` if it isn't 1920×1080.
    * **Cloudflare**: set `PREVIEW_COMPOSITION_DIR=compositions/<your-name>` when running `npm run deploy`, or edit the default in `scripts/build.mjs`. Update player dimensions in `public/index.html` if needed.
  </Step>

  <Step title="Deploy">
    ```bash Terminal theme={null}
    # Vercel
    vercel deploy

    # Cloudflare
    npm run deploy
    ```
  </Step>
</Steps>

## When to use a template vs. roll your own

Templates are optimized for **a single render endpoint behind a preview UI**. They're the fastest way to get a hosted Hyperframes render API running. If you need:

* A **render queue** with retries, deduplication, or priorities — start from a template, then add your own queue (e.g. Vercel Queues, Cloudflare Queues, SQS).
* **Multi-tenant rendering** with per-user composition uploads — start from a template, replace the bundled composition with a runtime-fetched one.
* **Self-hosted** rendering — see the [Rendering guide](/guides/rendering) and run `hyperframes render --docker` on your own infrastructure.

For everything else, the templates are the recommended starting point.

## Next Steps

<CardGroup cols={2}>
  <Card title="Rendering" icon="film" href="/guides/rendering">
    Render compositions locally or in Docker
  </Card>

  <Card title="Player package" icon="play" href="/packages/player">
    Embed `<hyperframes-player>` in any HTML page
  </Card>

  <Card title="Vercel template" icon="github" href="https://github.com/heygen-com/hyperframes-vercel-template">
    Source on GitHub
  </Card>

  <Card title="Cloudflare template" icon="github" href="https://github.com/heygen-com/hyperframes-cloudflare-template">
    Source on GitHub
  </Card>
</CardGroup>

---

# Feedback

**Source:** https://hyperframes.heygen.com/guides/feedback.md

# Feedback Collection

> How HyperFrames collects feedback, what data is collected, and how to opt out.

HyperFrames occasionally asks how a render went or how a Studio session felt. This page explains why we do it, when prompts appear, what data is collected, and how to disable them.

## Why We Ask

We use anonymous satisfaction scores to understand whether the tool is actually working well — not just whether it runs without errors. A render that takes 10 minutes and produces a broken file counts as a success in logs but a failure in practice. The feedback prompt is the only signal we have for that gap.

No account, email, or identity is tied to responses. Each installation generates a random UUID at setup; that is the only identifier.

## How It Works

### CLI — post-render prompt

After a successful `hyperframes render`, a short prompt may appear:

```
  How was this render? [1=poor 5=great, enter to skip]
  Any details? (enter to skip)
```

**When it shows:**

* First ever successful render
* Then every 15 renders after that (16th, 31st, 46th...)
* At most once per process — re-renders in the same session don't trigger a second prompt
* Automatically suppressed in quiet mode (`--quiet`), non-TTY shells, and CI environments

The prompt has a **10-second auto-timeout** — if you don't respond, it silently disappears and the CLI continues normally.

The render interval is configurable:

```bash theme={null}
# Show prompt every 5 renders instead of 15 (useful for testing)
HYPERFRAMES_FEEDBACK_INTERVAL=5 hyperframes render --output out.mp4
```

### Studio — session feedback bar

A thin 32px bar slides in at the bottom of the preview area periodically:

* Never on the first session — only starting from the 10th
* Then every 10 sessions (10th, 20th, 30th...)
* Slides in 3 seconds after page load to avoid flash
* Auto-dismisses after 20 seconds if ignored
* After any interaction (dismiss or submit), the session counter resets — next prompt after 10 more sessions

The session interval is configurable at build time:

```
VITE_HYPERFRAMES_FEEDBACK_INTERVAL=3
```

Invalid values (non-integer, zero, negative) fall back to the default.

**Note:** Disabling CLI telemetry (`hyperframes telemetry disable`) does not suppress the Studio bar — Studio feedback is gated separately. The submitted data is still sent through the same anonymous PostHog pipeline, so the same privacy guarantees apply.

### `hyperframes feedback` command

You can submit feedback manually at any time:

```bash theme={null}
# Quick rating
hyperframes feedback --rating 5

# Rating with details
hyperframes feedback --rating 3 --comment "render succeeded but GSAP timeline didn't animate text overlay"
```

| Flag        | Description                        |
| ----------- | ---------------------------------- |
| `--rating`  | Satisfaction score, 1–5 (required) |
| `--comment` | Optional free-text details         |

This command collects a doctor summary automatically, flushes telemetry, and exits. It appears under the **Settings** group in `hyperframes --help`.

## Agent Runtimes

When an AI agent is detected, HyperFrames **skips the interactive readline prompt** and prints a structured hint instead:

```
  [hyperframes] Agent feedback: hyperframes feedback --rating <1-5> --comment "..."
```

Agents can then submit feedback using the `hyperframes feedback` command above.

The same cadence gate applies: the hint only appears on the first render, then every 15th.

**Detected agents and their markers:**

| Agent                | Environment markers                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------- |
| Claude Code          | `CLAUDECODE` present, or `CLAUDE_CODE_ENTRYPOINT` present                                         |
| Codex                | `CODEX_THREAD_ID`, `CODEX_CI`, or `CODEX_SANDBOX_NETWORK_DISABLED` present                        |
| Cursor               | `TERM_PROGRAM` equals `cursor`                                                                    |
| GitHub Copilot Agent | `GITHUB_ACTIONS` equals `true` and (`COPILOT_AGENT_ID` present or `RUNNER_NAME` equals `Copilot`) |
| Replit               | `REPL_ID` or `REPLIT_USER` present                                                                |
| Hermes               | `HERMES_QUIET` present                                                                            |
| openclaw             | `OPENCLAW_STATE_DIR` or `OPENCLAW_CONFIG_PATH` present                                            |
| Pi                   | `PI_CODING_AGENT` present                                                                         |

Only the existence (or in some cases the value) of these variables is checked — API keys and secrets that happen to share a prefix are never read.

## What Is Collected

### CLI feedback

| Field                | Value                                  |
| -------------------- | -------------------------------------- |
| `$survey_id`         | `render_satisfaction`                  |
| `$survey_response`   | Rating (1–5)                           |
| `$survey_response_2` | Free-text comment (only when provided) |
| `render_duration_ms` | Time the render took in milliseconds   |
| `doctor_summary`     | System context (see below)             |

The `doctor_summary` is a compact string with environment context — included automatically so you don't need to run `hyperframes doctor` when reporting a problem:

```
os=darwin/arm64 node=v22.11.0 cpu=10cores mem=32GB ffmpeg=yes
```

It may also include `wsl` or sandbox runtime flags when those environments are detected.

### Studio feedback

| Field                | Value                                                                      |
| -------------------- | -------------------------------------------------------------------------- |
| `$survey_id`         | `studio_experience`                                                        |
| `$survey_response`   | Rating (1–5)                                                               |
| `$survey_response_2` | Free-text comment (only when provided)                                     |
| `source`             | `studio`                                                                   |
| `doctor_summary`     | Browser context (platform, screen, CPU cores, device memory, network type) |

## What Is NOT Collected

* File paths or project names
* Composition content, HTML, or video files
* Environment variable values
* Personally identifiable information
* IP addresses or precise location

Feedback is anonymous. Each installation has a random UUID (`anonymousId`) — there is no account, login, or email association.

## Config File

The CLI persists feedback state in `~/.hyperframes/config.json`:

```json theme={null}
{
  "telemetryEnabled": true,
  "anonymousId": "a1b2c3d4-...",
  "telemetryNoticeShown": true,
  "commandCount": 47,
  "renderSuccessCount": 14,
  "lastFeedbackPromptAt": 1
}
```

| Field                  | Description                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- |
| `renderSuccessCount`   | Total successful renders across all sessions                                                                  |
| `lastFeedbackPromptAt` | The `renderSuccessCount` value when the prompt last appeared — used to compute whether 15 renders have passed |

Studio stores the equivalent state in `localStorage` under the `hyperframes-studio:` prefix.

## Opting Out

### CLI — disable telemetry entirely

Disabling telemetry suppresses the CLI feedback prompt and all other CLI usage tracking:

```bash theme={null}
# Via CLI command (persisted to ~/.hyperframes/config.json)
hyperframes telemetry disable

# Or via environment variable (per-session)
HYPERFRAMES_NO_TELEMETRY=1 hyperframes render --output out.mp4

# Or via DO_NOT_TRACK (respects the global standard)
DO_NOT_TRACK=1 hyperframes render --output out.mp4
```

Once disabled, the `hyperframes feedback` command will print `Telemetry is disabled. Feedback not sent.` and exit without sending anything.

### CLI — suppress output without disabling telemetry

```bash theme={null}
# Quiet mode: renders without any post-render output (including the feedback prompt)
hyperframes render --quiet --output out.mp4
```

### CI environments

The CLI feedback prompt is automatically suppressed when the `CI` environment variable is set (GitHub Actions, CircleCI, etc. set this by default).

### Studio

The Studio feedback bar is not affected by the CLI telemetry setting. To disable it at build time, set:

```
VITE_HYPERFRAMES_NO_FEEDBACK=1
```

When set to `"1"`, the bar never shows — `shouldShowFeedback()` returns `false` unconditionally regardless of session count or `localStorage` state.

The session interval is still configurable independently:

```
VITE_HYPERFRAMES_FEEDBACK_INTERVAL=20
```

## Related

* [Telemetry](/packages/cli#telemetry) — full telemetry settings and what usage data is collected
* [`hyperframes feedback`](/packages/cli#feedback) — CLI command reference
* [Troubleshooting](/guides/troubleshooting) — if a prompt is blocking your pipeline unexpectedly
