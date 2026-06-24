# HyperFrames Catalog Index

> **The menu the SEOSONA Video pipeline + agents pick from.**
>
> **Source of truth (local, vendored):**
> `5_FRAMEWORK/hf_engine/registry/blocks/` (97 blocks) and
> `5_FRAMEWORK/hf_engine/registry/components/` (25 components).
> Each item is a directory with a `registry-item.json` (metadata) and an HTML file (the actual block/component).
>
> **Install pattern:** `npx hyperframes add <name>`
> **Generated:** 2026-06-24 by direct extraction of all 122 `registry-item.json` files. 0 malformed.

## Totals

| Kind | Count |
|---|---|
| Blocks | 97 |
| Components | 25 |
| **Total** | **122** |

### Blocks by category

| Category | Count |
|---|---|
| Shader Transitions (single-effect) | 14 |
| Transition Showcases (`transitions-*`) | 13 |
| Code — VS Code / typing / animation | 21 |
| Code — Apple Terminal profiles | 12 |
| Maps & Geography | 9 |
| Liquid Glass | 7 |
| VFX | 7 |
| Social / UI Overlays | 9 |
| Data & Diagrams | 4 |
| Showcase / Branding / Misc | 5 |
| **Blocks total** | **97** |

### Components by category

| Category | Count |
|---|---|
| Captions (`caption-*`) | 16 |
| Text effects | 4 (`morph-text`, `shimmer-sweep`, `texture-mask-text`, `caption-blend-difference`*) |
| Overlays / Texture | 3 (`grain-overlay`, `vignette`, `caption-texture`*) |
| Transitions (component-level) | 3 (`grid-pixelate-wipe`, `parallax-zoom`, `parallax-unzoom`) |
| Physics / Motion | 1 (`motion-blur`) |
| **Components total** | **25** |

\* counted under Captions in the per-row tables below.

---

## Shader Transitions — single-effect (14)

All `1920x1080`, `4s`, tagged `transition,shader`. See **TRANSITIONS.md** for usage.

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| chromatic-radial-split | `npx hyperframes add chromatic-radial-split` | Shader transition with chromatic aberration radial split | 1920x1080 | 4s |
| cinematic-zoom | `npx hyperframes add cinematic-zoom` | Shader transition with dramatic zoom blur | 1920x1080 | 4s |
| cross-warp-morph | `npx hyperframes add cross-warp-morph` | Shader transition with cross-warped morphing | 1920x1080 | 4s |
| domain-warp-dissolve | `npx hyperframes add domain-warp-dissolve` | Shader transition with fractal noise domain warping | 1920x1080 | 4s |
| flash-through-white | `npx hyperframes add flash-through-white` | Shader transition with white flash crossfade | 1920x1080 | 4s |
| glitch | `npx hyperframes add glitch` | Shader transition with digital glitch artifacts | 1920x1080 | 4s |
| gravitational-lens | `npx hyperframes add gravitational-lens` | Shader transition with gravitational lensing distortion | 1920x1080 | 4s |
| light-leak | `npx hyperframes add light-leak` | Shader transition with cinematic light leak overlay | 1920x1080 | 4s |
| ridged-burn | `npx hyperframes add ridged-burn` | Shader transition with ridged turbulence burn effect | 1920x1080 | 4s |
| ripple-waves | `npx hyperframes add ripple-waves` | Shader transition with concentric ripple wave distortion | 1920x1080 | 4s |
| sdf-iris | `npx hyperframes add sdf-iris` | Shader transition with signed distance field iris reveal | 1920x1080 | 4s |
| swirl-vortex | `npx hyperframes add swirl-vortex` | Shader transition with swirling vortex distortion | 1920x1080 | 4s |
| thermal-distortion | `npx hyperframes add thermal-distortion` | Shader transition with heat haze thermal distortion | 1920x1080 | 4s |
| whip-pan | `npx hyperframes add whip-pan` | Shader transition simulating a fast camera whip pan | 1920x1080 | 4s |

## Transition Showcases — `transitions-*` (13)

