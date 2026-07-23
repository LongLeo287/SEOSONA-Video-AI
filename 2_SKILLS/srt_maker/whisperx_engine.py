"""
SEOSONA Video — WhisperX ASR engine (m-bain/whisperX).

WhisperX = faster-whisper transcription + wav2vec2 forced alignment for *precise* word-level
timestamps (much tighter than Whisper's own), plus optional pyannote speaker diarization. Returns
the router's uniform [{"word","start","end"}, ...] shape.

Honest fallback: returns None (never fake) when `whisperx` is unavailable or a step fails.

Env:
  SEOSONA_ASR_DEVICE   cpu|cuda   (default cpu)
  SEOSONA_WHISPERX_MODEL  faster-whisper model id/size (default: large-v2)
  SEOSONA_HF_TOKEN     HuggingFace token — only needed if diarization is enabled
"""
import os

_DEVICE = os.environ.get("SEOSONA_ASR_DEVICE", "cpu")
_COMPUTE = "int8" if _DEVICE == "cpu" else "float16"


def transcribe(audio_path, language="vi"):
    try:
        import whisperx
    except ImportError:
        return None
    try:
        model_id = os.environ.get("SEOSONA_WHISPERX_MODEL", "large-v2")
        model = whisperx.load_model(model_id, _DEVICE, compute_type=_COMPUTE, language=language)
        audio = whisperx.load_audio(audio_path)
        result = model.transcribe(audio, language=language)

        # Forced alignment → precise per-word timestamps.
        try:
            align_model, metadata = whisperx.load_align_model(language_code=language, device=_DEVICE)
            result = whisperx.align(result["segments"], align_model, metadata, audio, _DEVICE,
                                    return_char_alignments=False)
        except Exception as e:  # noqa: BLE001 — alignment model may be missing for some languages
            print(f"[ASR:whisperx] alignment skipped ({e}); using segment timings.")

        words = []
        for seg in result.get("segments", []):
            for w in seg.get("words", []) or []:
                t = (w.get("word") or "").strip()
                s, e = w.get("start"), w.get("end")
                if t and s is not None and e is not None:
                    words.append({"word": t, "start": float(s), "end": float(e)})
            if not seg.get("words") and (seg.get("text") or "").strip():
                words.append({"word": seg["text"].strip(),
                              "start": float(seg.get("start", 0.0)), "end": float(seg.get("end", 0.0))})
        return words or None
    except Exception as e:  # noqa: BLE001
        print(f"[ASR:whisperx] failed ({e}).")
        return None


if __name__ == "__main__":
    import sys
    print(transcribe(sys.argv[1]) if len(sys.argv) > 1 else "usage: whisperx_engine.py <audio>")
