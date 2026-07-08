"""Regression test: mascot_rig._face must return None on ANY failure (its documented contract).

Same bug class as mascot_talk._locate_mouth: the old guard wrapped only the MediaPipe import,
leaving process()/landmark access unguarded, so a processing error propagated as an opaque
MediaPipe traceback instead of the intended None (which the caller turns into a clean
"no face found in mascot" RuntimeError). The whole body is now guarded.

Robust to MediaPipe being absent: if the import fails we get None anyway; if it succeeds, the
bad input still exercises the body guard.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

import mascot_rig as mr  # noqa: E402


class FaceContractTests(unittest.TestCase):
    def test_bad_input_returns_none(self):
        class NoSize:            # accessing .size raises AttributeError inside the guarded body
            def convert(self, mode):
                return self
        self.assertIsNone(mr._face(NoSize()))       # must not propagate

    def test_convert_error_returns_none(self):
        class BadImg:
            size = (64, 64)

            def convert(self, mode):
                raise RuntimeError("boom during processing")
        self.assertIsNone(mr._face(BadImg()))


if __name__ == "__main__":
    unittest.main()
