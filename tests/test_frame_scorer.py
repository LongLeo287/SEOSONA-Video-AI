# -*- coding: utf-8 -*-
"""Regression test: the cover-frame sharpness metric must strongly separate a sharp frame from a blurry one.

The Laplacian was applied with the default offset=0, so PIL clamped NEGATIVE edge responses to 0 — a
blurred frame's positive noise survived while its negatives clamped away, inflating its variance so blur
looked falsely sharp (only ~3.6x separation). offset=128 centres the response (dark-text-on-light edges,
SEOSONA's own style, aren't clamped) → sharp-vs-blur separation jumps ~5x, so blur is reliably rejected.
"""
import os
import sys
import tempfile
import shutil
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "thumbnail_maker"))

try:
    import frame_scorer as fs
    from PIL import Image, ImageFilter
    _ERR = None
except Exception as e:
    fs, _ERR = None, e


@unittest.skipIf(fs is None, f"frame_scorer/PIL import failed: {_ERR}")
class SharpnessMetricTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="fs_test_")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _png(self, im, name):
        p = os.path.join(self.d, name)
        im.save(p)
        return p

    def test_sharp_frame_scores_far_above_blur(self):
        im = Image.new("L", (64, 64), 230)                # light bg
        for x in range(0, 64, 4):                         # thin dark bars = dark-text-on-light edges
            for y in range(64):
                im.putpixel((x, y), 30)
        sharp = fs._scores(self._png(im, "sharp.png"))
        blur = fs._scores(self._png(im.filter(ImageFilter.GaussianBlur(3)), "blur.png"))
        self.assertIsNotNone(sharp)
        self.assertIsNotNone(blur)
        self.assertGreater(sharp[0], blur[0] * 5)         # strong separation → blur is reliably rejected

    def test_flat_frame_far_less_sharp_than_edgy(self):
        # a flat frame is maximally un-sharp — score FAR below an edgy one. (Absolute value isn't ~0 because
        # PIL leaves the 1px image border unfiltered, a constant artifact across all frames — use a ratio.)
        flat = fs._scores(self._png(Image.new("L", (64, 64), 200), "flat.png"))
        edgy = Image.new("L", (64, 64), 230)
        for x in range(0, 64, 4):
            for y in range(64):
                edgy.putpixel((x, y), 30)
        sharp = fs._scores(self._png(edgy, "edgy.png"))
        self.assertIsNotNone(flat)
        self.assertIsNotNone(sharp)
        self.assertGreater(sharp[0], flat[0] * 10)        # edgy is an order of magnitude sharper


if __name__ == "__main__":
    unittest.main()
