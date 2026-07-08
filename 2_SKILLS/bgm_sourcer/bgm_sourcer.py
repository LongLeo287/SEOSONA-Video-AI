# -*- coding: utf-8 -*-
"""BGM sourcer — grow the background-music library with REAL royalty-free tracks by mood, FREE + keyless.

The built-in library ships one track per mood (tech/news/insight/upbeat), so every video of a mood reuses
the identical music. This sources fresh full-length tracks from Openverse (→ Jamendo CC music), downloads
them into `7_ASSETS/audio/bgm/` as `bgm_<mood>_<id>.mp3`, and records attribution so the CC-BY obligation
is honoured. `native_composer._bgm(mood)` then rotates across the whole mood pool for variety.

    python 2_SKILLS/bgm_sourcer/bgm_sourcer.py --mood tech --n 2
    python 2_SKILLS/bgm_sourcer/bgm_sourcer.py --all --n 2      # top up every mood

Openverse audio is keyless (light rate limit). License: we take `cc0` + `by` (CC-BY needs attribution —
recorded in ATTRIBUTION.json; the publisher puts it in the video description). Best-effort; never raises.
"""
import os
import re
import json
import time
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BGM_DIR = os.path.join(ROOT, "7_ASSETS", "audio", "bgm")
ATTRIB = os.path.join(BGM_DIR, "ATTRIBUTION.json")
_API = "https://api.openverse.org/v1/audio/"
_UA = "SEOSONA-bgm/1.0 (+https://seosona.ai)"

# Mood → (primary query, broader fallback). Openverse ANDs terms, so >3 words often returns nothing —
# keep queries short and fall back broader on an empty result. Instrumental/non-distracting beds (BGM
# ducks under the voice, which stays the hero).
MOOD_QUERY = {
    "tech": ("ambient electronic", "ambient"),
    "news": ("corporate background", "corporate"),
    "insight": ("inspiring corporate", "inspiring"),
    "upbeat": ("upbeat corporate", "upbeat"),
    "default": ("ambient corporate", "ambient"),
}
_MIN_S, _MAX_S = 45, 360          # loops well, not a jingle; not an epic. (BGM loops under the voice.)
_BAD_TITLE = ("vocal", "lyric", "feat.", "remix", "acapella")   # distinctive → substring is safe (catches vocals/lyrics/remixed)
_BAD_WORD = ("rap",)      # SHORT → WHOLE-WORD only, else 'wrap'/'rapid'/'therapy'/'grape' falsely reject a good instrumental bed


def _api_get(params, retries=3):
    url = _API + "?" + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except Exception as e:
            if "429" in str(e) and i < retries - 1:
                time.sleep(2 * (i + 1))                 # rate-limit backoff
                continue
            print(f"[bgm] api error: {e}")
            return {}
    return {}


def _download(url, dst):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as r, open(dst, "wb") as f:
            f.write(r.read())
        return os.path.getsize(dst) > 20000            # a real track, not an error page
    except Exception as e:
        print(f"[bgm] download failed: {e}")
        if os.path.exists(dst):
            os.remove(dst)
        return False


def _load_attrib():
    try:
        return json.load(open(ATTRIB, encoding="utf-8"))
    except Exception:
        return []


def _save_attrib(rows):
    os.makedirs(BGM_DIR, exist_ok=True)
    json.dump(rows, open(ATTRIB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _instrumental_ok(title):
    t = (title or "").lower()
    if any(b in t for b in _BAD_TITLE):
        return False
    # short tokens need a word boundary — a bare 'rap' in 'wrap'/'rapid'/'therapy' would reject a good bed
    return not any(re.search(r"\b" + w + r"\b", t) for w in _BAD_WORD)


def source_bgm(mood="tech", n=1, page_size=20):
    """Source up to `n` NEW tracks for `mood` into the BGM library. Returns the list of new file paths.
    Skips tracks already recorded (by Openverse id) so re-runs top up rather than duplicate."""
    primary, fallback = MOOD_QUERY.get(mood, MOOD_QUERY["default"])
    results = []
    for q in (primary, fallback):                       # broaden the query if the specific one is dry
        data = _api_get({"q": q, "license": "by,cc0", "category": "music", "page_size": page_size})
        results = data.get("results") or []
        if results:
            break
    if not results:
        print(f"[bgm] no results for mood '{mood}' (q={primary!r}/{fallback!r})")
        return []
    attrib = _load_attrib()
    have_ids = {a.get("id") for a in attrib}
    new_paths = []
    for r in results:
        if len(new_paths) >= n:
            break
        rid = r.get("id")
        dur = (r.get("duration") or 0) / 1000.0
        title = r.get("title") or "untitled"
        if not rid or rid in have_ids or not (_MIN_S <= dur <= _MAX_S) or not _instrumental_ok(title):
            continue                                     # `not rid` guards the rid[:8] below (malformed API row)
        media = r.get("url")
        if not media:
            continue
        fname = f"bgm_{mood}_{rid[:8]}.mp3"
        dst = os.path.join(BGM_DIR, fname)
        if os.path.exists(dst):
            continue
        print(f"[bgm] ↓ {title[:40]!r} ({round(dur)}s, {r.get('license')}) → {fname}")
        if _download(media, dst):
            attrib.append({
                "id": rid, "file": fname, "mood": mood,
                "title": title, "creator": r.get("creator") or "",
                "license": f"CC {(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip(),
                "source": r.get("foreign_landing_url") or media, "provider": r.get("provider") or "",
            })
            have_ids.add(rid)
            new_paths.append(dst)
    _save_attrib(attrib)
    if new_paths:
        print(f"[bgm] +{len(new_paths)} track(s) for '{mood}'. Attribution → {os.path.relpath(ATTRIB, ROOT)}")
    else:
        print(f"[bgm] nothing new for '{mood}' (all filtered/duplicate).")
    return new_paths


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mood", default="tech")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--all", action="store_true", help="top up every mood")
    a = ap.parse_args()
    moods = [m for m in MOOD_QUERY if m != "default"] if a.all else [a.mood]
    total = 0
    for m in moods:
        total += len(source_bgm(m, n=a.n))
    print(f"\n[bgm] done — {total} new track(s) across {len(moods)} mood(s).")
