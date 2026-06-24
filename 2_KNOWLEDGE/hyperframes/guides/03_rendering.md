# HyperFrames — Rendering, 4K, Performance & HDR

This file consolidates four upstream guides covering local/Docker/CI rendering, 4K output, performance tuning, and HDR.

**Sources:**
- https://hyperframes.heygen.com/guides/rendering.md
- https://hyperframes.heygen.com/guides/4k-rendering.md
- https://hyperframes.heygen.com/guides/performance.md
- https://hyperframes.heygen.com/guides/hdr.md

---

# Rendering

**Source:** https://hyperframes.heygen.com/guides/rendering.md

# Rendering

> Render compositions to MP4, MOV, WebM, GIF, or PNG sequences locally or in Docker.

Render your Hyperframes [compositions](/concepts/compositions) to MP4, MOV, WebM, GIF, or PNG sequences with the [CLI](/packages/cli). The rendering pipeline is frame-by-frame and seek-driven — see [Deterministic Rendering](/concepts/determinism) for how this works under the hood.

## Getting Started

<Steps>
  <Step title="Verify your environment">
    Run the diagnostics command to check for required dependencies:

    ```bash Terminal theme={null}
    npx hyperframes doctor
    ```

    Expected output:

    ```
    ✓ Node.js    v22.x
    ✓ FFmpeg      7.x
    ✓ FFprobe     7.x
    ✓ Chrome      (bundled)
    ✓ Docker      available
    ```
  </Step>

  <Step title="Preview your composition">
    Before rendering, preview your composition in the browser to verify it looks correct:

    ```bash Terminal theme={null}
    npx hyperframes preview
    ```
  </Step>

  <Step title="Render to MP4">
    Run the render command from your project directory:

    ```bash Terminal theme={null}
    npx hyperframes render --output output.mp4
    ```

    Expected output:

    ```
    ⠋ Rendering composition "root" (30fps, standard quality)
    ✓ Captured 240 frames in 8.2s
    ✓ Encoded to output.mp4 (8.0s, 1920x1080, 4.2MB)
    ```
  </Step>
</Steps>

## Rendering Modes

