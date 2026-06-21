import json
import os
import sys
import tempfile
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

from video_template_factory import export_template_from_project, list_templates  # noqa: E402


class VideoTemplateFactoryTests(unittest.TestCase):
    def test_export_template_from_hyperframes_render_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = os.path.join(tmp, "NEWS_SAMPLE")
            render_dir = os.path.join(project_dir, ".temp", "hf_render")
            os.makedirs(render_dir)
            os.makedirs(os.path.join(project_dir, "SRT"))
            os.makedirs(os.path.join(project_dir, "Thumbnail"))

            with open(os.path.join(render_dir, "index.html"), "w", encoding="utf-8") as handle:
                handle.write("<html><body><div data-composition-id=\"news\">Hello</div></body></html>")
            with open(os.path.join(render_dir, "production_manifest.json"), "w", encoding="utf-8") as handle:
                json.dump({"template": "news_spatial_hyperframes", "duration": 42.0}, handle)
            with open(os.path.join(project_dir, "SRT", "NEWS_SAMPLE.srt"), "w", encoding="utf-8") as handle:
                handle.write("1\n00:00:00,000 --> 00:00:01,000\nXin chao\n")
            with open(os.path.join(project_dir, "Thumbnail", "NEWS_SAMPLE_Thumbnail.png"), "wb") as handle:
                handle.write(b"png")

            registry_root = os.path.join(tmp, "templates")
            manifest = export_template_from_project(
                project_dir,
                "Obscura News Template",
                out_root=registry_root,
                copy_assets=False,
            )

            template_dir = os.path.join(registry_root, "obscura-news-template")
            self.assertTrue(os.path.exists(os.path.join(template_dir, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(template_dir, "template.json")))
            self.assertEqual(manifest["id"], "obscura-news-template")
            self.assertEqual(manifest["source"]["project_name"], "NEWS_SAMPLE")
            self.assertEqual(manifest["render"]["engine"], "hyperframes")
            self.assertIn("index.html", manifest["files"])
            self.assertIn("production_manifest.json", manifest["files"])
            self.assertEqual(list_templates(registry_root)[0]["id"], "obscura-news-template")


if __name__ == "__main__":
    unittest.main()
