# -*- coding: utf-8 -*-
"""Deterministic beat-timing passes ported from SKILL AUTO (close_gaps / sync_list_items / zoom_plan).

The SKILL-AUTO doctrine: the LLM authors WHAT + WHY, Python owns all TIMING. Three passes:
  • close_gaps(beats)        — bridge sub-1.5s flicker gaps (or leave a real breather); fix overlaps.
  • sync_list_items(beats,w) — reveal each list row the moment the speaker says it (no spoiling).
  • zoom_plan(words)         — SCORE which spoken word deserves an emphasis zoom-punch (numbers,
                               brands, pivots, loaded pauses), not fixed N-second intervals.

VN-adapted: brand + pivot lexicons and list-stopwords are re-authored for Vietnamese (algorithms
transfer, lexicons do NOT). Operates on plain dict beats — engine-agnostic (talking-head or scenes).
"""
import re

# ── shared: overlays that leave the speaker visible → may overlap, never bridged/ceilinged ──
PARTIAL_KINDS = {"icon_tile", "icon", "chip", "badge", "marker", "emoji", "lottie", "count_up",
                 "word_pop", "hook_title", "subscribe", "bar_overlay", "ratio_dots", "headline_card"}


def _n(b, *keys, default=None):
    for k in keys:
        if isinstance(b, dict) and b.get(k) is not None:
            return float(b[k])
    return default


# ─────────────────────────────── close_gaps ───────────────────────────────
MAX_GAP = 1.5           # sub-1.5s gap between full-frame beats = flicker → bridge back-to-back
MAX_BRIDGED_DUR = 6.0   # but never inflate a beat past this (bridging kills flicker, not makes setpieces)


def close_gaps(beats, max_gap=MAX_GAP, max_bridged=MAX_BRIDGED_DUR):
    """Bridge micro-gaps + fix overlaps between adjacent full-frame beats in place. Returns beats.
    Two partial overlays are left alone (their overlap is intentional). SKILL AUTO close_gaps.py."""
    if not beats or len(beats) < 2:
        return beats
    order = sorted(range(len(beats)), key=lambda i: _n(beats[i], "start_sec", "start", default=0))
    for k in range(len(order) - 1):
        a, b = beats[order[k]], beats[order[k + 1]]
        ka = a.get("kind") or a.get("type")
        kb = b.get("kind") or b.get("type")
        if ka in PARTIAL_KINDS and kb in PARTIAL_KINDS:
            continue
        end_a = _n(a, "end_sec", "end", default=0)
        start_b = _n(b, "start_sec", "start", default=0)
        start_a = _n(a, "start_sec", "start", default=0)
        gap = start_b - end_a
        key_end = "end_sec" if "end_sec" in a else "end"
        if gap < 0:                                        # overlap → shorten earlier beat
            new_end = round(start_b - 0.02, 2)
            if new_end > start_a:
                a[key_end] = new_end
        elif 0 < gap <= max_gap:                           # micro-gap → bridge, unless it'd be a setpiece
            if (start_b - start_a) <= max_bridged:
                a[key_end] = round(start_b, 2)
    return beats


# ─────────────────────────────── sync_list_items ───────────────────────────────
_VN_STOP = {"và", "hoặc", "là", "của", "cho", "với", "một", "các", "những", "này", "đó", "kia",
            "thì", "mà", "ở", "trong", "trên", "dưới", "để", "khi", "nếu", "cũng", "đã", "sẽ",
            "đang", "bạn", "tôi", "mình", "chúng", "ta", "họ", "nó", "có", "không", "được", "bị",
            "rất", "quá", "lắm", "nhé", "nha", "ạ", "à", "ơi", "the", "a", "an", "and", "or", "to",
            "of", "in", "on", "for", "is", "are", "with", "this", "that", "it", "you", "your"}
_WORD_RE = re.compile(r"[\w]+", re.UNICODE)
MIN_LAST_ITEM_DWELL = 1.5


def _norm(s):
    return str(s or "").lower().strip().strip(",.!?;:\"'…")


def _keywords(text):
    return [t for t in _WORD_RE.findall(str(text or "").lower()) if t not in _VN_STOP and len(t) > 1]


def _find_appear(words, kws, win_start, win_end, after):
    for w in words or []:
        ws = float(w.get("start", 0))
        if ws < max(win_start, after):
            continue
        if ws > win_end:
            break
        tok = _norm(w.get("word", ""))
        if not tok:
            continue
        if tok in kws:
            return ws
        for kw in kws:
            if len(kw) >= 4 and kw in tok:
                return ws
    return None


