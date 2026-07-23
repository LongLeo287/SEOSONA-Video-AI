# -*- coding: utf-8 -*-
"""Talking-head step 1 — transcribe footage to word-level timestamps.

    python scripts/talking_head_transcribe.py --video <mp4> --out <dir>

Reuses the project ASR router (PhoWhisper-large primary → generic faster-whisper backup).
Writes <out>/words.json = [{"word","start","end"}, ...]. Then hand-edit brand spelling
into <out>/words_fixed.json before running edit_footage (see the talking-head SKILL).
"""
import os, sys, json, argparse, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, os.path.join(ROOT, "4_BRAIN")):
    if p not in sys.path:
        sys.path.insert(0, p)

from native_composer import _ffmpeg_bin  # concrete ffmpeg (PATH-independent)


def extract_audio(video, out_wav):
    subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", video, "-vn", "-ac", "1", "-ar", "16000", out_wav], check=True)
    return out_wav


def main():
    ap = argparse.ArgumentParser(description="Footage → word-level transcript (words.json)")
    ap.add_argument("--video", required=True, help="input footage .mp4")
    ap.add_argument("--out", default=None,
                    help="output dir (gets words.json); default = 8_WORKSPACE/<video-name>")
    ap.add_argument("--lang", default="vi")
    a = ap.parse_args()

    if not os.path.isfile(a.video):
        raise SystemExit(f"video not found: {a.video}")
    # Anchor the default under 8_WORKSPACE (repo-root-relative, NOT CWD) — a bare relative default
    # ("selfshot") littered stray dirs wherever the script happened to be invoked from.
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_out = os.path.join(root, "8_WORKSPACE",
                               os.path.splitext(os.path.basename(a.video))[0])
    out_dir = (a.out if os.path.isabs(a.out) else os.path.join(os.getcwd(), a.out)) if a.out \
        else default_out
    os.makedirs(out_dir, exist_ok=True)

    wav = os.path.join(out_dir, "_audio.wav")
    print(f"[transcribe] extracting audio → {wav}")
    extract_audio(a.video, wav)

    asr = __import__("2_SKILLS.srt_maker.asr_router", fromlist=["x"])
    print("[transcribe] running ASR router…")
    words = asr.transcribe_words(wav, language=a.lang) or []
    for w in words:
        w["duration"] = round(float(w.get("end", 0)) - float(w.get("start", 0)), 3)

    words_path = os.path.join(out_dir, "words.json")
    with open(words_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    try:
        os.remove(wav)
    except OSError:
        pass
    print(f"[transcribe] {len(words)} words → {words_path}")
    print("[transcribe] NEXT: copy to words_fixed.json, fix brand spelling (Claude/Hermes/AI/24-7), "
          "then run scripts/talking_head_edit.py")


if __name__ == "__main__":
    main()
