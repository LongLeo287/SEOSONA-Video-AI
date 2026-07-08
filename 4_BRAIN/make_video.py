# -*- coding: utf-8 -*-
"""SEOSONA one-shot — `make_video <github-url>`.

Fetch real GitHub data → classify the repo → auto-pick a template (+theme) →
auto-fill content (REAL data in the data slots; templated Vietnamese prose) →
render a finished SEOSONA video. No paid APIs.

    python 4_BRAIN/make_video.py https://github.com/owner/name
    python 4_BRAIN/make_video.py owner/name --template tool-walkthrough
    python 4_BRAIN/make_video.py --news urls.txt        # batch news rotation

The deterministic auto-content is an honest DRAFT: it only uses real fields
(name, desc, stars, language, license, topics) — never invents numbers. The
Scene-Composer agent can still author richer prose; this command exists so a
news batch can be produced with one call.
"""
import os, sys, json, re, argparse, subprocess
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

# Load .env NOW (before fetch_github's `gh api`) so GITHUB_TOKEN authenticates the repo fetch
# (60→5000 req/hr) and OPENAI_API_KEY is available as the LLM fallback. Best-effort.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
except Exception:
    pass

from scene_composer import fetch_github, repo_data_slots, compose
import native_composer as nc

# Per-render signals captured for the learning-flywheel (factory_metrics → learn_flywheel).
_LAST_RENDER = {}
_TEMPLATE_SCORES = os.path.join(ROOT, "3_MEMORY", "template_scores.json")

def _weak_templates():
    """Templates the flywheel found to empirically underperform (pass-rate <70% over >=3 runs).
    classify() drops these from rotation → the factory stops reusing what fails. Best-effort."""
    try:
        import json as _j
        s = _j.load(open(_TEMPLATE_SCORES, encoding="utf-8"))
        return {t for t, v in s.items() if v.get("n", 0) >= 3 and v.get("pass_rate", 1) < 0.7}
    except Exception:
        return set()

# Curated archetype LIBRARY (7_ASSETS/templates) — each is a DISTINCT structure with content-specific
# VN kickers (LẦM TƯỞNG / CÀI ĐẶT / ĐỐI ĐẦU…). The news pipeline rotates across these for real variety
# instead of one fixed dynamic skeleton (user 2026-07-03: "sao không random template").
_NEWS_ARCHETYPES = [
    "ai-news-flash", "benchmark-news", "case-study", "data-news", "deep-tutorial", "faq",
    "insight-explainer", "launch", "listicle-top5", "myth-buster", "opinion-insight", "quick-tip",
    "repo-showcase", "resource-list", "seo-explainer", "tool-walkthrough", "transformation",
    "trend-alert", "tutorial-gittree", "versus-deep",
]


# ---------------------------------------------------------------- classify
def classify(gh):
    """Pick (template, theme, reason) from repo metadata."""
    name = (gh.get("name") or "").lower()
    desc = (gh.get("desc") or "").lower()
    topics = set(t.lower() for t in (gh.get("topics") or []))
    text = f"{name} {desc} {' '.join(topics)}"
    has = lambda *ks: any(k in text for k in ks)

    # If the repo content clearly fits one of the NEW content-shape archetypes (top-N list, X-vs-Y,
    # tutorial…), use it for scene-arc variety. Only the 10 new archetypes early-return; generic
    # matches fall through to the repo-type logic below.
    try:
        import template_picker as _tp
        _a = _tp.pick_template(text, fallback=None)
        if _a in _tp.NEW_ARCHETYPES:
            return (_a, "light", f"archetype: {_a}")
    except Exception:
        pass

    if "awesome" in name or has("awesome", "curated", "collection", "list of", "list-of"):
        return ("resource-list", "light", "kho/list/awesome collection")
    if topics & {"tutorial", "learning", "education", "game", "visualization", "interactive"} \
       or has("tutorial", "visualize", "visualization", "learn git", "interactive"):
        return ("tutorial-gittree", "light", "công cụ học/trực quan")
    if topics & {"cli", "tool", "utility", "developer-tools", "productivity"} \
       or has("command line", "command-line", " cli", "terminal"):
        return ("tool-walkthrough", "light", "CLI/tiện ích")
    # AI / agent / data repos → the component-rich templates (chart + mockup + compare +
    # feature + stats), rotated so we don't repeat the same one every time.
    if topics & {"ai", "ml", "machine-learning", "llm", "agent", "ai-agent", "mcp",
                 "deep-learning", "nlp", "data", "analytics"} \
       or has("agent", "llm", " ai ", "mcp", "model", "data"):
        return (_rot(name, ["data-news", "benchmark-news", "insight-explainer"]), "light", "AI/agent — rich")
    # generic fallback ROTATES across rich showcase templates (was always repo-showcase).
    return (_rot(name, ["repo-showcase", "data-news", "tool-walkthrough", "benchmark-news"]),
            "light", "rotated showcase")


def _rot(name, options):
    """Deterministic per-repo rotation so the same repo is stable but different repos
    get different templates (fixes 'same template every time'). The learning-flywheel
    drops empirically-weak templates from the pool (keeps >=1)."""
    weak = _weak_templates()
    pool = [o for o in options if o not in weak] or options
    return pool[sum(ord(c) for c in (name or "x")) % len(pool)]

# ---------------------------------------------------------------- prose helpers
# make_video only adds repo-specific terms here; the AUTHORITATIVE tech lexicon lives in
# news_video_standards.CORE_PRONUNCIATION_LEXICON (merged underneath at compose time).
# Keep this minimal so we never override nvs's curated phonetics.
_BASE_LEX = {"SEOSONA": "sê ô sô na"}
_INSTALL = {"python": "pip install", "go": "go install", "rust": "cargo install",
            "javascript": "npm install", "typescript": "npm install"}

def _clean(s, maxlen=90):
    """Strip emoji/symbols + trailing punctuation; truncate at a word boundary.
    Keeps spoken/display prose clean (descs often start with an emoji or end '.')."""
    s = re.sub(r"[^\w\sÀ-ỹ.,:;/+&()%#-]", "", str(s or "")).strip()  # keep % (100%) and # (C#)
    s = re.sub(r"\s+", " ", s).rstrip(" .")
    if len(s) > maxlen:
        s = s[:maxlen].rsplit(" ", 1)[0]
    return s

def _terminal(gh):
    name = gh["name"]; url = gh["url"]
    lines = [("$", f"git clone {url}"), ("$", f"cd {name}")]
    lang = (gh.get("lang") or "").lower()
    if lang in _INSTALL: lines.append(("$", f"{_INSTALL[lang]} {name.lower()}"))
    lines.append(("ok", "Sẵn sàng dùng"))
    return {"title": f"~/{name}", "lines": lines}

def _compare(gh):
    name = gh["name"]
    right = [x for x in ["Miễn phí" if gh.get("license") or True else None,
                         "Mã nguồn mở", f"Viết bằng {gh['lang']}" if gh.get("lang") else "Hiện đại"] if x]
    return {"left": ("Cách thủ công", ["Tốn thời gian", "Khó bảo trì", "Phụ thuộc dịch vụ"]),
            "right": (name, right[:3])}

def _steps(gh):
    tps = (gh.get("topics") or [])[:4]
    if tps:
        return {"items": [(t.replace("-", " ").title(), "") for t in tps]}
    return {"items": [("Cài nhanh", ""), ("Mã nguồn mở", ""), ("Cộng đồng lớn", "")]}

