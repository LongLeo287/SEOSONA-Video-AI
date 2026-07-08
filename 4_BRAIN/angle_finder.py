# -*- coding: utf-8 -*-
"""4-angle topic ideation (pattern from Agent-Field/reels-af, Apache-2.0).

Most video topics get a cliché treatment. This generates 4 DIVERSE angles for a topic — each from a
different lens — rejects clichés, and recommends the strongest. Fills the "variant / angle discovery"
gap in the autonomous-factory north-star (mine the SRT/repo corpus for non-obvious angles).

REAL-LLM only (free Ollama or a key) — returns None without one, so callers keep their default flow.
Output: {"angles": [{lens, headline, hook, why}], "recommended": <index>}.
"""
from importlib import import_module

LENSES = [
    ("named-figure", "gắn với một case/nhân vật/doanh nghiệp cụ thể"),
    ("reversal", "đảo ngược một niềm tin phổ biến (điều ai cũng tin là sai)"),
    ("temporal", "theo thời gian / xu hướng sắp tới / điều sắp thay đổi"),
    ("cross-domain", "ẩn dụ liên ngành (giải thích SEO bằng thứ khác)"),
]

# AI-slop / clickbait clichés to avoid (aligns with the stop-slop skill + content_moderation)
CLICHES = ["trong thời đại số", "không thể phủ nhận", "bí quyết", "điều bạn cần biết",
           "thay đổi cuộc chơi", "đột phá", "x lý do", "bạn sẽ bất ngờ", "delve into"]

SYSTEM = (
    "Bạn là chuyên gia ý tưởng video ngắn SEO/Marketing cho SEOSONA (đối tượng B2B Việt). "
    "Cho 1 chủ đề, tạo ĐÚNG 4 góc tiếp cận KHÁC NHAU, mỗi góc theo một lăng kính cho sẵn. "
    "TRÁNH sáo rỗng/clickbait. Mỗi góc có headline ngắn + hook 1 câu + lý do nó hấp dẫn + điểm mới (0-10). "
    'Trả JSON: {"angles":[{"lens":"...","headline":"...","hook":"...","why":"...","novelty":int}]}'
)


def _llm_ready():
    try:
        sw = import_module("scene_writer")
        return sw._real_llm_available()
    except Exception:
        return False


def _has_cliche(text):
    t = (text or "").lower()
    return any(c in t for c in CLICHES)


def find_angles(topic):
    """Return {angles, recommended} for a topic, or None if no real LLM is available."""
    if not _llm_ready():
        return None
    try:
        llm = import_module("llm_engine")
        lenses = "\n".join(f"- {k}: {d}" for k, d in LENSES)
        user = f"Chủ đề: {topic}\n\nLăng kính (mỗi góc dùng 1):\n{lenses}"
        out = llm.generate_json_strict(SYSTEM, user, require_key="angles")   # robust cascade
        angles = out.get("angles") if isinstance(out, dict) else None
        if not (isinstance(angles, list) and angles):
            return None
        # drop cliché headlines/hooks, then recommend the highest-novelty survivor
        clean = [a for a in angles if isinstance(a, dict)
                 and not (_has_cliche(a.get("headline")) or _has_cliche(a.get("hook")))]
        pool = clean or angles

        def _novelty(a):
            # per-item safe: one malformed novelty (a float-string "4.5", text, or a non-dict angle) must not
            # raise and discard the WHOLE result — score it 0 so the good angles survive.
            try:
                return int(float(a.get("novelty", 0) or 0)) if isinstance(a, dict) else 0
            except (TypeError, ValueError):
                return 0
        best = max(range(len(pool)), key=lambda i: _novelty(pool[i]))
        return {"angles": pool, "recommended": best}
    except Exception:
        return None


if __name__ == "__main__":
    import sys, json
    topic = sys.argv[1] if len(sys.argv) > 1 else "Công cụ SEO cho người mới"
    r = find_angles(topic)
    if not r:
        print("[angle-finder] no real LLM (set a key or start Ollama) — returning nothing.")
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))
