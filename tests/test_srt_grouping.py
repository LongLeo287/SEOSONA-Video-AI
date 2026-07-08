"""Regression tests for whisper_engine.group_words_to_segments (word timings → caption segments).

Guards the Netflix-style segmentation: break at punctuation, cap by max words and max duration,
and carry each segment's start/end from its first/last word.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "srt_maker"))

import whisper_engine as we  # noqa: E402


def _w(word, s, e):
    return {"word": word, "start": s, "end": e}


class GroupWordsTests(unittest.TestCase):
    def test_punctuation_breaks_segment(self):
        segs = we.group_words_to_segments(
            [_w("Xin", 0, 0.3), _w("chào.", 0.3, 0.6), _w("Tôi", 0.6, 0.9), _w("là", 0.9, 1.1)])
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0]["text"], "Xin chào.")

    def test_max_words_cap(self):
        segs = we.group_words_to_segments(
            [_w(f"w{i}", i * 0.1, i * 0.1 + 0.1) for i in range(10)], max_words=7)
        self.assertTrue(all(len(s["words"]) <= 7 for s in segs))

    def test_max_duration_break(self):
        segs = we.group_words_to_segments(
            [_w("a", 0, 0.1), _w("b", 0.1, 3.0), _w("c", 3.0, 3.2)], max_duration=2.5)
        # 'b' pushes the first segment past 2.5s → it flushes before 'c'
        self.assertGreaterEqual(len(segs), 2)

    def test_segment_start_end_from_first_last_word(self):
        segs = we.group_words_to_segments([_w("Xin", 0.0, 0.3), _w("chào.", 0.3, 0.6)])
        self.assertEqual((segs[0]["start"], segs[0]["end"]), (0.0, 0.6))

    def test_empty_input(self):
        self.assertEqual(we.group_words_to_segments([]), [])

    def test_decimal_does_not_break_mid_phrase(self):
        # a '.' INSIDE a word (decimal) must not split the caption — break only on a trailing sentence mark
        segs = we.group_words_to_segments([_w("tăng", 0, .3), _w("3.5", .3, .6), _w("lần", .6, .9)])
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["text"], "tăng 3.5 lần")

    def test_thousands_separator_does_not_break(self):
        # VN thousands separator '.' ("1.000.000") must not fragment the phrase
        segs = we.group_words_to_segments(
            [_w("Doanh", 0, .3), _w("thu", .3, .6), _w("1.000.000", .6, .9), _w("đồng", .9, 1.2)])
        self.assertEqual(len(segs), 1)

    def test_trailing_period_still_breaks(self):
        segs = we.group_words_to_segments([_w("Giá", 0, .3), _w("5.", .3, .6), _w("Xong", .6, .9)])
        self.assertEqual(len(segs), 2)                 # '5.' ends with '.' → real sentence break


if __name__ == "__main__":
    unittest.main()
