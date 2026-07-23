# Voice and TTS Engine Routing

Created: 2026-06-19 · Rewritten: 2026-07-14 (engine consolidation — user decision after the
Phase-0 benchmark, evidence `8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md`)

## CURRENT POLICY (2026-07-14 — supersedes everything below the history line)

**Voice/TTS: ONE engine.** `2_SKILLS/voice_cloner/voice_router.py` → OmniVoice (k2-fsa, local,
VN-native 8482h, zero-shot + CQA voice clone, isolated torch-2.8 venv `.venv-omnivoice`).
- The Chí Quyết (CQA) clone is THE brand voice for BOTH brands (ref
  `7_ASSETS/voice/profiles/cqa_omnivoice_ref.wav`).
- **NO backup engine.** A failed synth returns `None` honestly; native_composer handles the
  no-voice case. No silent fallback ever.
- LICENSE: OmniVoice code Apache-2.0, **weights CC-BY-NC** (Emilia) — owner-accepted risk
  (recorded in voice_router.py + 0_SETUP/MODELS.md). VieNeu-TTS (Apache-2.0 code+weights, the only
  clean VN clone alternative) was REMOVED with all other engines — it stays on record as the
  license-clean option if the NC stance ever changes.
- Removed engines (do NOT re-add — see memory `no-recreate-deprecated-systems`): VieNeu, F5-TTS,
  edge-tts, kokoro, fish/cosyvoice, LoRA, sherpa.

**ASR: ONE engine, ONE model.** `2_SKILLS/srt_maker/asr_router.py` → PhoWhisper-large
(CT2 float16, `kiendt/PhoWhisper-large-ct2`) on faster-whisper/CTranslate2, cuda auto-detect.
- The bundled phowhisper-medium-ct2 was PROVEN DEFECTIVE (repetition-loop hallucinations) and
  deleted; openai-whisper + sherpa paths removed; WhisperX rejected (its VN aligner is CC-BY-NC).
- Overrides: `SEOSONA_PHOWHISPER_MODEL` (CT2 repo/dir) · `SEOSONA_ASR_DEVICE=cpu|cuda`.
- Output shape everywhere: `[{"word","start","end"}, ...]`; caption segmentation =
  `whisper_engine.group_words_to_segments`.

## Rules that still apply

1. Voice references: only rights-cleared samples under `7_ASSETS/voice/profiles/`; never clone a
   third-party voice without explicit permission (consent gate carries into V2).
2. Adding a NEW engine (only with an owner decision + benchmark evidence): new engine file + an
   explicit probe branch in the router — never a dead `if engine == …` that silently falls through.
3. Native word timestamps preferred; script-derived fallback for generated TTS; ASR for real
   footage.
4. After any voice/ASR change: run the pipeline smoke test, ffprobe both streams, confirm SRT
   matches the script, keep engine deps optional, no keys/samples/machine paths in docs.

## History (obsolete — kept for provenance)

- 2026-06-24: switchable multi-engine ASR router (PhoWhisper → faster-whisper → openai-whisper).
- 2026-06-29: OmniVoice primary → VieNeu backup; F5/edge-tts/LoRA/fish removed.
- The old P0–P3 external-repo priority list (VieNeu/GPT-SoVITS/fish/CosyVoice/edge-tts…) is void —
  engine selection is now a closed decision, revisited only via a new Phase-0-style benchmark.