Multi-effect demo reels (`transition,showcase`). Durations vary; useful as a library of variants.

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| transitions-3d | `npx hyperframes add transitions-3d` | Showcase of 3D perspective flip and rotate transitions | 1920x1080 | 11s |
| transitions-blur | `npx hyperframes add transitions-blur` | Showcase of blur-based transitions between scenes | 1920x1080 | 20s |
| transitions-cover | `npx hyperframes add transitions-cover` | Showcase of cover/uncover slide transitions | 1920x1080 | 21s |
| transitions-destruction | `npx hyperframes add transitions-destruction` | Showcase of destructive break-apart transitions | 1920x1080 | 14s |
| transitions-dissolve | `npx hyperframes add transitions-dissolve` | Showcase of dissolve and fade transitions | 1920x1080 | 24s |
| transitions-distortion | `npx hyperframes add transitions-distortion` | Showcase of warp and distortion transitions | 1920x1080 | 21s |
| transitions-grid | `npx hyperframes add transitions-grid` | Showcase of grid-based tile transitions | 1920x1080 | 11s |
| transitions-light | `npx hyperframes add transitions-light` | Showcase of light-based glow and flash transitions | 1920x1080 | 21s |
| transitions-mechanical | `npx hyperframes add transitions-mechanical` | Showcase of mechanical shutter and iris transitions | 1920x1080 | 15s |
| transitions-other | `npx hyperframes add transitions-other` | Showcase of miscellaneous creative transitions | 1920x1080 | 20s |
| transitions-push | `npx hyperframes add transitions-push` | Showcase of push and slide transitions | 1920x1080 | 24s |
| transitions-radial | `npx hyperframes add transitions-radial` | Showcase of radial wipe and reveal transitions | 1920x1080 | 20s |
| transitions-scale | `npx hyperframes add transitions-scale` | Showcase of scale and zoom transitions | 1920x1080 | 15s |

## Code — VS Code, typing & animation (21)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| code-3d-extrude | `npx hyperframes add code-3d-extrude` | Syntax-highlighted code on a lit, beveled 3D slab that rotates through real space and settles to a readable rest — true WebGL depth and lighting, not a 2D transform. | 1920x1080 | 8s |
| code-diff | `npx hyperframes add code-diff` | An edit shown as a colored diff — removed lines collapse in red, added lines expand in green. | 1920x1080 | 6s |
| code-highlight | `npx hyperframes add code-highlight` | A highlight band sweeps across a target line while the surrounding context dims — draws the eye to one line. | 1920x1080 | 5s |
| code-morph | `npx hyperframes add code-morph` | One snippet transforms into another — tokens glide between positions, leavers fade out, enterers fade in. Shiki Magic Move re-driven as a paused GSAP timeline. | 1920x1080 | 7s |
| code-particle-assemble | `npx hyperframes add code-particle-assemble` | Thousands of GPU points scatter through space and fly to the exact glyph pixels of the code, resolving into readable syntax-highlighted text — a particle system, not a token tween. | 1920x1080 | 8s |
| code-scroll | `npx hyperframes add code-scroll` | The camera scrolls a long file to bring a target line to center and spotlights it — for walking through real modules. | 1920x1080 | 6s |
| code-shader-dissolve | `npx hyperframes add code-shader-dissolve` | The code compiles into existence: a GPU fragment shader resolves it out of seeded noise with a chromatic dissolve front and edge glow, then holds crisp. | 1920x1080 | 7s |
| code-typing | `npx hyperframes add code-typing` | Token-streamed typing reveal with a caret that tracks the frontier — deterministic, no CSS animation. | 1920x1080 | 5s |
| code-snippet-flight | `npx hyperframes add code-snippet-flight` | Discrete code snippets fly in from the side and assemble into a stacked program, staggered. Block-level FLIP. | 1920x1080 | 6s |
| code-snippet-dark-2026 | `npx hyperframes add code-snippet-dark-2026` | VS Code workbench typing animation, Dark 2026 theme. Full editor chrome (activity bar, sidebar, tabs, terminal, status bar). | 1920x1080 | 11s |
| code-snippet-dark-modern | `npx hyperframes add code-snippet-dark-modern` | VS Code workbench typing animation, Dark Modern theme. | 1920x1080 | 11s |
| code-snippet-dark-plus | `npx hyperframes add code-snippet-dark-plus` | VS Code workbench typing animation, Dark+ theme. | 1920x1080 | 11s |
| code-snippet-light-2026 | `npx hyperframes add code-snippet-light-2026` | VS Code workbench typing animation, Light 2026 theme. | 1920x1080 | 11s |
| code-snippet-light-modern | `npx hyperframes add code-snippet-light-modern` | VS Code workbench typing animation, Light Modern theme. | 1920x1080 | 11s |
| code-snippet-light-plus | `npx hyperframes add code-snippet-light-plus` | VS Code workbench typing animation, Light+ theme. | 1920x1080 | 11s |
| code-snippet-high-contrast | `npx hyperframes add code-snippet-high-contrast` | VS Code workbench typing animation, High Contrast theme. | 1920x1080 | 11s |
| code-snippet-high-contrast-light | `npx hyperframes add code-snippet-high-contrast-light` | VS Code workbench typing animation, High Contrast Light theme. | 1920x1080 | 11s |
| code-snippet-monokai | `npx hyperframes add code-snippet-monokai` | VS Code workbench typing animation, Monokai theme. | 1920x1080 | 11s |
| code-snippet-solarized-light | `npx hyperframes add code-snippet-solarized-light` | VS Code workbench typing animation, Solarized Light theme. | 1920x1080 | 11s |
| code-snippet-visual-studio-dark | `npx hyperframes add code-snippet-visual-studio-dark` | VS Code workbench typing animation, Visual Studio Dark theme. | 1920x1080 | 11s |
| code-snippet-visual-studio-light | `npx hyperframes add code-snippet-visual-studio-light` | VS Code workbench typing animation, Visual Studio Light theme. | 1920x1080 | 11s |

