"""
SEOSONA THUMBNAIL — one module, one pipeline, one public entry point.
=====================================================================

    make_thumbnail(content, output_path, aspect_ratio, brand, ...)

    content text → NLP variables (key-normalized) → highlight tuples → HTML render → PNG

Everything thumbnail-related lives here: the brand palettes, the NLP wiring, the
keyword/highlight logic, and the Playwright HTML render. The two HTML files under
`templates/` are layout *assets* (portrait 9:16 + landscape 16:9), selected by aspect.

Callers (video_engine, course_video, workflow_thumbnail) call ONLY `make_thumbnail`.
Everything else in this module is private (`_`-prefixed). See 6_SOP/thumbnail_sop.md.
"""
import os
import re
import sys
import importlib
from html import escape as _hesc            # aliased: the render fn uses a local `html` var for the template
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Brand ────────────────────────────────────────────────────────────────────
BRAND_PALETTES = {
    "seosona": {
        "navy": "#1A2DB5", "blue": "#1565C0", "light_blue": "#BBDEFB", "yellow": "#FFD54F",
        "logo_path": "7_ASSETS/brand/logos/Seosona_Logo.png",
        "watermark": "SEO", "brand_name": "SEOSONA",
        "brand_tagline": "Share to be shared more",
        "brand_tagline_upper": "SHARE TO BE SHARED MORE",
    },
    "cqa": {
        "navy": "#1B3A8A", "blue": "#2B5EA7", "light_blue": "#BBDEFB", "yellow": "#FFD54F",
        "logo_path": "7_ASSETS/brand/logos/Chi Quyet Academy Mascot Logo.png",
        "watermark": "CQA", "brand_name": "CHÍ QUYẾT ACADEMY",
        "brand_tagline": "", "brand_tagline_upper": "",
    },
}

# Layouts the templates understand. Anything else collapses to "auto".
_VALID_LAYOUTS = {"auto", "portrait", "text_only", "card"}

# Canonical NLP variable names → aliases the LLM (or offline NLP) might emit.
# generate_json_from_prompt returns raw parsed JSON with NO key normalization and the
# online (Gemini) path is unconstrained, so we accept every reasonable spelling/casing.
_ALIASES = {
    "top_label":       ["top_label", "pill_label", "label", "kicker"],
    "main_title":      ["main_title", "title", "headline"],
    "title_highlight": ["title_highlight", "title_highlight_keyword", "highlight", "keyword"],
    "hook":            ["hook", "short_hook"],
    "cta":             ["cta", "cta_text"],
    "cta_highlight":   ["cta_highlight", "cta_highlight_keyword"],
    "subtext_italic":  ["subtext_italic", "subtext"],
    "layout_type":     ["layout_type", "layout"],
}


# ── Copy + design director ────────────────────────────────────────────────────
# The brain behind every thumbnail's words. This operationalizes the repo's design /
# UX / content skills so a thumbnail isn't just "rendered" — it's art-directed:
#   • Ogilvy (2_KNOWLEDGE/domain_skills/ogilvy)          → promise/big-idea first, simple beats clever
#   • copywriting + copy-editing                          → clarity > cleverness, benefit > feature, be specific
#   • page-cro (3-second scan rule)                       → ONE idea, instantly legible
#   • banner-design + thumbnail_prompt_1 (9_PROMPTS)      → minimalism, tech-editorial, word limits, 1 highlight
#   • ui-styling (contrast ≥4.5:1)                        → enforced by brand palette (light text on navy)
#   • stop-slop                                           → ban generic AI filler / clichés
_COPY_DIRECTOR_SYSTEM = (
    "You are SEOSONA's thumbnail art director — part conversion copywriter (Ogilvy + "
    "direct-response), part minimalist designer. You write thumbnail text that a viewer "
    "fully understands in a 3-second scan.\n"
    "RULES:\n"
    "1. ONE idea only. Lead with a concrete promise/payoff, not a topic.\n"
    "2. Clarity beats cleverness; a benefit beats a feature; be SPECIFIC (use a number if one fits).\n"
    "3. Word limits — top_label: ≤5 words UPPERCASE; main_title: 4–8 punchy words; cta: 2–4 action words.\n"
    "4. Exactly ONE highlight keyword in the title (title_highlight = the single most important word/phrase, "
    "a substring of main_title). cta_highlight = the punchiest substring of cta.\n"
    "5. Vietnamese output (brand content is Vietnamese). NO generic AI filler "
    "('khám phá ngay', 'bí mật', 'không thể tin nổi'), NO emojis, NO clickbait lies.\n"
    "6. subtext_italic: one short, true, thought-provoking line (or empty).\n"
    "Output ONLY JSON with EXACTLY these keys: top_label, main_title, title_highlight, "
    "hook, cta, cta_highlight, subtext_italic, layout_type (one of: text_only, portrait, card)."
)


