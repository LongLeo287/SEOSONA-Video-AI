# -*- coding: utf-8 -*-
"""Lock native_composer._KICKER_EMOJI's stated invariant: every kicker icon must be a SINGLE codepoint
with NO variation selector (U+FE0F). The module comment records that variation-selector emoji (⚙️ ⚠️ 🛠️)
'showed up blank in the render' — a PROVEN, VISIBLE failure (an empty box leads the kicker pill). The
factory loop grows this map (it just added it), and reaching for a natural-but-VS emoji like ⚙️ for
'SETUP' would silently reintroduce the blank. Lock it so drift fails at CI, not in a shipped video."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import native_composer as nc

VARIATION_SELECTOR = "️"


class TestKickerEmoji(unittest.TestCase):
    def test_no_variation_selector_or_multi_codepoint(self):
        bad = []
        for label, emo in nc._KICKER_EMOJI.items():
            if VARIATION_SELECTOR in emo or len(emo) != 1:
                bad.append(f"{label!r}={emo!r} (codepoints={[hex(ord(c)) for c in emo]})")
        self.assertEqual(bad, [], "kicker emoji that render BLANK (variation-selector / multi-codepoint): "
                                  + "; ".join(bad))

    def test_map_nonempty(self):
        self.assertGreater(len(nc._KICKER_EMOJI), 5)

    def test_kicker_label_prefixes_known_and_passes_unknown(self):
        # a mapped label gets its icon; an unmapped one is returned unchanged (never a stray blank prefix).
        any_label = next(iter(nc._KICKER_EMOJI))
        self.assertTrue(nc._kicker_label(any_label).endswith(any_label))
        self.assertEqual(nc._kicker_label("KHÔNG-CÓ-TRONG-MAP-XYZ"), "KHÔNG-CÓ-TRONG-MAP-XYZ")


if __name__ == "__main__":
    unittest.main()
