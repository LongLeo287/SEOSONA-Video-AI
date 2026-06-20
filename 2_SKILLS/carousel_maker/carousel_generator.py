"""
SEOSONA Carousel Generator v2.0
================================
Generates pixel-accurate Facebook Carousel slides matching the SEOSONA & CQA brand design system.
Supports 6 slide archetypes: cover, comparison, numbered_content, process, feature_cards, grid.
"""
import os
import json
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
    """Highlight a keyword inside text with a colored span."""
    if not highlight or not text:
        return _html_escape(text)
    escaped = _html_escape(text)
    hl = _html_escape(highlight)
    if hl in escaped:
        return escaped.replace(hl, f'<span style="color:{color}">{hl}</span>')
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

# ─── SVG Icons (line/outline style matching the brand) ────────────

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
}

DEFAULT_ICON_LIST = ["document", "chart", "trend", "database", "refresh", "zap", "shield", "clock", "globe", "lock", "check", "target", "link", "settings"]


def _get_icon_svg(name: str) -> str:
    return ICONS.get(name, ICONS["star"])


def _logo_html(logo_uri: str, invert: bool = False) -> str:
    if not logo_uri:
        return ""
    filter_style = 'filter:brightness(0) invert(1);' if invert else ''
    return f'<img src="{logo_uri}" class="logo" style="{filter_style}" />'


# ─── CSS Base ─────────────────────────────────────────────────────

