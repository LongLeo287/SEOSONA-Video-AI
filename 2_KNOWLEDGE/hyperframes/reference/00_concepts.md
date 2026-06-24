# HyperFrames — Core Concepts

Source: https://hyperframes.heygen.com/concepts/{compositions,data-attributes,determinism,frame-adapters,variables}.md (fetched 2026-06-24)

HyperFrames is the CORE render engine of SEOSONA Video. This file combines the 5 foundational concept docs: Compositions, Data Attributes, Deterministic Rendering, Frame Adapters, and Variables.

---

# Compositions

> The fundamental building block of a Hyperframes video.

A composition is an HTML document that defines a video timeline. Every clip -- video, image, audio -- lives inside a composition.

## Structure

Every composition needs a root element with `data-composition-id`:

```html index.html
<div id="root" data-composition-id="root"
     data-start="0" data-width="1920" data-height="1080">
  <!-- Elements go here -->
</div>
```

The `index.html` file is the top-level composition. It can contain nested compositions within it. Any composition can be imported into another -- there is no special "root" type.

## Clip Types

A clip is any discrete block on the timeline, represented as an HTML element with data attributes:

* `<video>` -- Video clips, B-roll, A-roll
* `<img>` -- Static images, overlays
* `<audio>` -- Music, sound effects
* `<div data-composition-id="...">` -- Nested compositions (animations, grouped sequences)

See the HTML Schema Reference (01_html_schema_reference.md) for the full list of attributes on each clip type.

## Nested Compositions

You can embed one composition inside another in two ways: loading from an external file or defining it inline. External files are the recommended approach for reusable compositions.

### External file

Reference another HTML file with `data-composition-src`. The framework automatically fetches the file, extracts the `<template>` content, mounts it, executes scripts, and registers the timeline.

```html index.html
<div
  id="el-5"
  data-composition-id="intro-anim"
  data-composition-src="compositions/intro-anim.html"
  data-start="0"
  data-track-index="3"
></div>
```

Each external composition file wraps its content in a `<template>` tag:

```html compositions/intro-anim.html
<template id="intro-anim-template">
  <div data-composition-id="intro-anim" data-width="1920" data-height="1080">
    <div class="title">Welcome!</div>

    <style>
      [data-composition-id="intro-anim"] .title {
        font-size: 72px; color: white; text-align: center;
      }
    </style>

    <script>
      const tl = gsap.timeline({ paused: true });
      tl.from(".title", { opacity: 0, y: -50, duration: 1 });
      window.__timelines["intro-anim"] = tl;
    </script>
  </div>
</template>
```

### Inline

Define a nested composition directly inside the parent. This is simpler for one-off compositions that do not need to be reused.

```html index.html
<div id="root" data-composition-id="root"
     data-start="0" data-width="1920" data-height="1080">

  <!-- Inline nested composition -->
  <div id="el-5" data-composition-id="intro-anim"
       data-start="0" data-track-index="3"
       data-width="1920" data-height="1080">
    <div class="title">Welcome!</div>
  </div>

  <script>
    // Timeline for the inline composition
    const introTl = gsap.timeline({ paused: true });
    introTl.from(".title", { opacity: 0, y: -50, duration: 1 });
    window.__timelines["intro-anim"] = introTl;
  </script>
</div>
```

Inline compositions do not use `<template>` tags or `data-composition-src`.

### Project Structure

```
project/
  index.html
  compositions/
    intro-anim.html
    caption-overlay.html
    outro-title.html
  assets/
    video.mp4
    music.mp3
    logo.png
```

## Two Layers: Primitives and Scripts

Every composition has two layers:

* **HTML** -- primitive clips (`video`, `img`, `audio`, nested compositions). The declarative structure: what plays, when, and on which track. Controlled by data attributes.
* **Script** -- effects, transitions, dynamic DOM, canvas, SVG -- creative animation via GSAP. Scripts do **not** control media playback or clip visibility.

> WARNING: Never use scripts to play/pause/seek media elements or to show/hide clips based on timing. The framework handles this automatically from data attributes. Scripts that duplicate this behavior will conflict with the framework.

## Variables (composition-level)

HyperFrames does not automatically bind `data-var-*` attributes into your composition DOM or CSS.

