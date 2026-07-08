"""Regression tests for the YouTube uploader's reliability contract.

The uploader shells out to the `yutu` CLI. It must:
  - bound the upload with a timeout (a stalled upload must never hang the publish step forever),
  - never raise for a missing binary — degrade to a False result so the dispatcher continues,
  - raise FileNotFoundError for a missing input video (a caller bug, surfaced early).

Hermetic: no real yutu, no network — uses a bogus binary name and a temp file.
"""
import inspect
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "1_AGENTS", "publisher_agent"))

import youtube_uploader as yu  # noqa: E402


class YouTubeUploaderContractTests(unittest.TestCase):
    def setUp(self):
        self.agent = yu.YouTubePublisherAgent(yutu_bin="definitely-not-a-real-binary-xyz")
        self.dir = tempfile.mkdtemp()
        self.vid = os.path.join(self.dir, "v.mp4")
        with open(self.vid, "wb") as f:
            f.write(b"x")

    def test_upload_is_time_bounded(self):
        # a stalled upload must not hang forever — the subprocess call carries an explicit timeout.
        src = inspect.getsource(yu.YouTubePublisherAgent.upload_video)
        self.assertIn("timeout=", src)
        self.assertIn("TimeoutExpired", src)

    def test_missing_binary_degrades_to_false(self):
        self.assertIs(self.agent.upload_video(self.vid, "Title"), False)

    def test_missing_video_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.agent.upload_video(os.path.join(self.dir, "nope.mp4"), "Title")


if __name__ == "__main__":
    unittest.main()