def _build_css(p: dict) -> str:
    """Generate the full CSS for all archetypes based on a palette dict."""
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,600;0,700;0,800;1,400;1,700&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
        width:1080px; height:1080px; overflow:hidden;
        font-family:'Be Vietnam Pro',sans-serif;
        background:{p['bg']};
        position:relative;
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

    /* ── Number Box ────── */
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
    .num-big {{
        font-size:120px; font-weight:800; color:{p['navy']};
        line-height:1; margin-right:24px;
    }}

    /* ── Cards ────── */
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
        color:{p['tag_ok_text']}; text-transform:uppercase;
        letter-spacing:2px; margin-bottom:16px;
    }}
    .tag-ok::before {{ content:'✅'; font-size:16px; }}
    .tag-bad {{
        display:inline-flex; align-items:center; gap:8px;
        background:{p['tag_bad_bg']}; border-radius:50px;
        padding:8px 20px; font-size:16px; font-weight:700;
        color:{p['tag_bad_text']}; text-transform:uppercase;
        letter-spacing:2px; margin-bottom:16px;
    }}
    .tag-bad::before {{ content:'❌'; font-size:16px; }}

    /* ── Closing Band ────── */
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

    /* ── Row Card (for process slides) ────── */
    .row-card {{
        display:flex; align-items:center; gap:20px;
        background:{p['card_bg']}; border-radius:18px;
        border:2px solid {p['card_border']};
        padding:22px 28px; margin-bottom:12px;
    }}
    .row-card .icon-wrap {{
        width:44px; height:44px; border-radius:12px;
        background:{p['number_bg']}; color:{p['blue']};
        display:flex; align-items:center; justify-content:center; flex-shrink:0;
    }}
    .row-card .rc-title {{
        font-size:28px; font-weight:700; color:{p['text']};
    }}
    .row-card .rc-desc {{
        font-size:22px; color:{p['text_sub']}; margin-top:4px;
    }}
    .row-card .rc-tag {{
        margin-left:auto; font-size:16px; font-weight:700;
        color:{p['blue']}; border:2px solid {p['card_border']};
        border-radius:50px; padding:6px 16px; white-space:nowrap;
    }}

    /* ── Feature Card (vertical stack) ────── */
    .feat-card {{
        display:flex; align-items:flex-start; gap:24px;
        background:{p['card_bg']}; border-radius:22px;
        border:2px solid {p['card_border']};
        box-shadow:0 6px 20px rgba(0,0,0,0.03);
        padding:32px 36px; margin-bottom:16px;
    }}
    .feat-card .icon-wrap {{
        width:50px; height:50px; border-radius:14px;
        background:{p['number_bg']}; color:{p['blue']};
        display:flex; align-items:center; justify-content:center; flex-shrink:0;
    }}
    .feat-card .fc-title {{
        font-size:30px; font-weight:700; color:{p['text']};
        margin-bottom:6px;
    }}
    .feat-card .fc-desc {{
        font-size:24px; color:{p['text_sub']}; line-height:1.5;
    }}

    /* ── Bullet List ────── */
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

    /* ── Stat Box ────── */
    .stat-row {{ display:flex; gap:16px; margin-top:20px; }}
    .stat-box {{
        flex:1; text-align:center; padding:20px 12px;
        border-radius:16px; border:2px solid {p['card_border']};
    }}
    .stat-box .num {{ font-size:48px; font-weight:800; color:{p['navy']}; }}
    .stat-box .lbl {{ font-size:16px; font-weight:600; color:{p['text_sub']}; margin-top:4px; }}

    /* ── Grid items ────── */
    .grid-2col {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
    .grid-item {{
        background:{p['card_bg']}; border-radius:14px;
        border:2px solid {p['card_border']};
        padding:18px 24px; font-size:24px; color:{p['text_sub']};
        display:flex; align-items:center; gap:10px;
    }}
    .grid-item .dot {{ width:10px; height:10px; border-radius:50%; background:{p['blue']}; flex-shrink:0; }}

    /* ── Quote Box ────── */
    .quote-box {{
        background:{p['card_bg']}; border-radius:20px;
        border:2px solid {p['card_border']};
        padding:28px 36px; font-size:28px; font-weight:600;
        color:{p['text']}; display:flex; align-items:center; gap:16px;
        margin-bottom:24px;
    }}
    .quote-box .q-icon {{
        width:44px; height:44px; border-radius:12px;
        background:{p['number_bg']}; color:{p['blue']};
        display:flex; align-items:center; justify-content:center; flex-shrink:0;
    }}
    """


# ─── Slide Renderers ──────────────────────────────────────────────

def _render_cover_dark(slide: dict, p: dict, logo_html: str, total: int) -> str:
    """Cover slide with dark navy background (SEOSONA style)."""
    title_html = _highlight(slide.get("title", ""), slide.get("highlight", ""), p["light_blue"])
    desc = _html_escape(slide.get("desc", ""))
    pill = _html_escape(slide.get("pill", ""))

    items_html = ""
    items = slide.get("items", [])
    if items:
        for i, item in enumerate(items):
            icon_name = item.get("icon", DEFAULT_ICON_LIST[i % len(DEFAULT_ICON_LIST)])
            items_html += f"""
            <div style="display:flex;align-items:center;gap:20px;padding:18px 0;border-bottom:1px solid rgba(255,255,255,0.1);">
                <span style="font-size:28px;font-weight:800;color:rgba(255,255,255,0.5);width:50px;">{i+1:02d}</span>
                <span style="font-size:28px;font-weight:700;color:white;flex:1;">{_html_escape(item.get('text', ''))}</span>
                <span style="color:rgba(255,255,255,0.4);">{_get_icon_svg(icon_name)}</span>
            </div>"""

    return f"""
    <div style="width:1080px;height:1080px;background:{p['cover_bg']};position:relative;overflow:hidden;">
        <div class="dot-grid-light"></div>
        {logo_html}
        <div style="position:absolute;top:50px;right:60px;">
            <div class="pill">{_html_escape(slide.get('tag', pill))}</div>
        </div>
        <div style="position:relative;z-index:5;padding:160px 80px 120px 80px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                <span style="width:10px;height:10px;border-radius:50%;background:{p['accent']};"></span>
                <span style="font-size:22px;font-weight:600;color:{p['light_blue']};letter-spacing:1px;">{_html_escape(slide.get('label', ''))}</span>
            </div>
            <h1 style="font-size:80px;font-weight:800;color:white;line-height:1.1;margin-bottom:24px;">{title_html}</h1>
            <div style="font-size:30px;color:rgba(255,255,255,0.7);line-height:1.5;border-left:5px solid {p['yellow']};padding-left:24px;margin-bottom:30px;">
                {desc}
            </div>
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


def _render_cover_light(slide: dict, p: dict, logo_html: str, total: int) -> str:
    """Cover slide with light background (CQA style) — includes comparison cards at bottom."""
    title_html = _highlight(slide.get("title", ""), slide.get("highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))

    left_card = slide.get("left_card", {})
    right_card = slide.get("right_card", {})
    cards_html = ""
    if left_card or right_card:
        cards_html = f"""
        <div style="display:flex;gap:16px;margin-top:32px;">
            <div style="flex:1;background:{p['tag_bad_bg']};border-radius:18px;padding:24px 28px;">
                <div style="font-size:16px;font-weight:700;color:{p['tag_bad_text']};text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                    {_html_escape(left_card.get('label', 'SEO TRUYỀN THỐNG'))}
                </div>
                <div style="font-size:24px;font-weight:700;color:{p['text']};">{_html_escape(left_card.get('text', ''))}</div>
            </div>
            <div style="flex:1;background:white;border-radius:18px;border:2px solid {p['card_border']};padding:24px 28px;">
                <div style="font-size:16px;font-weight:700;color:{p['tag_ok_text']};text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                    {_html_escape(right_card.get('label', 'SEO THỜI AI'))}
                </div>
                <div style="font-size:24px;font-weight:700;color:{p['text']};">{_html_escape(right_card.get('text', ''))}</div>
            </div>
        </div>"""

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>
        <div class="deco-circle"></div><div class="deco-circle-inner"></div>
        {logo_html}
        <div style="position:absolute;top:55px;right:60px;">
            <div class="pill-light">{_html_escape(slide.get('tag', slide.get('pill', '')))}</div>
        </div>
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
    """Numbered content slide with 2-column comparison cards."""
    num = slide.get("slide_number", f"{idx:02d}")
    label = _html_escape(slide.get("label", ""))
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])

    left = slide.get("left", {})
    right = slide.get("right", {})

    def _bullet_list(items, css_class="blue"):
        return '<ul class="bullet-list ' + css_class + '">' + "".join(f'<li><b>{_html_escape(b.split("**")[1] if "**" in b else "")}</b>{_html_escape(b.replace("**"+b.split("**")[1]+"**","") if "**" in b else b)}</li>' if "**" in b else f'<li>{_html_escape(b)}</li>' for b in items) + '</ul>'

    left_bullets = _bullet_list(left.get("items", []), "red")
    right_bullets = _bullet_list(right.get("items", []), "blue")

    # Build pagination dots
    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>
        <div class="deco-circle"></div><div class="deco-circle-inner"></div>
        {logo_html}
        <div style="position:relative;z-index:5;padding:150px 70px 120px 70px;">
            <div style="display:flex;align-items:flex-start;gap:24px;margin-bottom:30px;">
                <div class="num-box">{_html_escape(num)}</div>
                <div>
                    <div class="label">{label}</div>
                    <h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;">{heading_html}</h2>
                </div>
            </div>
            <div style="width:50px;height:5px;background:{p['navy']};border-radius:3px;margin-bottom:28px;margin-left:114px;"></div>
            <div style="display:flex;gap:16px;">
                <div class="card-pink" style="flex:1;">
                    <div class="tag-bad">{_html_escape(left.get('label', 'SEO TRUYỀN THỐNG'))}</div>
                    <div style="font-size:28px;font-weight:700;color:{p['text']};margin-bottom:16px;">{_html_escape(left.get('title', ''))}</div>
                    {left_bullets}
                </div>
                <div class="card" style="flex:1;">
                    <div class="tag-ok">{_html_escape(right.get('label', 'SEO THỜI AI'))}</div>
                    <div style="font-size:28px;font-weight:700;color:{p['accent']};margin-bottom:16px;">{_html_escape(right.get('title', ''))}</div>
                    {right_bullets}
                </div>
            </div>
        </div>
        <div class="pagination">{dots_html}</div>
        <div class="cta-arrow"><div class="circle">→</div></div>
    </div>"""


def _render_numbered_content(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    """Numbered content slide with single card panel + optional closing band."""
    num = slide.get("slide_number", f"{idx:02d}")
    label = _html_escape(slide.get("label", ""))
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))

    body_items = slide.get("body", [])
    if isinstance(body_items, str):
        body_items = [body_items]

    body_html = '<ul class="bullet-list blue">' + "".join(f'<li>{_html_escape(b)}</li>' for b in body_items) + '</ul>'

    # Optional 2x2 grid instead of list
    grid_items = slide.get("grid", [])
    if grid_items:
        body_html = '<div class="grid-2col">'
        for gi in grid_items:
            icon_name = gi.get("icon", "document")
            body_html += f"""
            <div style="display:flex;align-items:center;gap:14px;background:white;border-radius:14px;border:2px solid {p['card_border']};padding:18px 22px;">
                <span style="color:{p['blue']};">{_get_icon_svg(icon_name)}</span>
                <span style="font-size:24px;font-weight:600;color:{p['text']};">{_html_escape(gi.get('text', ''))}</span>
            </div>"""
        body_html += '</div>'

    closing_html = ""
    closing = slide.get("closing", "")
    if closing:
        cl_html = _highlight(closing, slide.get("closing_highlight", ""), p["yellow"])
        icon_name = slide.get("closing_icon", "lock")
        closing_html = f"""
        <div class="closing-band">
            <div class="icon-wrap">{_get_icon_svg(icon_name)}</div>
            <span>{cl_html}</span>
        </div>"""

    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>
        <div class="watermark">{_html_escape(num)}</div>
        {logo_html}
        <div style="position:relative;z-index:5;padding:150px 70px 120px 70px;">
            <div style="display:flex;align-items:flex-start;gap:20px;margin-bottom:12px;">
                <div class="num-big">{_html_escape(num)}</div>
                <div>
                    <div class="label">{label}</div>
                    <h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;">{heading_html}</h2>
                </div>
            </div>
            <div style="width:50px;height:5px;background:{p['navy']};border-radius:3px;margin:16px 0 20px 0;"></div>
            {"<p style='font-size:26px;color:" + p['text_sub'] + ";line-height:1.6;margin-bottom:24px;'>" + desc + "</p>" if desc else ""}
            <div class="card" style="padding:36px;">
                {body_html}
            </div>
            {closing_html}
        </div>
        <div class="pagination">{dots_html}</div>
        <div class="footer-bar">
            <span class="brand">{p['brand_name']} · <span style="font-weight:400;color:{p['footer_text']};">{p['brand_tagline']}</span></span>
        </div>
    </div>"""


def _render_process(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    """Process slide with numbered row cards and optional stats."""
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))

    steps = slide.get("steps", [])
    rows_html = ""
    for i, step in enumerate(steps):
        icon_name = step.get("icon", DEFAULT_ICON_LIST[i % len(DEFAULT_ICON_LIST)])
        tag_html = f'<span class="rc-tag">{_html_escape(step["tag"])}</span>' if step.get("tag") else ""
        desc_row = f'<div class="rc-desc">{_html_escape(step.get("desc", ""))}</div>' if step.get("desc") else ""
        rows_html += f"""
        <div class="row-card">
            <div class="num-box-dark">{i+1}</div>
            <div class="icon-wrap">{_get_icon_svg(icon_name)}</div>
            <div style="flex:1;">
                <div class="rc-title">{_html_escape(step.get('title', ''))}</div>
                {desc_row}
            </div>
            {tag_html}
        </div>"""

    stats = slide.get("stats", [])
    stats_html = ""
    if stats:
        stats_html = '<div class="stat-row">'
        for st in stats:
            stats_html += f'<div class="stat-box"><div class="num">{_html_escape(str(st.get("value", "")))}</div><div class="lbl">{_html_escape(st.get("label", ""))}</div></div>'
        stats_html += '</div>'

    page_tag = slide.get("page_tag", "")
    tag_html_top = f'<div class="pill-light" style="position:absolute;top:55px;right:60px;">{_html_escape(page_tag)}</div>' if page_tag else ""

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>
        {logo_html}
        {tag_html_top}
        <div style="position:relative;z-index:5;padding:140px 70px 120px 70px;">
            <div class="label">{_html_escape(slide.get('label', ''))}</div>
            <h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;margin-bottom:16px;">{heading_html}</h2>
            {"<p style='font-size:24px;color:" + p['text_sub'] + ";line-height:1.5;margin-bottom:20px;'>" + desc + "</p>" if desc else ""}
            {rows_html}
            {stats_html}
        </div>
        <div class="footer-bar">
            <span class="brand">{p['brand_name']} · <span style="font-weight:400;color:{p['footer_text']};">{p['brand_tagline']}</span></span>
        </div>
    </div>"""


def _render_feature_cards(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    """Feature/benefit slide with vertical card stack."""
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])
    desc = _html_escape(slide.get("desc", ""))

    features = slide.get("features", [])
    cards_html = ""
    for i, feat in enumerate(features):
        icon_name = feat.get("icon", DEFAULT_ICON_LIST[i % len(DEFAULT_ICON_LIST)])
        cards_html += f"""
        <div class="feat-card">
            <div class="icon-wrap">{_get_icon_svg(icon_name)}</div>
            <div>
                <div class="fc-title">{_html_escape(feat.get('title', ''))}</div>
                <div class="fc-desc">{_html_escape(feat.get('desc', ''))}</div>
            </div>
        </div>"""

    page_tag = slide.get("page_tag", "")
    tag_html_top = f'<div class="pill-light" style="position:absolute;top:55px;right:60px;">{_html_escape(page_tag)}</div>' if page_tag else ""

    dots_html = "".join(f'<div class="dot" style="width:28px;height:5px;border-radius:3px;background:{"#1A2DB5" if j == idx else "rgba(0,0,0,0.12)"};"></div>' for j in range(total))

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>
        {logo_html}
        {tag_html_top}
        <div style="position:relative;z-index:5;padding:140px 70px 120px 70px;">
            <div class="label">{_html_escape(slide.get('label', ''))}</div>
            <h2 style="font-size:55px;font-weight:800;color:{p['text']};line-height:1.15;margin-bottom:8px;">{heading_html}</h2>
            <div style="width:50px;height:5px;background:{p['navy']};border-radius:3px;margin-bottom:20px;"></div>
            {"<p style='font-size:24px;color:" + p['text_sub'] + ";line-height:1.5;margin-bottom:24px;'>" + desc + "</p>" if desc else ""}
            {cards_html}
        </div>
        <div class="pagination" style="gap:8px;">{dots_html}</div>
        <div style="position:absolute;bottom:50px;right:60px;font-size:22px;font-weight:600;color:{p['footer_text']};z-index:10;">
            {_html_escape(slide.get('footer_cta', 'Lưu lại & áp dụng'))}
        </div>
    </div>"""


