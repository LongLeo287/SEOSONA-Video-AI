# 2_SKILLS — Python skill toolkit (index)

Reusable Python skills the agents/pipeline call. Each is its own dir importable as
`2_SKILLS.<name>.<module>`. **Every skill listed below is wired into a live code path**
(pipeline_manager, workflow_router, or a `workflow_*` script). Grouped by function.

> Unwired skills were moved to `_QUARANTINE/orphan_skills/` on 2026-06-25 — see that
> folder's `README.md` for the list and how to restore them.

## 🎙️ Voice & TTS
| Skill | Does | Wired via |
|-------|------|-----------|
| `voice_cloner/` | TTS single-router: **VieNeu** (clone > preset) → honest **edge-tts** fallback (`voice_router.synthesize_voice`). Single source of truth — no legacy fish/f5/omnivoice branches. | `pipeline_manager`, `localizer` |
| `tts_generator/` | edge-TTS voice + subtitle generation (the fallback engine) | `voice_cloner/voice_router.py` |

## 📝 Subtitles
| Skill | Does | Wired via |
|-------|------|-----------|
| `srt_maker/` | generate SRT via faster-whisper / PhoWhisper (word-level timing) | `pipeline_manager`, `localizer` |

## 🎞️ Visual & media
| Skill | Does | Wired via |
|-------|------|-----------|
| `video_clipper/` | cut/format clips (incl. short-form vertical) | `pipeline_manager` (repurpose) |
| `thumbnail_maker/` | generate HTML thumbnails | `pipeline_manager`, `workflow_thumbnail` |
| `yt_downloader/` | download source videos from YouTube | `workflow_router` |
| `hf_blueprints/` | HyperFrames composition blueprints/templates (HTML, not a Python skill) | render scaffolds |

## ✍️ Content & processing
| Skill | Does | Wired via |
|-------|------|-----------|
| `carousel_maker/` | build social carousels | `workflow_social_post` |
| `translator/` | localize/translate script text | `localizer` |

**Active Python skills: 8** (+ `hf_blueprints` templates).

**Adding a skill:** create `2_SKILLS/<name>/` with a `.py` entry point + `__init__.py`,
call it from the relevant agent or `4_BRAIN/pipeline_manager.py`, and add a row above.
Heavy assets/models a skill needs go in `7_ASSETS/` (see `ASSETS_MAP.md`), not here.
