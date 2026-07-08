# Video-Template coverage audit (56 reels, frame-by-frame) — 2026-07-03

Honest answer to "does the frame library cover ALL styles of the 56 reference reels?"
**Component/LAYOUT vocabulary: YES (43 frames, verified below). Aesthetic STYLES: intentionally ONE — SEOSONA light.**

Source: `D:\SEOSONA AI\Video Template` (56 VN AI/tech 9:16 shorts). Method: contact sheets (~20 frames each),
viewed frame-by-frame (3 agents over all 56 + spot-checks). This closes the study.

## 1. Three separate tiers (don't conflate them)
- **Layout/component** = the card/graphic types. → the 43-frame catalog (`4_BRAIN/frame_study.py`). Covered.
- **Aesthetic/style** = dark-neon, purple-gradient, glossy-3D, particle. → **deliberately NOT replicated.**
  SEOSONA is **light-only** (brand rule). Any pattern seen in a dark reel is adopted in **LIGHT** form.
- **Motion** = reveals, spring, data-flow, shimmer, karaoke word-pop. → separate libraries (effect_library +
  native_composer tweens). Rich; not part of the frame count.

## 2. Coverage matrix — every distinct LAYOUT pattern seen → our frame
| Pattern seen in the reels | Our frame | Note |
|---|---|---|
| Big kinetic number / stat | `bignum` `stats` `stat_grid` | ✓ |
| Radial gauge / speedometer (6x, 80%) | **`gauge`** (BUILT this pass) | was the gap |
| Vertical metric rows (⭐ Stars 4.7K / Forks 1.3K) | **`metric_rows`** (BUILT) | was the gap |
| %/ratio circle | `ring` `ratio_dots` | ✓ |
| Bars / bar chart | `bars` `chart` | ✓ |
| Line/trend chart (+ traveling dot) | `linechart` | ✓ |
| Donut / pie breakdown | `donut` `pie` | ✓ |
| Timeline / milestones | `timeline` | ✓ |
| A-vs-B / before-after | `compare` `split_reveal` | ✓ |
| Feature matrix / ✓✗ table | `comparison_grid` | ✓ |
| Checklist / numbered steps / feature list | `checklist` `steps` `feature` `badges` `icongrid` | ✓ |
| Chip row (inline) | `chiprow` | ✓ |
| Pill stack (vertical "choose path") | **`pill_stack`** (BUILT) | was the gap |
| Tabbed list (Cơ bản/Nâng cao) | **`tabs`** (BUILT) | was the gap |
| Hub / node-link / architecture / RAG-fusion / agent-swarm | `hub` `concept_build` `org_diagram` `layer_stack` | ✓ (data-flow motion added) |
| Terminal / CLI | `terminal` (now **LIGHT**) | dark→light this pass |
| Code / JSON editor (filename tab, syntax) | **`codecard`** (BUILT) | distinct from terminal |
| File tree / repo card | `filetree` `repo` | ✓ |
| Chat / message thread | **`chat`** (BUILT) | was the gap |
| Browser/app screenshot mockup + annotations | `mockup` `annotated_screenshot` `photocard` | ✓ |
| Quote / tip / callout / alert / section divider | `quote` `tip` `callout` `alert` `divider` | ✓ |
| Live activity feed / toast | `ticker_feed` | ✓ |
| CTA (subscribe/like/share/follow) | `cta` | ✓ |

## 3. Deliberately NOT adopted (with reason)
- **Dark-neon / glowing-edge cards** — off the light-only brand. **Converted the only dark thing we had
  (`terminal`) to light.** Everything renders light.
- **Glossy 3D volumetric hero (clocks/gears/spheres), particle/confetti fields** — off the clean-flat SEOSONA
  look; would need heavy WebGL and read as a different channel. Skip.
- **Photoreal product-UI screenshots as the whole scene** — platform-specific; we frame real photos via
  `photocard`/`annotated_screenshot` instead.

## Verdict
43 light frames cover the full LAYOUT vocabulary of all 56 reels (0 gaps remaining after this pass); aesthetic
variety is intentionally one consistent SEOSONA-light style, not a mix of channels' looks. All in
`frame_study.py` (single catalog; `selfcheck()` = 0 drift; picker menu auto-generated → LLM offers all 43).