def _render_grid(slide: dict, p: dict, logo_html: str, idx: int, total: int) -> str:
    """Grid slide with quote box + 2-column grid items + closing band."""
    num = slide.get("slide_number", f"{idx:02d}")
    heading_html = _highlight(slide.get("heading", ""), slide.get("heading_highlight", ""), p["accent"])

    quote = slide.get("quote", "")
    quote_html = ""
    if quote:
        quote_html = f"""
        <div class="quote-box">
            <div class="q-icon">{_get_icon_svg('question')}</div>
            <div>
                <div style="font-size:16px;font-weight:600;color:{p['text_sub']};text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">
                    {_html_escape(slide.get('quote_label', 'NGƯỜI DÙNG HỎI'))}
                </div>
                <div style="font-size:26px;font-weight:700;color:{p['text']};">"{_html_escape(quote)}"</div>
            </div>
        </div>"""

    grid_label = slide.get("grid_label", "")
    grid_items = slide.get("grid_items", [])
    grid_html = ""
    if grid_items:
        grid_html += f'<div style="font-size:18px;font-weight:700;color:{p["text_sub"]};text-transform:uppercase;letter-spacing:3px;text-align:center;margin-bottom:14px;">{_html_escape(grid_label)}</div>'
        grid_html += '<div class="grid-2col">'
        for gi in grid_items:
            grid_html += f'<div class="grid-item"><span class="dot"></span>{_html_escape(gi)}</div>'
        grid_html += '</div>'

    closing = slide.get("closing", "")
    closing_html = ""
    if closing:
        cl_html = _highlight(closing, slide.get("closing_highlight", ""), p["yellow"])
        closing_html = f"""
        <div class="closing-band" style="margin-top:24px;">
            <div class="icon-wrap">{_get_icon_svg(slide.get('closing_icon', 'star'))}</div>
            <span>{cl_html}</span>
        </div>"""

    dots_html = "".join(f'<div class="dot{"" if j != idx else " active"}"></div>' for j in range(total))

    return f"""
    <div style="width:1080px;height:1080px;background:{p['bg']};position:relative;overflow:hidden;">
        <div class="dot-grid"></div>
        {logo_html}
        <div style="position:relative;z-index:5;padding:150px 70px 120px 70px;">
            <div style="display:flex;align-items:flex-start;gap:20px;margin-bottom:24px;">
                <div class="num-box">{_html_escape(num)}</div>
                <div>
                    <div class="label">{_html_escape(slide.get('label', ''))}</div>
                    <h2 style="font-size:50px;font-weight:800;color:{p['text']};line-height:1.15;">{heading_html}</h2>
                </div>
            </div>
            {quote_html}
            {grid_html}
            {closing_html}
        </div>
        <div class="pagination">{dots_html}</div>
        <div style="position:absolute;bottom:50px;right:60px;z-index:10;">
            <span style="font-size:22px;font-weight:700;color:{p['navy']};">{p['brand_name']}</span>
        </div>
    </div>"""


