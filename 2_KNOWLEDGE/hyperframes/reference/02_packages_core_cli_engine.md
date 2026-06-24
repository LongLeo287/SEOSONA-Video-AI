# HyperFrames Packages — core + cli + engine

Source: https://hyperframes.heygen.com/packages/{core,cli,engine}.md (fetched 2026-06-24)

Three foundational packages: `@hyperframes/core` (types, HTML gen, runtime, linter), the `hyperframes` CLI (primary interface), and `@hyperframes/engine` (low-level seek-and-capture engine).

---

# @hyperframes/core

> Types, HTML generation, runtime, and linter — the foundation every other package depends on.

```bash
npm install @hyperframes/core
```

## When to Use

> Most users do not need to install `@hyperframes/core` directly. The CLI, producer, and studio packages all depend on core internally.

**Use `@hyperframes/core` when you need to:**

* Lint compositions programmatically (CI pipelines, editor plugins)
* Parse HTML compositions into structured TypeScript objects
* Generate composition HTML from data (e.g., from an API or AI agent)
* Access the Hyperframes type system for your own tooling
* Embed the Hyperframes runtime in a custom player

## Package Exports

The core package has four entry points:

| Import                       | Description                                             |
| ---------------------------- | ------------------------------------------------------- |
| `@hyperframes/core`          | Types, parsers, generators, adapters, runtime utilities |
| `@hyperframes/core/lint`     | Composition linter                                      |
| `@hyperframes/core/compiler` | Timing compiler, HTML compiler, bundler, static guard   |
| `@hyperframes/core/runtime`  | Pre-built IIFE runtime for browser injection            |

## Types

```typescript
import type {
  TimelineElement,
  TimelineMediaElement,
  TimelineTextElement,
  TimelineCompositionElement,
  TimelineElementType,       // "video" | "image" | "text" | "audio" | "composition"
  CompositionSpec,
  CompositionVariable,
  CanvasResolution,          // "landscape" | "portrait" | "landscape-4k" | "portrait-4k" | "square" | "square-4k"
  Orientation,               // "16:9" | "9:16"
  FrameAdapter,
  FrameAdapterContext,
} from '@hyperframes/core';

// Type guards
import {
  isTextElement,
  isMediaElement,
  isCompositionElement,
  isStringVariable,
  isNumberVariable,
  isColorVariable,
  isBooleanVariable,
  isEnumVariable,
} from '@hyperframes/core';

// Constants
import {
  CANVAS_DIMENSIONS,        // { landscape: { width, height }, portrait: { width, height } }
  TIMELINE_COLORS,
  DEFAULT_DURATIONS,
} from '@hyperframes/core';
```

### Variable Types

```typescript
import type {
  CompositionVariableType,   // "string" | "number" | "color" | "boolean" | "enum"
  StringVariable,
  NumberVariable,
  ColorVariable,
  BooleanVariable,
  EnumVariable,
} from '@hyperframes/core';
```

### Keyframe Types

```typescript
import type {
  Keyframe,
  KeyframeProperties,
  ElementKeyframes,
  StageZoom,
  StageZoomKeyframe,
} from '@hyperframes/core';

import { getDefaultStageZoom } from '@hyperframes/core';
```

## Parsing and Generating HTML

```typescript
import { parseHtml, generateHyperframesHtml } from '@hyperframes/core';
import type { ParsedHtml, CompositionMetadata } from '@hyperframes/core';

// Parse HTML into structured data
const parsed: ParsedHtml = parseHtml(htmlString);
// parsed.elements, parsed.gsapScript, parsed.styles, parsed.resolution, parsed.keyframes

// Extract composition metadata
import { extractCompositionMetadata } from '@hyperframes/core';
const meta: CompositionMetadata = extractCompositionMetadata(htmlString);
// meta.id, meta.duration, meta.width, meta.height, meta.variables
//
// Variable metadata is declared on the document root, for example:
// <html
//   data-composition-id="card"
//   data-composition-duration="3"
//   data-composition-variables='[{"id":"title","label":"Title","type":"string","default":"Hello"}]'
// >

// Read resolved variables inside a composition (declared defaults +
// CLI overrides + per-instance host data-variable-values):
import { getVariables } from '@hyperframes/core';
const { title } = getVariables<{ title: string }>();

// Validate CLI / host overrides against the declared schema:
import { validateVariables, formatVariableValidationIssue } from '@hyperframes/core';
const issues = validateVariables({ title: 'Hello', count: 'three' }, meta.variables);
for (const issue of issues) {
  console.warn(formatVariableValidationIssue(issue));
}

// Generate HTML from structured data
const html = generateHyperframesHtml(elements, {
  animations,
  styles,
  resolution: 'landscape',
  compositionId: 'my-video',
});
```

### Modifying HTML

```typescript
import {
  updateElementInHtml,
  addElementToHtml,
  removeElementFromHtml,
  validateCompositionHtml,
} from '@hyperframes/core';

const updatedHtml = updateElementInHtml(html, 'el-1', { start: 5 });
const newHtml = addElementToHtml(html, newElement);
const cleanHtml = removeElementFromHtml(html, 'el-1');
const result = validateCompositionHtml(html);  // result.valid, result.errors
```