# ── NLP layer ──────────────────────────────────────────────────────────────--
def _normalize_nlp(raw):
    """Map any key-casing / alias the LLM returned to our canonical lowercase keys."""
    low = {(str(k) or "").strip().lower(): v for k, v in (raw or {}).items()}
    out = {}
    for canon, names in _ALIASES.items():
        for n in names:
            val = low.get(n)
            if val not in (None, ""):
                out[canon] = val
                break
    return out


def _nlp_variables(content, brand="seosona"):
    """Art-direct the thumbnail copy via the LLM engine, grounded by the repo's own
    intent + number extractors so the result is specific, not generic. The user prompt
    deliberately mentions 'thumbnail/pill_label/main_title/layout_type' so the offline
    Smart-NLP router recognises the intent when no API key is present. Best-effort:
    callers tolerate {} and fall back to content + defaults."""
    llm = importlib.import_module("4_BRAIN.llm_engine")

    # Grounding hints (offline-safe — no API key needed). _classify_intent picks the
    # angle (SEO / AI_AGENT / MARKETING / …); _extract_numbers surfaces a concrete stat
    # to make the hook specific instead of vague.
    try:
        intent = llm._classify_intent(content or "")
        numbers = llm._extract_numbers(content or "")
    except Exception:
        intent, numbers = "GENERAL", []

    hint = f"Detected angle: {intent}."
    if numbers:
        hint += f" Concrete numbers available (prefer one in the hook): {', '.join(numbers[:3])}."

    prompt = (
        "Art-direct a SEOSONA thumbnail for the content below. Extract the layout_type "
        "and write the pill_label / main_title / cta following every rule.\n\n"
        f"{hint}\n\nContent:\n" + (content or "")
    )
    return _normalize_nlp(llm.generate_json_from_prompt(_COPY_DIRECTOR_SYSTEM, prompt))


# ── Text / highlight helpers ─────────────────────────────────────────────────
# Function words that must NOT win the highlight — the bare longest-token heuristic otherwise picks
# "Những"/"Trong" etc. (a stopword makes a weak, off-message highlight).
_THUMB_STOP = {
    "và", "của", "trong", "cho", "để", "là", "các", "những", "một", "khi", "nếu", "với", "từ", "hay",
    "này", "đó", "thì", "mà", "ở", "về", "đã", "sẽ", "đang", "bạn", "tôi", "chúng", "ta", "nó", "bị",
    "được", "có", "không", "nên", "cần", "phải", "rất", "quá", "cũng", "đều", "chỉ", "còn", "đến",
    "theo", "trên", "dưới", "sau", "trước", "giữa", "cùng", "như", "bởi", "vì", "do", "điều", "cách",
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "is", "are", "your", "you",
}


def _extract_keyword(text):
    """Pick the most prominent word as the highlight keyword. Returns (prefix, kw, suffix).
    Prefers an ALL-CAPS acronym (SEO/AI/API/TOP — almost always the key term), else the longest CONTENT
    word (a bare longest token can be a stopword like 'Những', which makes a weak highlight)."""
    words = text.split()
    if not words:
        return "", "", ""
    if len(words) <= 2:
        return "", " ".join(words), ""

    def _clean(w):
        return w.lower().strip(".,!?:;\"'()")
    caps = [w for w in words if len(w) >= 2 and w.isalpha() and w.isupper()]   # acronyms: SEO, AI, TOP
    if caps:
        pick = max(caps, key=len)
    else:
        content = [w for w in words if _clean(w) not in _THUMB_STOP]           # skip function words
        pick = max(content or words, key=len)
    idx = words.index(pick)
    return " ".join(words[:idx]), pick, " ".join(words[idx + 1:])


