# scripts/ — index (what each script does, where to add)

Kept flat (standard for a tools dir) — many are `npm run` targets in `package.json`
or imported by `4_BRAIN`, so moving them would break refs. Grouped here for clarity.

## ▶️ Workflow entry points (run via `npm run`)
| Script | npm | Does |
|--------|-----|------|
| `workflow_video_news.py` | `video:news` | create a Vietnamese tech-news video |
| `workflow_video_course.py` | `video:course` | create a course/educational video |
| `workflow_social_post.py` | `post:image` | create a social carousel/post |
| `workflow_thumbnail.py` | `thumbnail:create` | generate a thumbnail |
| `queue_processor.py` | `start:queue` | process the `0_INPUT_INBOX/production_queue.yaml` |
| `export-video-template.py` | `video:template:export` | export a render into the template registry |

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
| `build_news_project.mjs` | build a news HyperFrames render project |

## 🎞️ Media / template tools (run by hand)
| Script | Does |
|--------|------|
| `clone_loop_template.py` | clone a loop video template |
| `convert_to_9_16.py` | convert a video to 9:16 vertical |
| `extract_frames.py` | extract frames from a video |
| `preview_news_spatial.py` | preview the news-spatial template in a browser |
| `preview_spatial_flow.py` | preview the spatial-flow template |

## 🛠️ Setup / maintenance
| Script | Does |
|--------|------|
| `clean_temp_data.py` | clean temp folders (also imported by `pipeline_manager`) |
| `download_local_models.py` | download local TTS / model files into `7_ASSETS/voice/models` |
| `fast_translate.py` | bulk Vietnamese→English translation utility |
| `inject_os_capabilities.py` | inject SEOSONA OS capabilities into the project |

**Adding a script:** put it here; if it's a user-facing command, add an entry to
`package.json` "scripts" and a row above.
