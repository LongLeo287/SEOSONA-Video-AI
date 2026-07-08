"""Regression test: every outward-facing social caption must pass the content-safety review.

write_facebook_caption ran _safety_review, but write_multi_platform (facebook/linkedin/tiktok)
skipped it — so multi-platform captions could ship an off-platform CTA / unsafe claim with no
warning. Both paths must now run the gate.

Hermetic: generate_post is stubbed (no LLM/network); content_moderation is pure.
"""
import contextlib
import io
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (PROJECT_ROOT, os.path.join(PROJECT_ROOT, "4_BRAIN"),
          os.path.join(PROJECT_ROOT, "1_AGENTS", "social_media_agent")):
    sys.path.insert(0, p)

import writer as w  # noqa: E402

_AGENT = next(getattr(w, n) for n in dir(w)
              if isinstance(getattr(w, n), type) and hasattr(getattr(w, n), "write_multi_platform"))

UNSAFE = "Liên hệ fiverr.com để thuê dịch vụ ngay"   # off-platform CTA → a 'block' flag


def _agent():
    a = _AGENT.__new__(_AGENT)          # bypass __init__ (no LLM wiring)
    a.model_name = "stub"
    a.generate_post = lambda prompt: {"caption": UNSAFE}
    return a


class SocialSafetyGateTests(unittest.TestCase):
    def test_multi_platform_runs_safety_review_per_platform(self):
        a = _agent()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = a.write_multi_platform("x", platforms=["facebook", "linkedin", "tiktok"])
        out = buf.getvalue()
        self.assertEqual(len(res), 3)
        self.assertTrue(all(res.values()))                     # all captions returned
        self.assertEqual(out.count("CONTENT-SAFETY"), 3)       # gate fired once per platform

    def test_facebook_caption_still_gated(self):
        a = _agent()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cap = a.write_facebook_caption("x")
        self.assertTrue(cap)
        self.assertIn("CONTENT-SAFETY", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