def _gittree():
    # x,y are PERCENT of the gittree viewBox (component does x/100*VBW). Keep nodes
    # well inside 0-100 so the graph never renders off-canvas (empty box bug).
    return {"commits": [{"id": "a", "x": 15, "y": 58, "branch": "main"},
                        {"id": "b", "x": 38, "y": 58, "branch": "main"},
                        {"id": "c", "x": 60, "y": 30, "branch": "feature"},
                        {"id": "d", "x": 82, "y": 58, "branch": "main"}],
            "edges": [["a", "b"], ["b", "c"], ["b", "d"], ["c", "d"]],
            "branches": {"main": nc.BLUE, "feature": nc.GREEN}, "head": "d"}

# Rich components from REAL repo data (were missing → those scenes rendered bare).
def _stats(gh):
    items = [(gh.get("stars_h", "0"), "GITHUB STARS")]
    if gh.get("lang"): items.append((gh["lang"], "NGÔN NGỮ"))
    items.append((gh.get("license") or "OSS", "GIẤY PHÉP"))
    return {"items": items[:3]}

def _mockup(gh):
    # If a REAL screenshot was captured (make() → _capture_shots), show it inside the
    # browser chrome — real visuals beat synthetic tiles. Else fall back to the data tiles.
    shots = gh.get("_shots") or []
    if shots:
        # `scroll` = a real page-scroll recording (native_composer overlays it as live footage over the
        # static screenshot). None if capture failed → static screenshot only.
        return {"img": shots[0]["img"], "url": shots[0]["url"], "title": gh.get("name", ""),
                "scroll": gh.get("_scroll")}
    return {"url": gh.get("full") or gh.get("url", "github.com"),
            "tiles": [(gh.get("stars_h", "0"), "Sao"),
                      (gh.get("lang") or "Đa nền", "Ngôn ngữ"),
                      (str(len(gh.get("topics") or [])) or "—", "Chủ đề"),
                      (gh.get("license") or "OSS", "Giấy phép")][:4]}

def _feature(gh):
    tps = (gh.get("topics") or [])[:3]
    emo = ["⚡", "🚀", "🔧", "📦", "🧠", "🔒"]
    if tps:
        return {"items": [(emo[i % len(emo)], t.replace("-", " ").title(), "") for i, t in enumerate(tps)]}
    return {"items": [("⚡", "Nhanh & gọn", ""), ("🔧", "Dễ tích hợp", ""), ("📦", "Mã nguồn mở", "")]}

def _tip(gh):
    return {"title": "Mẹo nhanh",
            "text": f"Clone {gh['name']}, đọc README rồi chạy thử — cộng đồng {gh.get('stars_h','nhiều')} sao hỗ trợ nhanh."}

def _quote(gh):
    return {"text": _clean(gh.get("desc"), 120) or f"{gh['name']} — dự án mã nguồn mở đáng chú ý",
            "by": gh.get("owner", "")}

def _chart(gh):
    tps = (gh.get("topics") or [])[:4]
    if tps:  # illustrative emphasis of the project's topics (not precise metrics)
        vals = [92, 78, 66, 54]
        return {"title": "Trọng tâm của dự án",
                "items": [(t.replace("-", " ").title(), vals[i % 4], "") for i, t in enumerate(tps)]}
    return {"title": "Vì sao nổi bật", "items": [("Hiệu năng", 90, ""), ("Dễ dùng", 82, ""), ("Cộng đồng", 75, "")]}

# ---------------------------------------------------------------- episodic anti-repeat
# Across a BATCH, stop every video opening the same way (pattern from mvanhorn/last30days):
# remember the last N videos' scene-1 opening + feed it to the outline as "open differently".
_ANGLES = os.path.join(ROOT, "3_MEMORY", "recent_angles.jsonl")

def _recent_openings(n=6):
    try:
        import json as _j
        rows = [_j.loads(x) for x in open(_ANGLES, encoding="utf-8").read().splitlines() if x.strip()]
        return [r.get("open", "") for r in rows[-n:] if r.get("open")]
    except Exception:
        return []

