"""Regression test: SRT timestamps must always be valid (ms 000-999, sec 00-59), even when a cue
boundary lands on an X.9995+ fraction that rounds up.

Bug: _srt_ts computed ms = round((sec-int(sec))*1000) independently, so 5.9996 → 1000 → "00:00:05,1000"
(invalid — ms overflowed instead of carrying to the next second). Rounding to whole ms first, then
decomposing with divmod, can never overflow. (course_video.ts had the same class via `{sec:06.3f}`
rounding 59.9996 → "60.000".)
"""
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import native_composer as nc  # noqa: E402

_SRT = re.compile(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})$")


class SrtTimestampTests(unittest.TestCase):
    def test_fractional_carry_does_not_overflow_ms(self):
        self.assertEqual(nc._srt_ts(5.9996), "00:00:06,000")     # was "00:00:05,1000"
        self.assertEqual(nc._srt_ts(59.9999), "00:01:00,000")    # was "00:00:59,1000"
        self.assertEqual(nc._srt_ts(3599.9996), "01:00:00,000")  # rolls hour correctly

    def test_ordinary_values(self):
        self.assertEqual(nc._srt_ts(0), "00:00:00,000")
        self.assertEqual(nc._srt_ts(3661.5), "01:01:01,500")
        self.assertEqual(nc._srt_ts(-1), "00:00:00,000")         # clamped at 0

    def test_always_valid_srt_shape(self):
        # sweep values whose fraction rounds up, plus a fine grid — every output must be a valid timestamp
        vals = [i * 0.1 for i in range(0, 6005)] + [k + 0.9996 for k in range(0, 120)]
        for v in vals:
            m = _SRT.match(nc._srt_ts(v))
            self.assertIsNotNone(m, f"malformed for {v}: {nc._srt_ts(v)}")
            hh, mm, ss, ms = (int(x) for x in m.groups())
            self.assertLess(ss, 60)
            self.assertLess(mm, 60)
            self.assertLess(ms, 1000)


if __name__ == "__main__":
    unittest.main()
