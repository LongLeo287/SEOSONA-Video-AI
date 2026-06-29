# -*- coding: utf-8 -*-
"""SEOSONA Video — Content Moderation (pre-render gate).

A skeptical CONTENT checker that runs on the Vietnamese script BEFORE rendering, distinct
from the output Evaluator (which checks the finished MP4). It enforces the brand rule
"real data only — no fabricated numbers/stars" and brand safety:

  - BLOCK: unsafe terms (profanity / guarantees that are legally risky).
  - FLAG (review): absolute/superlative marketing claims, unattributed statistics, and
    fabricated social-proof patterns ("X triệu view", "X sao") with no cited source.

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

# A numeric statistic (percent / multiplier / big count).
STAT = re.compile(r"\b\d[\d.,]*\s*(%|phần trăm|x|lần|triệu|tỷ|nghìn)\b", re.IGNORECASE)

# Source/attribution cues — if present near stats, the numbers are considered cited.
SOURCE_CUES = ["theo ", "nguồn", "thống kê", "báo cáo", "khảo sát", "nghiên cứu",
               "công bố", "according to", "source", "report", "study", "data from"]


def _has_word(text_low, term):
    t = term.lower()
    # phrase substring is fine for multi-word; word-boundary for single tokens
    if " " in t:
        return t in text_low
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

    cited = any(c in low for c in SOURCE_CUES)
    sp = SOCIAL_PROOF.findall(text)
    if sp and not cited:
        flags.append({"severity": "flag", "kind": "social-proof",
                      "detail": "engagement numbers without a cited source"})
    stats = STAT.findall(text)
    if stats and not cited:
        flags.append({"severity": "flag", "kind": "unattributed-stat",
                      "detail": f"{len(stats)} statistic(s) with no source cue (use real, cited data)"})

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
