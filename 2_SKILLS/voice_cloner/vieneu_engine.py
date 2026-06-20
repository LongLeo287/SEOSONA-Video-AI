import os
import asyncio

def synthesize(text, output_path, voice=None, reference_audio=None):
    """
    Synthesize speech using Vieneu V3 Turbo.
    Args:
        text (str): Vietnamese text to synthesize.
        output_path (str): The output file path (mp3/wav).
        voice (str): The preset voice ID.
        reference_audio (str): Optional clean male Southern Vietnamese reference audio.
    Returns:
        output_path on success, None on failure.
    """
    try:
        from vieneu import Vieneu
        
        print(f"[VieNeu Engine] Initializing v3turbo engine...")
        engine = Vieneu(mode="v3turbo")
        
        infer_kwargs = {"text": text}
        if reference_audio and os.path.exists(reference_audio):
            print(f"[VieNeu Engine] Generating voice from reference: {reference_audio}")
            infer_kwargs["ref_audio"] = reference_audio
        else:
            voice = voice or os.environ.get("SEOSONA_VIENEU_VOICE")
            if not voice:
                print("[VieNeu Engine] No preset voice configured.")
                return None
            print(f"[VieNeu Engine] Generating voice with preset: {voice}")
            infer_kwargs["voice"] = voice

        audio = engine.infer(**infer_kwargs)
        engine.save(audio=audio, output_path=output_path)
            
        print(f"[VieNeu Engine] Saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"[VieNeu Engine] Error: {e}")
        import traceback
        traceback.print_exc()
        return None
