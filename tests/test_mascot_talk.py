"""Regression test: _locate_mouth must return None on ANY failure (its documented contract).

MediaPipe's process()/landmark access can raise on odd inputs. The old guard wrapped only the
imports, so a processing error propagated and failed the mascot render. It now returns None so
make_talking_mascot falls back to a default mouth position.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

import mascot_talk as mt  # noqa: E402


class LocateMouthContractTests(unittest.TestCase):
    def test_processing_error_returns_none(self):
        class BadImg:
            size = (100, 100)

            def convert(self, mode):
                raise RuntimeError("boom during processing")
        self.assertIsNone(mt._locate_mouth(BadImg()))   # must not propagate

    def test_missing_size_returns_none(self):
        class NoSize:
            def convert(self, mode):
                return self
        # accessing .size raises AttributeError inside the guarded body → None
        self.assertIsNone(mt._locate_mouth(NoSize()))


if __name__ == "__main__":
    unittest.main()
