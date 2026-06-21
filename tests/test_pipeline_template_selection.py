import os
import sys
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

from pipeline_manager import _select_news_template  # noqa: E402


class PipelineTemplateSelectionTests(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("SEOSONA_NEWS_TEMPLATE", None)

    def test_default_template_selection_uses_spatial_for_short_news(self):
        self.assertEqual(_select_news_template(4), "news_spatial_hyperframes")
        self.assertEqual(_select_news_template(5), "news_loop_path_hyperframes")

    def test_env_override_allows_verified_template(self):
        os.environ["SEOSONA_NEWS_TEMPLATE"] = "mock_verified_template"
        self.assertEqual(_select_news_template(4), "mock_verified_template")

    def test_env_override_rejects_path_injection(self):
        os.environ["SEOSONA_NEWS_TEMPLATE"] = "../bad"
        with self.assertRaises(ValueError):
            _select_news_template(4)


if __name__ == "__main__":
    unittest.main()