The supported pattern is:

1. Declare the variables once on the sub-comp's `<html>` root with `data-composition-variables` (id + type + default).
2. Pass per-instance values on each composition host with `data-variable-values`.
3. Read the resolved values inside the composition with `window.__hyperframes.getVariables()`. The runtime layers the host's `data-variable-values` over the declared defaults on a per-instance basis, so the same source can be embedded multiple times with different values.

```html index.html
<div
  data-composition-id="card-pro"
  data-composition-src="compositions/card.html"
  data-start="0"
  data-track-index="1"
  data-variable-values='{"title":"Pro","color":"#ff4d4f"}'
></div>
<div
  data-composition-id="card-enterprise"
  data-composition-src="compositions/card.html"
  data-start="card-pro"
  data-track-index="1"
  data-variable-values='{"title":"Enterprise","color":"#22c55e"}'
></div>
```

```html compositions/card.html
<html data-composition-variables='[
  {"id":"title","type":"string","label":"Title","default":"Fallback"},
  {"id":"color","type":"color","label":"Color","default":"#111827"}
]'>
  <body>
    <div data-composition-id="card" data-width="1920" data-height="1080">
      <h1 class="title"></h1>

      <style>
        [data-composition-id="card"] {
          --card-color: #111827;
        }
        [data-composition-id="card"] .title {
          color: var(--card-color);
        }
      </style>

      <script>
        // Inside a sub-comp script, getVariables() returns the per-instance
        // values: declared defaults < host data-variable-values overrides.
        const { title, color } = __hyperframes.getVariables();
        const root = document.querySelector('[data-composition-id="card"]');
        root.querySelector(".title").textContent = title;
        root.style.setProperty("--card-color", color);
      </script>
    </div>
  </body>
</html>
```

If you are building tooling on top of `@hyperframes/core`, the same `data-composition-variables` array is readable via `extractCompositionMetadata()` for Studio editing UI and analysis pipelines.

## Listing Compositions

```bash
npx hyperframes compositions
```

---

# Data Attributes

> Core attributes for controlling element timing and behavior.

Hyperframes uses HTML data attributes to control timing, media playback, and composition structure. These are the declarative building blocks of every video.

## Timing Attributes

| Attribute          | Example            | Description                                                                                                                        |
| ------------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| `data-start`       | `"0"` or `"intro"` | Start time in seconds, or a clip ID reference for relative timing                                                                  |
| `data-duration`    | `"5"`              | Duration in seconds. Required for images. Optional for video/audio (defaults to source duration). Not used on compositions.        |
| `data-track-index` | `"0"`              | Timeline track number. Controls z-ordering (higher = in front) and groups clips into rows. Clips on the same track cannot overlap. |

## Media Attributes

| Attribute          | Example  | Description                                                 |
| ------------------ | -------- | ----------------------------------------------------------- |
| `data-media-start` | `"2"`    | Media playback offset / trim point in seconds. Default: `0` |
| `data-volume`      | `"0.8"`  | Audio/video volume, 0 to 1                                  |
| `data-has-audio`   | `"true"` | Indicates video has an audio track                          |

## Composition Attributes

| Attribute                    | Example                                                                | Description                                                                                                                                                                                                                                                                          |
| ---------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data-composition-id`        | `"root"`                                                               | Unique ID for composition wrapper (required on every composition)                                                                                                                                                                                                                   |
| `data-width`                 | `"1920"`                                                               | Composition width in pixels                                                                                                                                                                                                                                                         |
| `data-height`                | `"1080"`                                                               | Composition height in pixels                                                                                                                                                                                                                                                        |
| `data-composition-src`       | `"./intro.html"`                                                       | Path to external composition HTML file                                                                                                                                                                                                                                              |
| `data-variable-values`       | `'{"title":"Hello"}'`                                                  | JSON object of values passed to a nested composition. Inside the sub-composition, read them via `window.__hyperframes.getVariables()` — the runtime layers these over the sub-comp's own `data-composition-variables` defaults and exposes the merged result on a per-instance basis. |
| `data-composition-variables` | `'[{"id":"title","type":"string","label":"Title","default":"Hello"}]'` | JSON array of declared variables (`id`, `type`, `label`, `default`). Drives Studio editing UI and provides defaults read by `window.__hyperframes.getVariables()`. The CLI flag `hyperframes render --variables '<json>'` overrides these defaults at top-level render time; host elements override them per-instance via `data-variable-values`. |

## Element Visibility

Add `class="clip"` to all timed elements so the runtime can manage their visibility lifecycle:

```html index.html
<h1 id="title" class="clip"
    data-start="0" data-duration="5" data-track-index="0">
  Hello World
