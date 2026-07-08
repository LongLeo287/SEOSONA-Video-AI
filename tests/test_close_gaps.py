# -*- coding: utf-8 -*-
"""Lock beat_timing.close_gaps — the deterministic flicker/overlap pass now wired into the
talking-head b-roll render (talking_head_edit, before the broll list is built). Previously the
pass had ZERO call sites, so it was also untested; these lock the contract the render relies on."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import beat_timing as bt


class TestCloseGaps(unittest.TestCase):
    def test_bridges_micro_gap(self):
        # 0.4s gap between two full-frame beats reads as flicker → earlier beat's end extends to the next start.
        beats = [{"start": 0.0, "end": 3.0, "kind": "full"},
                 {"start": 3.4, "end": 5.0, "kind": "full"}]
        bt.close_gaps(beats)
        self.assertEqual(beats[0]["end"], 3.4)

    def test_fixes_overlap(self):
        # Overlap (end_a > start_b) → shorten the earlier beat so clips don't stack.
        beats = [{"start": 0.0, "end": 3.5, "kind": "full"},
                 {"start": 3.0, "end": 5.0, "kind": "full"}]
        bt.close_gaps(beats)
        self.assertLessEqual(beats[0]["end"], 3.0)
        self.assertGreater(beats[0]["end"], beats[0]["start"])   # never inverted

    def test_leaves_real_breather(self):
        # A >1.5s gap is an intentional breather, not flicker → left alone.
        beats = [{"start": 0.0, "end": 3.0, "kind": "full"},
                 {"start": 6.0, "end": 8.0, "kind": "full"}]
        bt.close_gaps(beats)
        self.assertEqual(beats[0]["end"], 3.0)

    def test_never_inflates_past_ceiling(self):
        # Bridging must not turn a beat into a setpiece: if start_b - start_a > 6s, don't bridge.
        beats = [{"start": 0.0, "end": 6.2, "kind": "full"},
                 {"start": 6.5, "end": 9.0, "kind": "full"}]
        bt.close_gaps(beats)
        self.assertEqual(beats[0]["end"], 6.2)     # (6.5-0.0)=6.5 > 6.0 ceiling → unchanged

    def test_partial_overlays_not_bridged(self):
        # Two partial overlays (speaker still visible) may overlap intentionally → never touched.
        beats = [{"start": 0.0, "end": 3.5, "kind": "icon_tile"},
                 {"start": 3.0, "end": 5.0, "kind": "chip"}]
        bt.close_gaps(beats)
        self.assertEqual(beats[0]["end"], 3.5)     # untouched despite the overlap

    def test_missing_end_is_noop_not_crash(self):
        # A beat expressing timing without an explicit end must not crash or get a false mutation.
        beats = [{"start": 0.0, "kind": "full"},
                 {"start": 3.4, "end": 5.0, "kind": "full"}]
        bt.close_gaps(beats)   # must not raise
        self.assertNotIn("end", beats[0])          # no end was invented

    def test_single_and_empty_safe(self):
        self.assertEqual(bt.close_gaps([]), [])
        one = [{"start": 0.0, "end": 3.0, "kind": "full"}]
        self.assertEqual(bt.close_gaps(one), one)


if __name__ == "__main__":
    unittest.main()
