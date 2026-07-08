# -*- coding: utf-8 -*-
"""SEOSONA element library — render one on-brand visual ELEMENT to a transparent PNG.

The talking-head reels are dense with small visual elements popped over the footage: glassy
icon-tiles, chips, ✓/✕ badges, sparkles, hand-drawn arrows, proof-rings. ASS text can't draw
those, so we render each element as an HTML/CSS + inline-SVG card on a TRANSPARENT background
(Playwright/Chromium, the same engine as native_composer/thumbnail_maker) → a PNG that
`talking_head_edit` composites over the footage at the right beat (and the faceless engine can
embed inline). LIGHT brand only: white/frosted glass, soft shadow, one semantic role colour
(never neon). Icons = the vendored Lucide set in `7_ASSETS/brand/icons/` (single-colour →
tinted to the element's role via `currentColor`).

    from element_maker import render_element
    render_element({"type":"icon_tile","icon":"clock","role":"caution","badge":"x",
                    "label":"Mất thời gian"}, "out.png")

One public function: `render_element(spec, out_png)` (+ `render_many` for a batch in one browser).
Element types: icon_tile · chip · badge · sparkle · arrow · ring · big_stat. `icon` accepts a
Lucide file name OR a concept word (mapped by ICON_ALIASES). See `element_library.json` for the
catalogue the pipeline/LLM picks from.
"""
import os
import re
import sys
import json
import tempfile
from importlib import import_module

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # VN/emoji prints on cp1252 Windows
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import brand_kit as bk  # noqa: E402 — single source of truth for palette + ROLES

ICON_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "icons")
TWEMOJI_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "twemoji")


def _twemoji_svg(ch):
    """Return the vendored Twemoji flat SVG for an emoji char (brand-consistent across machines),
    or None → fall back to the native OS emoji. Twemoji is CC-BY 4.0."""
    try:
        cp = "-".join(f"{ord(c):x}" for c in str(ch) if c != "️")
        p = os.path.join(TWEMOJI_DIR, f"{cp}.svg")
        return open(p, encoding="utf-8").read() if os.path.exists(p) else None
    except Exception:
        return None

# Concept word (VN/EN) → Lucide icon file. Lets a caller/LLM ask for an element by MEANING.
# Extend freely; unknown concepts fall back to the raw name then to a neutral dot.
ICON_ALIASES = {
    "time": "clock", "thời gian": "clock", "giờ": "clock", "deadline": "alarm-clock",
    "đếm ngược": "timer", "countdown": "timer", "lịch": "calendar", "calendar": "calendar",
    "tiền": "dollar-sign", "money": "dollar-sign", "chi phí": "coins", "cost": "coins",
    "giá": "dollar-sign", "ví": "wallet", "tiết kiệm": "piggy-bank", "quà": "gift", "free": "gift",
    "tăng": "trending-up", "growth": "trending-up", "giảm": "trending-down",
    "người": "user", "user": "user", "khách hàng": "users", "team": "users", "nhóm": "users",
    "công việc": "briefcase", "job": "briefcase", "ngành": "briefcase",
    "laptop": "laptop", "máy tính": "monitor", "công cụ": "wrench", "tool": "wrench",
    "cài đặt": "settings", "settings": "settings", "thư mục": "folder", "folder": "folder",
    "file": "file", "tài liệu": "files", "gói": "package", "sản phẩm": "package", "lớp": "layers",
    "ai": "bot", "agent": "bot", "bot": "bot", "trí tuệ": "brain", "brain": "brain",
    "code": "code", "lập trình": "code", "terminal": "terminal", "api": "plug", "provider": "plug",
    "nhanh": "zap", "speed": "zap", "tốc độ": "zap", "database": "database", "dữ liệu": "database",
    "cloud": "cloud", "mạng": "network", "quy trình": "workflow", "workflow": "workflow",
    "nhánh": "git-branch", "chat": "message-circle", "tin nhắn": "message-square",
    "email": "mail", "mail": "mail", "thông báo": "bell", "chia sẻ": "share-2", "share": "share-2",
    "thích": "thumbs-up", "like": "thumbs-up", "không thích": "thumbs-down", "tim": "heart",
    "điện thoại": "smartphone", "phone": "smartphone",
    "tìm kiếm": "search", "seo": "search", "search": "search", "web": "globe", "website": "globe",
    "biểu đồ": "chart-column", "chart": "chart-column", "thống kê": "chart-line",
    "mục tiêu": "target", "target": "target", "quảng cáo": "megaphone", "marketing": "megaphone",
    "bùng nổ": "rocket", "rocket": "rocket", "ra mắt": "rocket", "cúp": "trophy", "giải": "award",
    "sao": "star", "star": "star", "hot": "flame", "lửa": "flame", "trend": "flame",
    "ý tưởng": "lightbulb", "idea": "lightbulb", "mẹo": "lightbulb", "chìa khoá": "key", "key": "key",
    "link": "link", "liên kết": "link", "tag": "tag", "nhãn": "tag", "xem": "eye", "view": "eye",
    "đúng": "check", "check": "check", "hoàn thành": "circle-check", "done": "circle-check",
    "sai": "x", "loại": "x", "không": "x", "cấm": "circle-x",
    "cảnh báo": "triangle-alert", "warning": "triangle-alert", "lưu ý": "circle-alert",
    "thông tin": "info", "info": "info", "hỏi": "circle-question-mark",
    "khoá": "lock", "bảo mật": "shield", "an toàn": "shield", "mở khoá": "lock-open",
    "con trỏ": "mouse-pointer-2", "cursor": "mouse-pointer-2", "tay": "hand",
    "lấp lánh": "sparkles", "nghỉ": "umbrella", "biển": "umbrella", "nắng": "sun",
    "tập gym": "dumbbell", "gym": "dumbbell", "ăn": "utensils", "ngủ": "bed", "bay": "plane",
    # concrete objects (deterministic — keeps common concepts off the LLM)
    "bóng đèn": "lightbulb", "đèn": "lightbulb", "đồng hồ cát": "hourglass", "cát": "hourglass",
    "kính lúp": "search", "phóng to": "zoom-in", "thu nhỏ": "zoom-out",
    "giỏ hàng": "shopping-cart", "xe đẩy": "shopping-cart", "mua sắm": "shopping-bag",
    "quà tặng": "gift", "ổ khoá": "lock", "chìa": "key", "quả bom": "bomb", "bom": "bomb",
    "tên lửa": "rocket", "ngôi sao": "star", "trái tim": "heart", "pin": "battery",
    "nam châm": "magnet", "huy chương": "medal", "cúp": "trophy", "vương miện": "crown",
    "bản đồ": "map", "la bàn": "compass", "đám mây": "cloud", "mưa": "cloud-rain", "sấm": "zap",
    "núi": "mountain", "cây": "tree-pine", "nước": "droplet", "mặt trời": "sun", "mặt trăng": "moon",
    "đồng hồ": "clock", "máy ảnh": "camera", "video": "video", "nhạc": "music", "sách": "book-open",
    "bút": "pen", "thư": "mail", "chuông": "bell", "tiền mặt": "banknote", "thẻ": "credit-card",
    "mắt": "eye", "tay": "hand", "não": "brain", "robot": "bot", "cửa": "door-open",
    "gói hàng": "package", "giao hàng": "truck", "vé": "ticket", "lịch làm việc": "calendar-clock",
    "đám đông": "users", "cá nhân": "user", "công ty": "building-2", "nhà": "house", "văn phòng": "building",
    "bảo vệ": "shield-check", "cảnh sát": "shield", "y tế": "heart-pulse", "sức khoẻ": "heart-pulse",
    "giáo dục": "graduation-cap", "học": "graduation-cap", "khoá học": "graduation-cap",
}

