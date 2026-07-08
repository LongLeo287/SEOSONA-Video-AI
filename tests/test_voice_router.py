"""Regression tests for voice_router.synthesize_voice's failure contract.

Voice is on every video's critical path. The router promises 'audio_out on success, or None
only if both fail' — so a RAISING backup (VieNeu model/GPU error) must degrade to None, never
crash the render (native_composer relies on None to handle the no-voice case).

Hermetic: the engine modules are stubbed via import_module — no real TTS / models.
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
        self._has = vr._has_vieneu

    def tearDown(self):
        vr.import_module = self._imp
        vr._has_vieneu = self._has

    def _wire(self, ov_fn, vn_fn, has_vieneu=True):
        vr.import_module = lambda name: _mod(ov_fn) if "omnivoice" in name else _mod(vn_fn)
        vr._has_vieneu = lambda: has_vieneu

    def test_omnivoice_success_returns_path(self):
        self._wire(lambda t, o: o, lambda *a, **k: None)
        self.assertEqual(vr.synthesize_voice("hi", "out.mp3"), "out.mp3")

    def test_backup_used_when_omnivoice_fails(self):
        def ov(t, o): raise RuntimeError("omnivoice down")
        self._wire(ov, lambda t, o, **k: o)
        self.assertEqual(vr.synthesize_voice("hi", "out.mp3"), "out.mp3")

    def test_both_fail_returns_none_not_crash(self):
        def boom(*a, **k): raise RuntimeError("model missing")
        self._wire(boom, boom)
        self.assertIsNone(vr.synthesize_voice("hi", "out.mp3"))   # must not raise

    def test_vieneu_not_installed_returns_none(self):
        def ov(t, o): raise RuntimeError("omnivoice down")
        self._wire(ov, lambda *a, **k: None, has_vieneu=False)
        self.assertIsNone(vr.synthesize_voice("hi", "out.mp3"))


if __name__ == "__main__":
    unittest.main()
