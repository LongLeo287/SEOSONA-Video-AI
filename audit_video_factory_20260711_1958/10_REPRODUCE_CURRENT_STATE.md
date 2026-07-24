# 10 — REPRODUCE CURRENT STATE

> How to run the system as it stands today. **No installs were performed during this audit.**
> The cleanest single-video path is the **News / animated pipeline** (`npm run video:news`).

## Prerequisites (CONFIRMED from `0_SETUP/ENVIRONMENT.md`, `package.json`, `.env`)

1. **Node ≥ 20** (v22 tested) + `npm install` — pulls the render engine `hyperframes@0.7.24`, `@hyperframes/producer`, `ffmpeg-static`, `ffprobe-static`, `playwright`, `puppeteer-core`.
2. **Python 3.11** with the expected venvs on PATH. Inference venv pins **torch 2.5** (do not bump). OmniVoice brand-voice uses its own GPU venv (`7_ASSETS/voice/.venv-omnivoice`, PRESENT). Bootstrap: `0_SETUP\bootstrap.ps1`; verify: `python 0_SETUP\check_env.py` (npm: `env:check`).
3. **Models** — PhoWhisper-medium-ct2 ASR PRESENT in repo; OmniVoice CQA ref PRESENT; VieNeu backup auto-downloads (needs `HF_TOKEN` on first pull). LTX-Video local weights marker PRESENT (`7_ASSETS/models/ltx.ready`).
4. **`.env`** present (~3.5 KB). System is **keyless-capable**: LLM cascade Gemini→Z.ai→OpenAI→Ollama→Claude; render + VieNeu voice run local/free. See [ENV names](02_TECH_STACK_AND_SERVICES.md) — values never printed.
5. **GPU + NVIDIA driver** only needed for the OmniVoice brand voice; otherwise it falls back to VieNeu (CPU, off-brand).
6. **External SEOSONA OS junction** at `~/.seosona` — `npm run seosona:doctor` (also `npm test`) checks this binding. Rendering does not require the OS, but a stale junction fails the doctor check.

## Current runtime state at audit time (CONFIRMED)

- **Autonomous loop is PAUSED** — `0_INPUT_INBOX/STOP` exists (dated 2026-07-11 19:55, file locked/unreadable — likely held by `loop_guard`). Per `LOOP_OPERATING_SOP.md`, `queue_processor`/`daily`/`factory` loops halt while it is present. **Delete it to resume** batch/autonomous runs.
- **Production queue is empty** — `0_INPUT_INBOX/production_queue.yaml` has only empty `''` placeholders for `news_videos / course_videos / carousels / thumbnails`.
- **Dashboard** — Flask, port **5050** (`SEOSONA_DASHBOARD_PORT`/`PORT`). Started via `npm run start:dashboard`. During this audit it started and served HTTP 200 on all read-only endpoints (`/api/health`, `/api/metrics`, …); captured JSON is in `screenshots/`. (The in-app browser could not screenshot the page — its JS hung — so status JSON was captured instead.)

## Sample input

- Inline text/topic string, a `.txt`/`.md` script file, or a website / GitHub URL (auto-detected by `video_engine.detect_input_type`).
- Batch: fill `0_INPUT_INBOX/production_queue.yaml` under the relevant key.

## Commands — the happy path

```powershell
# 1) One video from a script / topic / URL (aspect default 9:16)
npm run video:news -- "Cách tối ưu SEO on-page 2026" my_first_video 9:16

# 2) GitHub repo → branded video (one-shot)
npm run make:video -- https://github.com/owner/name

# 3) Autonomous topic discovery → video (requires a reachable LLM)
npm run video:discover -- --discover "SEO"

# 4) Batch: fill production_queue.yaml, then process it
npm run start:queue        # or: npm run daily   (scheduled/unattended)

# Talking-head / course path (footage in → captioned short out)
npm run video:course -- <lecture.mp4> --srt <optional.srt>
```

Expected end state (CONFIRMED from script docstrings + verified outputs): `8_WORKSPACE/<project_name>/` containing **FINAL.mp4** (1080×1920 H.264 + AAC), **SRT**, **thumbnail PNG**, and a render manifest. Thumbnails-only → `8_WORKSPACE/Video_Thumbnails/`; social → `8_WORKSPACE/Social_Campaigns/`. `8_WORKSPACE/` is gitignored/transient.

## Standalone engines (NOT auto-wired — run by hand)

| Engine | Command | Runnable now? |
|---|---|---|
| Seedance / LTX-Video b-roll (#6) | `python scripts/seedance_engine.py --script ... ` | YES via keyless local LTX (weights present); paid providers inactive (no keys) |
| Lipsync service / MuseTalk (#3b) | `python 4_BRAIN/lipsync_service.py ...` | NO — `.venv-musetalk` missing |
| Portrait avatar / SadTalker (#3) | `python scripts/portrait_avatar.py ...` | NO — `.venv-sadtalker` + repo missing |
| LivePortrait motion (#5) | `python scripts/liveportrait_motion.py ...` | NO — `.venv-liveportrait` + weights missing |
| Cinematic reel editor (standalone) | `python 8_WORKSPACE/adsbootcamp_11_07/cinematic_reel.py ...` | Partial — needs ffmpeg/PIL/rembg; separate from the factory engine |

## Most likely failure points (INFERRED, evidence-backed)

1. **Loop paused** — the `STOP` file blocks batch/autonomous runs until deleted.
2. **Wrong Python on PATH** — three venvs; `workflow_router` monkeypatches `PIL.Image.ANTIALIAS` for MoviePy-1.0.3/Pillow-10 compat, so a Pillow mismatch surfaces here.
3. **OmniVoice GPU path inactive** → voice silently falls back to VieNeu (works, but off-brand — the 2026-07-06 renders show `vieneu:*`, not OmniVoice).
4. **LLM cascade all-down** — `topic_to_video`/`script_writer` ABORT by design (no fabrication) if `SEOSONA_REQUIRE_LLM=1` and no key/Ollama reachable. `video:news` from explicit text avoids this.
5. **Relative project paths** — `native_composer` needs absolute paths or renders silently fail with a stale mp4 (known bug class). See [FAILURE_ANALYSIS](06_FAILURE_ANALYSIS.md).
6. **Upstream scrape** — a URL that yields no usable text aborts before render (the one real FAILED report: `labs.toby.vn`).
7. **Length gate** — output outside the 15–95s band is rejected even though it rendered fine.
8. **`hyperframes` version lock** — pinned `0.7.24`; bumping without a render smoke-test breaks the engine.

## Key file paths

- Engine: `4_BRAIN/video_engine.py` → `4_BRAIN/native_composer.py` → `4_BRAIN/scene_composer.py`; router `4_BRAIN/workflow_router.py`; one-shot `4_BRAIN/make_video.py`.
- Config: `system_config.yaml` (render 1080×1920@30, libx264; brand profiles/colors/voice), `.env`, `seosona.project.json`.
- Setup: `0_SETUP/ENVIRONMENT.md`, `0_SETUP/bootstrap.ps1`, `0_SETUP/check_env.py`.
- Input/state: `0_INPUT_INBOX/production_queue.yaml`, `0_INPUT_INBOX/STOP` (kill-switch, present).
