# SOP: Voice Cloning & TTS Pipeline

## Overview

End-to-end procedure for generating branded voice audio from text scripts.
VieNeu-TTS is the primary engine — designed specifically for Vietnamese with natural prosody, emotion cues, and instant voice cloning.

## Voice Profiles

| Brand | Engine (Primary) | Fallback | Voice Character |
|:------|:----------------|:---------|:----------------|
| SEOSONA | VieNeu-TTS (built-in voice) | Edge-TTS (`vi-VN-HoaiMyNeural`) | Female, professional, authoritative |
| CQA | VieNeu-TTS (clone from sample) | Edge-TTS (`vi-VN-NamMinhNeural`) | Male (Chi Quyet), energetic, approachable |

## Engine Priority

| Priority | Engine | Install | GPU? | Voice Clone? | Quality |
|:---------|:-------|:--------|:-----|:-------------|:--------|
| 1 | VieNeu-TTS v3 Turbo | `pip install vieneu` | No (CPU/ONNX) | 3-5s reference | 48kHz, natural tone, emotion cues |
| 2 | OmniVoice (k2-fsa) | See github.com/k2-fsa/OmniVoice | Recommended | Yes | 600+ languages |
| 3 | CosyVoice3 | See github.com/FunAudioLLM/CosyVoice | Yes | Yes | Good multilingual |
| 4 | Edge-TTS (fallback) | `pip install edge-tts` | No | No | Pre-built voices only |

## Pipeline Flow

```
Script Text
  |
[1] Brand Detection -> system_config.yaml -> select engine
  |
[2] VieNeu-TTS available?
      YES -> Clone mode (CQA: ref_audio) or Default voice (SEOSONA)
      NO  -> Try OmniVoice -> CosyVoice -> Edge-TTS
  |
[3] Output: voice.mp3 (48kHz mono)
  |
[4] (Optional) Mix with BGM via audio_mixer.py
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
VieNeu-TTS handles English words in Vietnamese text natively via `sea-g2p` phonemizer.
No special markup needed — "SEO", "Google", "Content Marketing" are pronounced correctly.

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
     reference_audio: "7_ASSETS/voice_profiles/{name}_sample_30s.wav"
     fallback_engine: "edge-tts"
     fallback_voice: "vi-VN-HoaiMyNeural"
   ```

3. Test:
   ```bash
   python 2_SKILLS/voice_cloner/fish_audio_api.py
   ```

## Quality Checklist

- [ ] Voice sounds natural with proper Vietnamese tone/intonation
- [ ] Emotion cues render correctly (if used)
- [ ] English words (SEO, Google, etc.) are pronounced correctly
- [ ] No robotic artifacts or glitches
- [ ] Pacing matches video timing (not too fast/slow)
- [ ] BGM volume does not overpower voice
- [ ] Audio file is properly formatted (mono, correct sample rate)