def sync_list_items(beats, words):
    """Pin each list beat's items to when the speaker says them (adds item.appear_sec + extends the
    beat's end for the last item's dwell). Reveals rows in sync, never front-loading the punchline."""
    for b in beats or []:
        if (b.get("kind") or b.get("type")) != "list":
            continue
        items = b.get("items") or []
        if not items:
            continue
        win_s = _n(b, "start_sec", "start", default=0)
        win_e = _n(b, "end_sec", "end", default=win_s + 5)
        last = win_s
        out = []
        for idx, it in enumerate(items):
            if isinstance(it, dict) and it.get("appear_sec") is not None:
                out.append(it); last = float(it["appear_sec"]); continue
            text = it.get("text") if isinstance(it, dict) else str(it)
            found = _find_appear(words, _keywords(text), win_s, win_e, last)
            if found is None:
                slot = (win_e - last) / max(1, (len(items) - idx) + 1)
                appear = round(last + slot, 2)
            else:
                appear = round(max(found - 0.10, last + 0.05), 2)
            row = dict(it) if isinstance(it, dict) else {"text": text}
            row["appear_sec"] = appear
            out.append(row); last = appear
        b["items"] = out
        needed = float(out[-1]["appear_sec"]) + MIN_LAST_ITEM_DWELL
        if needed > win_e:
            b["end_sec" if "end_sec" in b else "end"] = round(needed, 2)
    return beats


# ─────────────────────────────── zoom_plan (emphasis selection) ───────────────────────────────
# VN + our brand tokens worth punching in on (lowercase, diacritic-as-spoken forms handled by ASR fix).
_ZOOM_BRANDS = {"seosona", "claude", "chatgpt", "gpt", "openai", "gemini", "google", "facebook",
                "tiktok", "youtube", "instagram", "seo", "canva", "notion", "github", "ahrefs",
                "semrush", "anthropic", "shopify", "wordpress", "midjourney"}
# Vietnamese pivot / attention words — the "loaded" turn before a punch.
_ZOOM_PIVOTS = {"nhưng", "chờ", "khoan", "thực", "thật", "tuy", "nhiên", "thay", "vào", "đó",
                "để", "ý", "nghe", "đây", "bí", "mật", "quan", "trọng", "lưu", "chú", "actually",
                "but", "wait"}
_NUM_PAT = re.compile(r"^[\$₫£€]?[\d.,]+[%kKmMbBtriệungàn]*$", re.UNICODE)


def _strip(w):
    return str(w or "").strip(".,!?;:'\"…%")


def _is_number(w):
    c = _strip(w)
    return bool(c) and bool(re.match(r"^[\$₫£€]?[\d][\d.,]*[%kKmMbB]?$", c))


def _score_word(words, i):
    w = words[i].get("word", "")
    s = 0.0
    t = _strip(w).lower()
    if _is_number(w):        s += 3.0
    if t in _ZOOM_BRANDS:    s += 2.5
    if t in _ZOOM_PIVOTS:    s += 2.0
    if i > 0:
        gap = float(words[i].get("start", 0)) - float(words[i - 1].get("end", 0))
        if gap > 0.5:        s += 1.2
        if gap > 1.0:        s += 0.6
        if re.search(r"[.!?]$", str(words[i - 1].get("word", ""))):
            s += 1.0
    return s


def zoom_plan(words, min_gap=3.5, intensity=1.06, window_dur=2.4, pre_pad=0.15, every=6.5):
    """Score each spoken word for punchiness and return emphasis-zoom windows
    [{start_sec,end_sec,scale,trigger}] — greedy top-N with min_gap so zooms don't pile up."""
    words = [w for w in (words or []) if isinstance(w, dict) and w.get("start") is not None]
    if not words:
        return []
    dur = float(words[-1].get("end", words[-1].get("start", 0)))
    target = max(3, int(dur / every))
    scored = sorted(((_score_word(words, i), i, float(words[i].get("start", 0)))
                     for i in range(len(words)) if _score_word(words, i) > 0), reverse=True)
    picks, chosen = [], []
    for s, i, t in scored:
        if any(abs(t - ct) < min_gap for ct in chosen):
            continue
        picks.append((t, words[i].get("word", ""))); chosen.append(t)
        if len(picks) >= target:
            break
    picks.sort()
    plan = []
    for t, label in picks:
        scale = intensity + (0.02 if _is_number(label) or _strip(label).lower() in _ZOOM_BRANDS else 0)
        plan.append({"start_sec": round(max(0.0, t - pre_pad), 3), "end_sec": round(t + window_dur, 3),
                     "scale": round(scale, 3), "trigger": _strip(label)})
    return plan


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    beats = [{"start_sec": 0, "end_sec": 3, "kind": "photocard"},
             {"start_sec": 3.8, "end_sec": 5, "kind": "quote"},
             {"start_sec": 2, "end_sec": 4, "kind": "list",
              "items": ["Tối ưu tiêu đề", "Nghiên cứu từ khóa", "Tăng tốc độ trang"]}]
    words = [{"word": "Tối", "start": 2.0, "end": 2.2}, {"word": "ưu", "start": 2.2, "end": 2.4},
             {"word": "tiêu", "start": 2.4, "end": 2.6}, {"word": "SEOSONA", "start": 3.0, "end": 3.5},
             {"word": "tăng", "start": 5.0, "end": 5.2}, {"word": "300%", "start": 5.4, "end": 6.0},
             {"word": "từ", "start": 6.5, "end": 6.7}, {"word": "khóa", "start": 6.7, "end": 6.9}]
    print("close_gaps:", [(b.get("start_sec"), b.get("end_sec"), b.get("kind")) for b in close_gaps([dict(x) for x in beats])])
    synced = sync_list_items([dict(x) for x in beats], words)
    print("sync_list_items:", [b["items"] for b in synced if (b.get("kind") == "list")])
    print("zoom_plan:", zoom_plan(words))
