# Voice and TTS Engine Routing

Created: 2026-06-19

This SOP maps external voice cloning and TTS repositories into SEOSONA Video without creating duplicate voice pipelines. All engines must route through the existing `tts_generator` and `voice_cloner` interfaces.

## Canonical Role Locks

| Layer | Canonical SEOSONA Video component | External repos allowed to influence it | Rule |
|---|---|---|---|
| Standard TTS | `2_SKILLS/tts_generator/tts_engine.py` | Edge-TTS, VieNeu-TTS, LuxTTS | Keep a simple standard TTS path for SEOSONA brand videos. |
| Voice cloning | `2_SKILLS/voice_cloner/fish_audio_api.py` | VieNeu-TTS, GPT-SoVITS, fish-speech, CosyVoice, OmniVoice | Add engines behind one adapter. Do not create engine-specific pipelines. |
| Subtitle timing | `4_BRAIN/pipeline_manager.py` | engines with word timestamps, forced alignment, script-derived fallback | Prefer native word timestamps; otherwise use verified script-derived fallback or ASR. |
| Long-form narration | future chunker under `2_SKILLS/tts_generator/` | ebook2audiobook, Coqui TTS | Extract chunking/retry/concat patterns, not full audiobook stack. |
| Voice cleanup | `2_SKILLS/audio_cleaner/` | voice-pro, Demucs patterns | Use only for owned or rights-cleared reference audio. |
| Voice dashboard | none yet | OmniVoice-Studio, voice-pro | Reference UI only. Do not embed full desktop/WebUI apps. |

## Engine Priority

### P0 - Target primary for Vietnamese

- `pnnbao97/VieNeu-TTS`: best project fit for Vietnamese TTS, instant cloning, CPU/on-device positioning, and SEOSONA/CQA brand needs.
- `edge-tts`: operational fallback already verified by smoke test. Keep it available even after VieNeu integration.

### P1 - Conditional high-value engines

- `RVC-Boss/GPT-SoVITS`: strong few-shot clone candidate for CQA voice once a clean reference set exists.
- `fishaudio/fish-speech`: modern open-source TTS candidate for high-quality synthesis if model/runtime requirements are acceptable.
- `FunAudioLLM/CosyVoice`: strong multilingual/controllable TTS candidate, but heavier runtime and likely GPU-oriented.
- `k2-fsa/OmniVoice`: strong multilingual fallback and voice-design candidate; evaluate install/runtime footprint before enabling.
- `abus-aikorea/voice-pro`: useful architecture reference for a creator-grade stack combining TTS, cloning, Whisper, Demucs, and translation.

### P2 - Reference-only or specialized

- `ysharma3501/LuxTTS`: keep as speed-focused TTS reference until quality/runtime are verified locally.
- `DrewThomasson/ebook2audiobook`: extract chunking, long-text normalization, resume/retry, and audiobook concatenation patterns.
- `debpalash/OmniVoice-Studio`: UI reference for future voice profile management.
- `coqui-ai/TTS`: XTTS lineage and API reference, but not a primary target because active maintenance is weaker than newer alternatives.

### P3 - Legacy or overbroad

- `CorentinJ/Real-Time-Voice-Cloning`: educational SV2TTS reference only. Do not use as production engine.
- `PaddlePaddle/PaddleSpeech`: broad enterprise speech toolkit; useful for research, overlarge for the short-video runtime.

## Adapter Contract

Every enabled engine must expose the same return shape:

```python
{
  "audio_path": "path/to/voice.wav",
  "word_timestamps": [
    {"word": "Xin", "start": 0.08, "end": 0.42}
  ],
  "engine": "vieneu",
  "sample_rate": 48000,
  "warnings": []
}
```

## Routing Rules

1. For SEOSONA brand videos, use standard Vietnamese TTS unless a task explicitly requests a cloned voice.
2. For CQA videos, prefer a cloned or brand-matched voice when a rights-cleared reference sample exists.
3. Prefer VieNeu-TTS for Vietnamese if installed and healthy.
4. Keep Edge-TTS as the fallback engine because it is currently verified in the local pipeline.
5. Never install or import heavyweight engines directly inside the main video runtime. Use isolated adapters and explicit health checks.
6. Use native word timestamps when an engine provides them.
7. If no native timestamps exist, use script-derived fallback for generated TTS; use ASR only when audio content is not generated from the known script.
8. Store only rights-cleared voice references under `7_ASSETS/voice/profiles/`.
9. Never clone a voice from third-party media without explicit permission.

## Recommended Next Work

| Adapter | Source inspiration | Target area | Purpose |
|---|---|---|---|
| `vieneu_engine.py` | VieNeu-TTS | `2_SKILLS/voice_cloner/` | Primary Vietnamese TTS/cloning adapter with Edge fallback. |
| `voice_engine_router.py` | voice-pro, GPT-SoVITS, CosyVoice, OmniVoice | `2_SKILLS/voice_cloner/` | One router that checks installed engines and dispatches safely. |
| `long_text_tts_chunker.py` | ebook2audiobook, Coqui TTS | `2_SKILLS/tts_generator/` | Split, synthesize, validate, and concatenate long scripts. |
| `voice_reference_cleaner.py` | voice-pro, Demucs | `2_SKILLS/audio_cleaner/` | Clean owned reference audio before cloning. |

## Validation Checklist

- Run current pipeline smoke test after any voice engine change.
- Confirm output has both video and audio streams with FFprobe.
- Confirm generated SRT preserves the source script when using generated TTS.
- Keep all engine-specific dependencies optional.
- Do not store API keys, personal voice samples, or machine-specific paths in docs or logs.
