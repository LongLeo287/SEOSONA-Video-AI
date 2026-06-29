# -*- coding: utf-8 -*-
"""SEOSONA Video — Feedback loop (Phase 6 close-out).

Closes the loop: quality scores + render signals (from the observability hub) →
a recommended quality GATE + actionable weak-signals → written to feedback_state.json,
which `quality_scorer` reads so the next batch is held to the bar the factory has
actually demonstrated (a ratchet — it goes UP as quality improves, never silently down,
and is capped so it stays reachable). No paid API; reads/writes local files only.

  python 9_DASHBOARD/feedback_loop.py          # recompute + write feedback_state.json
  python 9_DASHBOARD/feedback_loop.py --show   # print current state, change nothing

Run automatically at the end of each batch by scripts/daily_production.py.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATE = HERE / "feedback_state.json"

sys.path.insert(0, str(HERE))
import obs_metrics   # the hub (same folder)

GATE_FLOOR, GATE_CAP = 60, 85   # never below 60; never demand more than 85 (stays reachable)


def compute(min_samples=5):
    """Derive a recommended gate + weak signals from the hub's recent events."""
    events = obs_metrics._read_events()
    q = [e for e in events if e.get("event") == "quality" and isinstance(e.get("score"), (int, float))]
    r = [e for e in events if e.get("event") == "render"]
    scores = [e["score"] for e in q]
    n = len(scores)

    if n >= min_samples:
        ordered = sorted(scores)
        p25 = ordered[n // 4]                       # lower-quartile = a floor most takes clear
        gate = max(GATE_FLOOR, min(GATE_CAP, (int(p25) // 5) * 5))
    else:
        gate = GATE_FLOOR
    avg = round(sum(scores) / n, 1) if n else None
    passes = sum(1 for e in q if e.get("verdict") == "PASS")
    pass_rate = round(100.0 * passes / len(q), 1) if q else None

    # Weak signals — what to fix to make the next batch better.
    weak = []
    if r:
        est = sum(1 for e in r if e.get("caption_sync") == "estimated")
        if est / len(r) > 0.5:
            weak.append(f"caption-sync estimated on {round(100*est/len(r))}% of renders — "
                        "clone instability (bad takes -> ASR drops out). Improve voice clone / retry bad takes.")
        wpms = [e["wpm"] for e in r if isinstance(e.get("wpm"), (int, float))]
        if wpms:
            off = sum(1 for w in wpms if w < 130 or w > 180)
            if off / len(wpms) > 0.4:
                weak.append(f"wpm outside the comfortable band (130-180) on {round(100*off/len(wpms))}% of takes — "
                            "pacing auto-corrects, but the root is clone variance.")
    if avg is not None and avg < gate:
        weak.append(f"average score {avg} is below the gate {gate} — tighten content/brand before scaling.")
    if not weak:
        weak.append("no notable weak signals — quality is stable.")

    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "samples": n,
        "avg_score": avg,
        "pass_rate": pass_rate,
        "recommended_gate": gate,
        "weak_signals": weak,
    }


def write_state():
    state = compute()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[feedback] gate={state['recommended_gate']} (avg={state['avg_score']}, "
          f"pass={state['pass_rate']}%, n={state['samples']}) → {STATE.name}")
    for w in state["weak_signals"]:
        print(f"[feedback]   • {w}")
    return state


def current_gate(default=GATE_FLOOR):
    """Read the ratcheted gate for quality_scorer (file read — no import, safe from anywhere)."""
    try:
        return int(json.loads(STATE.read_text(encoding="utf-8")).get("recommended_gate", default))
    except Exception:
        return default


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true", help="print current state, don't recompute")
    a = ap.parse_args()
    if a.show:
        print(json.dumps(compute(), ensure_ascii=False, indent=2))
    else:
        write_state()
