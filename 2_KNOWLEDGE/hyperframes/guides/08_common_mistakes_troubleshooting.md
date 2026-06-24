# HyperFrames — Common Mistakes & Troubleshooting

**Sources:**
- https://hyperframes.heygen.com/guides/common-mistakes.md
- https://hyperframes.heygen.com/guides/troubleshooting.md

---

# Common Mistakes

**Source:** https://hyperframes.heygen.com/guides/common-mistakes.md

# Common Mistakes

> Pitfalls that break Hyperframes compositions.

These are mistakes that cannot be caught by the linter. For automated checks, run `npx hyperframes lint` (see [CLI](/packages/cli#lint)).

<Warning>
  The first two mistakes — animating video element dimensions and controlling media playback in scripts — are the most common causes of broken compositions. If your video looks wrong, check these first.
</Warning>

<AccordionGroup>
  <Accordion title="Animating video element dimensions">
    **Symptom:** Video frames stop updating, or browser performance drops severely.

    **Cause:** GSAP animating `width`, `height`, `top`, `left` directly on a `<video>` element can cause the browser to stop rendering frames.

    **Before (broken):**

    ```javascript index.html theme={null}
    // Animating the video element directly — causes frame rendering to stop
    tl.to("#el-video", { width: 500, height: 280, top: 700, left: 1400 }, 26);
    ```

    **After (fixed):**

    ```html index.html theme={null}
    <!-- Wrap the video in a div and animate the wrapper -->
    <div id="pip-wrapper" style="position: absolute; width: 1920px; height: 1080px;">
      <video id="el-video" data-start="0" data-track-index="0"
             src="./assets/video.mp4" style="width: 100%; height: 100%;"></video>
    </div>
    ```

    ```javascript index.html theme={null}
    // Animate the wrapper — the video fills it at 100%
    tl.to("#pip-wrapper", { width: 500, height: 280, top: 700, left: 1400 }, 26);
    ```

    Use a non-timed wrapper `<div>` for visual effects like picture-in-picture. Animate the wrapper; let the video fill it via CSS.
  </Accordion>

  <Accordion title="Controlling media playback in scripts">
    **Symptom:** Audio/video playback is out of sync, or plays when it should not.

    **Cause:** Calling `video.play()`, `video.pause()`, or setting `audio.currentTime` in your scripts. The [framework owns all media playback](/reference/html-schema#framework-managed-behavior).

    **Before (broken):**

    ```javascript index.html theme={null}
    // Conflicts with framework media sync
    document.getElementById("el-video").play();
    document.getElementById("el-audio").currentTime = 5;
    ```

    **After (fixed):**

    ```javascript index.html theme={null}
    // Don't control media playback at all. The framework handles it.
    // Use GSAP for visual animations only:
    tl.to("#el-video", { opacity: 1, duration: 0.5 }, 0);
    ```

    The framework reads [`data-start`](/concepts/data-attributes#timing-attributes), [`data-media-start`](/concepts/data-attributes#media-attributes), and [`data-volume`](/concepts/data-attributes#media-attributes) to control when and how media plays. See [Compositions: Two Layers](/concepts/compositions#two-layers-primitives-and-scripts) for the separation between HTML primitives and scripts.
  </Accordion>

  <Accordion title="Composition duration shorter than video">
    **Symptom:** Video plays for a few seconds then stops. Timeline shows 8-10 seconds even though the video is minutes long.

    **Cause:** The composition duration equals the [GSAP timeline duration](/guides/gsap-animation#timeline-duration-and-composition-duration), not `data-duration` on the video. If your last GSAP animation ends at 8 seconds, the composition is 8 seconds long — regardless of how long the video source is.

    **Before (broken):**

    ```javascript index.html theme={null}
    // Timeline is only 7.8s long — video cuts off after 7.8 seconds
    tl.to("#lower-third", { left: -640, duration: 0.6 }, 7.2);
    ```

    **After (fixed):**

    ```javascript index.html theme={null}
    tl.to("#lower-third", { left: -640, duration: 0.6 }, 7.2);

    // Extend the timeline to 283 seconds to match the video length
    tl.set({}, {}, 283);
    ```

    `tl.set({}, {}, TIME)` adds a zero-duration tween at the specified time, extending the timeline without affecting any elements.

    <Tip>
      A quick check: run `npx hyperframes compositions` to see the resolved duration of each composition. If it is shorter than expected, your timeline needs extending.
    </Tip>
  </Accordion>

  <Accordion title="Missing class='clip' on timed elements">
    **Symptom:** Elements are always visible, ignoring their `data-start` and `data-duration` timing.

    **Cause:** The [`class="clip"`](/concepts/data-attributes#element-visibility) attribute tells the runtime to manage the element's visibility lifecycle. Without it, the element is always rendered.

    **Before (broken):**

    ```html index.html theme={null}
    <!-- Missing class="clip" — this element is always visible -->
    <h1 id="title" data-start="2" data-duration="5" data-track-index="0">
      Hello World
    </h1>
    ```

    **After (fixed):**

    ```html index.html theme={null}
    <!-- With class="clip", the runtime shows this only from 2s to 7s -->
    <h1 id="title" class="clip" data-start="2" data-duration="5" data-track-index="0">
      Hello World
    </h1>
    ```

    <Note>
      The linter catches this one: `npx hyperframes lint` will flag timed elements missing `class="clip"`.
    </Note>
  </Accordion>

  <Accordion title="Oversized source images">
    **Symptom:** Preview stutters during scenes with images on screen. Render is slower than expected.

    **Cause:** Source images at much higher resolution than the canvas. Chrome decodes images to raw RGBA bitmaps before displaying them, and bitmap size is `width × height × 4` bytes — independent of file size on disk. A 7000×5000 JPEG is 140MB decoded, even if the file is only 2MB.

    Displaying such an image in a 384×1080 region wastes memory and forces the compositor to resample a huge texture every frame.

    **Before (bloated):**

    ```html index.html theme={null}
    <!-- 7000x5000 source, ~140MB decoded -->
    <img class="clip" data-start="0" data-duration="3"
         src="./assets/hero-scene.jpg" />
    ```

    **After (sized to the canvas):**

    ```bash Terminal theme={null}
    # Resize a batch of images to fit within 3840x3840, preserving aspect ratio
    mkdir -p assets/resized
    mogrify -path assets/resized -resize 3840x3840\> assets/*.jpg
    ```

    ```html index.html theme={null}
    <!-- ~3840x2560 source, ~40MB decoded -->
    <img class="clip" data-start="0" data-duration="3"
         src="./assets/resized/hero-scene.jpg" />
    ```

    **Rule of thumb:** source images at most 2x the canvas dimensions. For a 1920×1080 composition, 3840×2160 is already plenty. See [Performance: Image sizing](/guides/performance#image-sizing).
  </Accordion>

  <Accordion title="Heavy backdrop-filter stacks">
    **Symptom:** Specific scenes drop to 5-10fps in preview. The composition is fine elsewhere.

    **Cause:** `backdrop-filter: blur()` on large elements, especially stacked at high radii. Each blur layer forces the compositor to sample pixels behind the element, run a blur kernel, and composite the result. Stacked layers multiply the cost.

    **Before (expensive):**

    ```css theme={null}
    /* 8 layers per side = 16 blur passes every frame */
    .pb-1 { backdrop-filter: blur(1px); }
    .pb-2 { backdrop-filter: blur(2px); }
    .pb-3 { backdrop-filter: blur(4px); }
    .pb-4 { backdrop-filter: blur(8px); }
    .pb-5 { backdrop-filter: blur(16px); }
    .pb-6 { backdrop-filter: blur(32px); }
    .pb-7 { backdrop-filter: blur(64px); }
    .pb-8 { backdrop-filter: blur(128px); }
    ```

    **After (3 tuned layers):**

    ```css theme={null}
    /* Fewer passes with hand-picked radii — visually similar, much cheaper */
    .pb-1 { backdrop-filter: blur(4px); }
    .pb-2 { backdrop-filter: blur(16px); }
    .pb-3 { backdrop-filter: blur(48px); }
    ```

    **Guidelines:**

    * Keep stacked `backdrop-filter` layers to 2-3 per region
    * Avoid radii above 64px over large areas — the biggest radii dominate the total cost
    * For a static blur effect, pre-render it into a PNG once and overlay with a regular `<img>`

    See [Performance: backdrop-filter: blur()](/guides/performance#backdrop-filter-blur) for the full breakdown.
  </Accordion>

  <Accordion title="Expected HDR output but got SDR">
    **Symptom:** Expected an HDR render, but the output looks the same as SDR or `ffprobe` reports `color_transfer=bt709`.

    **Cause:** By default, Hyperframes only switches to HDR encoding when a source `<video>` or `<img>` is tagged with BT.2020 / PQ / HLG color metadata. Common reasons HDR is not engaged:

    1. **All sources are SDR.** Auto-detect leaves SDR-only compositions in SDR. Verify with `ffprobe`:

       ```bash Terminal theme={null}
       ffprobe -v error -show_streams source.mp4 | grep color_transfer
       # Want: smpte2084 (PQ) or arib-std-b67 (HLG)
       # SDR:  bt709, smpte170m, bt470bg, etc.
       ```

    2. **Wrong output format.** HDR output requires MP4. `--format mov` and `--format webm` fall back to SDR — Hyperframes logs a warning when this happens.

    3. **SDR was forced.** `--sdr` disables HDR even when HDR sources are present.

    If you need HDR regardless of source metadata, use `--hdr` to force it.

    `--docker` works the same as local rendering — auto-detect, `--hdr`, and `--sdr` are all forwarded into the container and produce the same output decisions (slower, since the container falls back to software WebGL for SDR DOM capture).

    See [HDR Rendering](/guides/hdr) for the full source requirements and verification steps.
  </Accordion>

  <Accordion title="Timeline key doesn't match data-composition-id">
    **Symptom:** Animations don't play. The composition appears static.

    **Cause:** The key used in `window.__timelines` must exactly match the [`data-composition-id`](/concepts/data-attributes#composition-attributes) attribute on the composition root element.

    **Before (broken):**

    ```javascript index.html theme={null}
    // Mismatch: HTML says "my-video", script registers "root"
    // <div data-composition-id="my-video" ...>
    window.__timelines["root"] = tl;
    ```

    **After (fixed):**

    ```javascript index.html theme={null}
    // Key matches the data-composition-id attribute
    // <div data-composition-id="my-video" ...>
    window.__timelines["my-video"] = tl;
    ```
  </Accordion>
</AccordionGroup>

## Debugging Checklist

When something does not work, check in this order:

1. **Run the linter:** `npx hyperframes lint` — catches most structural issues
2. **Timeline registered?** Is `window.__timelines["<id>"]` set? Does the key match [`data-composition-id`](/concepts/data-attributes#composition-attributes)?
3. **GSAP-only animations?** Only animate visual properties (opacity, transform, color) — see [GSAP Animation](/guides/gsap-animation#key-rules)
4. **Timeline long enough?** Add `tl.set({}, {}, DURATION)` at the end — see [Timeline Duration](/guides/gsap-animation#timeline-duration-and-composition-duration)
5. **Console errors?** Open browser console — runtime errors show as `[Browser:ERROR]`
6. **Still stuck?** See [Troubleshooting](/guides/troubleshooting) for environment and rendering issues

## Next Steps

<CardGroup cols={2}>
  <Card title="Troubleshooting" icon="wrench" href="/guides/troubleshooting">
    Fix environment and rendering issues
  </Card>

  <Card title="GSAP Animation" icon="wand-magic-sparkles" href="/guides/gsap-animation">
    Review animation rules and patterns
  </Card>

  <Card title="HTML Schema Reference" icon="code" href="/reference/html-schema">
    Full attribute reference and checklist
  </Card>

  <Card title="Data Attributes" icon="database" href="/concepts/data-attributes">
    Timing, media, and composition attributes
  </Card>
</CardGroup>

---

# Troubleshooting

**Source:** https://hyperframes.heygen.com/guides/troubleshooting.md

# Troubleshooting

> Solutions for common Hyperframes issues.

If your issue is about a specific coding mistake (animations not working, video cutting off early), see [Common Mistakes](/guides/common-mistakes) first. This page covers environment, tooling, and rendering issues.

<AccordionGroup>
  <Accordion title="&#x22;No composition found&#x22;">
    Your directory needs an `index.html` with a valid [composition](/concepts/compositions). The root element must have a [`data-composition-id`](/concepts/data-attributes#composition-attributes) attribute.

    **Fix:** Run `npx hyperframes init` to create a composition from an [example](/examples), or verify your `index.html` has the correct structure:

    ```html index.html theme={null}
    <div id="root" data-composition-id="my-video"
         data-start="0" data-width="1920" data-height="1080">
      <!-- elements here -->
    </div>
    ```
  </Accordion>

  <Accordion title="&#x22;FFmpeg not found&#x22;">
    Local [rendering](/guides/rendering) requires FFmpeg installed on your system. Install it for your platform:

    <CodeGroup>
      ```bash macOS theme={null}
      brew install ffmpeg
      ```

      ```bash Ubuntu/Debian theme={null}
      sudo apt install ffmpeg
      ```

      ```bash Windows theme={null}
      # Download from https://ffmpeg.org/download.html
      # Add the bin directory to your PATH
      ```

      ```bash Verify installation theme={null}
      ffmpeg -version
      ```
    </CodeGroup>

    After installing, run `npx hyperframes doctor` to verify the CLI can find it.

    <Tip>
      If you cannot install FFmpeg, use [Docker mode](/guides/rendering) instead — it bundles FFmpeg inside the container: `npx hyperframes render --docker --output output.mp4`
    </Tip>
  </Accordion>

  <Accordion title="Lint errors">
    Run `npx hyperframes lint` to check for common structural issues (see [CLI: lint](/packages/cli#lint)):

    | Error                         | Meaning                                                                                                      |
    | ----------------------------- | ------------------------------------------------------------------------------------------------------------ |
    | Missing `data-composition-id` | Root element needs this attribute. See [Compositions](/concepts/compositions).                               |
    | Missing `class="clip"`        | Timed visible elements need this class. See [Data Attributes](/concepts/data-attributes#element-visibility). |
    | Overlapping timelines         | Clips on the same [`data-track-index`](/concepts/data-attributes#timing-attributes) cannot overlap in time.  |
    | Unmuted video elements        | Video elements should be `muted` unless `data-has-audio="true"` is set.                                      |
    | Deprecated attribute names    | `data-layer` and `data-end` have been replaced. Check the [HTML Schema Reference](/reference/html-schema).   |
  </Accordion>

  <Accordion title="Preview not updating">
    Make sure you are editing the `index.html` in the project directory. The [preview server](/packages/cli#preview) watches for file changes and auto-reloads.

    If changes still do not appear:

    1. Check the terminal for errors from the preview server
    2. Stop and restart `npx hyperframes preview`
    3. Hard-refresh the browser: **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (macOS)
    4. Clear the browser cache if CSS changes are not reflected
  </Accordion>

  <Accordion title="Preview stutters or plays at a low frame rate">
    **Symptom:** Preview playback is jerky or skips frames, but the rendered mp4 looks fine.

    **Cause:** Individual frames are taking longer than 16-33ms to paint. Render hides this (it captures frames one at a time), preview does not.

    **Common culprits, most to least frequent:**

    * Stacked `backdrop-filter: blur()` layers, especially at radii above 32px
    * Source images at very high resolution (above 4K) displayed in small regions
    * `filter: blur()` or `filter: drop-shadow()` on large elements
    * Many elements with `box-shadow` or `text-shadow` that also animate

    **First thing to check:** does the stutter happen only during specific scenes, or throughout? Scene-specific stutter usually points at an element, often a blur overlay, that becomes visible in that scene.

    **How to diagnose:** open Chrome DevTools, switch to the Performance tab, record a few seconds of playback, and look for long tasks labeled "Composite Layers" or "Paint". See [Performance: Measuring a slow composition](/guides/performance#measuring-a-slow-composition) for the full walkthrough.

    **Temporary workaround:** render to mp4 and watch the output. Render is accurate regardless of per-frame cost.

    ```bash Terminal theme={null}
    npx hyperframes render --quality draft --output preview.mp4
    ```

    See [Performance](/guides/performance) for the full guide on expensive CSS patterns and how to fix them.
  </Accordion>

  <Accordion title="Render looks different from preview">
    Use `--docker` mode for [deterministic output](/concepts/determinism). Local renders may differ due to:

    * **Font availability** — different fonts on different platforms cause text reflow
    * **Chrome version** — local Chromium vs. Docker's pinned version can render slightly differently
    * **System-specific rendering** — GPU compositing, subpixel antialiasing, etc.

    ```bash Terminal theme={null}
    npx hyperframes render --docker --output output.mp4
    ```

    See [Rendering: When to Use Each Mode](/guides/rendering#when-to-use-each-mode) for guidance on choosing between local and Docker rendering.
  </Accordion>

  <Accordion title="Docker mode fails to start">
    Verify Docker is installed and the daemon is running:

    ```bash Terminal theme={null}
    docker info
    ```

    Common issues:

    * **Docker not running:** Start Docker Desktop or the Docker daemon
    * **Permission denied:** Add your user to the `docker` group (`sudo usermod -aG docker $USER`) and restart your shell
    * **Image pull fails:** Check your internet connection; the first render downloads the Hyperframes Docker image
  </Accordion>

  <Accordion title="Render is slow">
    Try these optimizations:

    1. Use `--quality draft` during development for faster encoding
    2. Run `npx hyperframes benchmark` to find the optimal worker count for your system
    3. Local Chrome/WebGL GPU capture is enabled automatically; compare with `--no-browser-gpu` if troubleshooting
    4. Use `--gpu` for hardware-accelerated encoding (local mode only)
    5. Reduce `--fps` to 24 if 30fps is not needed
    6. Check that your composition does not have unnecessary elements or overly complex animations

    See [Rendering: Options](/guides/rendering#options) for all available flags.
  </Accordion>
</AccordionGroup>

## System Diagnostics

Run `npx hyperframes doctor` to check your environment:

```bash Terminal theme={null}
npx hyperframes doctor
```

This checks for Node.js version, FFmpeg availability, Docker status, and other requirements. If `doctor` reports issues, address them before rendering.

## Still Stuck?

If none of the above resolves your issue:

1. Run `npx hyperframes info` to gather system and project details
2. Check [GitHub Issues](https://github.com/heygen-com/hyperframes/issues) for similar reports
3. Open a new issue with the output of `npx hyperframes info` and steps to reproduce

## Next Steps

<CardGroup cols={2}>
  <Card title="Common Mistakes" icon="triangle-exclamation" href="/guides/common-mistakes">
    Coding pitfalls that break compositions
  </Card>

  <Card title="Rendering" icon="film" href="/guides/rendering">
    Rendering modes, options, and tips
  </Card>

  <Card title="CLI Reference" icon="terminal" href="/packages/cli">
    Full list of CLI commands
  </Card>

  <Card title="Contributing" icon="code-branch" href="/contributing">
    Report bugs and contribute fixes
  </Card>
</CardGroup>
