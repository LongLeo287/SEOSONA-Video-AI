# -*- coding: utf-8 -*-
"""Security regression: the dashboard /api/action/preview endpoint runs `npx hyperframes preview "<dir>"`
with shell=True, interpolating the POSTed `project` name. Without validation that is a command-injection
(and path-traversal) surface — mitigated before only by a fragile `.exists()` check + Windows filename
rules. A strict single-segment name whitelist now rejects shell metachars / traversal before the shell.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "9_DASHBOARD"))

try:
    os.environ.setdefault("SEOSONA_DASH_HOST", "127.0.0.1")
    import server
    _client = server.app.test_client()
    _ERR = None
except Exception as e:
    _client, _ERR = None, e


@unittest.skipIf(_client is None, f"dashboard server import failed: {_ERR}")
class PreviewInjectionTests(unittest.TestCase):
    def _post(self, project):
        return _client.post("/api/action/preview", json={"project": project})

    def test_shell_metachars_and_traversal_rejected(self):
        for bad in ('../../etc', 'x" & calc & "', 'foo;bar', 'a | b', 'a && b', 'bad name', '..', 'a/b'):
            self.assertEqual(self._post(bad).status_code, 400, bad)

    def test_valid_name_passes_validation(self):
        # a well-formed (but non-existent) name must NOT be 400 — it passes the whitelist and 404s downstream
        self.assertNotEqual(self._post("valid_project-01").status_code, 400)

    def test_missing_project_rejected(self):
        self.assertEqual(self._post("").status_code, 400)


if __name__ == "__main__":
    unittest.main()
