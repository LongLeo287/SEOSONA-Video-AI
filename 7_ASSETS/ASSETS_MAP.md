# 7_ASSETS — Asset Map (single source of truth for where things live)

Reorganized 2026-06-24. Every reusable input asset has ONE clear home. To add or
edit an asset, drop it in the right folder below — no hunting.

```
7_ASSETS/
├── brand/                 ← SEOSONA brand library (the ONLY place for brand)
│   ├── SEOSONA/           full brand kit
│   ├── logos/             *.png logos (Seosona_Logo.png, CQA_Logo.png, ...)
│   ├── fonts/             *.ttf/*.otf (BeVietnamPro-*, Montserrat-*, ...)
│   ├── icons/             UI/brand icons
│   └── colors/            palette / color tokens (add here)
├── voice/                 ← ALL voice assets (one home; was models/refvoice/voice_profiles)
│   ├── models/            local TTS model files
│   ├── reference/         reference audio clips for cloning
│   └── profiles/          approved voice profiles + omnivoice-vi voice.pt profiles
│                          (e.g. seosona_male_southern.wav — the default voice target)
├── audio/                 ← music + sound effects
│   ├── bgm/               background music (*.mp3)
│   └── sfx/               sound effects — sfx/pops/, sfx/transitions/ (*.wav)
└── templates/             ← reusable VIDEO templates (exported HyperFrames projects)
```

## Where to add / edit (quick reference)

| Want to add… | Put it in |
|--------------|-----------|
| A new voice / cloned profile | `7_ASSETS/voice/profiles/` |
| A reference audio for cloning | `7_ASSETS/voice/reference/` |
| A logo / font / icon / brand color | `7_ASSETS/brand/{logos,fonts,icons,colors}/` |
| Background music / SFX | `7_ASSETS/audio/{bgm,sfx}/` |
| A reusable video template | `7_ASSETS/templates/` |

## NOT in 7_ASSETS (by design)
- **HyperFrames render engine + scene scaffolds** → `5_FRAMEWORK/` (that's framework
  CODE, not assets). `7_ASSETS/templates/` holds reusable *exported* templates; the
  engine that renders them lives in `5_FRAMEWORK/hf_engine` + `hf_core`.
- **Transient render outputs / analysis** → `8_WORKSPACE/_cache/` (srt_raw,
  video_analysis) — runtime data, gitignored, not reusable assets.
- **HyperFrames catalog blocks/components** → pulled on demand via
  `pipeline_manager.add_catalog_block()` from `5_FRAMEWORK/hf_engine/registry/`.

## Naming conventions
- Lowercase, hyphen or snake_case; no spaces.
- Logos: `<Brand>_Logo.png`. Fonts: keep the foundry name (`BeVietnamPro-Bold.ttf`).
- Voice profiles: `<name>_<gender>_<region>.{wav,pt}` (e.g. `seosona_male_southern.wav`).

## Code references
Asset paths are read from `system_config.yaml` and `4_BRAIN/pipeline_manager.py`.
If you move a folder, update those + this map.