### GSAP Script Parsing

```typescript
import {
  parseGsapScript,
  serializeGsapAnimations,
  updateAnimationInScript,
  addAnimationToScript,
  removeAnimationFromScript,
  getAnimationsForElement,
  validateCompositionGsap,
  keyframesToGsapAnimations,
  gsapAnimationsToKeyframes,
  SUPPORTED_PROPS,            // animatable properties
  SUPPORTED_EASES,            // available easing functions
} from '@hyperframes/core';
import type { GsapAnimation, GsapMethod, ParsedGsap } from '@hyperframes/core';

const parsed: ParsedGsap = parseGsapScript(scriptContent);
// parsed.animations, parsed.timelineVar, parsed.preamble, parsed.postamble
const script = serializeGsapAnimations(parsed.animations);
```

### HTML Generation

```typescript
import {
  generateHyperframesHtml,
  generateGsapTimelineScript,
  generateHyperframesStyles,
} from '@hyperframes/core';

const html = generateHyperframesHtml(elements, options);
const script = generateGsapTimelineScript(animations, options);
const { coreCss, customCss, googleFontsLink } = generateHyperframesStyles(
  elements, 'landscape', customStyles
);
```

### Template Utilities

```typescript
import {
  generateBaseHtml,
  getStageStyles,
  GSAP_CDN,
  BASE_STYLES,
  ELEMENT_BASE_STYLES,
  MEDIA_STYLES,
  TEXT_STYLES,
  ZOOM_CONTAINER_STYLES,
} from '@hyperframes/core';

const baseHtml = generateBaseHtml('landscape');
const styles = getStageStyles('portrait');
```

## Linter

```typescript
import { lintHyperframeHtml, lintMediaUrls } from '@hyperframes/core/lint';
import type {
  HyperframeLintResult,
  HyperframeLintFinding,
  HyperframeLintSeverity,     // "error" | "warning"
  HyperframeLinterOptions,
} from '@hyperframes/core/lint';

const result: HyperframeLintResult = lintHyperframeHtml(html, { filePath: 'index.html' });
// result.ok, result.errorCount, result.warningCount, result.findings

for (const finding of result.findings) {
  console.log(finding.severity, finding.code, finding.message);
  // finding.file, finding.selector, finding.elementId, finding.fixHint, finding.snippet
}

const mediaFindings = lintMediaUrls(result.findings);
```

Detected issues include:

* Missing timeline registration (`window.__timelines`)
* Unmuted video elements (causes autoplay failures)
* Missing `class="clip"` on timed visible elements
* Deprecated attribute names
* Missing composition dimensions (`data-width`, `data-height`)
* Invalid `data-start` references to nonexistent clip IDs

## Compiler

```typescript
// Timing compiler (browser-safe — no Node.js dependencies)
import {
  compileTimingAttrs,
  injectDurations,
  extractResolvedMedia,
  clampDurations,
} from '@hyperframes/core/compiler';
import type {
  UnresolvedElement,
  ResolvedDuration,
  ResolvedMediaElement,
  CompilationResult,
} from '@hyperframes/core/compiler';

const compiled: CompilationResult = compileTimingAttrs(html);
const updatedHtml = injectDurations(html, compiled.durations);
const media: ResolvedMediaElement[] = extractResolvedMedia(html);
```

```typescript
// HTML compiler (Node.js — requires media probing)
import { compileHtml } from '@hyperframes/core/compiler';
import type { MediaDurationProber } from '@hyperframes/core/compiler';

const prober: MediaDurationProber = async (src) => getDuration(src);
const compiledHtml = await compileHtml(html, prober);
```

```typescript
// HTML bundler (Node.js — bundles to single file)
import { bundleToSingleHtml } from '@hyperframes/core/compiler';
import type { BundleOptions } from '@hyperframes/core/compiler';

const bundled = await bundleToSingleHtml({ entryPath: './index.html', inline: true });
```

```typescript
// Static guard — validate HTML contract
import { validateHyperframeHtmlContract } from '@hyperframes/core/compiler';
import type {
  HyperframeStaticGuardResult,
  HyperframeStaticFailureReason,
} from '@hyperframes/core/compiler';

const guard: HyperframeStaticGuardResult = validateHyperframeHtmlContract(html);
// guard.ok, guard.failures[]
// Failure reasons: "missing_composition_id" | "missing_composition_dimensions"
//   | "missing_timeline_registry" | "invalid_script_syntax"
//   | "invalid_static_hyperframe_contract"
```

## Runtime

