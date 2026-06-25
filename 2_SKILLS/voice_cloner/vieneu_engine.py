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
        # Voice cloning is DEFERRED until a real reference exists. A clone is used ONLY
        # when the reference is present AND >=3s (VieNeu needs 3-5s+ for a stable voice);
        # otherwise we fall back to the configured male preset. This keeps output clean
        # while brand reference clips are still being recorded.
        ref_ok = False
        file_size = 0
        if reference_audio and os.path.exists(reference_audio):
            file_size = os.path.getsize(reference_audio)
            ref_sec = 0.0
            try:
                import wave, contextlib
                with contextlib.closing(wave.open(reference_audio, 'rb')) as _w:
                    ref_sec = _w.getnframes() / float(_w.getframerate() or 1)
            except Exception:
                ref_sec = file_size / 88200.0  # rough estimate: 44.1kHz/16-bit mono
            if file_size >= 1000 and ref_sec >= 3.0:
                ref_ok = True
            else:
                print(f"[VieNeu Engine] Reference unusable for clone ({ref_sec:.1f}s, {file_size:,} B) "
                      f"— needs >=3s. Using preset instead (clone deferred).")

        if ref_ok:
            print(f"[VieNeu Engine] CLONE from reference: {reference_audio} ({file_size:,} B)")
            infer_kwargs["ref_audio"] = reference_audio
        else:
            voice = voice or os.environ.get("SEOSONA_VIENEU_VOICE")
            if not voice:
                print("[VieNeu Engine] No preset voice configured.")
                return None
            # Encoding-safe: preset names contain Vietnamese diacritics that crash on cp1252 consoles.
            print("[VieNeu Engine] Generating voice with preset:", str(voice).encode("ascii", "replace").decode())
            infer_kwargs["voice"] = voice

        # Use VieNeu's recommended generation defaults (temperature ~0.8). The previous
        # override (temperature=0.1, top_p=0.5) was meant to stop gender drift but instead
        # forced a repetition loop + silence padding + dropped words (~23s of trailing
        # silence per sentence, hallucinated "bàn ăn…" garbage). Defaults generate clean,
        # correctly-sized speech, so we no longer override them here.

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
