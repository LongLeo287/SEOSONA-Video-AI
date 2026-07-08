# -*- coding: utf-8 -*-
"""Regression test: a malformed performance value must not crash the ledger rebuild (LEARN/ORIENT stage).

_perf_score did `float(perf["retention"])` unguarded — an injected/API value of "N/A"/""/text raised
ValueError, which propagated through rebuild() (uncaught) and crashed the whole factory LEARN stage
(factory_brain.learn doesn't guard rebuild). Bad real metrics now fall back to the QA proxy.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import factory_ledger as fl  # noqa: E402


class PerfScoreRobustnessTests(unittest.TestCase):
    def test_malformed_metrics_fall_back_to_qa(self):
        self.assertAlmostEqual(fl._perf_score({"performance": {"retention": "N/A"},
                                               "quality": {"score": 80}}), 0.80, places=3)
        self.assertAlmostEqual(fl._perf_score({"performance": {"retention": "", "ctr": None},
                                               "quality": {"score": 60}}), 0.60, places=3)

    def test_valid_metrics_scored(self):
        self.assertAlmostEqual(fl._perf_score({"performance": {"retention": 0.6, "ctr": 0.05}}), 0.57, places=2)

    def test_no_data_neutral(self):
        self.assertEqual(fl._perf_score({}), 0.5)
        self.assertEqual(fl._perf_score({"performance": {}, "quality": {"score": 90}}), 0.9)


class RebuildRobustnessTests(unittest.TestCase):
    def setUp(self):
        self._scan = fl.pm.scan
        fl.pm.scan = lambda ws=None: [
            {"performance": {"retention": "bad", "ctr": "x"}, "quality": {"score": 70, "pass": True},
             "variant": {"template": "t1"}},
            {"quality": {"score": 85, "pass": True}, "variant": {"template": "t2"}},
        ]

    def tearDown(self):
        fl.pm.scan = self._scan

    def test_rebuild_survives_malformed_manifest(self):
        led = fl.rebuild(write=False)                 # must not raise
        self.assertEqual(led["total_videos"], 2)
        self.assertIn("template", led["dimensions"])


if __name__ == "__main__":
    unittest.main()
