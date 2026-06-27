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

        # SINGLE generation on the FULL text — ONE consistent voice for the whole video.
        # VieNeu auto-chunks long text internally (max_chars=256) while keeping ONE resolved
        # voice, so the timbre stays consistent end-to-end. The old code split the text by
        # sentence and called infer() once PER sentence, which re-resolved/re-sampled the
        # voice each time and produced "several different voices in one video". A moderate
        # temperature + crossfade keeps delivery stable and the internal joins smooth,
        # WITHOUT the temp=0.1 silence/repetition bug.
        # Lower temperature = more deterministic delivery -> consistent timbre AND even
        # pace across VieNeu's internal chunks (high temp made each chunk sound like a
        # slightly different voice at an uneven speed). Higher crossfade smooths joins.
        infer_kwargs.setdefault("temperature", 0.4)
        infer_kwargs.setdefault("top_p", 0.85)
        infer_kwargs.setdefault("crossfade_p", 0.15)
        print("[VieNeu Engine] Generating full take (single, consistent voice)...")
        audio = engine.infer(**infer_kwargs)  # infer_kwargs already carries the full text + voice/ref
        engine.save(audio=audio, output_path=output_path)

        out_size = os.path.getsize(output_path)
        if out_size < 5000:
            print(f"[VieNeu Engine] WARNING: Output audio suspiciously small ({out_size} bytes).")
            return None
        print(f"[VieNeu Engine] OK: {output_path} ({out_size:,} bytes) — single consistent voice.")
        return output_path
    except Exception as e:
        print(f"[VieNeu Engine] Error: {e}")
        import traceback
        traceback.print_exc()
        return None
