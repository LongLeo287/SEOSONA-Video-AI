# -*- coding: utf-8 -*-
"""Batch-resilience for the data-viz render path: a single non-numeric value in a chart/linechart/donut/
pie must NOT crash native_composer._component (it runs in the render hot path — a raise kills the whole
video). donut/pie already guarded their per-item float() with try/except; chart + linechart did NOT
(bare float(it[1]) / float(p[1])) — a sibling inconsistency fixed 2026-07. These lock all four so a
malformed value (LLM 'N/A', a stray string, None) is SKIPPED, never fatal."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import native_composer as nc

ACC = "#2A5BDA"


class TestDataVizBatchResilience(unittest.TestCase):
    def test_chart_skips_non_numeric_bar(self):
        d = {"title": "T", "items": [("Good", 50), ("Bad", "N/A"), ("Also", 30), ("None", None)]}
        html = nc._component("chart", d, ACC)          # must not raise
        self.assertIn("c-chart", html)
        self.assertIn("Good", html)
        self.assertIn("Also", html)                    # the two valid bars survive
        self.assertNotIn("N/A", html)                  # the malformed bar was skipped, not rendered

    def test_linechart_points_skip_non_numeric(self):
        d = {"points": [("Jan", 10), ("Feb", "oops"), ("Mar", 30), ("Apr", 40)]}
        html = nc._component("linechart", d, ACC)      # must not raise
        self.assertIn("c-linechart", html)             # ≥2 valid points remain → still renders

    def test_linechart_values_skip_non_numeric(self):
        d = {"values": [10, "x", 30, 40], "labels": ["a", "b", "c", "d"]}
        html = nc._component("linechart", d, ACC)      # must not raise
        self.assertIsInstance(html, str)

    def test_donut_pie_still_guarded(self):
        # the sibling pattern this fix mirrors — assert it did not regress.
        for kind in ("donut", "pie"):
            d = {"segments": [("A", 3), ("B", "bad"), ("C", 5)]}
            html = nc._component(kind, d, ACC)          # must not raise
            self.assertIsInstance(html, str)

    def test_all_numeric_still_works(self):
        d = {"title": "T", "items": [("A", 40), ("B", 60)]}
        html = nc._component("chart", d, ACC)
        self.assertIn("40%", html)
        self.assertIn("60%", html)

    def test_concept_build_bad_coords_dont_crash(self):
        # node/frame coords are LLM-authored (x,y,w,h 0-1) → a stray string must default, not crash.
        d = {"nodes": [{"x": "left", "y": .5, "label": "A"}, {"x": .5, "y": "top", "label": "B"}],
             "edges": [(0, 1)], "frames": [{"x": .1, "y": .1, "w": "wide", "h": .3, "label": "F"}]}
        html = nc._component("concept_build", d, ACC)   # must not raise (bad coords default to center)
        self.assertIn("cb-frame", html)                 # frame with the "wide" width rendered (defaulted)

    def test_annotated_screenshot_bad_mark_coords_dont_crash(self):
        d = {"img": "x.png", "marks": [{"x": "?", "y": .1, "w": .3, "h": .15, "label": "here"}]}
        html = nc._component("annotated_screenshot", d, ACC)   # must not raise
        self.assertIsInstance(html, str)

    def test_ratio_dots_non_numeric_counts_default(self):
        d = {"total": "ten", "marked": None}
        html = nc._component("ratio_dots", d, ACC)      # must not raise → defaults 10/0
        self.assertIn("c-", html)

    def test_safe_coerce_helpers(self):
        self.assertEqual(nc._ff("N/A", 0.5), 0.5)
        self.assertEqual(nc._ff("3.5", 0.0), 3.5)
        self.assertEqual(nc._ii("ten", 10), 10)
        self.assertEqual(nc._ii("3.0", 0), 3)


if __name__ == "__main__":
    unittest.main()
