import os
import sys
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

from news_video_standards import (  # noqa: E402
    align_tts_boundaries_to_display_words,
    prepare_tts_script,
    validate_vietnamese_news_script,
)


class NewsVideoStandardsTests(unittest.TestCase):
    def test_prepare_tts_script_preserves_display_text_and_uses_pronunciation_text(self):
        plan = prepare_tts_script("AI Search từ GitHub đang ảnh hưởng SEO.")

        self.assertEqual(plan.display_text, "AI Search từ GitHub đang ảnh hưởng SEO.")
        self.assertIn("ây ai", plan.tts_text)
        self.assertIn("sớt", plan.tts_text)
        self.assertIn("gít hắp", plan.tts_text)
        self.assertIn("séo", plan.tts_text)
        self.assertIn("AI", plan.display_words)
        self.assertIn("GitHub", plan.display_words)

    def test_align_tts_boundaries_groups_pronounced_words_back_to_display_words(self):
        plan = prepare_tts_script("AI Search đang tăng.")
        boundaries = [
            {"word": "ây", "start": 0.00, "duration": 0.10},
            {"word": "ai", "start": 0.10, "duration": 0.12},
            {"word": "sớt", "start": 0.25, "duration": 0.20},
            {"word": "đang", "start": 0.48, "duration": 0.18},
            {"word": "tăng", "start": 0.70, "duration": 0.20},
        ]

        aligned = align_tts_boundaries_to_display_words(plan, boundaries, duration=1.0)

        self.assertEqual([item["word"] for item in aligned], ["AI", "Search", "đang", "tăng"])
        self.assertAlmostEqual(aligned[0]["start"], 0.00)
        self.assertAlmostEqual(aligned[0]["end"], 0.22)
        self.assertAlmostEqual(aligned[1]["start"], 0.25)
        self.assertAlmostEqual(aligned[1]["end"], 0.45)

    def test_validate_vietnamese_news_script_allows_known_technical_terms_only(self):
        valid = validate_vietnamese_news_script("AI Search và GitHub đang tác động đến SEO Việt Nam.")
        invalid = validate_vietnamese_news_script("AI Search is changing SEO for every marketer.")

        self.assertTrue(valid.is_valid, valid.disallowed_terms)
        self.assertFalse(invalid.is_valid)
        self.assertIn("is", invalid.disallowed_terms)
        self.assertIn("changing", invalid.disallowed_terms)


if __name__ == "__main__":
    unittest.main()
