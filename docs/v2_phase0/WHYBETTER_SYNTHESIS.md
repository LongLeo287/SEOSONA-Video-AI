# Why-are-they-better — synthesis of 4 repos vs V2 (2026-07-16)

Deep comparative dig: bachdyon (Remotion, Noncommercial), Auto-Create-Video (HyperFrames+GSAP, MIT), huytranvan/AI-auto-generate (HyperFrames, MIT), nexu/html-video (HyperFrames/Remotion, Apache-2.0). Parts: `WHYBETTER_{bachdyon,autocreate,huytranvan,nexu}.md`. Honest, non-defensive.

## The big correction (self-audit — nexu surfaced it)
My earlier premise "V2 = ffmpeg fades, no real animation" is **HALF WRONG about V2's capability**. V2 **already owns** a per-frame GSAP animation engine: ADR-002 (HyperFrames = seekable primary renderer) + legacy `4_BRAIN/native_composer.py` builds a **paused GSAP master timeline rendered per-frame via the HyperFrames CLI**, with the Remotion spring solver ported into GSAP CustomEase (`springLand`, ~L2906), SplitText kinetic type, ASR karaoke. The competitors stand on the **same HyperFrames+GSAP substrate** — they are NOT ahead on the engine.

**What actually happened:** the NEW `nativeRenderAdapter` I just built rendered ONE static PNG per element + faked motion with ffmpeg fades — a **regression** from both legacy and ADR-002. So my *demo* looked less animated than theirs, not because V2 lacks the engine, but because the new adapter down-specced it. That is the honest reason the last reel felt flatter.

## Where they are genuinely ahead (real gaps, all closable)
| # | Gap | Evidence | V2 fix | Effort | License |
|---|---|---|---|---|---|
| 1 | **LLM content director** — scene role / punch keyword / pacing decided by LLM semantic reasoning, not rules | bachdyon (#1), huytranvan authoring SKILL | **Wire V2's videoAnalyzer LLM seam** (currently deterministic→filler "ANH/ĐỂ") + filler blocklist + breath-segment (7-8 word) captions with 1 punch keyword | Med | technique |
| 2 | **Real per-frame motion applied to the NEW brand look** | all 4 use GSAP/WAAPI per-frame Chromium | **Rebuild nativeRenderAdapter motion on the HyperFrames/GSAP seek engine V2 ALREADY owns** (undo the fade regression) + harvest nexu's **WAAPI+GSAP `seek(timeMs)` driver** (~40 lines, Apache — captures native CSS @keyframes, the one class our seek-safety avoided) + font-settle/freeze-at-0 | Med/High | Apache (nexu) |
| 3 | **Sound design** — 3-tier semantic SFX + ffmpeg amix ducking | huytranvan `sfx-selector.ts`+`mixSfxOntoVoice` | **Port (MIT) + wire our existing `7_ASSETS/audio/sfx` + BGM into the native auto path** | Low | MIT |
| 4 | **Timing correctness** — fit-clip-to-narration + packet-counted MP3 duration | huytranvan `video-tools.ts`/`audio-tools.ts` | **Port verbatim (MIT).** ⚠️ V2 runs the SAME OmniVoice 24kHz MPEG-2 L3 → likely shares the ~30% `format=duration` bug — fix it | Low | MIT |
| 5 | **B-roll matched to speech** — semantic asset index + coverage planner | bachdyon | **Wire V2's #17 semantic-asset-index (partial) + coverage decider** | Med | technique |
| 6 | Art-directed template library (11) | huytranvan/nexu | Vendor Apache-2.0 templates (optional) | Low | Apache |

## Where V2 is genuinely ahead (fair, not defensive)
- **Keyless / local / free** vs their paid Gemini/OpenAI/fal/HeyGen stack.
- **Real talking-head** footage + **PhoWhisper ASR** + **face-centered reframe** + **burned ASS karaoke** — bachdyon has some; Auto-Create/huytranvan have NONE (they hand captions to CapCut, no ASR, faceless only).
- **rembg text-behind-speaker occlusion** — they only *avoid* the subject; we composite behind it.
- **Owns the animation engine lineage** (`5_FRAMEWORK/hf_engine`, Apache-2.0) + BGM sourcer + eval flywheel + knowledge graph + cover-frame scorer.

## Verdict
They are NOT structurally better; they made 2 bets we under-executed: (a) an LLM deciding content, and (b) actually using the per-frame animation engine. Both are **wiring/technique against our own stack**, no toolchain adoption needed. Net plan: **wire the LLM director + put the new brand look back on the GSAP seek engine + port the MIT sound/timing nuggets.** Keep V2's talking-head + brand + keyless advantages.

## Priority
- **P1a — LLM content director** (biggest content win; seam already exists) → kills filler-word selection.
- **P1b — Motion on the real GSAP seek engine** (undo the fade regression; V2 owns it) + nexu WAAPI seek driver.
- **P2 — Sound (SFX+ducking) + OmniVoice duration fix + fit-clip-to-narration** (MIT, low effort, quick quality lift).
- **P3 — B-roll semantic match; templates.**