# Badge glyphs (drawn as a corner chip). Colour follows the badge kind, not the tile role.
_BADGE = {"check": ("✓", "success"), "x": ("✕", "danger"), "warn": ("!", "caution"),
          "q": ("?", "info"), "star": ("★", "caution")}

# Concept → colour-emoji (Chromium renders these natively via the system emoji font). For the
# functional punctuation the reels use; extend freely. A raw emoji char in `char` also works.
EMOJI_ALIASES = {
    "warning": "⚠️", "cảnh báo": "⚠️", "lưu ý": "⚠️", "idea": "💡", "ý tưởng": "💡", "mẹo": "💡",
    "fire": "🔥", "hot": "🔥", "trend": "🔥", "money": "💰", "tiền": "💰", "chi phí": "💰",
    "chart": "📊", "biểu đồ": "📊", "thống kê": "📊", "gear": "⚙️", "cài đặt": "⚙️",
    "globe": "🌐", "web": "🌐", "toàn cầu": "🌐", "scale": "⚖️", "luật": "⚖️", "law": "⚖️",
    "point": "👉", "chỉ": "👉", "check": "✅", "đúng": "✅", "cross": "❌", "sai": "❌",
    "star": "⭐", "sao": "⭐", "rocket": "🚀", "bùng nổ": "🚀", "target": "🎯", "mục tiêu": "🎯",
    "sparkle": "✨", "warn2": "🚨", "clap": "👏", "brain": "🧠", "robot": "🤖", "ai": "🤖",
    "lock": "🔒", "key": "🔑", "phone": "📱", "mail": "📧", "bell": "🔔", "eyes": "👀",
}


def _role_hex(role):
    return bk.ROLES.get(role, bk.ROLES.get("emphasis"))


