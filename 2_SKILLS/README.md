# 2_SKILLS — Python skill toolkit (index)

Reusable Python skills the agents/pipeline call. Each is its own dir importable as
`2_SKILLS.<name>.<module>`. Grouped by function below.

## 🎙️ Voice & TTS
| Skill | Does |
|-------|------|
| `voice_cloner/` | TTS dispatch: VieNeu / **OmniVoice** / Fish-Audio / edge-tts fallback (`fish_audio_api.clone_voice`) |
| `tts_generator/` | edge-TTS voice + subtitle generation (the fallback engine) |

## 📝 Subtitles
| Skill | Does |
|-------|------|
| `srt_maker/` | generate SRT via faster-whisper (word-level timing) |
| `srt_parser/` | parse/manipulate SRT files |

## 🔊 Audio
| Skill | Does |
|-------|------|
| `audio_cleaner/` | clean/denoise audio |
| `audio_mixer/` | mix voice + BGM tracks |
| `sfx_mixer/` | mix sound effects / transitions |

## 🎞️ Visual & media
| Skill | Does |
|-------|------|
| `video_clipper/` | cut/format clips (incl. short-form) |
| `visual_fetcher/` | fetch images/visuals |
| `b_roll_fetcher/` | fetch B-roll footage |
| `thumbnail_maker/` | generate HTML thumbnails |
| `yt_downloader/` | download source videos from YouTube |
| `hf_blueprints/` | HyperFrames composition blueprints/templates |

## ✍️ Content & processing
| Skill | Does |
|-------|------|
| `script_writer/` | script generation helpers |
| `carousel_maker/` | build social carousels |
| `llm_processor/` | LLM call/processing utility |
| `metadata_extractor/` | extract metadata from media/sources |

**Adding a skill:** create `2_SKILLS/<name>/` with a `.py` entry point + `__init__.py`,
call it from the relevant agent or `4_BRAIN/pipeline_manager.py`, and add a row above.
Heavy assets/models a skill needs go in `7_ASSETS/` (see `ASSETS_MAP.md`), not here.
