# -*- coding: utf-8 -*-
"""SEOSONA image sourcer — auto-supply a real illustrative PHOTO for every scene.

The missing input layer: a talking-head/card scene needs a background photo, but the factory had
none (b-roll was user-supplied only). This sources one on demand — **Pexels/Unsplash search** by
concept (free stock, needs an API key) or **scrapes images from a source URL** (og:image + gallery
<img>, no key) — crops to 9:16, caches it, and LEARNS the concept→photo mapping so the photo kho
grows as the factory runs. So `input link/topic → storyboard → a real photo per scene` works with no
human supplying images. The element/motion layer then composites ON TOP of these photos.

    from image_sourcer import source_for_concept, scrape_url_images
    p = source_for_concept("ống kính tele")     # → 7_ASSETS/brand/photos/…jpg (Pexels, cached)
    ps = scrape_url_images("https://…")          # → [paths] scraped from the page
"""
import os
import re
import sys
import json
import hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "1_CONFIG"))
PHOTO_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "photos")
CACHE = os.path.join(PHOTO_DIR, "_photo_cache.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SEOSONA/1.0"}

# Concept (VN/EN) → an English Pexels query (stock search is best in English). Pass-through otherwise.
IMG_QUERY = {
    "ống kính tele": "telephoto lens", "ống kính": "camera lens", "máy ảnh": "camera",
    "hoàng hôn": "sunset city", "thành phố": "city skyline", "chân dung": "portrait photography",
    "phong cảnh": "landscape scenery", "seo": "seo marketing laptop", "marketing": "marketing team",
    "ai": "artificial intelligence technology", "lập trình": "programming code screen",
    "tiền": "money finance", "biểu đồ": "business chart graph", "văn phòng": "modern office",
    "làm việc": "working laptop desk", "học": "study education", "cà phê": "coffee cup",
    "điện thoại": "smartphone hand", "mạng xã hội": "social media phone", "khách hàng": "happy customer",
}

