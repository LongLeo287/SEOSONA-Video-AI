"""Engine #5 — LivePortrait motion: animate a still portrait (head pose + blinks + micro-expression).

Commercial-clean: LivePortrait's code + animation models are MIT (Kuaishou); its InsightFace detector
(non-commercial models) is swapped for MediaPipe FaceMesh (see the toolkit's face_analysis_mediapipe.py).
So no InsightFace weights are used and the output is safe for commercial video.

Pipeline role: still photo -> LivePortrait (alive head motion) -> MuseTalk re-lips to the CQA audio.
The driving template supplies the MOTION (its lips are irrelevant — MuseTalk overwrites them), so a
`driving_multiplier < 1` keeps a news-presenter subtle rather than the template's full expressions.

  python scripts/liveportrait_motion.py --source face.jpg --out animated.mp4 [--driving d0.mp4] [--amount 0.6]
"""
import argparse
import glob
import os
import shutil
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LP_DIR = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "LivePortrait")
VENV_PY = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", ".venv-liveportrait", "Scripts", "python.exe")
DEFAULT_DRIVING = os.path.join(LP_DIR, "assets", "examples", "driving", "d0.mp4")


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _dur(path):
    fp = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffprobe.exe")
    fp = fp if os.path.exists(fp) else "ffprobe"
    try:
        return float(subprocess.run([fp, "-v", "error", "-show_entries", "format=duration",
                                     "-of", "default=nk=1:nw=1", path], capture_output=True,
                                    text=True, timeout=30).stdout.strip())
    except Exception:
        return 0.0


def animate(source, out_mp4, driving=None, amount=0.6, loop_to=None, region="all"):
    """Animate `source` still with `driving` motion (scaled by `amount`). If loop_to (seconds) is given,
    the result is looped/trimmed to that length (so it can cover a longer audio track downstream).
    region: which motion to transfer — "all" | "pose" (head only) | "exp" | "lip" | "eyes"."""
    if not os.path.exists(VENV_PY):
        raise RuntimeError(f"LivePortrait venv missing: {VENV_PY}")
    driving = driving or DEFAULT_DRIVING
    out_mp4 = os.path.abspath(out_mp4)
    work = os.path.join(os.path.dirname(out_mp4) or ".", "_lp_out")
    os.makedirs(work, exist_ok=True)

    cmd = [VENV_PY, "inference.py", "-s", os.path.abspath(source), "-d", os.path.abspath(driving),
           "-o", work, "--driving_multiplier", str(amount), "--flag_pasteback",
           "--animation_region", region]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    env["PATH"] = os.path.join(ROOT, "node_modules", "ffmpeg-static") + os.pathsep + env.get("PATH", "")
    print(f"[liveportrait_motion] animate {os.path.basename(source)} (amount={amount})")
    proc = subprocess.run(cmd, cwd=LP_DIR, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=1800)
    if proc.returncode != 0:
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-20:]
        raise RuntimeError("LivePortrait failed:\n" + "\n".join(tail))

    # pick the non-concat output (the plain animated video, not the side-by-side)
    mp4s = [p for p in glob.glob(os.path.join(work, "**", "*.mp4"), recursive=True) if "_concat" not in p]
    if not mp4s:
        raise RuntimeError("LivePortrait produced no mp4")
    animated = max(mp4s, key=os.path.getmtime)

    if loop_to and _dur(animated) + 0.05 < loop_to:
        looped = os.path.join(work, "looped.mp4")
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-stream_loop", "-1",
                        "-i", animated, "-t", f"{loop_to:.3f}", "-c", "copy", looped], check=True)
        animated = looped
    shutil.copy2(animated, out_mp4)
    print(f"[liveportrait_motion] OK {out_mp4}")
    return out_mp4


def main():
    ap = argparse.ArgumentParser(description="LivePortrait: animate a still portrait (commercial-clean)")
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--driving", default=None, help="driving motion template (default d0.mp4)")
    ap.add_argument("--amount", type=float, default=0.6, help="motion strength 0..1 (subtle < 1)")
    ap.add_argument("--loop-to", type=float, default=None, help="loop/trim output to N seconds")
    a = ap.parse_args()
    animate(a.source, a.out, driving=a.driving, amount=a.amount, loop_to=a.loop_to)


if __name__ == "__main__":
    raise SystemExit(main())
