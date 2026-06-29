# -*- coding: utf-8 -*-
"""Build an OPTIMAL VieNeu clone reference from a raw voice recording.

A good zero-shot clone reference is NOT the raw recording — it is a short, clean,
mono, natural-level clip. This tool turns a long/stereo/loud recording (e.g. voice
ripped from a video) into a tuned reference:

  1. Isolate vocals with demucs (drops any background music; harmless if there is none).
  2. Score 14-18s windows bounded by speech pauses; pick the clearest one.
  3. Mono · 24 kHz · light high-pass + denoise · natural loudness (-20 LUFS).

Why short + clean: VieNeu instant-clone samples a few seconds of timbre; a 77s,
hot-compressed, stereo clip clones worse than a clean 14s mono one.

Usage:
    python scripts/build_voice_ref.py 7_ASSETS/voice/profiles/seosona.WAV \
        -o 7_ASSETS/voice/profiles/seosona_ref_clean.wav

Run once per brand voice; commit only the small output clip (the raw recording
stays local/gitignored). demucs is a one-time PREP dependency, not a runtime one.
"""
import os, sys, subprocess, argparse, tempfile, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import native_composer as nc  # for the resolved ffmpeg/ffprobe binaries


def _isolate_vocals(src, workdir):
    """demucs --two-stems=vocals → workdir/htdemucs/<name>/vocals.wav (falls back to src)."""
    try:
        import torch
        dev = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        dev = "cpu"
    subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals",
                    "-d", dev, "-o", workdir, src], check=True)
    name = os.path.splitext(os.path.basename(src))[0]
    voc = os.path.join(workdir, "htdemucs", name, "vocals.wav")
    return voc if os.path.exists(voc) else src


def _best_window(voc, lo=14.0, hi=18.0):
    """Return (start, end) of the clearest pause-bounded window (clean speech)."""
    import librosa, numpy as np
    y, sr = librosa.load(voc, sr=22050, mono=True)
    hop = 512
    rms_db = librosa.amplitude_to_db(
        librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0], ref=np.max)
    t = np.arange(len(rms_db)) * hop / sr
    valleys = [t[i] for i in range(1, len(rms_db) - 1)
               if rms_db[i] < -22 and rms_db[i] <= rms_db[i-1] and rms_db[i] <= rms_db[i+1]]
    best = None
    for a in valleys:
        for b in valleys:
            if lo <= b - a <= hi:
                mean_e = rms_db[(t >= a) & (t < b)].mean()
                if best is None or mean_e > best[2]:
                    best = (a, b, mean_e)
    if best:
        return best[0], best[1]
    # fallback: a fixed middle window
    dur = len(y) / sr
    s = max(0.0, dur / 2 - 7.5)
    return s, min(dur, s + 15.0)


def build(src, out, lo=14.0, hi=18.0, lufs=-20):
    src = os.path.abspath(src)
    out = os.path.abspath(out)
    work = tempfile.mkdtemp(prefix="voiceref_")
    try:
        voc = _isolate_vocals(src, work)
        a, b = _best_window(voc, lo, hi)
        print(f"[build_voice_ref] window {a:.1f}s -> {b:.1f}s ({b-a:.1f}s) from {os.path.basename(voc)}")
        ff = nc._ffmpeg_bin()
        af = f"highpass=f=70,afftdn=nr=10,loudnorm=I={lufs}:TP=-2:LRA=11,aresample=24000"
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{a:.2f}", "-to", f"{b:.2f}", "-i", voc,
                        "-af", af, "-ac", "1", "-c:a", "pcm_s16le", out], check=True)
        print(f"[build_voice_ref] OK -> {out} (mono 24kHz, {b-a:.1f}s)")
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build an optimal VieNeu clone reference.")
    ap.add_argument("src", help="raw voice recording (wav/mp3/m4a)")
    ap.add_argument("-o", "--out", required=True, help="output reference wav (mono 24kHz)")
    ap.add_argument("--min", type=float, default=14.0, help="min window seconds")
    ap.add_argument("--max", type=float, default=18.0, help="max window seconds")
    ap.add_argument("--lufs", type=float, default=-20, help="target loudness")
    args = ap.parse_args()
    build(args.src, args.out, args.min, args.max, args.lufs)
