# -*- coding: utf-8 -*-
"""SEOSONA Video — Observability hub (Phase 6).

ONE place that connects every quality/health signal that was scattered across the
engine, the scorer, and the queue:

  WRITE side (emitters call this, best-effort, never raises into a render):
    obs_metrics.record("render",  output=..., brand=..., duration=..., wpm=...,
                       caption_sync=..., sfx=..., render_seconds=...)
    obs_metrics.record("quality", output=..., score=..., verdict=...)
  → appended as JSON lines to logs/metrics/events.jsonl (the consolidated sink).

  READ side (the dashboard calls this):
    obs_metrics.read_health()  → one dict merging events.jsonl + the queue run.jsonl
    files + the daily logs + the 8_WORKSPACE outputs, with derived rates (caption-sync
    OK %, quality pass %, avg render time, voice-fallback %).

Nothing here needs a network or a paid API — it just reads/writes local files.
"""
import os
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
METRICS_DIR = ROOT / "logs" / "metrics"
EVENTS = METRICS_DIR / "events.jsonl"
QUEUE_LOGS = ROOT / "logs" / "queue"
DAILY_LOGS = ROOT / "logs" / "daily"
WORKSPACE = ROOT / "8_WORKSPACE"


# ───────────────────────────── write ─────────────────────────────
def record(event, **fields):
    """Append one metric event. Best-effort: a logging failure must NEVER break a render."""
    try:
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "event": event}
        rec.update(fields)
        with open(EVENTS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ───────────────────────────── read ──────────────────────────────
def _read_events(limit=400):
    if not EVENTS.exists():
        return []
    out = []
    try:
        for line in EVENTS.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        return []
    return out[-limit:]


def _pct(num, den):
    return round(100.0 * num / den, 1) if den else None


def read_health(recent=12):
    """Aggregate every signal into one health snapshot for the dashboard."""
    events = _read_events()
    renders = [e for e in events if e.get("event") == "render"]
    quality = {e.get("output"): e for e in events if e.get("event") == "quality"}

    # Merge quality onto each render by output path; build the recent table.
    rows = []
    for e in renders[-recent:][::-1]:
        out = e.get("output", "")
        q = quality.get(out, {})
        rows.append({
            "ts": e.get("ts", ""),
            "name": os.path.basename(out) if out else "?",
            "brand": e.get("brand", ""),
            "duration": e.get("duration"),
            "wpm": e.get("wpm"),
            "caption_sync": e.get("caption_sync"),     # "real" | "estimated"
            "sfx": e.get("sfx"),
            "render_seconds": e.get("render_seconds"),
            "score": q.get("score"),
            "verdict": q.get("verdict"),
        })

    # Derived rates over all recorded renders.
    n = len(renders)
    sync_real = sum(1 for e in renders if e.get("caption_sync") == "real")
    rseconds = [e["render_seconds"] for e in renders if isinstance(e.get("render_seconds"), (int, float))]
    qscores = [q["score"] for q in quality.values() if isinstance(q.get("score"), (int, float))]
    qpass = sum(1 for q in quality.values() if q.get("verdict") == "PASS")

    # Queue runs (Phase 3 run.jsonl files).
    qruns = []
    if QUEUE_LOGS.exists():
        for d in sorted(QUEUE_LOGS.iterdir(), reverse=True)[:8]:
            f = d / "run.jsonl"
            if f.exists():
                try:
                    r = json.loads(f.read_text(encoding="utf-8"))
                    qruns.append({"run": r.get("run", d.name),
                                  "ok": len(r.get("ok", [])),
                                  "failed": len(r.get("failed", [])),
                                  "skipped": len(r.get("skipped", []))})
                except Exception:
                    pass

    daily = sorted([p.name for p in DAILY_LOGS.glob("*.log")], reverse=True)[:5] if DAILY_LOGS.exists() else []
    outputs = len(list(WORKSPACE.rglob("*.mp4"))) if WORKSPACE.exists() else 0

    # Phase-6 feedback-loop state (ratcheted quality gate + weak signals), if computed.
    feedback = {}
    fstate = Path(__file__).resolve().parent / "feedback_state.json"
    if fstate.exists():
        try:
            feedback = json.loads(fstate.read_text(encoding="utf-8"))
        except Exception:
            feedback = {}

    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "totals": {
            "renders_recorded": n,
            "videos_on_disk": outputs,
            "caption_sync_real_pct": _pct(sync_real, n),
            "avg_render_seconds": round(sum(rseconds) / len(rseconds), 1) if rseconds else None,
            "avg_quality": round(sum(qscores) / len(qscores), 1) if qscores else None,
            "quality_pass_pct": _pct(qpass, len(quality)) if quality else None,
            "quality_gate": feedback.get("recommended_gate"),
        },
        "recent_renders": rows,
        "queue_runs": qruns,
        "daily_logs": daily,
        "feedback": feedback,
    }


if __name__ == "__main__":
    print(json.dumps(read_health(), ensure_ascii=False, indent=2))
