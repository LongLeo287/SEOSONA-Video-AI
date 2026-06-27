"""
Analytics Feedback Agent
Receives data from EVALUATE_NODE, analyzes quality scores and OODA retries,
and generates actionable proposals in both JSON and Markdown formats.
"""
import os
import json
import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "3_MEMORY" / "reports"

def generate_post_mortem(state):
    """
    Generates a post-mortem report from the graph state.
    """
    if not REPORTS_DIR.exists():
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    project_name = state.get("name", "Unknown_Project")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = f"{project_name}_{timestamp}"
    
    # Extract data from state
    score = state.get("quality_score", 0)
    errors = state.get("quality_errors", [])
    warnings = state.get("quality_warnings", [])
    retries = state.get("ooda_retries", 0)
    fatal_error = state.get("error", None)

    # 1. AI Logic for Actionable Proposals (Simulated for MVP)
    proposals = []
    
    if fatal_error:
        proposals.append({
            "target": "System Workflow",
            "issue": f"Fatal error occurred: {fatal_error}",
            "action": "Check logs and add exception handling in video_engine.py."
        })
        
    if retries > 0:
        proposals.append({
            "target": "OODA Loop Config",
            "issue": f"System had to auto-correct {retries} times during production.",
            "action": "Investigate EditorAgent scene lengths. Consider adjusting `max_scene_duration` in system_config.yaml."
        })
        
    if "Scene is too long" in str(warnings):
        proposals.append({
            "target": "Script Writer Agent",
            "issue": "Scenes generated are too lengthy.",
            "action": "Update `max_words_per_sentence` from 30 to 20 in prompt templates."
        })

    if not proposals and score >= 80:
        proposals.append({
            "target": "None",
            "issue": "Pipeline ran smoothly.",
            "action": "Maintain current configurations."
        })

    # 2. Build JSON Data
    report_data = {
        "report_id": report_id,
        "project_name": project_name,
        "timestamp": timestamp,
        "quality_score": score,
        "status": "FAILED" if fatal_error or errors else "PASS",
        "ooda_retries": retries,
        "errors": errors,
        "warnings": warnings,
        "proposals": proposals
    }

    # 3. Export JSON for Machine Learning (Centralized)
    json_path = REPORTS_DIR / f"{report_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)

    # 4. Export Markdown for Human Editor (Bundled in Video Workspace)
    project_dir = state.get("project_dir", None)
    if project_dir and os.path.exists(project_dir):
        md_path = Path(project_dir) / "Báo_cáo_chất_lượng.md"
    else:
        # Fallback to centralized reports if project_dir is missing
        md_path = REPORTS_DIR / f"{report_id}_Báo_cáo_chất_lượng.md"

    md_content = f"# 📊 Báo cáo Kiểm định Chất lượng: {project_name}\n\n"
    md_content += f"**Ngày giờ:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_content += f"**Trạng thái:** {'❌ THẤT BẠI' if fatal_error or errors else '✅ THÀNH CÔNG'}\n"
    md_content += f"**Điểm Chất lượng (AI):** {score}/100\n"
    md_content += f"**Số lần OODA Loop tự sửa lỗi:** {retries}\n\n"
    
    if fatal_error:
        md_content += f"## 🚨 Lỗi Nghiêm Trọng (Fatal Error)\n```\n{fatal_error}\n```\n\n"
        
    md_content += "## 💡 Đề xuất Cải tiến Hệ thống\n"
    for idx, p in enumerate(proposals):
        md_content += f"{idx+1}. **Mục tiêu:** {p['target']}\n"
        md_content += f"   - **Vấn đề phát hiện:** {p['issue']}\n"
        md_content += f"   - **Hành động đề xuất:** {p['action']}\n\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[Analytics Agent] Đã xuất báo cáo JSON cho AI: {json_path}")
    print(f"[Analytics Agent] Đã xuất báo cáo Markdown cho Người: {md_path}")
    return report_data
