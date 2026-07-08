"""
SEOSONA Carousel Generator v2.1 (Dynamic Layouts)
==================================================
Generates pixel-accurate Facebook Carousel slides matching the SEOSONA & CQA brand design system.
Supports 8 slide archetypes: cover, comparison, numbered_content, process, feature_cards, grid, image_split, mockup_showcase.
Includes dynamic layout variations (randomized flips/alignments) based on slide index.
"""
import os
import urllib.parse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass


def _html_escape(text: str) -> str:
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;")


def _highlight(text: str, highlight: str, color: str) -> str:
    import re
    escaped = _html_escape(text)
    if highlight:
        hl = _html_escape(highlight)
        if hl:
            # WHOLE-WORD highlight, NOT a bare substring: `escaped.replace(hl, …)` wrapped the keyword INSIDE
            # another word — "AI" → "Em[AI]l", "SEO" → "[SEO]ul" — and hit ALL occurrences. \b uses Unicode
            # \w so it respects VN diacritics; a function replacement stops re interpreting a '\' / backref in
            # hl. If the keyword is never a standalone word, nothing is wrapped (better than breaking a word).
            repl = f'<span style="color:{color}">{hl}</span>'
            escaped = re.sub(r'\b' + re.escape(hl) + r'\b', lambda _m: repl, escaped)
    # Support strikethrough: ~~text~~ → <s>text</s>
    escaped = re.sub(r'~~(.+?)~~', r'<s>\1</s>', escaped)
    return escaped


# ─── Brand Palettes ───────────────────────────────────────────────

PALETTE = {
    "seosona": {
        "navy":        "#0A1F5C",
        "cover_bg":    "#1A2DB5",
        "accent":      "#00B4D8",
        "blue":        "#1565C0",
        "light_blue":  "#BBDEFB",
        "bg":          "#F5F7FB",
        "card_bg":     "#FFFFFF",
        "card_border": "#E5EAF2",
        "text":        "#0E1633",
        "text_sub":    "#5A6588",
        "yellow":      "#FFD54F",
        "number_bg":   "#E3ECFF",
        "number_text": "#1A2DB5",
        "tag_ok_bg":   "#EBF5FF",
        "tag_ok_text": "#1565C0",
        "tag_bad_bg":  "#FEF0EF",
        "tag_bad_text": "#E53935",
        "closing_bg":  "#1A2DB5",
        "footer_text": "#7B8DB5",
        "brand_name":  "SEOSONA",
        "brand_tagline": "Share to be shared more",
        "cta_text":    "Khám phá",
    },
    "cqa": {
        "navy":        "#1B3A8A",
        "cover_bg":    "#F0F4FA",
        "accent":      "#3B82F6",
        "blue":        "#2B5EA7",
        "light_blue":  "#BBDEFB",
        "bg":          "#F0F4FA",
        "card_bg":     "#FFFFFF",
        "card_border": "#E8EDF5",
        "text":        "#0E1633",
        "text_sub":    "#3A4A6B",
        "yellow":      "#FFD54F",
        "number_bg":   "#E3ECFF",
        "number_text": "#1B3A8A",
        "tag_ok_bg":   "#EBF5FF",
        "tag_ok_text": "#1565C0",
        "tag_bad_bg":  "#FEF0EF",
        "tag_bad_text": "#E53935",
        "closing_bg":  "#1A2DB5",
        "footer_text": "#7B8DB5",
        "brand_name":  "CHÍ QUYẾT ACADEMY",
        "brand_tagline": "",
        "cta_text":    "Vuốt xem",
    },
}

ICONS = {
    "document": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    "chart":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "trend":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "database": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "refresh":  '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>',
    "zap":      '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "shield":   '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "clock":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "globe":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "lock":     '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "check":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "target":   '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "link":     '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "question": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "star":     '<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.7"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    "settings": '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "image":    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
}

DEFAULT_ICON_LIST = ["document", "chart", "trend", "database", "refresh", "zap", "shield", "clock", "globe", "lock", "check", "target", "link", "settings"]


def _get_icon_svg(name: str) -> str:
    return ICONS.get(name, ICONS["star"])


def _logo_html(logo_uri: str, invert: bool = False) -> str:
    if not logo_uri:
        return ""
    filter_style = 'filter:brightness(0) invert(1);' if invert else ''
    return f'<img src="{logo_uri}" class="logo" style="{filter_style}" />'


