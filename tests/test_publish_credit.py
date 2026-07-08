"""Regression test: CC-BY BGM attribution must reach EVERY publish path.

native_composer writes `<video>.credits.txt` when a sourced (CC-BY) BGM track is used.
publish_dispatch.publish() is the single dispatch choke point and must append that credit
to the description so the licence obligation reaches the platform — for direct callers
(e.g. telegram_remote) as well as video_engine's publish step. Idempotent (no double-append).

Hermetic: stubs the route functions and uses temp files — no network, no credentials.
"""
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "1_AGENTS", "publisher_agent"))

import publish_dispatch as pd  # noqa: E402

CREDIT = 'Music: "Song" by Artist (CC BY 4.0) — https://example.org'


class PublishCreditTests(unittest.TestCase):
    def setUp(self):
        self.seen = {}
        self._saved_routes = pd._ROUTES

        def _stub(name):
            def f(product):
                self.seen[name] = product.get("description", "")
                return {"ok": True, "status": "uploaded"}
            return f
        pd._ROUTES = {k: _stub(k) for k in ("telegram", "google_drive")}

        self.dir = tempfile.mkdtemp()
        self.vid = os.path.join(self.dir, "out.mp4")
        with open(self.vid, "wb") as f:
            f.write(b"x")

    def tearDown(self):
        pd._ROUTES = self._saved_routes

    def _write_credit(self):
        with open(self.vid + ".credits.txt", "w", encoding="utf-8") as f:
            f.write(CREDIT + "\n")

    def test_direct_caller_without_description_gets_credit(self):
        # the telegram_remote bypass: only {video, title}. The CC-BY credit MUST still be published.
        self._write_credit()
        pd.publish({"video": self.vid, "title": "T"}, destinations=["telegram"])
        self.assertIn(CREDIT, self.seen["telegram"])

    def test_credit_is_not_double_appended(self):
        # video_engine's publish step already appends the credit; publish() must not add it twice.
        self._write_credit()
        pd.publish({"video": self.vid, "title": "T", "description": "Hello\n\n" + CREDIT},
                   destinations=["telegram"])
        self.assertEqual(self.seen["telegram"].count(CREDIT), 1)

    def test_no_credits_file_leaves_description_untouched(self):
        pd.publish({"video": self.vid, "title": "T", "description": "Just desc"},
                   destinations=["telegram"])
        self.assertEqual(self.seen["telegram"], "Just desc")


if __name__ == "__main__":
    unittest.main()
