# -*- coding: utf-8 -*-
"""SEOSONA image generation — synthetic backgrounds + thumbnail art via NVIDIA NIM FLUX (free).

Fills the "no image-gen" gap: `image_sourcer` (Pexels) and `broll_sourcer` (Pixabay) give REAL stock
media; this generates SYNTHETIC/abstract art for scenes/thumbnails where no stock photo fits. Model =
`black-forest-labs/flux.1-schnell` (1–4 steps, fast). NIM-native endpoint (NOT OpenAI-compatible): the
image returns base64 under `artifacts[0].base64`. Free NVIDIA tier = ~40 RPM + finite credits → CACHE
HARD (1 credit/image); use for thumbnails (1/video) + hero backgrounds, NOT every scene. Best-effort:
returns None (→ caller falls back to stock/solid) so a render never depends on it.

    from image_gen import generate, for_concept
    p = generate("SEO dashboard analytics")   # → 7_ASSETS/brand/photos/gen/…png (brand-styled, cached)
"""
import os
import re
import sys
import json
import base64
import hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEN_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "photos", "gen")
CACHE = os.path.join(GEN_DIR, "_gen_cache.json")
_ENDPOINT = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell"
# brand contract baked into every prompt: light-only, SEOSONA blue/coral, clean, NO text (text is added
# by our own render/thumbnail layer — a generated image with garbled letters looks broken).
_BRAND = ("flat vector illustration, minimalist, clean, light background, soft shadows, "
          "SEOSONA brand palette blue #2A5BDA and coral #E2724D accents, professional, NO text, no words")


def _key():
    return os.getenv("NVIDIA_API_KEY")


def _load(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def _save(p, o):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    except Exception:
        pass


def _slug(s):
    return re.sub(r"[^\w]+", "-", str(s).lower().strip()).strip("-")[:40] or hashlib.md5(str(s).encode()).hexdigest()[:10]


def generate(prompt, out=None, *, width=1024, height=1024, steps=4, seed=0, brand=True, crop916=False):
    """Generate one image from `prompt` (brand-styled unless brand=False) → PNG path, or None. Cached by
    the full prompt+size so the same request never re-burns a credit."""
    key = _key()
    if not key:
        print("[image_gen] no NVIDIA_API_KEY — image generation disabled.")
        return None
    full = f"{prompt.strip()}, {_BRAND}" if brand else prompt.strip()
    ck = hashlib.md5(f"{full}|{width}x{height}|{steps}".encode()).hexdigest()[:16]
    cache = _load(CACHE, {})
    if ck in cache and os.path.exists(os.path.join(GEN_DIR, cache[ck])):
        return os.path.join(GEN_DIR, cache[ck])
    try:
        import urllib.request
        # FLUX.1-schnell is CFG-distilled → cfg_scale MUST be 0 (the API rejects >0 with HTTP 422).
        body = json.dumps({"prompt": full, "mode": "base", "cfg_scale": 0,
                           "width": width, "height": height, "steps": steps, "seed": seed}).encode()
        req = urllib.request.Request(_ENDPOINT, data=body,
            headers={"Authorization": "Bearer " + key, "Accept": "application/json",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:   # free image tier can queue slowly
            j = json.loads(r.read())
        arts = j.get("artifacts") or []
        b64 = arts[0].get("base64") if arts else None
        if not b64:
            print(f"[image_gen] no artifact returned ({str(j)[:120]})")
            return None
    except Exception as e:
        print(f"[image_gen] FLUX failed ({type(e).__name__}: {str(e)[:80]})")
        return None
    os.makedirs(GEN_DIR, exist_ok=True)
    out = out or os.path.join(GEN_DIR, f"{_slug(prompt)}_{ck}.png")
    open(out, "wb").write(base64.b64decode(b64))
    if crop916:
        try:                                                # crop the square/landscape to 9:16
            sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "image_sourcer"))
            from image_sourcer import _crop_916
            _crop_916(out)
        except Exception:
            pass
    cache[ck] = os.path.basename(out); _save(CACHE, cache)   # learn it
    return out


def for_concept(concept, crop916=True):
    """One brand-styled synthetic 9:16 background for a scene concept (cached). None if unavailable."""
    return generate(concept, width=1024, height=1024, crop916=crop916)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="NVIDIA FLUX image generation (brand-styled, cached)")
    ap.add_argument("prompt")
    ap.add_argument("--raw", action="store_true", help="no brand styling")
    ap.add_argument("--crop916", action="store_true")
    a = ap.parse_args()
    print("image:", generate(a.prompt, brand=not a.raw, crop916=a.crop916))
