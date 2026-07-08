"""Regression guard: carousel render must use a UNIQUE temp HTML file, not a shared fixed name.

A fixed 'temp_carousel.html' in output_dir gets clobbered when two carousel renders hit the same
directory at once (the factory runs renders as parallel subprocesses) → corrupt slides. The render
now uses tempfile.mkstemp. A full render needs Playwright, so this guards the source contract.
"""
import os
import re
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEN = os.path.join(PROJECT_ROOT, "2_SKILLS", "carousel_maker", "carousel_generator.py")


class CarouselTempFileTests(unittest.TestCase):
    def setUp(self):
        with open(GEN, encoding="utf-8") as f:
            self.src = f.read()

    def test_uses_unique_temp_not_fixed_name(self):
        self.assertIn("mkstemp", self.src)
        # the old shared fixed-name join must be gone
        self.assertNotRegex(self.src, r'os\.path\.join\(\s*output_dir\s*,\s*["\']temp_carousel\.html["\']')

    def test_temp_still_cleaned_up(self):
        # the finally-block cleanup must remain
        self.assertIn("os.remove(temp_html_path)", self.src)


if __name__ == "__main__":
    unittest.main()
