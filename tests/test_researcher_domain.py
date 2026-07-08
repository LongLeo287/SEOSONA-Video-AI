"""Regression test: _on_domain must use whole-word matching, not a naive substring test.

_DOMAIN contains the weak tokens "ai"/"seo"/"search". The old `any(k in blob for k in _DOMAIN)`
false-matched them inside ordinary words — "ai" in "email"/"maintain", "search" in "researcher",
"seo" in "seoul" — so off-domain articles polluted the research pool (the #1 off-topic-drift risk).
_on_domain now delegates to the careful _domain_hit (whole-word + weak-token corroboration).
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import researcher as r  # noqa: E402


class OnDomainSubstringTests(unittest.TestCase):
    def test_substring_false_positives_are_rejected(self):
        # each of these ONLY collided via substring; none is a real SEO/marketing item
        self.assertFalse(r._on_domain({"title": "Sign up for our weekly email newsletter"}))   # 'ai' in email
        self.assertFalse(r._on_domain({"title": "How to maintain your car engine"}))            # 'ai' in maintain
        self.assertFalse(r._on_domain({"title": "Researcher finds new deep-sea species"}))      # 'search' in researcher
        self.assertFalse(r._on_domain({"title": "Seoul travel guide 2025"}))                    # 'seo' in seoul

    def test_genuine_on_domain_items_kept(self):
        self.assertTrue(r._on_domain({"title": "Cách tối ưu SEO cho website"}))     # 'website' strong
        self.assertTrue(r._on_domain({"title": "Google ranking factors 2025"}))    # 'google'/'ranking' strong
        self.assertTrue(r._on_domain({"title": "Hướng dẫn SEO mới nhất 2025"}))     # 'seo' weak + diacritic/year


if __name__ == "__main__":
    unittest.main()
