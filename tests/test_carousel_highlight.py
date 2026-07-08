# -*- coding: utf-8 -*-
r"""Regression test: carousel slide highlight must be WHOLE-WORD, not a bare substring, and stay HTML-safe.

_highlight wrapped the keyword via `escaped.replace(hl, <span>)` — a substring replace hitting ALL
occurrences — so "AI" wrapped the "AI" INSIDE "Email" (→ "Em[AI]l") and any repeat. Now it uses a \b
word-boundary regex (Unicode \w → respects VN diacritics) with a function replacement (so a '\'/backref
in the keyword isn't interpreted). Injection escaping (< > & ' ") is preserved.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "carousel_maker"))

try:
    import carousel_generator as cg
    _ERR = None
except Exception as e:                       # playwright may be absent — skip rather than fail
    cg, _ERR = None, e


@unittest.skipIf(cg is None, f"carousel_generator import failed: {_ERR}")
class CarouselHighlightTests(unittest.TestCase):
    def test_keyword_not_wrapped_inside_another_word(self):
        out = cg._highlight("Dùng Email AI mỗi ngày", "AI", "#f00")
        self.assertIn("Email", out)                       # 'Email' stays intact
        self.assertNotIn("Em<span", out)                  # NOT "Em[AI]l"
        self.assertEqual(out.count("<span"), 1)           # only the standalone AI

    def test_seo_not_matched_inside_seoul(self):
        out = cg._highlight("Thành phố Seoul đẹp", "SEO", "#f00")
        self.assertNotIn("<span", out)                    # 'Seoul' must not be split

    def test_standalone_and_multiword_keyword(self):
        self.assertIn('<span style="color:#f00">SEO</span>', cg._highlight("Chiến lược SEO 2025", "SEO", "#f00"))
        self.assertIn('<span style="color:#f00">Tự động</span>',
                      cg._highlight("Tự động hoá quy trình", "Tự động", "#f00"))

    def test_html_is_escaped(self):
        out = cg._highlight("A < B & C's \"x\"", "", "#f00")
        self.assertIn("&lt;", out)
        self.assertIn("&amp;", out)
        self.assertNotIn("< B", out)                      # raw '<' must not survive


if __name__ == "__main__":
    unittest.main()
