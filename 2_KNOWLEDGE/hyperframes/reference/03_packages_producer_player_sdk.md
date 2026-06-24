# HyperFrames Packages — producer + player + sdk

Source: https://hyperframes.heygen.com/packages/{producer,player,sdk}.md (fetched 2026-06-24)

The programmatic render + edit + embed APIs. `@hyperframes/producer` is the full HTML-to-video pipeline the SEOSONA Video pipeline relies on; `@hyperframes/player` embeds compositions; `@hyperframes/sdk` is the headless editing engine.

---

# @hyperframes/producer

> Full HTML-to-video rendering pipeline with encoding, audio mixing, and Docker support.

Combines the engine's frame capture with FFmpeg encoding for a complete HTML-to-video pipeline. Supports MP4 (h264) and WebM (VP9 with alpha transparency); handles runtime injection, readiness gates, audio mixing, and optional Docker-based deterministic rendering.

```bash
npm install @hyperframes/producer
```

## What It Does (pipeline)

1. **Load the composition HTML** — reads `index.html` and any referenced sub-compositions.
2. **Inject the Hyperframes runtime** — manages timeline seeking, clip lifecycle, media playback.
3. **Wait for readiness gates** — polls `window.__playerReady` and `window.__renderReady` so all assets (fonts, images, video) are loaded before capture.
4. **Capture frames via the engine** — BeginFrame pipeline, each frame a pixel buffer.
5. **Encode to MP4 or WebM via FFmpeg** — MP4 h264; WebM VP9 with alpha.
6. **Mix audio tracks** — extracts audio from video clips + audio elements, applies `data-volume` and `data-media-start` offsets.

## Programmatic Usage (two-step API)

```typescript
import { createRenderJob, executeRenderJob } from '@hyperframes/producer';

const job = createRenderJob({
  fps: 30,
  quality: 'standard',
});

await executeRenderJob(job, './my-video', './output.mp4');
```

### Render Configuration

```typescript
import { createRenderJob } from '@hyperframes/producer';

const job = createRenderJob({
  fps: 30,                   // integer, or { num: 30000, den: 1001 } for NTSC
  quality: 'standard',       // 'draft', 'standard', or 'high'
  format: 'mp4',             // 'mp4', 'webm', 'mov', or 'png-sequence'
  workers: 4,                // Parallel render workers (1-8)
  useGpu: false,             // GPU-accelerated encoding
  debug: false,              // Debug logging
});
```

#### WebM with Transparency
```typescript
const job = createRenderJob({ fps: 30, quality: 'standard', format: 'webm' });
await executeRenderJob(job, './my-overlay', './overlay.webm');
```
When `format: 'webm'`: frames captured as PNG (preserves alpha); Chrome page background transparent via CDP; FFmpeg VP9 + `yuva420p`; audio encoded as Opus.

#### HDR Output
```typescript
const job = createRenderJob({ fps: 30, quality: 'standard', format: 'mp4', hdr: true });
await executeRenderJob(job, './my-video', './output.mp4');
```
When `hdr: true`: sources probed via `ffprobe` (PQ takes precedence over HLG); HDR videos/images extracted as 16-bit linear-light and composited natively; SDR DOM overlays converted sRGB → BT.2020; output `libx265` + `yuv420p10le` + HDR10 metadata. `format` must be `'mp4'` (`'mov'`/`'webm'` fall back to SDR). HDR `<img>` extraction = still images only.

### Progress Callbacks
```typescript
import type { ProgressCallback, RenderStatus } from '@hyperframes/producer';

const onProgress: ProgressCallback = (status: RenderStatus) => {
  console.log(`Status: ${status}`);
  // Statuses: "queued" | "preprocessing" | "rendering" | "encoding"
  //           | "assembling" | "complete" | "failed" | "cancelled"
};
```

### Cancellation
```typescript
import { RenderCancelledError } from '@hyperframes/producer';

try {
  await executeRenderJob(job);
} catch (err) {
  if (err instanceof RenderCancelledError) {
    console.log(`Cancelled: ${err.reason}`);
    // reason: "user_cancelled" | "timeout" | "aborted"
  }
}
```

## HTTP Server

```typescript
import { startServer } from '@hyperframes/producer/server';
await startServer({ port: 8080 });
```

### Server Endpoints
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/render` | Blocking render — returns JSON result |
| `POST` | `/render/stream` | Streaming render with Server-Sent Events |
| `POST` | `/lint` | Lint a composition for issues |
| `GET` | `/health` | Health check |
| `GET` | `/outputs/:token` | Download a rendered MP4 |

Lower-level handlers:
```typescript
import { createRenderHandlers, createProducerApp } from '@hyperframes/producer/server';

