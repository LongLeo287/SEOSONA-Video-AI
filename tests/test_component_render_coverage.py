# -*- coding: utf-8 -*-
"""Integration contract: every LLM-pickable component kind (component_picker._ALLOWED) MUST have a
render branch in native_composer. The paired direction (_ALLOWED subset of spec_lint._REQUIRED) is
already locked by test_spec_lint.test_no_allowed_kind_is_ungated — but that only proves spec_lint
KNOWS the kind, not that native_composer can RENDER it. A kind added to _ALLOWED without a render
handler passes the blank-risk gate (it has a _REQUIRED contract) yet renders BLANK in production — the
worst silent failure. The concurrent factory loop edits both _ALLOWED and native_composer, so this
cross-layer drift is a live risk; lock it.
"""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import component_picker as cp
import spec_lint as sl

NC_SRC = open(os.path.join(ROOT, "4_BRAIN", "native_composer.py"), encoding="utf-8", errors="replace").read()


def _rendered_kinds(src):
    """Kinds native_composer dispatches on — `kind == "x"`, `comp_kind == "x"`, and `kind in ("a","b")`."""
    kinds = set(re.findall(r'(?:kind|comp_kind|ck|_ck)\s*==\s*["\']([a-z_]+)["\']', src))
    for m in re.finditer(r'(?:kind|comp_kind|ck)\s+in\s+\(([^)]*)\)', src):
        kinds |= set(re.findall(r'["\']([a-z_]+)["\']', m.group(1)))
    return kinds


class TestComponentRenderCoverage(unittest.TestCase):
    def test_every_static_allowed_kind_has_render_branch(self):
        # STATIC pickable kinds need an explicit per-kind render branch. GROWN kinds (frame_synth) render
        # through the GENERIC render_generated path (asserted separately below), so subtract them — the same
        # exemption test_spec_lint applies to _REQUIRED. A static kind with no branch renders BLANK.
        allowed = cp._allowed() if hasattr(cp, "_allowed") else set(cp._ALLOWED)
        rendered = _rendered_kinds(NC_SRC)
        missing = sorted(allowed - sl._grown_kinds() - rendered)
        self.assertEqual(missing, [], f"static _ALLOWED kinds with NO native_composer render branch "
                                      f"(would render BLANK): {missing}")

    def test_grown_kinds_have_generic_render_path(self):
        # grown kinds don't get a per-kind branch — they MUST reach frame_synth.render_generated, or a grown
        # kind assigned to a scene would render blank despite passing every gate.
        self.assertIn("render_generated", NC_SRC,
                      "native_composer lost the generic grown-frame render path (render_generated)")

    def test_allowed_is_nonempty(self):
        # guard the guard: if _allowed() ever returns empty, the coverage check above is vacuously true.
        allowed = cp._allowed() if hasattr(cp, "_allowed") else set(cp._ALLOWED)
        self.assertGreater(len(allowed), 10, "component_picker._ALLOWED collapsed — coverage test would be vacuous")


if __name__ == "__main__":
    unittest.main()
