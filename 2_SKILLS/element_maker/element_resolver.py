# -*- coding: utf-8 -*-
"""Self-growing resolver for the SEOSONA element library.

When the factory hits a NEW word/concept that has no element yet, this resolves it to an on-brand
icon (or emoji) — and GROWS the library to cover it: it picks the best Lucide icon (alias → learned
cache → name match → local LLM), **auto-fetches that SVG** into `7_ASSETS/brand/icons/` if it isn't
vendored, and **learns** the concept→icon mapping so next time it's instant. So the resource pool
enriches itself as the factory runs. Fully offline-degradable (LLM optional; falls back to fuzzy
name-matching then a neutral dot). Each concept is resolved ONCE then cached → negligible GPU.

    from element_resolver import resolve_icon, resolve_emoji
    name, is_new = resolve_icon("nam châm")     # → ("magnet", True), magnet.svg fetched + learned
    emoji = resolve_emoji("ăn mừng")            # → "🎉" (learned)
"""
import os
import re
import sys
import json
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ICON_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "icons")
NAMES_FILE = os.path.join(ICON_DIR, "_lucide_names.json")
LEARNED_ICON = os.path.join(ICON_DIR, "_learned_icons.json")
LEARNED_EMOJI = os.path.join(ICON_DIR, "_learned_emoji.json")
RAW = "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{}.svg"


def _load_json(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


# Full Lucide catalog (validate picks + know what's auto-fetchable). Falls back to the vendored set.
_NAMES = set(_load_json(NAMES_FILE, []))
if not _NAMES:
    _NAMES = set(os.path.splitext(f)[0] for f in os.listdir(ICON_DIR) if f.endswith(".svg"))
_learned_icon = _load_json(LEARNED_ICON, {})
_learned_emoji = _load_json(LEARNED_EMOJI, {})


def _save(path, obj):
    try:
        json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    except Exception:
        pass


def _aliases():
    """element_maker's hand-curated alias maps (lazy import to avoid a cycle)."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import element_maker as em
        return em.ICON_ALIASES, em.EMOJI_ALIASES
    except Exception:
        return {}, {}


def _ollama(prompt, timeout=25):
    """One short local-LLM call (auto-detects the running model). None if Ollama is unreachable."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    model = os.getenv("SEOSONA_OLLAMA_MODEL")
    try:
        if not model:
            tags = json.load(urllib.request.urlopen(f"{host}/api/tags", timeout=4))
            model = (tags.get("models") or [{}])[0].get("name")
        if not model:
            return None
        body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                           "options": {"temperature": 0}}).encode()
        req = urllib.request.Request(f"{host}/api/generate", body, {"Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(req, timeout=timeout)).get("response", "").strip()
    except Exception:
        return None


def ensure_icon(name):
    """Guarantee the SVG for `name` is vendored — auto-fetch from Lucide if missing. True if usable."""
    p = os.path.join(ICON_DIR, f"{name}.svg")
    if os.path.exists(p):
        return True
    if name not in _NAMES:
        return False
    try:
        with urllib.request.urlopen(RAW.format(name), timeout=15) as r:
            data = r.read()
        if data and b"<svg" in data:
            open(p, "wb").write(data)
            return True
    except Exception:
        pass
    return False


def _name_match(concept):
    """Fuzzy match an English concept against Lucide icon NAMES (all tokens present → shortest)."""
    toks = [t for t in re.findall(r"[a-z0-9]+", concept) if len(t) > 1]
    if not toks:
        return None
    cands = [n for n in _NAMES if all(t in n for t in toks)]
    if not cands:                      # any single token as a whole word inside the kebab name
        cands = [n for n in _NAMES if any(t == n or t in n.split("-") for t in toks)]
    return min(cands, key=len) if cands else None


def _llm_icon(concept):
    """LLM path = TRANSLATE the concept to plain English nouns (a task a small model does well),
    then match those against the Lucide NAME catalog — far more reliable than asking a weak model to
    recall exact kebab-case icon names (which hallucinates)."""
    out = _ollama(
        f"Translate this concept into 1-3 simple, common English nouns suitable for picking a UI "
        f"icon. Concept: \"{concept}\". Reply with ONLY the English words separated by commas, "
        f"lowercase, no explanation. Example: 'đồng hồ cát' -> hourglass, timer")
    if not out:
        return None
    for w in re.findall(r"[a-z]+", out.lower()):        # first English word that maps to an icon
        if len(w) < 2:
            continue
        if w in _NAMES:
            return w
        hit = _name_match(w)
        if hit:
            return hit
    return None


def _learn_icon(concept, name):
    if concept and name:
        _learned_icon[concept] = name
        _save(LEARNED_ICON, _learned_icon)


def resolve_icon(concept):
    """Resolve a concept/word → a vendored on-brand icon name. Auto-fetches + learns new ones.
    Returns (icon_name, is_new). Never raises — worst case ('circle-dot', False)."""
    c = str(concept or "").lower().strip()
    if not c:
        return "circle-dot", False
    icon_alias, _ = _aliases()
    # 1) curated alias or previously-learned mapping
    for src in (icon_alias, _learned_icon):
        if c in src and ensure_icon(src[c]):
            return src[c], False
    # 2) the concept IS a valid icon name
    if c in _NAMES and ensure_icon(c):
        _learn_icon(c, c); return c, True
    # 3) fuzzy English name match
    hit = _name_match(c)
    if hit and ensure_icon(hit):
        _learn_icon(c, hit); return hit, True
    # 4) local LLM (handles Vietnamese + semantic mapping), validated against the catalog
    name = _llm_icon(c)
    if name and ensure_icon(name):
        _learn_icon(c, name); return name, True
    return "circle-dot", False


def resolve_emoji(concept):
    """Resolve a concept → ONE colour emoji (curated → learned → local LLM → ✨). Learns new ones."""
    c = str(concept or "").lower().strip()
    _, emoji_alias = _aliases()
    for src in (emoji_alias, _learned_emoji):
        if c in src:
            return src[c]
    out = _ollama(f"Reply with EXACTLY ONE emoji that best represents \"{concept}\". "
                  f"Only the emoji, no words.")
    if out:
        m = re.search(r"[\U0001F000-\U0001FAFF☀-➿←-⇿⬀-⯿]", out)
        if m:
            _learned_emoji[c] = m.group(0); _save(LEARNED_EMOJI, _learned_emoji)
            return m.group(0)
    return "✨"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for c in ["nam châm", "xe đẩy hàng", "huy chương", "đám mây", "pin", "kính lúp", "quả bom"]:
        print(f"{c!r:22} → icon {resolve_icon(c)}   emoji {resolve_emoji(c)!r}")