def _resolve_image_uri(path: str) -> str:
    """Resolve an image path to a file URI if it exists, otherwise return empty."""
    if not path: return ""
    if path.startswith("http") or path.startswith("data:"): return path
    if os.path.exists(path):
        return "file:///" + urllib.parse.quote(os.path.abspath(path).replace('\\', '/'))
    return ""


# ─── CSS Base ─────────────────────────────────────────────────────

def _build_css(p: dict) -> str:
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,600;0,700;0,800;1,400;1,700&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
        width:1080px; height:1080px; overflow:hidden;
        font-family:'Be Vietnam Pro',sans-serif;
        background:{p['bg']}; position:relative;
    }}

    /* ── Shared ────── */
    .logo {{ position:absolute; top:55px; left:60px; height:55px; z-index:100; }}
    .dot-grid {{
        position:absolute; inset:0; z-index:0;
        background-image:radial-gradient(rgba(0,0,0,0.04) 1.5px,transparent 1.5px);
        background-size:28px 28px;
    }}
    .dot-grid-light {{
        position:absolute; inset:0; z-index:0;
        background-image:radial-gradient(rgba(255,255,255,0.08) 1.5px,transparent 1.5px);
        background-size:28px 28px;
    }}
    .deco-circle {{
        position:absolute; top:-60px; right:-60px; width:320px; height:320px;
        border-radius:50%; border:2px solid rgba(0,0,0,0.05); z-index:1;
    }}
    .deco-circle-inner {{
        position:absolute; top:10px; right:10px; width:240px; height:240px;
        border-radius:50%; border:2px solid rgba(0,0,0,0.03); z-index:1;
    }}
    .watermark {{
        position:absolute; bottom:30px; right:40px;
        font-size:280px; font-weight:800; color:rgba(0,0,0,0.04);
        line-height:1; z-index:1; font-family:'Be Vietnam Pro',sans-serif;
    }}
    .pagination {{
        position:absolute; bottom:55px; left:60px;
        display:flex; gap:10px; align-items:center; z-index:10;
    }}
    .pagination .dot {{
        width:12px; height:12px; border-radius:50%;
        background:rgba(0,0,0,0.12);
    }}
    .pagination .dot.active {{
        width:32px; border-radius:6px;
        background:{p['navy']};
    }}
    .cta-arrow {{
        position:absolute; bottom:50px; right:60px;
        display:flex; align-items:center; gap:12px;
        font-size:24px; font-weight:600; color:{p['text_sub']};
        z-index:10;
    }}
    .cta-arrow .circle {{
        width:42px; height:42px; border-radius:50%;
        background:{p['navy']}; color:white;
        display:flex; align-items:center; justify-content:center;
        font-size:20px;
    }}
    .footer-bar {{
        position:absolute; bottom:50px; left:60px; right:60px;
        border-top:2px solid {p['card_border']}; padding-top:18px;
        display:flex; justify-content:space-between; align-items:center;
        font-size:22px; font-weight:600; color:{p['footer_text']};
        z-index:10;
    }}
    .footer-bar .brand {{ color:{p['navy']}; font-weight:700; }}

    /* ── Labels & Pills ────── */
    .label {{
        font-size:20px; font-weight:700; color:{p['blue']};
        text-transform:uppercase; letter-spacing:3px; margin-bottom:8px;
    }}
    .pill {{
        display:inline-flex; align-items:center; gap:10px;
        background:rgba(255,255,255,0.1); border:2px solid rgba(255,255,255,0.25);
        border-radius:50px; color:white; padding:12px 32px;
        font-size:24px; font-weight:700; letter-spacing:1px;
    }}
    .pill-light {{
        display:inline-flex; align-items:center; gap:10px;
        background:{p['tag_ok_bg']}; border:2px solid {p['card_border']};
        border-radius:50px; color:{p['navy']}; padding:10px 28px;
        font-size:20px; font-weight:700; letter-spacing:1px;
    }}

    /* ── Cards & Elements ────── */
    .num-box {{
        width:90px; height:90px; border-radius:20px;
        background:{p['number_bg']}; color:{p['number_text']};
        display:flex; align-items:center; justify-content:center;
        font-size:48px; font-weight:800; flex-shrink:0;
    }}
    .num-box-dark {{
        width:52px; height:52px; border-radius:14px;
        background:linear-gradient(135deg,{p['navy']},{p['blue']});
        color:white; display:flex; align-items:center; justify-content:center;
        font-size:22px; font-weight:800; flex-shrink:0;
    }}
    .num-big {{ font-size:120px; font-weight:800; color:{p['navy']}; line-height:1; margin-right:24px; }}
    
    .card {{
        background:{p['card_bg']}; border-radius:24px;
        border:2px solid {p['card_border']};
        box-shadow:0 8px 30px rgba(0,0,0,0.04);
        padding:40px; position:relative;
    }}
    .card-pink {{
        background:#FEF5F4; border-radius:24px;
        border:2px solid #F5DEDA;
        padding:40px; position:relative;
    }}
    .tag-ok {{
        display:inline-flex; align-items:center; gap:8px;
        background:{p['tag_ok_bg']}; border-radius:50px;
        padding:8px 20px; font-size:16px; font-weight:700;
        color:{p['tag_ok_text']}; text-transform:uppercase; letter-spacing:2px; margin-bottom:16px;
    }}
    .tag-ok::before {{ content:'✅'; font-size:16px; }}
    .tag-bad {{
        display:inline-flex; align-items:center; gap:8px;
        background:{p['tag_bad_bg']}; border-radius:50px;
        padding:8px 20px; font-size:16px; font-weight:700;
        color:{p['tag_bad_text']}; text-transform:uppercase; letter-spacing:2px; margin-bottom:16px;
    }}
    .tag-bad::before {{ content:'❌'; font-size:16px; }}

    .closing-band {{
        background:{p['closing_bg']}; border-radius:20px;
        padding:28px 36px; color:white; font-size:28px;
        font-weight:600; display:flex; align-items:center; gap:16px;
        margin-top:32px;
    }}
    .closing-band .icon-wrap {{
        width:44px; height:44px; border-radius:12px;
        background:rgba(255,255,255,0.15); display:flex;
        align-items:center; justify-content:center; flex-shrink:0; color:white;
    }}

    .bullet-list {{ list-style:none; padding:0; }}
    .bullet-list li {{
        position:relative; padding-left:28px; margin-bottom:16px;
        font-size:28px; color:{p['text_sub']}; line-height:1.5;
    }}
    .bullet-list li::before {{
        content:''; position:absolute; left:0; top:10px;
        width:10px; height:10px; border-radius:50%;
    }}
    .bullet-list.blue li::before {{ background:{p['blue']}; }}
    .bullet-list.red li::before {{ background:{p['tag_bad_text']}; }}

    /* ── Visual/Image Elements ────── */
    .img-placeholder {{
        width:100%; height:100%; border-radius:18px;
        background:{p['number_bg']}; color:{p['blue']};
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        font-size:20px; font-weight:600; border:2px dashed {p['card_border']};
    }}
    .mac-window {{
        background:white; border-radius:16px; border:2px solid {p['card_border']};
        box-shadow:0 12px 40px rgba(0,0,0,0.08); overflow:hidden;
        display:flex; flex-direction:column;
    }}
    .mac-header {{
        height:36px; background:#F8FAFC; border-bottom:1px solid {p['card_border']};
        display:flex; align-items:center; padding:0 16px; gap:8px;
    }}
    .mac-dot {{ width:12px; height:12px; border-radius:50%; }}

    /* ── Process Row Cards ────── */
    .row-card {{
        display:flex; align-items:center; gap:16px;
        background:{p['card_bg']}; border-radius:16px;
        border:2px solid {p['card_border']};
        padding:16px 20px; margin-bottom:12px;
        box-shadow:0 4px 16px rgba(0,0,0,0.04);
    }}
    .icon-wrap {{
        width:44px; height:44px; border-radius:12px;
        background:{p['number_bg']}; color:{p['blue']};
        display:flex; align-items:center; justify-content:center;
        flex-shrink:0;
    }}
    .rc-title {{
        font-size:22px; font-weight:700; color:{p['text']};
        line-height:1.3;
    }}
    .rc-desc {{
        font-size:18px; color:{p['text_sub']}; margin-top:4px;
        line-height:1.4;
    }}
    .rc-tag {{
        display:inline-flex; padding:6px 16px;
        background:{p['tag_ok_bg']}; border-radius:50px;
        font-size:14px; font-weight:700; color:{p['tag_ok_text']};
        letter-spacing:1px; text-transform:uppercase; flex-shrink:0;
    }}

    /* ── Feature Cards ────── */
    .feat-card {{
        display:flex; align-items:flex-start; gap:20px;
        background:{p['card_bg']}; border-radius:18px;
        border:2px solid {p['card_border']};
        padding:24px 28px; margin-bottom:16px;
        box-shadow:0 6px 20px rgba(0,0,0,0.04);
    }}
    .fc-title {{
        font-size:26px; font-weight:700; color:{p['text']};
        line-height:1.3; margin-bottom:8px;
    }}
    .fc-desc {{
        font-size:20px; color:{p['text_sub']}; line-height:1.5;
    }}

    /* ── Grid 2-column ────── */
    .grid-2col {{
        display:grid; grid-template-columns:1fr 1fr;
        gap:16px;
    }}
    .grid-item {{
        display:flex; align-items:center; gap:12px;
        background:{p['card_bg']}; border-radius:14px;
        border:2px solid {p['card_border']};
        padding:18px 20px;
        font-size:22px; font-weight:600; color:{p['text']};
        box-shadow:0 4px 12px rgba(0,0,0,0.04);
    }}
    .grid-item .dot {{
        width:10px; height:10px; border-radius:50%;
        background:{p['blue']}; flex-shrink:0;
    }}
    """

# ─── Renderers (Text-Heavy Archetypes) ────────────────────────────

def _render_cover_dark(slide: dict, p: dict, logo_html: str, total: int, idx: int) -> str:
    title_html = _highlight(slide.get("title", ""), slide.get("highlight", ""), p["light_blue"])
    desc = _html_escape(slide.get("desc", ""))
    pill = _html_escape(slide.get("pill", ""))

    items_html = ""
    for i, item in enumerate(slide.get("items", [])):
        icon_name = item.get("icon", DEFAULT_ICON_LIST[i % len(DEFAULT_ICON_LIST)])
        items_html += f"""
        <div style="display:flex;align-items:center;gap:20px;padding:18px 0;border-bottom:1px solid rgba(255,255,255,0.1);">
            <span style="font-size:28px;font-weight:800;color:rgba(255,255,255,0.5);width:50px;">{i+1:02d}</span>
            <span style="font-size:28px;font-weight:700;color:white;flex:1;">{_html_escape(item.get('text', ''))}</span>
            <span style="color:rgba(255,255,255,0.4);">{_get_icon_svg(icon_name)}</span>
        </div>"""

    return f"""
    <div style="width:1080px;height:1080px;background:{p['cover_bg']};position:relative;overflow:hidden;">
        <div class="dot-grid-light"></div>{logo_html}
        <div style="position:absolute;top:50px;right:60px;"><div class="pill">{_html_escape(slide.get('tag', pill))}</div></div>
        <div style="position:relative;z-index:5;padding:160px 80px 120px 80px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                <span style="width:10px;height:10px;border-radius:50%;background:{p['accent']};"></span>
                <span style="font-size:22px;font-weight:600;color:{p['light_blue']};letter-spacing:1px;">{_html_escape(slide.get('label', ''))}</span>
            </div>
            <h1 style="font-size:80px;font-weight:800;color:white;line-height:1.1;margin-bottom:24px;">{title_html}</h1>
            <div style="font-size:30px;color:rgba(255,255,255,0.7);line-height:1.5;border-left:5px solid {p['yellow']};padding-left:24px;margin-bottom:30px;">{desc}</div>
            {items_html}
        </div>
        <div style="position:absolute;bottom:50px;left:60px;right:60px;display:flex;justify-content:space-between;align-items:center;z-index:10;">
            <span style="font-size:22px;font-weight:700;color:white;">{p['brand_name']} · <span style="font-weight:400;opacity:0.7;">{p['brand_tagline']}</span></span>
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:22px;font-weight:600;color:rgba(255,255,255,0.7);">{_html_escape(p['cta_text'])}</span>
                <div style="width:40px;height:40px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;">
                    <span style="color:{p['cover_bg']};font-size:18px;font-weight:700;">→</span>
                </div>
            </div>
        </div>
    </div>"""


def _render_cover_light(slide: dict, p: dict, logo_html: str, total: int, idx: int) -> str:
    title_html = _highlight(slide.get("title", ""), slide.get("highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))
    
    # Flip the bottom comparison cards randomly based on index
    left_card, right_card = slide.get("left_card", {}), slide.get("right_card", {})
    if idx % 2 == 1 and left_card and right_card: 
        left_card, right_card = right_card, left_card

    cards_html = ""
    if left_card or right_card:
        cards_html = f"""
        <div style="display:flex;gap:16px;margin-top:32px;">
            <div style="flex:1;background:{p['tag_bad_bg']};border-radius:18px;padding:24px 28px;">
                <div style="font-size:16px;font-weight:700;color:{p['tag_bad_text']};text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">{_html_escape(left_card.get('label', ''))}</div>
                <div style="font-size:24px;font-weight:700;color:{p['text']};">{_html_escape(left_card.get('text', ''))}</div>
            </div>
            <div style="flex:1;background:white;border-radius:18px;border:2px solid {p['card_border']};padding:24px 28px;">
                <div style="font-size:16px;font-weight:700;color:{p['tag_ok_text']};text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">{_html_escape(right_card.get('label', ''))}</div>
                <div style="font-size:24px;font-weight:700;color:{p['text']};">{_html_escape(right_card.get('text', ''))}</div>
            </div>
        </div>"""

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div><div class="deco-circle"></div><div class="deco-circle-inner"></div>
        {logo_html}
        <div style="position:absolute;top:55px;right:60px;"><div class="pill-light">{_html_escape(slide.get('tag', slide.get('pill', '')))}</div></div>
        <div style="position:relative;z-index:5;padding:160px 80px 140px 80px;">
            <h1 style="font-size:85px;font-weight:800;color:{p['navy']};line-height:1.1;margin-bottom:12px;">{title_html}</h1>
            <div style="font-size:28px;color:{p['text_sub']};line-height:1.6;margin-bottom:10px;">{desc}</div>
            {cards_html}
        </div>
        <div class="footer-bar">
            <span class="brand">{p['brand_name']}</span>
            <span>{_html_escape(p['cta_text'])} <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:{p['card_border']};align-items:center;justify-content:center;margin-left:8px;">→</span></span>
        </div>
    </div>"""


