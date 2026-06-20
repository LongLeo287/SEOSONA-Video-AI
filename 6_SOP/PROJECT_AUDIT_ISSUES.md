# SEOSONA Video Project Audit Issues

Generated: 2026-06-20
Scope: SEOSONA Video repository, SEOSONA OS connector, video pipeline runtime, agent/skill imports, dependency/security smoke checks.

## Executive Status

- SEOSONA OS connector: pass.
- Project audit: pass.
- Node dependency audit: pass with 0 vulnerabilities.
- Runtime video output: pass, verified with the Obscura news video at `8_WORKSPACE/NEWS_OBSCURA_20260620/NEWS_OBSCURA_20260620.mp4`.
- Deep exhaustive security scan: deferred because the formal Codex security workflow requires explicit subagent authorization.

## Fixed During This Audit

| ID | Severity | Area | Issue | Action |
|---|---|---|---|---|
| SV-AUD-007 | P1 | Publisher agent | `1_AGENTS/publisher_agent/youtube_uploader.py` had invalid Python syntax in a broken string literal. | Rewrote the uploader with clean English logging and preserved yutu CLI behavior. |
| SV-AUD-008 | P1 | SEO metadata | `1_AGENTS/seo_optimizer/youtube_seo.py` had invalid Python syntax and placeholder-only metadata logic. | Replaced it with working title, description, tags, hashtags, and JSON-LD generation. |
| SV-AUD-009 | P1 | Package exports | `publisher_agent.__init__`, `seo_optimizer.__init__`, and `audio_cleaner.__init__` exported symbols that did not exist. | Updated exports and compatibility aliases. |
| SV-AUD-010 | P1 | Autonomy connector | `npm run autonomy:intake` pointed to local `1_CORE/scripts/autonomous_activation_gate.py`, but the project does not contain local `1_CORE`. | Added `~` expansion to `scripts/seosona-python.cjs` and repointed package scripts to `~/.seosona/1_CORE/scripts/autonomous_activation_gate.py`. |
| SV-AUD-011 | P2 | Security hardening | `2_SKILLS/metadata_extractor/extractor.py` used `eval()` to parse ffprobe frame rates. | Replaced with `fractions.Fraction`. |
| SV-AUD-012 | P2 | Security hardening | `2_SKILLS/audio_cleaner/demucs_engine.py` used `shell=True` with interpolated paths. | Replaced with list-form subprocess arguments. |
| SV-AUD-013 | P2 | Render runtime | HyperFrames render needed portable ffmpeg/ffprobe and UTF-8 environment handling. | `scripts/seosona-python.cjs` now injects `ffmpeg-static`, `ffprobe-static`, and UTF-8 env vars. |
| SV-AUD-014 | P2 | Render timeline | Caption and SFX tracks collided during HyperFrames lint. | SFX tracks now start from a separate track range; caption timing is bounded. |
| SV-AUD-020 | P1 | Video runtime | Current `video:run` failed on `.venv` due broken `voice_cloner.__init__`, VieNeu voice fallback, and MoviePy import compatibility. | Restored `fish_audio_api` export, added VieNeu-to-Edge fallback, and added MoviePy 1.x/2.x `AudioFileClip` compatibility. |
| SV-AUD-021 | P2 | Project audit | `4_BRAIN/pipeline_manager.py` contained duplicate `_estimate_word_level_data_from_script` definitions. | Removed the shadowed duplicate implementation. |
| SV-AUD-022 | P2 | Bootstrapper | `scripts/seosona_doctor.py` used shell-style command strings that broke on Windows paths with spaces. | Switched to list-form subprocess commands with `shutil.which()` executable resolution. |

## Open Issues

| ID | Severity | Area | Issue | Evidence | Recommended Next Action |
|---|---|---|---|---|---|
| SV-AUD-015 | P1 | Autonomy gate | `npm run autonomy:intake -- --task "audit SEOSONA Video pipeline"` resolves the OS script after the fix but produces no output for more than 90 seconds. | Process had to be stopped manually after `autonomous_activation_gate.py` stayed silent. | Add timeout/progress logging to the OS gate or create a project-local fast intake wrapper. |
| SV-AUD-016 | P2 | Placeholder content | Multiple agent/skill files still contain placeholder text `System log`. | `rg "System log" 1_AGENTS 2_SKILLS 4_BRAIN scripts -g '*.py'` still returns hits. | Replace placeholders in writer, researcher, script writer, repo analyzer, audio mixer, voice wrappers, and related templates. |
| SV-AUD-017 | P2 | Python package design | `4_BRAIN/workflow_router.py` imports `knowledge_indexer` as a script-local module, so package-style import fails unless `4_BRAIN` is manually added to `sys.path`. | Plain `importlib.import_module("4_BRAIN.workflow_router")` fails; script-mode runtime works. | Convert `4_BRAIN` imports to package-safe fallback imports. |
| SV-AUD-018 | P3 | Optional vector index | `workflow_router` logs `ChromaDB not installed. Skipping vector index.` | Import smoke shows the warning. | Decide whether ChromaDB is required; if yes, add it to requirements and doctor checks. |
| SV-AUD-019 | P3 | Large reference tree | Whole-repo Python compile over `5_FRAMEWORK` and `8_WORKSPACE` is too slow for routine CI. | `compileall` across runtime plus framework/workspace had to be stopped. | Add a scoped test command that excludes generated workspace, vendor, and reference trees. |
| SV-AUD-023 | P3 | Bootstrapper | The `.venv` Python runtime used by `video:run` does not have the `playwright` Python package, so the bootstrapper prints a Playwright browser install failure before rendering. | Smoke render still succeeds through HyperFrames browser cache. | Either install Python Playwright into `.venv` or make the bootstrapper skip Python Playwright when HyperFrames/node browser is authoritative. |

## Verification Commands

```bash
npm test
npm run seosona:resolve
npm run seosona:doctor
npm run seosona:validate
npm run seosona:audit-portability
npm run seosona:audit
npm audit --omit=dev --json
python -m pip check
node --check scripts/seosona-python.cjs
python -m py_compile 1_AGENTS/publisher_agent/youtube_uploader.py 1_AGENTS/seo_optimizer/youtube_seo.py 2_SKILLS/audio_cleaner/demucs_engine.py 2_SKILLS/metadata_extractor/extractor.py 4_BRAIN/pipeline_manager.py 4_BRAIN/workflow_router.py
npm run video:run -- 8_WORKSPACE/NEWS_OBSCURA_20260620_SCRIPT.txt seosona 9:16 AUDIT_SMOKE_VIDEO
```

## Current Verified Output

- `8_WORKSPACE/NEWS_OBSCURA_20260620/NEWS_OBSCURA_20260620.mp4`
- ffprobe: 1080x1920, 30 fps, H.264 video, AAC audio, duration 75.855 seconds.
- `8_WORKSPACE/AUDIT_SMOKE_VIDEO/AUDIT_SMOKE_VIDEO.mp4`
- ffprobe: 1080x1920, 30 fps, H.264 video, AAC audio, duration 75.855 seconds.

TASK COMPLETED
