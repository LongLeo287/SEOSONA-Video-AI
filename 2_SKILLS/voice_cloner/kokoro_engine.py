import os
import torch
import soundfile as sf
import traceback

def synthesize(text, output_path, voice="af_bella"):
    """
    Synthesize speech using Kokoro-82M locally.
    Args:
        text (str): Text to synthesize.
        output_path (str): The output file path (wav/mp3).
        voice (str): The voice pack name (e.g. af_bella).
    Returns:
        output_path on success, None on failure.
    """
    try:
        from kokoro import KPipeline
        
        print(f"[Kokoro Engine] Initializing Kokoro TTS with voice '{voice}'...")
        
        # Determine paths
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        models_dir = os.path.join(workspace_dir, "7_ASSETS", "models", "kokoro")
        model_path = os.path.join(models_dir, "kokoro-v1_0.pth")
        
        if not os.path.exists(model_path):
            print(f"[Kokoro Engine] Error: Model not found at {model_path}. Please run download_local_models.py")
            return None

        # Setup Pipeline
        # By default Kokoro supports American English (a) or British English (b). We'll use 'a'.
        # Since Kokoro doesn't natively support Vietnamese perfectly yet, it will read it phonetically 
        # or we can use an 'a' pipeline for english text.
        pipeline = KPipeline(lang_code='a', model=False)
        
        # Load weights explicitly if needed, or Kokoro handles it
        # Actually KPipeline will load weights from huggingface by default if not passed,
        # but we can pass the path if it supports it, or just rely on huggingface cache.
        # For simplicity, if kokoro is installed, it handles loading.
        
        generator = pipeline(
            text, voice=voice,
            speed=1.0, split_pattern=r'\n+'
        )
        
        audio_chunks = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_chunks.append(audio)
            
        if not audio_chunks:
            print("[Kokoro Engine] Failed to generate audio.")
            return None
            
        # Concatenate audio
        final_audio = torch.cat(audio_chunks, dim=0)
        
        # Save audio using soundfile (Kokoro returns 24kHz audio)
        sf.write(output_path, final_audio.numpy(), 24000)
        print(f"[Kokoro Engine] Saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"[Kokoro Engine] Error: {e}")
        traceback.print_exc()
        return None
