"""Regression tests for dub_align's timing math (no ffmpeg / no audio files).

_atempo_chain decomposes a speed factor into ffmpeg atempo steps — each step MUST stay in
ffmpeg's valid [0.5, 2.0] range, and the steps must multiply back to the requested factor,
or the dub plays at the wrong speed. plan() picks pad/audio/both from the dub-vs-slot ratio.
"""
import math
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import dub_align as da  # noqa: E402


def _steps(chain):
    return [float(x) for x in re.findall(r"atempo=([\d.]+)", chain)]


class AtempoChainTests(unittest.TestCase):
    def test_steps_multiply_back_to_factor(self):
        for f in (1.002, 1.5, 2.0, 2.5, 3.0, 4.0, 7.3, 10.0, 16.0, 0.5, 0.25, 0.7):
            prod = math.prod(_steps(da._atempo_chain(f)))
            self.assertAlmostEqual(prod, f, places=2, msg=f"factor {f} -> product {prod}")

    def test_every_step_in_ffmpeg_valid_range(self):
        for f in (1.5, 2.0, 3.0, 4.0, 16.0, 0.25):
            for s in _steps(da._atempo_chain(f)):
                self.assertGreaterEqual(s, 0.5 - 1e-9)
                self.assertLessEqual(s, 2.0 + 1e-9)

    def test_identity_factor(self):
        self.assertEqual(da._atempo_chain(1.0), "atempo=1.0")


class PlanStrategyTests(unittest.TestCase):
    def setUp(self):
        self._saved = da._dur
        # deterministic dub duration so the ratio (dub/slot) is fully controlled
        da._dur = lambda wav: self._dub
        self._dub = 1.0

    def tearDown(self):
        da._dur = self._saved

    def _one(self, dub, slot_start_gap):
        self._dub = dub
        segs = [{"start": 0.0, "end": 0.0, "wav": "a.wav"},
                {"start": slot_start_gap, "end": slot_start_gap, "wav": "b.wav"}]
        return da.plan(segs, total_dur=slot_start_gap + 5)[0]

    def test_dub_fits_slot_is_pad(self):
        r = self._one(dub=1.0, slot_start_gap=2.0)   # ratio 0.5 <= 1 → pad
        self.assertEqual(r["strategy"], "pad")

    def test_small_overflow_is_audio(self):
        # ratio just above 1 but under the audio-only threshold → speed audio only
        r = self._one(dub=1.0, slot_start_gap=0.95)
        self.assertLessEqual(r["ratio"], da.BOTH_MODE_AUDIO_ONLY_THRESHOLD)
        self.assertEqual(r["strategy"], "audio")

    def test_large_overflow_is_both(self):
        r = self._one(dub=5.0, slot_start_gap=1.0)   # ratio 5 → both
        self.assertEqual(r["strategy"], "both")

    def test_slot_never_zero(self):
        r = self._one(dub=1.0, slot_start_gap=0.0)   # same start → slot floored at 0.1
        self.assertGreaterEqual(r["slot_sec"], 0.1)


if __name__ == "__main__":
    unittest.main()