## Code — Apple Terminal profiles (12)

All `1920x1080`, `12s`. Per-character typing animation of a shell session, themed by Apple Terminal profile.

| Name | Install | Profile look | Dims | Dur |
|---|---|---|---|---|
| code-snippet-apple-terminal-basic | `npx hyperframes add code-snippet-apple-terminal-basic` | White bg, black text | 1920x1080 | 12s |
| code-snippet-apple-terminal-clear-dark | `npx hyperframes add code-snippet-apple-terminal-clear-dark` | Semi-transparent dark bg | 1920x1080 | 12s |
| code-snippet-apple-terminal-clear-light | `npx hyperframes add code-snippet-apple-terminal-clear-light` | Semi-transparent light bg | 1920x1080 | 12s |
| code-snippet-apple-terminal-grass | `npx hyperframes add code-snippet-apple-terminal-grass` | Black bg, green text | 1920x1080 | 12s |
| code-snippet-apple-terminal-homebrew | `npx hyperframes add code-snippet-apple-terminal-homebrew` | Black bg, bright green text, lime cursor | 1920x1080 | 12s |
| code-snippet-apple-terminal-man-page | `npx hyperframes add code-snippet-apple-terminal-man-page` | Pale yellow bg, black text | 1920x1080 | 12s |
| code-snippet-apple-terminal-novel | `npx hyperframes add code-snippet-apple-terminal-novel` | Warm parchment bg, dark brown text | 1920x1080 | 12s |
| code-snippet-apple-terminal-ocean | `npx hyperframes add code-snippet-apple-terminal-ocean` | Deep blue bg, white text | 1920x1080 | 12s |
| code-snippet-apple-terminal-pro | `npx hyperframes add code-snippet-apple-terminal-pro` | Black bg, grey text, lime green cursor | 1920x1080 | 12s |
| code-snippet-apple-terminal-red-sands | `npx hyperframes add code-snippet-apple-terminal-red-sands` | Deep red bg, sandy text | 1920x1080 | 12s |
| code-snippet-apple-terminal-silver-aerogel | `npx hyperframes add code-snippet-apple-terminal-silver-aerogel` | Dark grey bg, white text | 1920x1080 | 12s |
| code-snippet-apple-terminal-solid-colors | `npx hyperframes add code-snippet-apple-terminal-solid-colors` | Deep purple bg, white text | 1920x1080 | 12s |

