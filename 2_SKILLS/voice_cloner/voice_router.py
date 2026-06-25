"""
SEOSONA Video — Voice Router (single source of truth for TTS).

Two real paths only, with an HONEST fallback:

  1. VieNeu (primary · local · Apache-2.0 · code-switch native via sea-g2p):
       - clone from a brand reference audio (PREFERRED — keeps the exact brand voice), or
       - a preset voice if no reference.
       Reads Vietnamese correctly AND pronounces English terms in English
       ("AI Agent là tác nhân…" → "AI Agent" stays English).

  2. edge-tts (FALLBACK ONLY): the configured male Vietnamese voice. This is a
       NORTHERN voice and NOT the brand voice — it runs only if VieNeu can't, and
       it is logged loudly so a fallback is never mistaken for the brand voice.

Rebuilt 2026-06-24. The old fish_audio_api.py router had dead branches
(fish_audio/f5tts/cosyvoice/omnivoice all fell through to edge-tts) and duplicate
engines (2× VieNeu, 2× F5, a stray English Kokoro). Those are quarantined under
_QUARANTINE/voice_legacy/. This router routes only what actually works.
"""
import os
from importlib import import_module


# ---------------------------------------------------------------------------
# MALE-ONLY VOICE POLICY
# The SEOSONA/CQA brand voice is male Southern Vietnamese. A female voice is
# NEVER produced. These are VieNeu v3turbo's male presets; any other/unknown
# preset is coerced to the default male preset, and the edge fallback is locked
# to the approved male voice.
# ---------------------------------------------------------------------------
MALE_VIENEU_PRESETS = {"Gia Bảo", "Thái Sơn", "Đức Trí", "Xuân Vĩnh", "Trọng Hữu", "Bình An"}
DEFAULT_MALE_PRESET = "Trọng Hữu"
MALE_EDGE_VOICE = "vi-VN-NamMinhNeural"


def _coerce_male_preset(voice):
    """Return an approved MALE VieNeu preset, never a female/unknown one."""
    name = str(voice).strip() if voice else ""
    if name in MALE_VIENEU_PRESETS:
        return name
    if name:
        print(f"[Voice Router] '{name}' is not an approved MALE preset -> using {DEFAULT_MALE_PRESET}.")
    return DEFAULT_MALE_PRESET


def _has_vieneu():
    try:
        import vieneu  # noqa: F401
        return True
    except ImportError:
        return False


def _edge_fallback(text, audio_out, fallback_voice, reason):
    print(f"[Voice Router] FALLBACK -> edge-tts ({fallback_voice}) -- {reason}.")
    print("[Voice Router] WARNING: this is the NORTHERN fallback, NOT the brand voice.")
    tts = import_module("2_SKILLS.tts_generator.tts_engine")
    return tts.generate_voice_with_subtitles(text, audio_out, voice=fallback_voice)


def synthesize_voice(
    text,
    audio_out,
    *,
    brand="seosona",
    engine="vieneu",
    preset_voice=None,
    reference_audio=None,
    fallback_voice="vi-VN-NamMinhNeural",
    require_male_southern=False,
):
    """Generate the brand voice. VieNeu primary (clone > preset); edge-tts honest fallback.

    Returns audio_out on VieNeu success, the edge-tts result (path or (path, word_boundaries))
    on fallback, or None only if even the fallback fails.
    """
    # MALE-ONLY: never emit a female voice. Coerce the preset to an approved male
    # one and lock the edge fallback to the approved male voice.
    preset_voice = _coerce_male_preset(preset_voice)
    if fallback_voice != MALE_EDGE_VOICE:
        print(f"[Voice Router] fallback voice coerced to male {MALE_EDGE_VOICE}.")
        fallback_voice = MALE_EDGE_VOICE

    if engine != "vieneu":
        return _edge_fallback(text, audio_out, fallback_voice,
                              f"engine '{engine}' is no longer supported — use 'vieneu'")

    if not _has_vieneu():
        return _edge_fallback(text, audio_out, fallback_voice, "VieNeu is not installed")

    # Cloning is deferred until a >=3s reference exists; vieneu_engine auto-uses the
    # male preset when the reference is missing/too short. Always pass both so the
    # clone activates automatically once a real reference clip is dropped in.
    mode = "clone>preset" if reference_audio else f"preset '{preset_voice}'"
    print(f"[Voice Router] Engine: VieNeu ({mode}) | brand: {brand} | male voice: {preset_voice}")
    vieneu = import_module("2_SKILLS.voice_cloner.vieneu_engine")
    result = vieneu.synthesize(text, audio_out, voice=preset_voice, reference_audio=reference_audio)
    if result:
        return result
    return _edge_fallback(text, audio_out, fallback_voice, "VieNeu generation failed")


# Backward-compatible alias for the previous call site.
clone_voice = synthesize_voice