# ─── Main Generator ───────────────────────────────────────────────

RENDERERS = {
    "cover":             None,  # dispatched to dark/light based on brand
    "cover_dark":        _render_cover_dark,
    "cover_light":       _render_cover_light,
    "comparison":        _render_comparison,
    "content":           _render_numbered_content,  # alias
    "numbered_content":  _render_numbered_content,
    "process":           _render_process,
    "feature_cards":     _render_feature_cards,
    "grid":              _render_grid,
}


def generate_carousel_slides(slide_data: list, output_dir: str, logo_path: str = None, brand: str = "seosona"):
    """
    Generates PNG images for each slide using Playwright.
    
    Args:
        slide_data: list of slide dicts, each with a "type" key.
        output_dir: directory to write PNGs.
        logo_path: absolute path to the brand logo image.
        brand: "seosona" or "cqa" — controls palette & cover style.
    """
    os.makedirs(output_dir, exist_ok=True)
    p = PALETTE.get(brand, PALETTE["seosona"])

    if logo_path and os.path.exists(logo_path):
        logo_uri = "file:///" + urllib.parse.quote(logo_path.replace('\\', '/'))
    else:
        logo_uri = ""

    css = _build_css(p)
    total = len(slide_data)

    base_html = f"""<!DOCTYPE html>
    <html><head><style>{css}</style></head>
    <body><div id="slide-container"></div></body></html>"""

    temp_html_path = os.path.join(output_dir, "temp_carousel.html")
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(base_html)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
            page.goto(f"file:///{temp_html_path.replace(chr(92), '/')}")

            for idx, slide in enumerate(slide_data):
                slide_type = slide.get("type", "content")

                # Dispatch cover to dark/light based on brand
                if slide_type == "cover":
                    if brand == "cqa":
                        renderer = _render_cover_light
                        logo_h = _logo_html(logo_uri, invert=False)
                    else:
                        renderer = _render_cover_dark
                        logo_h = _logo_html(logo_uri, invert=True)
                else:
                    renderer = RENDERERS.get(slide_type, _render_numbered_content)
                    logo_h = _logo_html(logo_uri, invert=False)

                if renderer is None:
                    renderer = _render_numbered_content

                # Call the renderer
                if slide_type in ("cover", "cover_dark", "cover_light"):
                    inner_html = renderer(slide, p, logo_h, total)
                else:
                    inner_html = renderer(slide, p, logo_h, idx, total)

                # Escape backticks for JS injection
                safe_html = inner_html.replace('`', '\\`').replace('${', '\\${')
                page.evaluate(f'document.getElementById("slide-container").innerHTML = `{safe_html}`')

                out_file = os.path.join(output_dir, f"slide_{idx+1:02d}.png")
                page.screenshot(path=out_file)
                print(f"[Carousel Generator] Rendered {out_file}")

            browser.close()

    except Exception as e:
        print(f"[Carousel Generator] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up temp file
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except OSError:
                pass


if __name__ == "__main__":
    demo_slides = [
        {
            "type": "cover",
            "pill": "AI AGENT FOR SEO",
            "tag": "AI AGENT FOR SEO",
            "label": "Đội ngũ AI Agent",
            "title": "5 năng lực thay đổi cách bạn làm SEO",
            "highlight": "thay đổi",
            "desc": "Một đội Agent làm việc 24/7 — từ nghiên cứu, sản xuất nội dung đến dự báo và tối ưu chi phí.",
            "items": [
                {"text": "Tự động hóa sản xuất nội dung", "icon": "document"},
                {"text": "Tối ưu phân tích & kỹ thuật SEO", "icon": "chart"},
            ]
        },
        {
            "type": "numbered_content",
            "slide_number": "01",
            "label": "NGUYÊN TẮC 01",
            "heading": "Đừng để AI tự nhớ, hãy cho AI dữ liệu để đọc",
            "heading_highlight": "tự nhớ",
            "desc": "LLM hoạt động dựa trên xác suất dự đoán từ tiếp theo.",
            "body": ["Báo cáo ngành", "File PDF", "Website tham khảo", "Dữ liệu nội bộ doanh nghiệp"],
            "closing": "Sau đó yêu cầu AI chỉ sử dụng các nguồn này để trả lời.",
            "closing_icon": "lock",
        },
        {
            "type": "feature_cards",
            "label": "COST & EFFICIENCY",
            "page_tag": "05 / 05 · AI AGENT FOR SEO",
            "heading": "Tiết kiệm chi phí & tăng hiệu suất",
            "heading_highlight": "chi phí",
            "features": [
                {"icon": "zap", "title": "Nhanh hơn nhiều lần", "desc": "Nghiên cứu từ khóa từ một tuần rút xuống còn vài giờ."},
                {"icon": "target", "title": "Tối ưu chi phí nhân sự", "desc": "Đội Agent thay tác vụ lặp lại."},
                {"icon": "clock", "title": "Sẵn sàng & chính xác 24/7", "desc": "Vận hành liên tục, không lỗi do mệt mỏi."},
            ],
            "footer_cta": "Lưu lại & áp dụng",
        }
    ]
    generate_carousel_slides(demo_slides, "./test_carousel_v2", brand="seosona")
