"""
Chi Quyet Academy / SEOSONA — COURSE & knowledge video workflow (npm: video:course).

Course/knowledge videos are NOT generated like news. They REPURPOSE real lecture footage:
  1. analyse the video → get its SRT (transcribe)
  2. from the SRT → build the content cut-plan
  3. cut + splice the footage into one coherent lesson
  4. finish it talking-head style (real voice + burnt karaoke captions)

This is a thin entrypoint over `scripts/course_video.py` (the repurpose pipeline).

Usage:
  npm run video:course -- <lecture.mp4> [--srt lecture.srt] [--out lesson.mp4]
  npm run video:course -- <lecture.srt> --plan-only        # inspect the cut-plan only

If a video is given without --srt, a sibling <name>.srt is used when present, else the
video is transcribed automatically.
"""
import os
import sys
from pathlib import Path
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)

    src = argv[0]
    rest = argv[1:]
    cv = import_module("course_video")

    # Build course_video argv from the friendly entrypoint args.
    cv_argv = ["course_video"]
    if src.lower().endswith(".srt"):
        cv_argv += ["--srt", src]
    else:
        cv_argv += ["--video", src]
        if "--srt" not in rest:               # auto-attach a sibling SRT if present
            sib = Path(src).with_suffix(".srt")
            if sib.exists():
                cv_argv += ["--srt", str(sib)]
    cv_argv += rest

    sys.argv = cv_argv
    cv.main()


if __name__ == "__main__":
    main()
