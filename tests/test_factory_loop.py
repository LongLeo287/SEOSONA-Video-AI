# -*- coding: utf-8 -*-
"""Tests for the autonomous-factory loop core: manifest tagging + learning ledger.

Hermetic: builds synthetic manifests in a temp workspace (no render / ffprobe), so
the closed loop (variant tag → aggregate → weights → performance merge) is verified
without producing real videos.
"""
import os
import sys
import json
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import production_manifest as pm  # noqa: E402
import factory_ledger as fl  # noqa: E402


def _write_manifest(ws, vid, template, score, brand="seosona", perf=None):
    d = os.path.join(ws, vid)
    os.makedirs(d, exist_ok=True)
    man = {
        "video_id": vid, "project_dir": d, "created": "2026-06-29T10:00:00+07:00",
        "engine": "synthesized",
        "variant": {"template": template, "brand": brand, "aspect": "9:16",
                    "voice": "chiquyet", "topic": "seo", "source": "test",
                    "length_bucket": "30-60s", "hook_style": None, "thumbnail_style": None},
        "duration_s": 45.0, "outputs": {"mp4": None, "srt": None, "thumbnail": None},
        "quality": {"score": score, "pass": score >= 60}, "performance": perf or {},
    }
    with open(os.path.join(d, pm.MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(man, f)
    return d


class ManifestTests(unittest.TestCase):
    def test_scan_and_load(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_manifest(ws, "vidA", "repo-showcase", 100)
            _write_manifest(ws, "vidB", "data-news", 80)
            found = pm.scan(ws)
            self.assertEqual(len(found), 2)
            ids = {m["video_id"] for m in found}
            self.assertEqual(ids, {"vidA", "vidB"})

    def test_set_performance_merges(self):
        with tempfile.TemporaryDirectory() as ws:
            d = _write_manifest(ws, "vidA", "repo-showcase", 100)
            pm.set_performance(d, {"views": 1000, "ctr": 0.08, "retention": 0.6})
            m = pm.load(d)
            self.assertEqual(m["performance"]["views"], 1000)
            self.assertIn("updated", m["performance"])

    def test_length_bucket(self):
        self.assertEqual(pm._length_bucket(20), "<30s")
        self.assertEqual(pm._length_bucket(45), "30-60s")
        self.assertEqual(pm._length_bucket(90), "60-120s")
        self.assertEqual(pm._length_bucket(200), ">120s")


class LedgerTests(unittest.TestCase):
    def test_rebuild_ranks_by_score_qa_signal(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_manifest(ws, "a", "repo-showcase", 100)
            _write_manifest(ws, "b", "repo-showcase", 90)
            _write_manifest(ws, "c", "data-news", 60)
            led = fl.rebuild(ws, write=False)
            self.assertEqual(led["total_videos"], 3)
            self.assertEqual(led["signal"], "qa-only")
            tmpl = led["dimensions"]["template"]
            # repo-showcase (avg 0.95) must rank above data-news (0.60)
            keys = list(tmpl.keys())
            self.assertEqual(keys[0], "repo-showcase")
            self.assertGreater(tmpl["repo-showcase"]["avg_score"], tmpl["data-news"]["avg_score"])

    def test_template_weights_have_floor_and_winner(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_manifest(ws, "a", "winner", 100)
            _write_manifest(ws, "b", "loser", 60)
            led = fl.rebuild(ws, write=False)
            w = led["template_weights"]
            # Bayesian shrinkage maps the confidence-adjusted score onto [floor, 1] on a FIXED scale
            # (NOT min-max), so a 1-sample winner is pulled toward the global mean instead of being
            # pinned to 1.0 — it must still out-weight the loser and stay within (floor, 1].
            self.assertGreater(w["winner"], w["loser"])   # winner still ranks higher
            self.assertLessEqual(w["winner"], 1.0)        # fixed scale never exceeds 1
            self.assertGreater(w["winner"], 0.5)          # a top template still earns a high weight
            self.assertGreaterEqual(w["loser"], 0.15)     # exploration floor never zero

    def test_shrinkage_favors_more_samples(self):
        # A template proven over MANY high-scoring videos must out-weight a 1-video fluke of the same
        # score — the whole point of the confidence adjustment (else the flywheel learns from noise).
        with tempfile.TemporaryDirectory() as ws:
            for k in range(6):
                _write_manifest(ws, f"p{k}", "proven", 100)
            _write_manifest(ws, "f", "fluke", 100)
            _write_manifest(ws, "z", "baseline", 40)   # drags the global mean below 1.0 so shrinkage bites
            w = fl.rebuild(ws, write=False)["template_weights"]
            self.assertGreater(w["proven"], w["fluke"])

    def test_real_performance_upgrades_signal(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_manifest(ws, "a", "repo-showcase", 70,
                            perf={"views": 5000, "ctr": 0.1, "retention": 0.7})
            led = fl.rebuild(ws, write=False)
            self.assertEqual(led["signal"], "real+qa")
            # perf score should reflect strong retention, not just the 0.70 QA
            self.assertGreater(led["dimensions"]["template"]["repo-showcase"]["avg_score"], 0.7)


if __name__ == "__main__":
    unittest.main()
