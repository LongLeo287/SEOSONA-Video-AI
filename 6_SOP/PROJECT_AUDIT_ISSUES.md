# SEOSONA Video Project Audit Issues

Generated: 2026-06-21
Scope: Full SEOSONA Video operational audit, workflow boundaries, voice/subtitle standards, reproducible production assets, integration gates, image workflows, and local publish safety.

## Executive Status

- Operational open issues: none after the current remediation pass.
- SEOSONA OS connector: pass.
- Project audit: pass with production asset, portability, upload-safety, and voice-adapter gates.
- Integration audit: pass.
- Unit tests: pass, 12 tests.
- Node dependency audit: pass with 0 vulnerabilities across 52 production dependencies.
- HyperFrames LOOP clone template validation: pass.
- Post image workflow: pass, generated carousel PNGs and PAS caption.
- Thumbnail workflow: pass, generated 9:16 and 16:9 thumbnails.

## Fixed During This Remediation

| ID | Severity | Area | Issue | Action |
|---|---|---|---|---|
| SV-AUD-039 | P1 | Project bridge | `npm run seosona:doctor` could fail the project health gate on unrelated global OS strict-validation findings. | Split default project binding health from strict OS graph validation; strict mode remains available with `npm run seosona:doctor -- --strict`. |
| SV-AUD-040 | P1 | Autonomy intake | `autonomy:intake` expanded `~/.seosona` through a stale user-home junction and could not find the OS script. | Routed intake through `scripts/seosona-project-bridge.cjs intake`, which resolves OS root through the project manifest and fallback anchors. |
| SV-AUD-041 | P1 | Python wrapper | `scripts/seosona-python.cjs` ran the heavy bootstrapper before every Python command, causing install/update/download side effects during audit and intake. | Made bootstrap opt-in with `SEOSONA_PYTHON_BOOTSTRAP=1`; normal commands now execute only the requested script. |
| SV-AUD-042 | P2 | Audit scope | Project audit treated optional yutu/obscura OS artifacts as core HyperFrames blockers. | Reclassified optional upstream OS artifacts as warnings and kept production-blocking checks focused on SEOSONA Video core contracts. |
| SV-AUD-043 | P2 | Workspace topology | HyperFrames runtime, vendor snapshots, project skills, SOPs, and workspace outputs lacked a single reconnection map. | Added `6_SOP/SEOSONA_VIDEO_RECONNECTION_MAP.md` and linked it from the HyperFrames SOP. |
| SV-AUD-044 | P1 | Integration audit | `npm run video:audit:integration` failed when external Downloads copies of HyperFrames and SEOSONA were absent, even though project-local snapshots existed. | Added project-local fallback sources: `5_FRAMEWORK/hf_engine` for HyperFrames and `.agents/skills/seosona-news-maker/SKILL.md` for SEOSONA. |
| SV-AUD-021 | P2 | Project audit | `4_BRAIN/pipeline_manager.py` contained duplicate `_estimate_word_level_data_from_script` definitions. | Kept one active implementation and renamed the legacy version. |
| SV-AUD-027 | P1 | Video/image boundary | `run_pipeline(..., mode="carousel")` could still hit a legacy image branch inside the video pipeline. | Added a hard runtime guard and removed the unreachable carousel branch. |
| SV-AUD-028 | P1 | Post image workflow | Offline LLM routing could return carousel slide JSON where caption code expected a dict. | Prioritized PAS/social routing and added caption recovery for unexpected provider output. |
| SV-AUD-029 | P1 | Voice standard | Runtime fallback still had female `vi-VN-HoaiMyNeural` paths. | Standardized fallback to `vi-VN-NamMinhNeural`. |
| SV-AUD-030 | P2 | Regression coverage | No test covered social-caption recovery from slide-list output. | Added `tests/test_social_post_workflow.py`. |
| SV-AUD-031 | P2 | Pronunciation lexicon | `lexicon.json` could override the core AI/Search/GitHub/SEO pronunciation standards. | Added a non-removable core pronunciation lexicon in `news_video_standards.py` and merge external lexicon entries on top. |
| SV-AUD-032 | P1 | Reproducible assets | Required voice/BGM/SFX/template audio could be ignored by global media ignore rules. | Added `.gitignore` exceptions for stable production input assets and added audit checks. |
| SV-AUD-033 | P2 | Portability | Utility/runtime scripts used absolute local paths. | Converted path handling to project-relative `Path(__file__).resolve()` discovery. |
| SV-AUD-034 | P2 | Integration defaults | Integration audit hardcoded local download paths. | Replaced hardcoded defaults with env/project-drive/home Downloads discovery. |
| SV-AUD-035 | P2 | Voice adapter completeness | Fish/VieNeu path had an unfinished TODO and unclear fallback semantics. | Rewrote the adapter contract: use approved engines when available, otherwise explicitly fall back to the male Vietnamese voice. |
| SV-AUD-036 | P2 | Audit noise | Broad scans mixed runtime code with vendor/reference trees. | Added scoped runtime portability and asset checks to `npm run seosona:audit`. |
| SV-AUD-037 | P3 | Local publish safety | `auto_upload_gdrive` was enabled by default. | Disabled it by default and added an audit gate to prevent silent publish behavior. |
| SV-AUD-038 | P1 | Template registry | LOOP clone registry template referenced missing `../template_core.js`. | Removed the stale dependency; HyperFrames validation now passes with no console errors. |
| SV-INT-VOICE-REFERENCE | P1 | Voice standard | Prior audit listed the male Southern reference sample as missing. | Current integration audit confirms `7_ASSETS/voice/profiles/seosona_male_southern.wav` exists and passes. |

