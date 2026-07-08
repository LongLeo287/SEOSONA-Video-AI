"""Security regression: the dashboard must not bind to all interfaces with the debugger on.

9_DASHBOARD/server.py exposes POST /api/action/* routes that RUN repo scripts. Running Flask
with host='0.0.0.0' AND debug=True puts Werkzeug's interactive debugger (arbitrary code
execution via the browser) on the whole network — a critical RCE. The served config must
default to localhost + debugger-off; LAN/debug are explicit env opt-ins only.
"""
import os
import re
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER = os.path.join(PROJECT_ROOT, "9_DASHBOARD", "server.py")


class DashboardBindSecurityTests(unittest.TestCase):
    def setUp(self):
        with open(SERVER, encoding="utf-8") as f:
            self.src = f.read()

    def test_app_run_uses_configurable_host_and_debug(self):
        m = re.search(r"app\.run\(([^)]*)\)", self.src)
        self.assertIsNotNone(m, "no app.run(...) found")
        call = m.group(1)
        # must NOT hardcode all-interfaces binding or the interactive debugger on the served instance
        self.assertNotIn("0.0.0.0", call, "server binds 0.0.0.0 unconditionally")
        self.assertNotRegex(call, r"debug\s*=\s*True", "server runs with debug=True unconditionally")

    def test_defaults_are_localhost_and_debug_off(self):
        # the resolved config lines default to localhost + debugger off (LAN/debug are env opt-ins).
        self.assertIn('"127.0.0.1"', self.src)
        self.assertIn("SEOSONA_DASH_DEBUG", self.src)


if __name__ == "__main__":
    unittest.main()
