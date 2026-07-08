"""Regression tests for element_maker's safety surface.

Icon names come from element specs (LLM/picker output), so `_icon_svg` must not let a
`../`-bearing name escape ICON_DIR (path traversal). Text values must be HTML-escaped.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "2_SKILLS", "element_maker"))

try:
    import element_maker as em
    _ERR = None
except Exception as e:
    em, _ERR = None, e


@unittest.skipIf(em is None, f"element_maker import failed: {_ERR}")
class IconTraversalTests(unittest.TestCase):
    def test_traversal_name_does_not_read_outside_icon_dir(self):
        # a hostile icon name must basename-collapse and never leak an external file's content
        svg = em._icon_svg("../../../../Windows/System32/drivers/etc/hosts")
        self.assertNotIn("localhost", svg)
        self.assertNotIn("127.0.0.1", svg)

    def test_normal_icon_returns_string(self):
        self.assertIsInstance(em._icon_svg("circle-dot"), str)


@unittest.skipIf(em is None, f"element_maker import failed: {_ERR}")
class EscapeTests(unittest.TestCase):
    def test_esc_escapes_html_metachars(self):
        self.assertEqual(em._esc("a < b & c > d"), "a &lt; b &amp; c &gt; d")

    def test_chip_label_is_escaped(self):
        html = em._element_html({"type": "chip", "label": "<script>x</script>"})
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)


if __name__ == "__main__":
    unittest.main()