## Maps & Geography (9)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| us-map | `npx hyperframes add us-map` | Animated US choropleth with staggered state reveals, value labels, gradient legend — inline SVG + GSAP. | 1920x1080 | 12s |
| us-map-bubble | `npx hyperframes add us-map-bubble` | US bubble map: proportional city markers, value callouts, connection lines — composable with us-map. | 1920x1080 | 12s |
| us-map-flow | `npx hyperframes add us-map-flow` | US flow map: connection arcs between cities over a base map — origin-destination viz. | 1920x1080 | 12s |
| us-map-hex | `npx hyperframes add us-map-hex` | US hex grid map: each state an equal-weight hex with data fill and abbreviation label. | 1920x1080 | 10s |
| world-map | `npx hyperframes add world-map` | World choropleth, country-by-country reveal, tooltip labels, rotating globe inset — D3 Natural Earth. | 1920x1080 | 14s |
| spain-map | `npx hyperframes add spain-map` | Spain choropleth by autonomous community, staggered reveals, gradient legend — D3 conic conformal. | 1920x1080 | 12s |
| nyc-paris-flight | `npx hyperframes add nyc-paris-flight` | Apple-style map: plane flying NYC→Paris, marker circle, landing pop, SFX. | 1920x1080 | 6s |
| north-korea-locked-down | `npx hyperframes add north-korea-locked-down` | Map zoom into North Korea with red scribble circle, locked-down label, reddish editorial wash. | 1920x1080 | 7s |
| spotify-card † | see Social/UI | — | — | — |

† `spotify-card` is a social overlay, listed under Social/UI; placed here only as a cross-reference note. (Maps = 8 true map blocks; `north-korea-locked-down` and `nyc-paris-flight` are map-driven showcases.)

## Liquid Glass (7)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| ios26-liquid-glass | `npx hyperframes add ios26-liquid-glass` | 3D iPhone, iOS 26 home screen, liquid glass icons, shader wallpaper, dock, fluid glass notifications onto a GLTF device. (webgpu) | 1920x1080 | 15s |
| macos-tahoe-liquid-glass | `npx hyperframes add macos-tahoe-liquid-glass` | 3D MacBook, macOS Tahoe desktop, glass menu bar, Finder window, dock, cinematic camera move. (GLTF) | 1920x1080 | 15s |
| liquid-glass-context-menu | `npx hyperframes add liquid-glass-context-menu` | Frosted glass context menu panel drifting over an aurora shader background. (webgpu) | 1920x1080 | 8s |
| liquid-glass-media-controls | `npx hyperframes add liquid-glass-media-controls` | Frosted glass media control panels over an aurora shader background. (webgpu) | 1920x1080 | 8s |
| liquid-glass-notification | `npx hyperframes add liquid-glass-notification` | Frosted glass notification cards over an aurora shader background. (webgpu) | 1920x1080 | 8s |
| liquid-glass-widgets | `npx hyperframes add liquid-glass-widgets` | Frosted glass stat cards, showcase panel, pill chips over an aurora shader background. (webgpu) | 1920x1080 | 8s |
| vfx-liquid-glass | `npx hyperframes add vfx-liquid-glass` | VFX liquid glass composition block. (html-in-canvas, webgl) | 1920x1080 | 20s |