const handlers = createRenderHandlers(options);  // individual request handlers
const app = createProducerApp(options);          // full Hono app
```

## Docker Rendering

```bash
npx hyperframes render --docker --output output.mp4
```
Pinned Chrome version + font set → identical output across machines. Requires Docker installed and running (`npx hyperframes doctor`).

## Quality Presets
| Preset | Resolution | Encoding | Use Case |
| --- | --- | --- | --- |
| `draft` | Original | Fast CRF | Quick iteration |
| `standard` | Original | Balanced CRF | Production, sharing |
| `high` | Original | High-quality CRF | Final delivery, archival |

## GPU Encoding
| Platform | Encoder | Selection |
| --- | --- | --- |
| NVIDIA | NVENC | Auto-detected |
| macOS | VideoToolbox | Auto-detected |
| Linux | VAAPI | Auto-detected |
| Intel | QSV | Auto-detected |
| AMD on Windows | AMF | Auto-detected |

Producer API browser-GPU override:
```typescript
import { resolveConfig } from '@hyperframes/producer';

const job = createRenderJob({
  fps: 30, quality: 'standard',
  producerConfig: resolveConfig({ browserGpuMode: 'hardware' }),
});
```

## Additional Exports (re-exported engine functionality)
| Export | Description |
| --- | --- |
| `createCaptureSession()` | Create a frame capture session |
| `initializeSession()` | Initialize session with a composition |
| `captureFrame()` / `captureFrameToBuffer()` | Capture individual frames |
| `closeCaptureSession()` | Clean up a capture session |
| `getCompositionDuration()` | Get total composition duration |
| `getCapturePerfSummary()` | Get capture performance metrics |
| `createFileServer()` | HTTP file server for serving assets |
| `createVideoFrameInjector()` | Video frame injector for page |
| `resolveConfig()` / `DEFAULT_CONFIG` | Producer configuration |
| `createConsoleLogger()` / `defaultLogger` | Logging utilities |
| `quantizeTimeToFrame()` | Convert time to frame boundary |
| `resolveRenderPaths()` | Resolve render directory paths |
| `prepareHyperframeLintBody()` / `runHyperframeLint()` | Linting utilities |

## Logging

```ts
export type LogLevel = "error" | "warn" | "info" | "debug";

export interface ProducerLogger {
  error(message: string, meta?: Record<string, unknown>): void;
  warn(message: string, meta?: Record<string, unknown>): void;
  info(message: string, meta?: Record<string, unknown>): void;
  debug(message: string, meta?: Record<string, unknown>): void;
  isLevelEnabled?(level: LogLevel): boolean;
}
```
`createConsoleLogger(level)` returns a console-backed impl (filters by level, JSON-stringifies `meta`). `defaultLogger` is the singleton at `level="info"`.

Gate expensive meta in hot paths:
```ts
if (i % 30 === 0 && (log.isLevelEnabled?.("debug") ?? true)) {
  const hdrEl = stackingInfo.find((e) => e.isHdr);
  log.debug("[Render] HDR layer composite frame", { frame: i, time: time.toFixed(2), /* ... */ });
}
```
The `?? true` fallback keeps custom loggers without `isLevelEnabled` working unchanged.

## Regression Testing
```bash
cd packages/producer
bun run docker:build:test   # build test Docker image
bun run docker:test         # compare against golden baselines
bun run docker:test:update  # regenerate baselines
```

## Benchmarking
```bash
npx hyperframes benchmark
# or: cd packages/producer && bun run benchmark
```

## External assets (files outside `projectDir`)

A composition can reference absolute paths to assets outside the project directory. The producer handles these by:
1. **Detection** — HTML compiler walks every `[src]`/`[href]` and `url(...)` in `<style>`; out-of-`projectDir` files collected into an `externalAssets` map.
2. **Sanitised keys** — each absolute path → safe relative key prefixed `hf-ext/`. Windows drive-letter colons stripped (`D:\foo\x.wav` → `hf-ext/D/foo/x.wav`).
3. **Copy + rewrite** — file copied under `<compileDir>/hf-ext/...`, HTML rewritten to the sanitised key; file server serves both internal and external assets from the same root.

Containment check uses `path.relative()` (works on macOS/Linux/Windows). Helpers in `packages/producer/src/utils/paths.ts`.

---

# @hyperframes/player

> Embeddable web component for playing HyperFrames compositions in any web page.

Provides a `<hyperframes-player>` custom element. Zero dependencies, 3KB gzipped.

```bash
npm install @hyperframes/player
```

## Quick Start

### Via CDN
```html
<script type="module" src="https://cdn.jsdelivr.net/npm/@hyperframes/player"></script>

<hyperframes-player
  src="./my-composition/index.html"
  controls autoplay muted
  style="width: 100%; max-width: 800px; aspect-ratio: 16/9"
