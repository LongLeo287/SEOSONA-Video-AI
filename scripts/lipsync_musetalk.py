"""Engine #3b — MuseTalk lip-sync: face image OR real video + audio → lip-synced clip.

MuseTalk does latent-space *inpainting* of the mouth region on the SOURCE pixels, so it keeps the
real face and only redraws the lips to match the audio — sharper/more realistic than SadTalker's
full-head synthesis. Runs in an ISOLATED venv (2_KNOWLEDGE/external_toolkits/.venv-musetalk) as a
subprocess, so it never touches the hermes/OmniVoice envs. Pairs with SEOSONA's own CQA voice.

The upstream MuseTalk needs mmcv/mmpose (won't build on Windows); this repo's copy has its face
preprocessing swapped to MediaPipe FaceMesh (see musetalk/utils/preprocessing.py) so it installs
with pure pip — that is what unblocks Engine #3.

  python scripts/lipsync_musetalk.py --face face.png --audio voice.mp3 --out clip.mp4 [--fps 25] [--fp16]
  # --face may be an image (still portrait) OR a video (real footage to re-lip)
"""
import argparse
import glob
import os
import shutil
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MT_DIR = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "MuseTalk")
VENV_PY = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", ".venv-musetalk", "Scripts", "python.exe")
MODELS = os.path.join(MT_DIR, "models")

# Inference-path weights (dwpose skipped — replaced by MediaPipe; syncnet is train-only).
REQUIRED_WEIGHTS = {
    "MuseTalk V1.5 UNet": "musetalkV15/unet.pth",
    "MuseTalk V1.5 config": "musetalkV15/musetalk.json",
    "SD-VAE": "sd-vae/diffusion_pytorch_model.bin",
    "Whisper": "whisper/pytorch_model.bin",
    "Face-parse (bisenet)": "face-parse-bisent/79999_iter.pth",
    "Face-parse (resnet18)": "face-parse-bisent/resnet18-5c106cde.pth",
}


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _to_wav(audio, work, enhance=False):
    """MuseTalk's Whisper feature-extractor wants a wav; convert whatever we're given (16k mono).
    enhance=True (precision mode / HeyGen's enable_speech_enhancement): band-limit to the voice band,
    denoise, and loudness-normalise so the driving audio is cleaner -> steadier viseme prediction."""
    af = "highpass=f=80,lowpass=f=7500,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11" if enhance else None
    if audio.lower().endswith(".wav") and not enhance:
        return audio
    wav = os.path.join(work, "driven.wav")
    cmd = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", audio, "-ar", "16000", "-ac", "1"]
    if af:
        cmd += ["-af", af]
    subprocess.run(cmd + [wav], check=True)
    return wav


def _check_ready():
    if not os.path.exists(VENV_PY):
        raise RuntimeError(f"MuseTalk venv missing: {VENV_PY} — run the Engine #3b setup first")
    missing = [f"{name} ({rel})" for name, rel in REQUIRED_WEIGHTS.items()
               if not os.path.exists(os.path.join(MODELS, rel))]
    if missing:
        raise RuntimeError("MuseTalk weights missing — run scripts/download_musetalk_weights.py:\n  - "
                           + "\n  - ".join(missing))


def make_lipsync(face, audio, out_mp4, *, fps=25, fp16=True, bbox_shift=0, extra_margin=10, mode=None):
    """face (image or video) + audio → lip-synced mp4 at out_mp4.

    mode (HeyGen-style, optional): "speed" -> fp16, raw audio (fast draft); "precision" -> fp32 +
    speech-enhanced driving audio (higher fidelity, slower). If given, it overrides fp16."""
    _check_ready()
    enhance = False
    if mode == "speed":
        fp16 = True
    elif mode == "precision":
        fp16, enhance = False, True
    out_mp4 = os.path.abspath(out_mp4)
    result_dir = os.path.join(os.path.dirname(out_mp4) or ".", "_musetalk_out")
    os.makedirs(result_dir, exist_ok=True)
    wav = _to_wav(os.path.abspath(audio), result_dir, enhance=enhance)

    # MuseTalk drives from a YAML task list (video_path may be an image or a video).
    cfg = os.path.join(result_dir, "seosona_task.yaml")
    # forward slashes so YAML doesn't treat Windows backslashes as escape sequences (Windows accepts them)
    face_y = os.path.abspath(face).replace("\\", "/")
    wav_y = os.path.abspath(wav).replace("\\", "/")
    with open(cfg, "w", encoding="utf-8") as f:
        f.write("task_0:\n")
        f.write(f'  video_path: "{face_y}"\n')
        f.write(f'  audio_path: "{wav_y}"\n')
        f.write(f"  bbox_shift: {bbox_shift}\n")

    cmd = [VENV_PY, "-m", "scripts.inference",
           "--version", "v15",
           "--unet_model_path", "./models/musetalkV15/unet.pth",
           "--unet_config", "./models/musetalkV15/musetalk.json",
           "--vae_type", "sd-vae",
           "--whisper_dir", "./models/whisper",
           "--inference_config", cfg,
           "--result_dir", result_dir,
           "--fps", str(fps),
           "--extra_margin", str(extra_margin),
           "--parsing_mode", "jaw",
           "--ffmpeg_path", os.path.dirname(_ffmpeg()) or "."]
    if fp16:
        cmd.append("--use_float16")

    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", HF_HUB_OFFLINE="1")
    print(f"[lipsync_musetalk] {os.path.basename(face)} + {os.path.basename(audio)} -> {out_mp4}")
    proc = subprocess.run(cmd, cwd=MT_DIR, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=3600)
    if proc.returncode != 0:
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-25:]
        raise RuntimeError("MuseTalk failed:\n" + "\n".join(tail))

    mp4s = sorted(glob.glob(os.path.join(result_dir, "**", "*.mp4"), recursive=True), key=os.path.getmtime)
    if not mp4s:
        # inference.py swallows per-task errors (prints then exits 0) — surface its captured output.
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-30:]
        raise RuntimeError("MuseTalk produced no mp4. Engine output tail:\n" + "\n".join(tail))
    shutil.copy2(mp4s[-1], out_mp4)
    print(f"[lipsync_musetalk] OK {out_mp4}")
    return out_mp4


def main():
    ap = argparse.ArgumentParser(description="MuseTalk lip-sync: face (image/video) + audio → clip")
    ap.add_argument("--face", required=True, help="source image OR video of a face")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--fp16", action="store_true", default=True)
    ap.add_argument("--no-fp16", dest="fp16", action="store_false")
    ap.add_argument("--bbox-shift", type=int, default=0, help="nudge the mouth crop up/down if lips drift")
    ap.add_argument("--mode", choices=["speed", "precision"], default=None,
                    help="speed=fp16 fast draft; precision=fp32 + speech-enhanced audio (overrides --fp16)")
    a = ap.parse_args()
    make_lipsync(a.face, a.audio, a.out, fps=a.fps, fp16=a.fp16, bbox_shift=a.bbox_shift, mode=a.mode)


if __name__ == "__main__":
    raise SystemExit(main())
