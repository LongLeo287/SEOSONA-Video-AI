import os
import sys

# Ensure this runs in the correct isolated environment
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(CURRENT_DIR, ".venv-vieneu", "Scripts", "python.exe")

if sys.executable != VENV_PYTHON and os.path.exists(VENV_PYTHON):
    print(f"Relaunching via isolated environment: {VENV_PYTHON}")
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

try:
    from vieneu import Vieneu
except ImportError:
    print("Error: vieneu is not installed in the current environment.")
    print(f"Please run setup_vieneu_env.ps1 to install it.")
    sys.exit(1)

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Initialize the global TTS engine lazily
_tts_engine = None

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        print("Initializing VieNeu-TTS engine (v3 Turbo)...")
        _tts_engine = Vieneu()
    return _tts_engine

def generate_speech(text: str, output_path: str, reference_audio: str = None, voice: str = None):
    """
    Generates speech using VieNeu-TTS engine.
    
    Args:
        text (str): The text to synthesize.
        output_path (str): The path to save the output audio file.
        reference_audio (str, optional): Path to reference audio for voice cloning (3-5s).
        voice (str, optional): The name of an approved preset voice.
                               If reference_audio is provided, this is ignored.
    """
    tts = get_tts_engine()
    
    print(f"[VieNeu-TTS] Generating speech for: {text[:50]}...")
    
    infer_kwargs = {"text": text}
    
    if reference_audio and os.path.exists(reference_audio):
        print(f"[VieNeu-TTS] Using zero-shot voice cloning with reference: {reference_audio}")
        infer_kwargs["ref_audio"] = reference_audio
    elif voice:
        print(f"[VieNeu-TTS] Using preset voice: {voice}")
        infer_kwargs["voice"] = voice
    else:
        print("[VieNeu-TTS] No reference audio or preset voice configured; using engine default.")
        
    try:
        audio_spec = tts.infer(**infer_kwargs)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        tts.save(audio_spec, output_path)
        print(f"[VieNeu-TTS] Saved audio to: {output_path}")
        return True
    except Exception as e:
        print(f"[VieNeu-TTS] Error generating speech: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Quick test when running the script directly
    import argparse
    parser = argparse.ArgumentParser(description="Test VieNeu-TTS Local Engine")
    parser.add_argument("--text", type=str, default="Xin chào, đây là bản kiểm tra giọng nói SEOSONA.", help="Text to synthesize")
    parser.add_argument("--out", type=str, default="test_vieneu_output.wav", help="Output file path")
    parser.add_argument("--voice", type=str, default=None, help="Preset voice name")
    parser.add_argument("--ref", type=str, default=None, help="Reference audio path")
    args = parser.parse_args()
    
    generate_speech(args.text, args.out, reference_audio=args.ref, voice=args.voice)
