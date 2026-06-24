"""
SEOSONA Video — ASR Router (single switchable path for speech → word timestamps).

Mirrors voice_router: a primary engine with automatic backups, switch flow instantly
via the SEOSONA_ASR env var. Every engine returns the SAME shape so the pipeline never
changes:  [{"word": str, "start": float, "end": float}, ...]

Engines (primary first, rest are fallbacks):
  - phowhisper     : VinAI PhoWhisper (Vietnamese-specialised, lowest WER on VI).  [primary]
  - faster_whisper : CTranslate2 generic Whisper (fast, int8).                      [backup]
  - openai_whisper : reference openai-whisper (word_timestamps native).             [backup]

Switch:  SEOSONA_ASR=faster_whisper   (default: phowhisper)
Model:   SEOSONA_PHOWHISPER_MODEL=<CT2 PhoWhisper repo>  ·  SEOSONA_ASR_DEVICE=cpu|cuda
"""
import os

_DEVICE = os.environ.get("SEOSONA_ASR_DEVICE", "cpu")
_COMPUTE = "int8" if _DEVICE == "cpu" else "float16"


def _phowhisper(audio_path, language):
    """VinAI PhoWhisper via faster-whisper (CTranslate2). Vietnamese-specialised."""
    model_id = os.environ.get("SEOSONA_PHOWHISPER_MODEL", "kiendt/PhoWhisper-large-ct2")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        model = WhisperModel(model_id, device=_DEVICE, compute_type=_COMPUTE)
        segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)
        return _collect_fw(segments)
    except Exception as e:
        print(f"[ASR:phowhisper] unavailable ({e}).")
        return None


def _faster_whisper(audio_path, language):
    """Generic Whisper via faster-whisper (CTranslate2)."""
    size = os.environ.get("SEOSONA_WHISPER_SIZE", "base")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        model = WhisperModel(size, device=_DEVICE, compute_type=_COMPUTE)
        segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)
        return _collect_fw(segments)
    except Exception as e:
        print(f"[ASR:faster_whisper] failed ({e}).")
        return None


def _openai_whisper(audio_path, language):
    """Reference openai-whisper (kept as a last-resort backup)."""
    try:
        from .whisper_engine import generate_word_level_data
    except Exception:
        return None
    try:
        size = os.environ.get("SEOSONA_WHISPER_SIZE", "base")
        words = generate_word_level_data(audio_path, model_name=size)
        return words or None
    except Exception as e:
        print(f"[ASR:openai_whisper] failed ({e}).")
        return None


def _collect_fw(segments):
    """faster-whisper segment generator → uniform word list."""
    words = []
    for seg in segments:
        for w in (seg.words or []):
            t = (w.word or "").strip()
            if t:
                words.append({"word": t, "start": float(w.start), "end": float(w.end)})
    return words or None


_ENGINES = {
    "phowhisper": _phowhisper,
    "faster_whisper": _faster_whisper,
    "openai_whisper": _openai_whisper,
}


def transcribe_words(audio_path, language="vi"):
    """Transcribe → word-level timestamps via the primary engine, falling back on failure.

    Returns [{"word","start","end"}, ...] (possibly empty if every engine fails).
    """
    if not audio_path or not os.path.exists(audio_path):
        print(f"[ASR Router] audio not found: {audio_path}")
        return []
    primary = os.environ.get("SEOSONA_ASR", "phowhisper")
    chain = [primary] + [e for e in ("phowhisper", "faster_whisper", "openai_whisper") if e != primary]
    for engine in chain:
        fn = _ENGINES.get(engine)
        if not fn:
            continue
        words = fn(audio_path, language)
        if words:
            note = "" if engine == primary else " (fallback)"
            print(f"[ASR Router] engine '{engine}'{note} -> {len(words)} words.")
            return words
        print(f"[ASR Router] '{engine}' unavailable/failed -> trying next.")
    print("[ASR Router] WARNING: no ASR engine produced output.")
    return []