def _split_highlight(text, keyword):
    """Split `text` into (prefix, keyword, suffix) around `keyword` so the template's
    highlight span lands on the right words. Falls back to the longest-word heuristic."""
    if not text:
        return ("", "", "")
    if keyword:
        kw = str(keyword).strip()
        if kw:
            # WHOLE-WORD, case-insensitive. A plain substring find (text.upper().find) lands the highlight
            # INSIDE another word: kw "AI" → "Em[AI]l", "SEO" → "[SEO]ul", breaking the word on the thumbnail
            # (the CTR-critical asset). \b uses Unicode \w, so it respects Vietnamese diacritics. If the
            # keyword isn't a standalone word, fall back to the content-word heuristic (never a bad substring).
            m = re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE)
            if m:
                return (text[:m.start()].strip(), text[m.start():m.end()].strip(), text[m.end():].strip())
    return _extract_keyword(text)


def _cap_title(title, max_words=12, max_chars=72):
    """The title renders at a FIXED large font (105-130px) inside an overflow:hidden box, so a long title —
    e.g. the raw-content fallback, which can be a whole paragraph — is CLIPPED mid-word on the thumbnail.
    Cap it to a title-length AT A WORD BOUNDARY: a clean short title beats an arbitrarily-clipped one. The
    design target is 4-8 words, so a normal title is never touched; this only catches over-long input."""
    t = " ".join(str(title or "").split())            # normalise whitespace
    words = t.split(" ")
    if len(words) > max_words:
        t = " ".join(words[:max_words])
    if len(t) > max_chars:                             # guard a run of very long words too
        t = (t[:max_chars].rsplit(" ", 1)[0] or t[:max_chars])
    return t.strip()


# ── HTML render (private) ─────────────────────────────────────────────────────
def _temp_html_path(output_path):
    """Temp HTML path keyed to the UNIQUE output — never a shared fixed name — so concurrent renders
    into the same directory (a video's 9:16 + 16:9, or batch) can't clobber each other's temp file."""
    return os.path.join(os.path.dirname(output_path),
                        "_temp_" + os.path.splitext(os.path.basename(output_path))[0] + ".html")


def _render_html(output_path, top_label, main_title, hook, cta, portrait_path,
                 manual_title, manual_cta, aspect_ratio, brand, subtext_italic, layout_type):
    """Render the chosen template to PNG via Playwright. Internal — go through make_thumbnail."""
    print(f"Generating HTML-based Thumbnail ({aspect_ratio} | {brand})...")
    palette = BRAND_PALETTES.get(brand.lower(), BRAND_PALETTES["seosona"])

    # One template, two layouts: the aspect class selects which canvas renders.
    if aspect_ratio == "16:9":
        aspect_class, width, height = "is-landscape", 1920, 1080
    else:
        aspect_class, width, height = "is-portrait", 1080, 1920

    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates", "seosona_thumbnail.html"))
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", palette["logo_path"]))

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")

    logo_uri = "file:///" + logo_path.replace("\\", "/") if os.path.exists(logo_path) else ""

    title_1, title_kw, title_2 = manual_title if manual_title else _extract_keyword(main_title)
    cta_1, cta_kw, cta_2 = manual_cta if manual_cta else _extract_keyword(cta)
    # HTML-escape user text before it goes into the template — a title/cta with '<'/'>' would break the
    # render (malformed tags) and '&' should be an entity. Structural tokens (colours/classes/paths) below
    # are trusted and left as-is. Escapes here + top_label/subtext/hook in the map cover every text token.
    title_1, title_kw, title_2 = _hesc(str(title_1)), _hesc(str(title_kw)), _hesc(str(title_2))
    cta_1, cta_kw, cta_2 = _hesc(str(cta_1)), _hesc(str(cta_kw)), _hesc(str(cta_2))

    if layout_type == "auto":
        layout_type = "portrait" if (portrait_path and os.path.exists(portrait_path)) else "text_only"

    if layout_type == "portrait" and portrait_path and os.path.exists(portrait_path):
        portrait_uri = "file:///" + os.path.abspath(portrait_path).replace("\\", "/")
        portrait_style = text_align_class = title_class = ""
    elif layout_type == "card":
        portrait_uri, portrait_style, text_align_class, title_class = "", "display: none;", "", ""
    else:  # text_only
        portrait_uri, portrait_style = "", "display: none;"
        text_align_class = title_class = "center-full"

    subtext_style = "" if subtext_italic else "display: none;"
    card_style, card_content = "display: none;", ""

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    for token, value in {
        "{{ASPECT_CLASS}}": aspect_class,
        "{{COLOR_NAVY}}": palette["navy"], "{{COLOR_BLUE}}": palette["blue"],
        "{{COLOR_LIGHT_BLUE}}": palette["light_blue"], "{{COLOR_YELLOW}}": palette["yellow"],
        "{{TEXT_ALIGN_CLASS}}": text_align_class, "{{TITLE_CLASS}}": title_class,
        "{{PORTRAIT_STYLE}}": portrait_style, "{{SUBTEXT_STYLE}}": subtext_style,
        "{{CARD_STYLE}}": card_style, "{{CARD_CONTENT}}": card_content,
        "{{LOGO_PATH}}": logo_uri, "{{PORTRAIT_PATH}}": portrait_uri,
        "{{WATERMARK}}": palette["watermark"], "{{BRAND_NAME}}": palette["brand_name"],
        "{{BRAND_TAGLINE}}": palette["brand_tagline"], "{{BRAND_TAGLINE_UPPER}}": palette["brand_tagline_upper"],
        "{{TOP_LABEL}}": _hesc(str(top_label)), "{{MAIN_TITLE_1}}": title_1, "{{MAIN_TITLE_KW}}": title_kw,
        "{{MAIN_TITLE_2}}": title_2, "{{CTA_1}}": cta_1, "{{CTA_KW}}": cta_kw, "{{CTA_2}}": cta_2,
        "{{SUBTEXT_ITALIC}}": _hesc(str(subtext_italic)), "{{HOOK}}": _hesc(str(hook)),
    }.items():
        html = html.replace(token, str(value))   # coerce: a non-str NLP value (e.g. a number) must not crash replace()

    temp_html = _temp_html_path(output_path)   # unique per output — no cross-render collision (see helper)
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.goto(f"file:///{temp_html.replace(chr(92), '/')}", wait_until="networkidle")
            page.screenshot(path=output_path, type="png")
            browser.close()
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

    print(f"Thumbnail successfully saved to {output_path}")
    return output_path


