"""Studio job runner — the detached async worker behind the dashboard's Create/Studio view.

Spawned (non-blocking) by 9_DASHBOARD/server.py `/api/studio/generate`. Writes a job record to
3_MEMORY/studio_jobs/<id>.json and updates it through the lifecycle (running -> done|failed) so the
dashboard can poll `/api/studio/job/<id>`. Generation itself reuses 4_BRAIN/make_video.py (the real
engine) as an isolated subprocess — this wrapper only owns the job record + status.

  python scripts/studio_job.py --id 20260702-101500 --target owner/name --out 8_WORKSPACE/studio/<id>/<id>.mp4
  python scripts/studio_job.py --id test --target x/y --out /tmp/x.mp4 --dry   # plumbing test, no real render
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JOBS_DIR = os.path.join(ROOT, "3_MEMORY", "studio_jobs")


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _write(rec):
    os.makedirs(JOBS_DIR, exist_ok=True)
    path = os.path.join(JOBS_DIR, rec["id"] + ".json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)   # atomic — a poller never reads a half-written record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--target", required=True, help="github url or owner/name")
    ap.add_argument("--template")
    ap.add_argument("--aspect", choices=["9:16", "16:9", "1:1"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry", action="store_true", help="simulate lifecycle without a real render")
    a = ap.parse_args()

    rec = {
        "id": a.id, "kind": "studio", "status": "running",
        "target": a.target, "template": a.template or "(auto)", "aspect": a.aspect or "(template)",
        "output": None, "error": None,
        "started": _now(), "finished": None, "log_tail": [],
    }
    _write(rec)

    try:
        if a.dry:
            time.sleep(2)   # simulate work so the UI can show the running state
            rec["status"] = "done"
            rec["output"] = os.path.relpath(a.out, os.path.join(ROOT, "8_WORKSPACE")).replace("\\", "/")
            rec["log_tail"] = ["[dry] simulated render - no real video produced"]
        else:
            os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
            cmd = [sys.executable, os.path.join(ROOT, "4_BRAIN", "make_video.py"), a.target, "--out", a.out]
            if a.template:
                cmd += ["--template", a.template]
            if a.aspect:
                cmd += ["--aspect", a.aspect]
            env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", env=env, timeout=1800)
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-15:]
            rec["log_tail"] = tail
            if proc.returncode == 0 and os.path.exists(a.out):
                rec["status"] = "done"
                rec["output"] = os.path.relpath(a.out, os.path.join(ROOT, "8_WORKSPACE")).replace("\\", "/")
            else:
                rec["status"] = "failed"
                rec["error"] = (tail[-1] if tail else f"render failed (rc={proc.returncode})")
    except subprocess.TimeoutExpired:
        rec["status"] = "failed"
        rec["error"] = "timeout after 1800s"
    except Exception as e:  # noqa: BLE001 — any failure must land in the record, not crash silently
        rec["status"] = "failed"
        rec["error"] = str(e)[:300]
    finally:
        rec["finished"] = _now()
        _write(rec)
    return 0 if rec["status"] == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
