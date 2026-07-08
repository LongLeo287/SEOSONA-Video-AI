# -*- coding: utf-8 -*-
"""SEOSONA b-roll sourcer — auto-supply a real background VIDEO clip per scene (the video sibling of
`image_sourcer`, which only sourced photos).

Source: **Pixabay video API** (free key, Pixabay Content License = commercial + NO attribution). Search by
concept → download the clip → center-crop to 9:16 via ffmpeg → cache + LEARN the concept→clip mapping so
the kho grows as the factory runs. Reuses `image_sourcer.IMG_QUERY` (VN→English stock query) so both
sourcers share one concept vocabulary. Best-effort with a 429 backoff — never blocks a render.

    from broll_sourcer import source_broll
    clip = source_broll("làm việc")   # → 7_ASSETS/brand/broll/…mp4 (Pixabay, cropped 9:16, cached)
"""
import os
import re
import sys
import json
import time
import hashlib
import urllib.request
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "1_CONFIG"))
sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "image_sourcer"))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
BROLL_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "broll")
CACHE = os.path.join(BROLL_DIR, "_broll_cache.json")

try:                                                    # share the concept→English-query vocabulary
    from image_sourcer import IMG_QUERY
except Exception:
    IMG_QUERY = {}


def _creds_pixabay():
    try:
        from credentials_manager import creds
        return creds.get("pixabay", "api_key") or os.getenv("PIXABAY_API_KEY")
    except Exception:
        return os.getenv("PIXABAY_API_KEY")


def _ffmpeg():
    try:
        from importlib import import_module
        return import_module("native_composer")._ffmpeg_bin()
    except Exception:
        return "ffmpeg"


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
    s = re.sub(r"[^\w]+", "-", str(s).lower().strip()).strip("-")[:40]
    return s or hashlib.md5(str(s).encode()).hexdigest()[:10]


def _api_get(url, tries=3):
    """GET Pixabay JSON with a 429 backoff (free keys rate-limit / need a moment to warm). None on failure."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SEOSONA/1.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(3 * (i + 1))                 # 3s, 6s backoff
                continue
            print(f"[broll] Pixabay HTTP {e.code}")
            return None
        except Exception as e:
            print(f"[broll] Pixabay error ({type(e).__name__})")
            return None
    return None


def _download(url, out):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SEOSONA/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if data and len(data) > 20000:                  # a real clip, not an error page
            open(out, "wb").write(data)
            return out
    except Exception:
        pass
    return None


def _crop_916(src, out, w=1080, h=1920):
    """Center-crop + scale a clip to 9:16 (ffmpeg) so it fills a vertical scene. Falls back to the raw
    clip if ffmpeg fails."""
    import subprocess
    vf = f"crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale={w}:{h},setsar=1"
    try:
        # bound it: the input is an EXTERNALLY-downloaded clip (untrusted); a corrupt/pathological file
        # could make ffmpeg hang this unattended sourcing step. A 30s clip encodes in seconds, so 120s is
        # ample. On timeout fall back to the raw clip — same contract as an ffmpeg failure.
        r = subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                            "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", out],
                           capture_output=True, timeout=120)
    except Exception:      # TimeoutExpired (hang) OR ffmpeg missing → fall back to the raw clip
        return src
    return out if (r.returncode == 0 and os.path.exists(out)) else src


def search_pixabay_video(concept, n=1, min_dur=3, max_dur=30, crop=True):
    """Search Pixabay for a concept → download the best n clips into the kho (cropped 9:16, cached).
    Returns local mp4 paths ([] if no key / no result)."""
    key = _creds_pixabay()
    if not key:
        print("[broll] no PIXABAY_API_KEY — set it in .env (b-roll video disabled).")
        return []
    cache = _load(CACHE, {})
    ck = f"pixabay:{concept}"
    if ck in cache and all(os.path.exists(os.path.join(BROLL_DIR, f)) for f in cache[ck][:n]):
        return [os.path.join(BROLL_DIR, f) for f in cache[ck][:n]]
    query = IMG_QUERY.get(str(concept).lower().strip(), str(concept))
    url = f"https://pixabay.com/api/videos/?key={key}&q={urllib.parse.quote(query)}&per_page={max(n, 5)}"
    j = _api_get(url)
    if not j:
        return []
    os.makedirs(BROLL_DIR, exist_ok=True)
    out = []
    for i, hit in enumerate(j.get("hits", [])):
        if len(out) >= n:
            break
        dur = hit.get("duration", 0)
        if not (min_dur <= dur <= max_dur):
            continue
        vids = hit.get("videos", {}) or {}
        v = vids.get("medium") or vids.get("small") or vids.get("tiny") or {}
        src_url = v.get("url")
        if not src_url:
            continue
        raw = os.path.join(BROLL_DIR, f"_raw_{_slug(concept)}_{i}.mp4")
        if not _download(src_url, raw):
            continue
        fn = f"{_slug(concept)}_{i}.mp4"
        final = os.path.join(BROLL_DIR, fn)
        if crop:
            _crop_916(raw, final)
            try:
                os.remove(raw)
            except Exception:
                pass
        else:
            os.replace(raw, final)
        if os.path.exists(final):
            out.append(final)
    if out:
        cache[ck] = [os.path.basename(p) for p in out]
        _save(CACHE, cache)                             # learn it
    return out


def source_broll(concept, crop=True):
    """Main entry: one on-brand vertical b-roll clip for a scene concept (Pixabay, cached). None if none."""
    r = search_pixabay_video(concept, n=1, crop=crop)
    return r[0] if r else None


def for_scenes(scenes, key="concept"):
    """Given scene dicts, source one b-roll clip per scene by its concept/query. Returns {index: path}."""
    out = {}
    for i, s in enumerate(scenes):
        c = s.get(key) or s.get("h1") or s.get("query")
        if c:
            p = source_broll(c)
            if p:
                out[i] = p
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser(description="Pixabay b-roll video sourcer (9:16, cached)")
    ap.add_argument("--concept", required=True)
    ap.add_argument("-n", type=int, default=1)
    ap.add_argument("--no-crop", action="store_true")
    a = ap.parse_args()
    print("broll:", search_pixabay_video(a.concept, n=a.n, crop=not a.no_crop))