def _icon_svg(name):
    """Load a Lucide SVG for a file name OR any concept/word — the self-growing resolver maps the
    concept to the best icon, AUTO-FETCHES it if new, and learns it (so the library enriches itself).
    Strips width/height so CSS controls the size; keeps `currentColor` so the role colour tints it."""
    fn = ICON_ALIASES.get(str(name).lower().strip(), str(name))
    fn = os.path.basename(str(fn))                      # icon names are single tokens — strip any path
    p = os.path.join(ICON_DIR, f"{fn}.svg")             # traversal (e.g. an LLM-emitted '../') can't escape
    if not os.path.exists(p):
        try:                                            # resolve+fetch a NEW concept on demand
            import element_resolver as _r
            fn, _ = _r.resolve_icon(name)
            fn = os.path.basename(str(fn))
            p = os.path.join(ICON_DIR, f"{fn}.svg")
        except Exception:
            pass
    if not os.path.exists(p):
        p = os.path.join(ICON_DIR, "circle-dot.svg")   # neutral fallback
        if not os.path.exists(p):
            return ""
    svg = open(p, encoding="utf-8").read()
    svg = re.sub(r'\swidth="\d+"', ' width="100%"', svg, count=1)
    svg = re.sub(r'\sheight="\d+"', ' height="100%"', svg, count=1)
    return svg


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _element_html(spec):
    """Return the inner HTML for one element (positioned by the caller in a fl​ex root)."""
    t = spec.get("type", "icon_tile")
    role = spec.get("role", "emphasis")
    col = _role_hex(role)

    if t == "icon_tile":
        icon = _icon_svg(spec.get("icon", "circle-dot"))
        badge = ""
        bk_kind = spec.get("badge")
        if bk_kind in _BADGE:
            g, brole = _BADGE[bk_kind]
            badge = (f'<div class="badge" style="background:{_role_hex(brole)}">{g}</div>')
        elif bk_kind:                                   # a number/custom badge
            badge = f'<div class="badge" style="background:{col}">{_esc(bk_kind)}</div>'
        label = (f'<div class="tlabel">{_esc(spec["label"])}</div>' if spec.get("label") else "")
        return (f'<div class="wrap"><div class="tile" style="--c:{col}">'
                f'<div class="ico" style="color:{col}">{icon}</div>{badge}</div>{label}</div>')

    if t == "chip":
        icon = _icon_svg(spec["icon"]) if spec.get("icon") else ""
        ic = (f'<span class="cico" style="color:{col}">{icon}</span>' if icon else "")
        return (f'<div class="chip" style="--c:{col}">{ic}'
                f'<span class="ctext">{_esc(spec.get("label",""))}</span></div>')

    if t == "badge":
        g, brole = _BADGE.get(spec.get("kind", "check"), ("✓", "success"))
        c = _role_hex(spec.get("role", brole))
        return f'<div class="bigbadge" style="background:{c}">{g}</div>'

    if t == "sparkle":
        return (f'<svg class="spark" viewBox="0 0 100 100" style="color:{col}">'
                f'<path fill="currentColor" d="M50 2 L58 42 L98 50 L58 58 L50 98 L42 58 '
                f'L2 50 L42 42 Z"/></svg>')

    if t == "arrow":                                    # hand-drawn dashed curved arrow
        return (f'<svg class="arrow" viewBox="0 0 300 200" style="color:{col}">'
                f'<path fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round" '
                f'stroke-dasharray="2 16" d="M20 180 C 60 60, 180 40, 250 60"/>'
                f'<path fill="currentColor" d="M250 60 l-34 -6 l18 28 z"/></svg>')

    if t == "ring":                                     # proof highlight ring (rounded-rect stroke)
        w = int(spec.get("w", 360)); h = int(spec.get("h", 220))
        return (f'<svg class="ring" width="{w}" height="{h}" style="color:{col}">'
                f'<rect x="6" y="6" width="{w-12}" height="{h-12}" rx="26" fill="none" '
                f'stroke="currentColor" stroke-width="6" stroke-dasharray="3 14"/></svg>')

    if t == "emoji":                                    # native colour emoji (functional punctuation)
        ch = spec.get("char")
        if not ch:
            nm = str(spec.get("name", "")).lower().strip()
            ch = EMOJI_ALIASES.get(nm)
            if not ch:                                  # resolve any concept → emoji (learns it)
                try:
                    import element_resolver as _r
                    ch = _r.resolve_emoji(nm)
                except Exception:
                    ch = "✨"
        tw = _twemoji_svg(ch)                           # brand-consistent flat Twemoji if vendored
        # _esc the raw char too (spec["char"] is LLM/user-provided) — the one text insertion this file left
        # unescaped; a stray '<'/'&' would break the render. A real emoji codepoint is unchanged by _esc.
        return f'<div class="twemoji">{tw}</div>' if tw else f'<div class="emoji">{_esc(str(ch))}</div>'

    if t == "big_stat":                                 # a big number pop (money/stat)
        return (f'<div class="bigstat" style="color:{col}">{_esc(spec.get("value",""))}'
                f'<span class="bslabel">{_esc(spec.get("label",""))}</span></div>')

    if t == "tile3d":                                   # glossy pseudo-3D app-tile (iso-cube look)
        icon = _icon_svg(spec.get("icon", "box"))
        label = (f'<div class="tlabel">{_esc(spec["label"])}</div>' if spec.get("label") else "")
        return (f'<div class="wrap"><div class="tile3d" style="--c:{col}">'
                f'<div class="t3ico">{icon}</div></div>{label}</div>')

    if t == "phone":                                    # phone bezel (optionally wrapping a screenshot)
        src = spec.get("src")
        screen = ""
        if src and os.path.exists(src):
            screen = f'<img src="file:///{os.path.abspath(src).replace(os.sep, "/")}"/>'
        return f'<div class="phone"><div class="notch"></div><div class="screen">{screen}</div></div>'

    if t == "bracket":                                  # HUD corner brackets around a region
        w = int(spec.get("w", 420)); h = int(spec.get("h", 260)); s = 46
        L = (f'<svg class="brk" width="{w}" height="{h}" style="color:{col}">'
             f'<path fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round" '
             f'd="M8 {s} V8 H{s} M{w-s} 8 H{w-8} V{s} M{w-8} {h-s} V{h-8} H{w-s} M{s} {h-8} H8 V{h-s}"/></svg>')
        return L

    if t == "marker":                                   # marker highlight-swipe bar behind bold text
        return f'<div class="marker" style="background:{col}">{_esc(spec.get("label",""))}</div>'

    if t == "count_up":                                 # a number counting 0 → value (its own timeline)
        try:
            val = float(str(spec.get("value", 100)).replace(",", ""))
        except Exception:
            val = 100.0
        pre = json.dumps(str(spec.get("prefix", ""))); suf = json.dumps(str(spec.get("suffix", "")))
        lab = (f'<div class="culab">{_esc(spec["label"])}</div>' if spec.get("label") else "")
        return (f'<div class="wrap"><div class="countup" style="color:{col}">'
                f'<span id="cu">{_esc(spec.get("prefix",""))}{int(val)}{_esc(spec.get("suffix",""))}</span></div>{lab}'
                f'<script>window.__cu={{v:{val},pre:{pre},suf:{suf},ms:900}};'
                f'window.__seek=function(ms){{var p=Math.min(ms/window.__cu.ms,1);'
                f'document.getElementById("cu").textContent=window.__cu.pre+'
                f'Math.round(window.__cu.v*p).toLocaleString()+window.__cu.suf;}};</script>')

    if t == "confetti":                                 # celebration burst (own timeline)
        cols = [bk.ROLES["emphasis"], bk.ROLES["danger"], bk.ROLES["success"], bk.ROLES["caution"]]
        n = int(spec.get("count", 16))
        pieces = "".join(f'<i class="cf-p" style="background:{cols[i % 4]}"></i>' for i in range(n))
        return (f'<div class="confetti">{pieces}</div><script>(function(){{'
                f'var ps=document.querySelectorAll(".cf-p");window.__seek=function(ms){{var t=Math.min(ms/1200,1);'
                f'ps.forEach(function(el,i){{var a=(i/ps.length)*6.283,d=t*280*(0.55+0.45*((i*37)%10)/10);'
                f'el.style.transform="translate("+(Math.cos(a)*d)+"px,"+(Math.sin(a)*d-t*t*70)+"px) rotate("+(t*720*(i%2?1:-1))+"deg)";'
                f'el.style.opacity=(t<0.12?t/0.12:(t>0.72?Math.max(0,1-(t-0.72)/0.28):1));}});}};window.__seek(0);}})();</script>')

    if t == "kinetic":                                  # word-by-word pop-in text
        words = _esc(spec.get("text", "")).split()
        kw = str(spec.get("keyword", "")).lower()
        spans = "".join(f'<span class="kw" style="color:{col if w.lower().strip(".,!?") == kw else bk.INK}">{w}</span> '
                        for w in words)
        return (f'<div class="kinetic">{spans}</div><script>(function(){{'
                f'var sp=document.querySelectorAll(".kw"),n=sp.length,per=Math.min(90,700/Math.max(1,n));'
                f'window.__seek=function(ms){{sp.forEach(function(el,i){{var lt=Math.min(Math.max((ms-i*per)/300,0),1);'
                f'el.style.opacity=lt;el.style.transform="translateY("+((1-lt)*44)+"px) scale("+(0.55+0.45*lt)+")";}});}};'
                f'window.__seek(0);}})();</script>')

    if t == "pulse_ring":                               # attention ring (looping pulse)
        return (f'<div class="pring" style="border-color:{col}"></div><script>(function(){{'
                f'var e=document.querySelector(".pring");window.__seek=function(ms){{var t=(ms/900)%1;'
                f'e.style.transform="scale("+(0.5+t*1.15)+")";e.style.opacity=(1-t)*0.9;}};window.__seek(0);}})();</script>')

    if t == "progress_bar":                             # a bar filling 0 → value%
        val = float(spec.get("value", 80)); lab = _esc(spec.get("label", ""))
        return (f'<div class="pbarwrap"><div class="pbar"><div class="pbar-fill" style="background:{col}"></div></div>'
                f'<div class="pbar-lab">{lab}</div></div><script>(function(){{var v={val};'
                f'window.__seek=function(ms){{document.querySelector(".pbar-fill").style.width='
                f'(v*Math.min(ms/1100,1))+"%";}};window.__seek(0);}})();</script>')

    return f'<div style="color:{col}">{_esc(spec.get("label",""))}</div>'


