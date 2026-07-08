"""Regression test: the quality gate must score the FINAL video, not an intermediate.

workflow_router.evaluate_node used to scan the project dir and score the first .mp4 in walk
order — which can be an intermediate `_raw.mp4` (no captions/BGM), poisoning the learning-loop
quality signal. It now prefers the pipeline's returned output path and skips intermediates.
"""
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

try:
    import workflow_router as wr
    _ERR = None
except Exception as e:
    wr, _ERR = None, e


@unittest.skipIf(wr is None, f"workflow_router import failed: {_ERR}")
class PickScoredVideoTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "assets"))
        self.raw = os.path.join(self.d, "assets", "_raw.mp4")
        self.final = os.path.join(self.d, "v - SEOSONA.mp4")
        open(self.raw, "w").close()
        open(self.final, "w").close()

    def test_prefers_pipeline_output_path(self):
        self.assertEqual(wr._pick_scored_video(self.final, self.d), self.final)

    def test_scan_prefers_final_over_raw_intermediate(self):
        # no output path → scan the dir, but the FINAL video must win over _raw.mp4
        self.assertEqual(wr._pick_scored_video(None, self.d), self.final)

    def test_falls_back_to_raw_when_only_intermediate(self):
        d2 = tempfile.mkdtemp()
        raw = os.path.join(d2, "_raw.mp4"); open(raw, "w").close()
        self.assertEqual(wr._pick_scored_video(None, d2), raw)

    def test_none_when_nothing(self):
        self.assertIsNone(wr._pick_scored_video(None, tempfile.mkdtemp()))

    def test_ignores_non_mp4_output(self):
        # a stray non-mp4 output value must not be scored; scan instead
        self.assertEqual(wr._pick_scored_video("/x/notes.txt", self.d), self.final)


@unittest.skipIf(wr is None, f"workflow_router import failed: {_ERR}")
class DownloadSkillGuardTests(unittest.TestCase):
    """A missing/broken yt_downloader skill must abort cleanly, not AttributeError-crash the route."""

    def setUp(self):
        self._saved = wr.get_skill

    def tearDown(self):
        wr.get_skill = self._saved

    def test_missing_skill_aborts_cleanly(self):
        wr.get_skill = lambda name: None
        self.assertIsNone(wr.route("https://youtu.be/abc123"))

    def test_skill_without_download_video_aborts_cleanly(self):
        wr.get_skill = lambda name: object()      # has no download_video attr
        self.assertIsNone(wr.route("https://drive.google.com/file/d/x"))


if __name__ == "__main__":
    unittest.main()