def _render_comparison(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    num = slide.get("slide_number", f"{idx:02d}")
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    left, right = slide.get("left", {}), slide.get("right", {})

    # Random layout flip: side-by-side OR vertical stack if text is short
    is_vertical = (idx % 3 == 0)

    def _ul(items, cl="blue"): return f'<ul class="bullet-list {cl}">' + "".join(f'<li>{_html_escape(b)}</li>' for b in items) + '</ul>'
    
    if is_vertical:
        layout_html = f"""
        <div style="display:flex;flex-direction:column;gap:16px;">
            <div class="card-pink" style="padding:28px 40px;"><div class="tag-bad">{_html_escape(left.get('label',''))}</div><div style="font-size:26px;font-weight:700;color:{p['text']};">{_html_escape(left.get('title',''))}</div>{_ul(left.get('items',[]), 'red')}</div>
            <div class="card" style="padding:28px 40px;"><div class="tag-ok">{_html_escape(right.get('label',''))}</div><div style="font-size:26px;font-weight:700;color:{p['accent']};">{_html_escape(right.get('title',''))}</div>{_ul(right.get('items',[]), 'blue')}</div>
        </div>"""
    else:
        layout_html = f"""
        <div style="display:flex;gap:16px;">
            <div class="card-pink" style="flex:1;"><div class="tag-bad">{_html_escape(left.get('label',''))}</div><div style="font-size:28px;font-weight:700;color:{p['text']};margin-bottom:16px;">{_html_escape(left.get('title',''))}</div>{_ul(left.get('items',[]), 'red')}</div>
            <div class="card" style="flex:1;"><div class="tag-ok">{_html_escape(right.get('label',''))}</div><div style="font-size:28px;font-weight:700;color:{p['accent']};margin-bottom:16px;">{_html_escape(right.get('title',''))}</div>{_ul(right.get('items',[]), 'blue')}</div>
        </div>"""

    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))
    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div><div class="deco-circle"></div><div class="deco-circle-inner"></div>
        {logo_html}
        <div style="position:relative;z-index:5;padding:150px 70px 120px 70px;">
            <div style="display:flex;align-items:flex-start;gap:24px;margin-bottom:20px;">
                <div class="num-box">{_html_escape(num)}</div>
                <div><div class="label">{_html_escape(slide.get('label', ''))}</div><h2 style="font-size:50px;font-weight:800;color:{p['text']};line-height:1.15;">{heading_html}</h2></div>
            </div>
            {layout_html}
        </div>
        <div class="pagination">{dots_html}</div><div class="cta-arrow"><div class="circle">→</div></div>
    </div>"""


def _render_numbered_content(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    num = slide.get("slide_number", f"{idx:02d}")
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))

    # Randomly center-align text if no grid and short body
    body_items = slide.get("body", [])
    if isinstance(body_items, str): body_items = [body_items]
    is_centered = (idx % 2 == 1 and len(body_items) <= 2)

    align_css = "text-align:center; display:flex; flex-direction:column; align-items:center;" if is_centered else ""
    list_align = "list-style:none; padding:0;" if is_centered else "" # centered lists drop the blue dot
    
    body_html = f'<ul class="bullet-list blue" style="{list_align}">' + "".join(f'<li style="{"padding-left:0;::before{display:none;}" if is_centered else ""}">{_html_escape(b)}</li>' for b in body_items) + '</ul>'

    grid_items = slide.get("grid", [])
    if grid_items:
        align_css = ""
        body_html = '<div class="grid-2col">' + "".join(f'<div style="display:flex;align-items:center;gap:14px;background:white;border-radius:14px;border:2px solid {p["card_border"]};padding:18px 22px;"><span style="color:{p["blue"]};">{_get_icon_svg(gi.get("icon", "document"))}</span><span style="font-size:24px;font-weight:600;color:{p["text"]};">{_html_escape(gi.get("text", ""))}</span></div>' for gi in grid_items) + '</div>'

    closing_html = ""
    if slide.get("closing"):
        cl_html = _highlight(slide.get("closing", ""), slide.get("closing_highlight", ""), p["yellow"])
        closing_html = f'<div class="closing-band"><div class="icon-wrap">{_get_icon_svg(slide.get("closing_icon", "lock"))}</div><span>{cl_html}</span></div>'

    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))
    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div><div class="watermark">{_html_escape(num)}</div>{logo_html}
        <div style="position:relative;z-index:5;padding:150px 70px 120px 70px;">
            <div style="display:flex;align-items:flex-start;gap:20px;margin-bottom:12px;">
                <div class="num-big">{_html_escape(num)}</div>
                <div><div class="label">{_html_escape(slide.get('label', ''))}</div><h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;">{heading_html}</h2></div>
            </div>
            <div style="width:50px;height:5px;background:{p['navy']};border-radius:3px;margin:16px 0 20px 0;"></div>
            {"<p style='font-size:26px;color:" + p['text_sub'] + ";line-height:1.6;margin-bottom:24px;'>" + desc + "</p>" if desc else ""}
            <div class="card" style="padding:36px; {align_css}">{body_html}</div>
            {closing_html}
        </div>
        <div class="pagination">{dots_html}</div>
        <div class="footer-bar"><span class="brand">{p['brand_name']} · <span style="font-weight:400;color:{p['footer_text']};">{p['brand_tagline']}</span></span></div>
    </div>"""


