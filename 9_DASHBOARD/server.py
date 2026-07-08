import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory

app = Flask(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
# The observability hub (Phase 6) lives HERE in 9_DASHBOARD next to this server — one home
# for all observability. Engine emitters import it from this folder too.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT_DIR / "4_BRAIN"))   # for knowledge_graph (second-brain query API)
try:
    import obs_metrics
except Exception:
    obs_metrics = None
try:
    import knowledge_graph as kg   # recall/stats/health over the structure graph + content notes
except Exception:
    kg = None
INBOX_DIR = ROOT_DIR / "0_INPUT_INBOX"
QUEUE_FILE = INBOX_DIR / "production_queue.yaml"
DONE_DIR = INBOX_DIR / "done"
KNOW_DIR = ROOT_DIR / "2_KNOWLEDGE"
MEM_DIR = ROOT_DIR / "3_MEMORY"


def _read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default
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

    health = obs_metrics.read_health() if obs_metrics else {}

    return jsonify({
        "status": "online",
        "total_pending": total_pending,
        "total_done": total_done,
        "total_processing_temp": len(active_projects),
        "queue_details": queue_data,
        "done_files": done_files,
        "health": health,            # Phase 6: render/quality/sync/queue signals
    })


@app.route("/systemmap")
def systemmap():
    """Serve the full standalone SYSTEM_MAP.html (mermaid + vis-network) from docs/."""
    return send_from_directory(str(ROOT_DIR / "docs"), "SYSTEM_MAP.html")


@app.route("/api/health")
def health():
    """Just the observability snapshot (for scripts / external monitors)."""
    return jsonify(obs_metrics.read_health() if obs_metrics else {"error": "obs_metrics unavailable"})


# ---- Second-brain + factory data (Phase 0 read APIs; all local, zero-network) ----
@app.route("/api/graph")
def api_graph():
    """Knowledge graph (structure): nodes + edges for the embedded vis-network view."""
    return jsonify(_read_json(KNOW_DIR / "knowledge_graph.json", {"nodes": [], "edges": []}))


@app.route("/api/pipeline")
def api_pipeline():
    """The production pipeline as a DAG (4_BRAIN/pipeline_dag) → nodes+edges for the Pipeline view.
    Same {nodes,edges} contract as /api/graph so the frontend renderer is reused."""
    try:
        import pipeline_dag
        return jsonify(pipeline_dag.default_pipeline().to_graph())
    except Exception as e:
        return jsonify({"nodes": [], "edges": [], "error": str(e)})


@app.route("/api/graph-stats")
def api_graph_stats():
    if not kg:
        return jsonify({"error": "knowledge_graph unavailable"})
    try:
        return jsonify(kg.stats())
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/knowledge-audit")
def api_knowledge_audit():
    """System integrity: broken refs / overlaps / orphans / undocumented / stale."""
    return jsonify(_read_json(MEM_DIR / "knowledge_audit.json", {}))


@app.route("/api/factory-metrics")
def api_factory_metrics():
    """Per-video production flight recorder + template scoreboard."""
    rows = []
    p = MEM_DIR / "factory_metrics.jsonl"
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    return jsonify({"rows": rows[-50:], "template_scores": _read_json(MEM_DIR / "template_scores.json", {})})


@app.route("/api/recall")
def api_recall():
    """Second-brain content query — accumulated knowledge + rationale for a topic."""
    q = (request.args.get("q") or "").strip()
    if not kg or not q:
        return jsonify({"query": q, "results": []})
    try:
        return jsonify({"query": q, "results": kg.recall(q, limit=8)})
    except Exception as e:
        return jsonify({"query": q, "results": [], "error": str(e)})


@app.route("/api/learned")
def api_learned():
    """Effect→quality-score signal accumulated from real renders."""
    if not kg:
        return jsonify({"effects": {}})
    try:
        return jsonify(kg.effect_usage_stats())
    except Exception as e:
        return jsonify({"effects": {}, "error": str(e)})


@app.route("/api/events")
def api_events():
    """Live flight recorder — recent render/quality/publish events (newest first)."""
    rows = []
    p = ROOT_DIR / "logs" / "metrics" / "events.jsonl"
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    return jsonify({"events": rows[-60:][::-1], "total": len(rows)})


@app.route("/api/graph-health")
def api_graph_health():
    """Graph integrity signal: orphans + dead-end hubs + stats (from the query API)."""
    if not kg:
        return jsonify({"error": "knowledge_graph unavailable"})
    try:
        return jsonify({
            "stats": kg.stats(),
            "orphans": kg.orphans(),
            "dead_end_hubs": kg.dead_end_hubs(),
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/hot-learnings")
def api_hot_learnings():
    """Raw HOT_LEARNINGS.md (factory's self-analysis) for the Learning view."""
    p = MEM_DIR / "HOT_LEARNINGS.md"
    return jsonify({"markdown": p.read_text(encoding="utf-8") if p.exists() else ""})


@app.route("/api/angles")
def api_angles():
    """Recently produced angles/topics — what the factory has been making."""
    rows = []
    p = MEM_DIR / "recent_angles.jsonl"
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    return jsonify({"angles": rows[-30:][::-1]})


# ---- Phase 3: guarded management ACTIONS (local-only, run repo scripts) ----
def _run(cmd, timeout=600):
    """Run a repo script with the current interpreter; return status + tail of output.
    Force UTF-8 stdio so scripts that print unicode (→, emoji) don't crash on Windows cp1252."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, *cmd], cwd=str(ROOT_DIR),
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace", env=env,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
        return {"ok": proc.returncode == 0, "code": proc.returncode, "tail": out[-12:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "tail": [f"timeout after {timeout}s"]}
    except Exception as e:
        return {"ok": False, "code": -1, "tail": [str(e)]}


@app.route("/api/action/refresh-brain", methods=["POST"])
def action_refresh_brain():
    """Regenerate the knowledge graph + notes (structure + content) and re-sync SYSTEM_MAP."""
    g = _run(["scripts/gen_knowledge_graph.py"])
    n = _run(["scripts/gen_knowledge_notes.py"])
    if kg:  # drop in-memory caches so /api/recall + stats reflect the freshly-written files
        try:
            kg.reload()
        except Exception:
            pass
    return jsonify({"action": "refresh-brain", "ok": g["ok"] and n["ok"], "graph": g, "notes": n})


@app.route("/api/action/re-audit", methods=["POST"])
def action_re_audit():
    """Re-run the integrity auditor → refreshes 3_MEMORY/knowledge_audit.json."""
    return jsonify({"action": "re-audit", **_run(["scripts/knowledge_audit.py"])})


@app.route("/api/action/enqueue", methods=["POST"])
def action_enqueue():
    """Append one item to a production_queue category. Guarded: known category + bounded string."""
    body = request.get_json(silent=True) or {}
    item = (body.get("item") or "").strip()
    category = (body.get("category") or "news_videos").strip()
    valid = {"news_videos", "course_videos", "carousels", "thumbnails"}
    if not item or len(item) > 400:
        return jsonify({"ok": False, "error": "item required (1-400 chars)"}), 400
    if category not in valid:
        return jsonify({"ok": False, "error": f"category must be one of {sorted(valid)}"}), 400
    data = get_queue_data() or {}
    lst = [x for x in (data.get(category) or []) if x]  # drop empty placeholders
    lst.append(item)
    data[category] = lst
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    return jsonify({"ok": True, "category": category, "item": item, "queue_len": len(lst)})


@app.route("/api/workspace")
def api_workspace():
    """List all MP4 files in 8_WORKSPACE (for Library view)."""
    from datetime import datetime as _dt
    files = []
    if WORKSPACE_DIR.exists():
        for mp4 in sorted(WORKSPACE_DIR.rglob("*.mp4"),
                          key=lambda p: p.stat().st_mtime, reverse=True)[:50]:
            try:
                stat = mp4.stat()
                files.append({
                    "name": mp4.name,
                    "path": str(mp4.relative_to(WORKSPACE_DIR)).replace("\\", "/"),
                    "size_mb": round(stat.st_size / 1024 / 1024, 1),
                    "mtime": _dt.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                    "folder": mp4.parent.name if mp4.parent != WORKSPACE_DIR else "",
                })
            except Exception:
                pass
    return jsonify({"files": files, "total": len(files)})


@app.route("/api/daily-trend")
def api_daily_trend():
    """Aggregate render + quality events by day (last 30 days) for the Analytics charts."""
    from collections import defaultdict
    rows = []
    p = ROOT_DIR / "logs" / "metrics" / "events.jsonl"
    if p.exists():
        for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    by_day = defaultdict(lambda: {"renders": 0, "quality_pass": 0, "quality_total": 0, "scores": []})
    for e in rows:
        ts = (e.get("ts") or "")[:10]
        if not ts:
            continue
        if e.get("event") == "render":
            by_day[ts]["renders"] += 1
        elif e.get("event") == "quality":
            by_day[ts]["quality_total"] += 1
            if e.get("verdict") == "PASS":
                by_day[ts]["quality_pass"] += 1
            if isinstance(e.get("score"), (int, float)):
                by_day[ts]["scores"].append(e["score"])
    result = []
    for day in sorted(by_day.keys())[-30:]:
        d = by_day[day]
        result.append({
            "day": day,
            "renders": d["renders"],
            "quality_pass_pct": round(100 * d["quality_pass"] / d["quality_total"], 1) if d["quality_total"] else None,
            "avg_score": round(sum(d["scores"]) / len(d["scores"]), 1) if d["scores"] else None,
        })
    return jsonify({"days": result})


@app.route("/api/system-stats")
def api_system_stats():
    """Count files in key directories — used by Analytics overview cards."""
    from datetime import datetime as _dt

    def count_dir(rel, ext=None):
        # os.walk with onerror skips broken symlinks/junctions (e.g. dead vendored dataset links)
        # that would otherwise crash a Path.rglob() traversal with FileNotFoundError on Windows.
        p = ROOT_DIR / rel
        if not p.exists():
            return 0
        n = 0
        for _root, _dirs, files in os.walk(p, onerror=lambda e: None):
            n += sum(1 for f in files if ext is None or f.endswith(ext))
        return n

    mp4_total = 0
    for _root, _dirs, files in os.walk(WORKSPACE_DIR, onerror=lambda e: None):
        mp4_total += sum(1 for f in files if f.endswith(".mp4"))
    agents = len([d for d in (ROOT_DIR / "1_AGENTS").iterdir() if d.is_dir()]) \
             if (ROOT_DIR / "1_AGENTS").exists() else 0
    return jsonify({
        "mp4_total": mp4_total,
        "agents": agents,
        "skill_modules": count_dir("2_SKILLS") - 1,   # subtract README
        "brain_files": count_dir("4_BRAIN", ".py"),
        "knowledge_files": count_dir("2_KNOWLEDGE"),
        "templates": count_dir("7_ASSETS/templates", ".json"),
        "sop_files": count_dir("6_SOP"),
        "generated": _dt.now().isoformat(timespec="seconds"),
    })


@app.route("/api/templates")
def api_templates():
    """List all scene-structure templates from 7_ASSETS/templates/."""
    import glob as _glob
    tpl_dir = ROOT_DIR / "7_ASSETS" / "templates"
    templates = []
    if tpl_dir.exists():
        for f in sorted(tpl_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                templates.append({
                    "name": f.stem,
                    "file": f.name,
                    "components": len(data.get("scenes", data.get("components", []))),
                    "accent": data.get("accent", ""),
                    "kicker": data.get("kicker_hint", ""),
                })
            except Exception:
                templates.append({"name": f.stem, "file": f.name})
    return jsonify({"templates": templates, "total": len(templates)})


@app.route("/api/npm-scripts")
def api_npm_scripts():
    """List all npm scripts from package.json for Commands view."""
    pkg = ROOT_DIR / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            # Group scripts by prefix
            groups = {}
            for name, cmd in scripts.items():
                prefix = name.split(":")[0] if ":" in name else name.split("_")[0]
                groups.setdefault(prefix, []).append({"name": name, "cmd": cmd})
            return jsonify({"scripts": scripts, "groups": groups, "total": len(scripts)})
        except Exception as e:
            return jsonify({"scripts": {}, "groups": {}, "error": str(e)})
    return jsonify({"scripts": {}, "groups": {}})


@app.route("/api/file-tree")
def api_file_tree():
    """Return workspace directory tree (depth-limited) for File Explorer."""
    from datetime import datetime as _dt

    SKIP = {'.git', '__pycache__', 'node_modules', '.agents', '.cache', 'dist', 'build', '.venv', 'venv'}

    def make_node(p, depth=0):
        if depth > 2:
            return None
        try:
            name = p.name
            if name.startswith('.') or name in SKIP:
                return None
            is_dir = p.is_dir()
            node = {
                "name": name,
                "path": str(p.relative_to(ROOT_DIR)).replace("\\", "/"),
                "is_dir": is_dir,
            }
            if is_dir:
                children = []
                try:
                    items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                    for child in items[:24]:
                        child_node = make_node(child, depth + 1)
                        if child_node:
                            children.append(child_node)
                    node["children"] = children
                    node["child_count"] = sum(1 for _ in p.iterdir() if not _.name.startswith('.'))
                except PermissionError:
                    node["children"] = []
            else:
                try:
                    stat = p.stat()
                    node["size"] = stat.st_size
                    node["mtime"] = _dt.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
                    node["ext"] = p.suffix.lower()
                except Exception:
                    pass
            return node
        except Exception:
            return None

    tree = []
    try:
        items = sorted(ROOT_DIR.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for p in items:
            node = make_node(p, 0)
            if node:
                tree.append(node)
    except Exception as e:
        return jsonify({"tree": [], "error": str(e)})

    return jsonify({"tree": tree, "root": str(ROOT_DIR).replace("\\", "/")})


@app.route("/api/process-status")
def api_process_status():
    """Check if Python/Node processes are running (Windows tasklist)."""
    import subprocess as _sp
    procs = []
    try:
        result = _sp.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5, shell=True
        )
        for line in result.stdout.strip().splitlines():
            parts = [p.strip('"') for p in line.split('","')]
            if len(parts) >= 2:
                name_lower = parts[0].lower()
                if any(k in name_lower for k in ("python", "node", "ffmpeg")):
                    procs.append({"name": parts[0], "pid": parts[1] if len(parts) > 1 else "?"})
    except Exception as e:
        return jsonify({"processes": [], "error": str(e)})
    return jsonify({"processes": procs[:15], "count": len(procs)})


@app.route("/api/kanban")
def api_kanban():
    """Return kanban board lanes: queue / processing / qa / done."""
    queue_data = get_queue_data()
    health = obs_metrics.read_health() if obs_metrics else {}

    # --- Queue lane ---
    queue_items = []
    for cat, items in (queue_data or {}).items():
        for item in (items or []):
            if not item:
                continue
            queue_items.append({
                "id": abs(hash(str(item) + cat)) % 999999,
                "title": str(item)[:80],
                "type": cat,
                "lane": "queue",
            })

    # --- Done / QA lanes: from recent_renders (dedup by ts+name) ---
    qa_items, done_items = [], []
    seen_render = set()
    for r in (health.get("recent_renders") or []):
        name = str(r.get("name") or r.get("output") or "").replace("\\", "/").split("/")[-1]
        ts = str(r.get("ts") or "")
        uid = name + "|" + ts  # unique key
        if uid in seen_render:
            continue
        seen_render.add(uid)
        # Extract project from output path
        out = str(r.get("output") or r.get("name") or "").replace("\\", "/")
        parts = out.split("/")
        proj = parts[-2] if len(parts) >= 2 else ""
        verdict = r.get("verdict")
        card = {
            "id": abs(hash(uid)) % 9999999,
            "title": name[:80] or "render",
            "project": proj[:40],
            "type": "render",
            "score": r.get("score"),
            "duration": r.get("duration"),
            "wpm": r.get("wpm"),
            "ts": ts[:16],
            "verdict": verdict,
        }
        if verdict == "PASS":
            done_items.append({**card, "lane": "done"})
        else:
            qa_items.append({**card, "lane": "qa"})

    # --- Processing lane: workspace project folders WITHOUT mp4 yet ---
    processing_items = []
    if WORKSPACE_DIR.exists():
        for d in sorted(WORKSPACE_DIR.iterdir()):
            if d.is_dir() and not d.name.startswith((".", "_")):
                mp4s = list(d.glob("*.mp4"))
                all_files = list(d.iterdir())
                if not mp4s:
                    processing_items.append({
                        "id": abs(hash(d.name + "proc")) % 9999999,
                        "title": d.name[:80],
                        "type": "project",
                        "lane": "processing",
                        "n": len(all_files),
                    })

    # --- Done: also scan workspace for actual mp4s (ground truth) ---
    if not done_items and WORKSPACE_DIR.exists():
        for d in sorted(WORKSPACE_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if d.is_dir() and not d.name.startswith((".", "_")):
                for mp4 in sorted(d.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True):
                    if len(done_items) >= 15:
                        break
                    done_items.append({
                        "id": abs(hash(mp4.name + str(mp4.stat().st_mtime))) % 9999999,
                        "title": mp4.name[:80],
                        "project": d.name[:40],
                        "type": "render",
                        "lane": "done",
                        "size_mb": round(mp4.stat().st_size / 1_000_000, 1),
                    })

    lanes = {
        "queue":      queue_items[:25],
        "processing": processing_items[:12],
        "qa":         qa_items[:12],
        "done":       done_items[:20],
    }
    return jsonify({"lanes": lanes, "total": sum(len(v) for v in lanes.values())})


preview_process = None

@app.route("/api/video/<path:filepath>")
def api_video(filepath):
    """Serve MP4 video directly from 8_WORKSPACE for the Video Player modal."""
    return send_from_directory(str(WORKSPACE_DIR), filepath)

@app.route("/api/action/preview", methods=["POST"])
def action_preview():
    """Start the hyperframes preview server for a specific project."""
    global preview_process
    body = request.get_json(silent=True) or {}
    project = body.get("project")
    if not project:
        return jsonify({"ok": False, "error": "project name required"}), 400
    # `project` flows into a shell=True command below — allow ONLY a safe single-segment name (no shell
    # metachars &|;<>()"'`$, no spaces, no path separators or traversal). Factory project dirs are simple
    # slugs, so this rejects nothing real while closing command-injection + directory-traversal.
    import re as _r
    if not _r.fullmatch(r"[A-Za-z0-9_.\-]+", str(project)) or ".." in project:
        return jsonify({"ok": False, "error": "invalid project name"}), 400

    project_dir = WORKSPACE_DIR / project
    if not project_dir.exists():
        return jsonify({"ok": False, "error": "project not found"}), 404
        
    try:
        if preview_process:
            preview_process.terminate()
            preview_process.wait(timeout=2)
    except Exception:
        pass
        
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    # Add npx to path specifically for Windows if needed, but subprocess with shell=True works better on Windows for npx
    try:
        preview_process = subprocess.Popen(
            f"npx hyperframes preview \"{project_dir}\" --port 3000", 
            cwd=str(ROOT_DIR),
            env=env,
            shell=True
        )
        return jsonify({"ok": True, "project": project, "port": 3000})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ---- Studio / Create (async video generation — the one place the read-mostly model bends) ----
import re as _re
STUDIO_JOBS_DIR = MEM_DIR / "studio_jobs"


@app.route("/api/studio/generate", methods=["POST"])
def studio_generate():
    """Spawn a detached studio_job.py that reuses make_video. Returns a job_id to poll — never blocks."""
    from datetime import datetime as _dt
    body = request.get_json(silent=True) or {}
    target = (body.get("target") or "").strip()
    template = (body.get("template") or "").strip()
    aspect = (body.get("aspect") or "").strip()
    dry = bool(body.get("dry"))
    if not _re.match(r'^(https?://github\.com/)?[\w.-]+/[\w.-]+/?$', target):
        return jsonify({"ok": False, "error": "target must be a GitHub url or owner/name"}), 400
    if aspect and aspect not in {"9:16", "16:9", "1:1"}:
        return jsonify({"ok": False, "error": "aspect must be 9:16, 16:9 or 1:1"}), 400
    job_id = _dt.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    out = str(WORKSPACE_DIR / "studio" / job_id / (job_id + ".mp4"))
    cmd = [sys.executable, str(ROOT_DIR / "scripts" / "studio_job.py"),
           "--id", job_id, "--target", target, "--out", out]
    if template:
        cmd += ["--template", template]
    if aspect:
        cmd += ["--aspect", aspect]
    if dry:
        cmd += ["--dry"]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        subprocess.Popen(cmd, cwd=str(ROOT_DIR), env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   # detached, non-blocking
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    return jsonify({"ok": True, "job_id": job_id, "status": "queued"})


@app.route("/api/studio/jobs")
def studio_jobs():
    """Recent studio jobs (newest first)."""
    jobs = []
    if STUDIO_JOBS_DIR.exists():
        for p in sorted(STUDIO_JOBS_DIR.glob("*.json"), key=lambda x: x.name, reverse=True)[:30]:
            rec = _read_json(p, None)
            if rec:
                jobs.append(rec)
    return jsonify({"jobs": jobs})


@app.route("/api/studio/job/<job_id>")
def studio_job(job_id):
    """One studio job record (for status polling). job_id is validated to a safe token."""
    if not _re.match(r'^[\w.-]+$', job_id):
        return jsonify({"error": "bad id"}), 400
    rec = _read_json(STUDIO_JOBS_DIR / (job_id + ".json"), None)
    return jsonify(rec or {"error": "not found", "status": "unknown"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))   # honor PORT so a preview/second instance can use another port
    # SECURITY: this dashboard exposes POST /api/action/* routes that RUN repo scripts. Bind to localhost
    # and keep Flask's debugger OFF by default — `host=0.0.0.0` + `debug=True` put Werkzeug's interactive
    # debugger (arbitrary code execution via the browser on any exception) on the whole network = RCE.
    # Opt into LAN access / the debugger explicitly, and only on a trusted local machine.
    host = os.environ.get("SEOSONA_DASH_HOST", "127.0.0.1")   # set 0.0.0.0 to expose on the LAN (risky)
    debug = os.environ.get("SEOSONA_DASH_DEBUG") == "1"        # never the interactive debugger by default
    print(f"[SEOSONA] Nightingale Dashboard starting on http://{host}:{port}  (debug={debug})")
    # use_reloader keeps the dev workflow (server.py edits hot-reload) WITHOUT turning on the debugger's
    # RCE console. The loop respawns this daemon and relies on the reloader picking up edits.
    app.run(host=host, port=port, debug=debug, use_reloader=True)
