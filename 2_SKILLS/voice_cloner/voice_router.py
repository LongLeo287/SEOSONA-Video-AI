# -*- coding: utf-8 -*-
"""
SEOSONA Video — Voice Router (single source of truth for TTS).

ONE brand-voice policy (2026-06-29, user decision):
  1. OmniVoice (PRIMARY) — k2-fsa/OmniVoice, local, Apache-2.0, Vietnamese-native (8482h). The
     Chí Quyết (CQA) cloned voice is THE brand voice for BOTH SEOSONA and CQA. Runs in its isolated
     torch-2.8 venv via subprocess; output is gap-trimmed + loudness-normalized to read cleanly.
  2. VieNeu (BACKUP) — used only when OmniVoice can't run. Stable male preset.

ALL other voice engines removed (F5-TTS, edge-tts, LoRA, parallel/best-take, fish/cosyvoice/kokoro).
OmniVoice + VieNeu are the only two paths.
"""
import os
import glob
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DEFAULT_MALE_PRESET = "Gia Bảo"   # VieNeu backup preset (stable male voice)


def _ffmpeg():
    for c in glob.glob(os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg*")):
        if os.path.exists(c):
            return c
    return "ffmpeg"


def _has_vieneu():
    try:
        import vieneu  # noqa: F401
        return True
    except ImportError:
        return False


def synthesize_voice(
    text,
    audio_out,
    *,
    brand="seosona",
    engine=None,            # accepted for call-site compatibility; voice is fixed to brand policy
    preset_voice=None,
    reference_audio=None,   # ignored for OmniVoice — the brand voice is always the CQA clone
    fallback_voice=None,
    require_male_southern=False,
):
    """Generate the brand voice. OmniVoice (CQA voice) primary → VieNeu backup.
    Returns audio_out on success, or None only if both fail."""
    # 1) OmniVoice — the brand voice (CQA clone) for both brands
    try:
        ov = import_module("2_SKILLS.voice_cloner.omnivoice_engine")
        r = ov.synthesize(text, audio_out)
        if r:
            print(f"[Voice Router] OmniVoice — brand voice (CQA) | brand: {brand}")
            return r
    except Exception as e:
        print(f"[Voice Router] OmniVoice unavailable ({e}).")

    # 2) VieNeu BACKUP (used only when OmniVoice can't run)
    if not _has_vieneu():
        print("[Voice Router] BACKUP VieNeu not installed — no voice produced.")
        return None
    print(f"[Voice Router] BACKUP -> VieNeu preset '{DEFAULT_MALE_PRESET}'.")
    try:
        vieneu = import_module("2_SKILLS.voice_cloner.vieneu_engine")
        return vieneu.synthesize(text, audio_out, voice=preset_voice or DEFAULT_MALE_PRESET,
                                 reference_audio=None)
    except Exception as e:
        # honour the contract ("None only if both fail"): a raising backup must degrade to None, not crash
        # the render — native_composer relies on None to handle the no-voice case.
        print(f"[Voice Router] BACKUP VieNeu failed ({e}) — no voice produced.")
        return None


# Backward-compatible alias for the previous call site.
clone_voice = synthesize_voice
