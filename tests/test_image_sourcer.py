"""Regression tests for image_sourcer's pure image helpers (no network / no API key).

Covers the crop-to-9:16 geometry (both orientations), crash-safety on a bad path, the
empty-concept guard (no wasted Pexels call → off-topic photo), and dominant_color.
"""
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "image_sourcer"))

try:
    from PIL import Image
    import image_sourcer as isrc
    _ERR = None
except Exception as e:
    isrc, _ERR = None, e


@unittest.skipIf(isrc is None, f"PIL/image_sourcer unavailable: {_ERR}")
class CropTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def _img(self, name, w, h, color=(120, 60, 200)):
        p = os.path.join(self.dir, name)
        Image.new("RGB", (w, h), color).save(p)
        return p

    def test_wide_photo_crops_to_9_16(self):
        out = isrc._crop_916(self._img("wide.jpg", 2400, 1200))
        self.assertEqual(Image.open(out).size, (1080, 1920))

    def test_tall_photo_crops_to_9_16(self):
        out = isrc._crop_916(self._img("tall.jpg", 600, 2000))
        self.assertEqual(Image.open(out).size, (1080, 1920))

    def test_bad_path_does_not_crash(self):
        self.assertEqual(isrc._crop_916("/no/such/file.jpg"), "/no/such/file.jpg")

    def test_dominant_color_returns_hex(self):
        c = isrc.dominant_color(self._img("c.jpg", 100, 100, (200, 40, 40)))
        self.assertRegex(c, r"^#[0-9A-Fa-f]{6}$")


@unittest.skipIf(isrc is None, f"PIL/image_sourcer unavailable: {_ERR}")
class GuardTests(unittest.TestCase):
    def test_empty_concept_makes_no_pexels_call(self):
        # a blank concept must return [] WITHOUT hitting Pexels (a blank query returns random photos).
        self.assertEqual(isrc.search_pexels(""), [])
        self.assertEqual(isrc.search_pexels("   "), [])
        self.assertIsNone(isrc.source_for_concept(""))


if __name__ == "__main__":
    unittest.main()
