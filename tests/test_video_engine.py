"""Tests for the unified native_composer render path.

Covers the pure (no render) surface of the new engine: input detection, the
deterministic text->scenes planner, template integrity, and GitHub classify.
Rendering itself (node/hyperframes + ffmpeg + voice) is an integration concern
and is not exercised here.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import video_engine as ve  # noqa: E402
import native_composer as nc  # noqa: E402
import make_video as mv  # noqa: E402

KNOWN_COMPONENTS = {
    "bignum", "repo", "compare", "terminal", "steps", "badges", "stats",
    "quote", "tip", "feature", "chart", "mockup", "cta", "gittree", None,
}


class InputDetectionTests(unittest.TestCase):
    def test_github_url_routes_to_create(self):
        self.assertEqual(ve.detect_input_type("https://github.com/owner/name")[0], "create")

    def test_bare_owner_name_is_github(self):
        self.assertTrue(ve._is_github("owner/name"))
        self.assertFalse(ve._is_github("https://github.com/"))  # no repo path
        self.assertFalse(ve._is_github("just some text"))

    def test_youtube_routes_to_download(self):
        self.assertEqual(ve.detect_input_type("https://youtu.be/abc123")[0], "download")

    def test_plain_text_routes_to_create(self):
        self.assertEqual(ve.detect_input_type("Một kịch bản tiếng Việt")[0], "create")

    def test_generic_web_url_routes_to_scrape(self):
        self.assertEqual(ve.detect_input_type("https://example.com/article")[0], "scrape")


class ScenePlannerTests(unittest.TestCase):
    SCRIPT = ("SEOSONA tự động sản xuất video tiếng Việt bằng AI. "
              "Công cụ này rất mạnh và dễ dùng. Nó đã đạt 38000 sao trên GitHub. "
              "Cộng đồng đang phát triển nhanh chóng. Hãy thử ngay hôm nay.")

    def test_plan_returns_aligned_segments_and_scenes(self):
        segments, scenes = ve.plan_scenes(self.SCRIPT)
        self.assertEqual(len(segments), len(scenes))
        self.assertGreaterEqual(len(scenes), 4)

    def test_first_scene_is_hero_last_is_cta(self):
        _, scenes = ve.plan_scenes(self.SCRIPT)
        self.assertTrue(scenes[0]["hero"])
        self.assertEqual(scenes[-1]["comp"][0], "cta")

    def test_all_planned_components_are_known(self):
        _, scenes = ve.plan_scenes(self.SCRIPT)
        for sc in scenes:
            kind = sc["comp"][0] if sc.get("comp") else None
            self.assertIn(kind, KNOWN_COMPONENTS)

    def test_every_scene_has_a_segment_and_heading(self):
        segments, scenes = ve.plan_scenes(self.SCRIPT)
        for seg, sc in zip(segments, scenes):
            self.assertTrue(seg.strip())
            self.assertTrue(sc["h1"])

    def test_empty_input_does_not_crash(self):
        segments, scenes = ve.plan_scenes("")
        self.assertEqual(len(segments), len(scenes))
        self.assertGreaterEqual(len(scenes), 1)


class TemplateLibraryTests(unittest.TestCase):
    def test_all_templates_load_with_known_components(self):
        names = nc.list_templates()
        self.assertGreaterEqual(len(names), 1)
        for name in names:
            tpl = nc.load_template(name)
            self.assertIn("scenes", tpl)
            self.assertEqual(tpl.get("name"), name)
            for sc in tpl["scenes"]:
                self.assertIn(sc.get("component"), KNOWN_COMPONENTS)
                self.assertIn(sc.get("accent"), {"blue", "green", "orange"})

    def test_classify_returns_a_real_template(self):
        names = set(nc.list_templates())
        for gh in [
            {"name": "awesome-python", "desc": "curated list", "topics": []},
            {"name": "mytool", "desc": "a command line tool", "topics": ["cli"]},
            {"name": "gitviz", "desc": "visualize git", "topics": ["tutorial"]},
            {"name": "lib", "desc": "a library", "topics": []},
        ]:
            template, theme, _reason = mv.classify(gh)
            self.assertIn(template, names)
            self.assertEqual(theme, "light")  # brand law: light only


class BrandProfileTests(unittest.TestCase):
    def test_profiles_load_distinct_logo_and_voice(self):
        seo = nc._load_profile("seosona")
        cqa = nc._load_profile("cqa")
        self.assertEqual(seo["logo"], "Seosona_Logo.png")
        self.assertNotEqual(seo["logo"], cqa["logo"])  # cqa must not render as seosona
        self.assertIn("reference_audio", seo.get("voice", {}))

    def test_unknown_brand_falls_back_to_seosona_shape(self):
        prof = nc._load_profile("does-not-exist")
        self.assertEqual(prof["logo"], "Seosona_Logo.png")

    def test_footers_are_brand_specific(self):
        self.assertIn("seosona", nc.FOOTERS)
        self.assertIn("cqa", nc.FOOTERS)
        self.assertNotEqual(nc.FOOTERS["seosona"], nc.FOOTERS["cqa"])

    def test_make_video_accepts_brand_kwarg(self):
        import inspect
        sig = inspect.signature(nc.make_video)
        self.assertIn("brand", sig.parameters)


class BoundaryTests(unittest.TestCase):
    def test_carousel_mode_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "image workflows"):
            ve.run_pipeline("x", mode="carousel", project_name="VE_BOUNDARY_TEST")


if __name__ == "__main__":
    unittest.main()