<Tabs>
  <Tab title="Local Mode">
    ### Local Mode (default)

    Uses Puppeteer (bundled Chromium) and your system's FFmpeg. Fast for iteration during development.

    **Requires:** FFmpeg installed on your system. See [Troubleshooting](/guides/troubleshooting) if FFmpeg is not found.

    ```bash Terminal theme={null}
    npx hyperframes render --output output.mp4
    ```

    **Pros:**

    * Fast startup, no container overhead
    * Can use your system GPU for Chrome/WebGL capture by default
    * Can use your system GPU for hardware-accelerated encoding (with `--gpu`)
    * Best for iterative development

    **Cons:**

    * Output may vary across platforms due to font and Chrome version differences
    * Not suitable for CI/CD pipelines that require reproducibility
  </Tab>

  <Tab title="Docker Mode">
    ### Docker Mode

    [Deterministic](/concepts/determinism) output with an exact Chrome version and font set. Use this for production renders and CI pipelines.

    **Requires:** Docker installed and running.

    ```bash Terminal theme={null}
    npx hyperframes render --docker --output output.mp4
    ```

    **Pros:**

    * Identical output on every platform — same Chrome, same fonts, same FFmpeg
    * The same pipeline used in production
    * Ideal for CI/CD and automated workflows

    **Cons:**

    * Slower startup due to container initialization
    * Browser capture stays on the deterministic software-GL path
    * GPU encoding requires Docker host GPU passthrough and is not cross-platform on Docker Desktop

    <Note>
      Docker mode uses `chrome-headless-shell` with [BeginFrame](/concepts/determinism#how-it-works) control for frame-perfect, deterministic capture.
    </Note>
  </Tab>
</Tabs>

## When to Use Each Mode

| Scenario                        | Recommended Mode |
| ------------------------------- | ---------------- |
| Local development and iteration | Local            |
| CI/CD pipeline                  | Docker           |
| Sharing renders with a team     | Docker           |
| Quick preview export            | Local            |
| AI agent-driven rendering       | Docker           |
| Benchmarking performance        | Local            |

## Options

| Flag                                 | Values                            | Default                   | Description                                                                                                           |
| ------------------------------------ | --------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `--output`                           | path                              | `renders/<name>.mp4`      | Output file path                                                                                                      |
| `--format`                           | mp4, mov, webm, gif, png-sequence | mp4                       | Output format (see [Transparent Video](#transparent-video) below)                                                     |
| `--fps`                              | 24, 30, 60                        | 30                        | Frames per second                                                                                                     |
| `--gif-loop`                         | 0-65535                           | 0                         | GIF loop count. `0` loops forever                                                                                     |
| `--quality`                          | draft, standard, high             | standard                  | Encoding quality preset                                                                                               |
| `--crf`                              | 0–51                              | —                         | Override CRF (lower = higher quality). Cannot combine with `--video-bitrate`                                          |
| `--video-bitrate`                    | e.g. `10M`, `5000k`               | —                         | Target bitrate encoding. Cannot combine with `--crf`                                                                  |
| `--video-frame-format`               | auto, jpg, png                    | auto                      | Source video frame extraction format. Use `png` for UI recordings, screen captures, and color-sensitive source videos |
| `--workers`                          | 1-8 or `auto`                     | auto                      | Parallel render workers (see [Workers](#workers) below)                                                               |
| `--max-concurrent-renders`           | 1-10                              | 2                         | Max simultaneous renders via the producer server (see [Concurrent Renders](#concurrent-renders) below)                |
| `--batch`                            | path                              | —                         | JSON array of variable rows (or `{ "rows": [...] }`), rendering one output per row                                    |
| `--batch-concurrency`                | integer                           | 1                         | Maximum batch rows to render at once                                                                                  |
| `--batch-fail-fast`                  | —                                 | off                       | Stop launching new batch rows after the first row failure                                                             |
| `--gpu`                              | —                                 | off                       | GPU encoding (NVENC, VideoToolbox, AMF, VAAPI, QSV)                                                                   |
| `--browser-gpu` / `--no-browser-gpu` | —                                 | on locally, off in Docker | Use or opt out of host GPU acceleration for local Chrome/WebGL capture                                                |
| `--hdr`                              | —                                 | off                       | Force HDR output even if no HDR sources are detected (MP4 only). See [HDR Rendering](/guides/hdr)                     |
| `--sdr`                              | —                                 | off                       | Force SDR output even if HDR sources are detected                                                                     |
| `--docker`                           | —                                 | off                       | Use Docker for [deterministic rendering](/concepts/determinism)                                                       |
| `--quiet`                            | —                                 | off                       | Suppress verbose output                                                                                               |

## Quality and Encoding

The `--quality` flag selects a preset that controls the H.264 CRF (Constant Rate Factor) and encoder speed:

| Preset     | CRF | x264 Preset | Best For                                 |
| ---------- | --- | ----------- | ---------------------------------------- |
| `draft`    | 28  | ultrafast   | Quick previews, iteration                |
| `standard` | 18  | medium      | General use — visually lossless at 1080p |
| `high`     | 15  | slow        | Final delivery, near-lossless quality    |

For finer control, use `--crf` or `--video-bitrate` to override the preset:

```bash theme={null}
# Near-lossless quality (CRF 15 = very high quality, large file)
npx hyperframes render --crf 15 --output pristine.mp4

# Target a specific bitrate (useful for size-constrained delivery)
npx hyperframes render --video-bitrate 10M --output controlled.mp4
```

**Tip**: The default `standard` preset (CRF 18) is visually lossless at 1080p — most people cannot distinguish it from the source. Use `--quality draft` for faster iteration, or `--quality high` / `--crf 10` when file size is no concern.

## Animated GIF

Use GIF when the output needs to autoplay inline in GitHub PRs, READMEs, issue reports, and docs pages:

```bash Terminal theme={null}
npx hyperframes render --format gif --fps 15 --gif-loop 0 --output demo.gif
```

GIF output uses a two-pass FFmpeg palette encode (`palettegen` with diff statistics, then `paletteuse` with Sierra dithering) for better gradients and text edges than a single-pass conversion. GIFs are still much larger than MP4/WebM at the same dimensions, so prefer short compositions. GIF renders are capped at 30fps; pass `--fps 15` for smaller files.

GIF does not carry audio and only has 1-bit transparency. For transparent overlays, use `--format webm`, `--format mov`, or `--format png-sequence` instead.

For UI recordings, screen captures, or other source videos where saturated interface colors matter, pass `--video-frame-format png` to extract source video layers as PNG before browser capture. The default `auto` mode preserves the historical behavior: alpha-capable sources use PNG, opaque sources use JPG.

## GPU Acceleration

Hyperframes has two separate GPU acceleration surfaces:

* `--gpu` uses a hardware video encoder in FFmpeg when one is available. Supported backends include VideoToolbox on macOS, NVENC on NVIDIA systems, AMD AMF on Windows, VAAPI on Linux, and Intel QSV on supported Windows/Linux hosts.
* Browser GPU uses the host GPU for local Chrome/WebGL capture. It is enabled automatically for local renders and disabled in Docker. Use `--no-browser-gpu` to opt out.

```bash Terminal theme={null}
# Add hardware FFmpeg encoding to the default local browser-GPU render
npx hyperframes render --gpu --output encoded-fast.mp4

# Opt out of hardware Chrome/WebGL capture
npx hyperframes render --no-browser-gpu --output software-browser.mp4

# Use browser GPU plus hardware FFmpeg encoding
npx hyperframes render --gpu --output gpu.mp4
```

Browser GPU capture is local-mode only. It maps to platform-native Chrome GPU backends: Metal on macOS, D3D11 on Windows, and EGL on Linux. Use `--no-browser-gpu` or Docker mode when exact cross-machine reproducibility matters more than local render speed.

## Workers

Each render worker launches a **separate Chrome browser process** to capture frames in parallel. More workers can speed up rendering, but each one consumes \~256 MB of RAM and significant CPU.

### Default behavior

By default, Hyperframes uses **half of your CPU cores, capped at 4**:

| Machine          | CPU cores | Default workers |
| ---------------- | --------- | --------------- |
| MacBook Air (M1) | 8         | 4               |
| MacBook Pro (M3) | 12        | 4 (capped)      |
| 4-core laptop    | 4         | 2               |
| 2-core VM        | 2         | 1               |

This is intentionally conservative. Each worker spawns its own Chrome process, so the per-worker overhead is significant. Fewer workers avoids resource contention with FFmpeg encoding and your other applications.

### Choosing a worker count

```bash Terminal theme={null}
# Explicit worker count
npx hyperframes render --workers 1 --output output.mp4

# Let Hyperframes pick based on your CPU
npx hyperframes render --workers auto --output output.mp4

# Maximum parallelism (use with caution on laptops)
npx hyperframes render --workers 8 --output output.mp4
```

<Tip>
  Start with the default. If renders feel slow and your system has headroom (check Activity Monitor / `htop`), try increasing `--workers`. If you see high memory pressure or fan noise, reduce it.
</Tip>

### When to use 1 worker

* Short compositions (under 2 seconds / 60 frames) — parallelism overhead exceeds the benefit
* Low-memory machines (4 GB or less)
* Running renders alongside other heavy processes (video editing, large builds)

### When to increase workers

* Long compositions (30+ seconds) on a machine with 8+ cores and 16+ GB RAM
* Dedicated render machines or CI runners
* Docker mode on a well-provisioned host

## Batch Rendering

Batch rendering runs the same composition once per variables row:

```json rows.json theme={null}
[
  { "name": "Alice", "headline": "Welcome, Alice" },
  { "name": "Bob", "headline": "Welcome, Bob" }
]
```

```bash Terminal theme={null}
npx hyperframes render --batch rows.json --output "renders/{name}.mp4" --strict-variables
```

`--output` is a template. Use `{index}` or any scalar key from the row to make each path unique. Hyperframes preflights the full batch before rendering: malformed rows, missing placeholders, duplicate output paths, and strict variable mismatches fail before the first video starts. A `manifest.json` file is written next to the outputs with per-row status, output path, render time, duration when available, and error details.

Rows continue after failures by default so a bad data row does not discard the rest of the batch. Add `--batch-fail-fast` to stop launching new rows after the first failure, or `--json` to stream machine-readable progress events while the manifest is updated.

## Concurrent Renders

When multiple render requests hit the producer server simultaneously (common with AI agents), each render spawns its own set of Chrome worker processes. Too many concurrent renders can exhaust CPU and cause failures.

The producer server uses a **request-level semaphore** to queue renders. Only `maxConcurrentRenders` renders execute at a time — additional requests wait in a FIFO queue until a slot opens.

### Configuration

```bash Terminal theme={null}
# CLI flag
npx hyperframes render --max-concurrent-renders 2 --output output.mp4

# Environment variable (for the producer server)
PRODUCER_MAX_CONCURRENT_RENDERS=2
```

The default is **2** concurrent renders, which works well on 8-core machines where each render uses 2-3 workers.

### Queue status

The producer server exposes a `GET /render/queue` endpoint that returns the current state:

```json theme={null}
{
  "maxConcurrentRenders": 2,
  "activeRenders": 1,
  "queuedRenders": 3
}
```

AI agents can poll this endpoint to decide whether to submit a render or wait.

### SSE queue events

When using the streaming endpoint (`POST /render/stream`), queued requests receive a `queued` event before rendering begins:

```json theme={null}
{"type": "queued", "requestId": "...", "position": 2}
```

This lets agents report "waiting in queue" to users rather than appearing stuck.

### Choosing a concurrency limit

| Machine            | CPU cores | Recommended limit |
| ------------------ | --------- | ----------------- |
| 4-core VM          | 4         | 1                 |
| 8-core workstation | 8         | 2                 |
| 16-core server     | 16        | 3-4               |
| 32-core render box | 32        | 5-6               |

<Tip>
  When in doubt, use 1. Renders will queue up and execute sequentially, but each one gets full CPU and finishes as fast as possible. This is better than 3 renders fighting for CPU and all finishing slowly — or failing.
</Tip>

## Transparent Video

Hyperframes supports rendering with a transparent background — useful for overlays, lower thirds, subscribe cards, and any element you want to composite over other footage in a video editor.

### Recommended format: MOV (ProRes 4444)

```bash Terminal theme={null}
npx hyperframes render --format mov --output overlay.mov
```

**MOV with ProRes 4444** is the industry standard for transparent video. It works in all major video editors:

* CapCut
* Final Cut Pro
* Adobe Premiere Pro
* DaVinci Resolve
* After Effects

<Warning>
  ProRes MOV files are large (typically 5-40 MB for short clips) because ProRes is a high-quality intermediate codec optimized for editing, not delivery. This is expected — the same tradeoff Remotion and professional pipelines make.
</Warning>

### Format comparison

| Format           | Codec                   | Transparency   | Video editors                                       | Browsers        | File size |
| ---------------- | ----------------------- | -------------- | --------------------------------------------------- | --------------- | --------- |
| **MOV**          | ProRes 4444             | Yes            | CapCut, Final Cut, Premiere, DaVinci, After Effects | No              | Large     |
| **WebM**         | VP9                     | Yes            | None (shows black background)                       | Chrome, Firefox | Small     |
| **PNG sequence** | RGBA PNGs (no encoding) | Yes (lossless) | After Effects, Nuke, Fusion (image-sequence import) | No              | Largest   |
| **MP4**          | H.264                   | No             | All                                                 | All             | Small     |

<Note>
  **WebM VP9 alpha** is technically supported but all major video editors ignore the alpha channel and render transparent areas as black. Only Chromium-based browsers (Chrome, Arc, Brave, Edge) decode VP9 alpha correctly. Safari does not support it. Use MOV for editor workflows and WebM only for browser-based playback.
</Note>

### PNG sequence (no encoding)

```bash Terminal theme={null}
npx hyperframes render --format png-sequence --output frames/
```

`--format png-sequence` skips the encoder entirely. The captured RGBA frames are copied to `<output>/frame_NNNNNN.png` (zero-padded) and, if the composition has audio, an `audio.aac` sidecar is written alongside. Use this when you want lossless frames — for compositing in After Effects / Nuke / Fusion, or as the input to a custom encode pipeline. `--output` is treated as a directory and is created if it doesn't exist.

### How it works

When you render with `--format mov`, `--format webm`, or `--format png-sequence`, Hyperframes:

1. Captures each frame as a **PNG with alpha channel** (instead of JPEG for MP4)
2. Sets Chrome's page background to transparent via `Emulation.setDefaultBackgroundColorOverride`
3. Encodes with an alpha-capable codec (ProRes 4444 for MOV, VP9 for WebM); `png-sequence` skips encoding and writes the captured frames directly

Your composition's HTML should **not** set a `background` on `html` or `body` — leave it unset so the transparent background comes through.

### Authoring transparent compositions

```html theme={null}
<style>
  /* Do NOT set background on html/body — leave them transparent */
  * { margin: 0; padding: 0; box-sizing: border-box; }

  [data-composition-id="my-overlay"] {
    position: relative;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    /* No background here either */
  }
</style>
```

Only the visible elements (cards, text, images) will appear in the final video. Everything else will be transparent.

### Verifying transparency

* **In a browser:** Open the MOV file — it won't play (ProRes is not a browser codec). Instead, render a WebM copy and open it in Chrome on a checkerboard background page.
* **In a video editor:** Import the MOV file and place it on a track above other footage. Transparent areas should show the footage below.
* **Online tool:** Use [rotato.app/tools/transparent-video](https://rotato.app/tools/transparent-video) to verify your MOV or WebM has working transparency.

## Tips

<Tip>
  Use `draft` quality during development for fast previews. Switch to `standard` or `high` for final output.
</Tip>

* Use `npx hyperframes benchmark` to find optimal settings for your system
* Docker mode is slower but guarantees [identical output](/concepts/determinism) across platforms
* For compositions with many frames, `--gpu` can significantly speed up local encoding

## Next Steps

<CardGroup cols={2}>
  <Card title="Deterministic Rendering" icon="lock" href="/concepts/determinism">
    Understand the determinism guarantees
  </Card>

  <Card title="HDR Rendering" icon="sun" href="/guides/hdr">
    Render HDR10 MP4 from HDR video and image sources
  </Card>

  <Card title="Cloud Rendering" icon="cloud" href="/deploy/cloud">
    Render on HeyGen's hosted cloud — no local Chrome or FFmpeg
  </Card>

  <Card title="CLI Reference" icon="terminal" href="/packages/cli">
    Full list of CLI commands and flags
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="/guides/troubleshooting">
    Fix common rendering issues
  </Card>
</CardGroup>

---

# 4K Rendering

**Source:** https://hyperframes.heygen.com/guides/4k-rendering.md

# 4K Rendering

> Render any composition to 4K (3840×2160) without rewriting it — the CLI supersamples a 1080p composition via Chrome's device scale factor.

Hyperframes renders to 4K (3840×2160) two ways. Both produce a true 4K MP4; pick the one that matches your project.

<CardGroup cols={2}>
  <Card title="Author at 4K" icon="ruler">
    Scaffold the project at 4K so the composition is laid out at 4K natively. Best when you want crisp 4K-native typography and assets.

    ```bash theme={null}
    npx hyperframes init my-video --resolution 4k
    ```
  </Card>

  <Card title="Supersample at render" icon="up-right-and-down-left-from-center">
    Keep your existing 1080p composition. Pass `--resolution 4k` at render time and Chrome renders at 2× DPR so the screenshot lands at 4K.

    ```bash theme={null}
    npx hyperframes render --resolution 4k --output 4k.mp4
    ```
  </Card>
</CardGroup>

## Quickstart

<Steps>
  <Step title="Render an existing project at 4K">
    ```bash Terminal theme={null}
    npx hyperframes render --resolution 4k --output my-video-4k.mp4
    ```

    The composition's `data-width` / `data-height` are unchanged. Chrome's `deviceScaleFactor` is set to `2`, so the captured screenshot for each frame is 3840×2160. ffmpeg auto-detects the dimensions from the screenshot stream and encodes at 4K.
  </Step>

  <Step title="Or scaffold a new project at 4K">
    ```bash Terminal theme={null}
    npx hyperframes init my-video --resolution 4k
    ```

    Every scaffolded HTML file is patched in place: `data-width="3840"`, `data-height="2160"`, `data-resolution="landscape-4k"`, `#stage` CSS dimensions, and the `<meta viewport>` tag.
  </Step>

  <Step title="Verify the output is 4K">
    ```bash Terminal theme={null}
    ffprobe -v error -select_streams v:0 -show_entries stream=width,height my-video-4k.mp4
    ```

    Expected:

    ```
    width=3840
    height=2160
    ```
  </Step>
</Steps>

## Resolution presets

`--resolution` accepts these values on both `init` and `render`:

| Preset         | Dimensions | Aliases          |
| -------------- | ---------- | ---------------- |
| `landscape`    | 1920×1080  | `1080p`, `hd`    |
| `portrait`     | 1080×1920  | `1080p-portrait` |
| `landscape-4k` | 3840×2160  | `4k`, `uhd`      |
| `portrait-4k`  | 2160×3840  | `4k-portrait`    |

Examples:

```bash Terminal theme={null}
npx hyperframes render --resolution 4k         # landscape 4K
npx hyperframes render --resolution portrait-4k # vertical 4K (TikTok / Reels at max quality)
npx hyperframes render --resolution 1080p       # explicit 1080p (no-op on 1080p compositions)
```

## How `--resolution` works (supersampling)

The composition stays at its authored dimensions. Hyperframes computes a `deviceScaleFactor` from the ratio of output to composition dimensions and passes it to Chrome:

| Composition | `--resolution` | `deviceScaleFactor` | Output    |
| ----------- | -------------- | ------------------- | --------- |
| 1920×1080   | `4k`           | 2                   | 3840×2160 |
| 1080×1920   | `portrait-4k`  | 2                   | 2160×3840 |
| 3840×2160   | `4k`           | 1 (no-op)           | 3840×2160 |

Chrome then renders the page at the higher DPR — effectively rendering each CSS pixel as 2×2 device pixels — so the captured screenshot is at the requested resolution.

<Tip>
  This approach is intentionally simple — no composition edits, no second authoring pass. The tradeoff: 4K renders take roughly 4× as long per frame because there are 4× the pixels to capture and encode.
</Tip>

## What scales, what doesn't

Supersampling re-renders the page at higher DPR. That genuinely helps anything the browser rasterizes from a vector or high-resolution source, and does nothing for content already locked to a fixed pixel grid. Knowing which is which sets correct expectations before a 4K render:

| Asset type                                       | Behavior at `--resolution 4k`                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Text (HTML, SVG `<text>`, web fonts)             | ✅ **Re-rasterized at 4K.** Glyphs are vector and the browser shapes/rasterizes them at the new DPR. Crisp at any scale.                                                                                                                                                                                                |
| SVG / vector graphics                            | ✅ **Re-rasterized at 4K.** Same story as text — paths are vector.                                                                                                                                                                                                                                                      |
| CSS shapes, gradients, borders, shadows          | ✅ **Re-rasterized at 4K.** Browser-generated raster.                                                                                                                                                                                                                                                                   |
| Images with intrinsic dimensions ≥ 4K            | ✅ **Full benefit.** A 3840×2160 source serves all the detail.                                                                                                                                                                                                                                                          |
| Images smaller than 4K (e.g. a 1920×1080 PNG)    | ⚠️ **No new detail.** Browser upscales the source bitmap; output is no sharper than rendering at 1080p and upscaling externally — but no worse either.                                                                                                                                                                 |
| `<video>` elements                               | ❌ **Locked to source resolution.** A 1080p MP4 stays 1080p; the supersample only helps the surrounding DOM. Encode source video at the target resolution if you need 4K throughout.                                                                                                                                    |
| `<canvas>` (2D and WebGL)                        | ❌ **Locked to canvas's intrinsic dimensions.** `<canvas width="1920" height="1080">` is a 1080p bitmap regardless of DPR. To render canvas content at 4K, multiply `canvas.width` / `canvas.height` by your target DPR and scale the drawing context (`ctx.scale(2, 2)` for a 2× canvas with the same logical layout). |
| Pre-rendered video frames injected by the engine | ❌ **Locked to extraction resolution.** When the producer pre-extracts `<video>` frames via ffmpeg, they're decoded at the source video's dimensions.                                                                                                                                                                   |

**Rule of thumb**: if the asset is *vector or generated by the browser*, supersampling helps. If it's a *bitmap with fixed pixel dimensions* (video, canvas, low-res PNG), it doesn't — author it at the target resolution instead.

## Constraints

`--resolution` enforces three guards before any frames are captured. If any fail, the render exits before doing work.

### Aspect ratio must match

```bash theme={null}
# OK — both landscape
hyperframes render --resolution 4k         # composition is 1920×1080

# Error — composition is landscape, target is portrait
hyperframes render --resolution portrait-4k  # composition is 1920×1080
# → outputResolution portrait-4k (2160×3840) does not match the aspect ratio
#   of the composition (1920×1080). Pick a preset whose orientation matches.
```

### The scale must be an integer

The width ratio (output ÷ composition) must be a positive integer. 1080p → 4K is exactly `2×`. 720p → 4K would be `3×` and works. Non-integer scales like 900p → 4K (`2.4×`) introduce aliasing on subpixel-positioned text — Hyperframes refuses rather than producing a blurry render.

### Downsampling is not supported

`--resolution` only supersamples. A 4K composition cannot be downsampled to 1080p with this flag — render at the composition's native resolution and downscale separately with ffmpeg if needed.

### Not yet supported with `--hdr`

The HDR layered compositor processes pixel buffers at composition dimensions; supersample + HDR would need parallel scaling for those buffers. The combination is rejected with a clear error message. Render in two passes if you need both: HDR at composition resolution, then upscale separately.

## Performance

A 1080p → 4K supersample is roughly 4× more pixels to capture, encode, and write. Expect:

* **Per-frame capture**: 3–4× slower (Chrome paints 4× the pixels and the screenshot transfer is 4× larger)
* **Encoding**: 2–3× slower (depends on codec; H.264 scales sublinearly with resolution)
* **Memory**: bounded — the engine's frame data-URI cache is byte-budgeted (default 1500 MB per worker, configurable via `PRODUCER_FRAME_DATA_URI_CACHE_BYTES_MB`)
* **Output file size**: at the default CRF, expect 3–5× the file size of the 1080p render. Pass `--video-bitrate 25M` (or higher) for predictable file sizes.

For a 4K render of a 30-second composition, plan on a few minutes of wall time on a modern laptop. Add `--workers 4` (or more) on a render box for parallel capture.

## Studio support

The Renders panel in Studio includes a resolution dropdown next to the format and quality selectors. Pick `4K` (or `4K ↕` for portrait) and hit **Export** — the same supersampling path runs as the CLI flag, no composition edits required.

The dropdown defaults to `Auto` (render at the composition's authored size). Available presets:

* **Auto** — composition's native dimensions
* **1080p ↔** / **1080p ↕** — 1920×1080 / 1080×1920
* **4K ↔** / **4K ↕** — 3840×2160 / 2160×3840

The resolution applies per render, not per project — your composition files are unchanged. The same [constraints](#constraints) apply; when the producer rejects a combination, the failure surfaces in the Studio render queue.

You can also drive resolution from the CLI:

* **New project**: `hyperframes init my-video --resolution 4k`
* **Existing project**: `hyperframes render --resolution 4k --output 4k.mp4`

## See also

* [`render` CLI reference](/packages/cli#render) — every render flag including `--video-bitrate` and `--crf`
* [`init` CLI reference](/packages/cli#init) — the `--resolution` flag at scaffold time
* [HDR Rendering](/guides/hdr) — color pipeline guide; HDR + 4K is not yet a supported combination

---

# Performance

**Source:** https://hyperframes.heygen.com/guides/performance.md

# Performance

> How to keep preview playback smooth and diagnose expensive compositions.

Preview plays your composition in real time, so any frame that takes longer than 33ms (at 30fps) shows up as stutter. This page covers the patterns that blow that budget and how to spot them.

## Preview vs. render

Render captures frames one at a time and stitches them into a video. Slow frames make the render take longer, but you never see the pauses — you watch the finished mp4.

Preview does the same work in real time. If a frame takes 200ms to paint, you see a 200ms freeze.

This is why "render looks fine, preview stutters" is expected for paint-heavy compositions. It doesn't mean preview is broken — it means individual frames are too expensive for real-time playback.

## Expensive CSS patterns

These are the patterns that most often cause preview to drop below 30fps.

### backdrop-filter: blur()

Each `backdrop-filter: blur(radius)` sampled over a large area forces the compositor to read pixels from behind the element, run a blur kernel across them, and composite the result. Cost scales with both the blurred area and the radius.

Stacked blur layers multiply the cost. Eight layers at progressively larger radii (1, 2, 4, 8, 16, 32, 64, 128px) will happily take 200ms per frame over a 1920x1080 region on mid-tier GPUs.

**What to do:**

* Keep stacked layers to 2-3 maximum, with manually tuned radii
* Avoid `blur(128px)` or `blur(64px)` over large areas — the biggest radii dominate the cost
* For a static blur, render it once into a PNG and use a regular `<img>` overlay

### filter: blur() and filter: drop-shadow()

Same story as `backdrop-filter` but applied to the element itself rather than behind it. Fine on small elements, expensive on large ones.

### Shadows on many elements

`box-shadow` and `text-shadow` on a few elements are fine. On dozens of elements that also animate, the compositor re-rasterizes each shadowed layer on every frame.

### Large gradients with mask-image

Combined with `backdrop-filter`, `mask-image` can force additional compositor passes. If you have both on the same element, consider whether you need both.

## Image sizing

Image source resolution matters more than file size. Chrome decodes JPEGs and PNGs to raw RGBA bitmaps before displaying them — a decoded bitmap is:

```
bitmap_bytes = width × height × 4
```

A 7000×5000 source image is 140MB decoded, regardless of whether the JPEG on disk is 2MB or 5MB.

**Rule of thumb:** resize source images to at most 2x the canvas dimensions. For a 1920x1080 canvas, 3840x2160 source images are already overkill. Anything above that is paying for memory and texture-upload cost that never shows on screen.

```bash Terminal theme={null}
# ImageMagick one-liner to downsize a directory of images
mogrify -path resized -resize 3840x3840\> *.jpg
```

## Measuring a slow composition

Don't guess — measure. Chrome DevTools has everything you need.

<Steps>
  <Step title="Run preview">
    Start the preview server and open it in Chrome:

    ```bash Terminal theme={null}
    npx hyperframes preview
    ```
  </Step>

  <Step title="Open DevTools → Performance">
    `Cmd+Option+I` (macOS) or `Ctrl+Shift+I` (Linux/Windows), then switch to the **Performance** tab.
  </Step>

  <Step title="Record during playback">
    Hit the record button, click play in the preview, let it run 3-5 seconds through the jank-prone scene, then stop recording.
  </Step>

  <Step title="Read the main thread track">
    Look for long tasks (red-flagged in the timeline). Expand the tallest bars and check what Chrome labels them:

    * **Composite Layers / Paint** with a large duration = compositor cost (backdrop-filter, shadows, large textures)
    * **Decode Image** = image decode on first paint (rare in Chrome 131+, images decode off-thread by default)
    * **Layout / Recalculate Style** = layout thrashing from script
    * **Script** = JS work (rare for compositions, check author scripts)
  </Step>
</Steps>

Once you know which category dominates, you know what to change.

<Tip>
  A composition that runs at 60fps in isolation but stutters only during specific scenes is usually a composite-cost problem. Check which layers become visible during those scenes.
</Tip>

## When preview is unavoidable slow

Some compositions are legitimately too expensive for real-time playback. If you've reduced what you can and preview still stutters, render-to-mp4 and watch the output is a fine workflow — render is still accurate.

```bash Terminal theme={null}
npx hyperframes render --quality draft --output preview.mp4
```

Draft quality renders fast and is visually close to the final render for everything except encoder-level detail.

## WebM encode speed

Transparent WebM output uses FFmpeg's `libvpx-vp9` encoder. VP9 is CPU-heavy, so short overlay renders can spend most of their wall time in the encode stage even when frame capture is fast.

HyperFrames sets `-cpu-used 4` for VP9 by default. On a devbox check using an 8s 1280×720, 15fps VP9-alpha encode, explicit `-cpu-used 4` cut encode time from 6.3s to 2.6s versus libvpx's default, with SSIM 0.9986 and PSNR 50.5dB against the default encode. Your composition and host CPU will move those numbers, but the direction is consistent: higher values trade some compression efficiency for faster WebM encodes.

Tune per deployment with:

```bash Terminal theme={null}
PRODUCER_VP9_CPU_USED=2 npx hyperframes render --format webm --output overlay.webm
```

For one-off local renders, pass the same value directly:

```bash Terminal theme={null}
npx hyperframes render --format webm --vp9-cpu-used 2 --output overlay.webm
```

Valid values are integers from `-8` to `8`; HyperFrames clamps out-of-range values before passing them to FFmpeg.

## Next Steps

<CardGroup cols={2}>
  <Card title="Troubleshooting" icon="wrench" href="/guides/troubleshooting">
    Environment, tooling, and rendering issues
  </Card>

  <Card title="Common Mistakes" icon="triangle-exclamation" href="/guides/common-mistakes">
    Composition pitfalls that break rendering
  </Card>

  <Card title="Rendering" icon="film" href="/guides/rendering">
    Rendering modes, options, and flags
  </Card>

  <Card title="CLI Reference" icon="terminal" href="/packages/cli">
    Full list of CLI commands
  </Card>
</CardGroup>

---

# HDR

**Source:** https://hyperframes.heygen.com/guides/hdr.md

# HDR Rendering

> Render compositions to HDR10 MP4 (BT.2020 PQ or HLG, 10-bit H.265) when sources contain HDR video or images.

Hyperframes can render to HDR10 MP4 (H.265 10-bit, BT.2020) when your composition references HDR video or HDR still images. HDR is auto-detected by default from your media sources and falls back to SDR when none are present.

<Note>
  By default, Hyperframes probes your media and enables HDR only when HDR sources are present. Use `--hdr` to force HDR even without HDR sources, or `--sdr` to force SDR even when HDR sources are present.
</Note>

## Quickstart

<Steps>
  <Step title="Add an HDR source to your composition">
    Hyperframes detects HDR from the source's color space metadata. The most reliable HDR sources are:

    * **HDR video** tagged BT.2020 with PQ (`smpte2084`) or HLG (`arib-std-b67`) transfer
    * **HDR still images** as 16-bit PNG with BT.2020 PQ encoding

    See [Source Media](#source-media-requirements) for full details.
  </Step>

  <Step title="Render normally">
    ```bash Terminal theme={null}
    npx hyperframes render --output output.mp4
    ```

    HDR output requires `--format mp4`. If Hyperframes detects HDR sources, it renders HDR automatically. If you also pass `--format mov` or `--format webm`, Hyperframes logs a warning and falls back to SDR.
  </Step>

  <Step title="Verify the output is HDR">
    Use `ffprobe` to confirm the encoded stream carries HDR color tagging and HDR10 metadata:

    ```bash Terminal theme={null}
    ffprobe -v error -show_streams output.mp4 | grep -E 'color_transfer|color_primaries|color_space'
    ```

    See [Verifying HDR output](#verifying-hdr-output) for what to look for.
  </Step>
</Steps>

## How HDR Mode Works

During render, the producer:

<Steps>
  <Step title="Probes every video and image source">
    Runs `ffprobe` on each `<video>` and `<img>` source to read its color space (primaries, transfer function, matrix). This probe drives the default auto-detect behavior and is skipped only when you explicitly force SDR with `--sdr`.
  </Step>

  <Step title="Picks the dominant HDR transfer">
    If any source uses PQ (`smpte2084`), the output uses **PQ**. Otherwise, if any source uses HLG (`arib-std-b67`), the output uses **HLG**. If no HDR sources are found, the render stays SDR.
  </Step>

  <Step title="Encodes to H.265 10-bit BT.2020">
    The video encoder switches to `libx265` with `-pix_fmt yuv420p10le`, color tagging `colorprim=bt2020:transfer=<smpte2084|arib-std-b67>:colormatrix=bt2020nc`, and HDR10 static metadata (`master-display` and `max-cll`). Without that metadata, players (QuickTime, YouTube, HDR TVs) tone-map the stream as if it were SDR BT.2020 — which looks wrong.
  </Step>

  <Step title="Composites HDR sources natively, converts SDR overlays">
    HDR videos and images are extracted as 16-bit linear-light pixels via FFmpeg, kept out of the DOM screenshot, and composited server-side at full bit depth. SDR DOM overlays (text, shapes, UI from your HTML) are converted from **sRGB** to **BT.2020** before being layered on top, so colors do not shift.
  </Step>
</Steps>

## Source Media Requirements

### HDR video

Hyperframes recognizes HDR video from its `ffprobe` color space metadata:

| Indicator                             | Recognized as HDR   |
| ------------------------------------- | ------------------- |
| `color_primaries` contains `bt2020`   | Yes                 |
| `color_space` contains `bt2020`       | Yes                 |
| `color_transfer = smpte2084` (PQ)     | Yes — PQ            |
| `color_transfer = arib-std-b67` (HLG) | Yes — HLG           |
| All else (e.g. `bt709`, `smpte170m`)  | No — treated as SDR |

A valid HDR source is any MP4 whose stream metadata reports BT.2020 primaries plus PQ or HLG transfer. Hyperframes will detect it automatically:

```bash Terminal theme={null}
ffprobe -v error -show_streams assets/clip.mp4 | grep color
# color_primaries=bt2020
# color_transfer=smpte2084
# color_space=bt2020nc
```

### HDR still images

Hyperframes supports HDR still images delivered as **16-bit PNGs** tagged with BT.2020 primaries and PQ transfer. Drop them into the composition as a normal `<img>`:

```html index.html theme={null}
<img class="clip" data-start="0" data-duration="3"
     src="./assets/hdr-photo.png" />
```

When HDR is enabled, the image is decoded once to 16-bit linear-light RGB and composited natively into the HDR output.

<Note>
  HDR `<img>` decoding is limited to **16-bit PNG**. JPEG, WebP, AVIF, and APNG are not recognized as HDR sources — they load through the normal SDR DOM path. For HDR motion, use a `<video>` element.
</Note>

### SDR sources mixed with HDR

You can freely mix SDR and HDR media in the same composition:

* **SDR videos** stay in the DOM screenshot path and get the sRGB → BT.2020 conversion described above
* **HDR videos** are extracted natively at 16-bit and composited underneath the SDR DOM layer
* **SDR images and DOM elements** (text, shapes, gradients, GSAP animations) are converted from sRGB to BT.2020

This is the same pipeline that handles compositions where, for example, an HDR drone clip plays under an SDR lower-third with animated text.

## Output Format Requirements

| Output format | HDR supported                              |
| ------------- | ------------------------------------------ |
| `mp4`         | Yes — H.265 10-bit BT.2020, HDR10 metadata |
| `mov`         | No — falls back to SDR                     |
| `webm`        | No — falls back to SDR                     |
| `gif`         | No — falls back to SDR                     |

If HDR is enabled and you also pass `--format mov`, `--format webm`, or `--format gif`, Hyperframes logs a message and produces the equivalent SDR render. There is no error — the render still completes — so check the logs (or your verification step) to confirm you got HDR.

## Verifying HDR Output

Use `ffprobe` to confirm both the color tagging and the HDR10 static metadata are present:

```bash Terminal theme={null}
ffprobe -v error -show_streams -select_streams v:0 output.mp4 \
  | grep -E 'codec_name|pix_fmt|color_transfer|color_primaries|color_space'
```

For a PQ HDR10 render you should see:

```
codec_name=hevc
pix_fmt=yuv420p10le
color_space=bt2020nc
color_primaries=bt2020
color_transfer=smpte2084
```

Then check the HDR10 SEI / container boxes:

```bash Terminal theme={null}
ffprobe -v error -show_frames -read_intervals "%+#1" \
  -show_entries frame=side_data_list output.mp4
```

You should see entries for **Mastering display metadata** and **Content light level metadata**. Without them, HDR-aware players will treat the file as SDR BT.2020 and the colors will look washed-out or wrong on an HDR display.

For HLG renders the only difference is `color_transfer=arib-std-b67` — the rest of the checks are the same.

## Docker Rendering

Docker uses the same auto-detect logic as local rendering, so you can produce HDR10 MP4 output from the containerized renderer without extra flags:

```bash Terminal theme={null}
npx hyperframes render --docker --output output.mp4
```

The container runs the same probe → composite → encode pipeline as the local renderer. Verify the output with the same `ffprobe` checks described in [Verifying HDR output](#verifying-hdr-output).

<Note>
  Docker HDR rendering currently runs **CPU-side** for the SDR DOM layer (the container falls back to software WebGL because GPU passthrough is not configured by default). Frame capture is therefore slower than local headed Chrome — measure your own composition with `--quiet` off and compare wall-clock times before sizing CI runners. The encoded HDR10 metadata and pixel data are identical to a local render.
</Note>

## Limitations

* **MP4 only** — HDR output with `--format mov` or `--format webm` falls back to SDR
* **HDR images: 16-bit PNG only** — other formats (JPEG, WebP, AVIF, APNG) are not decoded as HDR and fall through the SDR DOM path
* **H.265 only — H.264 is stripped** — calling the encoder with `codec: "h264"` and `hdr: { transfer }` is rejected; the encoder logs a warning, drops `hdr`, and tags the output as SDR/BT.709. `libx264` cannot encode HDR, so the alternative would be a "half-HDR" file (BT.2020 container tags but a BT.709 VUI block in the bitstream) which confuses HDR-aware players.
* **GPU H.265 emits color tags but no static mastering metadata** — `useGpu: true` with HDR (nvenc, videotoolbox, amf, qsv, vaapi) tags the stream with BT.2020 + the correct transfer (smpte2084 / arib-std-b67) but does **not** embed `master-display` or `max-cll` SEI. ffmpeg does not let those flags pass through hardware encoders. The output is suitable for previews and authoring but not for HDR10-aware delivery (Apple TV, YouTube, Netflix). For spec-compliant HDR10 production output, leave `useGpu: false` so the SW `libx265` path embeds the mastering metadata.
* **Player support** — the [`<hyperframes-player>`](/packages/player) web component plays back the encoded MP4 in the browser and inherits whatever HDR support the host browser provides; it does not implement its own HDR pipeline
* **Headed Chrome HDR DOM capture** — the engine ships a separate WebGPU-based capture path for rendering CSS-animated DOM directly into HDR (`initHdrReadback`, `launchHdrBrowser`). It requires headed Chrome with `--enable-unsafe-webgpu` and is not used by the default render pipeline. See [Engine: HDR](/packages/engine#hdr-apis) if you are building a custom integration.

## Common Pitfalls

| Symptom                                                            | Likely cause                                                                                                |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Output looks identical to SDR                                      | Source media is SDR, or SDR was forced with `--sdr`. Run `ffprobe` on your inputs and check the render logs |
| Output is "kind of HDR" but tone-mapped wrong on YouTube/QuickTime | Missing HDR10 static metadata on the encoded stream. Verify with the ffprobe snippet above                  |
| Docker render is much slower than local                            | Expected — the container falls back to software WebGL for SDR DOM capture. Pixel output is the same         |
| Used `--format webm` and got SDR                                   | Expected — HDR output is MP4 only                                                                           |
| HDR `<img>` looks SDR / washed out                                 | Source is not a 16-bit PNG. Re-export as 16-bit PNG (BT.2020 PQ) or use a `<video>` element instead         |

## Next Steps

<CardGroup cols={2}>
  <Card title="Rendering" icon="film" href="/guides/rendering">
    Local vs Docker, quality presets, workers
  </Card>

  <Card title="CLI" icon="terminal" href="/packages/cli">
    Full `render` command reference including HDR auto-detect, `--hdr`, and `--sdr`
  </Card>

  <Card title="Engine: HDR APIs" icon="gear" href="/packages/engine#hdr-apis">
    Public HDR utilities exported from `@hyperframes/engine`
  </Card>

  <Card title="Common Mistakes" icon="triangle-exclamation" href="/guides/common-mistakes">
    Pitfalls that affect render output
  </Card>
</CardGroup>
