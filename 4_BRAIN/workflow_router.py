"""
Workflow Router — Smart entry point that decides which pipeline to run.
"""
import os
import sys

# --- SEOSONA AUTO-BOOTSTRAP ---
try:
    from importlib import import_module
    brain_dir = os.path.dirname(os.path.abspath(__file__))
    if brain_dir not in sys.path:
        sys.path.insert(0, brain_dir)
    bootstrap = import_module('seosona_bootstrap')
    bootstrap.bootstrap()
except Exception as e:
    print(f"[Router] Bootstrap check failed: {e}")
# ------------------------------

from importlib import import_module

# Monkey-patch cho MoviePy 1.0.3 tương thích với Pillow >= 10.0.0
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS

def detect_input_type(input_value):
    """
    Auto-detects the input type and returns the appropriate mode.
    """
    if not input_value:
        return "create", input_value

    # URL detection
    if input_value.startswith("http://") or input_value.startswith("https://"):
        if "youtube.com" in input_value or "youtu.be" in input_value:
            return "download", input_value
        return "scrape", input_value

    # File detection
    if os.path.isfile(input_value):
        ext = os.path.splitext(input_value)[1].lower()
        if ext == ".srt":
            return "repurpose", input_value
        elif ext in [".mp4", ".mkv", ".avi", ".mov"]:
            return "repurpose", input_value
        elif ext in [".txt", ".md"]:
            with open(input_value, 'r', encoding='utf-8') as f:
                text = f.read()
            return "create", text

    # Plain text (script)
    return "create", input_value

def route(input_value, brand="seosona", aspect_ratio="9:16", project_name=None):
    """
    Main entry point. Detects input type and routes to the correct pipeline.
    """
    mode, processed_input = detect_input_type(input_value)

    print(f"[Router] Input detected as: {mode.upper()}")
    print(f"[Router] Brand: {brand.upper()}")
    print(f"[Router] Aspect Ratio: {aspect_ratio}")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(project_root)
    from importlib import import_module

    if mode == "download":
        print("[Router] → Step 1: yt-dlp Download")
        yt_engine = import_module('2_SKILLS.yt_downloader.yt_dlp_engine')
        download_dir = os.path.join(project_root, '8_WORKSPACE', project_name or 'yt_download', '.temp')
        yt_engine.download_video(processed_input, download_dir)

        print("[Router] → Step 2: Routing downloaded file to Repurpose Pipeline")
        # Find the downloaded video file
        video_files = [f for f in os.listdir(download_dir) if f.endswith(('.mp4', '.mkv', '.webm'))] if os.path.exists(download_dir) else []
        if video_files:
            processed_input = os.path.join(download_dir, video_files[0])
            mode = "repurpose"
        else:
            print("[Router] ⚠ No video file found after download. Aborting.")
            return

    elif mode == "repurpose":
        print("[Router] → Routing to: SRT Analyzer → Clipper → Render Pipeline")
    elif mode == "scrape":
        print("[Router] -> Step 1: Web Scraping (crawl4ai)")
        print("[Router] -> Step 2: Extracting News Script (OpenAI)")
        print("[Router] -> Step 3: Screen Recording B-Roll (Playwright/browser-use)")
        print("[Router] -> Step 4: Routing to Render Pipeline")
    else:
        print("[Router] → Routing to: TTS → Whisper → Render Pipeline")

    pipeline = import_module('4_BRAIN.pipeline_manager')
    pipeline.run_pipeline(processed_input, brand=brand, mode=mode, aspect_ratio=aspect_ratio, project_name=project_name)

if __name__ == "__main__":
    input_val = sys.argv[1] if len(sys.argv) > 1 else "Welcome to SEOSONA Video Factory."
    brand = sys.argv[2] if len(sys.argv) > 2 else "seosona"
    ratio = sys.argv[3] if len(sys.argv) > 3 else "9:16"
    name = sys.argv[4] if len(sys.argv) > 4 else None
    route(input_val, brand, ratio, name)
