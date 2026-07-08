"""Regression tests for asr_router word collection + engine chaining.

whisper/faster-whisper can emit a None timestamp for an unaligned word. _collect_fw must skip
just THAT word — a single bad timestamp must not raise and discard the whole transcription
(which would fall back needlessly or yield empty captions).
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "srt_maker"))

import asr_router as ar  # noqa: E402


class _W:
    def __init__(self, word, start, end):
        self.word, self.start, self.end = word, start, end


class _Seg:
    def __init__(self, words):
        self.words = words


class CollectFwTests(unittest.TestCase):
    def test_skips_word_with_none_timestamp(self):
        segs = [_Seg([_W("Xin", 0.0, 0.5), _W("chào", None, 1.0), _W("SEOSONA", 1.0, 1.8)])]
        res = ar._collect_fw(segs)
        self.assertEqual([w["word"] for w in res], ["Xin", "SEOSONA"])

    def test_all_bad_returns_none(self):
        self.assertIsNone(ar._collect_fw([_Seg([_W("a", None, None)])]))

    def test_none_words_guarded(self):
        self.assertIsNone(ar._collect_fw([_Seg(None)]))

    def test_blank_word_skipped(self):
        res = ar._collect_fw([_Seg([_W("  ", 0.0, 0.5), _W("ok", 0.5, 1.0)])])
        self.assertEqual([w["word"] for w in res], ["ok"])


class TranscribeWordsTests(unittest.TestCase):
    def test_missing_audio_returns_empty(self):
        self.assertEqual(ar.transcribe_words("/no/such/audio.wav"), [])
        self.assertEqual(ar.transcribe_words(""), [])


if __name__ == "__main__":
    unittest.main()
