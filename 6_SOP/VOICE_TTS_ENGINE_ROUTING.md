# Voice and TTS Engine Routing

Created: 2026-06-19

This SOP maps external voice cloning and TTS repositories into SEOSONA Video without creating duplicate voice pipelines. All engines must route through the existing `voice_cloner` / `voice_router` interface (the old separate `tts_generator` was folded into the single router).

> **ASR (speech→subtitles) — switchable router, added 2026-06-24.**
> `2_SKILLS/srt_maker/asr_router.py` mirrors the voice router: a primary ASR engine with
> automatic backups. **PhoWhisper (VinAI, Vietnamese-specialised) is primary**, falling
> back to faster-whisper → openai-whisper. Switch instantly with `SEOSONA_ASR=faster_whisper`.
> Tunables: `SEOSONA_PHOWHISPER_MODEL` (CT2 repo, default `kiendt/PhoWhisper-large-ct2`),
> `SEOSONA_WHISPER_SIZE`, `SEOSONA_ASR_DEVICE=cpu|cuda`. Same word-timestamp output shape for
> every engine, so the pipeline (STEP 2 alignment + repurpose SRT) never changes. VideoLingo's
> single-line semantic subtitle cutting = `group_words_to_segments`.
>
> **CURRENT POLICY (2026-06-29, supersedes the 2026-06-24 rebuild below).** A single router
> (`2_SKILLS/voice_cloner/voice_router.py`) routes **OmniVoice (PRIMARY — k2-fsa, local, Apache-2.0,
> VN-native, cloning the Chí Quyết voice for BOTH brands) → VieNeu (BACKUP, only when OmniVoice can't
> run)**. ALL other engines are REMOVED: F5-TTS, edge-tts, LoRA, fish/cosyvoice/kokoro, the old
> `fish_audio_api.py` router. OmniVoice + VieNeu are the only two paths. Adding another engine = new
> file + a probe branch in `voice_router.py` (never a dead `if engine == …` that silently falls through).

## Canonical Role Locks

| Layer | Canonical SEOSONA Video component | External repos allowed to influence it | Rule |
|---|---|---|---|
| Standard TTS | `2_SKILLS/voice_cloner/voice_router.py` (unified — no separate tts_generator) | OmniVoice, VieNeu | Keep a simple standard TTS path for SEOSONA brand videos. |
| Voice routing | `2_SKILLS/voice_cloner/voice_router.py` | OmniVoice (primary), VieNeu (backup) | Single router. **OmniVoice primary → VieNeu backup**. No dead branches; edge-tts/F5/LoRA/fish removed. |
| Subtitle timing | `4_BRAIN/native_composer.py` (RULE #1 captions via `asr_router`) | engines with word timestamps, forced alignment, script-derived fallback | Prefer native word timestamps; otherwise use verified script-derived fallback or ASR. |
| Long-form narration | future chunker under `2_SKILLS/voice_cloner/` | ebook2audiobook, Coqui TTS | Extract chunking/retry/concat patterns, not full audiobook stack. |
| Voice cleanup | _(quarantined: (removed))_ | voice-pro, Demucs patterns | Not wired. Restore only if a cleanup step is actually needed; use only for owned/rights-cleared audio. |
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

| Adapter | Source inspiration | Target area | Purpose | Status |
|---|---|---|---|---|
| `omnivoice_engine.py` | k2-fsa/OmniVoice | `2_SKILLS/voice_cloner/` | PRIMARY: clones the CQA brand voice (isolated torch-2.8 venv). | ✅ DONE |
| `vieneu_engine.py` | VieNeu-TTS | `2_SKILLS/voice_cloner/` | BACKUP adapter, used only when OmniVoice can't run. | ✅ DONE |
| `voice_router.py` | — | `2_SKILLS/voice_cloner/` | Single router: **OmniVoice primary → VieNeu backup**. No dead branches; edge-tts/F5/LoRA/fish removed. | ✅ DONE |
| `long_text_tts_chunker.py` | ebook2audiobook, Coqui TTS | `2_SKILLS/voice_cloner/` | Split, synthesize, validate, and concatenate long scripts. | ⬜ Future |
| `voice_reference_cleaner.py` | voice-pro, Demucs | (was `audio_cleaner`, now quarantined) | Clean owned reference audio before cloning — only if a real need arises. | ⬜ Deferred |

## Validation Checklist

- Run current pipeline smoke test after any voice engine change.
- Confirm output has both video and audio streams with FFprobe.
- Confirm generated SRT preserves the source script when using generated TTS.
- Keep all engine-specific dependencies optional.
- Do not store API keys, personal voice samples, or machine-specific paths in docs or logs.
