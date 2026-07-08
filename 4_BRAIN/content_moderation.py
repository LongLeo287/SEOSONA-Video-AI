# -*- coding: utf-8 -*-
"""SEOSONA Video — Content Moderation (pre-render gate).

A skeptical CONTENT checker that runs on the Vietnamese script BEFORE rendering, distinct
from the output Evaluator (which checks the finished MP4). It enforces the brand rule
"real data only — no fabricated numbers/stars" and brand safety:

  - BLOCK: unsafe terms (profanity / guarantees that are legally risky); off-platform CTAs
    (a bare external domain in the CTA scene / after a "visit/download" verb) — the single CTA
    must be "follow SEOSONA", never send viewers off-platform.
  - FLAG (review): absolute/superlative marketing claims, unattributed statistics, and
    fabricated social-proof patterns ("X triệu view", "X sao") with no cited source.

The off-platform-CTA detector (`off_platform_domain`) is the SINGLE source of truth shared by
both video paths — the topic/discover path (via script_writer.verify Gate 3 → moderate) and the
GitHub-showcase path (make_video._lint_script imports it) — so the rule is defined in one place.

Note: the PATTERN strings below are Vietnamese because they match Vietnamese video CONTENT
(like the pronunciation lexicon) — they are data, not documentation. The module itself is
English. Free/local, rule-based; no API.

  from content_moderation import moderate
  v = moderate(script_text)        # {"ok": bool, "severity": "ok|flag|block", "flags": [...]}
"""
import os
import re
import sys
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Absolute / superlative marketing claims that need substantiation (FLAG, not block).
ABSOLUTE_CLAIMS = [
    "tốt nhất", "số 1", "số một", "duy nhất", "tuyệt đối", "đảm bảo", "cam kết",
    "chắc chắn 100", "100% hiệu quả", "hiệu quả tuyệt đối", "không ai bằng", "vô địch",
    "best", "number one", "#1", "guaranteed", "100% effective",
]

# Legally/brand risky — BLOCK until reworded.
UNSAFE_TERMS = [
    "chữa khỏi", "cam kết khỏi bệnh", "chắc chắn giàu", "làm giàu nhanh",
    "lãi suất đảm bảo", "cam kết lợi nhuận", "thần dược", "lừa đảo",
    "guaranteed profit", "get rich quick", "miracle cure",
]

# Fabricated social proof without a cited source (FLAG).
SOCIAL_PROOF = re.compile(
    r"\b\d[\d.,]*\s*(triệu|tỷ|nghìn|k|m)?\s*(view|lượt xem|like|lượt thích|follow|"
    r"theo dõi|subscriber|sao|star|đánh giá)\b", re.IGNORECASE)

# A numeric statistic (percent / multiplier / big count). NOTE: end with (?!\w), NOT \b — a trailing \b
# fails right after "%" (a non-word char), so "70%"/"tăng 47%" (the MOST common stat) silently never
# matched, while "5 triệu"/"3 lần" did. (?!\w) closes on both a symbol unit ("%") and a word unit.
STAT = re.compile(r"\b\d[\d.,]*\s*(%|phần trăm|x|lần|triệu|tỷ|nghìn)(?!\w)", re.IGNORECASE)

# Off-platform CTA (brand-safety): the single CTA must be "follow SEOSONA" — never send viewers to an
# external site. A BARE domain (no scheme) slips past URL/English-leak scrubbers, so match it directly;
# only treat it as a CTA (not a neutral mention) when the CTA scene or a "go visit/download" verb is near.
OFF_PLATFORM_DOMAIN = re.compile(
    r"\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:io|com|net|org|ai|co|dev|app|xyz|me|vn|gg|link|site|online|store|tech)\b",
    re.IGNORECASE)
CTA_VERBS = ("truy cập", "ghé thăm", "ghé qua", "ghé", "vào trang", "vào web", "tải tại", "tải về tại",
             "tải xuống tại", "đăng ký tại", "xem tại", "click vào", "nhấn vào", "nhấp vào",
             # more real off-platform CTA constructions (each still requires a DOMAIN to fire, so bare
             # informational mentions stay clean — e.g. "fiverr.com là nền tảng", "Google gọi … là").
             "liên hệ", "mua tại", "mua ở", "đặt tại", "đặt hàng tại", "đặt mua tại", "nhắn tin",
             "kết nối tại", "tìm tại", "tìm ở", "xem thêm tại", "đăng ký ở", "tải ở")
SAFE_DOMAINS = ("seosona", "youtube.com", "youtu.be")


def off_platform_domain(text, is_cta_scene=False):
    """Return the offending external domain if `text` is an off-platform CTA — a bare domain in the CTA
    scene OR after a "go visit/download" verb — else None. Neutral mentions (no verb, not the CTA scene)
    and SEOSONA's/YouTube's own presence pass. Single source of truth for BOTH the topic/discover path
    (via moderate() → verify Gate 3) and the GitHub-showcase path (make_video._lint_script)."""
    m = OFF_PLATFORM_DOMAIN.search(text or "")
    if not m:
        return None
    dom = m.group(0)
    if any(sd in dom.lower() for sd in SAFE_DOMAINS):
        return None
    if is_cta_scene or any(v in (text or "").lower() for v in CTA_VERBS):
        return dom
    return None

