# scripts/ — index (what each script does, where to add)

Kept flat (standard for a tools dir) — many are `npm run` targets in `package.json`
or imported by `4_BRAIN`, so moving them would break refs. Grouped here for clarity.

## ▶️ Workflow entry points (run via `npm run`)
| Script | npm | Does |
|--------|-----|------|
| `4_BRAIN/make_video.py` | `make:video` | GitHub URL → branded video (auto template) + `--news` batch |
| `workflow_video_news.py` | `video:news` | create a Vietnamese tech-news video |
| `workflow_video_course.py` | `video:course` | create a course/educational video |
| `talking_head_transcribe.py` | `talkinghead:transcribe` | footage → words.json (talking-head edit engine) |
| `talking_head_edit.py` | `talkinghead:edit` | footage + words + cards.json → captioned video (9:16/16:9) |
| `workflow_social_post.py` | `post:image` | create a social carousel/post |
| `workflow_thumbnail.py` | `thumbnail:create` | generate a thumbnail |
| `queue_processor.py` | `start:queue` | process the `0_INPUT_INBOX/production_queue.yaml` |
| `seosona-video-integration-audit.py` | `video:audit:integration` | audit the render-engine wiring |

## 🔌 Project infra (SEOSONA OS connector CLI)
| Script | Does |
|--------|------|
| `seosona-project-bridge.cjs` | capability bridge to SEOSONA OS (`~/.seosona`) |
| `seosona-project-audit.cjs` | project audit |
| `seosona-python.cjs` | resolve the project Python interpreter |
| `seosona_doctor.py` | project health check |

## 🏗️ Build
| Script | Does |
|--------|------|
| `build_desktop_app.cjs` | build the desktop app (`build:desktop`) |

## 🎞️ Media tools (run by hand)
| Script | Does |
|--------|------|
| `extract_frames.py` | extract frames from a video |

## 🛠️ Setup / maintenance
| Script | Does |
|--------|------|
| `clean_temp_data.py` | clean temp/cache folders in `8_WORKSPACE` |
| `download_local_models.py` | download local TTS / model files into `7_ASSETS/voice/models` |
| `fast_translate.py` | bulk Vietnamese→English translation utility |
| `inject_os_capabilities.py` | inject SEOSONA OS capabilities into the project |

## 🧪 Untracked scratch / one-off drivers (NOT in git, not npm targets)
Experimental drivers for the new engine, created ad-hoc: `clone_news.py`…`clone_news5.py`,
`clone_datanews.py`, `clone_seo.py`, `clone_repos.py`, `demo_freeform.py`, `demo_variety.py`,
`seo_roadmap.py`, `analyze_reference.py`, `build_bgm.py`, `build_sfx_library.sh`. They call
`native_composer`/`make_video` directly. Safe to `git clean`/consolidate when no longer needed.

**Adding a script:** put it here; if it's a user-facing command, add an entry to
`package.json` "scripts" and a row above.

> Retired (removed): `export-video-template.py`, `clone_loop_template.py`,
> `preview_news_spatial.py`, `preview_spatial_flow.py` (old HTML-template engine).
