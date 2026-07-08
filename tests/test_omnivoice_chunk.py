"""Regression tests for omnivoice_engine chunking + multi-chunk failure handling.

_chunk_text splits long scripts safely. synthesize() must NOT ship partial audio: if any chunk
(after the adaptive-shrink retry) can't be synthesized, it must fail over to None — the old code
checked the GLOBAL wav list, so a failed MIDDLE chunk was silently dropped → a missing narration
section desynced from the captions.

Hermetic: _synth_one / _concat_wavs / _post_process / available are stubbed (no real TTS).
"""
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "voice_cloner"))

import omnivoice_engine as oe  # noqa: E402

_SENT = "Đây là một câu khá dài dùng để kiểm tra việc chia nhỏ kịch bản dài thành nhiều đoạn an toàn cho engine. "


class ChunkTextTests(unittest.TestCase):
    def test_empty_returns_no_chunks(self):
        self.assertEqual(oe._chunk_text(""), [])
        self.assertEqual(oe._chunk_text("   "), [])

    def test_short_is_single_chunk(self):
        self.assertEqual(oe._chunk_text("Xin chào SEOSONA."), ["Xin chào SEOSONA."])

    def test_long_splits_and_respects_limit(self):
        chunks = oe._chunk_text(_SENT * 40, max_chars=1000)
        self.assertGreater(len(chunks), 1)
        # every chunk (whole sentences) stays within a small tolerance of the limit
        self.assertTrue(all(len(c) <= 1000 for c in chunks))

    def test_whitespace_normalized(self):
        self.assertEqual(oe._chunk_text("a\n\n  b\t c"), ["a b c"])


class SynthesizeMultiChunkTests(unittest.TestCase):
    def setUp(self):
        self._saved = (oe.available, oe._DEFAULT_REF, oe._ref_text, oe._concat_wavs, oe._post_process, oe._synth_one)
        ref = os.path.join(tempfile.mkdtemp(), "ref.wav"); open(ref, "wb").write(b"x")
        oe.available = lambda: True
        oe._DEFAULT_REF = ref
        oe._ref_text = lambda r: "ref text"
        oe._concat_wavs = lambda wavs, out: (open(out, "wb").write(b"y"), out)[1]
        oe._post_process = lambda raw, out: out
        self.text = _SENT * 40   # forces multiple chunks

    def tearDown(self):
        (oe.available, oe._DEFAULT_REF, oe._ref_text, oe._concat_wavs, oe._post_process, oe._synth_one) = self._saved

    def test_all_chunks_succeed_returns_path(self):
        oe._synth_one = lambda t, r, rt, l, o: (open(o, "wb").write(b"z"), o)[1]
        out = os.path.join(tempfile.mkdtemp(), "a.mp3")
        self.assertIsNotNone(oe.synthesize(self.text, out))

    def test_temp_files_are_per_call_isolated(self):
        # parallel renders share the system temp — each synthesis must use its OWN dir, not fixed names
        seen = []
        oe._synth_one = lambda t, r, rt, l, o: (seen.append(o), open(o, "wb").write(b"z"), o)[2]
        oe.synthesize("Xin chào một.", os.path.join(tempfile.mkdtemp(), "a.mp3"))
        oe.synthesize("Xin chào hai.", os.path.join(tempfile.mkdtemp(), "b.mp3"))
        self.assertNotEqual(os.path.dirname(seen[0]), os.path.dirname(seen[1]))
        self.assertTrue(all("omnivoice_raw.wav" not in p for p in seen))   # not the old fixed name

    def test_one_failing_chunk_returns_none_no_partial(self):
        chunks = oe._chunk_text(self.text)
        fail_key = chunks[1][:40]                 # fail everything derived from the 2nd chunk

        def synth(t, r, rt, l, o):
            if fail_key in t:
                return None                        # this chunk + all its shrink sub-pieces fail
            open(o, "wb").write(b"z"); return o
        oe._synth_one = synth
        out = os.path.join(tempfile.mkdtemp(), "b.mp3")
        self.assertIsNone(oe.synthesize(self.text, out))   # NOT a partial-audio path


if __name__ == "__main__":
    unittest.main()
