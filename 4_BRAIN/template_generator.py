# -*- coding: utf-8 -*-
"""Auto-grow the template library — generate a NEW archetype (scene-arc plan) from a brief (Phase 3).

Deterministic by default: assembles a scene arc from the 17 `native_composer` components by matching
content cues in the brief, always book-ended by a HOOK and a CTA. The output is a valid template JSON
(same schema as `7_ASSETS/templates/*.json`) that `native_composer` + `template_picker` can use immediately.

    python 4_BRAIN/template_generator.py "Top 7 lỗi SEO khiến tụt hạng" --scenes 7

Validates every component against the real set, so a generated template never references a non-existent
component. (Hook for an LLM proposer can be added later; the deterministic arc already ships usable plans.)
"""
import os
import re
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(ROOT, "7_ASSETS", "templates")
_AC = ["orange", "blue", "green"]

# the real component set — MUST be components native_composer actually RENDERS *and* auto_content fills.
# (items/tiles/data were here but native_composer has NO renderer for them → blank scenes. Removed.)
COMPONENTS = {"bignum", "stats", "compare", "steps", "quote", "tip", "feature", "terminal",
              "repo", "badges", "chart", "mockup", "gittree", "cta", "hub"}

# content cue → the body component that shows it (Vietnamese-first)
_CUE = [
    (("số liệu", "tăng", "phần trăm", "%", "triệu", "tỷ", "kỷ lục", "doanh thu"), "bignum"),
    (("so sánh", " vs", "khác nhau", "đối đầu"), "compare"),
    (("các bước", "cách làm", "quy trình", "hướng dẫn", "từng bước"), "steps"),
    (("mẹo", "lưu ý", "ghi nhớ", "bí kíp"), "tip"),
    (("trích dẫn", "quan điểm", "nói rằng", "góc nhìn"), "quote"),
    (("tính năng", "điểm mạnh", "ưu điểm", "nổi bật"), "feature"),
    (("danh sách", "liệt kê", "top ", "những "), "badges"),
    (("dòng lệnh", "code", "terminal", "câu lệnh"), "terminal"),
    (("giao diện", "demo", "mockup", "màn hình"), "mockup"),
    (("biểu đồ", "thống kê", "dữ liệu"), "chart"),
    (("hệ sinh thái", "kết nối", "tích hợp", "thành phần", "kiến trúc", "gồm nhiều"), "hub"),
]


def _slug(text):
    """Vietnamese-aware slug: strip diacritics → ascii, then kebab-case (so the filename is clean)."""
    import unicodedata
    t = text.replace("đ", "d").replace("Đ", "D")
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")  # drop combining marks
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")
    return t[:34] or "archetype"


# Viewer-facing Vietnamese kicker per component (NOT the raw type name "MOCKUP/CHART" — user 2026-07-03).
# Chosen to match native_composer's KICKER emoji map where possible (CON SỐ→📊, QUY MÔ→📈, GHI NHỚ→📌).
_KICKER_VN = {
    "mockup": "GIAO DIỆN", "chart": "TRỌNG TÂM", "badges": "NỔI BẬT", "quote": "TÓM LẠI",
    "terminal": "CÀI ĐẶT", "feature": "TÍNH NĂNG", "stats": "CON SỐ", "bignum": "QUY MÔ",
    "compare": "SO SÁNH", "tip": "GHI NHỚ", "steps": "CÁC BƯỚC", "repo": "DỰ ÁN", "gittree": "CẤU TRÚC",
    "hub": "HỆ SINH THÁI",
}


def _arc_from_brief(brief, n=7, seed=""):
    """HOOK → context → body components matched to the brief → CTA (n scenes total).

    `seed` (e.g. the repo name) makes the PADDING order vary per video, so two repos that share the
    same content cues still get a different component mix — the fix for 'same template every time'."""
    low = brief.lower()
    body, seen = [], set()
    for kws, c in _CUE:                              # 1) content-matched components (fit the topic)
        if any(k in low for k in kws) and c not in seen:
            body.append(c); seen.add(c)
    # 2) pad from a seed-ROTATED pool so the mix differs per video. NOTE 'steps' is NOT here — it only
    # enters via a real step CUE (các bước/quy trình); as filler it wrongly shows advantages as "N Bước".
    pool = ["feature", "stats", "bignum", "compare", "tip", "mockup", "chart", "badges", "quote", "terminal", "hub"]
    off = sum(ord(ch) for ch in (seed or brief)[:24]) % len(pool)
    rotated = pool[off:] + pool[:off]
    for d in rotated:
        if len(body) >= n - 3:
            break
        if d not in seen:
            body.append(d); seen.add(d)
    arc = [(None, "TIN NÓNG", True), (None, "BỐI CẢNH")]
    for c in body[:max(1, n - 3)]:
        arc.append((c, _KICKER_VN.get(c, c.upper())))   # VN label, not the raw type name
    arc.append(("cta", "SEOSONA AI"))
    return arc


def build_template(brief, name="_auto", n=7, seed=""):
    """Return a bespoke template DICT (not written to disk) — for per-video dynamic scene arcs."""
    scenes = []
    for i, item in enumerate(_arc_from_brief(brief, n, seed=seed)):
        comp = item[0]
        if comp is not None and comp not in COMPONENTS:
            comp = "feature"
        sc = {"component": comp, "accent": _AC[i % 3], "kicker_hint": item[1]}
        if len(item) > 2 and item[2]:
            sc["hero"] = True
        scenes.append(sc)
    return {"name": name, "title": brief[:40], "description": brief,
            "when_to_use": f"Auto-generated per-video arc — {brief[:60]}",
            "theme": "light", "aspect": "9:16", "scenes": scenes}


def generate(brief, name=None, n=7, overwrite=False):
    """Write a new archetype template JSON from `brief`. Returns the path, or None if it already exists."""
    name = name or _slug(brief)
    path = os.path.join(OUT_DIR, name + ".json")
    if os.path.exists(path) and not overwrite:
        print(f"[gen] exists (skip): {name}")
        return None
    d = build_template(brief, name=name, n=n, seed=name)
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[gen] + {name}  ({len(scenes)} scenes)")
    return path


if __name__ == "__main__":
    import sys, argparse
    ap = argparse.ArgumentParser(description="Generate a new SEOSONA template archetype from a brief.")
    ap.add_argument("brief"); ap.add_argument("--name"); ap.add_argument("--scenes", type=int, default=7)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    print("result:", generate(a.brief, a.name, a.scenes, a.overwrite))
