"""
Voice Engine Adapter — Routes TTS requests to the best available engine.
Currently falls back to Edge-TTS until VieNeu/Fish Audio adapters are installed.
"""
import os
import sys
from importlib import import_module

# Engine priority: vieneu > fish_audio > edge-tts
_AVAILABLE_ENGINES = []

def _probe_engines():
    """Check which TTS engines are actually installed."""
    global _AVAILABLE_ENGINES
    _AVAILABLE_ENGINES = []
    try:
        import vieneu
        _AVAILABLE_ENGINES.append("vieneu")
    except ImportError:
        pass
    # Fish Audio requires API key
    if os.environ.get("FISH_AUDIO_API_KEY"):
        _AVAILABLE_ENGINES.append("fish_audio")
    # Edge-TTS is always available (pure Python, no GPU)
    _AVAILABLE_ENGINES.append("edge-tts")

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
    """
    Unified voice generation entry point.
    Attempts requested engine first, then falls through priority list.
    """
    _probe_engines()
    
    if engine in _AVAILABLE_ENGINES and engine == "vieneu":
        if require_male_southern and not reference_audio and not preset_voice:
            print("[Voice Engine] VieNeu is available, but no approved male Southern preset/reference was configured.")
            print("[Voice Engine] Falling back to the configured male Vietnamese Edge-TTS voice.")
        else:
            print(f"[Voice Engine] Using VieNeu TTS...")
            vieneu_engine = import_module('2_SKILLS.voice_cloner.vieneu_engine')
            vieneu_result = vieneu_engine.synthesize(
                script_text,
                audio_out,
                voice=preset_voice,
                reference_audio=reference_audio,
            )
            if vieneu_result:
                return vieneu_result

    if "fish_audio" in _AVAILABLE_ENGINES and engine in ["fish_audio", "f5tts"]:
        print(f"[Voice Engine] Using Fish Audio API...")
        # TODO: implement fish audio adapter
        # fish_engine = import_module('2_SKILLS.voice_cloner.fish_engine')
        # return fish_engine.synthesize(script_text, audio_out)

    # Fallback: Edge-TTS (always works)
    actual_engine = engine if engine in _AVAILABLE_ENGINES else "edge-tts"
    if actual_engine != engine:
        print(f"[Voice Engine] '{engine}' not available. Falling back to Edge-TTS.")
    else:
        print(f"[Voice Engine] Using Edge-TTS.")
    
    tts_engine = import_module('2_SKILLS.tts_generator.tts_engine')
    return tts_engine.generate_voice_with_subtitles(script_text, audio_out, voice=fallback_voice)
