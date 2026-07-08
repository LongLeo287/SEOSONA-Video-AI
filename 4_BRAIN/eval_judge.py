# -*- coding: utf-8 -*-
"""SEOSONA Video — Gemini-as-judge qualitative QA.

Adopted from google/agents-cli's "Quality Flywheel" eval (free/local-only, via Gemini
vision). Scores what ffprobe / quality_scorer / evaluator CANNOT: Vietnamese narration
quality, brand fit, visual variety, coherence, on-screen readability. It extracts a few
REAL frames + the narration and asks Gemini to grade against a rubric.

    from eval_judge import judge
    v = judge("8_WORKSPACE/n8n/n8n - SEOSONA.mp4")
    # -> {"overall": 4.2, "pass": True, "scores": {...}, "notes": [...], "weak": [...]}

Degrades gracefully: no GEMINI_API_KEY / vision error → {"skipped": True, ...} (never blocks
a render — it's an extra QUALITATIVE dimension beside the metadata gate, not a hard gate).

CLI:  python 4_BRAIN/eval_judge.py "<video.mp4>"
"""
import os
import sys
import json
import glob
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
except Exception:
    pass
import native_composer as nc

PASS_THRESHOLD = 3.6   # mean of the 5 dims; any single dim <=2 also fails (hard issue)

# The qualitative rubric — exactly the things metadata can't see (and that we kept
# hitting by ear this session: English dumps, slug spam, draggy/garbled voice, overflow).
DIMENSIONS = {
    "narration_vn": "Lời đọc tiếng Việt tự nhiên, KHÔNG nhồi tiếng Anh thô, KHÔNG lặp slug repo, không lỗi/khó hiểu",
    "brand_fit":    "Đúng brand SEOSONA: nền SÁNG (light mode), màu xanh #2A5BDA / cam #E2724D, chuyên nghiệp",
    "visual_variety": "Các cảnh đa dạng (component khác nhau: số, bảng, ảnh thật, list), không lặp đơn điệu",
    "coherence":    "Mạch nội dung hợp lý: mở (hook) → thân → kêu gọi theo dõi (CTA)",
    "readability":  "Chữ trên màn vừa khung (không tràn/cụt), phụ đề dễ đọc",
}


def _frames(video, n=4):
    """Extract n REVEALED frames across the clip (downscaled) for the judge. Each of the n segments
    is sampled at a few points in its LATER half (skipping the entrance, where reveal animations
    aren't done yet) and the highest-CONTENT candidate is kept (frame_scorer sharp+entropy). This
    fixes the judge catching a scene at its transition/pre-reveal moment (an entrance frame shows an
    empty heading → the judge wrongly scored visual_variety/readability down for a fully-good scene)."""
    ffp, ffm = nc._ffprobe_bin(), nc._ffmpeg_bin()
    try:
        r = subprocess.run([ffp, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", video], capture_output=True, text=True, timeout=20)
        dur = float((r.stdout or "0").strip() or 0)
    except Exception:
        dur = 0.0
    if dur < 1:
        return []
    try:                                            # reuse the cover-frame scorer (no duplication)
        sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "thumbnail_maker"))
        import frame_scorer as _fs
    except Exception:
        _fs = None
    tmp = tempfile.mkdtemp(prefix="evaljudge_")
    seg, out = dur / n, []
    for k in range(n):
        best_p, best_s = None, -1.0
        for j, frac in enumerate((0.5, 0.68, 0.85)):      # later half of the segment → past the entrance
            t = seg * (k + frac)
            p = os.path.join(tmp, f"f{k}_{j}.png")
            subprocess.run([ffm, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                            "-i", video, "-frames:v", "1", "-vf", "scale=540:-1", p],
                           capture_output=True, timeout=30)
            if not os.path.exists(p):
                continue
            if _fs:
                sc = _fs._scores(p)                        # (sharp, entropy, luma)
                s = (sc[0] + sc[1]) if sc else 0.0         # content richness = sharp + entropy
            else:
                s = float(os.path.getsize(p))              # fallback: bigger PNG ≈ more content
            if s > best_s:
                best_s, best_p = s, p
        if best_p:
            out.append(best_p)
    return out


def _narration(video):
    """Plain narration text from the sidecar _cc.srt next to the video."""
    srts = glob.glob(os.path.join(os.path.dirname(video), "**", "*_cc.srt"), recursive=True)
    if not srts:
        return ""
    lines = [ln.strip() for ln in open(srts[0], encoding="utf-8")
             if ln.strip() and "-->" not in ln and not ln.strip().isdigit()]
    return " ".join(lines)


