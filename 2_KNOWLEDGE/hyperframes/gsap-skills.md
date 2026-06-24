# GSAP Skills + free plugins (for HyperFrames authoring)

Source: [greensock/gsap-skills](https://github.com/greensock/gsap-skills) (MIT, official
GreenSock) — AI authoring skills for GSAP, the animation library HyperFrames renders.
Install the full set for an agent with: `npx skills add https://github.com/greensock/gsap-skills`.

## The 8 skills (when to consult which)
| Skill | Use for |
|-------|---------|
| `gsap-core` | `gsap.to/from/fromTo`, easing, duration, stagger, transforms, autoAlpha, matchMedia |
| `gsap-timeline` | sequencing, position params, labels, nesting, playback control |
| `gsap-scrolltrigger` | scroll-linked, pin, scrub, parallax (rare in video, but available) |
| `gsap-plugins` | **ScrollTo, Flip, Draggable, SplitText, MorphSVG, DrawSVG, MotionPath, ScrambleText, CustomEase** |
| `gsap-utils` | clamp, mapRange, normalize, interpolate, random, snap, toArray, wrap |
| `gsap-react` / `gsap-frameworks` | useGSAP, context, cleanup (not used — HyperFrames is plain HTML) |
| `gsap-performance` | 60fps, will-change, batching |

## 🔓 All GSAP plugins are now FREE (Webflow, 2025+)
No Club GSAP membership / auth token needed — the full plugin set ships in the public
`gsap` npm package. **SEOSONA wires three into every render** (gsap 3.13.0):

| Plugin | What it unlocks for video |
|--------|---------------------------|
| **SplitText** | split text into chars/words/lines → **per-word / karaoke caption reveals**, kinetic typography |
| **ScrollTrigger** | scrub/pin (mostly for web; available if a composition needs it) |
| **MorphSVGPlugin** | morph one SVG shape into another → logo/icon transitions |

### How it's wired (already done)
- Plugin files live in `5_FRAMEWORK/hf_core/vendor/gsap/` (with version-matched `gsap.min.js`).
- `4_BRAIN/pipeline_manager.py` `_write_hyperframes_render_project` copies them into every
  render project's `assets/` and the generated `index.html` loads them +
  `gsap.registerPlugin(SplitText, ScrollTrigger, MorphSVGPlugin)`.
- So any composition HTML can use them directly, e.g. karaoke captions:
  ```js
  const split = new SplitText(".caption", { type: "words" });
  gsap.from(split.words, { opacity: 0, y: 20, stagger: 0.08, duration: 0.4 });
  ```

> Source of truth for what's installed/ingested: `2_KNOWLEDGE/INGESTION_INDEX.md`.
> Deeper GSAP authoring guidance: `2_KNOWLEDGE/hyperframes/guides/02_animation_gsap.md`.
