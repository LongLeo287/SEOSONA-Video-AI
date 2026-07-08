# -*- coding: utf-8 -*-
"""Regression test: the QA pacing dimension must be scored from the per-project sidecar, not silently
skipped.

Renders run in queue_processor SUBPROCESSES while score_video runs in the PARENT, so
native_composer._LAST_PACING (an in-memory global) is None at scoring time → the pacing check hit its
`else: total_points += 15` full-credit SKIP branch, disabling the dimension added to catch slow
slideshows. native_composer now writes _pacing.json next to the video; the scorer reads it cross-process.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import quality_scorer as qs  # noqa: E402
import native_composer as nc  # noqa: E402


class PacingSidecarTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="qs_test_")
        self.mp4 = os.path.join(self.d, "FINAL.mp4")
        with open(self.mp4, "wb") as f:
            f.write(b"\x00" * 100000)                     # a stand-in file (ffprobe will reject; pacing is independent)
        self._orig_global = getattr(nc, "_LAST_PACING", None)
        nc._LAST_PACING = None                            # prove the SIDECAR path, not the in-process global

    def tearDown(self):
        nc._LAST_PACING = self._orig_global
        shutil.rmtree(self.d, ignore_errors=True)

    def test_pacing_scored_from_sidecar_not_skipped(self):
        with open(os.path.join(self.d, "_pacing.json"), "w", encoding="utf-8") as f:
            json.dump({"durations": [3.0, 4.0, 3.5, 4.0, 3.5], "total": 18.0}, f)
        r = qs.score_video(self.mp4)
        self.assertIn("pacing", r["checks"])
        self.assertNotEqual(r["checks"]["pacing"]["status"], "SKIP")   # sidecar read → real pacing score

    def test_no_sidecar_and_no_global_skips(self):
        r = qs.score_video(self.mp4)                      # no sidecar, global None → SKIP (unchanged behaviour)
        self.assertEqual(r["checks"]["pacing"]["status"], "SKIP")


if __name__ == "__main__":
    unittest.main()
