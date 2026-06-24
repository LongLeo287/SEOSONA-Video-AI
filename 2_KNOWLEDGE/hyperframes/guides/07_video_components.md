# HyperFrames — Video Components & Editor Cheatsheet

**Sources:**
- https://hyperframes.heygen.com/guides/video-components.md
- https://hyperframes.heygen.com/guides/video-editor-cheatsheet.md

---

# Video Components

**Source:** https://hyperframes.heygen.com/guides/video-components.md

# Video Components

> Install production-ready video blocks and components from the HyperFrames catalog with one command — or contribute your own.

The HyperFrames **catalog** is a registry of 50+ production-ready video components — captions, code animations, social overlays, shader transitions, data viz, and more. Each one installs into any project with a single command and renders to a deterministic MP4. Don't rebuild a scene from scratch — install the one that already exists.

```bash Terminal theme={null}
npx hyperframes add x-post
```

## Browse the catalog

<CardGroup cols={2}>
  <Card title="Code Animations" icon="code" href="/catalog/blocks/code-morph">
    Typing, diff, morph, highlight, scroll, and GPU 3D/particle/shader code reveals
  </Card>

  <Card title="Captions" icon="closed-captioning" href="/catalog/components/caption-highlight">
    15 caption styles — karaoke, kinetic slam, neon, gradient, glitch, emoji pop
  </Card>

  <Card title="Social Overlays" icon="share-nodes" href="/catalog/blocks/x-post">
    X posts, TikTok / Instagram follow cards, Reddit, Spotify, lower thirds
  </Card>

  <Card title="Shader Transitions" icon="bolt" href="/catalog/blocks/whip-pan">
    14 WebGL transitions — whip pan, glitch, light leak, vortex, iris, burn
  </Card>

  <Card title="Liquid Glass & VFX" icon="wand-magic-sparkles" href="/catalog/blocks/ios26-liquid-glass">
    HTML-in-canvas effects — iOS 26 glass, device frames, portals, shatter, magnetic
  </Card>

  <Card title="Data" icon="chart-column" href="/catalog/blocks/data-chart">
    Animated charts and US / world / region maps with bubbles, flows, and hexes
  </Card>

  <Card title="CSS Transitions" icon="right-left" href="/catalog/blocks/transitions-3d">
    13 zero-dependency transitions — 3D, blur, cover, dissolve, push, radial
  </Card>

  <Card title="Code Snippets" icon="terminal" href="/catalog/blocks/code-snippet-dark-modern">
    24 syntax-highlighted code cards and Apple-terminal themes
  </Card>
</CardGroup>

Plus **Effects** (grain, vignette, shimmer, parallax), **Text Effects** (morph text, texture mask), and **Showcases** — browse them all under the [Catalog](/catalog/blocks/data-chart) tab.

## Blocks vs components

The catalog ships two kinds of item, installed the same way but wired differently:

|                             | **Blocks**                               | **Components**                                        |
| --------------------------- | ---------------------------------------- | ----------------------------------------------------- |
| What it is                  | A full standalone scene                  | A reusable snippet / effect                           |
| Has its own size & duration | Yes                                      | No — adapts to the host                               |
| Installs to                 | `compositions/<name>.html`               | `compositions/components/<name>.html`                 |
| Wired by                    | `data-composition-src` on a host element | Pasting its HTML / CSS / JS into your composition     |
| Examples                    | `x-post`, `data-chart`, `code-morph`     | `grain-overlay`, `caption-highlight`, `shimmer-sweep` |

## Install and wire

<Steps>
  <Step title="Find it">
    Browse the [Catalog](/catalog/blocks/data-chart) tab, or have your AI agent consult the registry — every item lists its name, description, tags, dimensions, and duration.
  </Step>

  <Step title="Add it">
    ```bash Terminal theme={null}
    npx hyperframes add data-chart
    ```

    The CLI writes the files and prints a snippet to paste into your host composition.
  </Step>

  <Step title="Wire a block">
    Blocks are standalone compositions — include them with `data-composition-src` and a timeline position:

    ```html index.html theme={null}
    <div
      data-composition-id="data-chart"
      data-composition-src="compositions/data-chart.html"
      data-start="0"
      data-duration="15"
      data-track-index="1"
      data-width="1920"
      data-height="1080"
    ></div>
    ```
  </Step>

  <Step title="Wire a component">
    Components are snippets — paste their HTML into your composition's markup, their CSS into your styles, and any JS into your script, then hook their timeline calls into yours.
  </Step>
</Steps>

<Tip>
  Using an AI agent? Install the HyperFrames skills with `npx skills add heygen-com/hyperframes` and ask it to "add a chart block" — the `/hyperframes-registry` skill discovers, installs, and wires the catalog item for you.
