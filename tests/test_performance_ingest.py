"""Regression test: performance ingest (OBSERVE stage) must not crash on a manifest missing video_id.

A single old/hand-edited manifest without 'video_id' previously KeyError-crashed the whole ingest
via {m["video_id"]: m ...}, so the learning signal never updated. It now skips that manifest.

Hermetic: production_manifest.scan / set_performance are stubbed.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "1_AGENTS", "analytics_feedback_agent"))

import performance_ingest as pi  # noqa: E402


class IngestRobustnessTests(unittest.TestCase):
    def setUp(self):
        self._scan = pi.pm.scan
        self._setperf = pi.pm.set_performance
        self.recorded = []
        pi.pm.scan = lambda ws=None: [
            {"video_id": "vidA", "project_dir": "/p/a"},
            {"project_dir": "/p/b", "variant": {}},          # MISSING video_id → must be skipped
        ]
        pi.pm.set_performance = lambda pdir, metrics: self.recorded.append((pdir, metrics))

    def tearDown(self):
        pi.pm.scan = self._scan
        pi.pm.set_performance = self._setperf

    def test_missing_video_id_does_not_crash_inject(self):
        r = pi.ingest(inject={"vidA": {"views": 100, "ctr": 0.1}})
        self.assertEqual(r["mode"], "inject")
        self.assertIn("vidA", r["updated"])
        self.assertEqual(self.recorded, [("/p/a", {"views": 100, "ctr": 0.1})])

    def test_unknown_inject_id_is_skipped(self):
        r = pi.ingest(inject={"nope": {"views": 1}})
        self.assertIn("nope", r["skipped"])
        self.assertEqual(self.recorded, [])


if __name__ == "__main__":
    unittest.main()
