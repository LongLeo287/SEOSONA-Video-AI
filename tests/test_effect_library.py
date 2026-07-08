# -*- coding: utf-8 -*-
"""Lock the effect_library tween-shape invariants that were previously only checked in the module's
__main__ self-test (which pytest never runs). A runtime smoke-test caught a STALE assertion there
(len==1) that shimmer — a legitimate 2-tween effect (reveal + sweep) whose tweens the consumer
tweens.extend()s — falsely tripped. These enforce the REAL contract every run."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import effect_library as el


def _is_gsap(x):
    return isinstance(x, str) and ("tl." in x or "fromTo" in x)


class TestEffectLibrary(unittest.TestCase):
    def test_every_text_effect_returns_valid_tweens(self):
        # ≥1 tween, each a GSAP timeline call — the invariant the render (tweens.extend) actually relies on.
        for nm, fn in el.TEXT_EFFECTS.items():
            t = fn("s", 5.0)
            self.assertTrue(t, nm)                                   # non-empty
            self.assertTrue(all(_is_gsap(x) for x in t), nm)        # each a real tween

    def test_shimmer_is_multi_tween(self):
        # shimmer must emit BOTH the headline reveal AND the sweep — dropping either would half-break it.
        t = el.TEXT_EFFECTS["shimmer"]("s", 5.0)
        self.assertEqual(len(t), 2)
        self.assertTrue(any("--sp" in x for x in t))                # the sweep tween is present

    def test_every_transition_returns_two_tweens(self):
        for nm, fn in el.TRANSITIONS.items():
            t = fn('"#s .kicker"', '"#s .comp"', 5.0)
            self.assertEqual(len(t), 2, nm)
            self.assertTrue(all("fromTo" in x for x in t), nm)

    def test_order_lists_cover_registries(self):
        # a name in the rotation ORDER but missing from the registry → KeyError at render time.
        for name in el.TEXT_EFFECT_ORDER:
            self.assertIn(name, el.TEXT_EFFECTS, name)
        for name in el.TRANSITION_ORDER:
            self.assertIn(name, el.TRANSITIONS, name)

    def test_text_effect_picker_is_deterministic(self):
        # same (idx, seed) → same effect (stable per-video rotation).
        a = el.text_effect("s", 5.0, 3, "seed-x")
        b = el.text_effect("s", 5.0, 3, "seed-x")
        self.assertEqual(a[1], b[1])


if __name__ == "__main__":
    unittest.main()
