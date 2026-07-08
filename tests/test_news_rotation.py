"""Regression test: one video's render failure must NOT abort the whole news batch.

make_video.news_rotation renders many repos in a loop. A raising render (transient error, bad
data, resource) previously propagated and killed every subsequent video. It now skips the failed
one and continues.

Hermetic: fetch_github / classify / auto_content / make_video_from_template are stubbed; no real
render, no network.
"""
import os
import sys
import tempfile
import types
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import make_video as mv  # noqa: E402


class NewsRotationResilienceTests(unittest.TestCase):
    def setUp(self):
        self._saved = (mv.fetch_github, mv.classify, mv.auto_content, mv.nc.make_video_from_template)
        self._ve = sys.modules.get("video_engine")
        ghs = {"u1": {"name": "repoA", "full": "o/repoA", "desc": "d", "error": None},
               "u2": {"name": "repoB", "full": "o/repoB", "desc": "d", "error": None},
               "u3": {"name": "repoC", "full": "o/repoC", "desc": "d", "error": None}}
        mv.fetch_github = lambda u: ghs[u]
        mv.classify = lambda gh: ("data-news", "light", "r")
        mv.auto_content = lambda gh, t: {"x": 1}

        def render(t, content, proj, output=None, theme=None):
            if "repoB" in output:
                raise RuntimeError("render boom")
            open(output, "wb").write(b"x")
        mv.nc.make_video_from_template = render
        ve = types.ModuleType("video_engine")
        ve.score_output = lambda *a, **k: None
        ve.maybe_publish = lambda *a, **k: None
        sys.modules["video_engine"] = ve

    def tearDown(self):
        mv.fetch_github, mv.classify, mv.auto_content, mv.nc.make_video_from_template = self._saved
        if self._ve is None:
            sys.modules.pop("video_engine", None)
        else:
            sys.modules["video_engine"] = self._ve

    def test_failed_render_skips_and_batch_continues(self):
        out = tempfile.mkdtemp()
        res = dict(mv.news_rotation(["u1", "u2", "u3"], out_dir=out))
        self.assertIsNotNone(res["u1"])    # produced before the failure
        self.assertIsNone(res["u2"])       # failed → skipped
        self.assertIsNotNone(res["u3"])    # produced AFTER the failure (batch didn't abort)

    def test_fetch_error_skips_video(self):
        out = tempfile.mkdtemp()
        mv.fetch_github = lambda u: {"error": "Not Found", "full": u}
        res = dict(mv.news_rotation(["u1"], out_dir=out))
        self.assertIsNone(res["u1"])


if __name__ == "__main__":
    unittest.main()
