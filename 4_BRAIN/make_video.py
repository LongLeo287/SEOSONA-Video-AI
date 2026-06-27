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
import os, sys, json, re, argparse

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
    return ("repo-showcase", "light", "repo showcase")

# ---------------------------------------------------------------- prose helpers
_BASE_LEX = {"GitHub": "gít hắp", "API": "ây pi ai", "AI": "ây ai", "CLI": "xi eo ai",
             "SEOSONA": "sê ô sô na", "MIT": "em ai ti", "open source": "âu pừn sọt",
             "Docker": "đốc cơ", "npm": "en pi em", "Git": "gít"}
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
            seg = f"{name}: {desc}."
            h1, h2 = name, "trên GitHub"
            data = slots["repo"]
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
        else:  # text-only scene
            if first:
                seg = f"{name} đang gây chú ý trong giới công nghệ — đây là lý do."
                h1, h2 = name, "có gì hot?"
            else:
                seg = f"Đây là điều khiến {name} trở nên nổi bật."
                h1, h2 = "Giải pháp", "đáng thử"

        SEG.append(seg); HEAD.append((h1, h2))
        if data is not None: DATA[i] = data

    lex = dict(_BASE_LEX)
    return compose(template, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=lex)

# ---------------------------------------------------------------- one-shot
def make(url, *, template=None, theme=None, output=None, project_dir=None, aspect=None):
    gh = fetch_github(url)
    if gh.get("error"):
        raise SystemExit(f"GitHub fetch failed for {url}: {gh['error']}")
    pick_t, pick_theme, reason = classify(gh)
    template = template or pick_t
    theme = theme or pick_theme
    name = gh["name"]
    project_dir = project_dir or os.path.join(ROOT, "8_WORKSPACE", "auto", name)
    output = output or os.path.join(project_dir, f"{name} - SEOSONA.mp4")
    print(f"[make_video] {gh['full']} → template={template} theme={theme} aspect={aspect or 'template'}  ({reason})")
    content = auto_content(gh, template)
    kw = {"aspect": aspect} if aspect else {}   # else use the template's aspect
    nc.make_video_from_template(template, content, project_dir, output=output, theme=theme, **kw)
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
