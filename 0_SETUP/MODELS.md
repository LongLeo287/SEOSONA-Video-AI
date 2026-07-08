# 0_SETUP — Model registry (what voice/ASR models the system uses, where, how to fetch)

Models are NOT in git (too big). They live either in-project (`7_ASSETS/models`) or in the shared
HuggingFace cache (`~/.cache/huggingface/hub`). Most auto-download on first use; pre-fetch below.

## Active models
| Model | Role | Where | Size | Fetch |
|-------|------|-------|------|-------|
| **k2-fsa/OmniVoice** | BRAND VOICE (primary, GPU) | HF cache | 3.1 GB | auto on first synth, or `huggingface-cli download k2-fsa/OmniVoice` |
| **pnnbao-ump/VieNeu-TTS-v3-Turbo** | backup voice | HF cache | 935 MB | auto (vieneu pkg), or `huggingface-cli download pnnbao-ump/VieNeu-TTS-v3-Turbo` |
| **PhoWhisper-medium CT2** | Vietnamese ASR (caption sync) | `7_ASSETS/models/phowhisper-medium-ct2` | 740 MB | `ct2-transformers-converter --model vinai/PhoWhisper-medium --output_dir 7_ASSETS/models/phowhisper-medium-ct2 --quantization int8` |
| **CQA brand-voice reference** | the voice OmniVoice clones | `7_ASSETS/voice/profiles/cqa_omnivoice_ref.wav` (+`.txt`) | small | ships in repo (or re-clean a CQA clip — see voice_router/omnivoice_engine) |

## Reclaimed 2026-06-30 (deleted — re-download only if ever needed)
- `models--kiendt--PhoWhisper-large-ct2` (2.9 GB) — old ASR, replaced by the in-project medium CT2. DELETED.
- `models--vinai--PhoWhisper-medium` (2.9 GB) — only the conversion source for the CT2 (kept). DELETED.
- `.venv-train` (LoRA training venv) — obsolete after LoRA removal. Already gone.
Total reclaimed ≈ 5.8 GB. If a fresh machine needs them: `huggingface-cli download vinai/PhoWhisper-medium`
then re-run the ct2 converter (only required to rebuild the CT2 — not needed if `7_ASSETS/models/phowhisper-medium-ct2` is present).

## Removed engines (do NOT re-add — see voice-clone-reference memory)
F5-TTS (model + f5-vietnamese + HF cache), edge-tts, Chí Quyết LoRA adapter — all deleted 2026-06-30.
Voice = OmniVoice (primary) + VieNeu (backup) only.

## Pre-fetch everything (optional, before first render)
```powershell
python -m pip install -U "huggingface_hub[cli]"
huggingface-cli download k2-fsa/OmniVoice
huggingface-cli download pnnbao-ump/VieNeu-TTS-v3-Turbo
# PhoWhisper CT2: see the ct2-transformers-converter command above
```
