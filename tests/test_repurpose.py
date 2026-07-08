"""Regression test: one failed clip must not abort the whole repurpose batch.

video_engine._repurpose cuts a short per hook. A raising cut (bad timestamp / corrupt region)
previously killed every remaining short. It now skips the failed hook and continues.

Hermetic: the SRT analyzer, clipper, and thumbnail maker are stubbed (no ffmpeg / no Playwright).
"""
import os
import sys
import tempfile
import types
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import video_engine as ve  # noqa: E402


class RepurposeResilienceTests(unittest.TestCase):
    def setUp(self):
        self._extract = ve._extract_srt_from_media
        self._mods = {k: sys.modules.get(k) for k in
                      ("1_AGENTS.repurposer_agent.srt_analyzer", "2_SKILLS.video_clipper.clipper",
                       "2_SKILLS.thumbnail_maker.thumbnail_maker")}
        ve._extract_srt_from_media = lambda m, o: True

        an = types.ModuleType("an")
        an.analyze_srt_for_hooks = lambda srt: [
            {"id": 1, "start": 0, "end": 5, "hook_text": "h1"},
            {"id": 2, "start": 5, "end": 10, "hook_text": "h2"},
            {"id": 3, "start": 10, "end": 15, "hook_text": "h3"}]
        cl = types.ModuleType("cl")

        def cut(media, s, e, out):
            if s == 5:
                raise RuntimeError("clip boom")     # the middle hook fails
            open(out, "wb").write(b"x")
        cl.cut_and_format_short = cut
        tm = types.ModuleType("tm")
        tm.make_thumbnail = lambda **k: None
        sys.modules["1_AGENTS.repurposer_agent.srt_analyzer"] = an
        sys.modules["2_SKILLS.video_clipper.clipper"] = cl
        sys.modules["2_SKILLS.thumbnail_maker.thumbnail_maker"] = tm

    def tearDown(self):
        ve._extract_srt_from_media = self._extract
        for k, v in self._mods.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v

    def test_failed_clip_skips_and_batch_continues(self):
        d = tempfile.mkdtemp()
        r = ve._repurpose(os.path.join(d, "src.mp4"), d, "seosona", "P")
        self.assertEqual(len(r["outputs"]), 2)                       # hook 2 skipped, 1 & 3 kept
        self.assertTrue(any("Part1" in o for o in r["outputs"]))
        self.assertTrue(any("Part3" in o for o in r["outputs"]))    # produced AFTER the failure


if __name__ == "__main__":
    unittest.main()
