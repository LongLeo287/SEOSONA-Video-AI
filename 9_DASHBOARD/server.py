import os
import yaml
from pathlib import Path
from flask import Flask, render_template, jsonify

app = Flask(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = ROOT_DIR / "0_INPUT_INBOX"
QUEUE_FILE = INBOX_DIR / "production_queue.yaml"
DONE_DIR = INBOX_DIR / "done"
# Active render area. The engine (native_composer / video_engine / make_video) writes
# finished projects under 8_WORKSPACE/ (auto/, news_batch/, clones/, ...), not .temp/.
WORKSPACE_DIR = ROOT_DIR / "8_WORKSPACE"

def get_queue_data():
    if not QUEUE_FILE.exists():
        return {}
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def get_done_files():
    if not DONE_DIR.exists():
        return []
    try:
        return [f.name for f in DONE_DIR.iterdir() if f.is_file()]
    except Exception:
        return []

def get_active_projects():
    """Render-project folders currently in 8_WORKSPACE (each = one video build)."""
    if not WORKSPACE_DIR.exists():
        return []
    try:
        return [d.name for d in WORKSPACE_DIR.iterdir()
                if d.is_dir() and not d.name.startswith((".", "_"))]
    except Exception:
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/metrics")
def metrics():
    queue_data = get_queue_data()
    done_files = get_done_files()
    active_projects = get_active_projects()

    # Calculate totals — count only real queued items (skip empty-string placeholders)
    total_pending = sum(len([i for i in items if i]) for items in queue_data.values() if items)
    total_done = len(done_files)

    return jsonify({
        "status": "online",
        "total_pending": total_pending,
        "total_done": total_done,
        "total_processing_temp": len(active_projects),
        "queue_details": queue_data,
        "done_files": done_files
    })

if __name__ == "__main__":
    print("🚀 SEOSONA Nightingale Dashboard starting on http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
