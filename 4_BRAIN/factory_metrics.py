# -*- coding: utf-8 -*-
"""Factory flight-recorder — observability-light (the useful slice of EverOS observability +
Pixelle progress-events, WITHOUT the daemon/Prometheus weight). Appends ONE JSON line per
produced video to `3_MEMORY/factory_metrics.jsonl`. Cheap, offline, zero-dependency, never
raises into a render. Now that the factory is autonomous (discovery -> corrective script gate),
this is its health signal: pass-rate, durations, sizes, script source over time.

  python 4_BRAIN/factory_metrics.py        # print a summary (count, pass-rate, avg duration)
"""
import datetime
import json
import os
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "3_MEMORY" / "factory_metrics.jsonl"


def record(**row):
    """Append one metrics row (best-effort; observability must NEVER break production)."""
    try:
        row.setdefault("ts", datetime.datetime.now().isoformat(timespec="seconds"))
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _rows():
    if not LOG.exists():
        return []
    out = []
    for ln in LOG.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def summary():
    rows = _rows()
    if not rows:
        print("[factory_metrics] no data yet — produce a video first.")
        return
    n = len(rows)
    ok = sum(1 for r in rows if r.get("ok"))
    durs = [r["dur_s"] for r in rows if isinstance(r.get("dur_s"), (int, float))]
    srcs = {}
    for r in rows:
        srcs[r.get("script", "?")] = srcs.get(r.get("script", "?"), 0) + 1
    avg = round(sum(durs) / len(durs), 1) if durs else 0
    print(f"[factory_metrics] {n} videos | verify-pass {ok}/{n} ({round(100*ok/n)}%) | "
          f"avg {avg}s | script-source {srcs}")
    print("  last 5:")
    for r in rows[-5:]:
        print(f"   {r.get('ts','?')[:16]}  {str(r.get('repo'))[:34]:<34} "
              f"{'OK' if r.get('ok') else 'FAIL':<4} {r.get('dur_s','?')}s {r.get('size_mb','?')}MB"
              + (f" ⚠{r.get('lint_warns')}" if r.get('lint_warns') else ""))


if __name__ == "__main__":
    summary()
