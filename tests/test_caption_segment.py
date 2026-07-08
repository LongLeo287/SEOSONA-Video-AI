# -*- coding: utf-8 -*-
"""Regression test: caption line-breaking must not fragment a SHORT line on a comma.

A comma was treated like a sentence-end, so "Hôm nay, tôi sẽ nói về SEO" (26 chars, fits one 42-char
line) got split onto two lines. Now a comma / pre-connective break requires the line to already have
body (≥60% of max); a real sentence/clause ender (. ! ? … : ;) still always breaks. Every emitted line
stays ≤ max_chars.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import caption_segment as cs  # noqa: E402


class CaptionSegmentTests(unittest.TestCase):
    def test_short_line_with_comma_stays_one_line(self):
        self.assertEqual(cs.segment_text("Hôm nay, tôi sẽ nói về SEO"), ["Hôm nay, tôi sẽ nói về SEO"])

    def test_sentence_end_always_breaks(self):
        r = cs.segment_text("Xin chào. Tôi là AI")
        self.assertEqual(r, ["Xin chào.", "Tôi là AI"])

    def test_comma_on_a_long_line_still_breaks(self):
        r = cs.segment_text("Công cụ chỉ đưa ra dữ liệu thô, còn quyết định là của bạn")
        self.assertGreaterEqual(len(r), 2)
        self.assertTrue(r[0].rstrip().endswith(","), r)   # broke at the comma once the line had body

    def test_every_line_within_max_chars(self):
        long = ("Công cụ chỉ đưa ra dữ liệu thô còn quyết định và chiến lược như thế nào "
                "thì phải do chính bạn là người quyết định cuối cùng cho toàn bộ dự án")
        for ln in cs.segment_text(long):
            self.assertLessEqual(len(ln), cs.MAX_CHARS, ln)


if __name__ == "__main__":
    unittest.main()
