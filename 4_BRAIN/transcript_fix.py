# -*- coding: utf-8 -*-
"""Deterministic transcription-correction memory (SKILL AUTO transcribe.py + align_transcript_to_script).

VN ASR mishears English brand/tech names ("Claude"→"cờ lâu", "ChatGPT"→"chat gbt"). Fixing them in a
TABLE at the transcript layer means a mistranscription is corrected once, for ALL future videos — not
per-caption. `fix_brands(text)` applies the table; `fix_against_script(words, script)` additionally
repairs brand-like tokens using OUR canonical `script_writer` output as truth (audio stays the truth
for everything else). The channel's correction memory — grow `_BRAND_FIX` as new mishearings appear.
"""
import re

# lowercase misheard form → correct display form. Order longest-first at apply time.
_BRAND_FIX = {
    "cờ lâu": "Claude", "cờ lau": "Claude", "cláo": "Claude", "chát gpt": "ChatGPT",
    "chat gpt": "ChatGPT", "chat gbt": "ChatGPT", "chát gbt": "ChatGPT", "gpt": "GPT",
    "ô pen ai": "OpenAI", "open ai": "OpenAI", "gemini": "Gemini", "gie mi nai": "Gemini",
    "gít hấp": "GitHub", "git hub": "GitHub", "gít hub": "GitHub", "gu gồ": "Google",
    "gúc gồ": "Google", "phây búc": "Facebook", "phây": "Facebook", "phêis búc": "Facebook",
    "in sờ ta": "Instagram", "tíc tóc": "TikTok", "diu túp": "YouTube", "diu tu bờ": "YouTube",
    "sê ô": "SEO", "ét cần bố": "Search Console", "ây pi ai": "API", "sê mờ rớt": "SEMrush",
    "a rép": "Ahrefs", "a hờ rép": "Ahrefs", "nô sần": "Notion", "hớt mét": "Hotmail",
    "cen va": "Canva", "rê mốt sần": "Remotion", "hai pơ phrêm": "HyperFrames",
    "sê ô sô na": "SEOSONA", "sê ô sô nà": "SEOSONA",
}
_BRAND_ITEMS = sorted(_BRAND_FIX.items(), key=lambda kv: -len(kv[0]))


def fix_brands(text):
    """Apply the brand-correction table to a transcript string (case-insensitive, word-boundary)."""
    out = str(text or "")
    for wrong, right in _BRAND_ITEMS:
        out = re.sub(rf"(?<!\w){re.escape(wrong)}(?!\w)", right, out, flags=re.IGNORECASE)
    return out


def _brandlike(tok):
    """A token worth correcting from the script: has a digit / internal caps / ALL-CAPS / is capitalised."""
    t = tok.strip(".,!?:;")
    return bool(t) and (any(c.isdigit() for c in t) or t.isupper()
                        or (len(t) > 1 and t[1:].lower() != t[1:]) or (t[:1].isupper() and len(t) > 2))


def fix_against_script(words, script_text):
    """Repair ONLY brand-like tokens in ASR `words` [{word,..}] using the canonical script as truth
    (difflib opcodes; audio stays the truth for non-brand words). Returns the mutated words."""
    try:
        from difflib import SequenceMatcher
    except Exception:
        return words
    spoken = [w.get("word", "") for w in (words or [])]
    script = re.findall(r"\S+", script_text or "")
    if not spoken or not script:
        return words
    sm = SequenceMatcher(a=[s.lower() for s in spoken], b=[s.lower() for s in script], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and (i2 - i1) == (j2 - j1):        # equal-length swap = safe brand repair
            for k in range(i2 - i1):
                if _brandlike(script[j1 + k]) and spoken[i1 + k].lower() != script[j1 + k].lower():
                    words[i1 + k]["word"] = script[j1 + k]
        elif tag == "equal":                                    # same word, adopt the script's CASING
            for k in range(i2 - i1):
                if _brandlike(script[j1 + k]) and spoken[i1 + k] != script[j1 + k]:
                    words[i1 + k]["word"] = script[j1 + k]
    return words


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(fix_brands("Mình dùng cờ lâu và chat gbt với sê ô để làm nội dung, đăng lên phây búc"))
