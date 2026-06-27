# HyperFrames Craft — design-direction reference (SEOSONA-adapted)

This folder is the **design-craft** half of the HyperFrames knowledge base: how to
make a frame *look produced* — motion choreography, marker highlighting, captions,
transitions, data-in-motion. It complements `../reference/` (engine API) and
`../guides/` (pipeline). Read this when you want a component to feel richer, not
when you want to know how the renderer works.

## Source & license

Ingested 2026-06-27 from **nexu-io/open-design** (`design-templates/hyperframes/`),
Apache-2.0. Open Design is an open-source agentic design workspace built on the same
HyperFrames engine SEOSONA Video uses. These docs are engine-agnostic design craft,
kept close to original so upstream updates stay diffable.

## ⚠️ SEOSONA brand override (read first — it overrides the docs)

These docs were written for a **dark-mode, neon-accent, 16:9** house style. SEOSONA
Video is the **opposite** and that is **brand law** ([[brand-colors-light-only]]).
Wherever a doc says "dark canvas / neon / cyan-on-black / 16:9", translate:

| Doc says | SEOSONA uses |
|----------|--------------|
| Dark background (`#0a0a0a`, `#1a1410`, emerald canvas) | **Light only** — `#FFFFFF` / `#F8FAFC` surfaces |
| Single neon accent (`#00ff95`, `#ff5e3a`) | **Brand palette** — blue `#2A5BDA`, coral `#E2724D`, green `#16A34A` (rotated per scene via `_auto_shift`) |
| Pure `#000`/`#fff` text | Ink `#0F172A` on light; white only inside a brand-gradient hero |
| 16:9 (1920×1080) | **9:16 (1080×1920)** vertical; respect bottom ~160px safe zone |
| "Druk Wide / Anton" display fonts | **Be Vietnam Pro** (BVP-Black/XBold/Bold) — Vietnamese diacritics |
| "Inter" body | Be Vietnam Pro Medium/SemiBold |

Everything else — **motion principles, easing, scene structure (build/breathe/resolve),
stagger choreography, marker-highlight CSS, caption timing, transition catalog** — is
brand-neutral and applies as-is. Use it.

## What's here

| File | Use it for |
|------|-----------|
| `references/motion-principles.md` | **The single most useful doc.** Easing-as-emotion, vary speed/direction/ease, build/breathe/resolve, choreography = hierarchy. Every component reveal should obey this. |
| `references/css-patterns.md` | 5 marker-highlight modes (highlight sweep, circle, burst, scribble, sketchout) in pure CSS+GSAP — for emphasising words in karaoke / tip / quote. |
| `references/captions.md` | Caption chunking (2–3 words, ≤28 chars), word-level color-flip via `tl.set`, clip-path exit wipe — feeds our karaoke + talking-head engines. |
| `references/transitions/` | CSS transition catalog (push, dissolve, radial, blur, 3D, destruction…) — scene-to-scene variety beyond our default crossfade. |
| `references/typography.md` | Hierarchy + weight ladder rules (700–900 headline / 300–400 body, 60px+ headline). Map font names → Be Vietnam Pro. |
| `patterns.md` | Composition patterns: PiP video-in-frame, title card, slide-show tracks, top-level composition shape. |
| `data-in-motion.md` | Data/stats pitfalls: no pie charts, no 6-panel dashboards, numbers need visual weight (fill bar / ring / shape). Directly informs `chart` + `bignum` + `stats`. |
| `house-style.md` / `visual-styles.md` | Background-layer depth (radial glows, ghost text, hairline rules), AI design-tells to avoid. |
| `palettes/` | 9 reference palettes — **not used** (SEOSONA palette is fixed) but `clean-corporate.md` shows the light-mode logic our palette already follows. |

## How this enriches SEOSONA video (the point)

Our engine (`4_BRAIN/native_composer.py`) renders 14 brand-locked components. Today
each reveals with a similar stagger. These docs let an LLM (or us) generate **richer,
varied freeform scenes that still obey the brand** — exactly the Open Design model of
"LLM writes HTML per request, DESIGN.md keeps it on-brand". The brand contract is
`7_ASSETS/brand/SEOSONA/DESIGN.md`; the motion vocabulary is here; the per-component
recipes are in `motion-recipes-seosona.md`.

Related: [[master-video-spec]] · [[brand-colors-light-only]] · [[render-engine-video-engine]]