</Tip>

## Contribute a video component

Your agent already knows how to build video components — it writes HTML, HyperFrames renders it. The registry is where that work ships to **every** HyperFrames user. Spotted a caption style on TikTok that doesn't exist yet, or built a transition worth sharing? Add it to the catalog.

<Info>
  **Quick version** — Fork the repo. Write one HTML file with a paused GSAP timeline. Add `registry-item.json`. Run `hyperframes lint` + `validate`. Publish with `npx hyperframes publish`. Open a PR.
</Info>

Every item is a single self-contained HTML file with a paused GSAP timeline — no build step, no framework. It must be deterministic (seeded randomness only, no `Date.now()` / `Math.random()`), register its timeline on `window.__timelines`, and meet the production-quality bar.

<CardGroup cols={2}>
  <Card title="Contributing to the Catalog" icon="cube" href="/contributing/catalog">
    The full idea → scaffold → build → validate → preview → ship workflow, the `registry-item.json` schema, the rules, and the quality bar
  </Card>

  <Card title="Open a component request" icon="lightbulb" href="https://github.com/heygen-com/hyperframes/issues/new">
    No code needed — share a visual reference and tag it <code>component-request</code>
  </Card>
</CardGroup>

## Next Steps

<CardGroup cols={2}>
  <Card title="Compositions" icon="layer-group" href="/concepts/compositions">
    How blocks nest into a host composition
  </Card>

  <Card title="Variables" icon="sliders" href="/concepts/variables">
    Parameterize an installed block to stay on-brand
  </Card>

  <Card title="The Pipeline" icon="diagram-project" href="/guides/pipeline">
    Design → plan → layout → build → validate → render
  </Card>

  <Card title="Contributing to the Catalog" icon="cube" href="/contributing/catalog">
    Add your own block or component to the registry
  </Card>
</CardGroup>

---

# Video Editor Cheatsheet

**Source:** https://hyperframes.heygen.com/guides/video-editor-cheatsheet.md

# Video Editor Cheatsheet

> Fast reference for video editors and creative people directing agents, cutting timing, tweaking layouts, previewing, and publishing HyperFrames projects.

Use this as a fast reference when you are directing agents, cutting timing, making visual layout tweaks, previewing, and sharing HyperFrames projects.

## The Fast Loop

```bash theme={null}
npx hyperframes init my-video --example blank
cd my-video
npx hyperframes preview
```

Keep the preview running while your agent edits `index.html` or files in `compositions/`. The Studio updates automatically, so you can direct the agent, scrub the result, make manual visual tweaks, then repeat.

Most production work should feel like this:

1. Ask the agent for the first cut, scene, caption pass, transition, or cleanup.
2. Use the Studio preview and timeline to check timing.
3. Use manual DOM editing for Figma-like layout tweaks: select elements, move them, and adjust visual properties directly.
4. Ask the agent to clean up or generalize anything you changed manually.
5. Lint, validate, render, and publish.

Before showing or rendering a project:

```bash theme={null}
npx hyperframes lint
npx hyperframes validate
npx hyperframes render --quality standard --output review.mp4
```

For fast iteration renders, use draft quality:

```bash theme={null}
npx hyperframes render --quality draft --output draft.mp4
```

For final delivery:

```bash theme={null}
npx hyperframes render --quality high --fps 30 --output final.mp4
```

## Terminal Shortcuts

Move around projects quickly:

```bash theme={null}
pwd                 # show current folder
ls                  # list files
cd my-video         # enter a project folder
cd ..               # go up one folder
cd -                # jump back to the previous folder
open .              # open the current folder in Finder on macOS
code .              # open the current folder in VS Code, if installed
```

Common HyperFrames project folders:

```bash theme={null}
cd assets           # source videos, images, audio
cd compositions     # reusable scenes and overlays
cd ..               # back to the project root
```

Run HyperFrames commands from the project root, where `index.html` lives. If you are not sure where you are, run `pwd` then `ls`. If you see `index.html`, you are in the right place.

## Preview Shortcuts

Start the Studio:

```bash theme={null}
npx hyperframes preview
```

Use a different port if `3002` is already busy:

```bash theme={null}
npx hyperframes preview --port 4567
```

Inside the Studio, shortcuts are grouped the same way the playbar's `⌨` panel groups them — playback first, then work-area markers, view controls, and app-level commands. Open the `⌨` panel in the playbar for an in-app cheatsheet, a frame-jump input, and live readouts of the in/out points.

### Playback