# WORD-level VN→EN lexicon: the scene concept is usually 1-2 VN content words (from _keywords/h1). A raw
# VN string sent to Pexels (English-tagged) returns RANDOM popular photos → a WRONG image. So we MAP the
# VN tokens to English and only search with a mapped query. `terms` = the SPECIFIC (non-generic) English
# nouns a relevant photo's `alt` should mention — used to REJECT off-topic results (ảnh phải đúng).
# value = (english query fragment, [specific terms to validate against the photo's alt]).
_TOKEN_LEX = {
    "ai": ("artificial intelligence", ["intelligence", "robot", "ai"]),
    "agent": ("ai automation robot", ["robot", "automation", "ai"]),
    "seo": ("seo marketing", ["seo", "marketing"]),
    "marketing": ("marketing", ["marketing"]),
    "nội": ("content writing", ["content", "writing"]), "dung": ("content", ["content"]),
    "content": ("content writing", ["content", "writing"]),
    "từ": ("keyword research", ["keyword", "research"]), "khóa": ("keyword research", ["keyword"]),
    "khoá": ("keyword research", ["keyword"]),
    "khách": ("customer service", ["customer", "client"]), "hàng": ("customer", ["customer"]),
    "doanh": ("business office", ["business", "office"]), "nghiệp": ("business", ["business"]),
    "thương": ("brand identity", ["brand"]), "hiệu": ("brand", ["brand"]),
    "chiến": ("strategy planning", ["strategy", "planning"]), "lược": ("strategy", ["strategy"]),
    "dữ": ("data analytics", ["data", "analytics"]), "liệu": ("data analytics", ["data", "analytics"]),
    "phân": ("data analysis", ["data", "analysis", "chart"]), "tích": ("data analysis", ["data", "analysis"]),
    "chất": ("quality inspection", ["quality", "inspection"]), "lượng": ("quality check", ["quality"]),
    "kiểm": ("quality inspection checklist", ["inspection", "check", "quality"]),
    "duyệt": ("review approval", ["review", "approval", "checklist"]),
    "tra": ("inspection check", ["inspection", "check"]),
    "nghiên": ("research study", ["research", "study"]), "cứu": ("research", ["research"]),
    "tự": ("automation", ["automation", "robot"]), "động": ("automation robot", ["automation", "robot"]),
    "quy": ("workflow process", ["workflow", "process"]), "trình": ("workflow process", ["workflow", "process"]),
    "công": ("tools technology", ["tools", "technology"]), "cụ": ("tools", ["tools"]),
    "nghệ": ("technology", ["technology"]),
    "website": ("website design", ["website", "web"]), "web": ("website", ["website", "web"]),
    "video": ("video production", ["video", "camera"]),
    "hình": ("photography", ["photography", "photo"]), "ảnh": ("photography", ["photography", "photo"]),
    "thiết": ("graphic design", ["design"]), "kế": ("design", ["design"]),
    "code": ("programming code screen", ["code", "programming"]),
    "xu": ("growth trend chart", ["growth", "trend", "chart"]), "hướng": ("trend direction", ["trend"]),
    "tăng": ("growth chart", ["growth", "chart"]), "trưởng": ("growth", ["growth"]),
    "lợi": ("success advantage", ["success"]), "thế": ("advantage success", ["success"]),
    "cạnh": ("competition", ["competition"]), "tranh": ("competition", ["competition"]),
    "đội": ("business team", ["team"]), "ngũ": ("team", ["team"]), "nhóm": ("team group", ["team"]),
    "học": ("education learning", ["education", "learning"]),
    "đào": ("training education", ["training", "education"]), "tạo": ("creation building", ["building"]),
    "thời": ("time clock", ["time", "clock"]), "gian": ("time", ["time"]),
    "kết": ("results success", ["results", "success"]), "quả": ("results", ["results"]),
    "tốc": ("speed motion", ["speed", "motion"]), "độ": ("speed", ["speed"]),
    "sáng": ("creative idea", ["creative", "idea"]), "tạo ": ("creative", ["creative"]),
    "văn": ("office", ["office"]), "phòng": ("office", ["office"]),
    "tiền": ("money finance", ["money", "finance"]), "doanh thu": ("revenue finance", ["finance", "revenue"]),
    "công nghệ": ("technology", ["technology"]), "trí tuệ": ("artificial intelligence", ["intelligence"]),
}
# generic English words that DON'T count as a relevance match (too broad to prove the photo is on-topic).
_GENERIC_TERMS = {"technology", "business", "modern", "office", "team", "working", "digital", "concept"}


def _build_query(concept):
    """VN/EN concept → (english_query, specific_terms). Returns (None, []) when nothing maps — better NO
    photo than a WRONG one. specific_terms drive the relevance gate against each photo's English `alt`."""
    c = str(concept or "").lower().strip()
    if not c:
        return None, []
    if c in IMG_QUERY:                                   # exact known phrase
        q = IMG_QUERY[c]
        return q, [w for w in re.findall(r"[a-z]+", q) if w not in _GENERIC_TERMS]
    frags, terms = [], []
    for tok in re.findall(r"[\wÀ-ỹ]+", c):
        hit = _TOKEN_LEX.get(tok)
        if hit:
            frags.append(hit[0]); terms.extend(hit[1])
    # also catch known 2-word phrases ("công nghệ", "trí tuệ", "doanh thu")
    for phrase, hit in _TOKEN_LEX.items():
        if " " in phrase and phrase in c:
            frags.append(hit[0]); terms.extend(hit[1])
    if not frags:                                        # nothing mapped → don't guess with VN text
        return None, []
    seen, q = set(), []
    for w in " ".join(frags).split():
        if w not in seen:
            seen.add(w); q.append(w)
    spec = [t for t in dict.fromkeys(terms) if t not in _GENERIC_TERMS]
    return " ".join(q[:5]), spec


def _creds_pexels():
    try:
        from credentials_manager import creds
        return creds.get("pexels", "api_key")
    except Exception:
        return os.getenv("PEXELS_API_KEY")


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


