"""Regression test: the OFFLINE script generator (the common quota-exhaustion path) must not
fabricate a specific quantity it has no data for.

It previously asserted 'đã nhận được hàng nghìn lượt đánh giá tích cực' ('received thousands of
positive reviews') for ANY GitHub project, prefixed with 'Theo dữ liệu mới nhất' — a fabricated
count that would ship in offline-generated videos.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import llm_engine as le  # noqa: E402


class OfflineNoFabricationTests(unittest.TestCase):
    def _narration(self, prompt):
        r = le._generate_script_offline(prompt)
        self.assertIsInstance(r, dict)
        return r["narrator_text"]

    def test_no_fabricated_review_count(self):
        for prompt in ("The best open source tool for AI agents and automation with modular architecture.",
                       "A powerful framework for building and shipping software faster with great performance."):
            narr = self._narration(prompt)
            self.assertNotIn("hàng nghìn lượt đánh giá", narr)   # fabricated count
            self.assertNotIn("Theo dữ liệu mới nhất", narr)      # fake "per the latest data" backing

    def test_still_produces_a_real_script(self):
        r = le._generate_script_offline("The best open source AI tool with modular architecture and integrations.")
        self.assertGreaterEqual(len(r["narrator_text"].split()), 80)   # substantial narration
        self.assertGreaterEqual(len(r["scenes"]), 6)

    def test_edge_inputs_do_not_crash(self):
        for prompt in ("", "   ", "SEO", "2026 100 50"):
            self.assertIsInstance(le._generate_script_offline(prompt), dict)


class OfflineCarouselTests(unittest.TestCase):
    def test_fallback_stats_are_not_fabricated_metrics(self):
        import json
        blob = json.dumps(le._generate_carousel_offline(
            "Cách tối ưu quy trình làm việc với công cụ tự động hóa."), ensure_ascii=False)
        # no invented performance numbers / timeframe promises for an unknown topic
        self.assertNotIn("60%", blob)
        self.assertNotIn("3x", blob)
        self.assertNotIn("30 ngày", blob)

    def test_still_produces_slides(self):
        r = le._generate_carousel_offline("Tối ưu SEO cho website doanh nghiệp.")
        self.assertIsInstance(r, list)
        self.assertGreaterEqual(len(r), 3)


if __name__ == "__main__":
    unittest.main()
