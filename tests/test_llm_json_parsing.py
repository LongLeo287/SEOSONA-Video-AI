"""Regression tests for llm_engine's JSON recovery from real-model output.

Models frequently wrap JSON in prose/fences despite 'output ONLY JSON' instructions
("Sure! Here is the JSON: ```json{...}``` Hope this helps!"). The cascade parsers must
recover the balanced JSON block instead of discarding a good response and falling through
to the next tier (or offline) — which degrades content quality.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import llm_engine as le  # noqa: E402

PROSE = ('Sure! Here is the JSON you asked for:\n```json\n'
         '{"angles": ["a", "b"], "scenes": [{"x": 1}]}\n```\nLet me know if you need changes.')


class ExtractBlockTests(unittest.TestCase):
    def test_object_in_prose(self):
        self.assertEqual(le._extract_json_block('note: {"a":1} end'), '{"a":1}')

    def test_array_of_objects_returns_whole_array(self):
        # the earliest bracket ([ ) is the outer structure — not the first inner {
        self.assertEqual(le._extract_json_block('x [{"a":1},{"b":2}] y'), '[{"a":1},{"b":2}]')

    def test_braces_inside_strings_and_nesting(self):
        s = '{"nested":{"k":[1,2]},"s":"a}b{c"}'
        self.assertEqual(le._extract_json_block("prefix " + s + " suffix"), s)

    def test_none_when_no_json(self):
        self.assertIsNone(le._extract_json_block("no json here"))


class ParserRecoveryTests(unittest.TestCase):
    def test_parse_json_or_none_recovers_prose(self):
        self.assertEqual(le._parse_json_or_none(PROSE),
                         {"angles": ["a", "b"], "scenes": [{"x": 1}]})

    def test_parse_json_or_none_fast_path_and_garbage(self):
        self.assertEqual(le._parse_json_or_none('{"a":1}'), {"a": 1})
        self.assertIsNone(le._parse_json_or_none("totally not json"))

    def test_json_ok_recovers_and_checks_key(self):
        self.assertIsNotNone(le._json_ok(PROSE, require_key="angles"))
        self.assertIsNone(le._json_ok(PROSE, require_key="missing"))

    def test_scenes_ok_recovers(self):
        self.assertIsNotNone(le._scenes_ok(PROSE))
        self.assertIsNone(le._scenes_ok("no scenes at all"))


if __name__ == "__main__":
    unittest.main()
