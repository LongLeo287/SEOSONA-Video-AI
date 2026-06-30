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
    """Extract n frames evenly across the clip (downscaled) for the judge."""
    ffp, ffm = nc._ffprobe_bin(), nc._ffmpeg_bin()
    try:
        r = subprocess.run([ffp, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", video], capture_output=True, text=True, timeout=20)
        dur = float((r.stdout or "0").strip() or 0)
    except Exception:
        dur = 0.0
    if dur < 1:
        return []
    tmp = tempfile.mkdtemp(prefix="evaljudge_")
    out = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        p = os.path.join(tmp, f"f{k}.png")
        subprocess.run([ffm, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                        "-i", video, "-frames:v", "1", "-vf", "scale=540:-1", p],
                       capture_output=True, timeout=30)
        if os.path.exists(p):
            out.append(p)
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


def _agent_review_dump(video_path, frames, narration):
    """Last resort when BOTH Gemini and local Ollama are unavailable: persist the frames +
    narration + rubric so the CODING AGENT (Claude) can grade them IN-SESSION (the user's
    standing rule: 'if Gemini is out of quota, you or a local LLM handle it'). Returns the
    request dir. The agent then Reads the frames and writes the verdict."""
    import shutil
    d = os.path.join(ROOT, "3_MEMORY", "eval_results", "agent_review",
                     os.path.splitext(os.path.basename(video_path))[0])
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


def judge(video_path):
    """Grade one rendered video qualitatively. Chain: Gemini vision → local Ollama vision →
    agent-review dump (Claude grades in-session). Returns a verdict dict (always graceful)."""
    if not video_path or not os.path.exists(video_path):
        return {"skipped": True, "reason": "file not found"}
    frames = _frames(video_path)
    if not frames:
        return {"skipped": True, "reason": "no frames extracted"}
    narration = _narration(video_path)
    res = _judge_gemini(frames, narration) or _judge_ollama(frames, narration)
    if not res or "scores" not in res:
        # Both cloud + local LLM unavailable → hand to the coding agent (user's rule).
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
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python 4_BRAIN/eval_judge.py <video.mp4>")
        sys.exit(1)
    v = judge(sys.argv[1])
    print(json.dumps(v, ensure_ascii=False, indent=2))
    sys.exit(0)