def _css():
    ink = bk.INK
    return f"""
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:transparent; font-family:'Be Vietnam Pro','Segoe UI',sans-serif; }}
    #root {{ display:flex; align-items:center; justify-content:center; padding:40px; }}
    .wrap {{ display:flex; flex-direction:column; align-items:center; gap:16px; }}
    .tile {{ position:relative; width:200px; height:200px; border-radius:34px;
             background:linear-gradient(160deg,#ffffff, #f4f7ff);
             border:2px solid color-mix(in srgb, var(--c) 45%, #dfe6f5);
             box-shadow:0 10px 34px rgba(15,23,42,.14); display:flex; align-items:center; justify-content:center; }}
    .ico {{ width:104px; height:104px; }} .ico svg {{ width:100%; height:100%; stroke-width:2.1; }}
    .badge {{ position:absolute; top:-14px; right:-14px; min-width:52px; height:52px; padding:0 8px;
              border-radius:26px; color:#fff; font-weight:800; font-size:30px; display:flex;
              align-items:center; justify-content:center; box-shadow:0 6px 16px rgba(15,23,42,.22); }}
    .tlabel {{ font-weight:700; font-size:34px; color:{ink}; text-align:center; max-width:360px; }}
    .chip {{ display:inline-flex; align-items:center; gap:14px; padding:16px 30px; border-radius:999px;
             background:#fff; border:2px solid color-mix(in srgb,var(--c) 40%,#e3e9f5);
             box-shadow:0 8px 26px rgba(15,23,42,.12); }}
    .cico {{ width:44px; height:44px; display:inline-flex; }} .cico svg {{ width:100%; height:100%; stroke-width:2.2; }}
    .ctext {{ font-weight:700; font-size:38px; color:{ink}; }}
    .bigbadge {{ width:120px; height:120px; border-radius:60px; color:#fff; font-weight:800;
                 font-size:70px; display:flex; align-items:center; justify-content:center;
                 box-shadow:0 10px 26px rgba(15,23,42,.24); }}
    .emoji {{ font-size:150px; line-height:1; filter:drop-shadow(0 6px 14px rgba(15,23,42,.20)); }}
    .twemoji {{ width:150px; height:150px; filter:drop-shadow(0 6px 14px rgba(15,23,42,.20)); }}
    .twemoji svg {{ width:100%; height:100%; }}
    .spark {{ width:120px; height:120px; filter:drop-shadow(0 6px 14px rgba(15,23,42,.18)); }}
    .arrow {{ width:300px; height:200px; filter:drop-shadow(0 4px 10px rgba(15,23,42,.12)); }}
    .ring {{ filter:drop-shadow(0 6px 16px rgba(15,23,42,.14)); }}
    .bigstat {{ font-weight:900; font-size:150px; letter-spacing:-2px; line-height:.9;
                display:flex; flex-direction:column; align-items:center;
                text-shadow:0 8px 24px rgba(15,23,42,.16); }}
    .bslabel {{ font-size:34px; font-weight:700; color:{ink}; margin-top:10px; }}
    /* glossy pseudo-3D app-tile: role gradient face + stacked extrusion shadow + top gloss */
    .tile3d {{ position:relative; width:210px; height:210px; border-radius:46px; overflow:hidden;
               background:linear-gradient(150deg, color-mix(in srgb,var(--c) 78%,#ffffff),
                                                   color-mix(in srgb,var(--c) 100%,#000 6%));
               box-shadow:0 10px 0 color-mix(in srgb,var(--c) 55%,#000 30%),
                          0 26px 44px rgba(15,23,42,.30); display:flex; align-items:center; justify-content:center; }}
    .tile3d::before {{ content:""; position:absolute; inset:0; border-radius:46px;
                       background:linear-gradient(180deg, rgba(255,255,255,.45), rgba(255,255,255,0) 55%); }}
    .t3ico {{ position:relative; width:112px; height:112px; color:#fff; }}
    .t3ico svg {{ width:100%; height:100%; stroke-width:2.3; }}
    /* phone bezel */
    .phone {{ position:relative; width:300px; height:600px; border-radius:52px; background:#0F172A;
              padding:16px; box-shadow:0 20px 50px rgba(15,23,42,.34); }}
    .phone .notch {{ position:absolute; top:22px; left:50%; transform:translateX(-50%);
                     width:120px; height:26px; background:#0F172A; border-radius:16px; z-index:2; }}
    .phone .screen {{ width:100%; height:100%; border-radius:38px; overflow:hidden; background:#fff; }}
    .phone .screen img {{ width:100%; height:100%; object-fit:cover; }}
    .brk {{ filter:drop-shadow(0 4px 10px rgba(15,23,42,.12)); }}
    .marker {{ display:inline-block; padding:8px 26px; border-radius:10px; color:#fff; font-weight:800;
               font-size:52px; transform:skewX(-6deg); box-shadow:0 8px 22px rgba(15,23,42,.20); }}
    .countup {{ font-weight:900; font-size:150px; letter-spacing:-2px; line-height:.9;
                text-shadow:0 8px 24px rgba(15,23,42,.16); font-variant-numeric:tabular-nums; }}
    .culab {{ font-size:34px; font-weight:700; color:{ink}; margin-top:12px; text-align:center; }}
    .confetti {{ position:relative; width:360px; height:360px; display:flex; align-items:center; justify-content:center; }}
    .cf-p {{ position:absolute; width:22px; height:30px; border-radius:4px; transform-origin:center;
             box-shadow:0 3px 8px rgba(15,23,42,.16); }}
    .kinetic {{ max-width:840px; font-weight:900; font-size:80px; line-height:1.06; text-align:center; }}
    .kinetic .kw {{ display:inline-block; transform-origin:center; }}
    .pring {{ width:200px; height:200px; border:11px solid; border-radius:50%;
              filter:drop-shadow(0 6px 16px rgba(15,23,42,.14)); }}
    .pbarwrap {{ width:540px; }}
    .pbar {{ width:100%; height:34px; border-radius:99px; background:#E3E9F5; overflow:hidden;
             box-shadow:inset 0 2px 5px rgba(15,23,42,.10); }}
    .pbar-fill {{ height:100%; width:0; border-radius:99px; }}
    .pbar-lab {{ margin-top:18px; font-weight:800; font-size:38px; color:{ink}; }}
    """


