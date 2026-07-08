# -*- coding: utf-8 -*-
"""Best cover-frame scorer — pick the SHARPEST, best-exposed, most-informative frame of a video for a
poster/thumbnail, instead of grabbing one blindly at a fixed timestamp (which often lands on a blurry
crossfade or a near-black transition frame).

Native re-implementation of Katna's frame-scoring idea (blur = variance-of-Laplacian, plus brightness +
entropy), using ONLY ffmpeg (already required) + Pillow. Katna itself is avoided: it pins OpenCV and caps
at Python 3.6-3.9. This stays dependency-light and Py3.10+ safe.

    from frame_scorer import best_frame
    best_frame("out.mp4", "Thumbnail/cover.png")     # → path to the chosen frame, or None

Best-effort: any failure returns None so the caller can fall back to a plain grab. Never raises.
"""
import os
import shutil
import tempfile
import subprocess

# Sample window — skip the very start/end (title cards, fade-outs) and spread candidates across the body.
_START_FRAC = 0.06
_END_FRAC = 0.92
_N = 9
_ANALYZE_W = 320          # downscale before scoring — Laplacian variance is scale-tolerant and this is fast
_TARGET_LUMA = 128.0      # mid-exposure target; both crushed blacks and blown highlights score lower
_W_SHARP, _W_ENTROPY, _W_BRIGHT = 0.5, 0.3, 0.2   # blur is the worst thumbnail sin → sharpness dominates


def _ffmpeg():
    return os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or "ffmpeg"


def _ffprobe():
    return os.environ.get("FFPROBE_BIN") or shutil.which("ffprobe") or "ffprobe"


def _duration(video):
    try:
        r = subprocess.run([_ffprobe(), "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", video], capture_output=True, text=True, timeout=30)
        return float((r.stdout or "").strip())
    except Exception:
        return 0.0


def _grab(video, t, dst):
    """Extract one frame at time `t` (seconds) to `dst` PNG. True on success."""
    try:
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", dst],
                       check=True, timeout=60)
        return os.path.exists(dst) and os.path.getsize(dst) > 0
    except Exception:
        return False


def _scores(png):
    """(sharpness, entropy, brightness_luma) for one frame, or None on failure. All raw — normalized later."""
    try:
        from PIL import Image, ImageFilter, ImageStat
        im = Image.open(png).convert("L")
        w, h = im.size
        if w > _ANALYZE_W:
            im = im.resize((_ANALYZE_W, max(1, round(h * _ANALYZE_W / w))))
        # sharpness = variance of the Laplacian (high on crisp edges, ~0 on blur/flat). offset=128 centres
        # the response so NEGATIVE edges (dark-text-on-light — SEOSONA's own style) aren't clamped to 0:
        # with offset=0 a blurred frame's positive noise survives while its negatives clamp away, inflating
        # its variance so blur looks falsely sharp. Centring at 128 sharpened sharp-vs-blur separation ~5×.
        lap = im.filter(ImageFilter.Kernel((3, 3), [0, -1, 0, -1, 4, -1, 0, -1, 0], scale=1, offset=128))
        sharp = ImageStat.Stat(lap).var[0]
        entropy = im.entropy()                 # information/detail — low on blank or single-tone frames
        luma = ImageStat.Stat(im).mean[0]
        return (sharp, entropy, luma)
    except Exception:
        return None


def _bright_score(luma):
    """1.0 at the mid-exposure target, falling off toward crushed (0) or blown (255)."""
    return max(0.0, 1.0 - abs(luma - _TARGET_LUMA) / _TARGET_LUMA)


def _norm(vals):
    lo, hi = min(vals), max(vals)
    rng = hi - lo
    return [(v - lo) / rng if rng > 1e-9 else 0.5 for v in vals]


def best_frame(video, out_png, n=_N, start_frac=_START_FRAC, end_frac=_END_FRAC, verbose=False):
    """Sample `n` frames across the video body, score each (sharpness+entropy+brightness), copy the best to
    `out_png`. Returns `out_png` on success, else None (caller should fall back to a plain grab)."""
    dur = _duration(video)
    if dur <= 0:
        return None
    a, b = dur * start_frac, dur * end_frac
    if b <= a:
        a, b = 0.0, dur
    n = max(2, int(n))
    times = [a + (b - a) * i / (n - 1) for i in range(n)]
    tmp = tempfile.mkdtemp(prefix="cover_")
    try:
        cand = []           # (t, png, raw_scores)
        for i, t in enumerate(times):
            p = os.path.join(tmp, f"c{i}.png")
            if _grab(video, t, p):
                s = _scores(p)
                if s:
                    cand.append((t, p, s))
        if not cand:
            return None
        sharp_n = _norm([c[2][0] for c in cand])
        ent_n = _norm([c[2][1] for c in cand])
        bright = [_bright_score(c[2][2]) for c in cand]
        best_i, best_score = 0, -1.0
        for i, c in enumerate(cand):
            score = _W_SHARP * sharp_n[i] + _W_ENTROPY * ent_n[i] + _W_BRIGHT * bright[i]
            if verbose:
                print(f"  t={c[0]:5.2f}s  sharp={c[2][0]:8.1f} ent={c[2][1]:.2f} luma={c[2][2]:5.1f} -> {score:.3f}")
            if score > best_score:
                best_i, best_score = i, score
        os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
        shutil.copy(cand[best_i][1], out_png)
        if verbose:
            print(f"  → picked t={cand[best_i][0]:.2f}s (score {best_score:.3f}) → {out_png}")
        return out_png
    except Exception:
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import sys
    v = sys.argv[1] if len(sys.argv) > 1 else "8_WORKSPACE/_comptest/comptest.mp4"
    o = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(v) or ".", "cover_best.png")
    print("result:", best_frame(v, o, verbose=True))
