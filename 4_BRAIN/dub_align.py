"""dub_align — fit per-line dubbed TTS audio onto an existing video timeline (Engine #4 keystone).

The problem: translating a 3.0s source line often yields 4.2s of TTS; naive concatenation drifts the
whole video out of sync. This module reconciles each subtitle slot's dub against its slot length.

CLEAN-ROOM NOTE: this is an independent implementation of the well-known "dub-to-timeline" strategy
(timeline-extension first, then speed audio / slow video / split-the-deficit). It was written from the
documented ALGORITHM, not from any GPL source — no code was copied from pyvideotrans (GPL-3.0), which
is logged as a REFERENCE study only. Keep it that way.

Two strategies:
  align_fit()      preserve the original timeline, fit each dub into its (gap-extended) slot.
  align_natural()  don't time-stretch; concat dubs back-to-back (optionally dropping mid silence) and
                   RETURN the new per-line timings so captions can be re-synced.

Segments in: list of {"start": sec, "end": sec, "wav": path}. Uses ffmpeg only (no new deps).
"""
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# If a dub is only slightly long (<= this ratio), speeding the AUDIO alone is imperceptible; beyond it,
# split the deficit between speeding audio and slowing video (matches the standard 1.2x threshold).
BOTH_MODE_AUDIO_ONLY_THRESHOLD = 1.2
MAX_ATEMPO_STEP = 2.0                     # ffmpeg atempo is valid in [0.5, 2.0]; chain for bigger factors


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _ffprobe():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffprobe.exe")
    return p if os.path.exists(p) else "ffprobe"


def _dur(wav):
    out = subprocess.run([_ffprobe(), "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nk=1:nw=1", wav], capture_output=True, text=True, timeout=30)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def _atempo_chain(factor):
    """Return an atempo filter string realising `factor` speed-up (>1 faster) via steps in [0.5,2.0]."""
    if abs(factor - 1.0) < 1e-3:
        return "atempo=1.0"
    steps, f = [], factor
    while f > MAX_ATEMPO_STEP:
        steps.append(MAX_ATEMPO_STEP); f /= MAX_ATEMPO_STEP
    while f < 0.5:
        steps.append(0.5); f /= 0.5
    steps.append(round(f, 4))
    return ",".join(f"atempo={s}" for s in steps)


def fit_audio_to(src_wav, target_sec, out_wav, *, sr=24000):
    """Make src_wav exactly target_sec long: speed it up if too long, pad tail silence if too short."""
    src = _dur(src_wav)
    if src <= 0 or target_sec <= 0:
        # degenerate → just emit target_sec of silence
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                        "-t", f"{max(0.05, target_sec):.3f}", "-i", f"anullsrc=r={sr}:cl=mono",
                        "-ar", str(sr), "-ac", "1", out_wav], check=True)
        return out_wav
    af = []
    if src > target_sec * 1.002:                       # too long → speed up
        af.append(_atempo_chain(src / target_sec))
    af.append("apad")                                   # pad if short (harmless if already long)
    af.append(f"atrim=end={target_sec:.3f}")            # then trim to the exact slot length
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", src_wav,
                    "-af", ",".join(af), "-ar", str(sr), "-ac", "1", out_wav], check=True)
    return out_wav


def plan(segments, total_dur=None):
    """Timeline-extension pass: give each slot the gap up to the next segment's start, so the required
    speed-up drops. Returns [{start, slot_sec, dub_sec, ratio, strategy}]."""
    segs = sorted(segments, key=lambda s: s["start"])
    out = []
    for i, s in enumerate(segs):
        nxt = segs[i + 1]["start"] if i + 1 < len(segs) else (total_dur if total_dur else s["end"])
        slot = max(0.1, nxt - s["start"])              # extend end to next start (absorb silent gap)
        dub = _dur(s["wav"])
        ratio = dub / slot if slot else 1.0
        if ratio <= 1.0:
            strat = "pad"                               # dub fits — pad tail silence
        elif ratio <= BOTH_MODE_AUDIO_ONLY_THRESHOLD:
            strat = "audio"                             # small overflow — speed audio only (imperceptible)
        else:
            strat = "both"                              # large — split deficit 50/50 (audio↑ + video↓)
        out.append({"start": s["start"], "slot_sec": round(slot, 3), "dub_sec": round(dub, 3),
                    "ratio": round(ratio, 3), "strategy": strat, "wav": s["wav"]})
    return out


