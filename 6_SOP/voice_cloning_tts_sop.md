# SOP: Voice Cloning & TTS Pipeline

## Overview

End-to-end procedure for generating branded voice audio from text scripts.
**OmniVoice (k2-fsa) is the primary engine** — local, Apache-2.0, Vietnamese-native (8482h), cloning the
Chí Quyết (CQA) voice as THE brand voice for BOTH brands. VieNeu is the backup.

## Voice Profiles

| Brand | Engine (Primary) | Backup | Voice Character |
|:------|:----------------|:---------|:----------------|
| SEOSONA | OmniVoice — CQA clone | VieNeu (preset, only if OmniVoice can't run) | the Chí Quyết brand voice |
| CQA | OmniVoice — CQA clone | VieNeu | the Chí Quyết brand voice |

## Engine Priority

Only two engines are wired through `2_SKILLS/voice_cloner/voice_router.py` — this is the
single source of truth (policy 2026-06-29). **OmniVoice PRIMARY → VieNeu BACKUP**. F5-TTS / edge-tts /
LoRA / CosyVoice / Fish-Audio / Kokoro were evaluated and **removed** (no dead branches); their knowledge
cards remain in `2_KNOWLEDGE/` for reference only. See `VOICE_TTS_ENGINE_ROUTING.md`.

| Priority | Engine | Install | GPU? | Voice Clone? | Quality |
|:---------|:-------|:--------|:-----|:-------------|:--------|
| 1 (primary) | OmniVoice (k2-fsa) | isolated torch-2.8 venv | Yes (RTX 3060) | yes — the CQA clone | 48kHz, VN-native, gap-trimmed + loudnorm |
| 2 (backup) | VieNeu-TTS | `pip install vieneu` | No (CPU/ONNX) | preset "Gia Bảo" | used ONLY when OmniVoice can't run |

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
      NO  -> VieNeu backup (preset "Gia Bảo"), logged loudly
  |
[3] Output: voice.mp3 (48kHz mono)
  |
[4] (Optional) Mix with BGM — handled by 4_BRAIN/native_composer.py (ffmpeg: BGM sidechain-duck + SFX + loudnorm)
      -> Volume ducking: voice at 1.0, BGM at 0.08-0.12
      -> Fade-in 1s, Fade-out 2s
  |
[5] Output: mixed_audio.mp3 -> passed to renderer
```

## VieNeu-TTS Features

### Emotion Cues (Experimental)
Insert directly into script text:
- `[cuoi]` — Laughing
- `[tho dai]` — Sighing
- `[hang giong]` — Clearing throat

### Code-Switching (En-Vi)
News-video code-switching is handled before TTS by `4_BRAIN/news_video_standards.py`.
The visible script and subtitles keep correct spelling such as `AI`, `SEO`, `GitHub`, and `Obscura`; the TTS input receives a separate Vietnamese pronunciation string.

### SDK Usage
```python
from vieneu import Vieneu
tts = Vieneu()

# Default voice
audio = tts.infer("Text here")
tts.save(audio, "output.wav")

# Voice cloning
audio = tts.infer("Text", ref_audio="chiquyet_sample_30s.wav")

# Emotion cues
audio = tts.infer("[cuoi] Noi dung vui ve [hang giong] tiep tuc...")
```

## Voice Sample Requirements

| Spec | Value |
|:-----|:------|
| Format | WAV, PCM 16-bit signed, mono |
| Sample Rate | 22050 Hz |
| Duration | 3-60 seconds (VieNeu: 3-5s minimum) |
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
     engine: "vieneu"
     model: "{name}_clone_v1"
     required_gender: "male"
     required_accent: "southern"
     reference_audio: "7_ASSETS/voice_profiles/{name}_sample_30s.wav"
     fallback_engine: "edge-tts"
     fallback_voice: "vi-VN-NamMinhNeural"
   ```

3. Test:
   ```bash
   node scripts/seosona-python.cjs -m py_compile 2_SKILLS/voice_cloner/voice_router.py
   ```

## Quality Checklist

- [ ] Voice sounds natural with proper Vietnamese tone/intonation
- [ ] Voice is male and matches the approved Southern Vietnamese target profile
- [ ] Emotion cues render correctly (if used)
- [ ] English/technical terms are spelled correctly on screen and pronounced via the lexicon
- [ ] No robotic artifacts or glitches
- [ ] Pacing matches video timing (not too fast/slow)
- [ ] BGM volume does not overpower voice
- [ ] Audio file is properly formatted (mono, correct sample rate)
