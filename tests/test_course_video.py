"""Regression tests for course_video's cut + caption logic.

Pure helpers (captions_from_plan, _first_num, _headline) run hermetically. The core `splice`
cut-length behavior (a wrong -ss/-to would make every course-video cut the wrong length) is
verified with real ffmpeg, skipped if ffmpeg is absent.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

import course_video as cv  # noqa: E402

_HAVE_FFMPEG = shutil.which("ffmpeg") is not None


class CaptionTimingTests(unittest.TestCase):
    def test_even_spacing_covers_the_segment(self):
        segs = [{"display": "một hai ba bốn", "start": 0.0, "end": 4.0}]
        words, sfx = cv.captions_from_plan(segs, [4.0], asr_words=None)
        self.assertEqual(len(words), 4)
        self.assertAlmostEqual(words[0]["start"], 0.0, places=2)
        self.assertAlmostEqual(words[-1]["end"], 4.0, places=1)   # last word ends at segment end
        # words are monotonic and non-overlapping
        for a, b in zip(words, words[1:]):
            self.assertLessEqual(a["end"], b["start"] + 1e-6)

    def test_zero_duration_falls_back_to_start_end(self):
        segs = [{"display": "a b", "start": 2.0, "end": 5.0}]
        words, _ = cv.captions_from_plan(segs, [0.0], asr_words=None)   # seg_dur 0 → use end-start=3s
        self.assertEqual(len(words), 2)
        self.assertAlmostEqual(words[-1]["end"], 3.0, places=1)

    def test_transition_sfx_between_segments_only(self):
        segs = [{"display": "x", "start": 0, "end": 1}, {"display": "y", "start": 1, "end": 2}]
        _, sfx = cv.captions_from_plan(segs, [1.0, 1.0])
        self.assertEqual(len(sfx), 1)                              # one splice point → one SFX


class TextHelperTests(unittest.TestCase):
    def test_first_num(self):
        self.assertEqual(cv._first_num("tăng 47% doanh thu"), "47%")
        self.assertEqual(cv._first_num("không có số"), "")

    def test_headline_truncates(self):
        self.assertTrue(cv._headline("một hai ba bốn năm sáu bảy", n=3).endswith("…"))


@unittest.skipUnless(_HAVE_FFMPEG, "ffmpeg required")
class SpliceLengthTests(unittest.TestCase):
    def test_cut_length_is_end_minus_start(self):
        d = tempfile.mkdtemp()
        src = os.path.join(d, "src.mp4")
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-f", "lavfi", "-i", "color=c=green:s=320x240:d=10",
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                        "-shortest", "-pix_fmt", "yuv420p", "-c:a", "aac", src],
                       capture_output=True, timeout=60)
        out, durs = cv.splice(src, [{"start": 3.0, "end": 6.0}], os.path.join(d, "out.mp4"))
        self.assertIsNotNone(out)
        self.assertTrue(2.5 < cv._duration(out) < 3.6)            # [3,6] → ~3s, NOT ~6s
        self.assertIsNone(cv.splice(src, [], os.path.join(d, "e.mp4"))[0])   # no segments → None


class SpliceFailedSegmentTests(unittest.TestCase):
    """A failed segment cut must ABORT (not silently drop a segment → desynced captions)."""

    def setUp(self):
        self._run = cv.subprocess.run
        self._dur = cv._duration
        cv._duration = lambda p: 2.0

    def tearDown(self):
        cv.subprocess.run = self._run
        cv._duration = self._dur

    class _R:
        def __init__(self, rc):
            self.returncode, self.stdout, self.stderr = rc, "", ""

    def test_aborts_when_a_segment_fails(self):
        segs = [{"start": 0.0, "end": 2.0}, {"start": 2.0, "end": 4.0}, {"start": 4.0, "end": 6.0}]

        def run(cmd, **k):
            if "-ss" in cmd:                                  # a segment cut
                if cmd[cmd.index("-ss") + 1] == "2.00":       # fail the middle one, no file written
                    return self._R(1)
                open(cmd[-1], "wb").write(b"x")
                return self._R(0)
            open(cmd[-1], "wb").write(b"y")                   # concat
            return self._R(0)
        cv.subprocess.run = run
        out, durs = cv.splice("src.mp4", segs, os.path.join(tempfile.mkdtemp(), "o.mp4"))
        self.assertIsNone(out)
        self.assertEqual(durs, [])

    def test_all_segments_succeed_returns_path(self):
        def run(cmd, **k):
            open(cmd[-1], "wb").write(b"x")
            return self._R(0)
        cv.subprocess.run = run
        segs = [{"start": 0.0, "end": 2.0}, {"start": 2.0, "end": 4.0}]
        out, durs = cv.splice("src.mp4", segs, os.path.join(tempfile.mkdtemp(), "o.mp4"))
        self.assertIsNotNone(out)
        self.assertEqual(len(durs), 2)


if __name__ == "__main__":
    unittest.main()