</h1>
```

## Relative Timing

A clip can reference another clip's `id` in its `data-start` attribute. This means "start when that clip ends":

```html index.html
<video id="intro" data-start="0" data-duration="10" data-track-index="0" src="..."></video>
<video id="main" data-start="intro" data-duration="20" data-track-index="0" src="..."></video>
<video id="outro" data-start="main" data-duration="5" data-track-index="0" src="..."></video>
```

`main` resolves to second 10, `outro` resolves to second 30. If `intro`'s duration changes, downstream clips shift automatically.

### Offsets (Gaps and Overlaps)

Add `+ N` or `- N` after the ID to offset from the end of the referenced clip:

```html index.html
<!-- 2-second gap after intro -->
<video id="scene-a" data-start="intro + 2" data-duration="20"
       data-track-index="0" src="..."></video>

<!-- 0.5-second overlap with intro (crossfade) -->
<video id="scene-b" data-start="intro - 0.5" data-duration="20"
       data-track-index="1" src="..."></video>
```

> NOTE: Overlapping clips must be on different tracks -- clips on the same track cannot overlap in time.

### Relative timing rules and constraints

**Same composition only** -- references resolve within the clip's parent composition. You cannot reference a clip in a sibling or parent composition.

**No circular references** -- A cannot start after B if B starts after A. The resolver detects cycles and throws an error.

**Referenced clip must have a known duration** -- either an explicit `data-duration` or a duration inferred from source media. If the referenced clip has no known duration, the reference cannot resolve.

**Parsing rules** -- if the value is a valid number, it is treated as absolute seconds. Otherwise it is parsed as one of:

* `<id>` -- start when that clip ends
* `<id> + <number>` -- start N seconds after that clip ends
* `<id> - <number>` -- start N seconds before that clip ends

**Chain length** -- references can chain (`A` -> `B` -> `C`), but deeply nested chains make the timeline harder to reason about. Keep chains under 3-4 levels for readability.

---

# Deterministic Rendering

> Same input, identical output. Every time.

Hyperframes is built around a core guarantee: **the same composition always produces the same video**. This is what makes automated pipelines, CI testing, and AI-driven workflows reliable.

## How It Works

The rendering pipeline is frame-by-frame and seek-driven. No realtime playback is involved -- every frame is independently seeked and captured.

1. **Frame clock** — The engine computes the time for each frame using integer math: `time = floor(frame) / fps`. There is no wall-clock dependency -- rendering is entirely decoupled from real time.
2. **Seek** — The frame adapter receives a `seekFrame(frame)` call and deterministically positions all animations, DOM state, and canvas content to the exact frame. The adapter's `renderSeek` pauses all GSAP timelines and seeks them to the computed time.
3. **Capture** — Chrome's `HeadlessExperimental.beginFrame` API captures the pixel buffer for the current frame. This is a single, atomic operation -- no partial paints or race conditions.
4. **Encode** — FFmpeg encodes the captured frames into the final MP4 video. Audio tracks from `<audio>` and `<video>` elements are mixed in during this stage.

Pipeline: `Frame Clock (t = frame / fps)` → `Seek (adapter.seekFrame(frame))` → `Capture (beginFrame API)` → `Encode (FFmpeg)` → `MP4`

## What Makes It Deterministic

* **No wall-clock dependencies** -- rendering does not use `Date.now()`, `requestAnimationFrame`, or system timers
* **No unseeded randomness** -- `Math.random()` without a seed breaks determinism
* **No render-time network fetches** -- all assets must be loaded before rendering starts
* **Fixed output parameters** -- `fps`, `width`, and `height` are locked before the first frame
* **Finite duration** -- every composition has a known, finite length

These same rules apply to every frame adapter. If you are building a custom adapter, you must follow the determinism contract.

## Docker Mode

For maximum reproducibility, render in Docker:

```bash
npx hyperframes render --docker --output output.mp4
```

Docker mode uses an exact Chrome version and font set, ensuring:

* Same Chromium rendering engine across all platforms
* Same system fonts (no platform-specific font substitution)
* Same FFmpeg encoder version

## Preview vs. Render Parity

The browser preview and the rendered MP4 should match. Hyperframes achieves this through:

* **One runtime** -- the same `hyperframe.runtime` drives both preview and render
* **Producer-canonical behavior** -- the producer's seek semantics are the source of truth
* **Readiness gates** -- `__playerReady` and `__renderReady` ensure the composition is fully loaded before any frame is captured

Parity here means **visual fidelity** — every frame looks the same. It does *not* mean performance parity. Preview plays in real time in a browser, so frame-rate limits are bound by your hardware. Render is seek-driven and frame-at-a-time, so it never drops frames regardless of per-frame cost. A composition can stutter in preview and render perfectly.

> NOTE: Local rendering (without Docker) may show slight differences due to platform-specific font rendering and Chrome version. Use Docker mode when exact reproducibility matters.

## For Adapter Authors

If you are building a frame adapter, your adapter must follow the determinism contract:

* `seekFrame(frame)` must be idempotent -- same frame, same result
* No side effects that depend on call order (must handle random access)
* No async operations that resolve after the frame is "committed"
* Clean lifecycle: `init` -> `seekFrame` (N times) -> `destroy`

---

# Frame Adapters

> Bring your own animation runtime to Hyperframes.

The Frame Adapter pattern is how Hyperframes supports multiple animation runtimes. The core question every adapter answers:

> What should the screen look like at frame N?

If a runtime can answer that, it can plug into Hyperframes.

> INFO: The Adapter API is currently at **v0** (experimental). Breaking changes are possible until v1. The core contract (seek-by-frame, deterministic output) is stable, but method signatures may evolve.

## How It Works

The host application (the engine or producer) drives rendering by calling adapter methods in a strict sequence. The adapter never controls its own clock -- it only responds to seek commands.

Sequence: `init(context)` → ready → `getDurationFrames()` → for each frame 0..N: normalize frame (clamp, floor) → `seekFrame(frame)` → adapter updates DOM/canvas state → host captures pixel buffer. Then `destroy()`.

## Adapter API (v0)

```typescript adapters/types.ts
type FrameAdapterContext = {
  compositionId: string;
  fps: number;
  width: number;
  height: number;
  rootElement?: HTMLElement;
};

