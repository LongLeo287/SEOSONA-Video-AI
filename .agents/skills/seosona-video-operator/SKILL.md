---
name: seosona-video-operator
description: Operate SEOSONA Video end-to-end: audit integrations, create Vietnamese tech-news videos, export reusable HyperFrames templates, and enforce voice/subtitle/audio/thumbnail quality gates.
metadata:
  type: skill
  project: seosona-video
  version: "1.0"
---

# SEOSONA Video Operator

Use this skill when a task asks to audit, improve, clone, template, or produce videos inside SEOSONA Video.

## Operating Contract

1. Source language in scripts, subtitles, scene copy, and thumbnails is Vietnamese.
2. English technical terms stay visually correct in display text.
3. Pronunciation is handled through the lexicon in `4_BRAIN/news_video_standards.py`, not by writing phonetics into display text.
4. Default news voice target is male Southern Vietnamese. The fallback voice is `vi-VN-NamMinhNeural`; true approved-clone output requires `7_ASSETS/voice_profiles/seosona_male_southern.wav` or an approved VieNeu preset.
5. Production outputs must include voice, background music, SFX/transitions, subtitles, thumbnail, and a production manifest.
6. HyperFrames is the canonical renderer. MoviePy/FFmpeg are fallback or muxing tools, not the primary template authoring model.

## Intake

Run the integration audit before major pipeline work:

```bash
npm run video:audit:integration
```

If the audit fails only because `SV-INT-VOICE-REFERENCE` is open, production may run with the male Edge-TTS fallback, but do not claim the output is a fully approved Southern voice clone.

## Create A News Video

Use:

```bash
npm run video:run -- seosona create 9:16 PROJECT_NAME
```

The pipeline routes through `4_BRAIN/workflow_router.py`, `4_BRAIN/pipeline_manager.py`, `4_BRAIN/news_video_standards.py`, and the HyperFrames templates under `5_FRAMEWORK/`.

## Export A Reusable Template

After a successful render, export the HyperFrames render project into the template registry:

```python
from video_template_factory import export_template_from_project

export_template_from_project(
    "8_WORKSPACE/PROJECT_NAME",
    "Project Name Template",
    out_root="7_ASSETS/video_templates",
)
```

The exported template preserves layout, motion, sample subtitle, thumbnail, and production metadata. It is intended for cloning a visual style while replacing script and voice in future runs.

## Required Verification

Run:

```bash
python -m unittest tests.test_news_video_standards tests.test_video_template_factory tests.test_video_integration_audit
npm run seosona:audit
```

For final delivery videos, also verify the MP4 with ffprobe or the project manifest:

- H.264 video stream.
- AAC audio stream.
- 1080x1920 for vertical news output.
- `production_manifest.json` reports voice, BGM, and SFX roles.
- SRT words match display text, not pronunciation text.
- Thumbnail exists under `8_WORKSPACE/<ProjectName>/Thumbnail/`.

## Related SOP

Read `6_SOP/SEOSONA_VIDEO_AUTONOMOUS_TEMPLATE_FACTORY.md` before changing template, clone, or automation behavior.