></hyperframes-player>
```
Classic `<script>` tag global build:
```html
<script src="https://cdn.jsdelivr.net/npm/@hyperframes/player/dist/hyperframes-player.global.js"></script>
```

### Via npm
```js
import '@hyperframes/player';
```
```html
<hyperframes-player src="/compositions/intro.html" controls></hyperframes-player>
```

## HTML Attributes
| Attribute | Type | Default | Description |
| --- | --- | --- | --- |
| `src` | string | required | URL or relative path to composition HTML |
| `width` | number | 1920 | Composition width in pixels |
| `height` | number | 1080 | Composition height in pixels |
| `controls` | boolean | false | Show playback controls overlay |
| `autoplay` | boolean | false | Start playing on load |
| `loop` | boolean | false | Loop playback |
| `muted` | boolean | true | Mute audio (required for autoplay in most browsers) |
| `poster` | string | — | Image URL before first play |
| `playback-rate` | number | 1 | Playback speed multiplier |

## JavaScript API (mirrors native `<video>`)
```js
const player = document.querySelector('hyperframes-player');

player.play();
player.pause();
player.seek(2.5);          // seek to 2.5 seconds

player.currentTime;        // number — current position in seconds
player.currentTime = 5;    // seek to 5 seconds
player.duration;           // number — total duration
player.paused;             // boolean
player.ready;              // boolean — true after composition loads
player.playbackRate;       // number — get/set speed
player.muted;              // boolean — get/set mute
player.loop;               // boolean — get/set loop
```

## Events
| Event | Detail | Description |
| --- | --- | --- |
| `ready` | `{ duration }` | Composition loaded, timeline discovered |
| `timeupdate` | `{ currentTime }` | Fires during playback (~30fps) |
| `play` | — | Playback started |
| `pause` | — | Playback paused |
| `ended` | — | Playback reached end |
| `error` | `{ message }` | Load or runtime error |

```js
player.addEventListener('ready', (e) => console.log('Duration:', e.detail.duration));
player.addEventListener('timeupdate', (e) => console.log('Time:', e.detail.currentTime));
player.addEventListener('error', (e) => console.error(e.detail.message));
```

## Framework Examples

### React
```jsx
import '@hyperframes/player';
function VideoPreview({ src }) {
  return <hyperframes-player src={src} controls style={{ width: '100%', maxWidth: 800 }} />;
}
```

### Vue
```vue
<template>
  <hyperframes-player :src="compositionUrl" controls />
</template>
<script setup>
import '@hyperframes/player';
const compositionUrl = './compositions/intro.html';
</script>
```

### Programmatic
```js
import '@hyperframes/player';
const player = document.createElement('hyperframes-player');
player.src = './my-composition/index.html';
player.controls = true;
player.addEventListener('ready', () => player.play());
document.getElementById('player-container').appendChild(player);
```

## Advanced: iframe access

The composition runs inside a sandboxed `<iframe>` in the player's Shadow DOM. The `iframeElement` getter exposes the inner iframe:
```js
const player = document.querySelector('hyperframes-player');
const iframe = player.iframeElement;
iframe.contentDocument.querySelectorAll('[data-composition-id]');
iframe.contentWindow.__timelines;   // GSAP timelines, element registry
```

Bridge into editor tools — studio exports a `resolveIframe` helper:
```ts
import { useTimelinePlayer, resolveIframe } from '@hyperframes/studio';

const { iframeRef } = useTimelinePlayer();
const player = document.createElement('hyperframes-player');
player.setAttribute('src', src);
container.appendChild(player);
iframeRef.current = resolveIframe(player);
```

React declarative ref pattern:
```tsx
import '@hyperframes/player';
import type { HyperframesPlayer } from '@hyperframes/player';
import { useTimelinePlayer, resolveIframe } from '@hyperframes/studio';

