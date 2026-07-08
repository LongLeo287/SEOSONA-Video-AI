"""Regression test: on-screen titles must preserve acronym casing (SEO, AI, API), not str.title() them.

_make_title builds the video title from a leading phrase of the SOURCE text (_leading_phrase keeps
original case), so a plain .title() turned 'SEO' into 'Seo' — mangling the exact-match keyword in the
video's own headline. _smart_title preserves any word that already carries an uppercase letter.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import llm_engine as le  # noqa: E402


class SmartTitleTests(unittest.TestCase):
    def test_acronyms_preserved(self):
        self.assertEqual(le._smart_title("SEO"), "SEO")
        self.assertEqual(le._smart_title("API"), "API")
        self.assertEqual(le._smart_title("SEO audit"), "SEO Audit")
        self.assertEqual(le._smart_title("ChatGPT prompt"), "ChatGPT Prompt")

    def test_all_lowercase_still_capitalised(self):
        self.assertEqual(le._smart_title("content marketing"), "Content Marketing")

    def test_make_title_does_not_mangle_source_acronym(self):
        title = le._make_title([], "SEO", text="SEO Checklist quan trọng cho website")
        self.assertIn("SEO", title)
        self.assertNotIn("Seo", title)     # the .title() bug produced 'Seo'


if __name__ == "__main__":
    unittest.main()