## VFX (7)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| vfx-iphone-device | `npx hyperframes add vfx-iphone-device` | Real GLTF iPhone 15 Pro Max + MacBook Pro models, live HTML-in-Canvas screens, morphing glass lens, product-review camera, 360° turntable. | 1920x1080 | 15s |
| vfx-liquid-background | `npx hyperframes add vfx-liquid-background` | Organic liquid sim with vertex displacement; HTML content floats above a rippling fluid surface. | 1920x1080 | 12s |
| vfx-magnetic | `npx hyperframes add vfx-magnetic` | Magnetic VFX composition block. (html-in-canvas, webgl) | 1920x1080 | 15s |
| vfx-portal | `npx hyperframes add vfx-portal` | Portal VFX composition block. (html-in-canvas, webgl) | 1920x1080 | 10s |
| vfx-shatter | `npx hyperframes add vfx-shatter` | Shatter VFX composition block. (html-in-canvas, webgl) | 1920x1080 | 12s |
| vfx-text-cursor | `npx hyperframes add vfx-text-cursor` | Dramatic text reveal with cursor glow, chromatic shadow rays, directional lighting on black; canvas shader post-processing. | 1920x1080 | 8s |
| vfx-liquid-glass | *(also in Liquid Glass)* | VFX composition block. | 1920x1080 | 20s |

## Social / UI Overlays (9)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| instagram-follow | `npx hyperframes add instagram-follow` | Instagram follow overlay with profile card and follow button. | 1080x1920 | 4.5s |
| tiktok-follow | `npx hyperframes add tiktok-follow` | TikTok follow overlay with profile card and follow button. | 1080x1920 | 4.5s |
| yt-lower-third | `npx hyperframes add yt-lower-third` | YouTube subscribe lower third with avatar and channel info. | 1920x1080 | 4.5s |
| x-post | `npx hyperframes add x-post` | X/Twitter post card overlay with engagement metrics. | 1920x1080 | 5s |
| reddit-post | `npx hyperframes add reddit-post` | Reddit post card overlay with upvotes and comments. | 1920x1080 | 5s |
| spotify-card | `npx hyperframes add spotify-card` | Spotify now-playing card with album art and progress bar. | 1080x1920 | 5s |
| macos-notification | `npx hyperframes add macos-notification` | macOS-style notification banner with app icon and message. | 1920x1080 | 5s |
| ui-3d-reveal | `npx hyperframes add ui-3d-reveal` | Perspective 3D reveal animation for UI elements. | 1920x1080 | 13s |
| logo-outro | `npx hyperframes add logo-outro` | Cinematic logo reveal: piece-by-piece assembly, glow bloom, tagline fade-in, URL pill. | 1920x1080 | 6s |

## Data & Diagrams (4)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| data-chart | `npx hyperframes add data-chart` | Animated bar + line chart, staggered reveal, NYT-style typography, value labels. | 1920x1080 | 15s |
| flowchart | `npx hyperframes add flowchart` | Animated decision tree: SVG connectors, sticky-note nodes, cursor interaction, typing correction. | 1920x1080 | 12s |
| flowchart-vertical | `npx hyperframes add flowchart-vertical` | Portrait decision tree (same as flowchart, vertical layout). | 1440x2560 | 12s |
| app-showcase | `npx hyperframes add app-showcase` | Fitness app product showcase with three floating smartphone screens (3D). | 1920x1080 | 5.5s |

## Showcase / Branding / Misc (5)

| Name | Install | Description | Dims | Dur |
|---|---|---|---|---|
| apple-money-count | `npx hyperframes add apple-money-count` | Apple-style finance counter $0→$10,000, green flash, money-icon burst with SFX. | 1920x1080 | 5s |
| blue-sweater-intro-video | `npx hyperframes add blue-sweater-intro-video` | Warm AI creator intro resolving into an X follow card. (SFX) | 1920x1080 | 12s |
| vpn-youtube-spot | `npx hyperframes add vpn-youtube-spot` | Snappy Apple-style YouTube insert: phone finds/installs a VPN app, with SFX. | 1920x1080 | 7s |
| app-showcase | *(also in Data & Diagrams)* | — | 1920x1080 | 5.5s |
| logo-outro | *(also in Social/UI)* | — | 1920x1080 | 6s |

---

## Components (25)

> Components are reusable styling/effect layers (no `dimensions`/`duration` in metadata — they adapt to the host composition). Install identically: `npx hyperframes add <name>`.

### Captions — `caption-*` (16)

See **CAPTIONS.md** for SEOSONA word-timed caption usage.

