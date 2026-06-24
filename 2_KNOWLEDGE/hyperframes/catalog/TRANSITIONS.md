# HyperFrames Transitions Catalog

> **Cinematic scene transitions for SEOSONA Video.**
>
> **Source of truth (local, vendored):** `5_FRAMEWORK/hf_engine/registry/blocks/`
> **Install pattern:** `npx hyperframes add <name>`
>
> Two families live here:
> 1. **Single-effect shader transitions** (14) — one named effect each, `1920x1080`, `4s`, tagged `transition,shader`. These are the building blocks SEOSONA picks per scene cut.
> 2. **Transition showcase reels** (13, `transitions-*`) — multi-variant demo compositions grouped by family. Use to browse/choose a look, or as a source of many variants in one block.
>
> Component-level transitions (`grid-pixelate-wipe`, `parallax-zoom`, `parallax-unzoom`) live in the components registry — listed at the bottom.

## How to use (shader-transitions init API)

The shader transition blocks are driven by the **shader-transitions init API** (documented separately in the HyperFrames engine docs — not repeated here). At a high level:

- Each shader block exposes two slots ("from" scene / "to" scene) and renders a GPU fragment-shader transition between them over the block's `duration` (4s default for single-effect blocks).
- SEOSONA's pipeline selects a transition by `name`, installs it with `npx hyperframes add <name>`, then feeds the outgoing and incoming scene frames into the block's init call. The effect (whip-pan, zoom, glitch, etc.) is fixed per block; timing/easing is controlled by the init API.
- For a menu of *many* effects at once, use a `transitions-*` showcase reel instead of a single-effect block.

> This file is a **catalog** — install + description only. For the exact init signature and parameters, see the shader-transitions API doc in the engine.

---

## Single-effect shader transitions (14)

All `1920x1080`, `4s`, `transition,shader`.

| Name | Install | Effect / description |
|---|---|---|
| whip-pan | `npx hyperframes add whip-pan` | Fast camera whip pan — energetic hard cut between scenes. |
| cinematic-zoom | `npx hyperframes add cinematic-zoom` | Dramatic zoom blur — punch-in dolly feel. |
| cross-warp-morph | `npx hyperframes add cross-warp-morph` | Cross-warped morphing between the two scenes. |
| light-leak | `npx hyperframes add light-leak` | Cinematic light leak overlay crossfade — warm analog wash. |
| glitch | `npx hyperframes add glitch` | Digital glitch artifacts — datamosh / signal-break cut. |
| ripple-waves | `npx hyperframes add ripple-waves` | Concentric ripple wave distortion — water/impact ripple. |
| swirl-vortex | `npx hyperframes add swirl-vortex` | Swirling vortex distortion — spin-out into next scene. |
| thermal-distortion | `npx hyperframes add thermal-distortion` | Heat-haze thermal distortion — shimmering mirage wipe. |
| sdf-iris | `npx hyperframes add sdf-iris` | Signed-distance-field iris reveal — clean geometric iris in/out. |
| gravitational-lens | `npx hyperframes add gravitational-lens` | Gravitational lensing distortion — space-warp bend. |
| ridged-burn | `npx hyperframes add ridged-burn` | Ridged turbulence burn — film-burn / dissolve edge. |
| domain-warp-dissolve | `npx hyperframes add domain-warp-dissolve` | Fractal-noise domain-warp dissolve — organic melt. |
| flash-through-white | `npx hyperframes add flash-through-white` | White flash crossfade — classic bright punch cut. |
| chromatic-radial-split | `npx hyperframes add chromatic-radial-split` | Chromatic aberration radial split — RGB-fringed burst. |

## Transition showcase reels — `transitions-*` (13)

`transition,showcase`. Multi-effect demo compositions; durations vary.

| Name | Install | Family / description | Dur |
|---|---|---|---|
| transitions-3d | `npx hyperframes add transitions-3d` | 3D perspective flip and rotate transitions. | 11s |
| transitions-blur | `npx hyperframes add transitions-blur` | Blur-based transitions between scenes. | 20s |
| transitions-cover | `npx hyperframes add transitions-cover` | Cover/uncover slide transitions. | 21s |
| transitions-destruction | `npx hyperframes add transitions-destruction` | Destructive break-apart transitions. | 14s |
| transitions-dissolve | `npx hyperframes add transitions-dissolve` | Dissolve and fade transitions. | 24s |
| transitions-distortion | `npx hyperframes add transitions-distortion` | Warp and distortion transitions. | 21s |
| transitions-grid | `npx hyperframes add transitions-grid` | Grid-based tile transitions. | 11s |
| transitions-light | `npx hyperframes add transitions-light` | Light-based glow and flash transitions. | 21s |
| transitions-mechanical | `npx hyperframes add transitions-mechanical` | Mechanical shutter and iris transitions. | 15s |
| transitions-other | `npx hyperframes add transitions-other` | Miscellaneous creative transitions. | 20s |
| transitions-push | `npx hyperframes add transitions-push` | Push and slide transitions. | 24s |
| transitions-radial | `npx hyperframes add transitions-radial` | Radial wipe and reveal transitions. | 20s |
| transitions-scale | `npx hyperframes add transitions-scale` | Scale and zoom transitions. | 15s |

## Component-level transitions (3)

From `5_FRAMEWORK/hf_engine/registry/components/`. Layer over a host composition rather than rendering two full scenes.

| Name | Install | Description |
|---|---|---|
| grid-pixelate-wipe | `npx hyperframes add grid-pixelate-wipe` | Screen dissolves into a grid of squares fading out with staggered timing — drop-in between scenes. |
| parallax-zoom | `npx hyperframes add parallax-zoom` | Center card scales up to fill the frame while siblings parallax outward — eBay Playbook hero transition. |
| parallax-unzoom | `npx hyperframes add parallax-unzoom` | Focus card scales down from full frame as siblings parallax in to form a grid (reverse of parallax-zoom). |

---

### Quick-pick guide for SEOSONA

| Want… | Reach for |
|---|---|
| Energetic hard cut | `whip-pan`, `flash-through-white` |
| Punch-in / emphasis | `cinematic-zoom`, `parallax-zoom` |
| Glitchy / tech | `glitch`, `chromatic-radial-split` |
| Organic / dreamy | `domain-warp-dissolve`, `ripple-waves`, `light-leak` |
| Sci-fi / space | `gravitational-lens`, `swirl-vortex` |
| Clean geometric | `sdf-iris`, `grid-pixelate-wipe` |
| Film/analog | `ridged-burn`, `light-leak` |
| Browse many at once | any `transitions-*` reel |
