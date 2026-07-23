#!/usr/bin/env python
"""vad_router — voice-activity detection: wav -> speech segments [{start, end}] (seconds).

author: SEOSONA  ·  STAGING DELIVERABLE — place at  <LEGACY_ROOT>/2_SKILLS/srt_maker/vad_router.py

The V2 seam `@seosona/engines` `vadAdapter.detectSpeech(wav)` calls `vad_router.detect_speech(wav)`
and expects on stdout:  SEOSONA_VAD_RESULT:[{"start": <sec>, "end": <sec>}, ...]

Uses silero-vad (MIT, tiny ~2 MB, CPU) — the recommended host for the IMPORTED-MEDIA branch
(trim dead air, drive cut points from real speech). Pure silence honestly returns [].

INSTALL:  pip install silero-vad torch torchaudio    (see docs/legacy_staging/README.md)
Authored against the silero-vad pip API; TEST on the host once. Never fabricates — any failure raises.
"""
import json
import sys

_MODEL = None


def _load():
    global _MODEL
    if _MODEL is None:
        from silero_vad import load_silero_vad

        _MODEL = load_silero_vad()
    return _MODEL


def detect_speech(wav_path: str, min_speech_ms: int = 250):
    """Return [{'start': sec, 'end': sec}] speech spans; [] for pure silence."""
    from silero_vad import get_speech_timestamps, read_audio

    model = _load()
    sr = 16000
    wav = read_audio(wav_path, sampling_rate=sr)
    ts = get_speech_timestamps(
        wav,
        model,
        sampling_rate=sr,
        min_speech_duration_ms=int(min_speech_ms),
        return_seconds=True,
    )
    return [{"start": float(t["start"]), "end": float(t["end"])} for t in ts]


def main() -> None:
    wav_path = sys.argv[1]
    segs = detect_speech(wav_path)
    print("SEOSONA_VAD_RESULT:" + json.dumps(segs, ensure_ascii=False))


if __name__ == "__main__":
    main()
