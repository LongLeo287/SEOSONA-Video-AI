import json
import os
import sys
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

from video_engine import run_pipeline  # noqa: E402


class WorkflowBoundaryTests(unittest.TestCase):
    def test_package_exposes_canonical_workflows(self):
        package_path = os.path.join(PROJECT_ROOT, "package.json")
        with open(package_path, "r", encoding="utf-8") as f:
            package = json.load(f)

        scripts = package.get("scripts", {})
        for script_name in [
            "make:video",
            "post:image",
            "thumbnail:create",
            "video:news",
            "video:course",
        ]:
            self.assertIn(script_name, scripts)

    def test_video_pipeline_rejects_carousel_mode(self):
        with self.assertRaisesRegex(RuntimeError, "image workflows"):
            run_pipeline("Short carousel content", mode="carousel", project_name="BOUNDARY_TEST")


if __name__ == "__main__":
    unittest.main()
