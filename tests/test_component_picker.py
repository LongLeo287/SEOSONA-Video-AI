"""Regression tests for component_picker.enrich_llm's apply-the-LLM-assignment contract.

  - keys are ALWAYS valid scene indices (an out-of-range i from the model is dropped),
  - numeric viz (linechart/donut/pie) is GROUNDED — dropped unless the scene has ≥2 real
    numbers, so the model can't fabricate a chart,
  - _validate still shapes the data.

Hermetic: _real_llm + generate_json_strict are stubbed (no network).
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import component_picker as cp  # noqa: E402
import llm_engine as le  # noqa: E402

SCENES = [
    {"seg": "Cảnh không có số nào ở đây", "h1": "A"},
    {"seg": "OpenClaw 77 điểm, Hermes 85, con người 93", "h1": "B"},
]


class EnrichLlmContractTests(unittest.TestCase):
    def setUp(self):
        self._real = cp._real_llm
        self._gen = le.generate_json_strict
        self._env = os.environ.get("SEOSONA_LLM_COMPONENTS")
        cp._real_llm = lambda: True
        os.environ["SEOSONA_LLM_COMPONENTS"] = "1"

    def tearDown(self):
        cp._real_llm = self._real
        le.generate_json_strict = self._gen
        if self._env is None:
            os.environ.pop("SEOSONA_LLM_COMPONENTS", None)
        else:
            os.environ["SEOSONA_LLM_COMPONENTS"] = self._env

    def _run(self, assign):
        le.generate_json_strict = lambda s, u, require_key=None: {"assign": assign}
        return cp.enrich_llm(SCENES)

    def test_out_of_range_index_dropped(self):
        res = self._run([{"i": 999, "kind": "alert", "data": {"role": "caution", "title": "X", "text": "y"}}])
        self.assertNotIn(999, res)
        self.assertTrue(all(0 <= k < len(SCENES) for k in res))

    def test_negative_index_dropped(self):
        res = self._run([{"i": -1, "kind": "alert", "data": {"role": "caution", "title": "X", "text": "y"}}])
        self.assertEqual(res, {})

    def test_grounded_numeric_kept(self):
        res = self._run([{"i": 1, "kind": "bars",
                          "data": {"items": [["OpenClaw", 77], ["Hermes", 85], ["Con người", 93]]}}])
        self.assertEqual(res.get(1, (None,))[0], "bars")

    def test_ungrounded_chart_dropped(self):
        # scene 0 has no numbers → a donut there is fabricated → dropped
        res = self._run([{"i": 0, "kind": "donut", "data": {"segments": [["A", 60], ["B", 40]]}}])
        self.assertNotIn(0, res)

    def test_valid_index_all_in_range(self):
        res = self._run([{"i": 1, "kind": "alert", "data": {"role": "caution", "title": "T", "text": "body"}}])
        self.assertTrue(all(0 <= k < len(SCENES) for k in res))


class MenuAllowedConsistencyTests(unittest.TestCase):
    """A component the LLM MENU advertises AND _validate shapes must be in _allowed() — else enrich_llm
    drops it at the gate (wasted LLM effort, lost visual)."""

    def test_rich_frames_are_llm_assignable(self):
        rich = ["comparison_grid", "split_reveal", "annotated_screenshot", "stat_grid",
                "ratio_dots", "layer_stack", "ticker_feed", "org_diagram", "concept_build"]
        allowed = cp._allowed()
        for k in rich:
            self.assertIn(k, allowed, f"{k} is validated+rendered+menu-advertised but not LLM-assignable")

    def test_no_menu_kind_is_validated_yet_dropped(self):
        # every kind _validate accepts (with correct data) must be reachable via _allowed()
        samples = {
            "comparison_grid": {"cols": [{"name": "A"}, {"name": "B"}], "rows": [["c", "x", "y"], ["d", "1", "2"]]},
            "stat_grid": {"stats": [{"value": "1", "label": "a"}, {"value": "2", "label": "b"}]},
            "org_diagram": {"parent": "P", "nodes": [{"label": "a"}, {"label": "b"}]},
        }
        allowed = cp._allowed()
        for k, d in samples.items():
            if cp._validate(k, d) is not None:
                self.assertIn(k, allowed)


class PickFillNoneSafetyTests(unittest.TestCase):
    """A text-less scene (seg=None) must not crash picking (seg.lower() / _nums(None))."""

    def test_pick_none_returns_none(self):
        self.assertIsNone(cp.pick(None))
        self.assertIsNone(cp.pick(None, label_fn=lambda s: "lab"))

    def test_fill_always_returns_valid_component(self):
        for seg, h1, i, prev in [("", "", 0, None), ("Câu SEO.", "SEO", 1, None),
                                 (None, None, 0, None), ("x" * 200, "H", 5, "photocard")]:
            r = cp.fill(seg, h1=h1, i=i, prev_kind=prev,
                        label_fn=lambda s: (s or "")[:20], concept="ống kính")
            self.assertIsInstance(r, tuple)
            self.assertEqual(len(r), 2)
            self.assertIsInstance(r[1], dict)


if __name__ == "__main__":
    unittest.main()