# ─── Renderers (Visual/Dynamic Archetypes) ─────────────────────────

def _render_image_split(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    """A 50/50 split layout. Randomly flips left/right."""
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))
    
    img_uri = _resolve_image_uri(slide.get("image", ""))
    img_html = f'<img src="{img_uri}" style="width:100%;height:100%;object-fit:cover;border-radius:18px;" />' if img_uri else f'<div class="img-placeholder">{_get_icon_svg("image")}<div style="margin-top:12px;">Ảnh minh hoạ</div></div>'

    body_items = slide.get("body", [])
    body_html = f'<ul class="bullet-list blue">' + "".join(f'<li>{_html_escape(b)}</li>' for b in body_items) + '</ul>'

    text_col = f"""
    <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div class="label">{_html_escape(slide.get('label', ''))}</div>
        <h2 style="font-size:46px;font-weight:800;color:{p['text']};line-height:1.2;margin-bottom:16px;">{heading_html}</h2>
        {"<p style='font-size:24px;color:" + p['text_sub'] + ";line-height:1.5;margin-bottom:24px;'>" + desc + "</p>" if desc else ""}
        {body_html}
    </div>"""
    
    img_col = f'<div style="flex:1; padding:16px; background:white; border-radius:24px; border:2px solid {p["card_border"]}; box-shadow:0 10px 30px rgba(0,0,0,0.05);">{img_html}</div>'

    # Random flip
    content_html = f"{img_col}{text_col}" if idx % 2 == 0 else f"{text_col}{img_col}"
    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>{logo_html}
        <div style="position:relative;z-index:5;padding:160px 70px 120px 70px;height:100%;display:flex;gap:40px;align-items:stretch;">
            {content_html}
        </div>
        <div class="pagination">{dots_html}</div>
        <div class="footer-bar"><span class="brand">{p['brand_name']}</span></div>
    </div>"""


def _render_mockup_showcase(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    """Browser/UI mockup window."""
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))
    
    img_uri = _resolve_image_uri(slide.get("image", ""))
    img_html = f'<img src="{img_uri}" style="width:100%;height:auto;display:block;" />' if img_uri else f'<div class="img-placeholder" style="height:400px;border:none;">{_get_icon_svg("image")}<div style="margin-top:12px;">App Screenshot</div></div>'

    # Mockup frame
    mockup_html = f"""
    <div class="mac-window">
        <div class="mac-header">
            <div class="mac-dot" style="background:#FF5F56;"></div><div class="mac-dot" style="background:#FFBD2E;"></div><div class="mac-dot" style="background:#27C93F;"></div>
        </div>
        <div style="background:white;">{img_html}</div>
    </div>"""

    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div><div class="deco-circle" style="top:auto;bottom:-60px;"></div>{logo_html}
        <div style="position:relative;z-index:5;padding:150px 70px 120px 70px;">
            <div style="text-align:center;margin-bottom:32px;">
                <div class="label">{_html_escape(slide.get('label', ''))}</div>
                <h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;margin-bottom:12px;">{heading_html}</h2>
                {"<p style='font-size:26px;color:" + p['text_sub'] + ";'>" + desc + "</p>" if desc else ""}
            </div>
            {mockup_html}
        </div>
        <div class="pagination">{dots_html}</div>
        <div class="footer-bar"><span class="brand">{p['brand_name']}</span></div>
    </div>"""