def align_fit(segments, out_wav, *, total_dur=None, sr=24000):
    """Preserve the original timeline. Fit each dub to its gap-extended slot, then lay every fitted clip
    at its start on a silent bed → one dubbed track that stays in sync with the source video."""
    p = plan(segments, total_dur)
    work = os.path.join(os.path.dirname(os.path.abspath(out_wav)) or ".", "_dubalign")
    os.makedirs(work, exist_ok=True)
    total = total_dur or (max(s["start"] + s["slot_sec"] for s in p) if p else 1.0)

    inputs, filters, mix = [], [], []
    for i, s in enumerate(p):
        fitted = os.path.join(work, f"seg_{i:04d}.wav")
        fit_audio_to(s["wav"], s["slot_sec"], fitted, sr=sr)
        inputs += ["-i", fitted]
        delay_ms = int(round(s["start"] * 1000))
        filters.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[d{i}]")
        mix.append(f"[d{i}]")
    if not inputs:
        raise RuntimeError("no segments to align")
    fc = ";".join(filters) + f";{''.join(mix)}amix=inputs={len(mix)}:normalize=0[out]"
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", *inputs,
                    "-filter_complex", fc, "-map", "[out]",
                    "-t", f"{total:.3f}", "-ar", str(sr), "-ac", "1", out_wav], check=True)
    return out_wav, p


def align_natural(segments, out_wav, *, drop_silence=True, gap_sec=0.12, sr=24000):
    """Don't time-stretch. Concatenate dubs in order (optionally dropping the original inter-line gaps),
    and RETURN the new per-line {start,end} so captions/subtitles can be re-timed to the new audio."""
    segs = sorted(segments, key=lambda s: s["start"])
    work = os.path.join(os.path.dirname(os.path.abspath(out_wav)) or ".", "_dubnat")
    os.makedirs(work, exist_ok=True)
    listf = os.path.join(work, "concat.txt")
    new_times, t = [], 0.0
    silence = os.path.join(work, "gap.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-t", f"{gap_sec:.3f}", "-i", f"anullsrc=r={sr}:cl=mono", silence], check=True)
    lines = []
    for i, s in enumerate(segs):
        d = _dur(s["wav"])
        new_times.append({"start": round(t, 3), "end": round(t + d, 3), "text": s.get("text", "")})
        lines.append(f"file '{os.path.abspath(s['wav'])}'")
        t += d
        if not drop_silence and i + 1 < len(segs):
            lines.append(f"file '{os.path.abspath(silence)}'"); t += gap_sec
    with open(listf, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
                    "-safe", "0", "-i", listf, "-ar", str(sr), "-ac", "1", out_wav], check=True)
    return out_wav, new_times


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Fit dubbed audio to a video timeline (Engine #4 keystone)")
    ap.add_argument("--segments", required=True, help="JSON file: [{start,end,wav,text?}, ...]")
    ap.add_argument("--out", required=True)
    ap.add_argument("--natural", action="store_true", help="concat mode (returns re-timed segments)")
    ap.add_argument("--total", type=float, default=None, help="total video duration (sec)")
    a = ap.parse_args()
    segs = json.load(open(a.segments, encoding="utf-8"))
    if a.natural:
        out, times = align_natural(segs, a.out)
        print(json.dumps({"out": out, "new_times": times}, ensure_ascii=False, indent=2))
    else:
        out, p = align_fit(segs, a.out, total_dur=a.total)
        print(json.dumps({"out": out, "plan": p}, ensure_ascii=False, indent=2))