# ── Public entry point ────────────────────────────────────────────────────────
def make_thumbnail(content, output_path, *, aspect_ratio="9:16", brand="seosona",
                   portrait_path=None, use_nlp=True, top_label=None, main_title=None,
                   cta=None, hook=None, subtext_italic=None, layout_type="auto"):
    """Render a branded thumbnail from raw content. THE entry point for the factory.

    Args:
        content: title / hook / concept text the thumbnail is about.
        output_path: PNG output path.
        aspect_ratio: "9:16" (1080×1920) or "16:9" (1920×1080).
        brand: "seosona" or "cqa".
        portrait_path: optional cutout/frame image for the portrait layout.
        use_nlp: run NLP variable extraction (set False for fully manual calls).
        top_label/main_title/cta/hook/subtext_italic/layout_type: explicit overrides —
            when given, they win over the NLP result. Pass main_title when the caller
            already has the exact headline (e.g. a scene's h1/h2) and only wants NLP for
            the highlight keyword + subtext.
    Returns:
        output_path on success.
    """
    nlp = {}
    if use_nlp:
        try:
            nlp = _nlp_variables(content, brand)
        except Exception as e:
            print(f"[thumbnail] NLP skipped ({e}); using content + defaults.")

    top = top_label or nlp.get("top_label") or ("SEOSONA" if brand == "seosona" else brand.upper())
    title = _cap_title(main_title or nlp.get("main_title") or content or "SEOSONA")
    cta_text = cta or nlp.get("cta") or "XEM NGAY"
    hook_str = hook if hook is not None else nlp.get("hook", "")
    sub = subtext_italic if subtext_italic is not None else (nlp.get("subtext_italic") or "")

    manual_title = _split_highlight(title, nlp.get("title_highlight"))
    manual_cta = _split_highlight(cta_text, nlp.get("cta_highlight"))

    lt = layout_type if layout_type != "auto" else (nlp.get("layout_type") or "auto")
    if lt not in _VALID_LAYOUTS:
        lt = "auto"

    return _render_html(
        output_path=output_path, top_label=top, main_title=title, hook=hook_str,
        cta=cta_text, portrait_path=portrait_path, manual_title=manual_title,
        manual_cta=manual_cta, aspect_ratio=aspect_ratio, brand=brand,
        subtext_italic=sub, layout_type=lt,
    )


if __name__ == "__main__":
    for ar in ("9:16", "16:9"):
        make_thumbnail(
            "TẠI SAO TÔI ĐẶT CƯỢC SEO VÀO AI AGENT — nhìn cách tập đoàn lớn triển khai",
            f"Thumbnail_Smoke_{ar.replace(':', 'x')}.png", aspect_ratio=ar, brand="seosona")