```typescript
import {
  loadHyperframeRuntimeSource,
  buildHyperframesRuntimeScript,
  HYPERFRAME_RUNTIME_ARTIFACTS,
  HYPERFRAME_RUNTIME_CONTRACT,
  HYPERFRAME_RUNTIME_GLOBALS,
  HYPERFRAME_BRIDGE_SOURCES,
  HYPERFRAME_CONTROL_ACTIONS,
} from '@hyperframes/core';
import type {
  HyperframeControlAction,
  HyperframesRuntimeBuildOptions,
} from '@hyperframes/core';

const runtimeSource = loadHyperframeRuntimeSource();
const script = buildHyperframesRuntimeScript(options);
```

The pre-built runtime IIFE is available as a direct import:

```typescript
import runtime from '@hyperframes/core/runtime';
```

## Frame Adapters

```typescript
import { createGSAPFrameAdapter } from '@hyperframes/core';
import type {
  FrameAdapter,
  FrameAdapterContext,
  GSAPTimelineLike,
  CreateGSAPFrameAdapterOptions,
} from '@hyperframes/core';

const adapter: FrameAdapter = createGSAPFrameAdapter({
  id: 'my-composition',
  fps: 30,
  timeline: gsapTimeline,
});

await adapter.init?.(context);
const durationFrames = adapter.getDurationFrames();
await adapter.seekFrame(42);
await adapter.destroy?.();
```

## Media Utilities

```typescript
import {
  MEDIA_VISUAL_STYLE_PROPERTIES,
  copyMediaVisualStyles,
  quantizeTimeToFrame,
} from '@hyperframes/core';
import type { MediaVisualStyleProperty } from '@hyperframes/core';

const frameTime = quantizeTimeToFrame(5.033, 30); // → snapped to frame
copyMediaVisualStyles(fromElement, toElement);
```

## Picker API

```typescript
import type {
  HyperframePickerApi,
  HyperframePickerBoundingBox,
  HyperframePickerElementInfo,
} from '@hyperframes/core';
```

---

# CLI (`hyperframes`)

> Create, preview, and render HTML video compositions from the command line.

```bash
npm install -g hyperframes
# or use directly with npx
npx hyperframes <command>
```

## Agent-Friendly by Default

Commands support explicit flags and parseable output. Inputs via flags (e.g., `--example`, `--video`, `--output`); missing required flags fail fast with a clear error; output is plain text. Interactivity is command-specific (`init` prompts on TTY by default; pass `--non-interactive` to force non-interactive). `--human-friendly` is command-specific (e.g., `catalog`), not global.

### JSON Output and `_meta` Envelope

All commands that support `--json` wrap output with a `_meta` field containing version-check info:

```json
{
  "name": "my-video",
  "duration": 10.5,
  "_meta": { "version": "0.1.4", "latestVersion": "0.1.5", "updateAvailable": true }
}
```

Version data comes from a 24-hour cache — no network request during `--json` output. Passive update notices print to stderr after command completion (suppressed in CI, non-TTY, or with `HYPERFRAMES_NO_UPDATE_CHECK=1`).

## Commands

### Create commands

#### `init`
Create a new composition project from an example.
```bash
npx hyperframes init my-video --example blank --video video.mp4
npx hyperframes init my-video --example blank --tailwind
npx hyperframes init my-video   # human mode, interactive
```
| Flag | Description |
| --- | --- |
| `--example, -e` | Example to scaffold (required in default mode) |
| `--resolution` | `landscape` (1920×1080), `portrait` (1080×1920), `landscape-4k` (3840×2160), `portrait-4k` (2160×3840), `square` (1080×1080), `square-4k` (2160×2160). Aliases: `1080p`, `4k`, `uhd`, `1080p-square`, `square-1080p`, `4k-square`. Default: keep template dimensions. |
| `--video, -V` | Path to a video file (MP4, WebM, MOV) |
| `--audio, -a` | Path to an audio file (MP3, WAV, M4A) |
| `--tailwind` | Add Tailwind CSS browser-runtime support to scaffolded HTML |
| `--skip-skills` | Skip AI coding skills installation |
| `--skip-transcribe` | Skip automatic whisper transcription |
| `--model` | Whisper model (e.g. `small.en`, `medium.en`, `large-v3`) |
| `--language` | Language code (e.g. `en`, `es`, `ja`) |

Examples: `blank`, `warm-grain`, `play-mode`, `swiss-grid`, `vignelli`. `--tailwind` injects pinned Tailwind v4 browser runtime and exposes `window.__tailwindReady` promise renders wait on before frame 0. When `--video`/`--audio` is provided, the CLI auto-transcribes with Whisper and patches captions in.

#### `add`
Install a **block** (sub-composition scene) or **component** (effect/snippet) from the registry into an existing project.
```bash
npx hyperframes add claude-code-window
npx hyperframes add shader-wipe --dir ./my-video
npx hyperframes add shader-wipe --no-clipboard --json
```
| Flag | Description |
| --- | --- |
| `<name>` (positional) | Registry item name |
| `--dir` | Project directory |
| `--no-clipboard` | Skip copying include snippet to clipboard |
| `--json` | Machine-readable summary |

Reads `hyperframes.json` for registry + drop paths. Output = files + a paste snippet (`<iframe>` tag for blocks, fragment path for components).

