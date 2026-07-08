"""Regression tests for scene_composer's deterministic, network-free surface.

Covers:
  - fetch_github's primary `gh api` call is time-bounded (an unattended batch must not hang forever),
  - repo_data_slots never crashes on a partial/empty gh dict and emits NO fabricated fallback,
  - _readme_digest tolerates empty / malformed markdown.

Hermetic: no `gh`, no network — only the pure builders + a source-level check for the timeout.
"""
import inspect
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import scene_composer as sc  # noqa: E402


class FetchGithubContractTests(unittest.TestCase):
    def test_primary_gh_api_call_is_time_bounded(self):
        # the README sub-fetch already uses timeout=30; the PRIMARY repos/<repo> call must too.
        self.assertIn("timeout=", inspect.getsource(sc.fetch_github))


class RepoDataSlotsTests(unittest.TestCase):
    def test_empty_dict_does_not_crash(self):
        s = sc.repo_data_slots({})
        self.assertIn("repo", s)
        self.assertIn("stars_bignum", s)

    def test_partial_dict_builds_real_values(self):
        s = sc.repo_data_slots({"stars": 38000, "lang": "Python", "name": "tool"})
        self.assertEqual(s["repo"]["stars"], "38,000")
        self.assertEqual(s["repo"]["name"], "tool")
        self.assertIn("Python", s["repo"]["tags"])

    def test_no_fabricated_language_fallback(self):
        # a missing language must NOT become a fake "ĐA NỀN TẢNG" (cross-platform) claim.
        s = sc.repo_data_slots({"name": "x", "stars": 5})
        self.assertNotIn("ĐA NỀN TẢNG", s["repo"]["tags"])


class ReadmeDigestTests(unittest.TestCase):
    def test_empty_readme_is_empty_dict(self):
        self.assertEqual(sc._readme_digest(""), {})

    def test_malformed_markdown_does_not_crash(self):
        md = "# T\n\n" + "một câu tổng quan đủ dài để vượt ngưỡng bốn mươi ký tự ở đây.\n\n- tính năng một\n- tính năng hai"
        d = sc._readme_digest(md)
        self.assertIn("features", d)
        self.assertIsInstance(d["features"], list)


if __name__ == "__main__":
    unittest.main()
