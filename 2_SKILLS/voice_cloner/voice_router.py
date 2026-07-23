# -*- coding: utf-8 -*-
"""
SEOSONA Video — Voice Router (single source of truth for TTS).

ONE brand-voice policy (2026-07-14, user decision after the Phase-0 benchmark):
  OmniVoice (ONLY engine) — k2-fsa/OmniVoice, local, Vietnamese-native (8482h). The Chí Quyết (CQA)
  cloned voice is THE brand voice for BOTH SEOSONA and CQA. Runs in its isolated torch-2.8 venv via
  subprocess; output is gap-trimmed + loudness-normalized to read cleanly.

  LICENSE NOTE: OmniVoice code is Apache-2.0 but the WEIGHTS are CC-BY-NC (trained on Emilia — see
  the k2-fsa/OmniVoice model card). The owner chose it anyway for voice quality (benchmark
  8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md), accepting the non-commercial license risk.

ALL other voice engines removed (VieNeu, F5-TTS, edge-tts, LoRA, parallel/best-take,
fish/cosyvoice/kokoro). There is NO fallback: if OmniVoice fails, this returns None and the render
handles the no-voice case honestly (no silent engine swap — V2 blueprint rule).
"""
from importlib import import_module


def synthesize_voice(
    text,
    audio_out,
    *,
    brand="seosona",
    engine=None,            # accepted for call-site compatibility; voice is fixed to brand policy
    preset_voice=None,      # ignored — kept for call-site compatibility
    reference_audio=None,   # ignored for OmniVoice — the brand voice is always the CQA clone
    fallback_voice=None,
    require_male_southern=False,
):
    """Generate the brand voice via OmniVoice (CQA clone). Returns audio_out on success, or None
    on failure — callers (native_composer) rely on None to handle the no-voice case."""
    try:
        ov = import_module("2_SKILLS.voice_cloner.omnivoice_engine")
        r = ov.synthesize(text, audio_out)
        if r:
            print(f"[Voice Router] OmniVoice — brand voice (CQA) | brand: {brand}")
            return r
    except Exception as e:
        print(f"[Voice Router] OmniVoice failed ({e}).")
    print("[Voice Router] No voice produced (OmniVoice is the only engine — no fallback).")
    return None


# Backward-compatible alias for the previous call site.
clone_voice = synthesize_voice
