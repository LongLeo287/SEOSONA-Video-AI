"""
SEOSONA Video — ASR (speech → word timestamps). ONE engine, ONE model (2026-07-14 user decision).

Model: VinAI PhoWhisper-large (CTranslate2, `kiendt/PhoWhisper-large-ct2`) on the faster-whisper
runtime — the field-consensus stack for Vietnamese pipelines (survey 2026-07-14: generic tools use
faster-whisper/whisper.cpp with base–medium; every serious language-specialised pipeline picks the
fine-tune — FunClip→Paraformer for zh, VN projects→PhoWhisper) and our own Phase-0 benchmark
(gold-set WER 0.041, 28/32 perfect; published pure-VN WER ~2× better than whisper large-v3 —
evidence in 8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md).

Removed with the consolidation (do NOT restore): the defective phowhisper-medium-ct2 int8 build
(repetition-loop hallucinations), generic faster-whisper base/large-v3 model weights, openai-whisper,
sherpa-onnx, WhisperX (its VN aligner is CC-BY-NC). No fallback model: if ASR fails the caller gets
[] and handles it honestly.

Output shape (unchanged): [{"word": str, "start": float, "end": float}, ...]
Overrides: SEOSONA_PHOWHISPER_MODEL=<CT2 repo/dir> · SEOSONA_ASR_DEVICE=cpu|cuda
"""
import os

_DEFAULT_MODEL = "kiendt/PhoWhisper-large-ct2"


def _device():
    """cuda when available, else cpu. large-ct2 on CPU int8 measured RTF ~3-4 (too slow for long
    footage) vs cuda/fp16 RTF ~0.3 — so auto-detect instead of defaulting to cpu. Env override kept."""
    forced = os.environ.get("SEOSONA_ASR_DEVICE")
    if forced:
        return forced
    try:
        import ctranslate2
        return "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    except Exception:
        return "cpu"


def _load_model(model_id):
    """WhisperModel on the detected device; a broken CUDA stack degrades to cpu/int8, never raises."""
    from faster_whisper import WhisperModel
    dev = _device()
    compute = "int8" if dev == "cpu" else "float16"
    try:
        return WhisperModel(model_id, device=dev, compute_type=compute)
    except Exception as e:
        if dev == "cpu":
            raise
        print(f"[ASR] cuda load failed ({str(e)[:120]}) -> cpu/int8")
        return WhisperModel(model_id, device="cpu", compute_type="int8")


def _whisperx(audio_path, language):
    """WhisperX: faster-whisper + wav2vec2 forced alignment for precise word timestamps."""
    try:
        from .whisperx_engine import transcribe
    except Exception:
        try:
            from whisperx_engine import transcribe
        except Exception:
            return None
    return transcribe(audio_path, language)


def _collect_fw(segments):
    """faster-whisper segment generator → uniform word list."""
    words = []
    for seg in segments:
        for w in (seg.words or []):
            t = (w.word or "").strip()
            if not t:
                continue
            try:
                # whisper/faster-whisper can return None timestamps for an unaligned word; skip just THAT
                # word — a single bad timestamp must not discard the whole transcription (→ empty captions).
                words.append({"word": t, "start": float(w.start), "end": float(w.end)})
            except (TypeError, ValueError):
                continue
    return words or None


def transcribe_words(audio_path, language="vi"):
    """Transcribe → word-level timestamps via PhoWhisper-large.

    Returns [{"word","start","end"}, ...] — empty list if the audio is missing or ASR fails
    (callers handle the no-captions case honestly; there is no fallback model).
    """
    if not audio_path or not os.path.exists(audio_path):
        print(f"[ASR] audio not found: {audio_path}")
        return []
    model_id = os.environ.get("SEOSONA_PHOWHISPER_MODEL", _DEFAULT_MODEL)
    try:
        model = _load_model(model_id)
        segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)
        words = _collect_fw(segments) or []
    except Exception as e:
        print(f"[ASR] PhoWhisper failed ({e}) — no transcription produced.")
        return []
    if words:
        print(f"[ASR] PhoWhisper-large -> {len(words)} words.")
    else:
        print("[ASR] WARNING: no words produced.")
    return words
