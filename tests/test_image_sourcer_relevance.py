r"""Regression test: the Pexels photo relevance gate must WHOLE-WORD match, not substring.

_relevant used `any(t in alt for t in terms)` on the photo's English alt text. Short relevance terms
('ai', 'seo', 'code', 'time', 'web') then matched INSIDE unrelated words — 'ai' in hair/rain/brain/
train/email/mountain/captain, 'seo' in Seoul, 'code' in barcode — so wildly off-topic stock photos
passed the gate (an AI scene getting a photo of hair or a mountain). Now a whole-word \b match.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "image_sourcer"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "1_CONFIG"))

try:
    import image_sourcer as isrc
    _ERR = None
except Exception as e:
    isrc, _ERR = None, e


@unittest.skipIf(isrc is None, f"image_sourcer import failed: {_ERR}")
class AltRelevanceTests(unittest.TestCase):
    def test_substring_collisions_rejected(self):
        self.assertFalse(isrc._alt_relevant("a woman with long hair", ["ai"]))     # 'ai' in 'hair'
        self.assertFalse(isrc._alt_relevant("email on a laptop", ["ai"]))          # 'ai' in 'email'
        self.assertFalse(isrc._alt_relevant("a snowy mountain range", ["ai"]))     # 'ai' in 'mountain'
        self.assertFalse(isrc._alt_relevant("Seoul city skyline", ["seo"]))        # 'seo' in 'Seoul'
        self.assertFalse(isrc._alt_relevant("a product barcode", ["code"]))        # 'code' in 'barcode'

    def test_real_matches_kept(self):
        self.assertTrue(isrc._alt_relevant("AI robot assistant", ["ai"]))
        self.assertTrue(isrc._alt_relevant("SEO strategy dashboard", ["seo"]))
        self.assertTrue(isrc._alt_relevant("clean source code editor", ["code"]))

    def test_no_terms_accepts_by_rank(self):
        self.assertTrue(isrc._alt_relevant("any photo at all", []))

    def test_none_alt_no_crash(self):
        self.assertFalse(isrc._alt_relevant(None, ["ai"]))


if __name__ == "__main__":
    unittest.main()
