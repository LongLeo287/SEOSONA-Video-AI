# -*- coding: utf-8 -*-
"""Regression test: ASS karaoke timestamps (H:MM:SS.cc) must stay valid when a fraction rounds up.

Bug: _ts formatted `sec % 60` as `{s:05.2f}`, so 59.9996 → "60.00" → "0:00:60.00" (invalid — seconds
must be 00-59, must carry to the next minute; libass can drop/mis-time the caption). Rounding to whole
centiseconds first, then decomposing with divmod, can never overflow. Same class as SRT timestamps.
"""
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

import talking_head_edit as th  # noqa: E402

_ASS = re.compile(r"^(\d+):(\d{2}):(\d{2})\.(\d{2})$")


class AssTimestampTests(unittest.TestCase):
    def test_fractional_carry_does_not_overflow(self):
        self.assertEqual(th._ts(59.9996), "0:01:00.00")     # was "0:00:60.00"
        self.assertEqual(th._ts(5.9996), "0:00:06.00")
        self.assertEqual(th._ts(3599.9996), "1:00:00.00")

    def test_ordinary_values(self):
        self.assertEqual(th._ts(0), "0:00:00.00")
        self.assertEqual(th._ts(3661.5), "1:01:01.50")
        self.assertEqual(th._ts(-1), "0:00:00.00")

    def test_always_valid_ass_shape(self):
        vals = [i * 0.1 for i in range(0, 4005)] + [k + 0.9996 for k in range(0, 120)]
        for v in vals:
            m = _ASS.match(th._ts(v))
            self.assertIsNotNone(m, f"malformed for {v}: {th._ts(v)}")
            _h, mm, ss, cc = (int(x) for x in m.groups())
            self.assertLess(ss, 60)
            self.assertLess(mm, 60)
            self.assertLess(cc, 100)


if __name__ == "__main__":
    unittest.main()
