# -*- coding: utf-8 -*-
"""Tests for the content/template schema validator (4_BRAIN/script_schema.py)."""
import os
import sys
import glob
import json
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import script_schema as ss  # noqa: E402
import production_manifest as pm  # noqa: E402


class ContentValidationTests(unittest.TestCase):
    def test_valid_content_passes(self):
        c = {"segments": ["Xin chào anh em.", "Hôm nay học tối ưu."],
             "scenes": [{"h1": "SEO", "h2": "2026"}, {"h1": "Bắt đầu", "h2": "ngay"}]}
        r = ss.validate_content(c)
        self.assertTrue(r["ok"], r["errors"])

    def test_segment_scene_count_mismatch_is_error(self):
        c = {"segments": ["one segment only."],
             "scenes": [{"h1": "A", "h2": "b"}, {"h1": "C", "h2": "d"}]}
        r = ss.validate_content(c)
        self.assertFalse(r["ok"])
        self.assertTrue(any("one narration segment per scene" in e for e in r["errors"]))

    def test_emoji_in_voice_is_error(self):
        c = {"segments": ["Tuyệt vời 🔥 anh em."],
             "scenes": [{"h1": "A", "h2": "b"}]}
        r = ss.validate_content(c)
        self.assertFalse(r["ok"])
        self.assertTrue(any("RULE #1" in e for e in r["errors"]))

    def test_long_heading_is_warning_not_error(self):
        c = {"segments": ["Một câu thoại bình thường."],
             "scenes": [{"h1": "Đây là một tiêu đề rất rất dài quá giới hạn", "h2": "x"}]}
        r = ss.validate_content(c)
        self.assertTrue(r["ok"])           # char limit = warning, not error
        self.assertTrue(any("h1" in w for w in r["warnings"]))


class TemplateValidationTests(unittest.TestCase):
    def test_all_shipped_templates_validate(self):
        for f in glob.glob(os.path.join(PROJECT_ROOT, "7_ASSETS", "templates", "*.json")):
            tpl = json.load(open(f, encoding="utf-8"))
            r = ss.validate_template(tpl)
            self.assertTrue(r["ok"], f"{os.path.basename(f)}: {r['errors']}")

    def test_bad_aspect_rejected(self):
        r = ss.validate_template({"name": "x", "aspect": "4:3", "scenes": [{}]})
        self.assertFalse(r["ok"])


class ScriptTxtTests(unittest.TestCase):
    def test_script_txt_from_srt(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "_captions_upload"))
            srt = os.path.join(d, "_captions_upload", "v_cc.srt")
            open(srt, "w", encoding="utf-8").write(
                "1\n00:00:00,000 --> 00:00:02,000\nXin chào anh em.\n\n"
                "2\n00:00:02,000 --> 00:00:04,000\nHôm nay học SEO.\n")
            out = pm._write_script_txt(d, os.path.relpath(srt, d))
            self.assertTrue(os.path.exists(out))
            txt = open(out, encoding="utf-8").read()
            self.assertIn("Xin chào anh em.", txt)
            self.assertIn("Hôm nay học SEO.", txt)
            self.assertNotIn("-->", txt)


if __name__ == "__main__":
    unittest.main()
