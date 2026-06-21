import importlib
import os
import sys
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

llm_engine = importlib.import_module("4_BRAIN.llm_engine")
social_writer = importlib.import_module("1_AGENTS.social_media_agent.writer")


class SocialPostWorkflowTests(unittest.TestCase):
    def test_pas_router_wins_when_social_content_mentions_carousel(self):
        result = llm_engine._smart_offline_router(
            "You are SEOSONA Social Media Strategist. Apply PAS framework.",
            "Analyze this data and write a PAS framework Social Media Post.\n\n"
            "Raw Data:\nCarousel automation helps SEOSONA publish faster.",
            "offline",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("caption", result)

    def test_facebook_caption_recovers_from_slide_json_shape(self):
        agent = social_writer.SocialMediaAgent()

        original = social_writer.generate_json_from_prompt
        social_writer.generate_json_from_prompt = lambda **_: [
            {"type": "cover", "title": "Carousel automation"},
            {"type": "content", "heading": "Publish faster"},
        ]
        try:
            caption = agent.write_facebook_caption(
                "Carousel automation helps SEOSONA publish faster with consistent branding."
            )
        finally:
            social_writer.generate_json_from_prompt = original

        self.assertIsInstance(caption, str)
        self.assertGreater(len(caption), 50)
        self.assertIn("#SEOSONA", caption)


if __name__ == "__main__":
    unittest.main()
