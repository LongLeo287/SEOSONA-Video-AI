# 2_SKILLS — Python skill toolkit (index)

Reusable Python skills the agents/pipeline call. Each is its own dir importable as
`2_SKILLS.<name>.<module>`. **Every skill listed below is wired into a live code path**
(video_engine, workflow_router, or a `workflow_*` script). Grouped by function.
Updated 2026-07-14 (engine consolidation).

## 🎙️ Voice & ASR (one engine each — 2026-07-14 user decision, no backups, fail honest)
| Skill | Does | Wired via |
|-------|------|-----------|
| `voice_cloner/` | **OmniVoice ONLY** (`voice_router.synthesize_voice` → `omnivoice_engine`, CQA brand clone, isolated `.venv-omnivoice`). Weights CC-BY-NC — owner-accepted (see `0_SETUP/MODELS.md`). No fallback: failure returns None. | `video_engine`, `native_composer` |
| `srt_maker/` | **PhoWhisper-large-ct2 ONLY** via faster-whisper (`asr_router.transcribe_words`, word timestamps, cuda auto-detect) + `whisper_engine.group_words_to_segments` (caption segmentation util) | `video_engine`, `talking_head_*` |

## 🎞️ Visual & media
| Skill | Does | Wired via |
|-------|------|-----------|
| `video_clipper/` | cut/format clips (incl. short-form vertical) | `video_engine` (repurpose) |
| `thumbnail_maker/` | generate HTML thumbnails (+ `frame_scorer` best-frame picker) | `video_engine`, `workflow_thumbnail` |
| `image_sourcer/` | auto-source a real 9:16 photo per scene (Pexels + URL scrape) | scene backgrounds |
| `broll_sourcer/` | source b-roll footage (yt-dlp based) | talking_head b-roll |
| `bgm_sourcer/` | CC music by mood (Openverse→Jamendo, keyless) → `7_ASSETS/audio/bgm` | `native_composer._bgm` |
| `element_maker/` | dense visual-element layer (icon-tiles/emoji/badges) HTML→transparent-PNG | talking-head `elements:[...]` |
| `yt_downloader/` | download source videos from YouTube | `workflow_router` |
| `hf_blueprints/` | HyperFrames composition blueprints/templates (HTML, not a Python skill) | render scaffolds |

## ✍️ Content & processing
| Skill | Does | Wired via |
|-------|------|-----------|
| `carousel_maker/` | build social carousels (demo output → `8_WORKSPACE/_demo/carousel`) | `workflow_social_post` |
| `os_*` dirs | SEOSONA-OS shared skills (gdrive-manager, humanizer, decodo, infographic) | OS integration |

**Adding a skill:** create `2_SKILLS/<name>/` with a `.py` entry point + `__init__.py`,
call it from the relevant agent or `4_BRAIN/video_engine.py`, and add a row above.
Heavy assets/models a skill needs go in `7_ASSETS/` (see `ASSETS_MAP.md`), not here —
and register any model in `0_SETUP/MODELS.md` (fetch + license + delete rules).