#### `catalog`
Browse the registry.
```bash
npx hyperframes catalog --type block --tag social
npx hyperframes catalog --json
npx hyperframes catalog --human-friendly   # interactive picker
```
Flags: `--type` (block|component), `--tag`, `--json`, `--human-friendly`.

#### `compositions`
List all compositions: shows ID, duration, resolution, element count. Flag: `--json`.

#### `transcribe`
Transcribe audio/video to word-level timestamps, or import an existing transcript.
```bash
npx hyperframes transcribe audio.mp3
npx hyperframes transcribe video.mp4 --model medium.en --language en
npx hyperframes transcribe subtitles.srt    # or .vtt, .json
```
| Flag | Description |
| --- | --- |
| `--dir, -d` | Project directory |
| `--model, -m` | Whisper model (default `small.en`): `tiny.en`, `base.en`, `small.en`, `medium.en`, `large-v3` |
| `--language, -l` | Language code |
| `--json` | Output as JSON |

Supported transcript imports: whisper.cpp JSON, OpenAI Whisper API JSON, SRT, VTT. All normalized to `[{text, start, end}]` and saved as `transcript.json`; caption HTML files are auto-patched.

#### `tts`
Generate speech from text using local Kokoro-82M (no API key, on-device).
```bash
npx hyperframes tts "Welcome to HyperFrames"
npx hyperframes tts "Hello world" --voice am_adam
npx hyperframes tts "Intro" --voice bf_emma --output narration.wav
npx hyperframes tts "Slow and clear" --speed 0.8
npx hyperframes tts --list
```
| Flag | Description |
| --- | --- |
| `--output, -o` | Output file path (default `speech.wav`) |
| `--voice, -v` | Voice ID |
| `--speed, -s` | Speed multiplier (default 1.0) |
| `--lang, -l` | Phonemizer locale (`en-us`, `en-gb`, `es`, `fr-fr`, `hi`, `it`, `pt-br`, `ja`, `zh`); inferred from voice ID prefix when omitted |
| `--list` | List voices |
| `--json` | Output as JSON |

Voice ID first letter = phonemizer language (`a`=American, `b`=British, `e`=Spanish, `f`=French, `h`=Hindi, `i`=Italian, `j`=Japanese, `p`=Brazilian Portuguese, `z`=Mandarin).

#### `remove-background`
Remove background from video/image using local AI (`u2net_human_seg`, MIT, ~168 MB ONNX). Output is transparent media.
```bash
npx hyperframes remove-background avatar.mp4 -o transparent.webm
npx hyperframes remove-background avatar.mp4 -o transparent.mov   # ProRes 4444
npx hyperframes remove-background portrait.jpg -o cutout.png
npx hyperframes remove-background avatar.mp4 -o subject.webm --background-output plate.webm
npx hyperframes remove-background --info
```
| Flag | Description |
| --- | --- |
| `--output, -o` | Output path; format from extension: `.webm` (default), `.mov`, `.png` |
| `--background-output, -b` | Inverse-alpha background plate (`.webm`/`.mov` only) |
| `--device` | `auto` (default), `cpu`, `coreml`, `cuda` |
| `--quality` | WebM preset: `fast` (crf 30), `balanced` (crf 18, default), `best` (crf 12) |
| `--info` | Print detected providers and exit |
| `--json` | Output as JSON |

For CUDA: set `HYPERFRAMES_CUDA=1`. Output formats: `.webm` (VP9 alpha, ~1MB/4s@1080p), `.mov` (ProRes 4444, ~50MB), `.png`. Chrome `<video>` only respects alpha for `yuva420p` WebM with `alpha_mode=1` (CLI sets both).

#### `capture`
Capture a website — screenshots, design tokens, fonts, assets, animations.
```bash
npx hyperframes capture https://stripe.com
npx hyperframes capture https://linear.app -o linear-capture
```
| Flag | Description |
| --- | --- |
| `-o, --output` | Output dir (default `./capture`, auto-suffixes) |
| `--timeout` | Page load timeout ms (default 120000) |
| `--skip-assets` | Skip downloading images/fonts |
| `--max-screenshots` | Max screenshots (default 24) |
| `--json` | Structured JSON |

Output is a self-contained dir with a `CLAUDE.md` file. Used by `/website-to-video` skill as step 1. Set `GEMINI_API_KEY` (or `OPENROUTER_API_KEY`) in `.env` for AI image descriptions.

### Preview commands

#### `preview`
Live preview server with hot reload.
```bash
npx hyperframes preview [dir]
npx hyperframes preview --port 4567
```
Flag `--port` (default 3002). Opens in Hyperframes Studio. Three auto-detected modes: embedded (default for npx), local studio (if `@hyperframes/studio` installed), monorepo.

#### `publish`
Upload project and get a stable `hyperframes.dev` URL.
```bash
npx hyperframes publish [dir]
npx hyperframes publish --yes
```
Flag `--yes` (skip confirmation). Zips, uploads to HyperFrames publish backend, prints stable claimable URL.

