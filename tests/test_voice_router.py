"""Regression tests for voice_router.synthesize_voice's failure contract.

Voice is on every video's critical path. Since the 2026-07-14 engine consolidation OmniVoice is the
ONLY engine: the router promises 'audio_out on success, or None on failure' — a raising engine must
degrade to None, never crash the render (native_composer relies on None for the no-voice case), and
no other engine may be invoked (no silent fallback).

Hermetic: the engine module is stubbed via import_module — no real TTS / models.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "voice_cloner"))

import voice_router as vr  # noqa: E402


def _mod(fn):
    class M:
        synthesize = staticmethod(fn)
    return M


class SynthesizeContractTests(unittest.TestCase):
    def setUp(self):
        self._imp = vr.import_module

    def tearDown(self):
        vr.import_module = self._imp

    def _wire(self, ov_fn):
        self.imported = []
        def imp(name):
            self.imported.append(name)
            if "omnivoice" in name:
                return _mod(ov_fn)
            raise AssertionError(f"unexpected engine import: {name}")
        vr.import_module = imp

    def test_omnivoice_success_returns_path(self):
        self._wire(lambda t, o: o)
        self.assertEqual(vr.synthesize_voice("hi", "out.mp3"), "out.mp3")

    def test_omnivoice_returns_none_passes_none_through(self):
        self._wire(lambda t, o: None)
        self.assertIsNone(vr.synthesize_voice("hi", "out.mp3"))

    def test_omnivoice_raises_degrades_to_none_not_crash(self):
        def boom(*a, **k): raise RuntimeError("model missing")
        self._wire(boom)
        self.assertIsNone(vr.synthesize_voice("hi", "out.mp3"))   # must not raise

    def test_no_other_engine_is_imported(self):
        self._wire(lambda t, o: o)
        vr.synthesize_voice("hi", "out.mp3")
        self.assertEqual(len(self.imported), 1)
        self.assertIn("omnivoice", self.imported[0])


if __name__ == "__main__":
    unittest.main()
