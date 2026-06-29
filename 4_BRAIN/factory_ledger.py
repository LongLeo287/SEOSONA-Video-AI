# -*- coding: utf-8 -*-
"""SEOSONA Video — Learning Ledger (ORIENT stage of the factory loop).

Aggregates every production_manifest into a memory of "what works", keyed by
variant dimension (template / brand / aspect / voice / topic / length). Produces:

  - 3_MEMORY/learning/ledger.json        — full per-dimension stats (human + audit)
  - 7_ASSETS/templates/_performance.json — template selection WEIGHTS (machine)

Today it scores on the QA signal (quality score + pass-rate). The moment real
metrics land in each manifest's `performance` block (views/CTR/retention via
analytics_feedback_agent.performance_ingest), the SAME aggregation upgrades to a
true market score with NO code change — `_score_row` just starts seeing them.

This is the ORIENT step of 6_SOP/AUTONOMOUS_FACTORY_LOOP.md.
"""
import os, sys, json
from collections import defaultdict
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
import production_manifest as pm

LEDGER_PATH = os.path.join(ROOT, "3_MEMORY", "learning", "ledger.json")
# NOTE: kept OUT of 7_ASSETS/templates/ on purpose — native_composer.list_templates()
# enumerates every *.json there, so a weights file placed inside would be mis-read as
# a (broken) template. Lives beside the ledger instead.
WEIGHTS_PATH = os.path.join(ROOT, "3_MEMORY", "learning", "template_weights.json")

DIMENSIONS = ["template", "brand", "aspect", "voice", "topic", "length_bucket"]


def _perf_score(m):
    """A single 0..1 desirability for a video.
    Prefers REAL performance (retention/CTR) when present; else falls back to QA."""
    perf = m.get("performance") or {}
    # Real-world signal (only when ingested). Retention 0..1, CTR 0..1 typical.
    if perf:
        ret = perf.get("retention")          # avg view fraction 0..1
        ctr = perf.get("ctr")                # 0..1
        if ret is not None or ctr is not None:
            r = float(ret) if ret is not None else 0.5
            c = float(ctr) if ctr is not None else 0.05
            return max(0.0, min(1.0, 0.7 * r + 0.3 * min(c / 0.1, 1.0)))
    # Fallback: internal QA score (0..100) — honest proxy until metrics exist.
    q = (m.get("quality") or {}).get("score")
    return (q / 100.0) if isinstance(q, (int, float)) else 0.5


def _now_iso():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def rebuild(workspace_dir=None, write=True):
    """Aggregate all manifests → ledger dict. Writes ledger.json + _performance.json."""
    manifests = pm.scan(workspace_dir)
    has_real = any((m.get("performance") or {}) for m in manifests)

    dims = {d: defaultdict(lambda: {"n": 0, "score_sum": 0.0, "qa_pass": 0,
                                    "qa_sum": 0.0, "views_sum": 0}) for d in DIMENSIONS}
    for m in manifests:
        s = _perf_score(m)
        var = m.get("variant") or {}
        qa = (m.get("quality") or {}).get("score") or 0
        qpass = 1 if (m.get("quality") or {}).get("pass") else 0
        views = (m.get("performance") or {}).get("views") or 0
        for d in DIMENSIONS:
            key = var.get(d) or "unknown"
            cell = dims[d][key]
            cell["n"] += 1
            cell["score_sum"] += s
            cell["qa_sum"] += qa
            cell["qa_pass"] += qpass
            cell["views_sum"] += views

    ledger = {"generated": _now_iso(), "total_videos": len(manifests),
              "signal": "real+qa" if has_real else "qa-only", "dimensions": {}}
    for d in DIMENSIONS:
        rows = {}
        for key, c in dims[d].items():
            n = c["n"] or 1
            rows[key] = {
                "n": c["n"],
                "avg_score": round(c["score_sum"] / n, 4),
                "avg_qa": round(c["qa_sum"] / n, 1),
                "qa_pass_rate": round(c["qa_pass"] / n, 3),
                "views_total": c["views_sum"],
            }
        ledger["dimensions"][d] = dict(sorted(rows.items(),
                                              key=lambda kv: -kv[1]["avg_score"]))

    # Template selection weights (softmax-ish: winners weighted up, min floor so
    # exploration never dies). Only over templates actually seen.
    tmpl = ledger["dimensions"].get("template", {})
    weights = {}
    if tmpl:
        floor = 0.15
        scores = {k: v["avg_score"] for k, v in tmpl.items() if k != "unknown"}
        if scores:
            lo, hi = min(scores.values()), max(scores.values())
            span = (hi - lo) or 1.0
            for k, sc in scores.items():
                weights[k] = round(floor + (1 - floor) * (sc - lo) / span, 3)

    if write:
        os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump(ledger, f, ensure_ascii=False, indent=2)
        os.makedirs(os.path.dirname(WEIGHTS_PATH), exist_ok=True)
        with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
            json.dump({"generated": ledger["generated"], "signal": ledger["signal"],
                       "weights": weights,
                       "note": "Template selection weights from factory_ledger. "
                               "Higher = produce more; floor 0.15 keeps exploration alive."},
                      f, ensure_ascii=False, indent=2)
    ledger["template_weights"] = weights
    return ledger


def top(dimension="template", n=5, workspace_dir=None):
    """Quick read: the n best-performing values of a dimension."""
    led = rebuild(workspace_dir, write=False)
    rows = led["dimensions"].get(dimension, {})
    return list(rows.items())[:n]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Rebuild the factory learning ledger")
    ap.add_argument("--dim", help="just print the top of this dimension")
    ap.add_argument("--n", type=int, default=5)
    a = ap.parse_args()
    if a.dim:
        for k, v in top(a.dim, a.n):
            print(f"{k}: {v}")
    else:
        led = rebuild()
        print(f"[ledger] {led['total_videos']} videos · signal={led['signal']}")
        print(f"[ledger] -> {LEDGER_PATH}")
        print(f"[ledger] template weights: {led['template_weights']}")
