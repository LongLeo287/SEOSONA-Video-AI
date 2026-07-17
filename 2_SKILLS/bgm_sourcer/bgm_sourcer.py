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
import sys
import json
import time
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BGM_DIR = os.path.join(ROOT, "7_ASSETS", "audio", "bgm")
ATTRIB = os.path.join(BGM_DIR, "ATTRIBUTION.json")
_API = "https://api.openverse.org/v1/audio/"
_UA = "SEOSONA-bgm/1.0 (+https://seosona.ai)"

# Mood → ordered query list, specific first, each falling back to the next on an empty result.
#
# THESE ARE MEASURED, NOT GUESSED. The previous table paired one "specific" query with one broad
# fallback, and three of its four specific queries return ZERO results — Openverse ANDs its terms, so
# a two-word query is already narrow enough to hit nothing:
#
#     tech     'ambient electronic'  -> 0     news    'corporate background' -> 0
#     insight  'inspiring corporate' -> 1     upbeat  'upbeat corporate'     -> 3
#
# So every mood was silently falling through to its one-word fallback, which made `tech` and
# `default` the SAME query ('ambient') and the mood distinction largely fictional. Counts below are
# from a live sweep of 40 candidate terms against `license=by,cc0&category=music` (2026-07-17); each
# list is ordered so the first entry that returns anything is the most specific one that works.
MOOD_QUERY = {
    "tech":    ["ambient electronic", "downtempo", "electronic", "techno", "synth", "ambient"],   # 0/2/39/39/60/64
    "news":    ["corporate", "documentary", "news", "minimal"],                                   # 5/38/158/240
    "insight": ["inspiring corporate", "inspiring", "uplifting", "cinematic", "piano"],           # 1/175/175/173/240
    "upbeat":  ["upbeat corporate", "upbeat", "energetic", "happy", "groove"],                    # 3/240/240/240/18
    "calm":    ["chillout", "calm", "relax", "lounge", "acoustic"],                               # 9/57/36/240/20
    "epic":    ["epic", "dramatic", "orchestral", "cinematic"],                                   # 162/74/15/173
    "default": ["ambient", "instrumental"],                                                       # 64/240
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


# ---------------------------------------------------------------- quality gate
#
# WHY THIS EXISTS. Until now the sourcer downloaded whatever the API returned and put it straight in
# the library — no measurement of any kind. "Creative Commons" says who may use a track, not whether
# it is usable: a CC track that is clipped, or mastered 20dB too quiet, or dead silent for its first
# 30 seconds, is exactly as unusable as a copyrighted one and we would only find out in a render.
#
# The measurements are the same ones the SFX curation uses (ffmpeg astats + ebur128), and the
# thresholds are chosen for a bed that gets DUCKED under a voice: level and cleanliness matter,
# dynamics do not much.
_FF = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
_MIN_LUFS, _MAX_LUFS = -32.0, -8.0     # outside this and it is unmixable, not just quiet
_MAX_FLAT = 3.0                        # astats flat factor: flat runs at full scale = clipped
_MAX_DC = 0.02


def _measure(path):
    """(lufs, true_peak, flat_factor, dc_offset) for a downloaded track, or None if unreadable."""
    if not os.path.exists(_FF):
        return None                                     # no ffmpeg -> cannot gate; caller keeps the track
    try:
        import subprocess
        r = subprocess.run(
            [_FF, "-nostdin", "-hide_banner", "-nostats", "-i", path,
             "-af", "astats=metadata=0,ebur128=peak=true", "-f", "null", "-"],
            capture_output=True, timeout=120)
        err = r.stderr.decode("utf-8", "replace")
        if r.returncode != 0:
            return None
        # ebur128 prints a running `I:` every 100ms starting at its -70 floor and THEN the Summary —
        # so parse the Summary block, never the first match, or every track measures -70.
        tail = err[err.rfind("Summary:"):] if "Summary:" in err else ""
        overall = err[err.rfind("Overall"):] if "Overall" in err else ""
        def num(pat, hay):
            m = re.search(pat, hay)
            try:
                return float(m.group(1)) if m else None
            except ValueError:
                return None
        return (num(r"I:\s*(-?[\d.]+)\s*LUFS", tail),
                num(r"Peak:\s*(-?[\d.]+)\s*dBFS", tail),
                num(r"Flat factor:\s*([\d.]+)", overall),
                num(r"DC offset:\s*(-?[\d.]+)", overall))
    except Exception as e:
        print(f"[bgm] measure failed: {e}")
        return None


def _quality_ok(path):
    """Reject a track we cannot actually mix. Returns (ok, reason)."""
    m = _measure(path)
    if m is None:
        return True, "unmeasured (no ffmpeg)"           # fail OPEN: never lose a track to a missing tool
    lufs, tp, flat, dc = m
    if lufs is None:
        return True, "unmeasured"
    if not (_MIN_LUFS <= lufs <= _MAX_LUFS):
        return False, f"level {lufs:.1f} LUFS outside {_MIN_LUFS}..{_MAX_LUFS}"
    if flat is not None and flat > _MAX_FLAT:
        return False, f"clipped (flat factor {flat:.1f})"
    if dc is not None and abs(dc) > _MAX_DC:
        return False, f"dc offset {dc:.3f}"
    return True, f"{lufs:.1f} LUFS, peak {tp if tp is None else round(tp,1)} dBFS"


def _jamendo_track_id(url):
    """The Jamendo track id behind an Openverse row — the track's REAL identity.

    Openverse dedup is by ITS id, so the same recording surfacing under two Openverse rows (or under
    two queries after re-indexing) downloads twice. The media URL carries `?trackid=20237`, which is
    the same for both. Exact, cheap, and it catches the case that actually happens.
    """
    m = re.search(r"trackid=(\d+)", url or "")
    return m.group(1) if m else None


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


def _candidates(mood, page_size, max_pages):
    """Walk the result PAGES for a mood's queries, most specific query first.

    THE POOL LIMITER THIS FIXES. `_api_get` only ever fetched page 1, so a mood could see at most
    `page_size` (20) candidates in its entire life — 'ambient' has 64 results across 4 pages and 44
    of them were simply unreachable. After the id/quality/duration filters took their cut, a top-up
    run went dry long before the API did, and `--n 30` could never be satisfied no matter how often
    it was run.

    Yields across EVERY query in the mood's list, in order, deduped by Openverse id. Specificity is
    preserved by the ORDER (the narrow queries are listed first, so their rows arrive first) rather
    than by stopping early: the caller breaks as soon as it has `n`, so a query that returns two rows
    which both turn out to be duplicates simply flows on to the next one. Stopping at the first query
    that returned anything looks equivalent and is not — 'downtempo' has exactly 2 results, and
    bailing there capped a `--n 3` top-up of `tech` at 1 track while 'electronic' (39) and 'ambient'
    (64) sat untouched.
    """
    seen = set()
    for q in MOOD_QUERY.get(mood, MOOD_QUERY["default"]):
        for page in range(1, max_pages + 1):
            data = _api_get({"q": q, "license": "by,cc0", "category": "music",
                             "page_size": page_size, "page": page})
            rows = data.get("results") or []
            if not rows:
                break
            for r in rows:
                rid = r.get("id")
                if rid and rid not in seen:
                    seen.add(rid)
                    yield q, r
            if page >= (data.get("page_count") or 1):
                break


def source_bgm(mood="tech", n=1, page_size=20, max_pages=5):
    """Source up to `n` NEW tracks for `mood` into the BGM library. Returns the list of new file paths.

    Every track is filtered on IDENTITY (Openverse id + Jamendo track id + attribution we can
    actually print), then downloaded, then MEASURED — and deleted again if it fails the quality gate.
    Re-runs top up rather than duplicate.
    """
    attrib = _load_attrib()
    have_ids = {a.get("id") for a in attrib}
    have_tracks = {a.get("jamendo_id") for a in attrib if a.get("jamendo_id")}
    new_paths, rejected = [], []
    for q, r in _candidates(mood, page_size, max_pages):
        if len(new_paths) >= n:
            break
        rid = r.get("id")
        dur = (r.get("duration") or 0) / 1000.0
        title = r.get("title") or ""
        creator = r.get("creator") or ""
        lic = (r.get("license") or "").lower()
        if not rid or rid in have_ids:                   # `not rid` guards the rid[:8] below
            continue
        if not (_MIN_S <= dur <= _MAX_S) or not _instrumental_ok(title):
            continue
        media = r.get("url")
        if not media:
            continue
        # CONTENT IDENTITY, not just the API's row id — the same recording under a second Openverse
        # id would otherwise download twice and then rotate against itself as "variety".
        jid = _jamendo_track_id(media)
        if jid and jid in have_tracks:
            continue
        # CC-BY IS ONLY SATISFIED IF THE CREDIT SHIPS. `soundDesign.bgmCreditLine` needs a title, a
        # creator AND a licence to write a real credit line; without them it emits
        # "see 7_ASSETS/audio/bgm/ATTRIBUTION.json", which is not attribution — it points a viewer at
        # a file they do not have. A track we cannot credit is a track we cannot legally publish, so
        # it is refused HERE rather than shipped and quietly under-credited.
        if lic != "cc0" and not (title and creator):
            rejected.append((title or rid, "CC-BY but no title/creator — could not be credited"))
            continue
        fname = f"bgm_{mood}_{rid[:8]}.mp3"
        dst = os.path.join(BGM_DIR, fname)
        if os.path.exists(dst):
            continue
        print(f"[bgm] ↓ {title[:40]!r} ({round(dur)}s, {r.get('license')}) → {fname}")
        if not _download(media, dst):
            continue
        ok, why = _quality_ok(dst)
        if not ok:
            os.remove(dst)                               # a CC track we cannot mix is not a win
            rejected.append((title or rid, why))
            print(f"[bgm]   ✗ rejected: {why}")
            continue
        print(f"[bgm]   ✓ {why}")
        attrib.append({
            "id": rid, "file": fname, "mood": mood, "query": q,
            "title": title or "untitled", "creator": creator,
            "license": f"CC {(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip(),
            "source": r.get("foreign_landing_url") or media, "provider": r.get("provider") or "",
            "jamendo_id": jid, "measured": why,
        })
        have_ids.add(rid)
        if jid:
            have_tracks.add(jid)
        new_paths.append(dst)
    _save_attrib(attrib)
    if new_paths:
        print(f"[bgm] +{len(new_paths)} track(s) for '{mood}'. Attribution → {os.path.relpath(ATTRIB, ROOT)}")
    else:
        print(f"[bgm] nothing new for '{mood}' (all filtered/duplicate/rejected).")
    if rejected:
        print(f"[bgm] {len(rejected)} rejected: " + "; ".join(f"{t[:28]!r} ({w})" for t, w in rejected[:5]))
    return new_paths


if __name__ == "__main__":
    import argparse
    # The documented invocation (`python bgm_sourcer.py --mood tech --n 2`) CRASHED on a stock
    # Windows console: stdout defaults to cp1252, and the very first progress line prints "↓", so the
    # run died with UnicodeEncodeError before downloading anything. It only ever worked when called
    # from something that had already set PYTHONIOENCODING (the engines do; a human does not).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
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
