"""
SEOSONA Video — Translate Router (switchable, primary + backup).

Same pattern as voice_router / asr_router: a primary translation engine with an
automatic backup, switch instantly via SEOSONA_TRANSLATOR.

  - llm    : 4_BRAIN.llm_engine (Gemini/OpenAI) — natural, context-aware, keeps tech
             English terms where idiomatic (matches the code-switch brand voice). [primary]
  - google : deep_translator GoogleTranslator — free, no API key.                  [backup]

Switch:  SEOSONA_TRANSLATOR=google   (default: llm)
"""
import os
from importlib import import_module

_SYS = (
    "You are a professional Vietnamese subtitle translator for a tech-news channel. "
    "Translate faithfully and naturally into fluent spoken Vietnamese. KEEP common English "
    "technical/brand terms in English where a Vietnamese speaker would (e.g. AI, Agent, "
    "machine learning, app, web, marketing). Do not add or drop meaning. Return ONLY the "
    "translation, one line per input line, in the same order."
)


def _llm_translate(lines, src, tgt):
    try:
        llm = import_module("4_BRAIN.llm_engine")
    except Exception:
        return None
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")):
        return None
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(lines))
    prompt = (f"Translate these {len(lines)} subtitle lines from {src} to {tgt}. "
              f"Return JSON: {{\"lines\": [\"...\"]}} with exactly {len(lines)} items, same order.\n\n{numbered}")
    try:
        res = llm.generate_json_from_prompt(_SYS, prompt)
        out = res.get("lines") if isinstance(res, dict) else None
        if out and len(out) == len(lines):
            return [str(x) for x in out]
    except Exception as e:
        print(f"[Translate:llm] failed ({e}).")
    return None


def _google_translate(lines, src, tgt):
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        return None
    try:
        # batch via a unique separator to keep alignment
        sep = "\n@@@\n"
        tr = GoogleTranslator(source=src or "auto", target=tgt).translate(sep.join(lines))
        parts = [p.strip() for p in tr.split("@@@")]
        if len(parts) == len(lines):
            return parts
        # fall back to per-line if the separator got mangled
        return [GoogleTranslator(source=src or "auto", target=tgt).translate(l) for l in lines]
    except Exception as e:
        print(f"[Translate:google] failed ({e}).")
        return None


_ENGINES = {"llm": _llm_translate, "google": _google_translate}


def translate_lines(lines, src="en", tgt="vi"):
    """Translate a list of strings; returns a same-length list (or the originals on total failure)."""
    lines = [l if l is not None else "" for l in lines]
    if not lines:
        return []
    primary = os.environ.get("SEOSONA_TRANSLATOR", "llm")
    for engine in [primary] + [e for e in ("llm", "google") if e != primary]:
        fn = _ENGINES.get(engine)
        if not fn:
            continue
        out = fn(lines, src, tgt)
        if out:
            note = "" if engine == primary else " (fallback)"
            print(f"[Translate Router] engine '{engine}'{note} -> {len(out)} lines.")
            return out
        print(f"[Translate Router] '{engine}' unavailable/failed -> next.")
    print("[Translate Router] WARNING: no translator available — returning source text.")
    return lines


def translate_segments(segments, src="en", tgt="vi"):
    """Translate srt-style segments (each a dict with 'text'); adds 'text_translated'."""
    texts = [s.get("text", "") for s in segments]
    translated = translate_lines(texts, src, tgt)
    for s, t in zip(segments, translated):
        s["text_translated"] = t
    return segments
