r"""Regression tests for bgm_sourcer:

1. _instrumental_ok — the short bad-word 'rap' must WHOLE-WORD match, not substring: it was rejecting
   good instrumental beds titled 'Wrapped'/'Rapid'/'Therapy'/'Grape' (all contain 'rap'). Distinctive
   tokens (vocal/lyric/remix/feat.) stay substring so they still catch vocals/lyrics/remixed.
2. source_bgm must not crash on a malformed API row with id=None — `f"...{rid[:8]}"` did `None[:8]`
   (TypeError) mid-loop, killing the whole --all batch. A `not rid` guard now skips it.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "bgm_sourcer"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "1_CONFIG"))

try:
    import bgm_sourcer as bgm
    _ERR = None
except Exception as e:
    bgm, _ERR = None, e


@unittest.skipIf(bgm is None, f"bgm_sourcer import failed: {_ERR}")
class InstrumentalFilterTests(unittest.TestCase):
    def test_rap_substring_does_not_reject_good_beds(self):
        for title in ("Wrapped in Ambient", "Rapid Pulse", "Therapy Session", "Grape Groove"):
            self.assertTrue(bgm._instrumental_ok(title), title)

    def test_actual_vocals_still_rejected(self):
        for title in ("Sick Rap Beat", "Smooth Vocals", "Lyrical Journey", "Track feat. Someone", "Live Remix"):
            self.assertFalse(bgm._instrumental_ok(title), title)


@unittest.skipIf(bgm is None, f"bgm_sourcer import failed: {_ERR}")
class SourceBgmRobustnessTests(unittest.TestCase):
    def setUp(self):
        self._api, self._load, self._save = bgm._api_get, bgm._load_attrib, bgm._save_attrib
        bgm._load_attrib = lambda: []
        bgm._save_attrib = lambda rows: None

    def tearDown(self):
        bgm._api_get, bgm._load_attrib, bgm._save_attrib = self._api, self._load, self._save

    def test_none_id_row_does_not_crash(self):
        bgm._api_get = lambda params, retries=3: {"results": [
            {"id": None, "duration": 60000, "title": "Wrapped Ambient", "url": "http://x"}]}
        self.assertEqual(bgm.source_bgm("tech", n=1), [])   # skipped, no TypeError on None[:8]


if __name__ == "__main__":
    unittest.main()