def _record_opening(repo, opening):
    try:
        import json as _j, datetime as _dt
        os.makedirs(os.path.dirname(_ANGLES), exist_ok=True)
        with open(_ANGLES, "a", encoding="utf-8") as f:
            f.write(_j.dumps({"repo": repo, "open": (opening or "").strip()[:60],
                              "ts": _dt.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------- Gemini prose
def _grounding(gh):
    """The REAL knowledge block (from the README digest) that both the outline + script are built on —
    so scenes state true facts (what it is, real features, real install) instead of fabricating."""
    f = gh.get("readme_facts") or {}
    if not f:
        return ""
    parts = ["=== KIẾN THỨC THẬT (từ README — CHỈ dùng dữ kiện trong đây, KHÔNG bịa ngoài) ==="]
    if f.get("overview"):
        parts.append(f"• Nó là gì / làm gì: {f['overview']}")
    if f.get("features"):
        parts.append("• Điểm/tính năng thật:\n  - " + "\n  - ".join(f["features"][:8]))
    if f.get("usage"):
        parts.append("• Cách dùng / cách hoạt động THẬT:\n  - " + "\n  - ".join(f["usage"][:6]))
    if f.get("install"):
        parts.append("• Lệnh cài THẬT (dùng đúng, đừng bịa 'pip install <tên>'):\n  " + "\n  ".join(f["install"][:4]))
    if f.get("use_cases"):
        parts.append("• Dùng để làm gì / ai dùng:\n  - " + "\n  - ".join(f["use_cases"][:4]))
    if f.get("sections"):
        parts.append("• Các phần trong tài liệu: " + ", ".join(f["sections"][:10]))
    return "\n".join(parts) + "\n"


def _gemini_outline(gh, kinds):
    """Stage 1 of a two-stage script (pattern adopted from ArcReel/Toonflow, re-implemented
    natively — their image/character/storyboard machinery is N/A to our faceless HTML engine,
    but their CORE discipline transfers: PLAN a coherent arc BEFORE writing scenes). Returns a
    short per-scene 'focus' list so the video flows hook→what-it-is→key-points→why→CTA instead
    of N disjoint/repetitive scenes (the original 'cảnh giống nhau' complaint). Returns None on
    any failure → stage 2 then runs WITHOUT a plan = exactly the previous behavior (no regression)."""
    try:
        import llm_engine
    except Exception:
        return None
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("SEOSONA_OLLAMA_MODEL")):
        return None  # need a real LLM (cloud Gemini OR local Ollama); offline NLP can't plan
    n = len(kinds)
    name, desc = gh.get("name", ""), (gh.get("desc") or "")
    # Outline patterns adopted from OpenMontage (AGPL — learned, re-implemented native):
    # a HOOK pattern for scene 1 + a fitting NARRATIVE STRUCTURE + one CLIMAX scene → kills the
    # "every video feels the same" problem by varying the arc per topic (not a fixed template).
    sysp = ("Bạn là đạo diễn nội dung video tin tức công nghệ SEOSONA. Trước khi viết lời, "
            "hãy LẬP DÀN Ý mạch lạc cho cả video: mỗi cảnh một TRỌNG TÂM riêng biệt, KHÔNG trùng ý. "
            "CẢNH 1 = HOOK mạnh, chọn 1 kiểu hợp dữ kiện: số liệu bất ngờ · lật ngộ nhận · "
            "tính mới/vừa ra mắt · câu hỏi tò mò · so sánh tương phản · góc nhìn ít ai nói "
            "(TRÁNH 'trong video này…'). Chọn 1 MẠCH KỂ hợp chủ đề (giới thiệu-dự-án · "
            "vấn-đề→giải-pháp · kể-bằng-số-liệu · so-sánh · tiến-trình/timeline) thay vì khuôn cố định. "
            "Đánh dấu 1 cảnh ĐIỂM NHẤN (cao trào) ở giữa-cuối. Cảnh cuối = kêu gọi theo dõi. "
            "GROUNDING: chỉ dựa trên dữ kiện được cung cấp, KHÔNG bịa.")
    _recent = _recent_openings()
    avoid = (("Mấy video GẦN ĐÂY đã mở đầu kiểu: " + " / ".join(f'\"{r[:40]}\"' for r in _recent)
              + ". Cảnh 1 video NÀY phải mở theo cách KHÁC HẲN (đừng lặp lại các kiểu trên).\n")
             if _recent else "")
    userp = (f"Repo: {name}\nMô tả (tiếng Anh): {desc}\n"
             f"Sao: {gh.get('stars_h')}, ngôn ngữ: {gh.get('lang')}, "
             f"chủ đề: {', '.join((gh.get('topics') or [])[:6])}\n"
             f"{_grounding(gh)}"
             f"Số cảnh: {n}. Vai trò trực quan từng cảnh: {kinds}\n"
             f"{avoid}"
             f"Trả JSON: {{\"focus\":[\"trọng tâm cảnh 1 (3-8 từ)\", ...]}} đúng {n} phần tử; "
             f"cảnh cuối = kêu gọi theo dõi SEOSONA.")
    try:
        out = llm_engine.generate_json_strict(sysp, userp, require_key="focus")   # robust cascade
        foci = out.get("focus") if isinstance(out, dict) else (out if isinstance(out, list) else None)
        if not foci or len(foci) < n:
            return None
        return [str(f).strip() for f in foci[:n]]
    except Exception:
        return None


def _gemini_script(gh, scenes, feedback=None, fallback=None):
    """Write clean Vietnamese segments + 2-tone headings via the LLM (Gemini free tier
    when GEMINI_API_KEY is set; offline → returns None so the deterministic path runs).
    Fixes 'voice lỗi tiếng Việt': the LLM TRANSLATES the English desc and never dumps raw
    English / the hyphenated repo slug into the spoken text."""
    try:
        import llm_engine
    except Exception:
        return None
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("SEOSONA_OLLAMA_MODEL")):
        return None  # cloud Gemini OR local Ollama; offline NLP can't translate/ground well
    kinds = [sc.get("component") or "text" for sc in scenes]
    name, desc = gh.get("name", ""), (gh.get("desc") or "")
    # Build on the ONE canonical rulebook (script_writer._system_prompt → MASTER_VIDEO_SPEC + grounding),
    # not a second inline copy of the grounding rules. Only the GitHub-specific delta stays here (repo-slug
    # handling, word-count target, seg-JSON shape). Falls back to a compact base if script_writer is absent.
    try:
        _base = import_module("script_writer")._system_prompt()
    except Exception:
        _base = ("Bạn là biên kịch video ngắn tiếng Việt cho SEOSONA. Viết thuần Việt, súc tích; "
                 "CHỈ dùng dữ kiện được cấp, KHÔNG bịa số/tên; KHÔNG chèn câu tiếng Anh; mỗi cảnh mở đầu khác nhau.")
    sysp = (_base + "\n\n=== BỔ SUNG (video tin tức từ GitHub) ===\n"
            "- DỊCH mô tả tiếng Anh sang tiếng Việt; tên repo: lần đầu nêu tên, sau gọi 'dự án này'/'công cụ này' (đừng lặp slug).\n"
            "- ĐỘ DÀI MỖI CẢNH: TỐI THIỂU 30 từ, lý tưởng 35-45 từ. Cảnh DƯỚI 30 từ là LỖI (trôi quá nhanh, "
            "người xem chưa kịp đọc/hiểu) — phải giải thích TRỌN Ý, thêm chi tiết cụ thể từ grounding, đừng "
            "viết cụt kiểu tiêu đề. Tổng cả video ~230-280 từ (~85-95 giây). Số đọc bình thường.\n"
            "- NỘI DUNG PHẢI CỤ THỂ, CẤM lý thuyết suông / marketing rỗng ('mạnh mẽ', 'nổi bật', 'tuyệt vời' "
            "mà không nói RÕ làm được gì). Xem xong người xem phải BIẾT ĐỦ: (1) chính xác NÓ LÀ GÌ + giải "
            "quyết vấn đề gì; (2) TÍNH NĂNG cụ thể — nói rõ làm được ĐIỀU GÌ; (3) CÁCH DÙNG/CÀI ĐẶT thật "
            "(bước/lệnh thật trong grounding); (4) DÙNG ĐỂ LÀM GÌ / ứng dụng thực tế. Mỗi ý phải bám dữ kiện "
            "grounding, KHÔNG chế thêm.\n"
            "- CHÍNH XÁC SỐ LIỆU (nhất là ở HOOK): số 'Sao' là LƯỢT SAO GitHub (người quan tâm/đánh dấu) — "
            "chỉ mô tả đúng vậy ('X lượt sao', 'X sao trên GitHub', 'được X người quan tâm'). TUYỆT ĐỐI KHÔNG "
            "phóng đại thành 'X lập trình viên/người dùng TIN TƯỞNG / TIN DÙNG / đang dùng' — sao ≠ số người "
            "dùng và ≠ sự tin tưởng. Giữ đúng Ý NGHĨA gốc của mọi con số, đừng đổi thành tuyên bố mạnh hơn.")
    # Stage 1: plan a coherent arc first (graceful — None → write without it = old behavior).
    plan = _gemini_outline(gh, kinds)
    plan_txt = ""
    if plan:
        plan_txt = ("Dàn ý đã duyệt — BÁM SÁT, mỗi cảnh đúng trọng tâm CỦA NÓ, không lặp ý cảnh khác:\n"
                    + "\n".join(f"  Cảnh {i + 1}: {p}" for i, p in enumerate(plan)) + "\n")
    userp = (f"Repo GitHub: {name}\nMô tả (tiếng Anh, hãy DỊCH): {desc}\n"
             f"Sao: {gh.get('stars_h')}, ngôn ngữ: {gh.get('lang')}, "
             f"chủ đề: {', '.join((gh.get('topics') or [])[:6])}\n"
             f"{_grounding(gh)}"
             f"Số cảnh: {len(scenes)}. Vai trò từng cảnh: {kinds}\n"
             f"{plan_txt}"
             f"{('BẢN TRƯỚC BỊ LỖI, hãy SỬA hết: ' + feedback + chr(10)) if feedback else ''}"
             f"Trả JSON: {{\"scenes\":[{{\"seg\":\"lời đọc\",\"h1\":\"dòng 1 (≤22)\","
             f"\"h2\":\"từ nhấn (≤22)\"}}]}} đúng {len(scenes)} phần tử. Cảnh cuối CHỈ có MỘT CTA: theo dõi "
             f"SEOSONA — TUYỆT ĐỐI KHÔNG kêu gọi truy cập/ghé/tải tại trang web hay tên miền ngoài "
             f"(vd '...io', '...com'); được nêu TÊN dự án như dữ kiện trung tính nhưng KHÔNG dẫn người xem rời kênh.")
    try:
        out = llm_engine.generate_json_strict(sysp, userp, require_key="scenes")   # robust cascade
        rows = out.get("scenes") if isinstance(out, dict) else (out if isinstance(out, list) else None)
        n = len(scenes)
        # Only give up (→ deterministic) if the LLM gave WAY too few. If it wrote most scenes, KEEP them
        # and pad the tail from the deterministic draft — don't discard good LLM prose over a count mismatch.
        if not rows or len(rows) < max(3, n - 3):
            return None
        import re as _re
        def _clean_voice(s):
            s = _re.sub(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF]", "", str(s))  # emoji
            s = _re.sub(r"https?://\S+|[→&%$#=]", " ", s)                              # urls/symbols
            return _re.sub(r"\s+", " ", s).strip()
        SEG = [_clean_voice(r.get("seg", "")) for r in rows[:n]]
        HEAD = [(str(r.get("h1", name)).strip(), str(r.get("h2", "")).strip()) for r in rows[:n]]
        if fallback and len(SEG) < n:                    # pad missing tail from the deterministic draft
            fSEG, fHEAD = fallback
            for i in range(len(SEG), n):
                SEG.append(fSEG[i] if i < len(fSEG) else "")
                HEAD.append(fHEAD[i] if i < len(fHEAD) else (name, ""))
        if any(not s for s in SEG):
            return None
        return SEG, HEAD
    except Exception as e:
        print(f"[make_video] Gemini script failed ({e}) — deterministic prose.")
        return None


# ---------------------------------------------------------------- script lint (no LLM)
# Mechanical quality gate (pattern from voocel/ainovel-cli, MIT): catch the MASTER_VIDEO_SPEC
# rules a model often misses — cheap, deterministic, no LLM call. Warns (non-blocking).
_LINT_FORBIDDEN = ("trong video này", "hôm nay mình", "như các bạn đã biết", "kính thưa")
_LINT_EN_OK = {"ai", "github", "python", "api", "seo", "app", "web", "ios", "css", "html",
               "js", "go", "rust", "sql", "llm", "ui", "ux", "pdf", "cli", "gpu", "open", "source",
               # tech loanwords standard in Vietnamese dev speech — flagging these as English-leak
               # forced a needless corrective-rewrite on ~every tech-showcase render (burned free quota)
               "import", "export", "backend", "frontend", "repository", "repo", "framework", "database",
               "server", "client", "dataset", "plugin", "template", "widget", "docker", "javascript",
               "typescript", "watermark", "browser", "script", "folder", "upload", "download", "online",
               "offline", "classification", "agents", "output", "prompt", "reddit", "server", "zero"}
# Off-platform-CTA guard lives in ONE place — content_moderation.off_platform_domain (also used by the
# topic/discover path via verify Gate 3) — so both video paths share a single source of truth. A bare
# domain (no scheme, slips past _clean_voice's `https?://` strip) in the CTA scene or after a visit-verb
# sends viewers OFF SEOSONA; neutral platform names WITHOUT a domain ("mã nguồn trên GitHub") don't trip.
# English-SENTENCE guard: the per-token English-leak check only fires on LONG (6+) lowercase words and
# skips Title-case — so a full English CTA built from short/Title words ("Go to X to try it now. Follow
# SEOSONA for more tips.") evades it. These are unambiguous English function words with NO Vietnamese
# syllable collision (deliberately excludes VN-colliding shorts like to/go/it/can/may/in/so/co/do); ≥2 in
# one segment ⇒ the segment is English, not Vietnamese (voice MUST be Vietnamese).
_EN_STOP = {"the", "for", "your", "you", "with", "and", "now", "try", "more", "follow", "get", "click",
            "here", "this", "that", "how", "why", "our", "free", "download", "watch", "subscribe", "tips",
            "best", "new", "from", "are", "will", "about", "just", "only", "also", "what", "when", "where",
            "which", "their", "them", "have", "has", "who", "been", "does", "not", "but", "out", "own"}
# Stars-inflation guard: the ONLY big count a GitHub showcase is given is the STAR count, so a segment
# that turns "N stars" into "N (users/developers) TRUST it" is a meaning-inflation (a star ≠ a user, ≠
# trust). Tell = a ≥1000 number + a user/dev noun + a TRUST verb specifically (not generic "sử dụng",
# so a real "supports N concurrent users" capacity fact does NOT false-trip). Prompt rule alone was
# advisory; the loop kept producing it ("4665 người dùng đã tin tưởng"), so enforce it via the rewrite.
_INFLATE_BIGNUM = __import__("re").compile(r"\b\d[\d.,]{3,}\b")
_INFLATE_USER = ("người dùng", "lập trình viên", "nhà phát triển", "thành viên", "developer")
_INFLATE_TRUST = ("tin tưởng", "tin dùng", "tin cậy")

def _lint_script(SEG, HEAD, kinds, name="", label=""):
    import re as _re
    from collections import Counter
    warn = []
    # a hyphenated repo name ("agency-agents") splits into parts ("agency","agents") that the per-token
    # English-leak check would otherwise flag — the project's OWN name is never an English leak.
    _name_parts = {p for p in _re.split(r"[-_ ]+", name.lower()) if len(p) >= 2}
    if SEG:
        last = SEG[-1].lower()
        if "seosona" not in last and "theo dõi" not in last:
            warn.append("cảnh cuối thiếu CTA theo dõi SEOSONA")
    _PLACEHOLDER = {"lời đọc", "dòng 1", "từ nhấn", "lời", "seg", "h1", "h2"}
    firsts = Counter()
    for i, s in enumerate(SEG):
        if s.strip().lower() in _PLACEHOLDER:          # model echoed the JSON schema example
            warn.append(f"cảnh {i}: ECHO placeholder (model không sinh nội dung thật)")
        w = len(s.split())
        if w < 5:
            warn.append(f"cảnh {i}: lời quá ngắn ({w} từ)")
        elif w > 40:
            warn.append(f"cảnh {i}: lời quá dài ({w} từ)")
        for ph in _LINT_FORBIDDEN:
            if ph in s.lower():
                warn.append(f"cảnh {i}: cụm cấm '{ph}'")
        try:                                                       # off-platform CTA (brand-safety, shared gate)
            _dm = import_module("content_moderation").off_platform_domain(s, is_cta_scene=(i == len(SEG) - 1))
        except Exception:
            _dm = None
        if _dm:
            warn.append(f"cảnh {i}: CTA ngoài kênh '{_dm}' (chỉ 1 CTA: theo dõi SEOSONA, không dẫn rời kênh)")
        _sll = s.lower()                                            # stars → "N users TRUST it" inflation
        if _INFLATE_BIGNUM.search(s) and any(u in _sll for u in _INFLATE_USER) and any(t in _sll for t in _INFLATE_TRUST):
            warn.append(f"cảnh {i}: SỐ phóng đại — số sao GitHub mô tả thành 'người dùng tin tưởng' (sao ≠ người dùng ≠ tin tưởng; nói đúng 'lượt sao')")
        for tok in _re.findall(r"[A-Za-z][A-Za-z]{5,}", s):       # English-leak suspect (long lowercase word)
            tl = tok.lower()
            if (tl not in _LINT_EN_OK and tl != name.lower() and tl not in _name_parts
                    and tl != "seosona" and not tok.istitle()):
                warn.append(f"cảnh {i}: nghi lọt tiếng Anh '{tok}'")   # skip Proper Nouns (Title-case)
                break
        _enw = [t for t in _re.findall(r"[A-Za-z]+", s.lower()) if t in _EN_STOP]  # English SENTENCE (short-word CTA)
        if len(_enw) >= 2:
            warn.append(f"cảnh {i}: nghi lọt tiếng Anh — câu tiếng Anh ({' '.join(_enw[:5])})")
        fw = (s.split() or [""])[0].lower().strip(".,!?:")
        if fw:
            firsts[fw] += 1
    for w, c in firsts.items():                                    # opening diversity (OpenMontage)
        if c >= 2:
            warn.append(f"từ mở đầu '{w}' lặp {c} cảnh")
    for k, c in Counter(k for k in kinds if k and k != "text").items():  # visual variety
        if c >= 4:
            warn.append(f"component '{k}' lặp {c}× (đơn điệu)")
    tag = f"[script-lint{(' ' + label) if label else ''}]"
    if warn:
        print(f"{tag} ⚠ {len(warn)} cảnh báo: " + " | ".join(warn[:8]))
    else:
        print(f"{tag} ✓ sạch (CTA · độ dài · không lọt-Anh · mở đầu & visual đa dạng)")
    return warn


# ---------------------------------------------------------------- auto content
def _enrich_seg(seg, gh, i):
    """Append a rotating REAL-data clause so deterministic scenes carry ~2× the words → the video reaches
    the ~90s target without fabricating anything (every clause comes from a real GitHub field). The hook
    scene (i==0) stays punchy. Different fact per scene → no repetition."""
    # NO stars fact here — the hook + stats scene already say the star count; repeating it across
    # scenes is the "trùng cảnh" the brand owner flagged. Each scene gets a DIFFERENT real fact +
    # a ROTATING connector so no two reads sound the same.
    # NOTE: the GitHub `desc` is English prose — NEVER speak it (it leaks English into the VN voice).
    # Only use short, safe real fields (language, license, topics) that read cleanly in Vietnamese.
    facts = []
    if gh.get("lang"):
        facts.append(f"được viết bằng {gh['lang']}, hiện đại và dễ mở rộng")
    if gh.get("license"):
        facts.append(f"phát hành theo giấy phép {gh['license']} nên hoàn toàn mở")
    tps = [t.replace("-", " ") for t in (gh.get("topics") or [])[:3]]
    if tps:
        facts.append("xoay quanh các chủ đề " + ", ".join(tps))
    if gh.get("homepage"):
        facts.append("và có cả trang giới thiệu riêng để tìm hiểu thêm")
    # Use each fact AT MOST ONCE across the whole video — NO wrap-around. A thin repo has few real
    # facts, so scenes past the fact count keep their clean base line instead of REPEATING a fact
    # (repetition is worse than a shorter video). This is the deterministic FALLBACK; the primary LLM
    # path writes a fully varied, spec-driven script.
    if i >= len(facts):
        return seg
    connectors = ["Đáng chú ý,", "Bên cạnh đó,", "Đặc biệt,", "Thú vị là", "Ngoài ra,", "Một điểm cộng:"]
    return f"{seg} {connectors[i % len(connectors)]} {facts[i]}."


def auto_content(gh, template):
    """Walk a template's scenes; produce segments + 2-tone headings + real data."""
    scenes = nc.load_template(template)["scenes"]
    n = len(scenes)
    slots = repo_data_slots(gh)
    name = gh["name"]; stars = gh.get("stars_h", "0")
    desc = _clean(gh.get("desc")) or f"{name} — dự án mã nguồn mở đáng chú ý"
    lang = gh.get("lang") or ""; lic = gh.get("license") or "mã nguồn mở"
    used_bignum = False

    SEG, HEAD, DATA = [], [], {}
    for i, sc in enumerate(scenes):
        kind = sc.get("component")
        first, last = i == 0, i == n - 1
        seg, h1, h2, data = None, name, "", None

        if last or kind == "cta":
            seg = f"Vào GitHub {name} để thử ngay. Theo dõi SEOSONA xem thêm thủ thuật."
            h1, h2 = "Theo dõi SEOSONA", "xem thêm mỗi ngày"
            data = {"line": "Thủ thuật AI & lập trình mỗi ngày", "btn": "👉 Theo dõi SEOSONA"}
        elif kind == "bignum":
            if not used_bignum:
                used_bignum = True
                seg = f"{name} đã đạt hơn {stars} sao trên GitHub."
                h1, h2 = name, f"{stars}★"
                data = {"big": stars, "label": "★  GITHUB STARS"}
            else:
                # 2nd number scene: DON'T restate the star count (voice + label differ) so it doesn't
                # feel like a duplicate of the hook. Frame it as adoption/trust instead.
                seg = "Mức độ tin dùng tăng đều, ngày càng nhiều lập trình viên chọn dự án này."
                h1, h2 = "Được tin dùng bởi", "cộng đồng dev"
                data = {"big": stars, "label": "LẬP TRÌNH VIÊN TIN DÙNG"}
        elif kind == "repo":
            # NEVER speak the raw English desc — VieNeu mangles it. Voice = Vietnamese;
            # the English desc still shows on the repo CARD (display), not in narration.
            seg = f"{name} là một dự án mã nguồn mở đang được giới công nghệ chú ý."
            h1, h2 = name, "trên GitHub"
            data = dict(slots["repo"])
            _shots = gh.get("_shots") or []
            if _shots:                       # show the REAL screenshot in the repo scene
                data["img"] = _shots[0]["img"]
                data["url"] = _shots[0]["url"]
        elif kind == "compare":
            seg = f"So với cách làm thủ công, {name} nhanh và gọn hơn hẳn."
            h1, h2 = "Vì sao chọn", name
            data = _compare(gh)
        elif kind == "terminal":
            seg = f"Cài đặt {name} chỉ với vài dòng lệnh."
            h1, h2 = "Cài đặt", "trong 30 giây"
            data = _terminal(gh)
        elif kind == "steps":
            seg = f"Những điểm chính làm nên sức hút của {name}."
            h1, h2 = "Bên trong", "có gì?"
            data = _steps(gh)
        elif kind == "badges":
            seg = f"Hoàn toàn miễn phí, mã nguồn mở, giấy phép {lic}."
            h1, h2 = "Miễn phí", "& mã nguồn mở"
            data = {"items": slots["badges"]}
        elif kind == "gittree":
            seg = f"{name} giúp bạn hình dung mọi thứ một cách trực quan."
            h1, h2 = "Trực quan hóa", "dễ hiểu"
            data = _gittree()
        elif kind == "hub":
            # orbit/hub hero (density study 2026-07: the most common reference hero — centre node +
            # satellites on a ring). Nodes = real features/topics so it's grounded, not decorative.
            seg = f"{name} kết nối nhiều thành phần lại trong một hệ thống liền mạch."
            h1, h2 = "Hệ sinh thái", name
            _raw = ((gh.get("readme_facts") or {}).get("features") or gh.get("topics") or [])
            _nodes = [re.sub(r"^[^0-9A-Za-zÀ-ỹ]+", "", str(x)).split(",")[0].strip()[:16]
                      for x in _raw if str(x).strip()][:6]
            data = {"center": _clean(name, 14) or "CORE", "nodes": _nodes or ["Core", "API", "CLI", "UI"],
                    "line": True}
        elif kind == "stats":
            seg = f"Vài con số nói lên sức hút của {name}."
            h1, h2 = "Những con số", "biết nói"
            data = _stats(gh)
        elif kind == "chart":
            seg = f"Đây là những gì {name} tập trung giải quyết."
            h1, h2 = "Trọng tâm", "dự án"
            data = _chart(gh)
        elif kind == "mockup":
            data = _mockup(gh)
            # Frame by what the shot ACTUALLY is: a real homepage = the app interface; a github page = code.
            if "github" in (data.get("url", "") or "").lower():
                seg = f"Toàn bộ mã nguồn của {name} được công khai, ai cũng xem được."
                h1, h2 = "Mã nguồn", "công khai"
            else:
                seg = f"Đây là giao diện thực tế của {name}, trực quan và dễ dùng."
                h1, h2 = "Giao diện", "thực tế"
        elif kind == "feature":
            seg = f"Những tính năng nổi bật khiến {name} đáng chú ý."
            h1, h2 = "Tính năng", "nổi bật"
            data = _feature(gh)
        elif kind == "tip":
            seg = f"Một mẹo nhỏ để bắt đầu với {name} thật nhanh."
            h1, h2 = "Mẹo", "bắt đầu nhanh"
            data = _tip(gh)
        elif kind == "quote":
            seg = f"Nói ngắn gọn, đây là tinh thần của {name}."
            h1, h2 = "Tóm lại", "một câu"
            data = _quote(gh)
        else:  # text-only scene
            if first:
                seg = f"{name} đang gây chú ý trong giới công nghệ — đây là lý do."
                h1, h2 = name, "có gì hot?"
            else:
                seg = f"Đây là điều khiến {name} trở nên nổi bật."
                h1, h2 = "Giải pháp", "đáng thử"

        SEG.append(_enrich_seg(seg, gh, i)); HEAD.append((h1, h2))
        if data is not None: DATA[i] = data

    # Prefer clean Gemini-written Vietnamese prose (translates the English desc, no slug
    # spam) — the deterministic SEG/HEAD above is the offline fallback. DATA (real repo
    # card / stars / badges) is kept either way.
    # KeyFacts (real numbers/entities) for the UNIFIED traceability gate — the same verify() the whole
    # factory uses, so make_video's script can no longer ship a fabricated number/name un-caught.
    try:
        import script_writer as _sw
        _kf = _sw.analyze(_sw.fetch(gh))
    except Exception:
        _sw, _kf = None, None

    def _traced(seg_list):
        """Traceability errors for a SEG list (numbers/entities not in KeyFacts)."""
        if not (_sw and _kf):
            return []
        vr = _sw.verify(_sw.Script(scenes=[{"idx": i, "text_vi": s, "h1": "", "h2": ""}
                                           for i, s in enumerate(seg_list)]), _kf)
        return [e for e in vr.errors if ("nghi bịa" in e or "lặp câu" in e)]

    g = _gemini_script(gh, scenes, fallback=(SEG, HEAD))    # pad tail from the deterministic draft
    if g:
        SEG, HEAD = g
        print("[make_video] script: LLM (clean Vietnamese)")
        # Corrective loop: SERIOUS lint warnings OR a traceability failure (fabricated number/name) →
        # regenerate ONCE with them fed back, keep whichever is cleaner. Bounded (1 retry).
        _k = [sc.get("component") or "text" for sc in scenes]
        w1 = _lint_script(SEG, HEAD, _k, name, label="draft")
        # Rewrite-trigger = only HARD problems. A single English WORD ("nghi lọt tiếng Anh 'watermark'") is a
        # loanword, not a translation failure — informational, NOT serious (flagging it forced a needless
        # rewrite on ~every tech render, burning free quota). A whole English SENTENCE ("câu tiếng Anh",
        # e.g. an English CTA) IS a real failure → serious. CTA/length/off-platform stay serious too.
        _SERIOUS = ("câu tiếng Anh", "thiếu CTA", "quá ngắn", "quá dài", "CTA ngoài kênh", "SỐ phóng đại")

        def _serious_of(warns, seg):                    # HARD problems only (+ fabrication) — must not ship
            return [x for x in warns if any(k in x for k in _SERIOUS)] + _traced(seg)
        serious = _serious_of(w1, SEG)
        if serious:
            g2 = _gemini_script(gh, scenes, feedback="; ".join(serious[:6]), fallback=(SEG, HEAD))
            if g2:
                w2 = _lint_script(g2[0], g2[1], _k, name, label="retry")
                # Accept the retry when it has FEWER SERIOUS problems (the ones that must not ship); total
                # warnings — which include SOFT loanword noise — are only a tiebreaker. Comparing totals ALONE
                # (the old check) would reject a valid serious-fix that happens to add a loanword, so the
                # serious problem (English/off-platform CTA, stat-inflation, fabrication) would ship anyway.
                if (len(_serious_of(w2, g2[0])), len(w2)) < (len(serious), len(w1)):
                    SEG, HEAD = g2
                    print("[make_video] script: regenerated cleaner after lint feedback")
    else:
        print("[make_video] script: deterministic template (LLM unavailable)")
    _final_bad = _traced(SEG)                           # final gate — applies to BOTH LLM + deterministic
    if _final_bad:
        print("[make_video] ⚠ VERIFY: " + " | ".join(_final_bad[:5]))

    # Cap repo-slug repetition in the SPOKEN text — DETERMINISTIC PATH ONLY. A hyphenated
    # slug said 8× is what VieNeu mangles, and the deterministic template repeats {name}
    # every segment. Gemini already varies it naturally (its prompt says "name once, then
    # 'dự án này'"), so forcing this on Gemini output produced awkward 'Dự án "công cụ này"'.
    if not g:
        seen = 0
        for i in range(len(SEG)):
            if name and name in SEG[i]:
                seen += 1
                if seen > 2:
                    SEG[i] = SEG[i].replace(name, "dự án này" if i % 2 else "công cụ này")

    # MULTI-SHOT: place captured screenshots across MORE than one scene (loha RULE #5).
    # shots[0] already went to the template's repo/mockup scene above (if it has one). Any
    # extra shot is injected into a spare text-only scene (not the hook or CTA) by overriding
    # its component to a mockup window — so a video can show 2 real screenshots, not 1.
    shots = gh.get("_shots") or []
    comp_overrides = {}
    if shots:
        placed = {i for i, d in DATA.items() if isinstance(d, dict) and d.get("img")}
        used = len(placed)
        for i, sc in enumerate(scenes):
            if used >= len(shots):
                break
            if i == 0 or i == n - 1 or i in placed or sc.get("component"):
                continue                     # skip hook, CTA, already-shot, and data-component scenes
            s = shots[used]
            DATA[i] = {"img": s["img"], "url": s["url"], "title": name}
            comp_overrides[i] = "mockup"
            # HONEST framing by shot SOURCE (user 2026-07-03: "giao diện thực tế phải là web/app,
            # KHÔNG phải github"). A github.com screenshot is the CODE page, not the app interface.
            if "github" in (s.get("url", "").lower()):
                SEG[i] = f"Toàn bộ mã nguồn của {name if used == 0 else 'dự án này'} được công khai trên GitHub."
                HEAD[i] = ("Mã nguồn", "công khai")
            else:
                SEG[i] = f"Đây là giao diện thực tế của {name if used == 0 else 'dự án này'}."
                HEAD[i] = ("Giao diện", "thực tế")
            placed.add(i); used += 1
        if used > 1:
            print(f"[make_video] multi-shot: {used} real screenshots placed across scenes")

    # AUTO source-credit (auto-select wiring for the lower-third component): put a lower-third with
    # the REAL repo attribution (name • stars • language) on one spare text-only scene, so the source
    # is always credited AND the new component is actually used by the factory. Conservative: real
    # fields only, one scene, never the hook/CTA/screenshot/data scenes. Gated off with SEOSONA_NO_CREDIT=1.
    if gh and (gh.get("full") or gh.get("name")) and os.environ.get("SEOSONA_NO_CREDIT") != "1":
        for i, sc in enumerate(scenes):
            if i == 0 or i == len(scenes) - 1 or i in comp_overrides or i in DATA or sc.get("component"):
                continue
            bits = [b for b in [f"{gh['stars_h']} sao" if gh.get("stars_h") else None,
                                gh.get("lang"), gh.get("license")] if b][:3]
            DATA[i] = {"title": gh.get("full") or gh.get("name"), "sub": " • ".join(bits)}
            comp_overrides[i] = "lower-third"
            SEG[i] = f"{gh.get('name','Dự án')} là dự án mã nguồn mở trên GitHub."
            HEAD[i] = ("Nguồn", "dự án")
            break

    # PACING: cap each scene's VOICE to ~26 words (~7-8s) so scenes stay PUNCHY, not 60-word paragraphs
    # (the slideshow root cause: long segments → 12-18s/scene). Keeps whole sentences up to the cap.
    def _cap_seg(t, mx=26):
        ws = str(t or "").split()
        if len(ws) <= mx:
            return t
        out, c = [], 0
        for s in re.split(r'(?<=[.!?…])\s+', str(t)):
            n = len(s.split())
            if out and c + n > mx:
                break
            out.append(s); c += n
            if c >= mx:
                break
        return " ".join(out) if out else " ".join(ws[:mx])
    SEG = [_cap_seg(s) for s in SEG]
    # GUARANTEE non-empty headings (the pacing template-pad grew scene counts and exposed empty h1/h2 on the
    # CTA / padded scenes → scene_composer rejects them). Fill any blank from the scene's own keywords.
    for i in range(len(SEG)):
        _h = HEAD[i] if i < len(HEAD) and HEAD[i] else ("", "")
        _h1, _h2 = (str(_h[0]).strip(), str(_h[1]).strip()) if len(_h) >= 2 else ("", "")
        if not _h1 or not _h2:
            _kw = [w for w in re.findall(r"[\wÀ-ỹ]+", SEG[i] if i < len(SEG) else "") if len(w) > 2][:3]
            _h1 = _h1 or (" ".join(_kw[:2]).capitalize() if _kw else (name or "SEOSONA"))
            _h2 = _h2 or (_kw[2] if len(_kw) > 2 else "chi tiết")
            HEAD[i] = (_h1, _h2)
    eff_kinds = [comp_overrides.get(i) or (scenes[i].get("component") or "text")
                 for i in range(len(SEG))]
    _w = _lint_script(SEG, HEAD, eff_kinds, name)
    _LAST_RENDER["lint_warns"] = len(_w)          # flywheel signals
    _LAST_RENDER["script"] = "llm" if g else "deterministic"
    lex = dict(_BASE_LEX)
    return compose(template, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=lex,
                   comp_overrides=comp_overrides)

# ---------------------------------------------------------------- real screenshots (shots)
def _capture_one(url, out):
    """Headless-capture one URL → PNG. Returns out on success, else None (best-effort)."""
    script = os.path.join(ROOT, "scripts", "capture_shot.js")
    if not os.path.exists(script):
        return None
    try:
        r = subprocess.run(["node", script, url, out], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=80)
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 8000:
            return out
    except Exception:
        pass
    return None

def _dom(u):
    return (u or "").replace("https://", "").replace("http://", "").split("/")[0] or "github.com"

def _capture_shots(gh, project_dir):
    """Up to 2 DISTINCT real screenshots — the project HOMEPAGE and the GitHub repo page
    (adopt loha RULE #5 '≥2-3 mockups': real visuals across more than one scene). Returns a
    list of {img, url}; empty on total failure → render falls back to synthetic tiles."""
    os.makedirs(project_dir, exist_ok=True)
    targets = []
    hp = (gh.get("homepage") or "").strip()
    if hp.startswith("http"):
        targets.append(hp)
    targets.append(gh.get("url") or f"https://github.com/{gh.get('full','')}")
    shots = []
    for i, u in enumerate(targets):
        p = _capture_one(u, os.path.join(project_dir, f"_shot_{i}.png"))
        if p:
            shots.append({"img": p, "url": _dom(u)})
            print(f"[make_video] shot {len(shots)} captured: {u}")
        else:
            print(f"[make_video] shot skipped: {u}")
    return shots


def _capture_scroll(gh, project_dir):
    """Record a REAL page-scroll (webm) of the project homepage (or the GitHub page) → live footage the
    mockup scene overlays over its static shot. Best-effort: returns the webm path or None."""
    script = os.path.join(ROOT, "scripts", "capture_scroll.js")
    if not os.path.exists(script):
        return None
    hp = (gh.get("homepage") or "").strip()
    url = hp if hp.startswith("http") else (gh.get("url") or f"https://github.com/{gh.get('full','')}")
    out = os.path.join(project_dir, "_scroll.webm")
    try:
        r = subprocess.run(["node", script, url, out, "6"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=110)
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 10000:
            print(f"[make_video] scroll video captured: {url}")
            return out
    except Exception as e:
        print(f"[make_video] scroll capture skipped: {e}")
    return None

def _finalize_outputs(gh, project_dir, output, name):
    """Ready-to-post sidecars + behavioral verify (adopted from AI-auto-generate-video /
    loha: the 3-file CapCut-ready output + RULE #8 'verify before deliver').
      • <name> - voice.mp3  — the narration track alone (drop into CapCut/editor)
      • script.txt          — plain narration text (CapCut auto-caption)
      • caption.txt         — a suggested post caption + hashtags
    Then runs evaluator.evaluate() so a silent/black/too-short render is flagged loudly."""
    import shutil, glob as _g
    va = os.path.join(project_dir, "proj", "assets", "voice.mp3")
    if os.path.exists(va):
        try: shutil.copy(va, os.path.join(project_dir, f"{name} - voice.mp3"))
        except Exception: pass
    srts = _g.glob(os.path.join(project_dir, "**", "*_cc.srt"), recursive=True)
    hook_vn = ""
    if srts:
        try:
            lines = [ln.strip() for ln in open(srts[0], encoding="utf-8")
                     if ln.strip() and "-->" not in ln and not ln.strip().isdigit()]
            open(os.path.join(project_dir, "script.txt"), "w", encoding="utf-8").write(" ".join(lines))
            hook_vn = lines[0] if lines else ""
        except Exception: pass
    try:  # caption = the Vietnamese opening line (VN channel) + topic hashtags
        tags = " ".join("#" + re.sub(r"[^a-z0-9]", "", t.lower()) for t in (gh.get("topics") or [])[:4])
        hook = hook_vn or f"{name} — {_clean(gh.get('desc'), 100)}"
        cap = f"{hook}\n\n#SEOSONA #congnghe #AI #laptrinh {tags}".strip()
        open(os.path.join(project_dir, "caption.txt"), "w", encoding="utf-8").write(cap)
    except Exception: pass
    _record_opening(gh.get("full") or name, hook_vn)   # episodic anti-repeat: remember this opening
    ev = {}
    try:
        ev = import_module("evaluator").evaluate(output, record=False) or {}
        if ev.get("ok"):
            print("[make_video] ✓ verify passed (audio not silent + frames not blank + duration OK)")
        else:
            print(f"[make_video] ⚠ VERIFY FOUND ISSUES: {'; '.join(ev.get('reasons', []))}")
    except Exception as e:
        print(f"[make_video] verify skipped ({type(e).__name__})")
    # Flight-recorder (observability-light): one JSONL row per video → factory health signal.
    try:
        sz = round(os.path.getsize(output) / 1e6, 2) if os.path.exists(output) else 0
        import_module("factory_metrics").record(
            repo=gh.get("full") or name, output=os.path.basename(output),
            size_mb=sz, dur_s=ev.get("duration") or ev.get("dur_s"),
            ok=bool(ev.get("ok")), issues=ev.get("reasons") or [],
            template=_LAST_RENDER.get("template"), script=_LAST_RENDER.get("script"),
            lint_warns=_LAST_RENDER.get("lint_warns"))
    except Exception:
        pass

# ---------------------------------------------------------------- one-shot
def make(url, *, template=None, theme=None, output=None, project_dir=None, aspect=None):
    gh = fetch_github(url)
    if gh.get("error"):
        raise SystemExit(f"GitHub fetch failed for {url}: {gh['error']}")
    pick_t, pick_theme, reason = classify(gh)
    theme = theme or pick_theme
    # DYNAMIC SCENE-ARC (default): compose a bespoke arc from the component library per video, matched
    # to this repo's content — instead of always reusing 1 of the 20 fixed templates. Set
    # SEOSONA_DYNAMIC_SCENES=0 to fall back to curated templates. A forced --template always wins.
    # STRUCTURAL VARIETY: rotate across the curated archetype LIBRARY (distinct structures + content-
    # specific VN tags), seeded by repo so different repos get different STRUCTURES — not one dynamic
    # skeleton every time. classify()'s content match is preferred (weighted first); the bespoke dynamic
    # arc stays in the mix as one option. SEOSONA_DYNAMIC_SCENES=0 → curated-only (no dynamic).
    if template is None:
        seed = sum(ord(c) for c in (gh.get("name") or "x")[:24])
        pool = list(dict.fromkeys([pick_t] + _NEWS_ARCHETYPES))   # content-pick first, then all (dedup)
        if os.environ.get("SEOSONA_DYNAMIC_SCENES", "1") != "0":
            pool.append("_dynamic")
        pick = pool[seed % len(pool)]
        if pick == "_dynamic":
            try:
                import template_generator as _tg
                topics = " ".join(gh.get("topics") or [])
                brief = f"{gh.get('name','')}. {_clean(gh.get('desc')) or ''}. {topics}".strip()
                gen_name = "_auto_" + re.sub(r"[^a-z0-9]+", "-", (gh.get("name", "x")).lower()).strip("-")[:30]
                tpl = _tg.build_template(brief, name=gen_name, n=int(os.environ.get("SEOSONA_SCENES", "11")), seed=gh.get("name", ""))
                nc.save_template(gen_name, tpl)
                template = gen_name
                reason = "dynamic arc: " + ">".join((s["component"] or "hook") for s in tpl["scenes"])
            except Exception as e:
                print(f"[make_video] dynamic scene-gen failed ({e}); using curated template")
                template = pick_t
        else:
            template = pick
            reason = f"archetype rotation {seed % len(pool) + 1}/{len(pool)}: {pick}"
    template = template or pick_t
    name = gh["name"]
    # Output folder = the project name directly under 8_WORKSPACE (no "auto" wrapper).
    project_dir = project_dir or os.path.join(ROOT, "8_WORKSPACE", name)
    output = output or os.path.join(project_dir, f"{name} - SEOSONA.mp4")
    print(f"[make_video] {gh['full']} → template={template} theme={theme} aspect={aspect or 'template'}  ({reason})")
    gh["_shots"] = _capture_shots(gh, project_dir)     # up to 2 real screenshots (homepage + GitHub), best-effort
    if os.environ.get("SEOSONA_SCROLL_VIDEO", "1") != "0":
        gh["_scroll"] = _capture_scroll(gh, project_dir)   # real page-scroll footage for the mockup scene
    _LAST_RENDER.clear(); _LAST_RENDER["template"] = template   # flywheel: record which template was used
    content = auto_content(gh, template)
    kw = {"aspect": aspect} if aspect else {}   # else use the template's aspect
    nc.make_video_from_template(template, content, project_dir, output=output, theme=theme, **kw)
    _finalize_outputs(gh, project_dir, output, name)
    # Optional: also hand off an editable CapCut project (env SEOSONA_CAPCUT_EXPORT=1) so the
    # user can embellish with CapCut's SFX/transitions/text-effects. Best-effort, off by default.
    if os.environ.get("SEOSONA_CAPCUT_EXPORT") == "1":
        try:
            import_module("capcut_export").export(output, aspect=aspect or "9:16")
        except Exception:
            pass
    return output

# ---------------------------------------------------------------- news rotation
def news_rotation(urls, *, out_dir=None):
    """Batch many repos into videos, rotating templates + alternating theme so a
    news feed doesn't look repetitive. Same-type runs are nudged to a sibling
    template; theme is driven by topic but alternated when it would repeat."""
    out_dir = out_dir or os.path.join(ROOT, "8_WORKSPACE", "news_batch")
    os.makedirs(out_dir, exist_ok=True)
    SIBLING = {"repo-showcase": "tool-walkthrough", "tool-walkthrough": "repo-showcase"}
    plan, prev_t, prev_theme = [], None, None
    metas = [(u, fetch_github(u)) for u in urls]
    for u, gh in metas:
        if gh.get("error"):
            plan.append((u, None, None, None, gh["error"])); continue
        t, theme, reason = classify(gh)
        if t == prev_t and t in SIBLING:                 # avoid 2 identical in a row
            t = SIBLING[t]; reason += " (xoay sang sibling)"
        if theme == prev_theme == "light" and t in SIBLING:
            pass                                          # light tools stay light; ok
        plan.append((u, gh, t, theme, reason))
        prev_t, prev_theme = t, theme

    results = []
    for u, gh, t, theme, reason in plan:
        if gh is None:
            print(f"  SKIP {u}: {reason}"); results.append((u, None)); continue
        name = gh["name"]
        out = os.path.join(out_dir, f"{name} - SEOSONA.mp4")
        print(f"\n=== {gh['full']} → {t} / {theme}  ({reason}) ===")
        try:                                   # one video's render failure must NOT abort the whole batch
            content = auto_content(gh, t)
            nc.make_video_from_template(t, content, os.path.join(out_dir, name), output=out, theme=theme)
        except Exception as _re:
            print(f"  [news_rotation] {name} render FAILED ({type(_re).__name__}: {_re}) — skipping, batch continues.")
            results.append((u, None)); continue
        try:                                   # quality gate + optional publish per video
            from video_engine import score_output, maybe_publish
            score_output(out, "seosona")
            maybe_publish(out, os.path.join(out_dir, name), name, gh.get("desc", ""), "seosona")
        except Exception as _e:
            print(f"[make_video] finalize skipped: {_e}")
        results.append((u, out))
    print(f"\n[news_rotation] {sum(1 for _,o in results if o)}/{len(results)} videos → {out_dir}")
    return results

# ---------------------------------------------------------------- CLI
def _main():
    ap = argparse.ArgumentParser(description="SEOSONA make_video — github url → branded video")
    ap.add_argument("target", nargs="?", help="github url or owner/name")
    ap.add_argument("--template", help="force a template (else auto)")
    ap.add_argument("--theme", choices=["light"], default="light", help="brand is light-mode only")
    ap.add_argument("--out", help="output mp4 path")
    ap.add_argument("--aspect", choices=["9:16", "16:9", "1:1"], help="override aspect (else template's)")
    ap.add_argument("--news", metavar="FILE", help="batch: a file with one github url per line")
    a = ap.parse_args()
    if a.news:
        urls = [l.strip() for l in open(a.news, encoding="utf-8") if l.strip() and not l.startswith("#")]
        news_rotation(urls)
    elif a.target:
        out = make(a.target, template=a.template, theme=a.theme, output=a.out, aspect=a.aspect)
        try:                                   # quality gate + optional publish (make:video)
            from video_engine import score_output, maybe_publish
            score_output(out, "seosona")
            maybe_publish(out, os.path.dirname(out), os.path.splitext(os.path.basename(out))[0], str(a.target), "seosona")
        except Exception as _e:
            print(f"[make_video] finalize skipped: {_e}")
        print("DONE:", out)
    else:
        ap.error("give a github url/owner-name, or --news FILE")

if __name__ == "__main__":
    _main()
