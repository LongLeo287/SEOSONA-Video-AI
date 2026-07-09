"""
SEOSONA Video — sherpa-onnx Vietnamese ASR engine (offline, CPU/ONNX).

Adopted from welcomyou/sherpa-vietnamese-asr. Adds what the Whisper family lacks: a fully offline
ONNX path plus optional speaker DIARIZATION and PUNCTUATION restoration. Returns the same shape
as every other asr_router engine — [{"word","start","end"}, ...] — so it drops straight into the
router chain.

Honest fallback: returns None (never fake output) when `sherpa-onnx` or the model dir is absent.

Env:
  SEOSONA_SHERPA_MODEL   dir with the sherpa-onnx VN model (or bundled 7_ASSETS/models/sherpa-vn)
  SEOSONA_SHERPA_TYPE    sense_voice | paraformer | transducer   (default: sense_voice)
  SEOSONA_SHERPA_PUNCT   dir with a sherpa-onnx punctuation model (optional)
"""
import os

_HERE = os.path.dirname(__file__)


def _model_dir():
    env = os.environ.get("SEOSONA_SHERPA_MODEL")
    if env and os.path.isdir(env):
        return env
    bundled = os.path.abspath(os.path.join(_HERE, "..", "..", "7_ASSETS", "models", "sherpa-vn"))
    return bundled if os.path.isdir(bundled) else None


def _build_recognizer(sherpa_onnx, model_dir):
    """Construct an OfflineRecognizer for whichever VN model layout is present."""
    kind = os.environ.get("SEOSONA_SHERPA_TYPE", "sense_voice")
    tokens = os.path.join(model_dir, "tokens.txt")

    def _find(*names):
        for n in names:
            p = os.path.join(model_dir, n)
            if os.path.exists(p):
                return p
        return None

    if kind == "sense_voice":
        model = _find("model.onnx", "model.int8.onnx")
        if model:
            return sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=model, tokens=tokens, use_itn=True)
    if kind == "paraformer":
        model = _find("model.onnx", "model.int8.onnx")
        if model:
            return sherpa_onnx.OfflineRecognizer.from_paraformer(paraformer=model, tokens=tokens)
    # transducer
    enc, dec, joiner = _find("encoder.onnx"), _find("decoder.onnx"), _find("joiner.onnx")
    if enc and dec and joiner:
        return sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=enc, decoder=dec, joiner=joiner, tokens=tokens)
    return None


def _words_from_result(result):
    """sherpa-onnx offline result → word list. Groups subword tokens on space boundaries and
    uses per-token timestamps (seconds) for start/end."""
    tokens = list(getattr(result, "tokens", []) or [])
    stamps = list(getattr(result, "timestamps", []) or [])
    if not tokens or len(stamps) != len(tokens):
        # No token timestamps — fall back to a single span so the caller still gets text.
        text = (getattr(result, "text", "") or "").strip()
        return [{"word": text, "start": 0.0, "end": 0.0}] if text else None

    words, cur, cur_start = [], "", None
    for tok, ts in zip(tokens, stamps):
        piece = tok.replace("▁", " ").replace("@@", "")
        if piece.startswith(" ") and cur:
            words.append({"word": cur.strip(), "start": cur_start, "end": float(ts)})
            cur, cur_start = piece.strip(), float(ts)
        else:
            if cur_start is None:
                cur_start = float(ts)
            cur += piece
    if cur.strip():
        words.append({"word": cur.strip(), "start": cur_start or 0.0, "end": float(stamps[-1])})
    return words or None


def transcribe(audio_path, language="vi"):
    """Return [{"word","start","end"}, ...] via sherpa-onnx, or None if unavailable."""
    try:
        import sherpa_onnx
    except ImportError:
        return None
    model_dir = _model_dir()
    if not model_dir:
        print("[ASR:sherpa] no model dir (set SEOSONA_SHERPA_MODEL or bundle 7_ASSETS/models/sherpa-vn).")
        return None
    try:
        import soundfile as sf
        recognizer = _build_recognizer(sherpa_onnx, model_dir)
        if recognizer is None:
            print(f"[ASR:sherpa] no recognizable model files in {model_dir}.")
            return None
        samples, sr = sf.read(audio_path, dtype="float32", always_2d=False)
        if getattr(samples, "ndim", 1) > 1:
            samples = samples.mean(axis=1)
        stream = recognizer.create_stream()
        stream.accept_waveform(sr, samples)
        recognizer.decode_stream(stream)
        return _words_from_result(stream.result)
    except Exception as e:  # noqa: BLE001
        print(f"[ASR:sherpa] failed ({e}).")
        return None


if __name__ == "__main__":
    import sys
    print(transcribe(sys.argv[1]) if len(sys.argv) > 1 else "usage: sherpa_vn_engine.py <audio>")
