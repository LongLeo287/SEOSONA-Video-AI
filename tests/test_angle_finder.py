# -*- coding: utf-8 -*-
"""Regression test: one malformed angle/novelty must not discard the WHOLE angle result.

find_angles picked the recommended angle via `int(pool[i].get("novelty",0) or 0)`. A float-string
novelty ("4.5" → int() ValueError) or a non-dict angle (.get AttributeError) raised, hit the outer
except, and returned None — losing ALL angles (the whole enrichment) over one bad element. Per-item safe
coercion now scores the bad one 0 so the good angles survive.
"""
import os
import sys
import types
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import angle_finder as af  # noqa: E402


class AngleNoveltyRobustnessTests(unittest.TestCase):
    def setUp(self):
        self._ready, self._imp = af._llm_ready, af.import_module
        af._llm_ready = lambda: True

    def tearDown(self):
        af._llm_ready, af.import_module = self._ready, self._imp

    def _wire(self, angles):
        fake = types.SimpleNamespace(generate_json_strict=lambda *a, **k: {"angles": angles})
        af.import_module = lambda name: fake

    def test_float_string_novelty_does_not_discard_all(self):
        self._wire([
            {"headline": "Góc nhìn thứ nhất", "hook": "a", "novelty": "4.5"},   # float-string (was the crash)
            {"headline": "Góc nhìn hay nhất", "hook": "b", "novelty": 5},
            "not a dict",                                                       # malformed element
        ])
        r = af.find_angles("chủ đề test")
        self.assertIsNotNone(r)                                                # survived, not None
        self.assertEqual(r["angles"][r["recommended"]]["headline"], "Góc nhìn hay nhất")  # highest novelty

    def test_no_llm_returns_none(self):
        af._llm_ready = lambda: False
        self.assertIsNone(af.find_angles("x"))


if __name__ == "__main__":
    unittest.main()
