"""Regression test: the number-traceability gate must treat PERCENTAGES tightly.

Bug: _traceability/_strip_fabricated built kf_nums = [n["value"] for n in kf.numbers] — dropping the
`pct` flag — and matched with _num_match, whose max(999, …) tolerance is meaningless for 0–100 pct
values. So a fabricated "50%" traced to a real "30%" (or even to a raw count of 50) and shipped —
defeating "no fabricated numbers" for the MOST common marketing fabrication (percentages).

Fix: a spoken percentage traces ONLY to a source percentage, within a tight ~2-point/3% tolerance.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import script_writer as sw  # noqa: E402


def _scene(text):
    return sw.Script(scenes=[{"idx": 0, "text_vi": text, "h1": "a", "h2": "b"}])


class PctMatchTests(unittest.TestCase):
    def test_helper_tolerance(self):
        self.assertTrue(sw._pct_match(80, 80))       # exact
        self.assertTrue(sw._pct_match(80, 78))       # honest rounding (2 points)
        self.assertFalse(sw._pct_match(50, 30))      # fabrication — different fact
        self.assertFalse(sw._pct_match(50, 80))


class TraceabilityPctTests(unittest.TestCase):
    def test_fabricated_pct_is_caught(self):
        kf = sw.KeyFacts(numbers=[{"value": 30, "raw": "30%", "pct": True}])
        errs, _ = sw._traceability(_scene("Doanh thu tăng tới 50% mỗi tháng."), kf)
        self.assertTrue(any("50%" in e for e in errs), errs)   # was silently traced to 30% before

    def test_matching_pct_passes(self):
        kf = sw.KeyFacts(numbers=[{"value": 80, "raw": "80%", "pct": True}])
        errs, _ = sw._traceability(_scene("Có tới 80% doanh nghiệp áp dụng."), kf)
        self.assertFalse(errs, errs)

    def test_pct_cannot_trace_to_raw_count(self):
        # a source count of 50 (NOT a percentage) must not legitimise a spoken "50%"
        kf = sw.KeyFacts(numbers=[{"value": 50, "raw": "50 sản phẩm", "pct": False}])
        errs, _ = sw._traceability(_scene("Hiệu quả tăng 50% rõ rệt."), kf)
        self.assertTrue(any("50%" in e for e in errs), errs)

    def test_plain_number_unaffected(self):
        kf = sw.KeyFacts(numbers=[{"value": 119787, "raw": "119,787", "pct": False}])
        errs, _ = sw._traceability(_scene("Dự án đã đạt hơn 119 nghìn sao."), kf)
        self.assertFalse(errs, errs)                            # 119,000 ≈ 119,787 still traces


class StripFabricatedPctTests(unittest.TestCase):
    def test_fabricated_pct_is_stripped_consistently(self):
        kf = sw.KeyFacts(numbers=[{"value": 30, "raw": "30%", "pct": True}])
        script = _scene("Doanh thu tăng 50% trong năm nay.")
        n = sw._strip_fabricated(script, kf)
        self.assertEqual(n, 1)
        out = script.scenes[0]["text_vi"]
        self.assertNotIn("50%", out)
        self.assertIn("một phần", out)                         # pct → grounded generic


if __name__ == "__main__":
    unittest.main()
