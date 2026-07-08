# -*- coding: utf-8 -*-
"""Integration contract: every component kind hard-coded in a template (7_ASSETS/templates/*.json) MUST
be renderable by native_composer. This is a PROVEN recurring bug — commit 8743ea6 fixed listicle-top5,
which used component 'items' (no render branch) → a blank scene shipped. The factory loop keeps adding
templates, so this drift is live; lock it. Renderable universe = static render branches ∪ grown kinds
(generic frame_synth path) ∪ LLM-pickable (_allowed) — deliberately broad so only a genuinely unknown
kind (like 'items') fails, never a valid one."""
import os
import re
import sys
import json
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import component_picker as cp
import spec_lint as sl

TEMPLATE_DIR = os.path.join(ROOT, "7_ASSETS", "templates")
NC_SRC = open(os.path.join(ROOT, "4_BRAIN", "native_composer.py"), encoding="utf-8", errors="replace").read()


def _rendered_kinds(src):
    kinds = set(re.findall(r'(?:kind|comp_kind|ck|_ck)\s*==\s*["\']([a-z_]+)["\']', src))
    for m in re.finditer(r'(?:kind|comp_kind|ck)\s+in\s+\(([^)]*)\)', src):
        kinds |= set(re.findall(r'["\']([a-z_]+)["\']', m.group(1)))
    return kinds


def _universe():
    allowed = cp._allowed() if hasattr(cp, "_allowed") else set(cp._ALLOWED)
    return _rendered_kinds(NC_SRC) | sl._grown_kinds() | allowed


class TestTemplateIntegrity(unittest.TestCase):
    def test_every_template_component_is_renderable(self):
        universe = _universe()
        self.assertGreater(len(universe), 20, "renderable universe collapsed — check would be vacuous")
        bad = []
        for t in sorted(f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".json")):
            data = json.load(open(os.path.join(TEMPLATE_DIR, t), encoding="utf-8"))
            for i, sc in enumerate(data.get("scenes", [])):
                if isinstance(sc, dict):
                    k = sc.get("component")
                    if k and k not in universe:
                        bad.append(f"{t} scene[{i}] component={k!r}")
        self.assertEqual(bad, [], "template scenes with UNRENDERABLE component (would render blank): " + "; ".join(bad))

    def test_all_templates_parse(self):
        # a malformed template JSON crashes load_template at render time; catch it here.
        for t in sorted(f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".json")):
            with open(os.path.join(TEMPLATE_DIR, t), encoding="utf-8") as f:
                json.load(f)   # raises on bad JSON → test fails with the filename


if __name__ == "__main__":
    unittest.main()
