# -*- coding: utf-8 -*-
"""Regression test: parse_srt must not let ONE malformed cue abort the whole SRT parse.

`a, b = tl.split("-->")` ValueError'd on a line with a stray 2nd "-->", and `_ts_to_sec` raises on a
bad timestamp — both propagated (parse_srt had no guard), crashing the entire parse (→ course planning
fails, 0 cues). Now: maxsplit=1 + per-cue try/except skips the bad cue, keeps the good ones.
"""
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import course_planner as cp  # noqa: E402

_SRT = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> --> 00:00:04,000
Malformed double arrow

3
bad:ts --> also:bad
Bad timestamp

4
00:00:05,000 --> 00:00:06,000
Second good cue
"""


class ParseSrtRobustnessTests(unittest.TestCase):
    def setUp(self):
        self.p = os.path.join(tempfile.mkdtemp(), "t.srt")
        with open(self.p, "w", encoding="utf-8") as f:
            f.write(_SRT)

    def test_malformed_cues_skipped_good_kept(self):
        cues = cp.parse_srt(self.p)                       # must not raise
        self.assertEqual([c["text"] for c in cues], ["Hello world", "Second good cue"])
        self.assertEqual((cues[0]["start"], cues[0]["end"]), (1.0, 2.0))

    def test_clean_srt_unchanged(self):
        p = os.path.join(tempfile.mkdtemp(), "clean.srt")
        with open(p, "w", encoding="utf-8") as f:
            f.write("1\n00:00:01,000 --> 00:00:02,500\nXin chào\n")
        cues = cp.parse_srt(p)
        self.assertEqual(len(cues), 1)
        self.assertEqual(cues[0]["text"], "Xin chào")
        self.assertAlmostEqual(cues[0]["end"], 2.5, places=3)


if __name__ == "__main__":
    unittest.main()
