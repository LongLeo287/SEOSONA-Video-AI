"""Engine #3 — Portrait Avatar: still photo + audio → lip-synced talking clip (SadTalker, Apache-2.0).

Runs SadTalker in its ISOLATED venv (2_KNOWLEDGE/external_toolkits/.venv-sadtalker) as a subprocess,
so it never touches the hermes inference/harness env. Pairs with SEOSONA's own voice (OmniVoice/VieNeu):
give it a lecturer photo + a voice.mp3 and it returns a talking-head clip that can be composited with
the talking-head engine's karaoke captions + element layer.

  python scripts/portrait_avatar.py --image face.png --audio voice.mp3 --out clip.mp4 [--enhance] [--size 512]
"""
import argparse
import os
import subprocess
import sys
import glob
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ST_DIR = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "SadTalker")
VENV_PY = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", ".venv-sadtalker", "Scripts", "python.exe")


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _to_wav(audio, work):
    """SadTalker is happiest with a 16k mono wav; convert whatever we're given."""
    if audio.lower().endswith(".wav"):
        return audio
    wav = os.path.join(work, "driven.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", audio, "-ar", "16000", "-ac", "1", wav], check=True)
    return wav


def make_avatar(image, audio, out_mp4, *, still=True, enhance=False, size=256, preprocess="full"):
    if not os.path.exists(VENV_PY):
        raise RuntimeError(f"SadTalker venv missing: {VENV_PY} — run the Engine #3 setup first")
    for p in ("checkpoints/SadTalker_V0.0.2_256.safetensors",):
        if not os.path.exists(os.path.join(ST_DIR, p)):
            raise RuntimeError(f"SadTalker weights missing ({p}) — download them first")

    out_mp4 = os.path.abspath(out_mp4)
    result_dir = os.path.join(os.path.dirname(out_mp4) or ".", "_sadtalker_out")
    os.makedirs(result_dir, exist_ok=True)
    wav = _to_wav(os.path.abspath(audio), result_dir)

    cmd = [VENV_PY, "inference.py",
           "--source_image", os.path.abspath(image),
           "--driven_audio", wav,
           "--result_dir", result_dir,
           "--checkpoint_dir", "checkpoints",
           "--size", str(size),
           "--preprocess", preprocess]
    if still:
        cmd.append("--still")          # less head motion — steadier for a lecturer talking to camera
    if enhance:
        cmd += ["--enhancer", "gfpgan"]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    print(f"[portrait_avatar] SadTalker: {os.path.basename(image)} + {os.path.basename(audio)} → {out_mp4}")
    proc = subprocess.run(cmd, cwd=ST_DIR, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=1800)
    if proc.returncode != 0:
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-15:]
        raise RuntimeError("SadTalker failed:\n" + "\n".join(tail))

    # SadTalker writes a timestamped .mp4 under result_dir — grab the newest
    mp4s = sorted(glob.glob(os.path.join(result_dir, "**", "*.mp4"), recursive=True), key=os.path.getmtime)
    if not mp4s:
        raise RuntimeError("SadTalker produced no mp4")
    shutil.copy2(mp4s[-1], out_mp4)
    print(f"[portrait_avatar] ✓ {out_mp4}")
    return out_mp4


def main():
    ap = argparse.ArgumentParser(description="Portrait avatar: photo + audio → lip-synced clip (SadTalker)")
    ap.add_argument("--image", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--enhance", action="store_true", help="GFPGAN face enhance (slower, sharper)")
    ap.add_argument("--motion", action="store_true", help="allow head motion (default: still)")
    ap.add_argument("--size", type=int, default=256, choices=[256, 512])
    a = ap.parse_args()
    make_avatar(a.image, a.audio, a.out, still=not a.motion, enhance=a.enhance, size=a.size)


if __name__ == "__main__":
    raise SystemExit(main())
