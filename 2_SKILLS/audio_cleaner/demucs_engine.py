import os
import subprocess
import shutil

def extract_vocals(input_audio_path, output_dir, model="htdemucs"):
    """
    Extracts vocals from an audio file using Demucs (voice-pro logic).
    Returns the path to the isolated vocal file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    print(f"[Demucs] Extracting vocals from {os.path.basename(input_audio_path)} using {model}...")
    
    # Run Demucs CLI
    # Expected output structure: <output_dir>/<model>/<filename>/vocals.wav
    command = f'python -m demucs.separate -n {model} --two-stems=vocals "{input_audio_path}" -o "{output_dir}"'
    
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[Demucs] Error during separation: {e.stderr.decode('utf-8', errors='ignore')}")
        return None

    filename_no_ext = os.path.splitext(os.path.basename(input_audio_path))[0]
    vocal_path = os.path.join(output_dir, model, filename_no_ext, "vocals.wav")
    
    if os.path.exists(vocal_path):
        # Move to the root of output_dir for easier access
        final_vocal_path = os.path.join(output_dir, f"{filename_no_ext}_vocals.wav")
        shutil.move(vocal_path, final_vocal_path)
        print(f"[Demucs] Successfully extracted vocals: {final_vocal_path}")
        return final_vocal_path
    else:
        print("[Demucs] Failed to locate output vocal file.")
        return None

if __name__ == "__main__":
    # Test script
    pass
