import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

from video_integration_audit import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
