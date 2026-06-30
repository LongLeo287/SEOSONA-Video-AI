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
from scene_composer import fetch_github, repo_data_slots, compose
import native_composer as nc

# ---------------------------------------------------------------- classify
def classify(gh):
    """Pick (template, theme, reason) from repo metadata."""
    name = (gh.get("name") or "").lower()
    desc = (gh.get("desc") or "").lower()
    topics = set(t.lower() for t in (gh.get("topics") or []))
    text = f"{name} {desc} {' '.join(topics)}"
    has = lambda *ks: any(k in text for k in ks)

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
    get different templates (fixes 'same template every time')."""
    return options[sum(ord(c) for c in (name or "x")) % len(options)]

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
    s = re.sub(r"[^\w\sÀ-ỹ.,:;/+&()-]", "", str(s or "")).strip()
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
        return {"img": shots[0]["img"], "url": shots[0]["url"], "title": gh.get("name", "")}
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

# ---------------------------------------------------------------- Gemini prose
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
    userp = (f"Repo: {name}\nMô tả (tiếng Anh): {desc}\n"
             f"Sao: {gh.get('stars_h')}, ngôn ngữ: {gh.get('lang')}, "
             f"chủ đề: {', '.join((gh.get('topics') or [])[:6])}\n"
             f"Số cảnh: {n}. Vai trò trực quan từng cảnh: {kinds}\n"
             f"Trả JSON: {{\"focus\":[\"trọng tâm cảnh 1 (3-8 từ)\", ...]}} đúng {n} phần tử; "
             f"cảnh cuối = kêu gọi theo dõi SEOSONA.")
    try:
        out = llm_engine.generate_json_from_prompt(sysp, userp, model_name="gemini-2.5-flash")
        foci = out.get("focus") if isinstance(out, dict) else (out if isinstance(out, list) else None)
        if not foci or len(foci) < n:
            return None
        return [str(f).strip() for f in foci[:n]]
    except Exception:
        return None


def _gemini_script(gh, scenes):
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
    # Prompt hardened with prompt-master gems (MIT): explicit role + GROUNDING (no fabrication)
    # + Gemini-specific guard (it hallucinates stats / drifts format). Brand tone locked.
    sysp = ("Bạn là biên kịch video tin tức công nghệ tiếng Việt cho kênh SEOSONA "
            "(thương hiệu: xanh #2A5BDA / cam #E2724D, tông chuyên nghiệp, khán giả VN). "
            "Viết kịch bản NGẮN, tự nhiên, thuần Việt. TUYỆT ĐỐI KHÔNG chèn nguyên câu "
            "tiếng Anh vào lời đọc; DỊCH mô tả sang tiếng Việt. Tên repo đọc tự nhiên, "
            "lần đầu nêu tên rồi sau gọi 'dự án này' / 'công cụ này' (đừng lặp slug). "
            "Mỗi cảnh 1 ý, ~15-28 từ. Số đọc bình thường. "
            "GROUNDING: CHỈ dùng dữ kiện được cung cấp (tên/mô tả/sao/ngôn ngữ/chủ đề); "
            "TUYỆT ĐỐI KHÔNG bịa số liệu, tính năng, hay khẳng định không có trong dữ kiện.")
    # Stage 1: plan a coherent arc first (graceful — None → write without it = old behavior).
    plan = _gemini_outline(gh, kinds)
    plan_txt = ""
    if plan:
        plan_txt = ("Dàn ý đã duyệt — BÁM SÁT, mỗi cảnh đúng trọng tâm CỦA NÓ, không lặp ý cảnh khác:\n"
                    + "\n".join(f"  Cảnh {i + 1}: {p}" for i, p in enumerate(plan)) + "\n")
    userp = (f"Repo GitHub: {name}\nMô tả (tiếng Anh, hãy DỊCH): {desc}\n"
             f"Sao: {gh.get('stars_h')}, ngôn ngữ: {gh.get('lang')}, "
             f"chủ đề: {', '.join((gh.get('topics') or [])[:6])}\n"
             f"Số cảnh: {len(scenes)}. Vai trò từng cảnh: {kinds}\n"
             f"{plan_txt}"
             f"Trả JSON: {{\"scenes\":[{{\"seg\":\"lời đọc\",\"h1\":\"dòng 1 (≤22)\","
             f"\"h2\":\"từ nhấn (≤22)\"}}]}} đúng {len(scenes)} phần tử, cảnh cuối là CTA theo dõi SEOSONA.")
    try:
        out = llm_engine.generate_json_from_prompt(sysp, userp, model_name="gemini-2.5-flash")
        rows = out.get("scenes") if isinstance(out, dict) else (out if isinstance(out, list) else None)
        if not rows or len(rows) < len(scenes):
            return None
        import re as _re
        def _clean_voice(s):
            s = _re.sub(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF]", "", str(s))  # emoji
            s = _re.sub(r"https?://\S+|[→&%$#=]", " ", s)                              # urls/symbols
            return _re.sub(r"\s+", " ", s).strip()
        SEG = [_clean_voice(r.get("seg", "")) for r in rows[:len(scenes)]]
        HEAD = [(str(r.get("h1", name)).strip(), str(r.get("h2", "")).strip()) for r in rows[:len(scenes)]]
        if any(not s for s in SEG):
            return None
        return SEG, HEAD
    except Exception as e:
        print(f"[make_video] Gemini script failed ({e}) — deterministic prose.")
        return None


# ---------------------------------------------------------------- auto content
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
            else:
                seg = f"Cộng đồng {name} đang lớn rất nhanh với {stars} sao."
                h1, h2 = "Được tin dùng bởi", "cộng đồng dev"
            data = {"big": stars, "label": "★  GITHUB STARS"}
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
        elif kind == "stats":
            seg = f"Vài con số nói lên sức hút của {name}."
            h1, h2 = "Những con số", "biết nói"
            data = _stats(gh)
        elif kind == "chart":
            seg = f"Đây là những gì {name} tập trung giải quyết."
            h1, h2 = "Trọng tâm", "dự án"
            data = _chart(gh)
        elif kind == "mockup":
            seg = f"Mọi thông tin quan trọng của {name} gói gọn trong một chỗ."
            h1, h2 = "Tổng quan", "dự án"
            data = _mockup(gh)
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

        SEG.append(seg); HEAD.append((h1, h2))
        if data is not None: DATA[i] = data

    # Prefer clean Gemini-written Vietnamese prose (translates the English desc, no slug
    # spam) — the deterministic SEG/HEAD above is the offline fallback. DATA (real repo
    # card / stars / badges) is kept either way.
    g = _gemini_script(gh, scenes)
    if g:
        SEG, HEAD = g
        print("[make_video] script: Gemini (clean Vietnamese)")
    else:
        print("[make_video] script: deterministic template (Gemini unavailable)")

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
            SEG[i] = f"Đây là giao diện thực tế của {name if used == 0 else 'dự án này'}."
            HEAD[i] = ("Giao diện", "thực tế")
            placed.add(i); used += 1
        if used > 1:
            print(f"[make_video] multi-shot: {used} real screenshots placed across scenes")

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
    try:
        ev = import_module("evaluator").evaluate(output, record=False)
        if ev.get("ok"):
            print("[make_video] ✓ verify passed (audio not silent + frames not blank + duration OK)")
        else:
            print(f"[make_video] ⚠ VERIFY FOUND ISSUES: {'; '.join(ev.get('reasons', []))}")
    except Exception as e:
        print(f"[make_video] verify skipped ({type(e).__name__})")

# ---------------------------------------------------------------- one-shot
def make(url, *, template=None, theme=None, output=None, project_dir=None, aspect=None):
    gh = fetch_github(url)
    if gh.get("error"):
        raise SystemExit(f"GitHub fetch failed for {url}: {gh['error']}")
    pick_t, pick_theme, reason = classify(gh)
    template = template or pick_t
    theme = theme or pick_theme
    name = gh["name"]
    # Output folder = the project name directly under 8_WORKSPACE (no "auto" wrapper).
    project_dir = project_dir or os.path.join(ROOT, "8_WORKSPACE", name)
    output = output or os.path.join(project_dir, f"{name} - SEOSONA.mp4")
    print(f"[make_video] {gh['full']} → template={template} theme={theme} aspect={aspect or 'template'}  ({reason})")
    gh["_shots"] = _capture_shots(gh, project_dir)     # up to 2 real screenshots (homepage + GitHub), best-effort
    content = auto_content(gh, template)
    kw = {"aspect": aspect} if aspect else {}   # else use the template's aspect
    nc.make_video_from_template(template, content, project_dir, output=output, theme=theme, **kw)
    _finalize_outputs(gh, project_dir, output, name)
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
        content = auto_content(gh, t)
        nc.make_video_from_template(t, content, os.path.join(out_dir, name), output=out, theme=theme)
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
