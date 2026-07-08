"""Regression tests for spec_lint — the pre-render blank-risk / discipline gate.

Focus of the fix locked here: BLANK-RISK uses an explicit emptiness check, so a numeric 0
(bignum big=0, gauge value=0) is treated as real data, while missing keys and empty
strings/lists are still flagged.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import spec_lint as sl  # noqa: E402


class BlankRiskTests(unittest.TestCase):
    def test_zero_value_is_not_blank(self):
        self.assertEqual(sl._comp_blankrisk("bignum", {"big": 0}), [])
        self.assertEqual(sl._comp_blankrisk("gauge", {"value": 0}), [])
        self.assertEqual(sl._comp_blankrisk("ratio_dots", {"total": 0}), [])

    def test_missing_field_is_flagged(self):
        self.assertTrue(sl._comp_blankrisk("bignum", {}))
        self.assertTrue(sl._comp_blankrisk("bars", {"items": []}))     # empty list = missing
        self.assertTrue(sl._comp_blankrisk("quote", {"text": ""}))     # empty string = missing

    def test_present_field_passes(self):
        self.assertEqual(sl._comp_blankrisk("bars", {"items": [["a", 5]]}), [])
        self.assertEqual(sl._comp_blankrisk("bignum", {"big": "38,000"}), [])

    def test_lint_scenes_flags_only_empty_component(self):
        r = sl.lint_scenes([
            {"h1": "A", "comp": ("bignum", {"big": 0})},         # valid 0 — no flag
            {"h1": "B", "comp": ("bars", {"items": []})},        # empty — flag
            {"h1": "C", "comp": ("quote", {"text": "x"})},
            {"h1": "D", "comp": ("tip", {"text": "y"})},
        ])
        blanks = [x for x in r["warnings"] if "BLANK-RISK" in x]
        self.assertEqual(len(blanks), 1)
        self.assertIn("scene 1", blanks[0])


class DisciplineRuleTests(unittest.TestCase):
    def test_low_variety_flagged(self):
        scenes = [{"h1": str(i), "comp": ("quote", {"text": "x"})} for i in range(4)]
        r = sl.lint_scenes(scenes)
        self.assertTrue(any("LOW-VARIETY" in x for x in r["warnings"]))

    def test_empty_scene_list_not_ok(self):
        self.assertFalse(sl.lint_scenes([])["ok"])


class AllowedKindsHaveBlankRiskContractTests(unittest.TestCase):
    """Every LLM-assignable component (_ALLOWED) must have a blank-risk contract here, so a template /
    LLM-direct set with empty data is caught pre-render (defense-in-depth floor)."""

    def test_no_allowed_kind_is_ungated(self):
        import component_picker as cp
        # Every STATIC LLM-assignable kind (_ALLOWED) needs an explicit _REQUIRED contract. Self-grown
        # frame_synth kinds are LLM-assignable too but have arbitrary runtime schemas — they're floored
        # GENERICALLY in _comp_blankrisk (not listed in _REQUIRED), so subtract them from the gap check.
        gap = sorted(cp._allowed() - set(sl._REQUIRED.keys()) - sl._grown_kinds())
        self.assertEqual(gap, [], f"LLM-assignable but not blank-risk-gated: {gap}")

    def test_grown_frame_with_empty_data_is_floored(self):
        # a self-grown kind assigned with NO data must be caught generically (would render blank)
        grown = sl._grown_kinds()
        if grown:
            k = next(iter(grown))
            self.assertTrue(sl._comp_blankrisk(k, {}), f"grown '{k}' empty should be blank-risk")
            self.assertFalse(sl._comp_blankrisk(k, {"title": "x"}), f"grown '{k}' with data should pass")

    def test_new_rich_kinds_flag_when_empty(self):
        for kind in ("comparison_grid", "split_reveal", "annotated_screenshot", "concept_build", "filetree"):
            self.assertTrue(sl._comp_blankrisk(kind, {}), f"{kind} empty should be blank-risk")


if __name__ == "__main__":
    unittest.main()
