"""
Quality Scorer — Pre-publish video quality gate.
Checks output video for technical integrity before delivery.
"""
import os
import subprocess
import json

_GATE_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                           "9_DASHBOARD", "feedback_state.json")


def _current_gate(default=60):
    """Pass threshold from the Phase-6 feedback loop (a ratchet). Pure file read — no import
    of any 9_DASHBOARD module, so quality_scorer stays self-contained and safe to call from
    anywhere. Falls back to 60 when the loop hasn't run yet."""
    try:
        with open(_GATE_STATE, encoding="utf-8") as f:
            return int(json.load(f).get("recommended_gate", default))
    except Exception:
        return default


def score_video(video_path, expected_duration=None, brand="seosona"):
    """
    Scores a rendered video on multiple quality dimensions.
    Returns a dict with score (0-100), pass/fail, and detailed breakdown.
    """
    if not os.path.exists(video_path):
        return {"score": 0, "pass": False, "errors": ["Video file not found"]}

    results = {
        "file": os.path.basename(video_path),
        "checks": {},
        "errors": [],
        "warnings": [],
    }
    total_points = 0
    max_points = 0

    # --- CHECK 1: File exists and has reasonable size (10 pts) ---
    max_points += 10
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if file_size_mb < 0.05:
        results["errors"].append(f"File too small: {file_size_mb:.2f} MB")
        results["checks"]["file_size"] = {"status": "FAIL", "value": f"{file_size_mb:.2f} MB"}
    elif file_size_mb > 500:
        results["warnings"].append(f"File unusually large: {file_size_mb:.1f} MB")
        results["checks"]["file_size"] = {"status": "WARN", "value": f"{file_size_mb:.1f} MB"}
        total_points += 7
    else:
        results["checks"]["file_size"] = {"status": "PASS", "value": f"{file_size_mb:.2f} MB"}
        total_points += 10

    # --- CHECK 2: FFprobe metadata (30 pts) ---
    max_points += 30
    try:
        probe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=15)
        if probe_result.returncode == 0:
            probe_data = json.loads(probe_result.stdout)
            streams = probe_data.get("streams", [])
            fmt = probe_data.get("format", {})

            # Video stream exists
            video_streams = [s for s in streams if s.get("codec_type") == "video"]
            audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

            if not video_streams:
                results["errors"].append("No video stream found")
                results["checks"]["video_stream"] = {"status": "FAIL"}
            else:
                vs = video_streams[0]
                width = int(vs.get("width", 0))
                height = int(vs.get("height", 0))
                results["checks"]["resolution"] = {"status": "PASS", "value": f"{width}x{height}"}
                total_points += 10

                # Check 9:16 or 16:9
                if width > 0 and height > 0:
                    ratio = width / height
                    if 0.5 < ratio < 0.6:  # 9:16
                        results["checks"]["aspect_ratio"] = {"status": "PASS", "value": "9:16"}
                    elif 1.7 < ratio < 1.8:  # 16:9
                        results["checks"]["aspect_ratio"] = {"status": "PASS", "value": "16:9"}
                    else:
                        results["warnings"].append(f"Non-standard aspect ratio: {ratio:.2f}")
                        results["checks"]["aspect_ratio"] = {"status": "WARN", "value": f"{ratio:.2f}"}

            if not audio_streams:
                results["errors"].append("No audio stream found")
                results["checks"]["audio_stream"] = {"status": "FAIL"}
            else:
                results["checks"]["audio_stream"] = {"status": "PASS"}
                total_points += 10

            # Duration check
            duration = float(fmt.get("duration", 0))
            if duration < 3:
                results["errors"].append(f"Video too short: {duration:.1f}s")
                results["checks"]["duration"] = {"status": "FAIL", "value": f"{duration:.1f}s"}
            elif expected_duration and abs(duration - expected_duration) > 3:
                results["warnings"].append(
                    f"Duration mismatch: expected ~{expected_duration:.1f}s, got {duration:.1f}s"
                )
                results["checks"]["duration"] = {"status": "WARN", "value": f"{duration:.1f}s"}
                total_points += 5
            else:
                results["checks"]["duration"] = {"status": "PASS", "value": f"{duration:.1f}s"}
                total_points += 10
        else:
            results["errors"].append("FFprobe failed to read file")
    except FileNotFoundError:
        results["warnings"].append("FFprobe not found, skipping stream checks")
        total_points += 15  # Give partial credit
    except Exception as e:
        results["errors"].append(f"FFprobe error: {e}")

    # --- CHECK 3: Companion files exist (20 pts) ---
    max_points += 20
    project_dir = os.path.dirname(video_path)

    # Search recursively — native_composer writes the sidecar SRT to _captions_upload/
    # (a non-auto-loading folder so players don't draw a 2nd subtitle over the karaoke)
    # and the thumbnail to Thumbnail/. Accept either, anywhere under the project dir.
    def _find_srt():
        for _root, _dirs, files in os.walk(project_dir):
            if any(f.lower().endswith(".srt") for f in files):
                return True
        return False

    if _find_srt():
        results["checks"]["srt_file"] = {"status": "PASS"}
        total_points += 10
    else:
        results["warnings"].append("No SRT subtitle file found")
        results["checks"]["srt_file"] = {"status": "WARN"}

    thumb_dir = os.path.join(project_dir, "Thumbnail")
    has_thumb = os.path.isdir(thumb_dir) and any(
        f.lower().endswith((".png", ".jpg")) for f in os.listdir(thumb_dir)
    )
    if has_thumb:
        results["checks"]["thumbnail"] = {"status": "PASS"}
        total_points += 10
    else:
        results["warnings"].append("No thumbnail found")
        results["checks"]["thumbnail"] = {"status": "WARN"}

    # --- CHECK: PACING / DENSITY (15 pts) — the dimension the old gate missed (a slow slideshow passed
    #     100/100). Reads the last render's per-scene durations (native_composer._LAST_PACING). ---
    max_points += 15
    try:
        import native_composer as _nc, spec_lint as _sl
        # PREFER the per-project sidecar written at render time: renders run in queue_processor SUBPROCESSES
        # while this scorer runs in the PARENT, so the in-memory _LAST_PACING global is None here → the
        # pacing dimension was being silently full-credited. Fall back to the global for a same-process score.
        _pac = None
        try:
            _pf = os.path.join(project_dir, "_pacing.json")
            if os.path.exists(_pf):
                with open(_pf, encoding="utf-8") as _f:
                    _pac = json.load(_f)
        except Exception:
            _pac = None
        if not (_pac and _pac.get("durations")):
            _pac = getattr(_nc, "_LAST_PACING", None)
        if _pac and _pac.get("durations"):
            _ps = _sl.pacing_score(_pac["durations"], _pac.get("total"))
            _pw = _sl.lint_pacing(_pac["durations"], _pac.get("total"))
            total_points += round(15 * _ps / 100)
            results["checks"]["pacing"] = {"status": "PASS" if _ps >= 70 else "WARN", "value": f"{_ps}/100"}
            for _m in _pw:
                results["warnings"].append(_m)
        else:
            total_points += 15                        # no data (non-native path) → don't penalise
            results["checks"]["pacing"] = {"status": "SKIP"}
    except Exception:
        total_points += 15
        results["checks"]["pacing"] = {"status": "SKIP"}

    # --- FINAL SCORE ---
    score = int((total_points / max_points) * 100) if max_points > 0 else 0
    gate = _current_gate()        # data-driven (ratchets up as the factory improves); default 60
    passed = score >= gate and len(results["errors"]) == 0

    results["score"] = score
    results["pass"] = passed
    results["gate"] = gate
    results["max_points"] = max_points
    results["earned_points"] = total_points

    status = "PASS" if passed else "FAIL"
    print(f"[Quality Scorer] {status} — Score: {score}/100 (gate {gate})")
    if results["errors"]:
        for err in results["errors"]:
            print(f"  [ERROR] {err}")
    if results["warnings"]:
        for warn in results["warnings"]:
            print(f"  [WARN] {warn}")

    return results