# ─── Simple Fallbacks for other archetypes ────────────────────────

def _render_process(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    
    rows_list = []
    for i, step in enumerate(slide.get("steps", [])):
        desc_html = f'<div class="rc-desc">{_html_escape(step.get("desc", ""))}</div>' if step.get("desc") else ""
        tag_html = f'<span class="rc-tag">{_html_escape(step["tag"])}</span>' if step.get("tag") else ""
        # Inline badge (e.g., RAG, MCP) next to title
        badge_html = f'<span style="display:inline-flex;padding:4px 14px;background:{p["number_bg"]};color:{p["blue"]};border-radius:6px;font-size:16px;font-weight:800;letter-spacing:1px;margin-left:10px;vertical-align:middle;">{_html_escape(step["badge"])}</span>' if step.get("badge") else ""
        # Right-side tag (e.g., VAI TRÒ, SỰ THẬT) as pill
        right_tag_html = f'<span style="display:inline-flex;padding:6px 18px;border:1.5px solid {p["card_border"]};border-radius:50px;font-size:16px;font-weight:700;color:{p["text_sub"]};letter-spacing:1px;text-transform:uppercase;white-space:nowrap;flex-shrink:0;">{_html_escape(step["right_tag"])}</span>' if step.get("right_tag") else ""
        rows_list.append(f'<div class="row-card"><div class="num-box-dark">{i+1}</div><div class="icon-wrap">{_get_icon_svg(step.get("icon", "check"))}</div><div style="flex:1;"><div class="rc-title">{_html_escape(step.get("title", ""))}{badge_html}</div>{desc_html}</div>{right_tag_html}{tag_html}</div>')
    
    # Stats row at bottom
    stats = slide.get("stats", [])
    stats_html = ""
    if stats:
        stats_items = "".join(f'<div style="flex:1;background:white;border-radius:18px;border:2px solid {p["card_border"]};padding:20px;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,0.04);"><div style="font-size:48px;font-weight:900;color:{p["navy"]};line-height:1;">{_html_escape(s.get("value",""))}</div><div style="font-size:16px;font-weight:700;color:{p["text_sub"]};margin-top:8px;text-transform:uppercase;letter-spacing:1px;">{_html_escape(s.get("label",""))}</div></div>' for s in stats)
        stats_html = f'<div style="display:flex;gap:14px;margin-top:20px;">{stats_items}</div>'

    rows_html = "".join(rows_list)
    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))
    return f"""<div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;"><div class="dot-grid"></div>{logo_html}<div style="position:relative;z-index:5;padding:140px 70px 120px 70px;"><div class="label">{_html_escape(slide.get('label', ''))}</div><h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;margin-bottom:20px;">{heading_html}</h2>{rows_html}{stats_html}</div><div class="pagination">{dots_html}</div><div class="footer-bar"><span class="brand">{p['brand_name']} · <span style="font-weight:400;color:{p['footer_text']};">{p['brand_tagline']}</span></span></div></div>"""


