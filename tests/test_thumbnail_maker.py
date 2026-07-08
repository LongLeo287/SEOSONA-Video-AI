"""Regression tests for thumbnail_maker's pure helpers.

Focus: the temp-HTML filename must be UNIQUE per output. A shared fixed name
("_temp_thumbnail.html") let two concurrent renders into the same directory clobber
each other's temp file mid-render → a wrong/corrupt PNG. The full Playwright render is
an integration concern and is not exercised here.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "thumbnail_maker"))

try:
    import thumbnail_maker as tm
    _IMPORT_ERR = None
except Exception as e:  # playwright may be absent in some envs — skip rather than fail
    tm, _IMPORT_ERR = None, e


@unittest.skipIf(tm is None, f"thumbnail_maker import failed: {_IMPORT_ERR}")
class TempHtmlPathTests(unittest.TestCase):
    def test_two_aspects_in_same_dir_do_not_collide(self):
        a = tm._temp_html_path(os.path.join("proj", "thumb_9x16.png"))
        b = tm._temp_html_path(os.path.join("proj", "thumb_16x9.png"))
        self.assertNotEqual(a, b)

    def test_temp_lives_beside_output(self):
        p = tm._temp_html_path(os.path.join("some", "dir", "t.png"))
        self.assertEqual(os.path.dirname(p), os.path.join("some", "dir"))
        self.assertTrue(os.path.basename(p).endswith(".html"))

    def test_not_the_old_shared_fixed_name(self):
        p = tm._temp_html_path(os.path.join("d", "cover.png"))
        self.assertNotEqual(os.path.basename(p), "_temp_thumbnail.html")
        self.assertIn("cover", os.path.basename(p))


@unittest.skipIf(tm is None, f"thumbnail_maker import failed: {_IMPORT_ERR}")
class KeywordHighlightTests(unittest.TestCase):
    def test_acronym_wins_highlight(self):
        pre, kw, suf = tm._extract_keyword("Tại sao nên đầu tư vào SEO ngay")
        self.assertEqual(kw, "SEO")

    def test_stopword_never_wins(self):
        _, kw, _ = tm._extract_keyword("Những điều cần biết về marketing")
        self.assertNotIn(kw.lower(), tm._THUMB_STOP)

    def test_split_highlight_does_not_break_a_word(self):
        # kw "AI" must land on the standalone word, NOT inside "Email" (the old substring find gave "Em[AI]l")
        self.assertEqual(tm._split_highlight("Dùng Email AI mỗi ngày", "AI"), ("Dùng Email", "AI", "mỗi ngày"))

    def test_split_highlight_standalone_keyword(self):
        self.assertEqual(tm._split_highlight("Chiến lược SEO 2025", "SEO"), ("Chiến lược", "SEO", "2025"))

    def test_split_highlight_seo_not_matched_inside_seoul(self):
        pre, kw, suf = tm._split_highlight("Thành phố Seoul đẹp", "SEO")
        self.assertNotEqual(kw, "SEO")                 # 'Seoul' must not be split into '[SEO]ul'

    def test_split_highlight_missing_keyword_falls_back(self):
        _, kw, _ = tm._split_highlight("Hôm nay trời rất đẹp", "XYZ")
        self.assertTrue(kw)                            # falls back to the content-word heuristic

    def test_cap_title_leaves_normal_title_untouched(self):
        t = "Tối ưu SEO cho website doanh nghiệp"      # 6 words → within the 4-8 target
        self.assertEqual(tm._cap_title(t), t)

    def test_cap_title_truncates_a_paragraph_at_a_word_boundary(self):
        para = ("Hôm nay chúng ta sẽ nói về cách tối ưu SEO cho website "
                "doanh nghiệp nhỏ trong năm 2026 với các công cụ AI hiện đại")
        capped = tm._cap_title(para)
        self.assertLessEqual(len(capped.split()), 12)
        self.assertTrue(para.startswith(capped.split(" ")[0]))   # kept the front (key message)
        self.assertNotIn("  ", capped)                            # no mid-word cut / double space

    def test_cap_title_empty(self):
        self.assertEqual(tm._cap_title(""), "")
        self.assertEqual(tm._cap_title(None), "")


if __name__ == "__main__":
    unittest.main()
