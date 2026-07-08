"""Regression test for broll_sourcer._crop_916's reliability contract.

The clip fed to ffmpeg is an EXTERNALLY-downloaded (untrusted) Pixabay video, so the crop
must be time-bounded (a corrupt clip must not hang the unattended sourcing step) and must
degrade to the raw clip on any ffmpeg failure — never raise.

Hermetic: no real ffmpeg, no network — points _ffmpeg at a bogus binary.
"""
import inspect
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "broll_sourcer"))

import broll_sourcer as b  # noqa: E402


class CropContractTests(unittest.TestCase):
    def test_crop_is_time_bounded(self):
        self.assertIn("timeout=", inspect.getsource(b._crop_916))

    def test_missing_or_bad_ffmpeg_falls_back_to_raw(self):
        saved = b._ffmpeg
        try:
            b._ffmpeg = lambda: "definitely-not-ffmpeg-xyz"
            # no crash, returns the source path unchanged (the documented failure contract)
            self.assertEqual(b._crop_916("in.mp4", "out.mp4"), "in.mp4")
        finally:
            b._ffmpeg = saved


if __name__ == "__main__":
    unittest.main()
