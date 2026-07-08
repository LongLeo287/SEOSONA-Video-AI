# -*- coding: utf-8 -*-
"""Regression test: knowledge_graph._tokens / recall must not crash on a null field.

_tokens did `s.lower()` unguarded, so a note with title=None or text=None (a malformed/hand-edited JSON
row), or a None query, raised AttributeError — taking DOWN the whole recall (the 'check recall first
before re-deriving' workflow). str(s or "") makes one bad note a no-op instead of a crash.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import knowledge_graph as kg  # noqa: E402


class TokensRobustnessTests(unittest.TestCase):
    def test_tokens_on_none_and_nonstr(self):
        self.assertEqual(kg._tokens(None), [])
        self.assertEqual(kg._tokens(""), [])
        self.assertEqual(kg._tokens("SEO video"), ["seo", "video"])   # normal path unchanged


class RecallRobustnessTests(unittest.TestCase):
    def setUp(self):
        self._orig = kg._load_notes
        kg._load_notes = lambda: {"notes": [
            {"title": None, "text": None, "source": "bad"},               # malformed row → must not crash
            {"title": "SEO guide", "text": "all about seo", "source": "good", "kind": "lesson"},
        ]}

    def tearDown(self):
        kg._load_notes = self._orig

    def test_recall_skips_null_note_and_returns_valid(self):
        r = kg.recall("seo")
        self.assertEqual([x["title"] for x in r], ["SEO guide"])          # null note skipped, no crash

    def test_recall_empty_query(self):
        self.assertEqual(kg.recall(""), [])
        self.assertEqual(kg.recall(None), [])                             # None query no longer crashes


if __name__ == "__main__":
    unittest.main()
