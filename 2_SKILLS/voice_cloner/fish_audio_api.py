import os
import sys
from importlib import import_module

def clone_voice(script_text, audio_out, brand="cqa", engine="vieneu"):
    print(f"[Voice Cloner] {engine} requested, but falling back to edge-tts for stability...")
    tts_engine = import_module('2_SKILLS.tts_generator.tts_engine')
    return tts_engine.generate_voice_with_subtitles(script_text, audio_out, voice='vi-VN-NamMinhNeural')