def render_element(spec, out_png, *, scale=2):
    """Render ONE element spec to a transparent PNG. `spec.type` ∈ icon_tile/chip/badge/sparkle/
    arrow/ring/big_stat. Returns out_png. Auto-sizes the viewport to the element + shadow padding."""
    return render_many([(spec, out_png)], scale=scale)[0]


# ---------------------------------------------------------------- animated clips (rich motion)
# ffmpeg can slide/fade an overlay but NOT scale-overshoot / bounce / spin / kinetic. For those we
# render the element as a TRANSPARENT WebM: a seek-safe Web-Animation played frame-by-frame in
# Chromium (deterministic, like the faceless engine's GSAP) → VP9 yuva420p. This is how we hit
# CapCut-grade element motion natively — no CapCut, no human, headless.
CLIP_INSET = 100                      # motion headroom around the element (also the overlay offset)
_ANIM_KF = {
    "pop":    "[{transform:'scale(.3)',opacity:0},{transform:'scale(1.12)',opacity:1,offset:.62},{transform:'scale(1)',opacity:1}]",
    "bounce": "[{transform:'translateY(96px)',opacity:0},{transform:'translateY(-18px)',opacity:1,offset:.6},{transform:'translateY(0)',opacity:1}]",
    "spin":   "[{transform:'rotate(-28deg) scale(.4)',opacity:0},{transform:'rotate(6deg) scale(1.06)',opacity:1,offset:.7},{transform:'rotate(0) scale(1)',opacity:1}]",
    "slide-up":   "[{transform:'translateY(120px)',opacity:0},{transform:'translateY(0)',opacity:1}]",
    "slide-left": "[{transform:'translateX(150px)',opacity:0},{transform:'translateX(0)',opacity:1}]",
    "rise":   "[{transform:'translateY(60px)',opacity:0},{transform:'translateY(0)',opacity:1}]",
}


