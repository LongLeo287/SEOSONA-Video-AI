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
            # Validate reference audio file is not empty
            file_size = os.path.getsize(reference_audio)
            if file_size < 1000:
                print(f"[VieNeu Engine] WARNING: Reference audio too small ({file_size} bytes), likely corrupted.")
                return None
            print(f"[VieNeu Engine] CLONE: male Southern voice from reference: {reference_audio}")
            print(f"[VieNeu Engine]    Reference file size: {file_size:,} bytes")
            infer_kwargs["ref_audio"] = reference_audio
        else:
            voice = voice or os.environ.get("SEOSONA_VIENEU_VOICE")
            if not voice:
                print("[VieNeu Engine] No preset voice configured.")
                return None
            print(f"[VieNeu Engine] Generating voice with preset: {voice}")
            infer_kwargs["voice"] = voice
            
        # Enforce deterministic generation to prevent voice drifting across chunks
        infer_kwargs["temperature"] = 0.1
        infer_kwargs["top_p"] = 0.5
        infer_kwargs["repetition_penalty"] = 1.05

        # Chunk the text to prevent Vieneu from drifting gender on long texts
        import re
        chunks = [c.strip() for c in re.split(r'(?<=[.!?。！？\n])\s+', text) if c.strip()]
        if not chunks:
            chunks = [text]

        from moviepy.editor import AudioFileClip, concatenate_audioclips
        temp_clips = []
        for i, chunk in enumerate(chunks):
            print(f"[VieNeu Engine] Generating chunk {i+1}/{len(chunks)}...")
            infer_kwargs["text"] = chunk
            chunk_audio = engine.infer(**infer_kwargs)
            chunk_path = f"{output_path}_chunk_{i}.mp3"
            engine.save(audio=chunk_audio, output_path=chunk_path)
            
            out_size = os.path.getsize(chunk_path)
            if out_size >= 1000:
                temp_clips.append(AudioFileClip(chunk_path))

        if not temp_clips:
            print("[VieNeu Engine] WARNING: Failed to generate any valid audio chunks.")
            return None

        # Concatenate all chunks
        final_clip = concatenate_audioclips(temp_clips)
        final_clip.write_audiofile(output_path, logger=None)
        final_clip.close()
        for clip in temp_clips:
            clip.close()

        # Cleanup chunk files
        for i in range(len(chunks)):
            chunk_path = f"{output_path}_chunk_{i}.mp3"
            if os.path.exists(chunk_path):
                try:
                    os.remove(chunk_path)
                except Exception:
                    pass
            
        print(f"[VieNeu Engine] OK: Saved combined audio: {output_path}")
        # Verify output file is valid
        out_size = os.path.getsize(output_path)
        if out_size < 5000:
            print(f"[VieNeu Engine] WARNING: Output audio suspiciously small ({out_size} bytes).")
            return None
        print(f"[VieNeu Engine]    Output size: {out_size:,} bytes - voice generation successful.")
        return output_path
    except Exception as e:
        print(f"[VieNeu Engine] Error: {e}")
        import traceback
        traceback.print_exc()
        return None
