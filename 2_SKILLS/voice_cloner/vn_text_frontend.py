"""
SEOSONA Video — Vietnamese text front-end (undertheseanlp/underthesea).

Two jobs the TTS + subtitle stages were missing a real VN-aware layer for:
  - normalize_for_tts(text)   : clean + normalize VN text and expand digit runs to spoken words
                                so the TTS reads "2025" / "15%" naturally, not digit-by-digit.
  - split_for_subtitle(text)  : sentence/segment split for clean subtitle line breaks.

Honest fallback: if `underthesea` is not installed, normalization degrades to light regex cleanup
and splitting falls back to punctuation — never raises, never fabricates.
"""
import re

try:
    from underthesea import text_normalize as _uts_normalize, sent_tokenize as _uts_sent
    _HAS_UTS = True
except Exception:  # noqa: BLE001
    _HAS_UTS = False

_ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def _read_int(n):
    """Small VN number-to-words for 0..9999 (covers years, counts, percentages in scripts)."""
    n = int(n)
    if n < 10:
        return _ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        s = ("mười" if t == 1 else f"{_ONES[t]} mươi")
        if o:
            s += " " + ("mốt" if o == 1 and t > 1 else ("lăm" if o == 5 and t > 0 else _ONES[o]))
        return s
    if n < 1000:
        h, r = divmod(n, 100)
        s = f"{_ONES[h]} trăm"
        if r:
            s += (" lẻ " + _ONES[r]) if r < 10 else " " + _read_int(r)
        return s
    th, r = divmod(n, 1000)
    s = f"{_read_int(th)} nghìn"
    if r:
        s += (" không trăm " if r < 100 else " ") + _read_int(r)
    return s


def _expand_numbers(text):
    text = re.sub(r"(\d+)\s*%", lambda m: _read_int(m.group(1)) + " phần trăm", text)
    return re.sub(r"\b\d{1,4}\b", lambda m: _read_int(m.group(0)), text)


def normalize_for_tts(text):
    if not text:
        return text
    base = _uts_normalize(text) if _HAS_UTS else re.sub(r"\s+", " ", text).strip()
    try:
        return _expand_numbers(base)
    except Exception:  # noqa: BLE001
        return base


def split_for_subtitle(text):
    if not text:
        return []
    if _HAS_UTS:
        try:
            return [s.strip() for s in _uts_sent(text) if s.strip()]
        except Exception:  # noqa: BLE001
            pass
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]


if __name__ == "__main__":
    print(normalize_for_tts("Năm 2025 tăng 15% so với trước."))
    print(split_for_subtitle("Câu một. Câu hai! Câu ba?"))
