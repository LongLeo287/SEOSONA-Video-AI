# -*- coding: utf-8 -*-
"""SEOSONA Video — LLM scene writer (copywriting-aware).

The high-quality path for turning a topic/script into scenes, applying the craft from
`2_KNOWLEDGE/domain_skills/` (Ogilvy headlines, conversion copywriting, SEO intent, no
AI-slop). Kept SEPARATE from video_engine so neither file gets overloaded.

Runs on whatever LLM `llm_engine` can reach — FREE local Ollama (set SEOSONA_OLLAMA_MODEL)
or a cloud key — and returns None if none is available, so the caller falls back to the
deterministic planner. Vietnamese output (video content language).

  from scene_writer import write_scenes
  scenes = write_scenes("Lộ trình làm SEO thời AI")   # [{seg,h1,h2}] or None
"""
import os
import sys
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load .env so _real_llm_available() sees the keys REGARDLESS of import order (it reads env directly,
# before llm_engine — which also loads .env — is imported). Without this, a gate check before llm_engine
# import wrongly returns "no LLM" despite valid keys → silent deterministic fallback. Best-effort.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
except Exception:
    pass

# The craft is distilled here (the full skills live in 2_KNOWLEDGE/domain_skills/).
SYSTEM_PROMPT = (
    "Bạn là Scene-Composer kiêm copywriter của SEOSONA (kênh SEO/Marketing tiếng Việt). "
    "Biến nội dung người dùng thành 5–9 cảnh video dọc, áp dụng nguyên tắc viết bán hàng:\n"
    "- HOOK (Ogilvy): câu đầu hứa MỘT lợi ích cụ thể hoặc tạo tò mò — đủ mạnh để dừng lướt. "
    "Không chào hỏi, không 'hôm nay mình giới thiệu'.\n"
    "- Mỗi cảnh 1 ý, câu thoại tiếng Việt tự nhiên, ngắn gọn, có chủ ngữ + động từ mạnh.\n"
    "- KHÔNG sáo rỗng/AI-slop: tránh 'trong thời đại số', 'không thể phủ nhận', "
    "'hãy cùng khám phá', 'đóng vai trò quan trọng'.\n"
    "- KHÔNG bịa số liệu, không 'tốt nhất/số 1' nếu không có nguồn.\n"
    "- Nhắm ĐÚNG 1 ý định tìm kiếm (SEO). Cảnh cuối là CTA: theo dõi SEOSONA.\n"
    "- h1 = chủ đề (≤4 chữ), h2 = điểm nhấn (≤4 chữ).\n"
    "- KHI HỢP LÝ, dùng cấu trúc rõ để cảnh dễ minh hoạ trực quan (video sinh động hơn): "
    "so sánh 'A vs B' hoặc 'thay vì X thì Y', liệt kê 3 mục, hay nêu số liệu cụ thể — nhưng câu vẫn phải TỰ NHIÊN, không gượng.\n"
    'Trả về JSON: {"scenes":[{"seg":"câu thoại","h1":"...","h2":"..."}]}'
)


def _real_llm_available():
    """True only when a GENUINE LLM is reachable — a cloud key, or a running Ollama with a
    model set. We must NOT fall through to llm_engine's offline NLP router here: that isn't
    copywriting-aware, and the deterministic planner in video_engine is already better."""
    if os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return True
    model = os.getenv("SEOSONA_OLLAMA_MODEL")
    if not model:
        return False
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    try:
        import requests
        return requests.get(f"{host}/api/tags", timeout=3).status_code == 200
    except Exception:
        return False


def _brand_context():
    """Load the load-once brand/company context so generation is data-driven + on brand-voice
    without re-prompting (the ContentOS pattern). Returns '' if not set up."""
    p = os.path.join(ROOT, ".claude", "product-marketing-context.md")
    try:
        return open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    except Exception:
        return ""


def write_scenes(topic_or_script, min_scenes=4, max_scenes=9):
    """Return validated scene dicts from a REAL LLM (copywriting-aware + brand-context-aware),
    or None — when None, the caller uses the deterministic planner. Never uses offline NLP."""
    if not _real_llm_available():
        return None
    # UNIFIED pipeline first (script_writer: fetch→analyze→reason/angle→plan→write→VERIFY). Use its
    # output ONLY when it passes verification — one writer + one rulebook + fabrication gate. If it
    # can't produce a clean verified script, fall back to this module's proven prompt below.
    try:
        _swm = import_module("script_writer")
        _script, _vr, _ = _swm.generate_script(topic_or_script, topic=str(topic_or_script),
                                               n_scenes=min(max_scenes, 7), context=str(topic_or_script))
        if _script and _vr.ok and min_scenes <= len(_script.scenes) <= max_scenes:
            print("[scene_writer] via script_writer (verified ✓)")
            # keep the writer's component/block SUGGESTION so the render couples to its intent
            return [{"seg": s["text_vi"], "h1": s["h1"], "h2": s["h2"],
                     "comp_hint": s.get("comp_hint"), "block": s.get("block"),
                     "fx": s.get("fx")} for s in _script.scenes]
    except Exception as _e:
        print(f"[scene_writer] unified pipeline skipped ({_e})")
    ctx = _brand_context()
    user_input = (f"BRAND CONTEXT (follow strictly):\n{ctx}\n\n---\nNỘI DUNG: {topic_or_script}"
                  if ctx else str(topic_or_script))
    sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
    try:
        llm = import_module("llm_engine")
        out = llm.generate_json_strict(SYSTEM_PROMPT, user_input, require_key="scenes")   # robust cascade
    except Exception as e:
        print(f"[scene_writer] LLM call failed ({e}); deterministic fallback.")
        return None
    scenes = out.get("scenes") if isinstance(out, dict) else None
    if not (isinstance(scenes, list) and min_scenes <= len(scenes) <= max_scenes):
        return None
    clean = []
    for s in scenes:
        if isinstance(s, dict) and str(s.get("seg", "")).strip():
            clean.append({"seg": str(s["seg"]).strip(),
                          "h1": str(s.get("h1", "")).strip(),
                          "h2": str(s.get("h2", "")).strip()})
    return clean or None


if __name__ == "__main__":
    import json
    topic = sys.argv[1] if len(sys.argv) > 1 else "Lộ trình làm SEO thời AI"
    r = write_scenes(topic)
    print(json.dumps(r, ensure_ascii=False, indent=2) if r else "(no LLM available → deterministic planner)")