| Shortcut              | Action                                        |
| --------------------- | --------------------------------------------- |
| `Space`               | Play or pause                                 |
| `K`                   | Stop                                          |
| `J`                   | Play backward (press again to shuttle faster) |
| `L`                   | Play forward (press again to shuttle faster)  |
| `←` / `→`             | Step 1 frame                                  |
| `Shift+←` / `Shift+→` | Step 10 frames                                |

`J` and `L` build the classic NLE shuttle: each repeat ramps the playback rate up. Tap `K` between shuttle bursts to stop. With `K` held, tapping `J` or `L` steps one frame in that direction.

### Work area (in / out points)

| Shortcut  | Action                                           |
| --------- | ------------------------------------------------ |
| `I`       | Set in-point at the playhead                     |
| `Shift+I` | Clear in-point                                   |
| `O`       | Set out-point at the playhead                    |
| `Shift+O` | Clear out-point                                  |
| `A`       | Jump to in-point (or composition start if unset) |
| `E`       | Jump to out-point (or composition end if unset)  |

The in and out points define a **work area**. When loop is on, both forward and backward playback loop within those boundaries — useful for tightening a transition or scrubbing a single clip without trimming it. The seek bar renders a teal band between in and out, with tick markers at each point. Clear the markers from the `⌨` panel or with `Shift+I` and `Shift+O`.

### View

| Shortcut                                      | Action                         |
| --------------------------------------------- | ------------------------------ |
| `Cmd+Scroll` / `Ctrl+Scroll` over the preview | Zoom the preview at the cursor |

### Application

| Shortcut                                  | Action                                                                          |
| ----------------------------------------- | ------------------------------------------------------------------------------- |
| `Shift+T`                                 | Show or hide the timeline editor                                                |
| `Cmd+1` / `Ctrl+1`                        | Switch sidebar to Compositions                                                  |
| `Cmd+2` / `Ctrl+2`                        | Switch sidebar to Assets                                                        |
| `Cmd+Z` / `Ctrl+Z`                        | Undo                                                                            |
| `Cmd+Shift+Z` / `Ctrl+Shift+Z` / `Ctrl+Y` | Redo                                                                            |
| `Delete` / `Backspace`                    | Delete the selected timeline clip or DOM element (when not typing in an editor) |
| `Escape`                                  | Leave a sub-composition or close editor dialogs                                 |

<Tip>
  Preview uses the same runtime as rendering, so the visual frame matches the output. If preview stutters on a heavy frame but the render is clean, that is expected — preview plays in real time, render captures one frame at a time.
</Tip>

## Agent-Led Editing

Ask the agent to verify visible changes in the browser. For a user-visible edit, a good handoff is:

```
Run the preview, check it with agent-browser, take a screenshot, and render a draft MP4 to take a look at the frames with ffmpeg.
```

## Manual DOM Editing

In the Studio, you can edit the DOM visually for the final 10% of creative adjustment where dragging is faster than describing.

Use manual DOM editing for:

* moving titles, captions, product cards, logos, and overlays into position
* adjusting size, spacing, opacity, color, and other visual properties
* checking composition balance at an exact timestamp
* making Figma-like placement tweaks

Use agents for:

* creating scenes from scratch
* refactoring repeated visual patterns
* wiring GSAP timelines
* fixing broken timing, layout overflow, or render errors
* turning a manual visual tweak into reusable, clean HTML/CSS

After manual DOM edits, ask the agent to inspect the diff and keep the source clean:

```
I moved the hero title and resized the CTA manually in Studio. Inspect the changes, clean up the CSS if needed, then run lint and validate.
```

## CLI Commands Editors Use Most

| Command                                              | Use it for                                                     |
| ---------------------------------------------------- | -------------------------------------------------------------- |
| `npx hyperframes init my-video`                      | Create a new project                                           |
| `npx hyperframes init my-video --example warm-grain` | Start from a visual template                                   |
| `npx hyperframes init my-video --video source.mp4`   | Import video and generate captions from the source audio       |
| `npx hyperframes capture https://example.com`        | Capture a website as source material for a video               |
| `npx hyperframes preview`                            | Open the live Studio preview                                   |
| `npx hyperframes lint`                               | Catch structural mistakes before preview or render             |
| `npx hyperframes validate`                           | Run the composition in headless Chrome to catch runtime errors |
| `npx hyperframes inspect`                            | Find text overflow and layout problems across the timeline     |
| `npx hyperframes snapshot --at 1,3,5`                | Save PNG checks at exact timestamps                            |
| `npx hyperframes render --output final.mp4`          | Render the video                                               |
| `npx hyperframes publish`                            | Upload the project and get a shareable HyperFrames URL         |
| `npx hyperframes doctor`                             | Check Node.js, FFmpeg, Chrome, Docker, and other dependencies  |
| `npx hyperframes docs`                               | Open local CLI docs                                            |
| `npx hyperframes upgrade`                            | Check for a newer CLI version                                  |

