# -*- coding: utf-8 -*-
"""Export a finished SEOSONA video into an EDITABLE CapCut project (draft).

Why: CapCut ships a huge library of SFX, transitions, text-effects and stickers. Instead of
shipping only a flat MP4, SEOSONA can hand the user a CapCut project that opens with the video
already on the timeline — the user then embellishes it with CapCut's native effects and re-exports.

Built on GuanYixuan/pyCapCut (Apache-2.0) — international CapCut. The draft format version on this
machine (CapCut 8.9) matches what pyCapCut emits (draft `version` 360000); CapCut itself stamps
drafts with a 6.x app_version, so the lib's 6.7 stamp is fine. NOTE: pyCapCut emits a minimal
(subset) segment schema — CapCut's reader fills missing fields with defaults; if a future CapCut
rejects it, regenerate from a fresh CapCut draft as the template.

  python 4_BRAIN/capcut_export.py "8_WORKSPACE/<name>/<name> - SEOSONA.mp4"
  npm run capcut:export -- "<path-to-mp4>"
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def capcut_drafts_dir():
    """Auto-detect the local CapCut (or JianYing) drafts folder on Windows. Returns None if none."""
    la = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    for sub in (r"CapCut\User Data\Projects\com.lveditor.draft",
                r"JianyingPro\User Data\Projects\com.lveditor.draft"):
        p = os.path.join(la, sub)
        if os.path.isdir(p):
            return p
    return None


def export(mp4, name=None, aspect="9:16", srt=None, drafts_dir=None):
    """Create a CapCut draft containing the SEOSONA MP4 (+ optional editable SRT captions).
    Returns the draft folder path, or None on failure (best-effort, never raises into a render)."""
    try:
        import pycapcut as cc
        from pycapcut import trange
    except Exception:
        print("[capcut] pycapcut not installed — `pip install -e 2_KNOWLEDGE/external_toolkits/pyCapCut`")
        return None
    if not os.path.exists(mp4):
        print(f"[capcut] mp4 not found: {mp4}")
        return None
    dd = drafts_dir or capcut_drafts_dir()
    if not dd:
        print("[capcut] CapCut drafts folder not found (is CapCut Desktop installed?).")
        return None
    name = name or ("SEOSONA - " + os.path.splitext(os.path.basename(mp4))[0])
    W, H = (1080, 1920) if str(aspect).startswith("9") else (1920, 1080)
    try:
        folder = cc.DraftFolder(dd)
        script = folder.create_draft(name, W, H, allow_replace=True)
        mat = cc.VideoMaterial(mp4)                       # MP4 carries its own baked audio
        script.add_track(cc.TrackType.video)
        script.add_segment(cc.VideoSegment(mat, trange(0, mat.duration)))
        if srt and os.path.exists(srt):                  # optional: editable caption track
            try:
                script.import_srt(srt)
            except Exception as e:
                print(f"[capcut] srt import skipped ({type(e).__name__})")
        script.save()
        out = os.path.join(dd, name)
        print(f"[capcut] ✓ draft created → open CapCut, project '{name}'  ({out})")
        return out
    except Exception as e:
        print(f"[capcut] export failed ({type(e).__name__}: {e})")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python 4_BRAIN/capcut_export.py <mp4> [9:16|16:9] [srt]")
        sys.exit(1)
    mp4 = sys.argv[1]
    aspect = sys.argv[2] if len(sys.argv) > 2 else "9:16"
    srt = sys.argv[3] if len(sys.argv) > 3 else None
    sys.exit(0 if export(mp4, aspect=aspect, srt=srt) else 1)
