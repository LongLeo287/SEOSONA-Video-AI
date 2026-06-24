# Render Engine Decision — HyperFrames (2026-06-23)

**Decision: HyperFrames is the SOLE render engine. Remotion is ELIMINATED.**

Remotion was evaluated for reference only. It is **source-available with a paid
company license** ($100/mo minimum + $0.01/render for an autonomous commercial
factory). Per the rule "if it charges a fee, drop it," **Remotion is ruled out** —
no further Remotion work, no `@remotion/*` dependency anywhere in SEOSONA Video.
HyperFrames (Apache-2.0, free) carries the entire render path.

## Why

Both engines share the **same render core** — seek each frame in headless Chromium, encode with FFmpeg, deterministic output. So render *quality* is not the deciding factor. The differences:

| | HyperFrames (heygen-com/hyperframes) | Remotion (remotion-dev/remotion) |
|---|---|---|
| Authoring | HTML/CSS + GSAP (what SEOSONA already builds) | React components (frame-driven) |
| License | **Apache-2.0 — free, no thresholds** | Source-available; **paid for 4+ employee companies** → autonomous factory = "Automators" tier **$100/mo min + $0.01/render** |
| Agent fit | Built for agents; LLMs emit HTML easily | React frame-driven is harder for LLMs |
| Captions | DIY (we use faster-whisper already) | Built-in Whisper word-timed captions |
| Migration | already integrated | **rewrite all HTML/GSAP scenes → React** (weeks) |

Migrating would mean **paying a license + a multi-week React rewrite for a render core we already have.** Not justified. If we ever want Remotion's captions, we already have `faster-whisper` (used in the repurpose SRT path) — no license exposure.

## Adopted hardening (done 2026-06-23, commit c9e9140)
1. **Killed the `npx --yes hyperframes@0.6.112` network dependency** — render now prefers the local `node_modules/.bin/hyperframes` binary (pinned in package.json); falls back to npx with a warning only if not installed. Run `npm install` to materialize it. *(Was: every render downloaded from npm mid-pipeline — an npm hiccup killed a run.)*
2. **Untracked the vendored `5_FRAMEWORK/hf_engine/`** (54MB, never executed by the render path) — kept on disk as reference, gitignored.

## Validated by real render tests (2026-06-24)

A minimal HyperFrames project was actually rendered with the local binary to verify each item:

- ✅ **Local binary works** — `node_modules/.bin/hyperframes render` produced an MP4 with no network. Confirms the npx-removal hardening.
- ✅ **0.7.4 ADOPTED** — rendered the same project on 0.6.112 (7.4s) and 0.7.4 (4.8s, **faster**); `--quality high`/`--fps`/`--resolution` all accepted. Default pinned to **0.7.4** in package.json + `pipeline_manager` (revert with `SEOSONA_HF_VERSION=0.6.112`). *Do one real-video render to confirm before high-volume use.*
- ✅ **Shader transitions WORK** — a 3-scene project with `whip-pan` + `light-leak` rendered successfully. The IIFE is vendored at `.agents/skills/graphic-overlays/assets/vendor/shader-transitions.global.js`; a working reference is at `5_FRAMEWORK/hf_core/templates/shader_transitions_reference.html`.
- ✅ **Producer API UNBLOCKED (now opt-in)** — it first failed because `@hyperframes/producer` pulls full `puppeteer` whose bundled Chrome download fails here. Fix: skip the download (`.puppeteerrc.cjs` `skipDownload:true` / `PUPPETEER_SKIP_DOWNLOAD=1`) and point puppeteer at an **existing Chrome** (system Chrome / Playwright Chromium / Edge) via `PUPPETEER_EXECUTABLE_PATH`. Validated: rendered via the Producer API with streaming progress using system Chrome. Implemented as the Node helper `5_FRAMEWORK/hf_producer_render.mjs` (auto-detects Chrome), enabled from the pipeline with `SEOSONA_HF_PRODUCER=1`. **Default stays CLI** (simplest, reliable); the Producer path adds streaming progress + a render queue for high throughput.
  - Install once: `PUPPETEER_SKIP_DOWNLOAD=1 npm install @hyperframes/producer` (the `.puppeteerrc.cjs` makes this automatic), then run with `SEOSONA_HF_PRODUCER=1`.

### Shader-transition integration recipe (for a real-render session)
The 13 transitions are declared via a JS call, NOT attributes. To wire into `_write_hyperframes_render_project`:
1. Copy the vendored `shader-transitions.global.js` into the render `assets/` (next to `gsap.min.js`).
2. Emit each scene as `<div id="scene-N" class="scene">…</div>` (N+1 scenes).
3. After gsap, add `<script src="assets/shader-transitions.global.js"></script>`.
4. Emit: `const tl = HyperShader.init({ bgColor, accentColor, scenes:["scene-0",…], transitions:[{time, shader, duration}] }); window.__timelines["main"] = tl;` — with **exactly `scenes.length-1` transitions**, using the builder's existing `scene_edges` as the `time` values. (Gate behind `SEOSONA_HF_TRANSITIONS=1`; validate on a real video before defaulting on.)

## Still open (need scale / a real session)
- Quality flags are env-tunable now (`SEOSONA_HF_QUALITY/FPS/RESOLUTION`) — turn on `high`/`60`/`4k` per content.
- For scale: `--docker` (byte-identical → content-hash skip-rebuild caching) + `@hyperframes/aws-lambda` / `gcp-cloud-run` to fan out renders.

## Sources
- https://github.com/heygen-com/hyperframes (Apache-2.0, "Write HTML. Render video. Built for agents.")
- https://registry.npmjs.org/hyperframes (latest 0.7.4; pinned 0.6.112)
- https://www.remotion.dev/docs/license · https://remotion.pro/license (company-size license)
- https://github.com/remotion-dev/remotion