function StudioPreview({ src }: { src: string }) {
  const { iframeRef, onIframeLoad } = useTimelinePlayer();
  const playerRef = useRef<HyperframesPlayer>(null);
  useEffect(() => { iframeRef.current = resolveIframe(playerRef.current); });
  return <hyperframes-player ref={playerRef} src={src} onLoad={onIframeLoad} />;
}
```

> WARNING (common gotcha): If you pass the `<hyperframes-player>` element itself (not `iframeElement`) into a hook/API expecting an `<iframe>`, every `.contentWindow`/`.contentDocument` access returns `null` (iframe is inside Shadow DOM). Timeline seek/play/pause/DOM inspection silently no-op. Always extract `iframeElement` first, or use `resolveIframe`.

## Architecture

Uses an iframe inside a Shadow DOM container → isolation (CSS/JS can't leak), security (sandbox), scaling (auto-scales to fit via CSS transforms). Communicates with the composition via the HyperFrames runtime bridge protocol (`postMessage`). Existing compositions work unmodified.

## Controls

When `controls` is present: Play/Pause (left), scrub bar with drag (mouse + touch), time display (right). Auto-hides after 3s inactivity, reappears on hover.

---

# @hyperframes/sdk

> Headless, framework-neutral composition editing engine for agents and custom editors.

Programmatic editing layer: opens composition HTML, exposes query/mutation APIs, emits JSON patches, supports undo/redo, persists through pluggable adapters — no React, Studio, or browser UI required.

```bash
npm install @hyperframes/sdk
```

## Package Exports
| Import | Description |
| --- | --- |
| `@hyperframes/sdk` | Main editing API, types, memory/headless adapters, iframe preview adapter |
| `@hyperframes/sdk/adapters/memory` | In-memory persistence adapter for tests, demos, ephemeral sessions |
| `@hyperframes/sdk/adapters/fs` | Node.js filesystem persistence adapter with version history |
| `@hyperframes/sdk/adapters/headless` | No-op preview adapter for agents, CI, server-side editing |

## Quick Start
```typescript
import { openComposition } from "@hyperframes/sdk";

const comp = await openComposition(html);

const [headlineId] = comp.find({ text: "Old headline" });
if (headlineId) {
  comp.setText(headlineId, "New headline");
  comp.setStyle(headlineId, { color: "#FFD60A", fontSize: "96px" });
}

const updatedHtml = comp.serialize();
comp.dispose();
```

## Core Concepts

### Explicit Element IDs
All edits target stable HyperFrames element IDs (safe for headless agents/backends — no mouse/selection state).
```typescript
const allElements = comp.getElements();
const imageIds = allElements.filter((element) => element.tag === "img").map((element) => element.id);
for (const id of imageIds) {
  comp.setAttribute(id, "loading", "eager");
}
```

### Typed Methods
```typescript
comp.setText("hf-title", "Launch day");
comp.setStyle("hf-title", { color: "#ffffff", transform: "translateY(24px)" });
comp.setAttribute("hf-logo", "src", "/assets/logo.png");
comp.setTiming("hf-title", { start: 0.5, duration: 2.5 });
comp.setVariableValue("brandColor", "#6C5CE7");
comp.removeElement("hf-old-caption");
```

`batch()` groups several mutations into one undo entry / persist write / change notification:
```typescript
comp.batch(() => {
  comp.setText("hf-title", "Version 2");
  comp.setStyle("hf-title", { color: "#22C55E" });
  comp.setTiming("hf-title", { start: 1, duration: 3 });
});
```

### Advanced Dispatch API
```typescript
comp.dispatch({ type: "setStyle", target: "hf-card", styles: { borderRadius: "24px" } });
```
Guard optional operations with `can()`:
```typescript
const result = comp.can({ type: "setGsapTween", animationId: "anim-1", properties: { ease: "power3.out" } });
if (result.ok) {
  comp.setGsapTween("anim-1", { ease: "power3.out" });
}
```

## Persistence
```typescript
import { openComposition } from "@hyperframes/sdk";
import { createFsAdapter } from "@hyperframes/sdk/adapters/fs";

const comp = await openComposition(html, {
  persist: createFsAdapter({ root: "./project" }),
  persistPath: "index.html",
});

comp.setText("hf-title", "Saved title");
await comp.flush();
```
Host applications can implement the same `PersistAdapter` interface for S3, HTTP, IndexedDB, etc. Persistence failures emit events instead of crashing:
```typescript
comp.on("persist:error", ({ error }) => console.error("Autosave failed:", error.message));
```

## Undo, Redo, and Patch Events
```typescript
comp.setText("hf-title", "Draft");
comp.undo();
comp.redo();

const unsubscribe = comp.on("patch", ({ patches, inversePatches, origin }) => {
  saveToHostHistory({ patches, inversePatches, origin });
});
unsubscribe();
```

## Embedded Override Mode
For template-driven products: open with an `overrides` object; SDK applies the sparse override set on top of base HTML, accumulates edits into it, lets the host store only the delta.
```typescript
const comp = await openComposition(templateHtml, {
  overrides: {
    "hf-title.text": "Customer-specific title",
    "hf-logo.attr.src": "/customers/acme/logo.png",
  },
  history: false,
});

comp.setStyle("hf-title", { color: "#0EA5E9" });
const nextOverrides = comp.getOverrides();
```
Use `applyPatches()` when the host owns undo/redo and needs to replay inverse patches without loops.

## Preview Adapters
```typescript
import { openComposition, createHeadlessAdapter } from "@hyperframes/sdk";

const comp = await openComposition(html, { preview: createHeadlessAdapter() });
```
For browser integrations, `createIframePreviewAdapter()` bridges the SDK to a same-origin composition iframe (hit-testing, selection, draft preview outside the model mutation path).