def render_element_clip(spec, out_webm, *, anim="pop", ent=0.5, dur=3.4, fps=25):
    """Render an element as a TRANSPARENT WebM with a rich entrance (pop/bounce/spin/…), held to `dur`.
    The element's REST top-left sits at (CLIP_INSET, CLIP_INSET) in the canvas, so the caller overlays
    the clip at (x-CLIP_INSET, y-CLIP_INSET). Returns out_webm (or None on failure)."""
    from playwright.sync_api import sync_playwright
    import subprocess, glob
    kf = _ANIM_KF.get(anim, _ANIM_KF["pop"]); vw, vh = 540, 700
    css = _css() + (f"\n#root{{align-items:flex-start;justify-content:flex-start;padding:{CLIP_INSET}px;}}"
                    f"\n#root>*{{transform-origin:center center;}}")
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body><div id="root">{_element_html(spec)}</div><script>'
            # if the element defined its OWN timeline (e.g. count_up), use it; else animate the root transform
            f'if(typeof window.__seek!=="function"){{const R=document.querySelector("#root>*");'
            f'const a=R.animate({kf},{{duration:{int(ent*1000)},fill:"both",'
            f'easing:"cubic-bezier(.2,.8,.25,1.15)"}});a.pause();'
            f'window.__seek=(ms)=>{{a.currentTime=Math.min(ms,{int(ent*1000)});}};}}window.__seek(0);'
            f'</script></body></html>')
    _d = tempfile.mkdtemp(prefix="elclip_")   # per-call dir: parallel renders share the system temp, so a
    tmp = os.path.join(_d, "clip.html")       # fixed html/frames name would collide (mixed frames = corrupt clip)
    open(tmp, "w", encoding="utf-8").write(html)
    fdir = os.path.join(_d, "frames")
    os.makedirs(fdir, exist_ok=True)
    for f in glob.glob(os.path.join(fdir, "*.png")):
        os.remove(f)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            pg = b.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=1)
            pg.goto("file:///" + tmp.replace("\\", "/"), wait_until="networkidle")
            n = int(ent * fps)
            for i in range(n + 1):
                pg.evaluate(f"window.__seek({(i / fps) * 1000:.1f})")
                pg.screenshot(path=os.path.join(fdir, f"f_{i:03d}.png"), omit_background=True)
            b.close()
    except Exception as e:
        print(f"[element clip] render failed ({e})"); return None
    try:
        import native_composer as _nc
        ff = _nc._ffmpeg_bin()
    except Exception:
        ff = "ffmpeg"
    hold = max(0.0, dur - ent)
    os.makedirs(os.path.dirname(os.path.abspath(out_webm)) or ".", exist_ok=True)
    # QuickTime qtrle = lossless RGBA — the RELIABLE alpha-video codec for ffmpeg overlay (VP9's
    # yuva420p silently drops alpha through filters). `.mov` container.
    ext = os.path.splitext(out_webm)[1].lower()
    if ext == ".webm":
        codec, pix = ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p"], "yuva420p"
    else:
        codec, pix = ["-c:v", "qtrle", "-pix_fmt", "argb"], "rgba"
    r = subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(fps),
                        "-i", os.path.join(fdir, "f_%03d.png"),
                        "-vf", f"tpad=stop_mode=clone:stop_duration={hold:.2f},format={pix}",
                        *codec, "-an", out_webm], capture_output=True, text=True)
    if not os.path.exists(out_webm):
        print(f"[element clip] ffmpeg failed: {(r.stderr or '')[-200:]}")
        return None
    return out_webm