| Name | Install | Description |
|---|---|---|
| caption-blend-difference | `npx hyperframes add caption-blend-difference` | Auto-inverting text via `mix-blend-mode: difference` — flips white/black per-pixel against the background. |
| caption-clip-wipe | `npx hyperframes add caption-clip-wipe` | Left-to-right clip-path wipe reveal per word. |
| caption-editorial-emphasis | `npx hyperframes add caption-editorial-emphasis` | Dual-font system with dramatic size contrast for emphasis words. |
| caption-emoji-pop | `npx hyperframes add caption-emoji-pop` | Emoji integration with stroked text and horizontal squeeze entrance. |
| caption-glitch-rgb | `npx hyperframes add caption-glitch-rgb` | RGB chromatic aberration with CRT scanline overlay. |
| caption-gradient-fill | `npx hyperframes add caption-gradient-fill` | Gradient-clipped text with elastic bounce entrance. |
| caption-highlight | `npx hyperframes add caption-highlight` | Red background sweep behind each active word, TikTok-style. |
| caption-kinetic-slam | `npx hyperframes add caption-kinetic-slam` | Full-screen single-word display with alternating entrance directions. |
| caption-matrix-decode | `npx hyperframes add caption-matrix-decode` | Character scramble animation before text reveal. |
| caption-neon-accent | `npx hyperframes add caption-neon-accent` | Multi-color neon glow accents with wiggle drift animation. |
| caption-neon-glow | `npx hyperframes add caption-neon-glow` | Cyan and magenta neon glow with keyword accent colors. |
| caption-parallax-layers | `npx hyperframes add caption-parallax-layers` | Behind-subject 3D text layering with vertical stretch effect. |
| caption-particle-burst | `npx hyperframes add caption-particle-burst` | Keyword words trigger colored particle explosions. |
| caption-pill-karaoke | `npx hyperframes add caption-pill-karaoke` | Pill-shaped container with per-word karaoke color highlight. |
| caption-texture | `npx hyperframes add caption-texture` | Flowing texture mask over large uppercase text — ships 6 textures (lava, marble, metal, wood, concrete, rock), configurable via `texture` var. |
| caption-weight-shift | `npx hyperframes add caption-weight-shift` | Elegant font-weight transition between caption lines. |

### Text effects (3)

| Name | Install | Description |
|---|---|---|
| morph-text | `npx hyperframes add morph-text` | Gooey text morph — cycles an editable word list using SVG threshold + GSAP blur. |
| shimmer-sweep | `npx hyperframes add shimmer-sweep` | Animated light sweep across text/elements via CSS gradient mask — AI accents, premium reveals. |
| texture-mask-text | `npx hyperframes add texture-mask-text` | CSS luminance masks cut holes through letterforms — 66 pre-built texture masks from ambientCG PBR maps. |

### Overlays / Texture (2)

| Name | Install | Description |
|---|---|---|
| grain-overlay | `npx hyperframes add grain-overlay` | Animated film grain texture overlay (CSS keyframes) — warmth/analog character on any composition. |
| vignette | `npx hyperframes add vignette` | Cinematic radial vignette overlay (pure-CSS gradient) — darkens edges to pull focus to center. |

### Transitions — component-level (3)

| Name | Install | Description |
|---|---|---|
| grid-pixelate-wipe | `npx hyperframes add grid-pixelate-wipe` | Screen dissolves into a grid of squares fading out with staggered timing — use between scenes. |
| parallax-zoom | `npx hyperframes add parallax-zoom` | Center card scales up to fill the frame while siblings parallax outward — eBay Playbook hero transition. |
| parallax-unzoom | `npx hyperframes add parallax-unzoom` | Focus card scales down from full frame as siblings parallax in to form a grid (reverse of parallax-zoom). |

### Physics / Motion (1)

| Name | Install | Description |
|---|---|---|
| motion-blur | `npx hyperframes add motion-blur` | Velocity-driven motion blur — samples element position each frame, applies one-sided SVG `feGaussianBlur` ghost trail proportional to speed. |