#### `lint`
```bash
npx hyperframes lint [dir]
npx hyperframes lint [dir] --verbose   # include info-level
npx hyperframes lint [dir] --json
```
Flags: `--json`, `--verbose`. Severity: Error (`✗`, must fix), Warning (`⚠`), Info (`ℹ`, `--verbose` only).

#### `beats`
Detect beats in a composition's music track, write beat file for Studio guides.
```bash
npx hyperframes beats [dir]
npx hyperframes beats [dir] --json
```
Finds music track (`<audio data-timeline-role="music">` or id `music`/`bgm`/`soundtrack`), runs same detection Studio uses, writes `beats/<audio-path>.json`:
```json
{ "version": 1, "audio": "music.wav", "beats": [{ "time": 2.027, "strength": 0.924 }] }
```
Flag `--json` outputs `{ ok, file, count, bpm }`. Requires local Chrome.

#### `inspect`
Inspect rendered visual layout across the timeline (also alias `layout`).
```bash
npx hyperframes inspect [dir] --json
npx hyperframes inspect [dir] --samples 15
npx hyperframes inspect [dir] --at 1.5,4,7.25
```
Reports text/elements escaping boxes (`text_box_overflow`), overlapping text (`content_overlap`), occluded text (`text_occluded`).
| Flag | Description |
| --- | --- |
| `--json` | Agent-readable findings with `schemaVersion`, `samples`, `issues`, bounding boxes |
| `--samples` | Midpoint samples (default 9) |
| `--at` | Comma-separated timestamps |
| `--tolerance` | Allowed pixel overflow (default 2) |
| `--timeout` | Runtime-init wait ms (default 5000) |
| `--collapse-static` | Collapse repeated static issues (default true) |
| `--max-issues` | Max findings (default 80) |
| `--strict` | Exit non-zero on warnings too |

Opt-out attributes: `data-layout-allow-overflow`, `data-layout-ignore`, `data-layout-allow-overlap`, `data-layout-allow-occlusion`.

**Motion verification**: drop a `*.motion.json` sidecar next to the composition; `inspect` evaluates it automatically. Assertions:
```json
{
  "duration": 6,
  "assertions": [
    { "kind": "appearsBy", "selector": "#headline", "bySec": 0.5 },
    { "kind": "before", "a": "#headline", "b": "#cta" },
    { "kind": "staysInFrame", "selector": ".card" },
    { "kind": "keepsMoving", "withinSelector": ".scene" }
  ]
}
```
| Assertion | Checks |
| --- | --- |
| `appearsBy(selector, bySec)` | visible (opacity ≥ 0.5) no later than `bySec` (`motion_appears_late`) |
| `before(a, b)` | `a` appears strictly before `b` (`motion_out_of_order`) |
| `staysInFrame(selector)` | box never leaves canvas once visible (`motion_off_frame`) |
| `keepsMoving(withinSelector?)` | no static window > `maxStaticSec` (default 2s) (`motion_frozen`) |

Motion findings are errors by default; a selector matching nothing → `motion_selector_missing`.

#### `snapshot`
Capture key frames as PNG screenshots.
```bash
npx hyperframes snapshot my-project --at 2.9,10.4,18.7
npx hyperframes snapshot my-project --frames 10
```
Flags: `--frames` (default 5), `--at`, `--timeout` (default 5000). Captures 1920×1080 PNGs.

### Build commands

#### `render`
Render to MP4 or WebM.
```bash
npx hyperframes render --output output.mp4
npx hyperframes render --docker --output output.mp4   # deterministic
npx hyperframes render --format webm --output overlay.webm   # transparency
npx hyperframes render --output output.mp4 --fps 60 --quality high
npx hyperframes render --no-browser-gpu --output cpu-browser.mp4
npx hyperframes render --gpu --output gpu.mp4
```
| Flag | Values | Default | Description |
| --- | --- | --- | --- |
| `--output` | path | `renders/<name>.mp4` | Output file path |
| `--format` | mp4, webm, mov, png-sequence | mp4 | Output format (WebM/MOV = transparency; png-sequence = dir of RGBA PNGs) |
| `--fps` | 24, 30, 60 | 30 | Frames per second |
| `--quality` | draft, standard, high | standard | Encoding quality (drives CRF/bitrate) |
| `--crf` | 0-51 | — | Override CRF (lower=higher quality). Exclusive w/ `--video-bitrate` |
| `--video-bitrate` | e.g. `10M`, `5000k` | — | Target bitrate. Exclusive w/ `--crf` |
| `--video-frame-format` | auto, jpg, png | auto | Source video frame extraction. `png` for UI/screen recordings |
| `--resolution` | landscape, portrait, landscape-4k, portrait-4k, square, square-4k (+ aliases) | — | Output resolution preset; supersamples via Chrome `deviceScaleFactor`. Aspect must match; integer multiple. Not w/ `--hdr` |
| `--hdr` | — | off | Force HDR output. MP4 only |
| `--sdr` | — | off | Force SDR output |
| `--workers` | 1-8 | 4 | Parallel render workers |
| `--low-memory-mode` / `--no-low-memory-mode` | — | auto (≤8GB RAM) | Force low-memory safe profile. Env fallback `PRODUCER_LOW_MEMORY_MODE`. Auto-detect reads host RAM (`os.totalmem()`), not cgroup limits — containerized/serverless/`--docker` should set env explicitly |
| `--gpu` | — | off | GPU encoding (NVENC, VideoToolbox, AMF, VAAPI, QSV) |
| `--browser-gpu` / `--no-browser-gpu` | — | on locally, off in Docker | Host GPU accel for local Chrome/WebGL capture |
| `--docker` | — | off | Docker deterministic rendering |
| `--quiet` | — | off | Suppress verbose output |
| `--variables` | JSON object | — | Variable overrides merged over `data-composition-variables` defaults |
| `--variables-file` | path | — | JSON file with overrides |
| `--strict-variables` | — | off | Fail if any `--variables` key undeclared or wrong type |
| `--browser-timeout` | seconds (0.001–86400) | 60 | Puppeteer page-nav timeout. Flag takes SECONDS; env `PRODUCER_PAGE_NAVIGATION_TIMEOUT_MS` takes MS. Heavy comps may also need `PRODUCER_PUPPETEER_PROTOCOL_TIMEOUT_MS`, `PRODUCER_PLAYER_READY_TIMEOUT_MS` |

