"""Regression test: native_composer._item_reveal_times must never raise.

It runs in the MAIN render tween loop, so a raise there (from malformed word-timing — e.g. an
explicit null "start", or odd keyword text tripping a beat_timing helper) would crash the WHOLE
video render. The already-computed even reveal times are the documented fallback; the whole body
is now guarded to return them on any error.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import native_composer as nc  # noqa: E402


class ItemRevealTimesTests(unittest.TestCase):
    def test_malformed_word_timing_falls_back_to_even(self):
        comp = ("checklist", {"items": [{"text": "alpha"}, {"text": "beta"}, {"text": "gamma"}]})
        # an explicit null "start" makes float(grp[0].get("start")) raise TypeError inside the body
        grp = [{"start": None, "end": None}, {"start": None, "end": None}]
        out = nc._item_reveal_times(comp, grp, 1.0, 0.5, 3)   # must not propagate
        self.assertEqual(out, [1.0, 1.5, 2.0])                # == even = [rstart + k*rint]

    def test_no_word_list_returns_even(self):
        comp = ("checklist", {"items": [{"text": "a"}, {"text": "b"}]})
        self.assertEqual(nc._item_reveal_times(comp, [], 0.0, 0.4, 2), [0.0, 0.4])


if __name__ == "__main__":
    unittest.main()
