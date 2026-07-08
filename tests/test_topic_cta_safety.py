"""Regression test: the topic→video CTA safety net must neutralize an off-platform CTA that
survives rewrites — the single CTA must be 'follow SEOSONA'.

topic_to_script() replaces the CTA scene with the canonical clean CTA if it still carries an
off-platform domain, and drops the offending sentence from a mid-scene. Hermetic: script_writer
is stubbed; content_moderation.off_platform_domain is the real shared detector.
"""
import os
import sys
import types
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))


class _VR:
    def __init__(self):
        self.ok, self.errors, self.unsourced = True, [], False


class _Script:
    def __init__(self, scenes):
        self.scenes = scenes


# Build a fake script_writer, but DO NOT install it at import time. A module-level
# `sys.modules["script_writer"] = _fake_sw` pollutes EVERY other test module during pytest collection —
# they'd import this fake instead of the real script_writer (e.g. test_traceability_pct got a fake with no
# _traceability/_pct_match/KeyFacts). topic_to_video import_module()s script_writer at CALL time, so the
# fake only needs to exist while a test method runs → install it in setUp, restore in tearDown.
_fake_sw = types.ModuleType("script_writer")
_fake_sw.verify = lambda script, kf, unsourced=False: _VR()

import topic_to_video as tv  # noqa: E402


def _wire(scenes):
    # real call is generate_script(topic, topic=topic, n_scenes=..) → first param must NOT be named `topic`
    _fake_sw.generate_script = lambda _inp, **k: (_Script(scenes), _VR(), {})


class CtaSafetyNetTests(unittest.TestCase):
    def setUp(self):
        # install the fake only for the duration of each test, then restore — so we never pollute
        # sys.modules for other test modules that import the REAL script_writer.
        self._orig_sw = sys.modules.get("script_writer")
        sys.modules["script_writer"] = _fake_sw

    def tearDown(self):
        if self._orig_sw is not None:
            sys.modules["script_writer"] = self._orig_sw
        else:
            sys.modules.pop("script_writer", None)

    def test_off_platform_cta_scene_replaced_with_clean(self):
        scenes = [{"text_vi": "Nội dung bình thường về SEO."},
                  {"text_vi": "Truy cập fiverr.com ngay hôm nay để thuê."}]   # last = CTA w/ off-platform
        _wire(scenes)
        text, vr = tv.topic_to_script("seo")
        self.assertEqual(scenes[-1]["text_vi"], tv._CLEAN_CTA)     # neutralized
        self.assertNotIn("fiverr.com", text)

    def test_clean_cta_left_alone(self):
        scenes = [{"text_vi": "Mẹo SEO hữu ích."},
                  {"text_vi": "Theo dõi SEOSONA để xem thêm nội dung."}]
        _wire(scenes)
        tv.topic_to_script("seo")
        self.assertNotEqual(scenes[-1]["text_vi"], "")            # unchanged, still a clean CTA
        self.assertIn("SEOSONA", scenes[-1]["text_vi"])

    def test_empty_script_returns_empty(self):
        _fake_sw.generate_script = lambda _inp, **k: (_Script([]), _VR(), {})
        text, _ = tv.topic_to_script("seo")
        self.assertEqual(text, "")


if __name__ == "__main__":
    unittest.main()
