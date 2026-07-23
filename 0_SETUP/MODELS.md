# 0_SETUP — Model registry (what voice/ASR models the system uses, where, how to fetch)

Models are NOT in git (too big). They live in the shared HuggingFace cache
(`~/.cache/huggingface/hub`). Most auto-download on first use; pre-fetch below.

## Active models
| Model | Role | Where | Size | Fetch |
|-------|------|-------|------|-------|
| **k2-fsa/OmniVoice** | BRAND VOICE (the ONLY voice engine, GPU) | HF cache | 3.1 GB | auto on first synth, or `huggingface-cli download k2-fsa/OmniVoice` |
| **kiendt/PhoWhisper-large-ct2** | Vietnamese ASR — the ONLY ASR model (caption sync) | HF cache | 3.1 GB | auto on first transcribe, or `huggingface-cli download kiendt/PhoWhisper-large-ct2` |
| **CQA brand-voice reference** | the voice OmniVoice clones | `7_ASSETS/voice/profiles/cqa_omnivoice_ref.wav` (+`.txt`) | small | ships in repo (or re-clean a CQA clip — see voice_router/omnivoice_engine) |

LICENSE NOTE: OmniVoice weights are CC-BY-NC (model card) — owner-accepted risk (2026-07-14
decision, benchmark evidence in `8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md`).

## Deleted 2026-07-14 (engine consolidation — do NOT restore / re-add)
Voice = OmniVoice ONLY (user decision; no backup engine, no stored alternatives):
- `7_ASSETS/models/phowhisper-medium-ct2` (int8 CT2) — PROVEN DEFECTIVE in the Phase-0 benchmark
  (repetition-loop hallucinations + collapse on a 40s clip; VAD does not fix it). DELETED;
  PhoWhisper-large-ct2 replaces it (WER 0.041 vs 0.702 on the gold set).
- VieNeu (engine file, `vieneu` pip pkg, HF caches v0.3B + v3-Turbo + neucodec + MOSS tokenizers),
  F5-TTS Vietnamese caches (hynt + yukiakai + vocos), sherpa-onnx ASR, openai-whisper ASR path,
  `download_local_models.py`, wav2vec2-base-vi-vlsp2020 (NC-licensed WhisperX aligner, unused).
- Final sweep (same day): `kokoro` pip pkg + its G2P deps (misaki/espeakng-loader/phonemizer),
  the stale kokoro auto-download in `seosona_doctor.py` (now checks OmniVoice instead), orphan
  `vn_text_frontend.py` (duplicate of VietNormalizer, 0 callers), `setup_vieneu_env.ps1`, and
  unused ASR caches `whisper-large-v3-turbo` + `faster-whisper-small` (≈2 GB more).
  ≈7 GB reclaimed total. Earlier removals (2026-06-30): F5-TTS engine, edge-tts, Chí Quyết LoRA.
Kept deliberately: `eustlb/higgs-audio-v2-tokenizer` + `facebook/w2v-bert-2.0` (OmniVoice fine-tune
token encoding). NOTE: a 2.4 MB `models--openai--whisper-tiny` cache entry (tokenizer.json only)
auto-recreates on first transcribe — it is faster-whisper's tokenizer dependency for the CT2 model,
NOT the whisper-tiny model; leave it.

## Deleted 2026-07-14 (third wave — local GenVideo removed, user decision)
LTX-Video local lane: `Lightricks/LTX-Video` (17.7 GB) + `LTX-Video-0.9.5` (5.9 GB) caches,
`scripts/ltx_video.py`, the `local` adapter in seedance_engine, `ltx.ready` marker. Engine #6 is
PROMPT-ONLY until a paid key (FAL_KEY / REPLICATE_API_TOKEN) is added — see 6_SOP/LTX_BROLL_PLAN.md.
Also deleted: all vetted reference repo clones in `2_KNOWLEDGE/external_toolkits/` except `pyCapCut`
(used by capcut_export); verdicts live in INGESTION_LOG.

## Deleted 2026-07-14 (second wave — lipsync/avatar line removed entirely, user decision)
Engines #3/#3b/#4-mascot/#5 (SadTalker, MuseTalk, mascot rig/talk/perform/hybrid, LivePortrait,
Rhubarb QC, lipsync_service, avatar_motion) + their venvs/weights under
`2_KNOWLEDGE/external_toolkits/` (~22.6 GB) + `openai/whisper-tiny` (was only MuseTalk's feature
extractor). `4_BRAIN/dub_align.py` kept (pure dubbing timing math, not avatar);
`7_ASSETS/brand/SEOSONA/mascot_poses` kept (brand artwork, engine-independent).

## Pre-fetch everything (optional, before first render)
```powershell
python -m pip install -U "huggingface_hub[cli]"
huggingface-cli download k2-fsa/OmniVoice
huggingface-cli download kiendt/PhoWhisper-large-ct2
```