type FrameAdapter = {
  id: string;
  init?: (ctx: FrameAdapterContext) => Promise<void> | void;
  getDurationFrames: () => number;
  seekFrame: (frame: number) => Promise<void> | void;
  destroy?: () => Promise<void> | void;
};
```

## Required Semantics

* `getDurationFrames()` must return a finite integer >= 0
* `seekFrame(frame)` must support arbitrary seek order (forward, backward, random)
* `seekFrame(frame)` must be idempotent for the same input frame
* `seekFrame(frame)` must clamp internal time to the adapter's range
* Adapters should be paused/seek-driven, not clock-driven

## Host Orchestration

The host normalizes frames before calling the adapter:

```typescript engine/render-loop.ts
normalizedFrame = clamp(Math.floor(frame), 0, durationFrames);
```

A typical render loop:

```typescript engine/render-loop.ts
await adapter.init?.({ compositionId, fps, width, height, rootElement });
const durationFrames = adapter.getDurationFrames();

for (let frame = 0; frame <= durationFrames; frame += 1) {
  await adapter.seekFrame(frame);
  // capture pixel buffer for this frame
}

await adapter.destroy?.();
```

## Determinism Contract

These rules are non-negotiable for any adapter:

* Canonical clock: `t = frame / fps`
* No wall-clock dependencies (`Date.now`, drift-dependent logic)
* No unseeded randomness
* No render-time network fetches
* Fixed output params (`fps`, `width`, `height`)
* Finite duration only
* Deterministic frame quantization before seek

## Supported Runtimes (first-party adapters)

All runtime adapters live in the `/hyperframes-animation` skill.

| Runtime            | Seek Method                                                                    | Skill                    |
| ------------------ | ------------------------------------------------------------------------------ | ------------------------ |
| GSAP               | `timeline.totalTime(timeSeconds)` or `timeline.seek(timeSeconds)`              | `/hyperframes-animation` |
| Anime.js           | `instance.seek(timeMs)` for animations registered on `window.__hfAnime`        | `/hyperframes-animation` |
| CSS keyframes      | Browser `Animation.currentTime`, with paused negative-delay fallback           | `/hyperframes-animation` |
| Lottie / dotLottie | `goToAndStop(timeMs, false)`, raw-frame setters, or player seek APIs           | `/hyperframes-animation` |
| Three.js / WebGL   | `hf-seek` events plus `window.__hfThreeTime` for deterministic scene rendering | `/hyperframes-animation` |
| Web Animations API | `document.getAnimations()` and `animation.currentTime`                         | `/hyperframes-animation` |

## Conformance Tests

Every adapter should pass these minimum tests:

1. **Repeatability** -- seek same frame twice, get identical output
2. **Random seek** -- seek order `[90, 10, 50, 10]` produces deterministic results
3. **Bounds** -- negative and overflow frame values do not break
4. **Duration** -- returned duration is a finite integer
5. **Cleanup** -- no leaked timers/listeners after `destroy`

---

# Variables

> Parameterize compositions so the same source can render different content.

Variables let you declare named, typed slots in a composition and fill them at render time — from a parent composition, from the CLI, or from an API call. A card composition that takes `title` and `color` can be embedded a hundred times with a hundred different values without duplicating any HTML.

## Declaring Variables

Add `data-composition-variables` to the `<html>` root of any composition. Its value is a JSON array of variable declarations — one object per variable:

```html compositions/card.html
<html data-composition-variables='[
  {"id":"title",  "type":"string",  "label":"Title",  "default":"Hello"},
  {"id":"color",  "type":"color",   "label":"Color",  "default":"#111827"},
  {"id":"price",  "type":"number",  "label":"Price",  "default":0,        "unit":"$"},
  {"id":"featured","type":"boolean","label":"Featured","default":false},
  {"id":"plan",   "type":"enum",    "label":"Plan",   "default":"pro",
   "options":[{"value":"pro","label":"Pro"},{"value":"enterprise","label":"Enterprise"}]}
]'>
```

Every declaration requires four fields: `id`, `type`, `label`, and `default`. `id` must be unique within the composition.

## Variable Types

| Type      | `default` value          | Extra options                                                    |
| --------- | ------------------------ | ---------------------------------------------------------------- |
| `string`  | `"some text"`            | `placeholder?: string`, `maxLength?: number`                     |
| `number`  | `0`                      | `min?: number`, `max?: number`, `step?: number`, `unit?: string` |
| `color`   | `"#rrggbb"`              | —                                                                |
| `boolean` | `true` / `false`         | —                                                                |
| `enum`    | one of the option values | `options: [{value: string, label: string}]`                      |

The Studio editing UI uses `label`, `type`, and the type-specific options to render the right input widget for each variable.

## What can be a variable

The five declared types cover typed primitive data. For everything else, a `string` variable holding a URL is the escape hatch: your composition reads the URL and assigns it to whatever DOM element needs it.

### Parameterizing media assets

The same composition can render different images, video clips, or audio tracks just by swapping URLs through a string variable:

```html compositions/product-card.html
<html data-composition-variables='[
  {"id":"productImage","type":"string","label":"Product image URL","default":"https://cdn.example.com/products/default.png"},
  {"id":"productName","type":"string","label":"Product name","default":"Untitled"}
]'>
  <body>
    <div data-composition-id="product-card" data-width="1920" data-height="1080" data-duration="5">
      <img class="product-img" alt="" />
      <h1 class="product-name"></h1>

      <script>
        const {
          productImage = "https://cdn.example.com/products/default.png",
          productName = "Untitled",
        } = __hyperframes.getVariables();
        const root = document.querySelector('[data-composition-id="product-card"]');
        root.querySelector(".product-img").src = productImage;
        root.querySelector(".product-name").textContent = productName;
      </script>
    </div>
  </body>
