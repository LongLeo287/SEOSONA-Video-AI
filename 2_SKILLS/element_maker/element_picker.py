# -*- coding: utf-8 -*-
"""Auto-place ELEMENTS from the narration — the loop that makes the element library actually USED.

Given the word-level transcript (what the talking-head engine already produces), this scans the
spoken words for concepts we can illustrate and emits a timed `elements:[...]` plan — an icon-tile /
emoji / stat popped in a safe zone exactly when that word is spoken, with the role + badge inferred
from nearby cues (a "not X" phrase → coral ✕ tile; a "free/fast/auto" phrase → green ✓ tile). So a
plain talking-head auto-gets the dense element layer, no hand-authoring. Deterministic + alias-driven
(reliable, no LLM); unknown concepts still resolve via `element_resolver` at render time.

    from element_picker import pick_elements
    els = pick_elements(words, W=1080, H=1920)   # → [{type,icon,role,badge,label,t,dur,x,y,w}, ...]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import element_maker as em   # noqa: E402 — ICON_ALIASES / EMOJI_ALIASES = the concept vocabulary

# Cue words near a concept steer its role + badge (the reels' problem→solution grammar).
_NEG = ("không", "đừng", "tránh", "sai", "mất", "tốn", "kém", "khó", "chậm", "lỗi", "rủi ro",
        "nguy hiểm", "thất bại", "vấn đề", "bỏ", "ngừng", "cấm", "đắt", "phí")
_POS = ("miễn phí", "free", "nhanh", "tự động", "tốt", "dễ", "hiệu quả", "tăng", "thành công",
        "tối ưu", "tiết kiệm", "chính xác", "mạnh", "đơn giản", "xong", "hoàn thành", "chuẩn")
_URGENT = ("gấp", "deadline", "hết hạn", "đếm ngược", "nhanh lên", "chỉ còn", "kịp", "khẩn")
# Pure emphasis/emotion words → an emoji pop (not an icon tile).
_EMOJI_CUES = {"tuyệt vời": "star", "bùng nổ": "fire", "cảnh báo": "warning", "lưu ý": "warning",
               "quan trọng": "warning", "mẹo": "idea", "ý tưởng": "idea", "wow": "eyes",
               "bất ngờ": "eyes", "tiền": "money", "chi phí": "money", "kết quả": "chart"}

# Concept vocabulary = the alias keys (single- and multi-word). Longer phrases matched first.
_CONCEPTS = sorted(em.ICON_ALIASES.keys(), key=lambda k: -len(k.split()))
_STOP = set("là và của có không được một những các với cho khi này đó đã sẽ rất thì mà ở từ ra vào "
            "nên cũng để theo trên về bạn mình tôi nó em anh chị".split())
_ANIMS = ("rise", "slide-left", "drop", "slide-right")   # rotated per slot for entrance variety
# A spoken number ≥2 digits (opt %/+) → a count_up; a celebration beat → a Lottie motion-graphic.
_NUM_RE = re.compile(r"^(\d{2,})([%+]?)$")
_CELEBRATE = ("thành công", "tuyệt vời", "chúc mừng", "xuất sắc", "bùng nổ", "hoàn thành",
              "kỷ lục", "ấn tượng", "tăng vọt", "đột phá", "vượt trội")


def _norm(w):
    return re.sub(r"[^\wÀ-ỹ]+", "", str(w).lower())


def _find_phrase(anchor, joined):
    """Fuzzy-locate a spoken phrase in the word stream (SKILL-AUTO align_to_speech): exact contiguous →
    ≥70% of tokens in-order within a small window → substring on tokens ≥4 chars. Returns (i,j) or None."""
    a = [x for x in (_norm(t) for t in str(anchor).split()) if x]
    if not a:
        return None
    n, m = len(joined), len(a)
    for i in range(n - m + 1):                          # 1) exact contiguous
        if joined[i:i + m] == a:
            return i, i + m - 1
    win = m + 3                                          # 2) ≥70% in-order within window
    need = max(1, int(0.7 * m))
    for i in range(n):
        seg = joined[i:i + win]
        j = hits = 0
        for wtok in seg:
            if j < m and wtok == a[j]:
                j += 1; hits += 1
        if hits >= need:
            return i, min(n - 1, i + win - 1)
    for i, wtok in enumerate(joined):                   # 3) substring on a ≥4-char token
        if any(len(x) >= 4 and x in wtok for x in a):
            return i, i
    return None


def snap_to_speech(elements, words, lead=0.10, tail=0.80, max_dur=6.0):
    """Time each element that carries a `speech_anchor` (or `anchor`) by WHEN the phrase is spoken —
    author intent by meaning, machine derives the frames. Snaps `t` to phrase start − lead; extends
    `dur` to cover the phrase + tail (never SHORTENS the author's dur). Returns the mutated list."""
    toks = [{"w": _norm(x.get("word", "")), "s": float(x.get("start", 0)), "e": float(x.get("end", 0))}
            for x in (words or [])]
    joined = [t["w"] for t in toks]
    for e in elements or []:
        anc = e.get("speech_anchor") or e.get("anchor")
        if not anc or not toks:
            continue
        r = _find_phrase(anc, joined)
        if not r:
            continue
        i, j = r
        t0 = max(0.0, toks[i]["s"] - lead)
        span = (toks[j]["e"] + tail) - t0
        e["t"] = round(t0, 2)
        e["dur"] = round(min(max_dur, max(float(e.get("dur", 0) or 0), span)), 2)  # never shorten
    return elements


def _role_badge(ctx):
    """Infer (role, badge, emoji_char) from the words around a concept."""
    if any(k in ctx for k in _URGENT):
        return "caution", None, None
    if any(k in ctx for k in _POS):
        return "success", "check", None
    if any(k in ctx for k in _NEG):
        return "danger", "x", None
    return "emphasis", None, None


def pick_elements(words, W=1080, H=1920, *, max_elements=14, min_gap=1.6, top_band=None,
                  zones=None, dur=3.6):
    """Scan `words` (each {word,start,end}) → a timed elements plan. Places tiles/emojis in top-band
    slots (clear of the centred speaker + bottom captions), rotating across slots, density-capped."""
    if not words:
        return []
    toks = [{"w": _norm(w.get("word", "")), "raw": str(w.get("word", "")),
             "t": float(w.get("start", 0))} for w in words]
    text_at = [t["w"] for t in toks]
    # candidate slots: two rows in the TOP third, 3 across — never over the mouth or the caption band
    if zones is None:
        y0, y1 = int(H * 0.12), int(H * 0.30)
        xs = [int(W * 0.05), int(W * 0.37), int(W * 0.69)]
        zones = [(x, y0) for x in xs] + [(x, y1) for x in xs]
    tile_w = int(W * 0.20)
    out, last_t, slot, used_concepts = [], -99.0, 0, set()
    cu_count, lottie_done = 0, False

    i = 0
    while i < len(toks) and len(out) < max_elements:
        t = toks[i]
        if not t["w"] or t["w"] in _STOP or (t["t"] - last_t) < min_gap:
            i += 1
            continue
        ctx = " ".join(text_at[max(0, i - 3):i + 4])     # a small window for cue detection
        emitted = False

        # 0a) a spoken NUMBER → a count_up (prominent animated stat)
        m = _NUM_RE.match(t["raw"].replace(".", "").replace(",", ""))
        if m and int(m.group(1)) >= 10 and cu_count < 2:
            role = "success" if any(k in ctx for k in _POS) else "emphasis"
            lbl = " ".join(t2["raw"] for t2 in toks[i + 1:i + 3]
                           if t2["w"] and t2["w"] not in _STOP)[:22]
            x, y = zones[slot % len(zones)]
            out.append({"type": "count_up", "value": int(m.group(1)), "suffix": m.group(2) or "",
                        "role": role, "label": lbl, "t": round(t["t"], 2), "dur": 2.8,
                        "x": x, "y": y, "anim": "pop"})
            cu_count += 1; last_t = t["t"]; slot += 1; i += 1
            continue

        # 0b) a CELEBRATION beat → a Lottie motion-graphic (once)
        if not lottie_done and any(k in ctx for k in _CELEBRATE):
            src = "check" if any(k in ctx for k in ("hoàn thành", "xong", "done")) else "fireworks"
            x, y = zones[slot % len(zones)]
            out.append({"type": "lottie", "src": src, "t": round(t["t"], 2), "dur": 2.4,
                        "x": x, "y": y, "w": 300, "h": 300})
            lottie_done = True; last_t = t["t"]; slot += 1; i += 1
            continue

        # 1) emoji cue (emphasis/emotion) — a quick pop
        for phrase, name in _EMOJI_CUES.items():
            if phrase in ctx and phrase not in used_concepts:
                x, y = zones[slot % len(zones)]
                out.append({"type": "emoji", "name": name, "t": round(t["t"], 2), "dur": dur,
                            "x": x + tile_w // 3, "y": y, "w": 150, "anim": "pop"})
                used_concepts.add(phrase); last_t = t["t"]; slot += 1; emitted = True
                break
        if emitted:
            i += 1
            continue

        # 2) concept → icon tile (match 1-3 word windows against the alias vocabulary)
        for n in (3, 2, 1):
            gram = " ".join(text_at[i:i + n]).strip()
            if gram and gram in em.ICON_ALIASES and gram not in used_concepts:
                role, badge, _ = _role_badge(ctx)
                label = " ".join(t2["raw"] for t2 in toks[i:i + n]).strip().capitalize()
                x, y = zones[slot % len(zones)]
                out.append({"type": "icon_tile", "icon": gram, "role": role, "badge": badge,
                            "label": label, "t": round(t["t"], 2), "dur": dur,
                            "x": x, "y": y, "w": tile_w, "anim": _ANIMS[slot % len(_ANIMS)]})
                used_concepts.add(gram); last_t = t["t"]; slot += 1
                i += n; emitted = True
                break
        if not emitted:
            i += 1
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    demo = "Làm SEO thủ công rất mất thời gian và tốn chi phí nhưng dùng AI thì tự động và miễn phí"
    ws, tt = [], 0.0
    for w in demo.split():
        ws.append({"word": w, "start": tt, "end": tt + 0.4}); tt += 0.45
    for e in pick_elements(ws):
        print(f"  t={e['t']:>5}  {e['type']:10} {e.get('icon') or e.get('name'):12} "
              f"role={e.get('role','-'):9} badge={e.get('badge')}  '{e.get('label','')}'")
