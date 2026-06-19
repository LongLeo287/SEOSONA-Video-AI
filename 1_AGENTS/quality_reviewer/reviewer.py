"""
Quality Reviewer Agent — Pre-publish quality gate for SEOSONA Video Factory.
Runs quality_scorer and decides whether a video is ready for publishing.
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def review_video(video_path, brand="seosona", expected_duration=None, auto_pass_threshold=80):
    """
    Reviews a rendered video and returns a publish recommendation.

    Args:
        video_path: Path to the rendered .mp4
        brand: "seosona" or "cqa"
        expected_duration: Expected duration in seconds (optional)
        auto_pass_threshold: Score above this auto-passes (default 80)

    Returns:
        dict with recommendation ("PUBLISH", "REVIEW", "REJECT"), score, and details
    """
    from importlib import import_module
    scorer = import_module('4_BRAIN.quality_scorer')

    print(f"[Quality Reviewer] Reviewing: {os.path.basename(video_path)}")
    print(f"[Quality Reviewer] Brand: {brand} | Threshold: {auto_pass_threshold}")

    result = scorer.score_video(video_path, expected_duration=expected_duration, brand=brand)

    score = result.get("score", 0)
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    # Decision logic
    if errors:
        recommendation = "REJECT"
        reason = f"Critical errors found: {'; '.join(errors)}"
    elif score >= auto_pass_threshold:
        recommendation = "PUBLISH"
        reason = f"Score {score}/100 exceeds auto-pass threshold ({auto_pass_threshold})"
    elif score >= 60:
        recommendation = "REVIEW"
        reason = f"Score {score}/100 — manual review recommended. Warnings: {'; '.join(warnings)}"
    else:
        recommendation = "REJECT"
        reason = f"Score {score}/100 is below minimum quality (60)"

    review_result = {
        "recommendation": recommendation,
        "reason": reason,
        "score": score,
        "brand": brand,
        "checks": result.get("checks", {}),
        "errors": errors,
        "warnings": warnings,
    }

    icon = {"PUBLISH": "V", "REVIEW": "?", "REJECT": "X"}.get(recommendation, "?")
    print(f"[Quality Reviewer] [{icon}] {recommendation} — {reason}")

    return review_result


def batch_review(project_dir, brand="seosona"):
    """
    Finds and reviews all .mp4 files in a project directory.
    """
    results = []
    for f in os.listdir(project_dir):
        if f.endswith(".mp4"):
            video_path = os.path.join(project_dir, f)
            result = review_video(video_path, brand=brand)
            results.append(result)
    return results