Parametrized renders: declare `data-composition-variables` on root, override with `--variables`/`--variables-file`. WebM transparency: `--format webm` → VP9+alpha; root HTML should use `background: transparent`. Overlay with ffmpeg:
```bash
ffmpeg -c:v libvpx-vp9 -i captions.webm -i background.mp4 \
  -filter_complex "[1:v][0:v]overlay=0:0" -y composited.mp4
```

#### `benchmark`
Find optimal render settings. Flags `--runs` (1-20, default 3), `--json`.

### Utility commands

#### `doctor`
Check environment (CLI version, Node.js, FFmpeg, FFprobe, Chrome, Docker). Flag `--json` (includes `_meta`). `doctor --json` always exits 0 on successful execution — health is in `ok` field. Gate via `jq -e '.ok'`. Paths redacted to `$HOME` in JSON.

#### `info`
Project metadata (name, resolution, duration, element counts, tracks, size). Flag `--json`.

#### `upgrade`
```bash
npx hyperframes upgrade --check --json
```
Flags `--check`, `--json`, `--yes`. Returns `{ current, latest, updateAvailable, _meta }`.

#### `browser`
```bash
npx hyperframes browser ensure   # find/download Chrome
npx hyperframes browser path     # print exe path
npx hyperframes browser clear    # remove cached download
```

#### `docs`
Inline docs: `data-attributes`, `examples`, `rendering`, `gsap`, `troubleshooting`, `compositions`.

#### `feedback`
```bash
npx hyperframes feedback --rating 5
npx hyperframes feedback --rating 3 --comment "..."
```
Flags `--rating` (1–5, required), `--comment`. No-op when telemetry disabled.

#### `telemetry`
`enable` / `disable` / `status`. Collects command names, render perf, error/checkpoint names, system info, coarse env fingerprint (incl. coding-agent name like `claude_code`/`codex`/`cursor`). Redacts paths/query strings. Disable with `HYPERFRAMES_NO_TELEMETRY=1`.

#### `skills`
Install HyperFrames skills for AI coding tools.
```bash
npx hyperframes skills              # all defaults (Claude, Gemini, Codex)
npx hyperframes skills --claude --gemini
```
Flags: `--claude` (`~/.claude/skills/`), `--gemini` (`~/.gemini/skills/`), `--codex` (`~/.codex/skills/`), `--cursor` (`.cursor/skills/`). Skills: `/hyperframes` (entry), `/hyperframes-core`, `/hyperframes-animation`, `/hyperframes-creative`, `/hyperframes-media`, `/hyperframes-registry`. As of v0.4.5, CLI sets `GIT_CLONE_PROTECTION_ACTIVE=0` to avoid Git LFS post-checkout-hook clone failure.

## `hyperframes auth`

Sign in to HeyGen. Credentials stored in `~/.heygen/credentials` (mode `0600`), **shared with the `heygen` CLI**. Resolution order: `HEYGEN_API_KEY` env → `HYPERFRAMES_API_KEY` env → `~/.heygen/credentials`.

Subcommands:
- `auth login --api-key` — save key (verified against `GET /v3/users/me`). Interactive prompt or `echo "$KEY" | hyperframes auth login --api-key`.
- `auth status` — show source, type, identity. Exits non-zero when nothing configured. `--json`.
- `auth logout` — remove credential. `--keep-api-key`, `--yes`.

Env vars: `HEYGEN_API_KEY`, `HYPERFRAMES_API_KEY` (alias), `HEYGEN_API_URL` (default `https://api.heygen.com`), `HEYGEN_CONFIG_DIR` (default `~/.heygen`).

