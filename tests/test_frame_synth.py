"""Regression tests for frame_synth's safety gate + templating.

Generated frames are PERSISTED and re-rendered by a full browser engine, so validate() must
reject ALL active content (any event handler, script/js URIs, iframe/object/embed/…), and
_fill() must HTML-escape data values. _load() must tolerate a missing/corrupt state file.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import frame_synth as fs  # noqa: E402

GOOD = ('<div class="card" style="background:#fff;color:#2A5BDA">{{title}}'
        '<ul>{{#items}}<li class="ritem">{{.}}</li>{{/items}}</ul></div>')


class ValidateSafetyTests(unittest.TestCase):
    def test_good_template_passes(self):
        ok, reason = fs.validate({"html": GOOD}, {"title": "T", "items": ["a", "b"]})
        self.assertTrue(ok, reason)

    def test_active_content_blocked(self):
        vectors = [
            '<div class="c"><script>x()</script></div>',
            '<div class="c"><img src="x" onerror="alert(1)"></div>',   # onerror (not onload)
            '<div class="c" onclick="steal()">hi</div>',
            '<div class="c"><iframe src="x"></iframe></div>',
            '<div class="c"><object data="x"></object></div>',
            '<a class="c" href="javascript:x()">hi</a>',
            '<div class="c" style="background:url(http://evil/x.png)">hi</div>',
        ]
        for html in vectors:
            ok, _ = fs.validate({"html": html}, {})
            self.assertFalse(ok, f"should block: {html}")

    def test_dark_background_blocked(self):
        ok, _ = fs.validate({"html": '<div class="c" style="background:#111">x</div>'}, {})
        self.assertFalse(ok)   # SEOSONA is light-only

    def test_no_false_positive_on_plain_text(self):
        # 'on'-words without an =event-handler must not trip the gate
        html = '<div class="c" style="background:#fff">Bật lên, tắt đi — act on it</div>'
        ok, _ = fs.validate({"html": html}, {})
        self.assertTrue(ok)


class FillEscapeTests(unittest.TestCase):
    def test_data_values_are_escaped(self):
        out = fs._fill('<div class="c">{{title}}</div>', {"title": "<script>x</script>"}, "#2A5BDA")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_leftover_placeholders_stripped(self):
        out = fs._fill('<div class="c">{{missing}}</div>', {}, "#2A5BDA")
        self.assertNotIn("{{", out)


class LoadRobustnessTests(unittest.TestCase):
    def test_load_never_raises(self):
        self.assertIsInstance(fs._load(), dict)   # missing/corrupt file → {}


if __name__ == "__main__":
    unittest.main()
