# HyperFrames Captions Catalog

> **Word-timed caption components for SEOSONA Video.**
>
> **Source of truth (local, vendored):** `5_FRAMEWORK/hf_engine/registry/components/`
> **Install pattern:** `npx hyperframes add <name>`
>
> Caption components are reusable styling layers — they carry **no** `dimensions` or `duration` in metadata; they adapt to the host composition and are driven per-word by SEOSONA's caption timing (word-timed / karaoke-style reveals). Each is tagged `captions,caption-style,*`.
>
> 16 caption components in total.

## All caption components (16)

| Name | Install | Description | Best for |
|---|---|---|---|
| caption-pill-karaoke | `npx hyperframes add caption-pill-karaoke` | Pill-shaped container with per-word karaoke color highlight. | Word-timed karaoke captions (core SEOSONA style). |
| caption-highlight | `npx hyperframes add caption-highlight` | Red background sweep behind each active word, TikTok-style. | TikTok / Shorts active-word highlight. |
| caption-kinetic-slam | `npx hyperframes add caption-kinetic-slam` | Full-screen single-word display with alternating entrance directions. | High-energy one-word-at-a-time hooks. |
| caption-clip-wipe | `npx hyperframes add caption-clip-wipe` | Left-to-right clip-path wipe reveal per word. | Clean progressive word reveal. |
| caption-gradient-fill | `npx hyperframes add caption-gradient-fill` | Gradient-clipped text with elastic bounce entrance. | Colorful, playful captions. |
| caption-neon-glow | `npx hyperframes add caption-neon-glow` | Cyan and magenta neon glow with keyword accent colors. | Gaming / night / neon aesthetic. |
| caption-neon-accent | `npx hyperframes add caption-neon-accent` | Multi-color neon glow accents with wiggle drift animation. | Lively neon with motion. |
| caption-emoji-pop | `npx hyperframes add caption-emoji-pop` | Emoji integration with stroked text and horizontal squeeze entrance. | Social captions that pop emojis on keywords. |
| caption-particle-burst | `npx hyperframes add caption-particle-burst` | Keyword words trigger colored particle explosions. | Emphasis bursts on hook words. |
| caption-glitch-rgb | `npx hyperframes add caption-glitch-rgb` | RGB chromatic aberration with CRT scanline overlay. | Cyber / tech / glitchy captions. |
| caption-matrix-decode | `npx hyperframes add caption-matrix-decode` | Character scramble animation before text reveal. | "Decode" reveal, hacker/tech vibe. |
| caption-editorial-emphasis | `npx hyperframes add caption-editorial-emphasis` | Dual-font system with dramatic size contrast for emphasis words. | Editorial / documentary captions. |
| caption-weight-shift | `npx hyperframes add caption-weight-shift` | Elegant font-weight transition between caption lines. | Minimal, typographic captions. |
| caption-parallax-layers | `npx hyperframes add caption-parallax-layers` | Behind-subject 3D text layering with vertical stretch effect. | Depth / behind-the-subject captions. |
| caption-texture | `npx hyperframes add caption-texture` | Flowing texture mask over large uppercase text — ships 6 textures (lava, marble, metal, wood, concrete, rock), configurable via the `texture` variable. | Big textured display captions. |
| caption-blend-difference | `npx hyperframes add caption-blend-difference` | Auto-inverting text via `mix-blend-mode: difference` — flips white/black per-pixel against the background. | Captions that stay legible over any background. |

## SEOSONA usage notes

- **Word timing:** all `caption-*` components are designed to be fed word-by-word timing data; the active-word treatment (highlight, color, slam, wipe) is what differs between styles.
- **No fixed size/duration:** because these are components (not blocks), they have no `dimensions`/`duration` in `registry-item.json` — they inherit the host composition's canvas and run for as long as the caption track does.
- **Configurable variants:** `caption-texture` exposes a `texture` variable (lava / marble / metal / wood / concrete / rock). Others expose keyword-accent hooks (`caption-neon-glow`, `caption-particle-burst`, `caption-neon-accent`).
- **Background-safe pick:** `caption-blend-difference` auto-inverts, the safest default when the underlying footage brightness varies.

### Quick-pick guide

| Want… | Reach for |
|---|---|
| Default karaoke word-timed | `caption-pill-karaoke` |
| TikTok/Shorts highlight | `caption-highlight` |
| One huge word at a time | `caption-kinetic-slam` |
| Neon / gaming | `caption-neon-glow`, `caption-neon-accent` |
| Tech / glitch | `caption-glitch-rgb`, `caption-matrix-decode` |
| Emoji-forward social | `caption-emoji-pop` |
| Editorial / minimal | `caption-editorial-emphasis`, `caption-weight-shift` |
| Big textured display | `caption-texture` |
| Legible over any footage | `caption-blend-difference` |