def render_many(pairs, *, scale=2):
    """Render several (spec, out_png) pairs in ONE browser (faster for a whole video's elements)."""
    from playwright.sync_api import sync_playwright
    css = _css()
    outs = []
    _d = tempfile.mkdtemp(prefix="el_")   # per-call html scratch — parallel renders can't share a fixed name
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for spec, out_png in pairs:
            pg = None
            try:                                   # one bad element must not lose the whole batch of overlays
                html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>'
                        f'<body><div id="root">{_element_html(spec)}</div></body></html>')
                tmp = os.path.join(_d, "el.html")
                open(tmp, "w", encoding="utf-8").write(html)
                os.makedirs(os.path.dirname(os.path.abspath(out_png)) or ".", exist_ok=True)
                pg = b.new_page(viewport={"width": 900, "height": 700}, device_scale_factor=scale)
                pg.goto("file:///" + tmp.replace("\\", "/"), wait_until="networkidle")
                el = pg.query_selector("#root > *")
                (el or pg).screenshot(path=out_png, omit_background=True)  # transparent PNG, tight bbox
                outs.append(out_png)
            except Exception as _e:
                print(f"[element_maker] element render skipped ({type(_e).__name__}: {_e}).")
            finally:
                if pg is not None:
                    try: pg.close()
                    except Exception: pass
        b.close()
    return outs


LOTTIE_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "lottie")
_LOTTIE_JS = os.path.join(LOTTIE_DIR, "lottie.min.js")

# Concept (VN/EN) → a vendored Lottie animation (7_ASSETS/brand/lottie/*.json). So a caller/picker
# can request a rich motion-graphic by MEANING, e.g. a big-win beat → "ăn mừng" → fireworks.
LOTTIE_ALIASES = {
    "đúng": "check", "xong": "check", "check": "check", "tick": "check",
    "hoàn thành": "done", "done": "done", "thành công": "success", "success": "success",
    "ăn mừng": "fireworks", "chúc mừng": "fireworks", "celebration": "fireworks",
    "pháo hoa": "fireworks", "bùng nổ": "fireworks", "tuyệt vời": "fireworks",
    "thích": "thumbs-up", "like": "thumbs-up", "đồng ý": "thumbs-up",
    "tim": "heart", "yêu": "heart", "heart": "heart",
    "tiền": "coins", "xu": "coins", "money": "coins", "coins": "coins",
    "thông báo": "bell", "chuông": "bell", "bell": "bell", "nhắc": "bell",
    "tìm kiếm": "search", "search": "search", "lỗi": "error", "error": "error", "sai": "error",
    "tải xuống": "download", "download": "download", "gửi mail": "mail-sent", "đã gửi": "mail-sent",
    "đang tải": "loading", "loading": "loading", "chờ": "loading",
    "sao": "star", "star": "star", "mũi tên": "arrow", "arrow": "arrow",
    "rocket": "rocket-money", "lên đỉnh": "rocket-money", "tăng vọt": "rocket-money",
    "biểu đồ": "chart", "chart": "chart", "tăng trưởng": "chart", "thống kê": "chart",
    "đồng hồ": "clock", "thời gian": "clock", "clock": "clock", "đếm giờ": "clock",
    "thông báo": "notification", "notification": "notification", "nhắc nhở": "notification",
    "chiến thắng": "win", "thắng": "win", "vô địch": "win", "win": "win",
    "ý tưởng": "idea", "mẹo": "idea", "idea": "idea", "sáng tạo": "idea", "bóng đèn": "idea",
}