</html>
```

> NOTE: The runtime probes the DOM after your composition script runs, so a `<video>` or `<audio>` `src` assigned at runtime from a variable is discovered and pre-extracted for the render. Just set the `src` from your variable.

The pattern covers the three media element types:

* **`<img src>`** — assign from a string variable. Chrome fetches it during capture like any other image; no extra config.
* **`<video src>`** — assign from a string variable, but keep the timing attributes (`data-start`, `data-duration`, `data-track-index`, `data-has-audio`) on the element itself. The probe phase scans `video[data-start]` elements after your script runs and reads the resolved `src` for pre-extraction.
* **`<audio src>`** — same as video. The audio is decoded during capture and mixed into the final output.

Pass assets as URL references your composition resolves at render time; don't inline base64. URL-shaped assets travel cleanly through both the local renderer and the Lambda surface (256 KiB execution-input cap on distributed renders).

### Parameterizing media color grading

Media color grading can read exact variable references inside `data-color-grading`. Use `$name` or `${name}` as the entire value for a field; the runtime resolves it from the current composition's variables before applying the shader grading:

```html compositions/hero.html
<html data-composition-variables='[
  {"id":"gradingPreset","type":"enum","label":"Color grading preset","default":"warm-clean",
   "options":[{"value":"warm-clean","label":"Warm Clean"},{"value":"cool-clean","label":"Cool Clean"}]},
  {"id":"gradingIntensity","type":"number","label":"Color grading intensity","default":0.75,"min":0,"max":1,"step":0.05},
  {"id":"gradingExposure","type":"number","label":"Exposure","default":0,"min":-2,"max":2,"step":0.05}
]'>
  <body>
    <div data-composition-id="hero" data-width="1920" data-height="1080">
      <video
        id="hero-video"
        src="assets/hero.mp4"
        data-start="0"
        data-track-index="0"
        muted
        playsinline
        data-color-grading='{
          "preset":"$gradingPreset",
          "intensity":"$gradingIntensity",
          "adjust":{"exposure":"${gradingExposure}"},
          "colorSpace":"rec709"
        }'
      ></video>
    </div>
  </body>