## Release Bookkeeping

The active runtime and asset gates are clean. Git still contains pending modified/untracked/deleted files because this remediation intentionally updates project code, SOPs, generated skills, and template assets. The deleted legacy image/logo files are not referenced by current runtime gates; the active brand assets are now protected by `npm run seosona:audit`.

## Verification Commands

```bash
node scripts/seosona-python.cjs -m unittest discover tests
node scripts/seosona-python.cjs -m py_compile scripts/convert_to_9_16.py scripts/extract_frames.py scripts/preview_news_spatial.py scripts/inject_os_capabilities.py 4_BRAIN/run_demo.py 2_SKILLS/thumbnail_maker/thumbnail_generator.py 2_SKILLS/voice_cloner/fish_audio_api.py 4_BRAIN/news_video_standards.py 4_BRAIN/video_integration_audit.py
npm run seosona:audit
npm run video:audit:integration
npm audit --omit=dev --json
npx --yes hyperframes@0.6.112 validate 7_ASSETS/templates/loop-source-seosona-clone
npm run post:image -- "AI Search đang thay đổi cách người dùng tìm thông tin. Doanh nghiệp cần chuẩn hóa nội dung, dữ liệu nguồn và quy trình xuất bản để được AI trích dẫn đúng."
npm run thumbnail:create -- "SEOSONA kiểm tra pipeline video và hình ảnh"
```

## Current Verified Outputs

- `8_WORKSPACE/Social_Campaigns/Campaign_SEOSONA_1782018875/`: carousel plan, Facebook caption, and 6 rendered PNG slides.
- `8_WORKSPACE/Video_Thumbnails/SEOSONA_SEOSONA_kiểm_tra_1782018875/`: 9:16 and 16:9 thumbnail PNGs.
- `8_WORKSPACE/LOOP_CLONE_SEOSONA_TEMPLATE/LOOP_CLONE_SEOSONA_TEMPLATE.mp4`: LOOP clone template video.
- `7_ASSETS/templates/loop-source-seosona-clone/`: HyperFrames template validated with no console errors and 150 text elements passing WCAG AA.

TASK COMPLETED
