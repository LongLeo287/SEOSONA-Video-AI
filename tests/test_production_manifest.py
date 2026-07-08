"""Regression tests for production_manifest — the data layer the whole learning loop reads.

A single corrupt or minimal manifest must never crash factory_brain / set_performance:
  - load(corrupt/missing) → None (degrade, like scan() already does),
  - set_performance on a manifest with no 'performance' key → creates it, no KeyError,
  - scan() skips corrupt files.
"""
import json
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import production_manifest as pm  # noqa: E402


def _write(d, obj_or_text):
    p = os.path.join(d, pm.MANIFEST_NAME)
    with open(p, "w", encoding="utf-8") as f:
        if isinstance(obj_or_text, str):
            f.write(obj_or_text)
        else:
            json.dump(obj_or_text, f)
    return p


class LoadRobustnessTests(unittest.TestCase):
    def test_missing_returns_none(self):
        self.assertIsNone(pm.load(tempfile.mkdtemp()))

    def test_corrupt_returns_none(self):
        d = tempfile.mkdtemp()
        _write(d, "{ broken json,,,")
        self.assertIsNone(pm.load(d))            # degrade, not crash

    def test_valid_loads(self):
        d = tempfile.mkdtemp()
        _write(d, {"video_id": "y", "performance": {"views": 5}})
        self.assertEqual(pm.load(d)["video_id"], "y")


class SetPerformanceTests(unittest.TestCase):
    def test_creates_missing_performance_key(self):
        d = tempfile.mkdtemp()
        _write(d, {"video_id": "x"})             # no 'performance' key
        r = pm.set_performance(d, {"views": 100})
        self.assertEqual(r["performance"]["views"], 100)

    def test_merges_into_existing_performance(self):
        d = tempfile.mkdtemp()
        _write(d, {"video_id": "y", "performance": {"views": 5}})
        r = pm.set_performance(d, {"ctr": 0.1})
        self.assertEqual(r["performance"]["views"], 5)
        self.assertEqual(r["performance"]["ctr"], 0.1)

    def test_missing_manifest_returns_none(self):
        self.assertIsNone(pm.set_performance(tempfile.mkdtemp(), {"views": 1}))


class ScanTests(unittest.TestCase):
    def test_scan_skips_corrupt(self):
        ws = tempfile.mkdtemp()
        _write(os.path.join(ws, "a"), {"video_id": "a"}) if False else None
        good = os.path.join(ws, "good"); os.makedirs(good)
        bad = os.path.join(ws, "bad"); os.makedirs(bad)
        _write(good, {"video_id": "good"})
        _write(bad, "{ nope")
        ids = {m.get("video_id") for m in pm.scan(ws)}
        self.assertIn("good", ids)
        self.assertNotIn(None, ids - {"good"})   # the corrupt one contributed nothing

    def test_length_bucket(self):
        self.assertEqual(pm._length_bucket(10), "<30s")
        self.assertEqual(pm._length_bucket(200), ">120s")
        self.assertEqual(pm._length_bucket(None), "unknown")


if __name__ == "__main__":
    unittest.main()
