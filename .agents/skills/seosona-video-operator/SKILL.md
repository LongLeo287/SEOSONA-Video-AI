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
**This is the MAIN / master entry** — it routes to the right engine + workflow skill below.

## Two video engines (pick by input)

| Engine | Input | Output | Voice | Entry skill / command |
|---|---|---|---|---|
| **Synthesized** (`4_BRAIN/video_engine.py` → `native_composer.py`) | text / GitHub repo / website / news brief | build scenes from JSON template (9:16 + 16:9) | AI (VieNeu) | `/seosona-news-maker`, `/faceless-explainer`, `/pr-to-video`, `/product-launch-video`, `/website-to-video`, `/general-video` + `/scene-composer` (compose content). Commands: `npm run make:video` / `video:news` |
| **Footage** (`scripts/talking_head_*`) | self-shot video / screen-rec | edit + karaoke caption + card (9:16 + 16:9) | REAL voice | `/talking-head-video-editor`. Commands: `npm run talkinghead:transcribe` → `talkinghead:edit` |

Edit/overlay an existing video: `/embedded-captions`, `/graphic-overlays`. Avatar (paid, future): `/heygen-native-api`.

## Operating Contract

1. Source language in scripts, subtitles, scene copy, and thumbnails is Vietnamese.
2. English technical terms stay visually correct in display text.
3. Pronunciation is handled through the lexicon in `4_BRAIN/news_video_standards.py`, not by writing phonetics into display text.
4. Default news voice target is male Southern Vietnamese. The fallback voice is `vi-VN-NamMinhNeural`; true approved-clone output requires `7_ASSETS/voice/profiles/seosona_ref13.wav` or an approved VieNeu preset.
   - **All voice goes through ONE path:** `2_SKILLS/voice_cloner/voice_router.py` (`synthesize_voice`) → **VieNeu (clone > preset)**, with an honest edge-tts fallback that logs loudly that it is the Northern non-brand voice. Engines are: SEOSONA → VieNeu clone of the Southern reference; CQA → VieNeu clone of the expert reference (config in `system_config.yaml`). VieNeu is the only engine — there is no fish_audio/F5/OmniVoice/Kokoro path (removed). Never add a dead `if engine==…` branch; add a real probe.
5. Production outputs must include voice, background music, SFX/transitions, subtitles, thumbnail, and a production manifest.
6. HyperFrames is the canonical renderer. MoviePy/FFmpeg are fallback or muxing tools, not the primary template authoring model.

## HyperFrames — Resources & How To Use (READ THIS to build/render)

HyperFrames is the core engine. Everything you need is already in this repo — use it, don't reinvent HTML by hand.

**1. Agent skills (slash commands in `.agents/skills/`)** — invoke these to author compositions:
- `/hyperframes` — entry router ("make me a video" → picks the workflow)
- `/hyperframes-core` — HTML structure, clips, tracks, data attributes
- `/hyperframes-animation` — GSAP/Lottie/Three/CSS timeline authoring
- `/hyperframes-cli` — init/preview/render/lint/doctor
- `/hyperframes-creative` — design direction, palettes, typography, beats
- `/hyperframes-media` — TTS, transcription, background removal
- `/hyperframes-registry` — install catalog blocks/components
- Workflow skills: `/seosona-news-maker`, `/talking-head-video-editor`, `/scene-composer`, `/general-video`, `/faceless-explainer`, `/embedded-captions`, `/graphic-overlays`, `/motion-graphics`, `/product-launch-video`, `/website-to-video`, `/pr-to-video`

**2. Knowledge base — `2_KNOWLEDGE/hyperframes/`** (read for API/rules/specs):
- `guides/` — quickstart, GSAP contract, rendering/4K/HDR, the 7-step pipeline, prompting, common mistakes
- `reference/` — HTML schema, package APIs (core/cli/engine, producer/player/sdk, shader-transitions), cloud scale
- `catalog/CATALOG_INDEX.md` — all 122 blocks+components; `TRANSITIONS.md`; `CAPTIONS.md`
- Start at `2_KNOWLEDGE/hyperframes/README.md`.

**3. Catalog — pull ready-made blocks instead of hand-coding:**
```bash
npx hyperframes add <block-name>   # e.g. whip-pan, cinematic-zoom, caption-pill-karaoke, code-typing, us-map
```
Browse names + categories in `2_KNOWLEDGE/hyperframes/catalog/CATALOG_INDEX.md`. Transitions → `TRANSITIONS.md`; word-timed captions → `CAPTIONS.md`. Source HTML lives in `5_FRAMEWORK/hf_engine/registry/{blocks,components}/`.

**4. Render** — the pipeline (`4_BRAIN/video_engine.py` → `native_composer.py`) renders via the local `hyperframes` binary (no npx network). Tunables via env: `SEOSONA_HF_VERSION` (default 0.7.4), `SEOSONA_HF_QUALITY/FPS/RESOLUTION`, `SEOSONA_HF_TRANSITIONS=1`, `SEOSONA_HF_PRODUCER=1` (Producer API, streaming progress). Decisions + recipes: `6_SOP/RENDER_ENGINE_DECISION.md`.

**Workflow:** intent → `/hyperframes` (or a workflow skill) → consult `2_KNOWLEDGE/hyperframes/` for the schema → pull catalog blocks/transitions/captions with `npx hyperframes add` → assemble composition → render. Don't hand-write what the catalog already provides.

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

The pipeline routes through `4_BRAIN/workflow_router.py`, `4_BRAIN/video_engine.py` → `native_composer.py`, `4_BRAIN/news_video_standards.py`, and the HyperFrames templates under `5_FRAMEWORK/`.

## Localize / Dub A Foreign Video

Translate + dub a source video into the SEOSONA brand voice (e.g. English → Vietnamese):

```python
from repurposer_agent import localize_video
localize_video("input_en.mp4", src_lang="en", tgt_lang="vi", brand="seosona")
# -> { srt: translated .srt, audio: brand-voiced dubbed .wav, segments: N }
```

Chain (all switchable routers, graceful fallback): ASR (`SEOSONA_ASR`, PhoWhisper primary)
→ translate (`SEOSONA_TRANSLATOR`, LLM primary / Google backup, keeps EN tech terms)
→ VieNeu brand-voice dub, time-fit to the source timing. CLI:
`python 1_AGENTS/repurposer_agent/localizer.py input.mp4 --src en --tgt vi`.

## Export A Reusable Template

After a successful render, export the render project into the template registry.
Templates are JSON in `7_ASSETS/templates/`, extracted via `native_composer.extract_template`
(the old `video_template_factory` is retired (removed)):

```python
from native_composer import extract_template

extract_template(
    "8_WORKSPACE/PROJECT_NAME",
    "Project Name Template",
    out_root="7_ASSETS/templates",
)
```

The exported template preserves layout, motion, sample subtitle, thumbnail, and production metadata. It is intended for cloning a visual style while replacing script and voice in future runs.

## Required Verification

Run:

```bash
python -m pytest tests/ -q
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