def _judge_gemini(frames, narration):
    """Ask Gemini (vision) to grade. Returns the parsed dict, or None on no-key / failure.
    Tries a small chain of free Flash models (each has its own quota)."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    try:
        from google import genai
        from google.genai import types
    except Exception:
        return None
    client = genai.Client(api_key=key)
    rub = "\n".join(f"- {k}: {v}" for k, v in DIMENSIONS.items())
    prompt = (
        "Bạn là giám khảo QA cho video ngắn 9:16 của kênh công nghệ SEOSONA (tiếng Việt). "
        f"Dưới đây là {len(frames)} khung hình trích đều từ video + toàn bộ lời đọc.\n\n"
        f"LỜI ĐỌC:\n{narration[:1600]}\n\n"
        "Chấm TỪNG tiêu chí 1-5 (5 = xuất sắc). Nếu tiêu chí nào < 4, thêm 1 note ngắn cụ thể:\n"
        + rub + "\n\n"
        'Chỉ trả JSON: {"scores":{"narration_vn":int,"brand_fit":int,"visual_variety":int,'
        '"coherence":int,"readability":int},"notes":["..."],"verdict":"pass"|"fail"}'
    )
    parts = [types.Part.from_text(text=prompt)]
    for fp in frames:
        parts.append(types.Part.from_bytes(data=open(fp, "rb").read(), mime_type="image/png"))
    for m in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"):
        try:
            resp = client.models.generate_content(
                model=m, contents=parts,
                config=types.GenerateContentConfig(response_mime_type="application/json"))
            return json.loads((resp.text or "").strip())
        except Exception as e:
            print(f"[eval_judge] {m} failed: {str(e)[:110]}")
    return None


def _judge_ollama(frames, narration):
    """LOCAL fallback when Gemini is down (quota/no-key). Uses an Ollama VISION model
    (set SEOSONA_OLLAMA_VISION, e.g. 'llava' or 'qwen2.5vl', + `ollama serve`). Returns the
    parsed dict, or None if not configured / unreachable."""
    model = os.getenv("SEOSONA_OLLAMA_VISION")
    if not model:
        return None
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    try:
        import base64
        import requests
        imgs = [base64.b64encode(open(f, "rb").read()).decode() for f in frames]
        rub = "\n".join(f"- {k}: {v}" for k, v in DIMENSIONS.items())
        prompt = ("Giám khảo QA video 9:16 tiếng Việt (kênh SEOSONA). Lời đọc:\n"
                  + narration[:1500] + "\n\nChấm 1-5 từng tiêu chí:\n" + rub
                  + '\nTrả JSON: {"scores":{... 5 keys ...},"notes":[],"verdict":"pass|fail"}')
        r = requests.post(f"{host}/api/chat", timeout=240, json={
            "model": model, "stream": False, "format": "json",
            "messages": [{"role": "user", "content": prompt, "images": imgs}]})
        if r.status_code == 200:
            print(f"[eval_judge] graded by LOCAL Ollama vision ({model})")
            return json.loads(r.json().get("message", {}).get("content") or "{}")
        print(f"[eval_judge] ollama HTTP {r.status_code}")
    except Exception as e:
        print(f"[eval_judge] ollama vision unavailable ({type(e).__name__})")
    return None


def _agent_review_path(video_path):
    """The stable per-video agent-review dir (frames dump + agent verdict live together)."""
    return os.path.join(ROOT, "3_MEMORY", "eval_results", "agent_review",
                        os.path.splitext(os.path.basename(video_path))[0])


def record_agent_verdict(review_dir, scores, notes=None):
    """Persist an AGENT-graded verdict (written when Gemini+Ollama are both down and the coding agent
    grades the dumped frames in-session, per the user's rule). Saved as verdict.json IN the review dir
    so a later judge()/eval_run consumes it — this is what CLOSES the flywheel OODA loop at the agent
    tier (previously the dump was write-only, so an agent grade never fed back). Same schema as judge()."""
    scores = {k: v for k, v in (scores or {}).items()}
    nums = [v for v in scores.values() if isinstance(v, (int, float))]
    overall = round(sum(nums) / len(nums), 2) if nums else 0.0
    weak = [k for k, v in scores.items() if isinstance(v, (int, float)) and v <= 2]
    verdict = {"overall": overall, "pass": bool(overall >= PASS_THRESHOLD and not weak),
               "scores": scores, "notes": list(notes or []), "weak": weak, "by": "agent"}
    try:
        os.makedirs(review_dir, exist_ok=True)
        json.dump(verdict, open(os.path.join(review_dir, "verdict.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[eval_judge] could not write agent verdict: {e}")
    return verdict


def _agent_review_dump(video_path, frames, narration):
    """Last resort when BOTH Gemini and local Ollama are unavailable: persist the frames +
    narration + rubric so the CODING AGENT (Claude) can grade them IN-SESSION (the user's
    standing rule: 'if Gemini is out of quota, you or a local LLM handle it'). Returns the
    request dir. The agent then Reads the frames and writes the verdict (record_agent_verdict)."""
    import shutil
    d = _agent_review_path(video_path)
    os.makedirs(d, exist_ok=True)
    kept = []
    for i, f in enumerate(frames):
        dst = os.path.join(d, f"frame_{i}.png")
        try:
            shutil.copy(f, dst); kept.append(dst)
        except Exception:
            pass
    json.dump({"video": video_path, "narration": narration, "frames": kept,
               "rubric": DIMENSIONS, "pass_threshold": PASS_THRESHOLD},
              open(os.path.join(d, "request.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return d


def _emit_quality(video_path, verdict):
    """Feed the QUALITATIVE eval verdict into the observability hub (obs_metrics 'quality' event) so
    feedback_loop / the OODA gate learn from it. Previously eval scores were ORPHANED — only the metadata
    quality_scorer (video_engine) reached the gate, so the dashboard's avg_score stayed null despite real
    eval verdicts. 0-5 → 0-100 to match video_engine's scale; verdict PASS/REVIEW. Best-effort, never raises."""
    try:
        ov = verdict.get("overall")
        if not isinstance(ov, (int, float)):
            return
        from importlib import import_module as _im
        sys.path.insert(0, os.path.join(ROOT, "9_DASHBOARD"))
        _im("obs_metrics").record("quality", output=os.path.basename(video_path),
                                  score=round(ov * 20, 1),
                                  verdict="PASS" if verdict.get("pass") else "REVIEW",
                                  source="eval_judge")
    except Exception:
        pass


def judge(video_path):
    """Grade one rendered video qualitatively. Chain: Gemini vision → local Ollama vision →
    agent-review dump (Claude grades in-session). Returns a verdict dict (always graceful).
    A scored verdict (Gemini OR agent-consumed) also emits an obs_metrics 'quality' event → the gate."""
    if not video_path or not os.path.exists(video_path):
        return {"skipped": True, "reason": "file not found"}
    frames = _frames(video_path)
    if not frames:
        return {"skipped": True, "reason": "no frames extracted"}
    narration = _narration(video_path)
    res = _judge_gemini(frames, narration) or _judge_ollama(frames, narration)
    if not res or "scores" not in res:
        # Before re-dumping: an AGENT verdict from a prior in-session grading CLOSES the loop — use it.
        _vp = os.path.join(_agent_review_path(video_path), "verdict.json")
        if os.path.exists(_vp):
            try:
                _v = json.load(open(_vp, encoding="utf-8"))
                if isinstance(_v, dict) and "scores" in _v:
                    for f in frames:
                        try:
                            os.remove(f)
                        except Exception:
                            pass
                    print(f"[eval_judge] ✅ using AGENT verdict — overall {_v.get('overall')}/5 "
                          f"({'PASS' if _v.get('pass') else 'REVIEW'})")
                    _emit_quality(video_path, _v)          # agent verdict → the gate (no longer orphaned)
                    return _v
            except Exception:
                pass
        # Both cloud + local LLM unavailable and no agent verdict yet → hand to the coding agent (user's rule).
        review_dir = _agent_review_dump(video_path, frames, narration)
        for f in frames:
            try:
                os.remove(f)
            except Exception:
                pass
        rel = os.path.relpath(review_dir, ROOT)
        print(f"[eval_judge] Gemini + local LLM both unavailable → AGENT REVIEW queued: {rel}")
        return {"skipped": True, "reason": "needs agent/local review", "agent_review": rel}
    for f in frames:
        try:
            os.remove(f)
        except Exception:
            pass
    scores = res["scores"]
    nums = [v for v in scores.values() if isinstance(v, (int, float))]
    overall = round(sum(nums) / len(nums), 2) if nums else 0.0
    weak = [k for k, v in scores.items() if isinstance(v, (int, float)) and v <= 2]
    passed = overall >= PASS_THRESHOLD and not weak
    out = {"overall": overall, "pass": passed, "scores": scores,
           "notes": res.get("notes", []), "weak": weak}
    print(f"[eval_judge] {'✅ PASS' if passed else '⚠ REVIEW'} — overall {overall}/5 :: "
          + ", ".join(f"{k} {v}" for k, v in scores.items()))
    if out["notes"]:
        print("           notes: " + " | ".join(str(n) for n in out["notes"][:4]))
    _emit_quality(video_path, out)                         # Gemini/Ollama verdict → the gate
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python 4_BRAIN/eval_judge.py <video.mp4>")
        sys.exit(1)
    v = judge(sys.argv[1])
    print(json.dumps(v, ensure_ascii=False, indent=2))
    sys.exit(0)
