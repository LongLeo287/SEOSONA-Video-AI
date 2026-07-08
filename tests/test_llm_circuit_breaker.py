"""Tests for the API-key circuit-breaker in llm_engine (pattern mined from OmniRoute).

Pure logic only — no network. Verifies a rate-limited key is skipped for a cooldown
window instead of being re-tried first on every call, and recovers after the window.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import llm_engine as L  # noqa: E402


def _order(keys):
    """Replicate the ordering _gemini_scenes uses: ready keys first, cooling ones last."""
    return [k for k in keys if L._key_ready(k)] + [k for k in keys if not L._key_ready(k)]


class CircuitBreakerTests(unittest.TestCase):
    def setUp(self):
        L._KEY_COOLDOWN.clear()

    def test_fresh_keys_keep_order(self):
        keys = ["kA", "kB", "kC"]
        self.assertEqual(_order(keys), keys)

    def test_tripped_key_moves_last_and_is_not_ready(self):
        keys = ["kA", "kB", "kC"]
        L._trip_key("kA", 300)
        self.assertFalse(L._key_ready("kA"))
        self.assertEqual(_order(keys), ["kB", "kC", "kA"])

    def test_cooldown_expiry_restores_readiness(self):
        L._trip_key("kB", -1)  # cooldown already in the past
        self.assertTrue(L._key_ready("kB"))

    def test_all_tripped_still_returns_all_keys(self):
        # last-resort: never hard-fail just because every key is cooling down
        keys = ["kA", "kB"]
        L._trip_key("kA", 300)
        L._trip_key("kB", 300)
        self.assertCountEqual(_order(keys), keys)


if __name__ == "__main__":
    unittest.main()
