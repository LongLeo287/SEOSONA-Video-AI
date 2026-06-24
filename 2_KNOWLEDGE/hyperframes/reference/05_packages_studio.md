# HyperFrames Package — @hyperframes/studio

Source: https://hyperframes.heygen.com/packages/studio.md (fetched 2026-06-24)

> Visual composition editor with live preview, timeline view, and hot reload.

Browser-based React visual editor for creating and previewing compositions: real-time preview, visual timeline, player controls — all updating live as you edit HTML.

```bash
npm install @hyperframes/studio
```

> TIP: For most development workflows you do not need to install studio directly. `npx hyperframes preview` starts it automatically with hot reload. Install only if embedding the editor in your own app.

## Running the Studio
```bash
npx hyperframes preview        # recommended

# From the monorepo
bun run dev
bun run --filter @hyperframes/studio dev
```

## Package Exports
| Import | Description |
| --- | --- |
| `@hyperframes/studio` | React components, hooks, and types |
| `@hyperframes/studio/tailwind-preset` | Tailwind CSS preset for studio styling |

Peer dependencies: `react` (18 or 19), `react-dom` (18 or 19), `zustand` (4 or 5).

## Components

### Layout
```typescript
import { NLELayout, NLEPreview, CompositionBreadcrumb } from '@hyperframes/studio';
import type { CompositionLevel } from '@hyperframes/studio';

<NLELayout>{/* Preview, timeline, editor panels */}</NLELayout>
<NLEPreview />
<CompositionBreadcrumb levels={levels} />
```

### Player & Timeline
```typescript
import {
  Player, PlayerControls, Timeline, PreviewPanel, AgentActivityTrack,
} from '@hyperframes/studio';
import type { AgentActivity, TimelineElement, ActiveEdits } from '@hyperframes/studio';

<Player />
<PlayerControls />        // play, pause, seek, frame-step
<Timeline />             // timeline editor with scrubber
<PreviewPanel />
<AgentActivityTrack activities={activities} />   // for agent workflows
```

### Editor Components
```typescript
import { SourceEditor, PropertyPanel, FileTree } from '@hyperframes/studio';

<SourceEditor />    // CodeMirror-based, HTML/CSS/JS
<PropertyPanel />   // property inspector for selected elements
<FileTree />        // project file browser
```

### Full Application
```typescript
import { StudioApp } from '@hyperframes/studio';
<StudioApp />   // complete studio (wraps all components)
```

## Hooks

### `useTimelinePlayer`
```typescript
import { useTimelinePlayer } from '@hyperframes/studio';
const player = useTimelinePlayer();
// player.play(), player.pause(), player.seek(time), player.stepForward(), player.stepBackward()
```

### `usePlayerStore`
```typescript
import { usePlayerStore, liveTime, formatTime } from '@hyperframes/studio';
const store = usePlayerStore();   // current time, duration, playing state
const display = formatTime(liveTime.current);
```

### `useCodeEditor`
```typescript
import { useCodeEditor } from '@hyperframes/studio';
const editor = useCodeEditor();
// editor.code, editor.setCode(), editor.diff, editor.onChange()
```

### `useElementPicker`
```typescript
import { useElementPicker } from '@hyperframes/studio';
const picker = useElementPicker();
// picker.selectedElement, picker.selectElement(id), picker.clearSelection()
```

## Features

### Live Preview
Renders the composition in an iframe using the Hyperframes runtime — same runtime code, seek logic, and clip lifecycle as render. Hot reload picks up HTML changes within milliseconds.

> NOTE: Visual output of preview matches render exactly. Real-time playback smoothness depends on hardware (preview plays at 30/60fps). Render captures each frame individually via seek-driven pipeline → expensive frames make render slower but never drop. Stutter in preview with a clean rendered mp4 is expected.

### Timeline View
* Each clip = colored bar on its track
* Bar position/width reflect `data-start` and `data-duration`
* Higher rows render in front; lower rows underneath
* Relative timing references (`data-start="intro"`) resolved and displayed as absolute positions

### Timeline Editing
Supports move and trim actions that persist directly back into HTML source (maps to `data-start`, `data-duration`, `data-track-index`, `z-index`).

### Player Controls
Play/Pause, Seek (click timeline to jump), Scrub (drag playhead frame by frame), Frame step (advance/rewind one frame).

### Hot Reload
File changes applied without restarting the server. Preview maintains current playback position when possible.

## Architecture
1. **Iframe preview** — composition HTML loaded in isolated iframe with Hyperframes runtime injected (same path as production).
2. **Runtime bridge** — communicates with iframe via `postMessage` (play, pause, seek; receives current time, duration, readiness).
3. **Timeline component** — parses composition via `@hyperframes/core` to extract clip timing data.
4. **File watcher** — Vite-based dev server watches project files, triggers HMR.

## Tailwind CSS Preset
```typescript
// tailwind.config.ts
import studioPreset from '@hyperframes/studio/tailwind-preset';

export default {
  presets: [studioPreset],
  // ... your config
};
```
