# -*- coding: utf-8 -*-
"""Partial re-render (KeepVoice family) — redo only the broken stage, reuse the expensive cached ones.

    python scripts/rerender.py <project_dir> --redo visual   # video lỗi → keep voice, re-render video
    python scripts/rerender.py <project_dir> --redo voice    # voice lỗi → keep video, re-do voice + remux
    python scripts/rerender.py <project_dir> --redo mix      # SFX/BGM/loudness lỗi → keep voice+video
    python scripts/rerender.py <project_dir> --redo thumb    # ảnh bìa lỗi → keep tất cả

Reads `<project_dir>/proj/content.json` (written by native_composer.make_video) so the re-render uses
the EXACT same segments/scenes → the kept voice/video always matches. Reuses:
  voice → `proj/assets/voice.mp3` (skips ~32s TTS)   ·   video → `_raw.mp4` (skips the HyperFrames render).
"""
import os
import sys
import json
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import native_composer as nc  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Partial re-render a SEOSONA video (reuse cached stages).")
    ap.add_argument("project_dir", help="the video's project dir (has proj/content.json)")
    ap.add_argument("--redo", required=True,
                    help="stage(s) to redo: visual | voice | mix | thumb | all (comma-separated)")
    a = ap.parse_args()

    content = os.path.join(a.project_dir, "proj", "content.json")
    if not os.path.exists(content):
        sys.exit(f"[rerender] không thấy {content} — video này render trước khi có content.json; cần redo=all từ đầu.")
    try:
        d = json.load(open(content, encoding="utf-8"))
    except Exception as e:
        sys.exit(f"[rerender] content.json hỏng ({e}) — cần redo=all từ đầu.")
    if not (d.get("segments") and d.get("scenes")):     # partial/old content.json → helpful msg, not a raw KeyError
        sys.exit(f"[rerender] content.json thiếu segments/scenes (định dạng cũ) — cần redo=all từ đầu.")
    params = d.get("params", {}) or {}

    print(f"[rerender] {a.project_dir} | redo={a.redo}")
    out = nc.make_video(a.project_dir, d["segments"], d["scenes"], redo=a.redo, **params)
    print(f"[rerender] done → {out}")


if __name__ == "__main__":
    main()