</html>
```

### Swapping media: do you need to vary duration too?

Usually no. `data-duration` is optional on `<video>` and `<audio>` — leave it off and the renderer ffprobes the source and uses its natural length:

```html compositions/hero.html
<video id="hero" data-start="0" data-track-index="0"></video>
<script>
  document.getElementById("hero").src = __hyperframes.getVariables().heroVideo;
</script>
```

To clamp or pin the clip to a specific length per render, expose duration as its own `number` variable and apply it via the same script:

```html compositions/hero.html
<video id="hero" data-start="0" data-track-index="0"></video>
<script>
  const { heroVideo, heroDuration } = __hyperframes.getVariables();
  const el = document.getElementById("hero");
  el.src = heroVideo;
  if (heroDuration !== undefined) {
    el.setAttribute("data-duration", String(heroDuration));
  }
</script>
```

The probe phase reads `data-duration` from the live DOM after your script runs, so an attribute written programmatically behaves identically to one baked into the source HTML.

## What can't be a variable

| What                                        | Mechanism (not a variable)                                                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Composition dimensions                      | `data-width` / `data-height` on the composition element — parsed from the source HTML at compile time, not from the live DOM |
| Frame rate                                  | `--fps` flag on `hyperframes render`, or `config.fps` in the SDK                                                              |
| Output format / codec / quality             | `--format` / `--codec` / `--quality` flags, or the SDK equivalents                                                            |
| A sibling or parent composition's variables | Variables are per-composition; use `data-variable-values` on each sub-comp host element to pass overrides                     |

The deeper rule: variables are runtime values your script applies to the DOM. They can drive anything the renderer reads from the live DOM after that script runs — text, colors, media `src`, even clip `data-duration`. They can't change inputs the renderer reads once at compile time (dimensions) or that live entirely outside the composition (CLI flags, encoder settings).

## Reading Variables at Runtime

Inside any composition script, call `window.__hyperframes.getVariables()` to get the resolved variable values. The return type is `Partial<Record<string, unknown>>` — use destructuring with defaults matching the declared `default` values:

```html compositions/card.html
<html data-composition-variables='[
  {"id":"title","type":"string","label":"Title","default":"Untitled"},
  {"id":"color","type":"color","label":"Color","default":"#111827"}
]'>
  <body>
    <div data-composition-id="card" data-width="1920" data-height="1080">
      <h1 class="card-title"></h1>

      <style>
        [data-composition-id="card"] { --card-color: #111827; }
        [data-composition-id="card"] .card-title { color: var(--card-color); }
      </style>

      <script>
        const { title = "Untitled", color = "#111827" } = __hyperframes.getVariables();
        const root = document.querySelector('[data-composition-id="card"]');
        root.querySelector(".card-title").textContent = title;
        root.style.setProperty("--card-color", color);
      </script>
    </div>
  </body>
</html>
```

`__hyperframes.getVariables()` is a shorthand for `window.__hyperframes.getVariables()` and works in both top-level and sub-composition scripts. The runtime automatically scopes sub-compositions so each instance sees its own resolved values.

## Per-instance Overrides (Sub-compositions)

When embedding a composition inside another, use `data-variable-values` on the host element to pass a JSON object of override values for that particular instance:

```html index.html
<div
  data-composition-id="card-pro"
  data-composition-src="compositions/card.html"
  data-start="0"
  data-track-index="1"
  data-variable-values='{"title":"Pro","color":"#ff4d4f"}'
></div>
<div
  data-composition-id="card-enterprise"
  data-composition-src="compositions/card.html"
  data-start="card-pro"
  data-track-index="1"
  data-variable-values='{"title":"Enterprise","color":"#22c55e"}'
></div>
```

## CLI Overrides (Top-level Renders)

```bash
# Inline JSON
npx hyperframes render --variables '{"title":"Q4 Report","color":"#1d4ed8"}' --output q4.mp4

# JSON file
npx hyperframes render --variables-file ./vars.json --output out.mp4

# Fail on undeclared or mistyped variables
npx hyperframes render --variables '{"title":"Q4 Report"}' --strict-variables --output out.mp4
```

`--strict-variables` turns variable warnings into errors. Any variable in `--variables` not declared in `data-composition-variables`, or whose value does not match the declared type, causes the render to exit non-zero.

> NOTE: CLI overrides apply only to the top-level composition. Sub-composition variables are controlled by `data-variable-values` on each host element.

## Batch Renders

```json rows.json
[
  { "name": "Alice", "title": "Q4 Report" },
  { "name": "Bob", "title": "Renewal Plan" }
]
```

```bash
npx hyperframes render --batch rows.json --output "renders/{name}.mp4" --strict-variables
```

Each row is treated like a `--variables` object and merged over the composition defaults. Output paths support `{key}` placeholders from the row plus `{index}`. Hyperframes validates missing placeholders, output collisions, and `--strict-variables` issues before the first row starts rendering, then writes `manifest.json` next to the outputs with one status row per render. `--batch-concurrency 2` can run rows in parallel (default `1`).

## Layering and Precedence

| Source                      | Precedence | Where declared                                      |
| --------------------------- | ---------- | --------------------------------------------------- |
| Declared defaults           | Lowest     | `data-composition-variables` on `<html>`            |
| Per-instance host overrides | Middle     | `data-variable-values` on the sub-comp host element |
| CLI `--variables` flag      | Highest    | `hyperframes render --variables '{...}'`            |

A missing key at any layer falls through to the next lower layer. If no layer provides a value, the declared `default` is used.

## Validation

The linter checks variable declarations statically (`npx hyperframes lint`): catches malformed JSON, missing required fields (`id`, `type`, `label`, `default`), and type mismatches between `type` and the `default` value.

At render time, the CLI validates `--variables` against the schema and reports issues as warnings (or errors with `--strict-variables`):

* **undeclared** — a key in `--variables` has no matching `id` in `data-composition-variables`
* **type-mismatch** — the value's JS type does not match the declared `type`
* **enum-out-of-range** — an enum value is not in the declared `options` list

## Inspecting Variables Programmatically

```typescript
import { extractCompositionMetadata } from "@hyperframes/core";
import { readFileSync } from "node:fs";

const html = readFileSync("compositions/card.html", "utf8");
const { variables } = extractCompositionMetadata(html);
// variables is CompositionVariable[]
```

This is the same API the Studio editing UI uses to build the variables panel for each composition.
