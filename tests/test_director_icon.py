# -*- coding: utf-8 -*-
"""Regression test: director._scene_icon must WHOLE-WORD match, not substring.

_ICON used a bare "ai" keyword with `any(k in low for k in kws)`, so any sentence containing the
substring 'ai' — 'hai' (two), 'mai' (tomorrow), 'sai' (wrong), 'trai' (boy) — got a 🤖 AI emoji, and
'ảnh' (image) matched inside 'cảnh' (scene) → wrong 🖼. Runs for EVERY video. Now space-padded like
_SVG's " ai " cue, so only the standalone words match.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import director as d  # noqa: E402


class SceneIconWholeWordTests(unittest.TestCase):
    def test_ai_substring_words_do_not_trigger_robot(self):
        # 'trai'/'sai'/'hai' all contain 'ai' but are not the word 'ai'
        self.assertNotEqual(d._scene_icon("Con trai tôi làm sai bài này hai lần"), "🤖")

    def test_canh_does_not_trigger_image_icon(self):
        # 'cảnh' contains 'ảnh' but is not the word 'ảnh'
        self.assertNotEqual(d._scene_icon("Mỗi cảnh nên khác nhau"), "🖼")

    def test_real_ai_content_still_gets_robot(self):
        self.assertEqual(d._scene_icon("Trí tuệ nhân tạo thay đổi mọi thứ"), "🤖")
        self.assertEqual(d._scene_icon("Công nghệ AI thông minh"), "🤖")

    def test_real_image_content_still_matches(self):
        self.assertEqual(d._scene_icon("Bức ảnh này rất đẹp"), "🖼")

    def test_multiword_cue_still_matches(self):
        self.assertEqual(d._scene_icon("Nó ngốn tài nguyên máy tính"), "💻")


class SceneSvgWholeWordTests(unittest.TestCase):
    def test_kho_substring_words_do_not_trigger_package(self):
        # 'khoa'/'khoản'/'khoảng' contain 'kho' but are not the word 'kho'
        self.assertNotEqual(d._scene_svg("Ngành khoa cử ngày xưa"), "package")
        self.assertNotEqual(d._scene_svg("Khoảng cách còn khá xa"), "package")

    def test_real_kho_still_matches_package(self):
        self.assertEqual(d._scene_svg("Lưu tất cả vào kho chung"), "package")

    def test_ai_cues_still_match_brain(self):
        self.assertEqual(d._scene_svg("Công nghệ AI tiên tiến"), "brain")     # " ai " cue
        self.assertEqual(d._scene_svg("Đó là sức mạnh của AI."), "brain")     # "ai." sentence-end cue

    def test_multiword_svg_cue_still_matches(self):
        self.assertEqual(d._scene_svg("Dự án này là open source"), "git-branch")


if __name__ == "__main__":
    unittest.main()