## `hyperframes cloud`, `lambda`, `cloudrun`

See `06_deployment_cloud_scale.md` for the full cloud/lambda/cloudrun subcommand reference. Quick chooser:
- `hyperframes render` (local): fastest iteration loop during authoring.
- `hyperframes lambda render`: bring-your-own-AWS distributed rendering, chunked parallelism.
- `hyperframes cloud render`: zero-infra, HeyGen-hosted, pay per credit.
- `hyperframes cloudrun`: GCP equivalent of lambda.

## hyperframes.json

`hyperframes init` writes this; `hyperframes add` reads it.
```json
{
  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": {
    "blocks": "compositions",
    "components": "compositions/components",
    "assets": "assets"
  }
}
```
| Field | Description |
| --- | --- |
| `registry` | Base URL `add` pulls from |
| `paths.blocks` | Where block `.html` files land |
| `paths.components` | Where component files land |
| `paths.assets` | Where asset files land |

---

# @hyperframes/engine

> Seekable page-to-video capture engine using Chrome's BeginFrame API.

The low-level video capture pipeline: loads an HTML page in headless Chrome, seeks to each frame independently, captures pixel buffers via Chrome's `HeadlessExperimental.beginFrame`. This is the layer that makes Hyperframes rendering deterministic.

```bash
npm install @hyperframes/engine
```

> WARNING: Most users should NOT use the engine directly. Use the CLI (`npx hyperframes render`) or the producer package instead — they handle runtime injection, audio mixing, and encoding for you.

## How It Works (seek-and-capture loop)

1. **Launch headless Chrome** — `chrome-headless-shell`, controlled via Chrome DevTools Protocol (CDP).
2. **Load the composition** — HTML loaded into a page; Hyperframes runtime injected.
3. **Seek to each frame** — calls `renderSeek(time)` per frame. No wall clock.
4. **Capture via BeginFrame** — `HeadlessExperimental.beginFrame` captures compositor output as a pixel buffer.
5. **Hand off frames** — buffers passed to a consumer (typically FFmpeg via producer).

## Configuration

```typescript
import { resolveConfig, DEFAULT_CONFIG } from '@hyperframes/engine';
import type { EngineConfig } from '@hyperframes/engine';

const config = DEFAULT_CONFIG;
const config2 = resolveConfig({ /* ... custom options */ });
```

### Quality Presets
| Preset | Use Case | Speed |
| --- | --- | --- |
| `draft` | Fast iteration | Fastest |
| `standard` | Production balance | Moderate |
| `high` | Final delivery | Slowest |

### FPS Options
`24` (cinematic, smaller files), `30` (standard web), `60` (smooth motion, UI animations).

## Programmatic Usage (session-based)

```typescript
import {
  createCaptureSession,
  initializeSession,
  captureFrame,
  captureFrameToBuffer,
  getCompositionDuration,
  closeCaptureSession,
} from '@hyperframes/engine';

const session = await createCaptureSession({ fps: { num: 30, den: 1 }, width: 1920, height: 1080 });
await initializeSession(session, './my-video/index.html');
const duration = getCompositionDuration(session);

const totalFrames = Math.ceil(duration * 30);
for (let i = 0; i < totalFrames; i++) {
  const result = await captureFrame(session, i);          // result.path, result.captureTimeMs
  const bufResult = await captureFrameToBuffer(session, i); // bufResult.buffer, bufResult.captureTimeMs
}

await closeCaptureSession(session);
```

### Browser Management
```typescript
import { acquireBrowser, releaseBrowser, resolveHeadlessShellPath, buildChromeArgs } from '@hyperframes/engine';

const browser = await acquireBrowser();
const chromePath = await resolveHeadlessShellPath();
await releaseBrowser(browser);
```

### Encoding (FFmpeg; MP4 h264, WebM VP9 with alpha)
```typescript
import {
  encodeFramesFromDir, muxVideoWithAudio, applyFaststart,
  detectGpuEncoder, getEncoderPreset, ENCODER_PRESETS,
} from '@hyperframes/engine';

const mp4Preset = getEncoderPreset('standard', 'mp4');
// { codec: "h264", pixelFormat: "yuv420p", preset: "medium", quality: 23 }
const webmPreset = getEncoderPreset('standard', 'webm');
// { codec: "vp9", pixelFormat: "yuva420p", preset: "good", quality: 23 }

await encodeFramesFromDir(framesDir, 'frame_%06d.png', outputPath, {
  fps: { num: 30, den: 1 }, ...webmPreset,
});
await muxVideoWithAudio(videoPath, audioPath, outputPath);  // Opus for WebM, AAC for MP4
await applyFaststart(inputPath, outputPath);                // MP4 faststart; no-op for WebM
const gpu = await detectGpuEncoder();
// gpu: "nvenc" | "videotoolbox" | "vaapi" | "qsv" | "amf" | null
```

**WebM with VP9 Alpha**: `format: "webm"` configures `libvpx-vp9` + `yuva420p`, `-auto-alt-ref 0`, `alpha_mode=1`, `-row-mt 1`, Opus audio.

