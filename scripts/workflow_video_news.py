"""
SEOSONA News Video workflow entrypoint.

Input:
  - Vietnamese news script text
  - .txt/.md script file
  - website URL for scrape-to-news-video

Output:
  - 8_WORKSPACE/<project>/ MP4, SRT, thumbnail, and render manifest
"""
import os
import sys
from importlib import import_module


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/workflow_video_news.py <script_or_file_or_url> [project_name] [aspect_ratio]")
        sys.exit(1)


    # NOTE: the old --generate-broll / --autopilot flags were removed — they set
    # SEOSONA_AUTO_BROLL / SEOSONA_AUTOPILOT env vars that the legacy pipeline_manager
    # read but the current video_engine does not. They were dead no-ops.
    input_value = sys.argv[1]

    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    aspect_ratio = sys.argv[3] if len(sys.argv) > 3 else "9:16"

    router = import_module("4_BRAIN.workflow_router")
    router.route(input_value, brand="seosona", aspect_ratio=aspect_ratio, project_name=project_name)


if __name__ == "__main__":
    main()
