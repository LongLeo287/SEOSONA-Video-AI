# SOP: Voice Cloning & TTS Pipeline

## Overview

End-to-end procedure for generating branded voice audio from text scripts.
**OmniVoice (k2-fsa) is the ONLY voice engine** (user decision 2026-07-14) — local, Vietnamese-native
(8482h), zero-shot + CQA voice clone, cloning the Chí Quyết (CQA) voice as THE brand voice for BOTH
brands. There is **NO backup engine**: a failed synth returns `None` honestly (no silent fallback).
License note: OmniVoice code is Apache-2.0 but the WEIGHTS are CC-BY-NC — owner-accepted risk,
recorded in `voice_router.py` + `0_SETUP/MODELS.md`.

## Voice Profiles

| Brand | Engine | Voice Character |
|:------|:-------|:----------------|
| SEOSONA | OmniVoice — CQA clone | the Chí Quyết brand voice |
| CQA | OmniVoice — CQA clone | the Chí Quyết brand voice |

## Engine

ONE engine is wired through `2_SKILLS/voice_cloner/voice_router.py` — this is the single source of
truth (policy 2026-07-14). VieNeu / F5-TTS / edge-tts / kokoro / sherpa / LoRA / CosyVoice /
Fish-Audio were evaluated and **removed** (code + pip + model caches; no dead branches); their
knowledge cards remain in `2_KNOWLEDGE/` for reference only. See `VOICE_TTS_ENGINE_ROUTING.md`.

| Engine | Install | GPU? | Voice Clone? | Quality |
|:-------|:--------|:-----|:-------------|:--------|
| OmniVoice (k2-fsa) | isolated torch-2.8 venv at `7_ASSETS/voice/.venv-omnivoice` | Yes (RTX 3060) | yes — zero-shot + the CQA clone | 48kHz, VN-native, gap-trimmed + loudnorm |

## Pipeline Flow

```
Script Text
  |
[1] Brand Detection -> system_config.yaml -> select engine
  |
[2] OODA Loop Check -> If script segment is too long, EditorAgent trims/rewrites before passing to TTS
  |
[3] OmniVoice available (isolated venv reachable)?
      YES -> OmniVoice clones the CQA brand voice
      NO  -> synth returns None honestly (NO backup engine); the pipeline fails loudly
  |
[3] Output: voice.mp3 (48kHz mono)
  |
[4] (Optional) Mix with BGM — handled by 4_BRAIN/native_composer.py (ffmpeg: BGM sidechain-duck + SFX + loudnorm)
      -> Volume ducking: voice at 1.0, BGM at 0.08-0.12
      -> Fade-in 1s, Fade-out 2s
  |
[5] Output: mixed_audio.mp3 -> passed to renderer
```

## TTS Text Handling

### Code-Switching (En-Vi)
News-video code-switching is handled before TTS by `4_BRAIN/news_video_standards.py`.
The visible script and subtitles keep correct spelling such as `AI`, `SEO`, `GitHub`, and `Obscura`; the TTS input receives a separate Vietnamese pronunciation string.

### Usage
Always synthesize through the router (never call an engine module directly):
```python
from voice_router import synthesize_voice  # 2_SKILLS/voice_cloner/voice_router.py

path = synthesize_voice("Text here", "voice.mp3", brand="seosona")
# path is None if OmniVoice can't run — handle it; there is NO backup engine.
```

## Voice Sample Requirements

| Spec | Value |
|:-----|:------|
| Format | WAV, PCM 16-bit signed, mono |
| Sample Rate | 22050 Hz |
| Duration | 3-60 seconds |
| Content | Clean speech, no background music/noise |
| Extraction | `ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 22050 -ac 1 output.wav` |

## Adding a New Voice

1. Extract clean audio from video:
   ```bash
   ffmpeg -ss 30 -t 30 -i "source_video.mp4" -vn -acodec pcm_s16le -ar 22050 -ac 1 "7_ASSETS/voice_profiles/{name}_sample_30s.wav"
   ```

2. Add config in `system_config.yaml`:
   ```yaml
   voice:
     engine: "omnivoice"
     model: "{name}_clone_v1"
     required_gender: "male"
     required_accent: "southern"
     reference_audio: "7_ASSETS/voice_profiles/{name}_sample_30s.wav"
     # No fallback engine — OmniVoice is the only engine (2026-07-14); a failed synth returns None.
   ```

3. Test:
   ```bash
   node scripts/seosona-python.cjs -m py_compile 2_SKILLS/voice_cloner/voice_router.py
   ```

## Quality Checklist

- [ ] Voice sounds natural with proper Vietnamese tone/intonation
- [ ] Voice is male and matches the approved Southern Vietnamese target profile
- [ ] English/technical terms are spelled correctly on screen and pronounced via the lexicon
- [ ] No robotic artifacts or glitches
- [ ] Pacing matches video timing (not too fast/slow)
- [ ] BGM volume does not overpower voice
- [ ] Audio file is properly formatted (mono, correct sample rate)