### Streaming Encoder (memory-efficient, no disk frames)
```typescript
import { spawnStreamingEncoder } from '@hyperframes/engine';

const encoder = await spawnStreamingEncoder({
  outputPath: './output.mp4', fps: { num: 30, den: 1 }, width: 1920, height: 1080,
});
encoder.writeFrame(frameBuffer);
const result = await encoder.finalize();
```

### Video Frame Extraction
```typescript
import {
  parseVideoElements, extractAllVideoFrames, getFrameAtTime,
  createFrameLookupTable, FrameLookupTable,
} from '@hyperframes/engine';

const videos = parseVideoElements(html);
const frames = await extractAllVideoFrames(videoPath, { fps: 30 });
const lookup = createFrameLookupTable(frames);
const frame = lookup.getFrameAtTime(5.0);
```

### Audio Processing
```typescript
import { parseAudioElements, processCompositionAudio } from '@hyperframes/engine';

const audioElements = parseAudioElements(html);
const mixResult = await processCompositionAudio({ audioElements, duration, fps });
```

### Parallel Rendering
```typescript
import {
  calculateOptimalWorkers, distributeFrames,
  executeParallelCapture, getSystemResources,
} from '@hyperframes/engine';

const resources = getSystemResources();
const workers = calculateOptimalWorkers(totalFrames);
const tasks = distributeFrames(totalFrames, workers);
const results = await executeParallelCapture(tasks);
```

### File Server
```typescript
import { createFileServer } from '@hyperframes/engine';

const server = await createFileServer({ root: './my-video', port: 0 });
// server.url, server.port
await server.close();
```

## HDR APIs

Two layers: color-space utilities (classify sources, configure FFmpeg encoder) and a WebGPU readback runtime (capture CSS-animated DOM into HDR). For end-to-end HDR use the producer/CLI with `--hdr`/`--sdr` auto-detect.

### Color space utilities
```typescript
import {
  isHdrColorSpace, detectTransfer, analyzeCompositionHdr,
  getHdrEncoderColorParams, DEFAULT_HDR10_MASTERING,
} from '@hyperframes/engine';
import type { HdrTransfer, HdrEncoderColorParams, HdrMasteringMetadata } from '@hyperframes/engine';

isHdrColorSpace(colorSpace);          // boolean — true for BT.2020 / PQ / HLG
detectTransfer(colorSpace);           // 'pq' | 'hlg'
analyzeCompositionHdr([cs1, cs2]);    // { hasHdr, dominantTransfer: 'pq' | 'hlg' | null }

const params = getHdrEncoderColorParams('pq');
// {
//   colorPrimaries: 'bt2020', colorTrc: 'smpte2084', colorspace: 'bt2020nc',
//   pixelFormat: 'yuv420p10le',
//   x265ColorParams: 'colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:master-display=...:max-cll=1000,400',
//   mastering: { masterDisplay: '...', maxCll: '1000,400' },
// }
```
`getHdrEncoderColorParams` always includes color tagging + HDR10 static metadata (mastering display + content light level).

### WebGPU HDR DOM capture
```typescript
import {
  launchHdrBrowser, buildHdrChromeArgs, initHdrReadback,
  uploadAndReadbackHdrFrame, float16ToPqRgb,
} from '@hyperframes/engine';

const { browser, page } = await launchHdrBrowser({ width: 1920, height: 1080 });
const ok = await initHdrReadback(page, 1920, 1080);
const { rgba16, bytesPerRow } = await uploadAndReadbackHdrFrame(page, float16Base64);
const pqRgb = float16ToPqRgb(rgba16, width, height, bytesPerRow);
```
> WARNING: Requires headed Chrome with `--enable-unsafe-webgpu` — WebGPU is unavailable in `chrome-headless-shell`. NOT used by the default HDR render pipeline.

## The `window.__hf` Protocol

Any page implementing this protocol can be captured (not limited to Hyperframes compositions):
```typescript
interface HfProtocol {
  duration: number;                  // Total duration in seconds
  seek(time: number): void;          // Seek to a specific time
  media?: HfMediaElement[];          // Optional media element declarations
}

interface HfMediaElement {
  elementId: string;
  src: string;
  startTime: number;
  endTime: number;
  mediaOffset?: number;
  volume?: number;
  hasAudio?: boolean;
}
```

## Key Concepts

**BeginFrame Rendering**: Chrome's `HeadlessExperimental.beginFrame` explicitly advances the compositor, producing each frame on demand → no dropped frames, no timing dependency, pixel-perfect output.

**Seek Contract**: relies on runtime's `renderSeek(time)`, which (1) pauses all GSAP timelines, (2) seeks every timeline to the exact timestamp, (3) updates all media elements, (4) mounts/unmounts clips by `data-start`/`data-duration`.

**Chrome Requirements**: requires `chrome-headless-shell` (included), pinned Chrome version. For fully deterministic output (incl. fonts), use Docker mode via the producer.
