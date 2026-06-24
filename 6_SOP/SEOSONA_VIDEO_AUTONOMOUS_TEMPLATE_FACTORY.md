# SEOSONA Video Autonomous Template Factory SOP

Created: 2026-06-21

## Purpose

This SOP connects HyperFrames, SEOSONA video-maker rules, Hermes Agent operating patterns, and SEOSONA Video into one repeatable workflow for Vietnamese tech-news videos, reusable templates, and clone-style visual production.

## Canonical Sources

| Source | Role In SEOSONA Video | Integration Decision |
|---|---|---|
| `SEOSONA_HYPERFRAMES_SOURCE`, project-drive Downloads, or user Downloads | Local source snapshot for HyperFrames CLI, packages, catalog, skills, docs, and registry patterns. | Reference and sync source. Do not create a second runtime tree. |
| `https://github.com/heygen-com/hyperframes` | Upstream source for HTML-native deterministic rendering, CLI, core/engine/producer, catalog, skills, Studio, and cloud rendering patterns. | Canonical renderer and template model. |
| `SEOSONA_seosona_SKILL`, project-drive Downloads, or user Downloads | Production rules for scene slides, voice/text separation, karaoke captions, SFX, thumbnail, and verification. | Assimilated as SEOSONA quality gates. |
| `https://github.com/NousResearch/hermes-agent` | Operating model for self-improving agents, skills, memory, subagents, scheduled work, terminal/browser control, and persistent learning. | Reference for project-local agent behavior, not imported as an app stack. |

## Routing

1. Use `.agents/skills/hyperframes/SKILL.md` as the entrypoint for video composition work.
2. Use `.agents/skills/seosona-news-maker/SKILL.md` when the work needs production-quality vertical video rules.
3. Use `.agents/skills/seosona-video-operator/SKILL.md` for project-specific automation, audit, template export, and delivery gates.
4. Store reusable templates under `7_ASSETS/templates/<template-id>/`.
5. Store generated productions under `8_WORKSPACE/<ProjectName>/`.

## Autonomous Workflow

### 1. Audit Integration Readiness

Run:

```bash
npm run video:audit:integration
```

The audit checks:

- Local HyperFrames source snapshot.
- Local SEOSONA skill source.
- Project HyperFrames and SEOSONA skills.
- HyperFrames templates.
- BGM, SFX, and font asset libraries.
- Vietnamese male Southern voice policy.
- The approved male Southern voice reference sample.

### 2. Produce News Video

The current news video pipeline must:

- Keep display text and subtitle text in Vietnamese.
- Preserve approved English terms visually.
- Apply pronunciation through `4_BRAIN/news_video_standards.py`.
- Use male Southern target settings from `system_config.yaml`.
- Generate voice, BGM, SFX, scene transitions, SRT, thumbnail, and `production_manifest.json`.
- Render through HyperFrames.

### 3. Export Template

After a successful render, export the reusable template:

```bash
npm run video:template:export -- 8_WORKSPACE/PROJECT_NAME "PROJECT_NAME Template"
```

Or from Python:

```python
from video_template_factory import export_template_from_project

export_template_from_project(
    "8_WORKSPACE/PROJECT_NAME",
    "PROJECT_NAME Template",
    out_root="7_ASSETS/templates",
)
```

The output includes:

- `index.html`
- `hyperframes.json` when available
- `production_manifest.json`
- `sample.srt` when available
- `thumbnail.*` when available
- `assets/` when `copy_assets=True`
- `template.json`

### 4. Clone Video Style

To clone a video style safely:

1. Use only owned, licensed, or generated input assets.
2. Extract a reusable visual template from a verified SEOSONA render.
3. Replace script and voice while preserving layout, motion, timing roles, and audio roles.
4. Re-run the full news quality gate and integration audit.
5. Do not claim voice clone quality unless an approved male Southern reference sample or preset is configured.

## Quality Gates

| Gate | Required Standard |
|---|---|
| Script | Vietnamese, with approved English technical terms only. |
| Pronunciation | Lexicon-based; no phonetic text in visible copy or SRT. |
| Voice | Male Southern target; approved reference required for clone-grade output. |
| Captions | Word-level karaoke, display words aligned to voice timing. |
| Audio | Voice, BGM, and at least one SFX/transition role. |
| Visuals | 9:16, 1080x1920, light-mode SEOSONA/CQA style. |
| Thumbnail | Exists under the project `Thumbnail/` folder. |
| Manifest | Records template, duration, scene count, audio roles, and quality gate state. |
| Template | Exported with `template.json` before reuse. |

## Current Gate State

`SV-INT-VOICE-REFERENCE` is closed in the current project state because `7_ASSETS/voice/profiles/seosona_male_southern.wav` exists. Edge-TTS `vi-VN-NamMinhNeural` remains the approved operational fallback when a clone-grade VieNeu/Fish preset is not available.
