# VIDEO ARCHITECTURE — one shared spine, two specialised branches

SEOSONA makes two visually different kinds of video from **one shared foundation**. This is the map of
what is SHARED (never duplicate it) vs what is BRANCH-SPECIFIC (specialise it). The rule: add to the
shared spine when both branches benefit; add to a branch only for its medium.

## The shared spine (BOTH branches use — do NOT duplicate)
| Piece | Where | Role |
|---|---|---|
| **LLM cascade** | `llm_engine.generate_json_strict()` | Gemini(keys rotated)→Z.ai→OpenAI→Ollama→Claude, shape-validated, no offline router. Used by every content generator. |
| **Brand** | `brand_kit.py` | single palette + CTA copy (light-mode only). |
| **SFX library** | `7_ASSETS/audio/sfx/` | impact / pops / riser / transition / typing / ui accents. |
| **Caption segmentation** | `caption_segment.py` | natural-break word grouping for karaoke. |
| **Narrative structure** | HOOK → … → CTA (5-act) | the retention spine of every script. |
| **Verify discipline** | `script_writer.verify` (news) · `spec_lint.lint_course` (talking-head) | nothing ships un-checked. |

## Branch NEWS — animated (HyperFrames)
Topic/GitHub → **generated** Vietnamese narration → animated scenes → TTS voice.
| Layer | Module | Vocab |
|---|---|---|
| Prompt/rules | `9_PROMPTS/MASTER_VIDEO_SPEC.md` + `script_writer` | — |
| **Library** | `component_picker` + `block_picker` + `effect_library` | component (~15: bignum/compare/steps/…) · block (data-chart/…) · effect (SFX/transition/entrance) |
| Template | `template_picker` | layout templates |
| Voice | `voice_router` → **OmniVoice** (TTS) | brand clone |
| Render | `native_composer` | HTML/HyperFrames → mp4 |
| Coupling | `script_writer.suggest_component / suggest_fx` | writer suggests component+block+fx per scene; narration written to fit |

## Branch TALKING-HEAD — real footage (course / knowledge)
SRT of a real teacher → **selected/re-ordered** real segments (nothing generated) → cards over footage.
Narration = the teacher's REAL voice (no TTS); traceability N/A (real transcript).
| Layer | Module | Vocab |
|---|---|---|
| Prompt/rules | `9_PROMPTS/COURSE_SPLICE_PROMPT.md` + `course_planner` | 5-act splice matrix |
| **Library** | cards in `talking_head_edit.build_ass` | card types: header / bullet / stat / term / **steps** / **quote** |
| Template | 3-zone layout (TOP card / MIDDLE speaker / BOTTOM karaoke) + card templates cloned from reference reels | — |
| Voice | the real footage audio | — |
| Render | `talking_head_edit` (+ `course_video`) | ASS karaoke + cards burned on footage |
| Coupling | `course_planner.suggest_card(part)` | each segment gets a typed card from its part; `course_video.topcards_from_plan` emits it; `spec_lint.lint_course` validates the type |

## Why NOT a fully separate branch
Talking-head is ALREADY a parallel branch (own prompt, card library, template, render, gate). It SHARES
the spine (LLM/brand/SFX/structure/caption) because duplicating those would violate "tránh trùng lặp"
and drift out of sync. Component/block/fx are the NEWS medium (animated); talking-head uses cards on
real footage — different medium, correctly separate. Keep the spine shared; grow each branch's own
library/prompt/template as its medium needs.
