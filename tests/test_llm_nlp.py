"""Regression tests for llm_engine's offline NLP primitives (used by every offline generator).

_classify_intent mis-scored the topic via SUBSTRING matches ('top'∈laptop, 'api'∈therapist,
'app'∈apply, 'cost'∈costume) → the wrong hook angle on offline content. It now matches whole words.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import llm_engine as le  # noqa: E402


class ClassifyIntentTests(unittest.TestCase):
    def test_substring_collisions_no_longer_misclassify(self):
        # each of these embeds a topic keyword inside a common word — must NOT trigger that topic
        self.assertEqual(le._classify_intent("Đánh giá laptop mỏng nhẹ 2026"), "GENERAL")   # top∈laptop
        self.assertEqual(le._classify_intent("Cách apply xin việc hiệu quả"), "GENERAL")     # app∈apply
        self.assertEqual(le._classify_intent("Bộ costume Halloween đẹp"), "GENERAL")         # cost∈costume
        self.assertEqual(le._classify_intent("Người therapist giỏi ở Hà Nội"), "GENERAL")    # api∈therapist

    def test_genuine_topics_classify(self):
        self.assertEqual(le._classify_intent("Chiến lược SEO từ khóa cho website"), "SEO")
        self.assertEqual(le._classify_intent("Cách viết content nội dung hay"), "CONTENT")
        self.assertEqual(le._classify_intent("AI agent với LLM và RAG"), "AI_AGENT")
        self.assertEqual(le._classify_intent("Chiến dịch marketing viral TikTok"), "MARKETING")
        self.assertEqual(le._classify_intent("Top 10 công cụ SEO"), "SEO")   # 'top' as a whole word still matches

    def test_no_keyword_is_general(self):
        self.assertEqual(le._classify_intent("Hôm nay trời đẹp và mát mẻ"), "GENERAL")


class ExtractNumbersTests(unittest.TestCase):
    def test_finds_percentages_and_units(self):
        nums = le._extract_numbers("Tăng 47% trong 3 tháng, tiết kiệm 10 giờ")
        joined = " ".join(nums)
        self.assertIn("47", joined)
        self.assertIn("3", joined)

    def test_no_numbers_returns_empty(self):
        self.assertEqual(le._extract_numbers("không có số nào ở đây"), [])


if __name__ == "__main__":
    unittest.main()
