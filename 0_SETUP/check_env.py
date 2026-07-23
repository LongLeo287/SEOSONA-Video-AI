# -*- coding: utf-8 -*-
"""SEOSONA Video — environment status checker (the management dashboard).

ONE place to see what's installed and what's missing. Run on this machine or after cloning to a new
one to know exactly what to set up. Read-only — it never installs anything (use bootstrap.ps1 for that).

    python 0_SETUP/check_env.py
"""
import os
import sys
import shutil
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOME = os.path.expanduser("~")
OK, BAD, WARN = "  OK  ", "MISSING", " WARN "


def _py(venv):
    return os.path.join(venv, "Scripts", "python.exe")


def _probe(py, code):
    """Return (ok, text) from running `code` in interpreter `py`."""
    if not os.path.exists(py):
        return False, "interpreter not found"
    try:
        r = subprocess.run([py, "-c", code], capture_output=True, text=True, timeout=120)
        return r.returncode == 0, (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else ""
    except Exception as e:
        return False, str(e)[:80]


def line(status, name, detail=""):
    print(f"  [{status}] {name:<34} {detail}")


def main():
    print("=" * 72)
    print("  SEOSONA VIDEO — ENVIRONMENT STATUS")
    print("=" * 72)

    # ---- Python virtual environments ----
    print("\nPYTHON ENVIRONMENTS")
    main_py = os.environ.get("SEOSONA_MAIN_PY") or sys.executable  # the hermes inference venv
    ok, v = _probe(main_py, "import sys,torch;print('py',sys.version.split()[0],'torch',torch.__version__,'cuda',torch.cuda.is_available())")
    line(OK if ok else BAD, "main / inference venv", v)
    for label, venv, probe in [
        ("OmniVoice venv (torch CUDA)", os.path.join(ROOT, "7_ASSETS/voice/.venv-omnivoice"),
         "import torch,omnivoice;print('torch',torch.__version__,'cuda',torch.cuda.is_available())"),
    ]:
        py = _py(venv)
        ok, v = _probe(py, probe)
        st = OK if ok else (WARN if "OBSOLETE" in label else BAD)
        line(st, label, v or ("not present" if not os.path.exists(py) else ""))

    # ---- key Python packages (main venv) ----
    print("\nKEY PACKAGES (main venv)")
    for pkg, imp in [("faster-whisper (ASR)", "faster_whisper"),
                     ("ctranslate2", "ctranslate2"), ("moviepy (mux)", "moviepy"),
                     ("soundfile", "soundfile"), ("librosa", "librosa"),
                     ("markitdown (ingest)", "markitdown"), ("yt-dlp (sourcing)", "yt_dlp"),
                     ("playwright (publish)", "playwright")]:
        ok, _ = _probe(main_py, f"import {imp}")
        line(OK if ok else BAD, pkg)

    # ---- models ----
    print("\nMODELS")
    models = [
        ("PhoWhisper-large CT2 (ASR, HF cache)", os.path.join(HOME, ".cache/huggingface/hub/models--kiendt--PhoWhisper-large-ct2")),
        ("OmniVoice (brand voice, HF cache)", os.path.join(HOME, ".cache/huggingface/hub/models--k2-fsa--OmniVoice")),
        ("CQA brand-voice reference", os.path.join(ROOT, "7_ASSETS/voice/profiles/cqa_omnivoice_ref.wav")),
    ]
    for name, p in models:
        line(OK if os.path.exists(p) else BAD, name)

    # ---- node + system tools ----
    print("\nNODE + TOOLS")
    line(OK if shutil.which("node") else BAD, "node", subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip() if shutil.which("node") else "")
    line(OK if os.path.isdir(os.path.join(ROOT, "node_modules")) else BAD, "node_modules (npm install)")
    line(OK if os.path.exists(os.path.join(ROOT, "node_modules/hyperframes/dist/cli.js")) else BAD, "hyperframes (render engine)")
    ff = os.path.join(ROOT, "node_modules/ffmpeg-static/ffmpeg.exe")
    line(OK if os.path.exists(ff) else BAD, "ffmpeg (ffmpeg-static)")
    for t in ("git", "uv"):
        line(OK if shutil.which(t) else WARN, t)

    print("\n" + "=" * 72)
    print("  Missing items → see 0_SETUP/ENVIRONMENT.md + run 0_SETUP/bootstrap.ps1")
    print("=" * 72)


if __name__ == "__main__":
    main()
