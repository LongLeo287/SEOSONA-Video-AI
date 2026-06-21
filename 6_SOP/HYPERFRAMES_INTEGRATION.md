# HyperFrames Integration SOP

## Purpose

SEOSONA Video uses HyperFrames as the primary HTML-to-video renderer for template-driven vertical video, motion graphics, caption effects, and reusable visual blocks.

## Source Of Truth

- Vendor source snapshot: `5_FRAMEWORK/hf_core/.skills/`
- Registry snapshot: `5_FRAMEWORK/hf_core/registry/`
- Active render project: `5_FRAMEWORK/hf_core/`
- Reusable stat-card render project: `5_FRAMEWORK/hf_cards/`

Do not create another HyperFrames vendor tree. The local `registry/` is already synchronized with the external HyperFrames repo, so new ingestion work should update the single `.skills/` snapshot or create SEOSONA-native adapters around it.

## Routing

Use the vendor skills as follows:

- `hyperframes-core`: composition structure, data attributes, sub-compositions, media, validation.
- `hyperframes-animation`: GSAP timelines, motion rules, transitions, runtime adapters.
- `hyperframes-creative`: style direction, typography, pacing, palette decisions.
- `hyperframes-media`: TTS, transcription, captions, media preparation.
- `hyperframes-registry`: block/component lookup and install patterns.
- `faceless-explainer`: long-form text-to-video workflow patterns.
- `embedded-captions` and `graphic-overlays`: existing footage enhancement.
- `motion-graphics`: short kinetic stat cards, lower thirds, chart reveals, and logo stings.
- `seosona-video-operator`: project-level audit, Vietnamese news delivery gates, template export, and clone-safe reuse.

## SEOSONA Video Rules

1. Keep HyperFrames CLI calls pinned to `hyperframes@0.6.112` unless the whole project is upgraded in one pass.
2. Run `npm run check` inside the affected HyperFrames project after editing any composition.
3. Avoid render-time network fetches. Use local `@font-face` declarations and local assets.
4. Put vendor knowledge in `5_FRAMEWORK/hf_core/.skills/`; put SEOSONA-specific decisions in this SOP or project memory.
5. Use `8_WORKSPACE/<ProjectName>/` for production outputs. Do not revive legacy `4_WORKSPACE/output` paths.
6. Prefer HyperFrames for template and motion work; keep MoviePy only for clipping or fallback processing.

## Template Export

Verified render outputs can be exported into reusable templates with `4_BRAIN/video_template_factory.py`.

```python
from video_template_factory import export_template_from_project

export_template_from_project(
    "8_WORKSPACE/PROJECT_NAME",
    "PROJECT_NAME Template",
    out_root="7_ASSETS/video_templates",
)
```

Run `npm run video:audit:integration` before major template or clone work. The audit intentionally reports `SV-INT-VOICE-REFERENCE` until the approved male Southern voice sample exists.

## Ingestion Notes

The external HyperFrames registry matched the existing local registry byte-for-byte during ingestion. Only missing vendor skill files were added to `.skills/`. This avoids duplicate block libraries and keeps the project from drifting across two HyperFrames copies.
