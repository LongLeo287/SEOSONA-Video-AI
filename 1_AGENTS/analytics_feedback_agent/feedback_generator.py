# -*- coding: utf-8 -*-
"""Analytics Feedback Agent — post-mortem + improvement proposals.

RE-GROUNDED 2026-06-29: the old version read a `state` dict from `EVALUATE_NODE`,
a node of the Supergraph that was RETIRED when the engine moved to video_engine.py
(it never ran anymore). It now reads from the produced project's
`production_manifest.json` (+ quality_scorer result), which IS the new engine's
output. The old `state`-dict signature still works (back-compat shim) so any legacy
caller keeps functioning.

LEARN stage of 6_SOP/AUTONOMOUS_FACTORY_LOOP.md.
"""
import os, sys, json, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "3_MEMORY" / "reports"
sys.path.insert(0, str(PROJECT_ROOT / "4_BRAIN"))


def _proposals(score, errors, warnings, fatal_error):
    """Turn QA signals into concrete, actionable improvement proposals."""
    out = []
    if fatal_error:
        out.append({"target": "video_engine", "issue": f"Fatal error: {fatal_error}",
                    "action": "Inspect the project log; add/inspect exception handling around the failing stage."})
    w = str(warnings)
    if "aspect" in w.lower():
        out.append({"target": "template/aspect", "issue": "Non-standard aspect ratio detected.",
                    "action": "Set aspect explicitly (9:16 / 16:9) in the template or --aspect."})
    if "duration" in w.lower():
        out.append({"target": "scene planner", "issue": "Duration drifted from target.",
                    "action": "Tune segment count / pacing (MAX_WPM) so the video lands in its length bucket."})
    if "thumbnail" in w.lower():
        out.append({"target": "thumbnail step", "issue": "No thumbnail produced.",
                    "action": "Verify the frame-grab thumbnail step ran (Thumbnail/thumbnail.png)."})
    if "srt" in w.lower() or "subtitle" in w.lower():
        out.append({"target": "captions", "issue": "No sidecar SRT found.",
                    "action": "Confirm _captions_upload/<name>_cc.srt is written."})
    if not out and (score or 0) >= 80:
        out.append({"target": "none", "issue": "Clean run.", "action": "Maintain current configuration."})
    elif not out:
        out.append({"target": "quality", "issue": f"Score {score} below target.",
                    "action": "Review the QA breakdown in the manifest; address the lowest-scoring check."})
    return out


def _from_manifest(project_dir):
    """Build a state-like dict from a produced project's manifest + QA."""
    import production_manifest as pm
    import quality_scorer
    m = pm.load(project_dir) or {}
    mp4 = (m.get("outputs") or {}).get("mp4")
    q = {}
    if mp4:
        ap = os.path.join(project_dir, mp4)
        if os.path.exists(ap):
            q = quality_scorer.score_video(ap, brand=(m.get("variant") or {}).get("brand", "seosona"))
    return {
        "name": m.get("video_id") or os.path.basename(project_dir),
        "project_dir": project_dir,
        "quality_score": q.get("score", (m.get("quality") or {}).get("score", 0)),
        "quality_errors": q.get("errors", []),
        "quality_warnings": q.get("warnings", []),
        "ooda_retries": 0,
        "error": None,
        "variant": m.get("variant", {}),
    }


def generate_post_mortem(state_or_dir):
    """Generate a post-mortem report.

    Accepts EITHER a produced project_dir (str — the new path) OR a legacy `state`
    dict (back-compat). Writes JSON (machine, centralised) + Markdown (human, in the
    project dir). Returns the report dict.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(state_or_dir, (str, os.PathLike)):
        state = _from_manifest(str(state_or_dir))
    else:
        state = state_or_dir or {}

    project_name = state.get("name", "Unknown_Project")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = f"{project_name}_{timestamp}"
    score = state.get("quality_score", 0)
    errors = state.get("quality_errors", [])
    warnings = state.get("quality_warnings", [])
    retries = state.get("ooda_retries", 0)
    fatal_error = state.get("error", None)

    proposals = _proposals(score, errors, warnings, fatal_error)
    report_data = {
        "report_id": report_id, "project_name": project_name, "timestamp": timestamp,
        "quality_score": score, "status": "FAILED" if fatal_error or errors else "PASS",
        "variant": state.get("variant", {}),
        "errors": errors, "warnings": warnings, "proposals": proposals,
    }

    with open(REPORTS_DIR / f"{report_id}.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)

    project_dir = state.get("project_dir")
    md_path = (Path(project_dir) / "Bao_cao_chat_luong.md") if project_dir and os.path.exists(project_dir) \
        else (REPORTS_DIR / f"{report_id}_Bao_cao_chat_luong.md")
    md = f"# 📊 Báo cáo Chất lượng: {project_name}\n\n"
    md += f"**Thời gian:** {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
    md += f"**Trạng thái:** {'❌ THẤT BẠI' if fatal_error or errors else '✅ THÀNH CÔNG'}\n"
    md += f"**Điểm chất lượng:** {score}/100\n"
    if state.get("variant"):
        md += f"**Variant:** {json.dumps(state['variant'], ensure_ascii=False)}\n"
    md += "\n## 💡 Đề xuất cải tiến\n"
    for i, p in enumerate(proposals, 1):
        md += f"{i}. **{p['target']}** — {p['issue']}\n   → {p['action']}\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[Analytics Agent] report JSON: {REPORTS_DIR / (report_id + '.json')}")
    print(f"[Analytics Agent] report MD:   {md_path}")
    return report_data


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Generate a post-mortem from a produced project dir")
    ap.add_argument("project_dir")
    a = ap.parse_args()
    generate_post_mortem(a.project_dir)
