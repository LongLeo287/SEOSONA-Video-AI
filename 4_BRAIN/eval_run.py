# -*- coding: utf-8 -*-
"""SEOSONA Video — Eval Flywheel runner (regression harness).

Adopted from google/agents-cli's eval loop: run a FIXED set of repos through the factory,
grade each with the Gemini judge (eval_judge), and write a timestamped results file. Run it
after changing the pipeline to catch regressions ("did my change make narration/brand/visuals
worse?") that the metadata gate can't see.

By default it JUDGES videos that already exist under 8_WORKSPACE/<name> (cheap, no GPU). Pass
--render to (re)render any missing one first (uses the GPU + Gemini script path).

    python 4_BRAIN/eval_run.py                 # judge existing videos in the eval set
    python 4_BRAIN/eval_run.py --render        # render missing ones, then judge all

Results → 3_MEMORY/eval_results/results_<ts>.json  (+ a printed summary).
"""
import os
import sys
import json
import glob
import time
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import eval_judge

DATASET = os.path.join(ROOT, "1_CONFIG", "eval_datasets", "news_eval.json")   # tracked input
RESULTS_DIR = os.path.join(ROOT, "3_MEMORY", "eval_results")                  # runtime output (gitignored)


def _find_mp4(project_dir):
    for p in glob.glob(os.path.join(project_dir, "*.mp4")):
        if not os.path.basename(p).startswith("_") and "_raw" not in os.path.basename(p):
            return p
    return None


def run(dataset_path=DATASET, render_missing=False):
    cases = json.load(open(dataset_path, encoding="utf-8")).get("cases", [])
    results = []
    for c in cases:
        name = c.get("id") or c["url"].rstrip("/").split("/")[-1]
        proj = os.path.join(ROOT, "8_WORKSPACE", name)
        mp4 = _find_mp4(proj)
        if not mp4 and render_missing:
            print(f"[eval_run] rendering {name} …")
            try:
                import make_video
                mp4 = make_video.make(c["url"])
            except Exception as e:
                print(f"[eval_run] render failed for {name}: {e}")
        if not mp4:
            results.append({"id": name, "skipped": True, "reason": "no video (use --render)"})
            continue
        print(f"[eval_run] judging {name} …")
        v = eval_judge.judge(mp4)
        results.append({"id": name, **v})

    ts = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, f"results_{ts}.json")
    json.dump({"ts": ts, "results": results}, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    graded = [r for r in results if "overall" in r]
    passed = [r for r in graded if r.get("pass")]
    print("\n================ EVAL FLYWHEEL SUMMARY ================")
    for r in results:
        if "overall" in r:
            tag = "✅" if r["pass"] else "⚠"
            print(f"  {tag} {r['id']:24s} {r['overall']}/5" + (f"  weak={r['weak']}" if r.get("weak") else ""))
        else:
            print(f"  – {r['id']:24s} skipped ({r.get('reason','')})")
    if graded:
        avg = round(sum(r["overall"] for r in graded) / len(graded), 2)
        print(f"  ----\n  graded {len(graded)} | pass {len(passed)}/{len(graded)} | avg {avg}/5")
    print(f"  results → {os.path.relpath(out_path, ROOT)}")
    print("======================================================")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SEOSONA Eval Flywheel — grade the eval set")
    ap.add_argument("--render", action="store_true", help="render any missing video before judging")
    ap.add_argument("--dataset", default=DATASET)
    a = ap.parse_args()
    run(a.dataset, render_missing=a.render)