# Source/attribution cues — if present near stats, the numbers are considered cited.
# A genuine source attribution near a statistic. CRITICAL: NO bare "theo" — Vietnamese "theo"
# ("according to / follow / by / in my opinion", as in "theo tôi", "theo dõi") appears in almost every
# script, so `("theo " in low)` spuriously marked EVERY stat as cited and silently DISABLED the
# unattributed-stat / social-proof gate (defeating "real data only — no fabricated numbers"). Require a
# real source noun; "theo" counts only when it directly precedes one. Short English cues use word
# boundaries so 'source' ≠ 'resource'/'outsource' and 'report' ≠ 'reporter'.
SOURCE_RE = re.compile(
    r"nguồn|thống kê|báo cáo|khảo sát|nghiên cứu|công bố|số liệu|dữ liệu từ|"
    r"according to|data from|\bsources?\b|\breports?\b|\bstud(?:y|ies)\b|"
    r"theo\s+(?:nguồn|báo cáo|nghiên cứu|thống kê|khảo sát|số liệu|dữ liệu)",
    re.IGNORECASE)

# AI-slop tells (from the `stop-slop` domain skill): generic, hedging, clichéd phrasing that
# reads like a machine. FLAG so the script gets rewritten to a sharp human voice.
SLOP_PHRASES = [
    # Vietnamese
    "trong thời đại số", "trong thế giới ngày nay", "không thể phủ nhận", "đáng chú ý là",
    "nhìn chung", "hãy cùng tìm hiểu", "hãy cùng khám phá", "nói tóm lại", "có thể nói rằng",
    "ngày càng trở nên", "đóng vai trò quan trọng", "mở ra một kỷ nguyên",
    # English
    "in today's world", "in the digital age", "it's worth noting", "delve into",
    "game-changer", "revolutionize", "in conclusion", "unlock the power", "navigate the",
    "ever-evolving", "it is important to note",
]


def _has_word(text_low, term):
    t = term.lower()
    # Word-boundary around the WHOLE term (multi-word too — re.escape keeps the internal spaces literal).
    # Plain substring mis-fired on a token that PREFIXES a longer one: "số 1" ∈ "số 10"/"số 100" (a mere
    # number list), and "chắc chắn 100" ∈ "chắc chắn 1000 đồng". Boundaries stop both.
    return re.search(r"(?<![\wÀ-ỹ])" + re.escape(t) + r"(?![\wÀ-ỹ])", text_low) is not None


def moderate(text, strict=None, record=True):
    """Check a script. Returns {ok, severity, flags}. severity: ok | flag | block.
    strict (env SEOSONA_MODERATION=strict) makes FLAGs also fail ok; default warns."""
    if strict is None:
        strict = os.environ.get("SEOSONA_MODERATION", "warn").lower() == "strict"
    text = str(text or "")
    low = text.lower()
    flags = []

    for w in UNSAFE_TERMS:
        if _has_word(low, w):
            flags.append({"severity": "block", "kind": "unsafe-term", "detail": w})
    for w in ABSOLUTE_CLAIMS:
        if _has_word(low, w):
            flags.append({"severity": "flag", "kind": "absolute-claim", "detail": w})

    cited = bool(SOURCE_RE.search(text))
    sp = SOCIAL_PROOF.findall(text)
    if sp and not cited:
        flags.append({"severity": "flag", "kind": "social-proof",
                      "detail": "engagement numbers without a cited source"})
    stats = STAT.findall(text)
    if stats and not cited:
        flags.append({"severity": "flag", "kind": "unattributed-stat",
                      "detail": f"{len(stats)} statistic(s) with no source cue (use real, cited data)"})

    slop = [p for p in SLOP_PHRASES if p in low]
    if slop:
        flags.append({"severity": "flag", "kind": "ai-slop",
                      "detail": f"clichéd/AI-slop phrasing: {', '.join(slop[:4])} — rewrite sharper"})

    cta_dom = off_platform_domain(text)          # full-text, verb-based (scene position N/A here)
    if cta_dom:
        flags.append({"severity": "block", "kind": "off-platform-cta",
                      "detail": f"external CTA '{cta_dom}' — the single CTA must be follow SEOSONA (no off-platform)"})

    has_block = any(f["severity"] == "block" for f in flags)
    severity = "block" if has_block else ("flag" if flags else "ok")
    ok = (severity == "ok") or (severity == "flag" and not strict)

    icon = {"ok": "✅", "flag": "⚠️", "block": "⛔"}[severity]
    print(f"[moderation] {icon} {severity.upper()}"
          + ("" if not flags else " :: " + "; ".join(f"{f['kind']}:{f['detail']}" for f in flags)))
    if record:
        try:
            sys.path.insert(0, os.path.join(ROOT, "9_DASHBOARD"))
            import_module("obs_metrics").record("moderation", severity=severity,
                                                flags=[f["kind"] for f in flags])
        except Exception:
            pass
    return {"ok": ok, "severity": severity, "flags": flags}


if __name__ == "__main__":
    import json
    src = sys.argv[1] if len(sys.argv) > 1 else "Khoá học SEO tốt nhất, đảm bảo 100% lên top, 5 triệu view."
    print(json.dumps(moderate(src), ensure_ascii=False, indent=2))
