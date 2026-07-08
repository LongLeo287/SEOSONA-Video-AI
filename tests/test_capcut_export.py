"""Regression test: the CapCut draft canvas must match the VIDEO's real pixel size.

Bug fixed: the canvas was inferred from the `aspect` string, so a wrong/omitted aspect
produced a mismatched canvas (e.g. 1920×1080 for a 9:16 video) → the video sat letterboxed
in the CapCut draft. It now reads width/height from the VideoMaterial.

Requires pycapcut + ffmpeg; skipped otherwise (no network — temp dirs only).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

try:
    import pycapcut  # noqa: F401
    import capcut_export as ce
    _HAVE_CC = True
except Exception:
    _HAVE_CC = False

_HAVE_FFMPEG = shutil.which("ffmpeg") is not None


def _make_mp4(path, w, h):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"color=c=blue:s={w}x{h}:d=1", "-pix_fmt", "yuv420p", path],
                   capture_output=True, timeout=60)


def _canvas(draft_dir):
    d = json.load(open(os.path.join(draft_dir, "draft_content.json"), encoding="utf-8"))
    c = d.get("canvas_config", {})
    return (c.get("width"), c.get("height"))


@unittest.skipUnless(_HAVE_CC and _HAVE_FFMPEG, "pycapcut + ffmpeg required")
class CanvasMatchesVideoTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.dd = os.path.join(self.dir, "drafts")
        os.makedirs(self.dd)

    def test_portrait_canvas_matches_video_despite_wrong_aspect(self):
        mp4 = os.path.join(self.dir, "p.mp4"); _make_mp4(mp4, 1080, 1920)
        out = ce.export(mp4, name="p", aspect="16:9", drafts_dir=self.dd)   # WRONG aspect on purpose
        self.assertIsNotNone(out)
        self.assertEqual(_canvas(out), (1080, 1920))                        # matches the VIDEO, not aspect

    def test_landscape_canvas_matches_video_despite_wrong_aspect(self):
        mp4 = os.path.join(self.dir, "l.mp4"); _make_mp4(mp4, 1920, 1080)
        out = ce.export(mp4, name="l", aspect="9:16", drafts_dir=self.dd)
        self.assertIsNotNone(out)
        self.assertEqual(_canvas(out), (1920, 1080))


@unittest.skipUnless(_HAVE_CC, "pycapcut required")
class GracefulFailureTests(unittest.TestCase):
    def test_missing_mp4_returns_none(self):
        self.assertIsNone(ce.export("/no/such/video.mp4", drafts_dir=tempfile.mkdtemp()))


if __name__ == "__main__":
    unittest.main()