def _render_feature_cards(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    # Existing feature_cards implementation...
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    cards_html = "".join(f'<div class="feat-card"><div class="icon-wrap">{_get_icon_svg(feat.get("icon", "star"))}</div><div><div class="fc-title">{_html_escape(feat.get("title", ""))}</div><div class="fc-desc">{_html_escape(feat.get("desc", ""))}</div></div></div>' for feat in slide.get("features", []))
    return f"""<div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;"><div class="dot-grid"></div>{logo_html}<div style="position:relative;z-index:5;padding:140px 70px 120px 70px;"><div class="label">{_html_escape(slide.get('label', ''))}</div><h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;margin-bottom:20px;">{heading_html}</h2>{cards_html}</div><div class="footer-bar"><span class="brand">{p['brand_name']}</span></div></div>"""

def _render_grid(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    # Existing grid implementation...
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    grid_html = '<div class="grid-2col">' + "".join(f'<div class="grid-item"><span class="dot"></span>{_html_escape(gi)}</div>' for gi in slide.get("grid_items", [])) + '</div>'
    return f"""<div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;"><div class="dot-grid"></div>{logo_html}<div style="position:relative;z-index:5;padding:150px 70px 120px 70px;"><div class="label">{_html_escape(slide.get('label', ''))}</div><h2 style="font-size:50px;font-weight:800;color:{p['text']};line-height:1.15;margin-bottom:24px;">{heading_html}</h2>{grid_html}</div><div class="footer-bar"><span class="brand">{p['brand_name']}</span></div></div>"""


RENDERERS = {
    "cover":             None,
    "cover_dark":        _render_cover_dark,
    "cover_light":       _render_cover_light,
    "comparison":        _render_comparison,
    "content":           _render_numbered_content,
    "numbered_content":  _render_numbered_content,
    "process":           _render_process,
    "feature_cards":     _render_feature_cards,
    "grid":              _render_grid,
    "image_split":       _render_image_split,
    "mockup_showcase":   _render_mockup_showcase,
}

def generate_carousel_slides(slide_data: list, output_dir: str, logo_path: str = None, brand: str = "seosona"):
    os.makedirs(output_dir, exist_ok=True)
    p = PALETTE.get(brand, PALETTE["seosona"])
    logo_uri = "file:///" + urllib.parse.quote(logo_path.replace('\\', '/')) if logo_path and os.path.exists(logo_path) else ""
    css = _build_css(p)
    total = len(slide_data)
    base_html = f"<!DOCTYPE html><html><head><style>{css}</style></head><body><div id=\"slide-container\"></div></body></html>"
    # UNIQUE temp name (atomic mkstemp) — a fixed "temp_carousel.html" would be clobbered when two carousel
    # renders hit the same output_dir at once (the factory runs renders as parallel subprocesses) → corrupt slides.
    import tempfile as _tf
    _fd, temp_html_path = _tf.mkstemp(prefix="temp_carousel_", suffix=".html", dir=output_dir)
    os.close(_fd)
    with open(temp_html_path, 'w', encoding='utf-8') as f: f.write(base_html)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
            page.goto(f"file:///{temp_html_path.replace(chr(92), '/')}")

            for idx, slide in enumerate(slide_data):
                slide_type = slide.get("type", "content")
                if slide_type == "cover":
                    renderer = _render_cover_light if brand == "cqa" else _render_cover_dark
                    logo_h = _logo_html(logo_uri, invert=(brand != "cqa"))
                else:
                    renderer = RENDERERS.get(slide_type, _render_numbered_content)
                    logo_h = _logo_html(logo_uri, invert=False)

                if slide_type in ("cover", "cover_dark", "cover_light"):
                    inner_html = renderer(slide, p, logo_h, total, idx)
                else:
                    inner_html = renderer(slide, p, logo_h, idx, total)

                safe_html = inner_html.replace('`', '\\`').replace('${', '\\${')
                page.evaluate(f'document.getElementById("slide-container").innerHTML = `{safe_html}`')
                out_file = os.path.join(output_dir, f"slide_{idx+1:02d}.png")
                page.screenshot(path=out_file)
                print(f"[Carousel Generator] Rendered {out_file}")
            browser.close()
    except Exception as e:
        print(f"[Carousel Generator] Error: {e}")
    finally:
        if os.path.exists(temp_html_path):
            try: os.remove(temp_html_path)
            except OSError: pass

if __name__ == "__main__":
    demo_slides = [
        {
            "type": "image_split",
            "label": "GIAO DIỆN MỚI",
            "heading": "Thiết kế chia đôi linh hoạt",
            "heading_highlight": "chia đôi",
            "desc": "Bố cục ngẫu nhiên lật trái/phải để tránh sự nhàm chán.",
            "body": ["Hỗ trợ ảnh Placeholder", "Tự động bo góc", "Drop shadow tinh tế"],
            "image": ""
        },
        {
            "type": "mockup_showcase",
            "label": "DEMO SẢN PHẨM",
            "heading": "Nhúng ảnh vào Mockup Trình duyệt",
            "heading_highlight": "Mockup",
            "desc": "Tự động bao bọc ảnh bằng khung macOS cực kỳ chuyên nghiệp.",
            "image": ""
        }
    ]
    generate_carousel_slides(demo_slides, "./test_carousel_v2", brand="seosona")
