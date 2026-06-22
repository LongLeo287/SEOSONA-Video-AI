import os
import subprocess
import shutil

def apply_lexicon(text, lexicon=None):
    """
    Applies the lexicon dictionary to the text, changing how it is pronounced 
    without altering the original text used for captions.
    """
    if not lexicon:
        return text
    
    modified_text = text
    for word, pronunciation in lexicon.items():
        # Using simple replace for now, could be enhanced with regex for word boundaries
        modified_text = modified_text.replace(word, pronunciation)
        
    return modified_text

def synthesize(script_text, output_path, ref_audio_path=None, ref_text="", lexicon=None):
    """
    Generates speech using F5-TTS local installation.
    Requires F5-TTS to be installed in the environment (f5-tts_infer-cli).
    """
    if lexicon:
        tts_text = apply_lexicon(script_text, lexicon)
    else:
        tts_text = script_text

    print(f"[F5-TTS Local] Generating audio for: '{tts_text[:50]}...'")

    # If no ref audio provided, look for a default one in the workspace
    if not ref_audio_path:
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '8_WORKSPACE'))
        ref_audio_path = os.path.join(workspace_dir, '..', '7_ASSETS', 'refvoice', 'clone_ref.wav')
    
    if not os.path.exists(ref_audio_path):
        print(f"⚠️ [F5-TTS Local] Reference audio not found at: {ref_audio_path}")
        print("Please provide a clone_ref.wav file for voice cloning.")
        # Fallback to a stub file creation for pipeline testing purposes
        with open(output_path, "wb") as f:
            pass
        return output_path

    # Route to isolated .venv-f5 environment following SEOSONA architecture
    script_dir = os.path.dirname(__file__)
    venv_f5_cli_windows = os.path.join(script_dir, ".venv-f5", "Scripts", "f5-tts_infer-cli.exe")
    venv_f5_cli_linux = os.path.join(script_dir, ".venv-f5", "bin", "f5-tts_infer-cli")
    
    if os.path.exists(venv_f5_cli_windows):
        f5_cli = venv_f5_cli_windows
    elif os.path.exists(venv_f5_cli_linux):
        f5_cli = venv_f5_cli_linux
    else:
        # Fallback to global if venv not setup yet
        f5_cli = shutil.which("f5-tts_infer-cli")
    
    if not f5_cli:
        print("⚠️ [F5-TTS Local] f5-tts_infer-cli not found in .venv-f5 or PATH.")
        print("Please run setup_f5_env.ps1 first to setup the isolated environment.")
        # Fallback stub
        with open(output_path, "wb") as f:
            pass
        return output_path

    cmd = [
        f5_cli,
        "-m", "F5-TTS",
        "-r", ref_audio_path,
        "-s", ref_text if ref_text else "This is a reference voice.",
        "-t", tts_text,
        "-o", output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[F5-TTS Local] Successfully generated audio at: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ [F5-TTS Local] Failed to generate audio: {e}")
        raise RuntimeError(f"F5-TTS CLI failed: {e}")

    return output_path
