# 7_ASSETS — Asset Map (single source of truth for where things live)

Reorganized 2026-06-24. Every reusable input asset has ONE clear home. To add or
edit an asset, drop it in the right folder below — no hunting.

```
7_ASSETS/
├── brand/                 ← SEOSONA + CQA brand library (the ONLY place for brand)
│   ├── SEOSONA/           full brand kit (carousels, proposals, source images)
│   ├── logos/             *.png logos (Seosona_Logo.png, "Chi Quyet Academy Mascot Logo.png", ...)
│   ├── fonts/             *.ttf (BeVietnamPro-* used by the engine; Montserrat-* extra)
│   └── icons/             UI/brand icons (placeholder)
├── voice/                 ← ALL voice assets (one home; was models/refvoice/voice_profiles)
│   ├── models/            local TTS model files
│   ├── reference/         reference audio clips for cloning
│   └── profiles/          VieNeu clone references
│                          (default: seosona_ref13.wav — see system_config.yaml profiles.*.voice)
├── audio/                 ← music + sound effects
│   ├── bgm/               background music (*.mp3): bgm_tech_ambient/news/insight/upbeat
│   └── sfx/               sound effects (curated by manifest.json): transition/, impact/,
│                          ui/, typing/, riser/ (*.mp3)
└── templates/             ← JSON scene-structure templates (*.json) for native_composer
```

## Where to add / edit (quick reference)

| Want to add… | Put it in |
|--------------|-----------|
| A new voice / cloned profile | `7_ASSETS/voice/profiles/` |
| A reference audio for cloning | `7_ASSETS/voice/reference/` |
| A logo / font / icon | `7_ASSETS/brand/{logos,fonts,icons}/` |
| Background music / SFX | `7_ASSETS/audio/{bgm,sfx}/` |
| A reusable video template | `7_ASSETS/templates/` |

## NOT in 7_ASSETS (by design)
- **HyperFrames render engine + scene scaffolds** → `5_FRAMEWORK/` (that's framework
  CODE, not assets). `7_ASSETS/templates/` holds reusable *exported* templates; the
  engine that renders them lives in `5_FRAMEWORK/hf_engine` + `hf_core`.
- **Transient render outputs / analysis** → `8_WORKSPACE/_cache/` (srt_raw,
  video_analysis) — runtime data, gitignored, not reusable assets.
- **HyperFrames catalog blocks/components** → pulled on demand via
  `npx hyperframes add <name>` from `5_FRAMEWORK/hf_engine/registry/` / `hf_core/`.

## Naming conventions
- Lowercase, hyphen or snake_case; no spaces.
- Logos: `<Brand>_Logo.png`. Fonts: keep the foundry name (`BeVietnamPro-Bold.ttf`).
- Voice profiles: `<name>_<gender>_<region>.{wav,pt}` (e.g. `seosona_male_southern.wav`).

## Code references
Asset paths are read from `system_config.yaml` and `4_BRAIN/native_composer.py`
(via `_load_profile`). If you move a folder, update those + this map.