## Timing Cheatsheet

Every visible timed layer should usually be a clip:

```html theme={null}
<h1
  class="clip"
  data-start="0"
  data-duration="3"
  data-track-index="0"
>
  Opening title
</h1>
```

Use these attributes like timeline controls:

| Attribute              | Video editor meaning                    |
| ---------------------- | --------------------------------------- |
| `data-start`           | When the layer starts                   |
| `data-duration`        | How long the layer stays active         |
| `data-track-index`     | Timeline track number                   |
| `data-media-start`     | Offset into a media file                |
| `data-volume`          | Audio volume for an audio or video clip |
| `data-composition-src` | Nested scene or reusable overlay        |

For GSAP animation, register one paused timeline per composition:

```html theme={null}
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });

  tl.from("#title", { opacity: 0, y: 40, duration: 0.6 });
  tl.set({}, {}, 5); // keeps the timeline at least 5 seconds long

  window.__timelines["main"] = tl;
</script>
```

<Warning>
  If a video cuts off early, check that the GSAP timeline is at least as long as the intended edit. The final `tl.set({}, {}, 5)` pattern is the fix.
</Warning>

## Render Presets

| Goal                 | Command                                                             |
| -------------------- | ------------------------------------------------------------------- |
| Fast iteration       | `npx hyperframes render --quality draft --output draft.mp4`         |
| Review link          | `npx hyperframes render --quality standard --output review.mp4`     |
| Final export         | `npx hyperframes render --quality high --fps 30 --output final.mp4` |
| Transparent overlay  | `npx hyperframes render --format webm --output overlay.webm`        |
| Deterministic output | `npx hyperframes render --docker --output final.mp4`                |

Use WebM for transparent overlays, captions, and lower thirds. Use `--docker` when you need pixel-consistent output across different machines.

## Publish and Share

Use `publish` when you want to share the editable project, not just the rendered MP4:

```bash theme={null}
npx hyperframes publish
```

Publish zips the current project, uploads it, and prints a stable `hyperframes.dev` URL. The URL includes a claim token so the recipient can open it, claim the project, and continue editing in the web app.

```bash theme={null}
npx hyperframes publish ./my-video   # publish a specific folder
npx hyperframes publish --yes        # skip the confirmation prompt in scripts
```

Publish expects an `index.html` at the project root. It ignores `.git`, `node_modules`, `dist`, `.next`, and `coverage`.

## What Agent Browser Is

`agent-browser` is a browser automation tool for AI agents. It opens Chrome, navigates to your preview, clicks controls, reads page state, and captures screenshots. It is how an agent proves the video preview actually works instead of only saying the code looks right.

Typical verification flow:

```bash theme={null}
agent-browser open http://localhost:3002
agent-browser snapshot -i
agent-browser screenshot --screenshot-dir ./qa
```

Use it when you want the agent to open the HyperFrames Studio preview, play or scrub the video, click timeline controls, inspect visible UI text, capture screenshots for review, or record proof of a tested flow.

For editor-facing changes, keep `npx hyperframes preview` running, then have the agent use `agent-browser` against the local preview URL.

## Quick Fixes

| Problem                        | Command or check                                            |
| ------------------------------ | ----------------------------------------------------------- |
| Preview will not start         | `npx hyperframes doctor`                                    |
| Port already in use            | `npx hyperframes preview --port 4567`                       |
| Render fails                   | `npx hyperframes lint` then `npx hyperframes validate`      |
| Need exact frame checks        | `npx hyperframes snapshot --at 1,2.5,5`                     |
| Text overflows in the frame    | `npx hyperframes inspect`                                   |
| Final render is too slow       | Try `--quality draft`, reduce image sizes, or lower `--fps` |
| Need to share editable project | `npx hyperframes publish`                                   |

<CardGroup cols={2}>
  <Card title="Prompt Guide" icon="wand-magic-sparkles" href="/guides/prompting">
    How to direct AI agents to build better videos
  </Card>

  <Card title="Timeline Editing" icon="timeline" href="/guides/timeline-editing">
    Timing, tracks, and GSAP timeline patterns
  </Card>

  <Card title="Common Mistakes" icon="circle-exclamation" href="/guides/common-mistakes">
    Pitfalls the linter can't catch
  </Card>

  <Card title="CLI Reference" icon="terminal" href="/packages/cli">
    Full command reference
  </Card>
</CardGroup>
