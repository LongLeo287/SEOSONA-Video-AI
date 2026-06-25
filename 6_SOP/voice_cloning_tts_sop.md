# SOP: Voice Cloning & TTS Pipeline

## Overview

End-to-end procedure for generating branded voice audio from text scripts.
VieNeu-TTS is the primary engine — designed specifically for Vietnamese with natural prosody, emotion cues, and instant voice cloning.

## Voice Profiles

| Brand | Engine (Primary) | Fallback | Voice Character |
|:------|:----------------|:---------|:----------------|
| SEOSONA | VieNeu-TTS approved male Southern reference/preset | Edge-TTS (`vi-VN-NamMinhNeural`) | Male, Southern Vietnamese target, professional, authoritative |
| CQA | VieNeu-TTS approved male Southern reference/preset | Edge-TTS (`vi-VN-NamMinhNeural`) | Male, Southern Vietnamese target, energetic, approachable |

## Engine Priority

Only two engines are wired through `2_SKILLS/voice_cloner/voice_router.py` — this is the
single source of truth. F5-TTS / OmniVoice / CosyVoice / Fish-Audio were evaluated and
**removed** (no dead branches); their knowledge cards remain in `2_KNOWLEDGE/repos/` for
reference only. See `VOICE_TTS_ENGINE_ROUTING.md`.

| Priority | Engine | Install | GPU? | Voice Clone? | Quality |
|:---------|:-------|:--------|:-----|:-------------|:--------|
| 1 (primary) | VieNeu-TTS v3 Turbo | `pip install vieneu` | No (CPU/ONNX) | 3-5s reference | 48kHz, natural tone, emotion cues |
| 2 (fallback) | Edge-TTS | `pip install edge-tts` | No | No | Pre-built voice `vi-VN-NamMinhNeural` (Northern — honest fallback, NOT the brand voice) |

## Pipeline Flow

```
Script Text
  |
[1] Brand Detection -> system_config.yaml -> select engine
  |
[2] OODA Loop Check -> If script segment is too long, EditorAgent trims/rewrites before passing to TTS
  |
[3] VieNeu-TTS available + reference/preset configured?
      YES -> Clone (reference) or preset mode
      NO  -> Edge-TTS honest fallback (`vi-VN-NamMinhNeural`), logged loudly
  |
[3] Output: voice.mp3 (48kHz mono)
  |
[4] (Optional) Mix with BGM via 5_FRAMEWORK/moviepy_wrapper/audio_mixer.py
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