def render_lottie_clip(lottie_json, out_mov, *, w=320, h=320, dur=None, fps=25):
    """Render a Lottie animation (After-Effects JSON — the huge free LottieFiles ecosystem) to a
    TRANSPARENT `.mov` (qtrle) via the vendored lottie-web, seek-safe frame-by-frame. `lottie_json` =
    a path (abs, or a name under 7_ASSETS/brand/lottie/). Returns out_mov or None. Fully headless."""
    from playwright.sync_api import sync_playwright
    import subprocess, glob
    p = LOTTIE_ALIASES.get(str(lottie_json).lower().strip(), lottie_json)   # concept → animation
    if not os.path.isabs(p):
        cand = os.path.join(LOTTIE_DIR, p if str(p).endswith(".json") else str(p) + ".json")
        p = cand if os.path.exists(cand) else p
    if not os.path.exists(p) or not os.path.exists(_LOTTIE_JS):
        print(f"[lottie] missing json/lib: {p}"); return None
    data = open(p, encoding="utf-8").read()
    js = open(_LOTTIE_JS, encoding="utf-8").read()
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'*{{margin:0}}body{{background:transparent}}#c{{width:{w}px;height:{h}px}}</style>'
            f'<script>{js}</script></head><body><div id="c"></div><script>'
            f'const anim=lottie.loadAnimation({{container:document.getElementById("c"),'
            f'renderer:"svg",loop:false,autoplay:false,animationData:{data}}});'
            f'anim.addEventListener("DOMLoaded",()=>{{window.__dur=anim.getDuration()*1000;'
            f'window.__fr=anim.frameRate;window.__tf=anim.getDuration(true);'   # frames
            f'window.__seek=(ms)=>anim.goToAndStop(Math.min((ms/1000)*window.__fr,window.__tf-0.01),true);'
            f'window.__seek(0);window.__ready=true;}});</script></body></html>')
    _d = tempfile.mkdtemp(prefix="lottie_")   # per-call dir (parallel renders share system temp)
    tmp = os.path.join(_d, "lottie.html")
    open(tmp, "w", encoding="utf-8").write(html)
    fdir = os.path.join(_d, "frames")
    os.makedirs(fdir, exist_ok=True)
    for f in glob.glob(os.path.join(fdir, "*.png")):
        os.remove(f)
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)  # out = w×h
            pg.goto("file:///" + tmp.replace("\\", "/"), wait_until="networkidle")
            pg.wait_for_function("window.__ready===true", timeout=8000)
            total = dur if dur else (pg.evaluate("window.__dur") / 1000.0)
            n = int(total * fps)
            for i in range(n + 1):
                pg.evaluate(f"window.__seek({(i / fps) * 1000:.1f})")
                pg.screenshot(path=os.path.join(fdir, f"f_{i:03d}.png"), omit_background=True)
            b.close()
    except Exception as e:
        print(f"[lottie] render failed ({e})"); return None
    try:
        import native_composer as _nc
        ff = _nc._ffmpeg_bin()
    except Exception:
        ff = "ffmpeg"
    os.makedirs(os.path.dirname(os.path.abspath(out_mov)) or ".", exist_ok=True)
    subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(fps),
                    "-i", os.path.join(fdir, "f_%03d.png"), "-vf", "format=rgba",
                    "-c:v", "qtrle", "-pix_fmt", "argb", "-an", out_mov], capture_output=True, text=True)
    return out_mov if os.path.exists(out_mov) else None


if __name__ == "__main__":
    out = os.path.join(ROOT, "8_WORKSPACE", "element_previews")
    demo = [
        ({"type": "icon_tile", "icon": "clock", "role": "caution", "badge": "x", "label": "Mất thời gian"}, "tile_clock_x.png"),
        ({"type": "icon_tile", "icon": "rocket", "role": "success", "badge": "check", "label": "Tự động"}, "tile_rocket_ok.png"),
        ({"type": "chip", "icon": "search", "role": "emphasis", "label": "SEO"}, "chip_seo.png"),
        ({"type": "badge", "kind": "x"}, "badge_x.png"),
        ({"type": "sparkle", "role": "caution"}, "sparkle.png"),
        ({"type": "arrow", "role": "emphasis"}, "arrow.png"),
        ({"type": "big_stat", "role": "success", "value": "3 phút", "label": "thay vì 3 tiếng"}, "bigstat.png"),
    ]
    render_many([(s, os.path.join(out, f)) for s, f in demo])
    print("element previews →", out)
