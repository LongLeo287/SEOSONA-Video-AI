# -*- coding: utf-8 -*-
"""Caption segmentation — break long Vietnamese caption text at NATURAL points, not mid-phrase.

Ported (re-implemented, no import) from Huanshere/VideoLingo (Apache-2.0): split a long line at
sentence boundaries / conjunctions, then enforce a single-line max length. Keeps captions readable
("Netflix" ~42 chars/line) without dragging in VideoLingo's spaCy/pandas/streamlit stack.

Standalone + safe: nothing calls it unless opted in (talking_head_edit `smart_chunk`), so it can't
break the working fixed-N karaoke chunking.
"""
import re

MAX_CHARS = 42

# Vietnamese break tokens — prefer ending a line just before these connectives / after punctuation.
_CONNECTIVES = {"và", "nhưng", "thì", "để", "vì", "nên", "mà", "hoặc", "rồi", "khi",
                "nếu", "là", "cho", "với", "của", "trong", "theo", "bằng"}
_END_PUNCT = tuple(".!?…:;")


def _is_break_after(tok):
    # a HARD boundary that always ends a caption line — sentence/clause enders (. ! ? … : ;). A COMMA is a
    # SOFTER break: handled in segment_words WITH a line-length guard, so a short "Hôm nay, tôi…" (fits one
    # line) isn't needlessly fragmented onto two lines.
    return tok.rstrip().endswith(_END_PUNCT)


def segment_words(words, max_chars=MAX_CHARS):
    """Group word objects [{word,start,end}] into lines that break at natural points and stay
    under max_chars. Returns a list of word-object lists (timings preserved)."""
    lines, cur, cur_len = [], [], 0
    for i, w in enumerate(words):
        tok = str(w.get("word", ""))
        add = len(tok) + (1 if cur else 0)
        # break BEFORE a token that would push the line OVER the limit — so every line stays ≤ max_chars
        # (the old code appended first then broke, leaving the overflowing token on the line → 43-55-char
        # lines that overflow the karaoke pill). A lone token longer than max_chars stays alone (unsplittable).
        if cur and cur_len + add > max_chars:
            lines.append(cur); cur, cur_len = [], 0; add = len(tok)
        cur.append(w); cur_len += add
        nxt = str(words[i + 1].get("word", "")).lower().strip(".,!?:;") if i + 1 < len(words) else ""
        # ALSO break at a natural point: a sentence/clause ender ALWAYS breaks; a softer comma or a
        # pre-connective break only once the line has some body (≥60% of max) — else short captions fragment.
        has_body = cur_len >= max_chars * 0.6
        natural = _is_break_after(tok) or (has_body and (tok.rstrip().endswith(",") or nxt in _CONNECTIVES))
        if natural and i + 1 < len(words):
            lines.append(cur); cur, cur_len = [], 0
    if cur:
        lines.append(cur)
    # merge a tiny trailing line (1-2 words) into the previous one for nicer wrapping — but ONLY if the
    # merged line still fits (else a lonely short line is better than a line that overflows the pill).
    def _ll(line):
        return len(" ".join(str(x.get("word", "")) for x in line))
    if len(lines) >= 2 and len(lines[-1]) <= 2 and _ll(lines[-2]) + 1 + _ll(lines[-1]) <= max_chars:
        lines[-2].extend(lines.pop())
    return lines


# Readability standards (Netflix/BBC timed-text, adopted 2026-07-02): a caption the eye can't read hurts
# retention. CPS = characters-per-second reading-speed ceiling; a cue that flashes < ~0.83s is unreadable.
CPS_MAX = 20
LINE_MAX = 42
MIN_CUE_S = 0.83


def readability_warnings(groups):
    """Flag ASS/karaoke cue groups that break reading-speed standards: too fast (CPS), too long a line, or
    on-screen too briefly. `groups` = [[{word,start,end}, ...], ...] (segment_words output). Advisory —
    returns a list of warnings, empty if all cues are comfortably readable."""
    out = []
    for i, g in enumerate(groups):
        g = [x for x in g if str(x.get("word", "")).strip()]
        if not g:
            continue
        text = " ".join(str(x["word"]) for x in g)
        try:
            dur = float(g[-1]["end"]) - float(g[0]["start"])
        except Exception:
            continue
        cps = (len(text) / dur) if dur > 0 else 999
        if cps > CPS_MAX:
            out.append(f"cue {i}: {cps:.0f} CPS > {CPS_MAX} — too fast to read ('{text[:24]}…')")
        if len(text) > LINE_MAX:
            out.append(f"cue {i}: {len(text)} chars > {LINE_MAX}/line — wraps/too long")
        if 0 < dur < MIN_CUE_S:
            out.append(f"cue {i}: {dur:.2f}s < {MIN_CUE_S}s — flashes too fast to read")
    return out


def segment_text(text, max_chars=MAX_CHARS):
    """Split a plain string into natural lines (≤ max_chars each). Returns a list of strings."""
    words = [{"word": t} for t in text.split()]
    return [" ".join(x["word"] for x in line) for line in segment_words(words, max_chars)]


if __name__ == "__main__":
    import sys
    s = sys.argv[1] if len(sys.argv) > 1 else \
        "Công cụ chỉ đưa ra dữ liệu thôi còn quyết định và chiến lược như thế nào thì phải do bạn quyết định"
    for ln in segment_text(s):
        print(f"[{len(ln):2}] {ln}")
