# HyperFrames Package — @hyperframes/shader-transitions

Source: https://hyperframes.heygen.com/packages/shader-transitions.md (fetched 2026-06-24)

> WebGL shader transitions for HyperFrames scenes and compositions.

Adds GPU-accelerated scene-to-scene transitions. Captures scene samples, uploads them as WebGL textures, drives fragment-shader compositing from a GSAP timeline. The 13 transition shaders + the `init()` API.

```bash
npm install @hyperframes/shader-transitions
```

Browser global build:
```html
<script src="https://cdn.jsdelivr.net/npm/@hyperframes/shader-transitions/dist/index.global.js"></script>
```

## When to Use

* Add shader-based scene transitions (domain warp, whip pan, glitch, iris, light leak, thermal distortion, …)
* Attach GPU transitions to an existing GSAP timeline
* Build a transition picker / validation UI around the shader registry
* Feature-detect native HTML-in-canvas capture support
* Use the producer's deterministic page-side compositor for render-mode captures

## Package Exports
| Import | Description |
| --- | --- |
| `init()` | Creates or augments a GSAP timeline with shader transitions |
| `SHADER_NAMES` | Array of supported shader names for validation and UI pickers |
| `isHtmlInCanvasCaptureSupported()` | Feature-detects Chrome's native HTML-in-canvas capture path |
| `installPageSideCompositor()` | Installs the render-mode compositor used by the producer path |
| `isPageSideCompositingSupported()` | Checks whether page-side shader compositing is available |

## Quick Start
```typescript
import { init } from "@hyperframes/shader-transitions";

const timeline = init({
  bgColor: "#0a0a0a",
  accentColor: "#ff6b2b",
  scenes: ["scene-1", "scene-2", "scene-3"],
  transitions: [
    { time: 3, shader: "domain-warp", duration: 0.8 },
    { time: 8, shader: "light-leak", duration: 0.7 },
  ],
});

window.__timelines ??= {};
window.__timelines.hero = timeline;
```

Pass an existing GSAP timeline when the composition already owns the animation sequence:
```typescript
const timeline = gsap.timeline({ paused: true });
timeline.from("#headline", { opacity: 0, y: 40, duration: 0.6 });

init({
  bgColor: "#000000",
  scenes: ["intro", "demo", "outro"],
  transitions: [
    { time: 5, shader: "cinematic-zoom" },
    { time: 12, shader: "glitch", duration: 0.5 },
  ],
  timeline,
});
```

If WebGL is unavailable, the package falls back to normal timeline playback without shader compositing.

## Available Shaders (13)
| Shader | Description |
| --- | --- |
| `domain-warp` | Organic noise-based warp with a glowing edge |
| `ridged-burn` | Ridged noise burn with sparks and heat glow |
| `whip-pan` | Horizontal motion blur simulating a fast camera pan |
| `sdf-iris` | Circular iris wipe with a glowing ring edge |
| `ripple-waves` | Concentric ripple distortion radiating from center |
| `gravitational-lens` | Warping gravity well with chromatic aberration |
| `cinematic-zoom` | Radial zoom blur with chromatic fringing |
| `chromatic-split` | RGB channel separation expanding from center |
| `glitch` | Digital glitch with block displacement and scanlines |
| `swirl-vortex` | Spiral rotation with noise-based warping |
| `thermal-distortion` | Heat shimmer rising from the bottom |
| `flash-through-white` | Flash to white, then reveal the next scene |
| `cross-warp-morph` | Noise-driven morph blending both scenes |
| `light-leak` | Warm cinematic light leak with lens flare |

(Note: the table above lists 14 named shaders; the doc title references "the 13 transitions + init API". `flash-through-white` is the one sometimes counted separately as a flash rather than a warp/distortion transition.)

Use `SHADER_NAMES` for a typed list:
```typescript
import { SHADER_NAMES } from "@hyperframes/shader-transitions";
```

## Configuration
```typescript
type TransitionConfig = {
  time: number;
  shader?: string;
  duration?: number;
  ease?: string;
};

type HyperShaderConfig = {
  bgColor: string;
  accentColor?: string;
  scenes: string[];
  transitions: TransitionConfig[];
  timeline?: gsap.core.Timeline;
  compositionId?: string;
  previewCaptureFps?: number;
};
```
`shader` is optional. Omit it to use a CSS fallback transition at that point in the timeline.

## Preview and Render Behavior

Browser previews pre-capture transition samples and cache matching snapshots in IndexedDB. Cache keys include composition ID, scene DOM/style signatures, timing, capture FPS, scale, and dimensions — page refreshes reuse samples while runtime edits invalidate only adjacent transition caches.

During producer renders, shader transitions use a deterministic page-side compositor instead of preview-time snapshot caching, keeping frame capture seek-driven (no wall-clock playback dependency).
