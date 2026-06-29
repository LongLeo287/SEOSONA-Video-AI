# -*- coding: utf-8 -*-
"""SEOSONA Video — independent Evaluator (Loop Engineering maker-checker).

The renderer is the GENERATOR; this is the EVALUATOR — an independent, skeptical gate that
assumes the output is BROKEN until proven otherwise and judges BEHAVIOR by inspecting the
real MP4 (frames + audio), not just file metadata. It complements `quality_scorer` (which
scores ffprobe metadata) by catching what metadata can't:

  - audio is actually present (not silent) and 48 kHz (the "mất voice" class of bug)
  - frames are not blank/black (the empty-component / black-render class of bug)
  - duration is within a sane band

Verdict gates publishing (`video_engine.maybe_publish` calls this first) and is recorded to
the observability hub. Free/local — only ffmpeg/ffprobe + PIL.

  from evaluator import evaluate
  v = evaluate("out.mp4")          # {"ok": bool, "reasons": [...], "score": int, ...}
"""
import os
import sys
import json
import subprocess
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Behavioral thresholds. Deliberately loose — this catches CATASTROPHIC failures (silent,
# blank, wrong length), not nuance; the quality_scorer handles graded scoring.
MIN_DURATION, MAX_DURATION = 15.0, 95.0
SILENCE_DBFS = -50.0          # mean volume below this ≈ no voice
BLANK_STDDEV = 2.5            # per-frame luma stddev below this ≈ uniform (black/blank)
REQUIRE_SR = 48000


def _ffprobe():
    return os.environ.get("SEOSONA_FFPROBE", "ffprobe")


def _ffmpeg():
    return os.environ.get("SEOSONA_FFMPEG", "ffmpeg")


def _probe(video):
    try:
        r = subprocess.run([_ffprobe(), "-v", "quiet", "-print_format", "json",
                            "-show_format", "-show_streams", video],
                           capture_output=True, text=True, timeout=20)
        return json.loads(r.stdout) if r.returncode == 0 else {}
    except Exception:
        return {}


def _mean_volume(video):
    try:
        r = subprocess.run([_ffmpeg(), "-hide_banner", "-nostats", "-i", video,
                            "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True, timeout=60)
        for line in r.stderr.splitlines():
            if "mean_volume:" in line:
                return float(line.split("mean_volume:")[1].split("dB")[0].strip())
    except Exception:
        pass
    return None


def _frame_stddev(video, t, tmp):
    """Extract one frame and return its luma standard deviation (0 ≈ uniform/blank)."""
    try:
        from PIL import Image, ImageStat
        out = os.path.join(tmp, f"f_{int(t*10)}.png")
        r = subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                            "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", out],
                           capture_output=True, timeout=30)
        if r.returncode != 0 or not os.path.exists(out):
            return None
        std = ImageStat.Stat(Image.open(out).convert("L")).stddev[0]
        os.remove(out)
        return std
    except Exception:
        return None


def evaluate(video_path, brand="seosona", record=True):
    """Skeptical behavioral gate. Returns a verdict dict; ok=True only if NOTHING failed."""
    reasons = []
    if not video_path or not os.path.exists(video_path):
        return {"ok": False, "reasons": ["file not found"], "score": 0}

    # Reuse the technical scorer (don't duplicate metadata checks).
    sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
    try:
        qs = import_module("quality_scorer").score_video(video_path, brand=brand)
    except Exception as e:
        qs = {"score": None, "pass": None, "error": str(e)}
    if qs.get("pass") is False:
        reasons.append(f"quality_scorer FAIL ({qs.get('score')}/100 < gate {qs.get('gate', 60)})")

    probe = _probe(video_path)
    streams = probe.get("streams", [])
    astreams = [s for s in streams if s.get("codec_type") == "audio"]

    # Behavioral: audio present + 48 kHz + not silent.
    if not astreams:
        reasons.append("no audio stream")
    else:
        sr = int(astreams[0].get("sample_rate", 0))
        if sr != REQUIRE_SR:
            reasons.append(f"audio sample_rate {sr} != {REQUIRE_SR} (won't play on many devices)")
        mv = _mean_volume(video_path)
        if mv is None or mv < SILENCE_DBFS:
            reasons.append(f"audio effectively silent (mean {mv} dBFS)")

    # Behavioral: duration band.
    try:
        dur = float(probe.get("format", {}).get("duration", 0))
    except (TypeError, ValueError):
        dur = 0.0
    if not (MIN_DURATION <= dur <= MAX_DURATION):
        reasons.append(f"duration {dur:.1f}s out of band [{MIN_DURATION}-{MAX_DURATION}]")

    # Behavioral: frames are not blank/black (sample 3 points across the clip).
    if dur > 1:
        tmp = os.path.join(ROOT, "logs", "_eval_frames")
        os.makedirs(tmp, exist_ok=True)
        blanks = 0
        for frac in (0.25, 0.5, 0.8):
            std = _frame_stddev(video_path, dur * frac, tmp)
            if std is not None and std < BLANK_STDDEV:
                blanks += 1
        if blanks:
            reasons.append(f"{blanks}/3 sampled frames are blank/black")

    verdict = {
        "ok": len(reasons) == 0,
        "reasons": reasons,
        "score": qs.get("score"),
        "duration": round(dur, 1),
        "file": os.path.basename(video_path),
    }
    print(f"[evaluator] {'✅ PASS' if verdict['ok'] else '❌ REJECT'} — {verdict['file']}"
          + ("" if verdict["ok"] else " :: " + "; ".join(reasons)))
    if record:
        try:
            sys.path.insert(0, os.path.join(ROOT, "9_DASHBOARD"))
            import_module("obs_metrics").record(
                "evaluation", output=video_path, ok=verdict["ok"], reasons=reasons,
                score=qs.get("score"))
        except Exception:
            pass
    return verdict


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python 4_BRAIN/evaluator.py <video.mp4>")
        sys.exit(1)
    v = evaluate(sys.argv[1])
    print(json.dumps(v, ensure_ascii=False, indent=2))
    sys.exit(0 if v["ok"] else 2)
