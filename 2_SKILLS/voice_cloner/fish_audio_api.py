"""Voice engine adapter for SEOSONA Video.

This module routes TTS requests to the best available approved engine. When no
clone-grade engine or preset is configured, it deliberately falls back to the
approved male Vietnamese Edge-TTS voice and reports that choice in logs.
"""
import os
from importlib import import_module


_AVAILABLE_ENGINES = []


def _probe_engines():
    """Check which TTS engines are actually installed or configured."""
    global _AVAILABLE_ENGINES
    _AVAILABLE_ENGINES = []

    try:
        import vieneu  # noqa: F401
        _AVAILABLE_ENGINES.append("vieneu")
    except ImportError:
        pass

    if os.environ.get("FISH_AUDIO_API_KEY"):
        _AVAILABLE_ENGINES.append("fish_audio")

    _AVAILABLE_ENGINES.append("edge-tts")


def _run_edge_tts(script_text, audio_out, fallback_voice):
    tts_engine = import_module("2_SKILLS.tts_generator.tts_engine")
    return tts_engine.generate_voice_with_subtitles(script_text, audio_out, voice=fallback_voice)


def clone_voice(
    script_text,
    audio_out,
    brand="cqa",
    engine="vieneu",
    fallback_voice="vi-VN-NamMinhNeural",
    preset_voice=None,
    reference_audio=None,
    require_male_southern=False,
):
    """Generate voice with the requested engine or the approved male fallback."""
    _probe_engines()

    if engine == "vieneu" and "vieneu" in _AVAILABLE_ENGINES:
        if require_male_southern and not reference_audio and not preset_voice:
            print("[Voice Engine] VieNeu is available, but no approved male Southern preset/reference was configured.")
            print("[Voice Engine] Falling back to the configured male Vietnamese Edge-TTS voice.")
        else:
            print("[Voice Engine] Using VieNeu TTS.")
            vieneu_engine = import_module("2_SKILLS.voice_cloner.vieneu_engine")
            vieneu_result = vieneu_engine.synthesize(
                script_text,
                audio_out,
                voice=preset_voice,
                reference_audio=reference_audio,
            )
            if vieneu_result:
                return vieneu_result

    if engine in ["fish_audio", "f5tts"] and "fish_audio" in _AVAILABLE_ENGINES:
        try:
            print("[Voice Engine] Using Fish Audio API adapter.")
            fish_engine = import_module("2_SKILLS.voice_cloner.fish_engine")
            fish_result = fish_engine.synthesize(
                script_text,
                audio_out,
                voice=preset_voice,
                reference_audio=reference_audio,
            )
            if fish_result:
                return fish_result
        except ModuleNotFoundError:
            print("[Voice Engine] Fish Audio key is set, but no project adapter is installed.")
            print("[Voice Engine] Falling back to the configured male Vietnamese Edge-TTS voice.")

    if engine not in _AVAILABLE_ENGINES:
        print(f"[Voice Engine] '{engine}' not available. Falling back to Edge-TTS.")
    else:
        print("[Voice Engine] Using Edge-TTS.")
    return _run_edge_tts(script_text, audio_out, fallback_voice)