def _download(url, out):
    import requests
    try:
        r = requests.get(url, headers=UA, timeout=20)
        if r.status_code == 200 and r.content and len(r.content) > 4000:
            open(out, "wb").write(r.content)
            return out
    except Exception:
        pass
    return None


def _crop_916(path, w=1080, h=1920):
    """Center-crop a photo to 9:16 and resize — so it fills a vertical scene predictably."""
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        tw, th = im.size
        target = w / h
        if tw / th > target:                     # too wide → crop sides
            nw = int(th * target); im = im.crop(((tw - nw) // 2, 0, (tw + nw) // 2, th))
        else:                                     # too tall → crop top/bottom
            nh = int(tw / target); im = im.crop((0, (th - nh) // 2, tw, (th + nh) // 2))
        # LANCZOS is the quality-best resampler for DOWNSCALING (stock photos are far larger than
        # 1080×1920); the default (BICUBIC) is softer. These are the scene backgrounds viewers see.
        im.resize((w, h), Image.LANCZOS).save(path, quality=88)
        return path
    except Exception:
        return path


def _alt_relevant(alt, terms):
    """A photo's English `alt` is relevant only if it contains a specific term as a WHOLE WORD. A bare
    `t in alt` substring test matched 'ai' inside hair/rain/brain/train/email/mountain/captain/air, 'seo'
    in Seoul, 'code' in barcode, 'time' in maritime — so wildly off-topic stock photos passed the gate.
    Empty terms → accept by Pexels rank (the query was all-generic). English alt → \\b works cleanly."""
    if not terms:
        return True
    low = str(alt or "").lower()
    return any(re.search(r"\b" + re.escape(t) + r"\b", low) for t in terms)


def search_pexels(concept, n=1, orientation="portrait", crop=True):
    """Search Pexels for a concept → download the best n vertical photos into the kho. Cached.
    Returns a list of local paths ([] if no key / no result)."""
    import requests
    if not str(concept or "").strip():
        # empty concept (e.g. a scene with no concept/h1/title) → NO query: a blank Pexels search both
        # wastes an API call AND returns RANDOM popular photos → an off-topic image on that scene. The
        # caller (native_composer) already handles [] gracefully (no photo / synthetic fallback).
        return []
    key = _creds_pexels()
    if not key:
        print("[image] no PEXELS_API_KEY — set it in .env (Pexels path disabled; URL-scrape still works)")
        return []
    cache = _load(CACHE, {})
    ck = f"pexels:{concept}"
    if ck in cache and all(os.path.exists(os.path.join(PHOTO_DIR, f)) for f in cache[ck][:n]):
        return [os.path.join(PHOTO_DIR, f) for f in cache[ck][:n]]
    # VN concept → a MAPPED English query. If nothing maps, we do NOT send the raw VN string (Pexels
    # would return random popular photos = a WRONG image); return [] so the scene uses a non-photo comp.
    query, terms = _build_query(concept)
    if not query:
        print(f"[image] no confident query for '{concept}' — skipping (thà không ảnh còn hơn ảnh sai)")
        return []
    os.makedirs(PHOTO_DIR, exist_ok=True)
    out = []
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "orientation": orientation, "per_page": 15, "size": "large"},
                         headers={"Authorization": key}, timeout=20)
        photos = (r.json() or {}).get("photos", []) if r.status_code == 200 else []
    except Exception as e:
        print(f"[image] pexels failed ({e})"); return []
    # RELEVANCE GATE — keep only photos whose English `alt` mentions a SPECIFIC concept term. Pexels ranks
    # by query but a generic query can still surface off-topic hero shots; this rejects them. If we have
    # no specific terms (query was all-generic), accept by rank (Pexels relevance is enough there).
    def _relevant(ph):
        return _alt_relevant(ph.get("alt"), terms)
    ranked = [ph for ph in photos if _relevant(ph)] or ([] if terms else photos)
    if not ranked:
        print(f"[image] no RELEVANT photo for '{concept}' (query='{query}', terms={terms}) — skipping")
        return []
    for i, ph in enumerate(ranked[:n]):
        src = (ph.get("src") or {}).get("portrait") or (ph.get("src") or {}).get("large2x")
        if not src:
            continue
        fn = f"{_slug(concept)}_{i}.jpg"
        p = _download(src, os.path.join(PHOTO_DIR, fn))
        if p:
            if crop:
                _crop_916(p)
            out.append(p)
    if out:
        cache[ck] = [os.path.basename(p) for p in out]; _save(CACHE, cache)   # learn it
    return out


def scrape_url_images(url, n=6, min_w=500, crop=False):
    """Scrape illustrative images from a source page: og:image + gallery <img> (src/srcset).
    Downloads the good-sized ones into the kho. No API key needed. Returns local paths."""
    import requests
    try:
        html = requests.get(url, headers=UA, timeout=20).text
    except Exception as e:
        print(f"[image] fetch failed ({e})"); return []
    urls = []
    for m in re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', html, re.I):
        urls.append(m)
    for m in re.findall(r'<img[^>]+(?:data-src|src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)', html, re.I):
        urls.append(m)
    # absolutise + dedupe, keep order
    base = re.match(r"(https?://[^/]+)", url)
    seen, clean = set(), []
    for u in urls:
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/") and base:
            u = base.group(1) + u
        if u.startswith("http") and u not in seen:
            seen.add(u); clean.append(u)
    os.makedirs(PHOTO_DIR, exist_ok=True)
    out = []
    for i, u in enumerate(clean):
        if len(out) >= n:
            break
        fn = f"scrape_{_slug(url)}_{i}.jpg"
        p = _download(u, os.path.join(PHOTO_DIR, fn))
        if not p:
            continue
        try:
            from PIL import Image
            w, h = Image.open(p).size
            if w < min_w or (w / h > 3 or h / w > 3):    # skip tiny / banner-strip images
                os.remove(p); continue
        except Exception:
            os.remove(p); continue
        if crop:
            _crop_916(p)
        out.append(p)
    return out


def dominant_color(path, fallback="#2A5BDA"):
    """Extract a photo's dominant SATURATED colour → hex, for per-scene colour harmony (tint the
    frame border / step number / keyword to match the photo, so each scene feels cohesive)."""
    try:
        from PIL import Image
        from collections import Counter
        im = Image.open(path).convert("RGB").resize((72, 72))
        def sat(c):
            mx, mn = max(c), min(c); return (mx - mn) / (mx + 1)
        # getdata() is deprecated and removed in Pillow 14 (2027-10); prefer its drop-in replacement
        # when present, fall back on older Pillow. Same flat list of (r,g,b) tuples either way.
        px = list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())
        pool = [c for c in px if sat(c) > 0.28 and 42 < sum(c) / 3 < 224] or px
        r, g, b = Counter(pool).most_common(1)[0][0]
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception:
        return fallback


def source_logo(brand, out_dir=None):
    """Fetch a brand/tool LOGO from Wikipedia (KEYLESS) — for showing a client/tool logo when named.
    Scores the page's images for logo-likeness (logo/wordmark/svg + brand-token, blocks photos/chrome),
    downloads the best, caches. Returns a local path or None. (SKILL AUTO fetch_logo, ported.)"""
    import requests
    out_dir = out_dir or PHOTO_DIR
    cache = _load(CACHE, {})
    ck = f"logo:{str(brand).lower().strip()}"
    if ck in cache and os.path.exists(os.path.join(out_dir, cache[ck])):
        return os.path.join(out_dir, cache[ck])
    api = "https://en.wikipedia.org/w/api.php"

    def _get(params):
        try:
            return requests.get(api, params={**params, "format": "json"}, headers=UA, timeout=15).json()
        except Exception:
            return {}
    # 1) find the page (title candidates → search fallback)
    title = None
    for cand in (brand, f"{brand} (company)", f"{brand} (software)"):
        d = _get({"action": "query", "titles": cand, "prop": "info"})
        pages = (d.get("query", {}) or {}).get("pages", {})
        if pages and "-1" not in pages:
            title = next(iter(pages.values())).get("title"); break
    if not title:
        d = _get({"action": "query", "list": "search", "srsearch": f"{brand} logo", "srlimit": 1})
        hits = (d.get("query", {}) or {}).get("search", [])
        if hits:
            title = hits[0]["title"]
    if not title:
        return None
    # 2) the page's images → score by logo-likeness
    d = _get({"action": "query", "titles": title, "prop": "images", "imlimit": 60})
    imgs = [im["title"] for p in (d.get("query", {}) or {}).get("pages", {}).values()
            for im in (p.get("images") or [])]
    bt = re.sub(r"[^a-z0-9]", "", str(brand).lower())

    def _score(fn):
        f = fn.lower()
        if not f.endswith((".svg", ".png", ".jpg", ".jpeg")):
            return -99
        if any(b in f for b in ("commons-logo", "edit-", "wiki", "ambox", "question_book",
                                "folder", "increase", "decrease", "red_x", "check", "padlock", "portal")):
            return -99
        s = 0
        if "logo" in f: s += 3
        if "wordmark" in f or f.endswith(".svg"): s += 2
        if bt and bt[:6] in re.sub(r"[^a-z0-9]", "", f): s += 3
        if any(x in f for x in ("photo", "ceo", "founder", "building", "headquarters")): s -= 4
        return s
    best = max(imgs, key=_score, default=None)
    if not best or _score(best) < 1:
        return None
    # 3) resolve the file URL (imageinfo) + download
    d = _get({"action": "query", "titles": best, "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 400})
    url = None
    for p in (d.get("query", {}) or {}).get("pages", {}).values():
        ii = p.get("imageinfo") or []
        if ii:
            url = ii[0].get("thumburl") or ii[0].get("url"); break
    if not url:
        return None
    os.makedirs(out_dir, exist_ok=True)
    fn = f"logo_{_slug(brand)}.png"
    p = _download(url, os.path.join(out_dir, fn))
    if p:
        cache[ck] = fn; _save(CACHE, cache)
    return p


def source_for_concept(concept, crop=True):
    """Main entry: one on-brand vertical photo for a scene concept (Pexels, cached). None if unavailable."""
    r = search_pexels(concept, n=1, crop=crop)
    return r[0] if r else None


def assign_from_url(scenes, url, n=8):
    """Scrape images from a source URL and round-robin assign them to photocard/mockup/repo scenes
    that have no img yet — so a video built FROM a link uses the LINK'S OWN real images (the "input
    link → cào ảnh → storyboard có ảnh" path). Returns the count assigned. Falls back silently."""
    pool = scrape_url_images(url, n=n)
    if not pool:
        return 0
    k = 0
    for sc in scenes:
        comp = sc.get("comp")
        if (comp and isinstance(comp, (list, tuple)) and len(comp) == 2 and isinstance(comp[1], dict)
                and comp[0] in ("photocard", "mockup", "repo") and not comp[1].get("img")):
            comp[1]["img"] = os.path.abspath(pool[k % len(pool)]); k += 1
    return k


def for_scenes(scenes, key="concept"):
    """Given scene dicts, source one photo per scene by its concept/query. Returns {index: path}."""
    out = {}
    for i, s in enumerate(scenes):
        c = s.get(key) or s.get("h1") or s.get("query")
        if c:
            p = source_for_concept(c)
            if p:
                out[i] = p
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept"); ap.add_argument("--url"); ap.add_argument("-n", type=int, default=3)
    a = ap.parse_args()
    if a.url:
        print("scraped:", scrape_url_images(a.url, n=a.n))
    elif a.concept:
        print("pexels:", search_pexels(a.concept, n=a.n))
    else:
        print("usage: --concept '<concept>' | --url '<page>'")
