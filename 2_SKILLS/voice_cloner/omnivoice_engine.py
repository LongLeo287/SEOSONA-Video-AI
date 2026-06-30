# -*- coding: utf-8 -*-
"""OmniVoice engine — the SEOSONA + CQA brand voice (k2-fsa/OmniVoice, local, VN-trained 8482h).

Runs OmniVoice in its isolated torch-2.8 venv (`7_ASSETS/voice/.venv-omnivoice`) via subprocess —
the main render venv is torch 2.5, so this mirrors the LoRA bridge pattern. Default clone reference =
the cleaned Chí Quyết (CQA) voice; the SAME voice is used for both brands per the brand decision.

Output is post-processed to read cleanly: internal long silences trimmed (no dead gaps) and loudness
normalized. Returns the wav path, or None to let voice_router fall back to VieNeu.
"""
import os
import sys
import subprocess
import tempfile
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_VENV = os.path.join(ROOT, "7_ASSETS", "voice", ".venv-omnivoice", "Scripts", "python.exe")
_DEFAULT_REF = os.path.join(ROOT, "7_ASSETS", "voice", "profiles", "cqa_omnivoice_ref.wav")
_DEFAULT_REF_TXT = os.path.join(ROOT, "7_ASSETS", "voice", "profiles", "cqa_omnivoice_ref.txt")
_MODEL = os.environ.get("SEOSONA_OMNIVOICE_MODEL", "k2-fsa/OmniVoice")


def available():
    return os.path.exists(_VENV)


def _ffmpeg():
    try:
        return import_module("native_composer")._ffmpeg_bin()
    except Exception:
        return "ffmpeg"


def _ref_text(reference_audio):
    """ref_text for a reference clip: the sibling .txt, else transcribe once (cached)."""
    sib = os.path.splitext(reference_audio)[0] + ".txt"
    if os.path.exists(sib):
        return open(sib, encoding="utf-8").read().strip()
    try:
        asr = import_module("2_SKILLS.srt_maker.asr_router")
        w = asr.transcribe_words(reference_audio, language="vi") or []
        t = " ".join(x["word"] for x in w)
        open(sib, "w", encoding="utf-8").write(t)
        return t
    except Exception:
        return ""


def _post_process(raw, out):
    """Trim internal long silences (no dead gaps) + loudnorm + 48k → the clean delivered wav."""
    r = subprocess.run(
        [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", raw,
         "-af", "silenceremove=stop_periods=-1:stop_threshold=-38dB:stop_duration=0.35:"
                "start_periods=1:start_threshold=-38dB,loudnorm=I=-16:TP=-1.5,aresample=48000",
         out], capture_output=True)
    if r.returncode == 0 and os.path.exists(out):
        return out
    # if post-process fails, deliver the raw synth rather than nothing
    try:
        import shutil
        shutil.copy(raw, out)
        return out
    except Exception:
        return None


def synthesize(text, audio_out, *, reference_audio=None, ref_text=None, language="vi"):
    """Synthesize `text` in the brand (CQA) voice via OmniVoice. Returns audio_out or None."""
    if not available():
        print("[OmniVoice] venv not found — falling back.")
        return None
    ref = reference_audio if (reference_audio and os.path.exists(reference_audio)) else _DEFAULT_REF
    if not os.path.exists(ref):
        print("[OmniVoice] no reference clip — falling back.")
        return None
    rtext = ref_text or _ref_text(ref)
    raw = os.path.join(tempfile.gettempdir(), "omnivoice_raw.wav")
    cmd = [_VENV, "-m", "omnivoice.cli.infer", "--model", _MODEL, "--language", language,
           "--text", text, "--ref_audio", os.path.abspath(ref), "--ref_text", rtext,
           "--output", raw]
    print(f"[OmniVoice] synth (brand voice, ref={os.path.basename(ref)})…")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", HF_HUB_DISABLE_SYMLINKS_WARNING="1")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=env,
                           timeout=int(os.environ.get("SEOSONA_OMNIVOICE_TIMEOUT", "1200")))
    except subprocess.TimeoutExpired:
        print("[OmniVoice] timeout — falling back.")
        return None
    if r.returncode != 0 or not os.path.exists(raw):
        print(f"[OmniVoice] synth failed (rc={r.returncode}) — falling back. {r.stderr[-200:]}")
        return None
    os.makedirs(os.path.dirname(os.path.abspath(audio_out)) or ".", exist_ok=True)
    return _post_process(raw, audio_out)


if __name__ == "__main__":
    txt = sys.argv[1] if len(sys.argv) > 1 else "Xin chào, đây là SEOSONA."
    out = os.path.join(tempfile.gettempdir(), "omnivoice_engine_demo.wav")
    print("result:", synthesize(txt, out))
