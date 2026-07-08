# -*- coding: utf-8 -*-
"""Footage sourcing — thin yt-dlp wrapper (ADOPT from REPO VIDEO.txt vetting, Unlicense).

Download source lectures / B-roll for the course-repurpose pipeline. yt-dlp is a pinned tool
dependency (already installed); this is a thin, factory-friendly wrapper — NOT a vendored copy.

    python scripts/source_footage.py <url> [--out 0_INPUT_INBOX] [--audio] [--max-h 1920]

COMPLIANCE: downloaded material is for reference / B-roll / your-own-channel re-use only — it is the
factory's job to RESPECT copyright + platform ToS. Do not redistribute third-party content.
"""
import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def download(url, out_dir=None, audio_only=False, max_h=1920):
    """Download a single URL via yt-dlp → returns the saved file path (or None)."""
    try:
        import yt_dlp
    except ImportError:
        print("[source] yt-dlp not installed (pip install yt-dlp).")
        return None
    out_dir = Path(out_dir or (ROOT / "0_INPUT_INBOX" / "footage"))
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = {}
    opts = {
        "outtmpl": str(out_dir / "%(title).80s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: saved.update({"f": d.get("filename")}) if d.get("status") == "finished" else None],
    }
    if audio_only:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]
    else:
        opts["format"] = f"bestvideo[height<=?{max_h}]+bestaudio/best[height<=?{max_h}]/best"
        opts["merge_output_format"] = "mp4"
    print(f"[source] downloading {url} → {out_dir}")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        # dead / private / geo-blocked / format-unavailable URLs raise DownloadError — honour the
        # documented "(or None)" contract so a batch caller can skip one bad URL, not crash.
        print(f"[source] download failed ({type(e).__name__}): {e}")
        return None
    f = saved.get("f")
    if f and audio_only:
        f = str(Path(f).with_suffix(".wav"))
    print(f"[source] {'done → ' + f if f else 'finished (path: ' + str(out_dir) + ')'}")
    return f or (info.get("requested_downloads", [{}])[0].get("filepath") if info else None)


def main():
    ap = argparse.ArgumentParser(description="Download source footage via yt-dlp")
    ap.add_argument("url")
    ap.add_argument("--out", default=None)
    ap.add_argument("--audio", action="store_true", help="extract audio (wav) only")
    ap.add_argument("--max-h", type=int, default=1920)
    a = ap.parse_args()
    r = download(a.url, a.out, a.audio, a.max_h)
    sys.exit(0 if r else 1)


if __name__ == "__main__":
    main()
