# -*- coding: utf-8 -*-
"""Web RESEARCH for the FETCH stage — topic → REAL facts from multiple sources, FREE (no API key).

The factory is given a TOPIC (e.g. "SEO 2026 ở TP.HCM"), not data. This gathers real, recent
Vietnamese information to ground the script on: Google News RSS for discovery + a best-effort fetch
of a few article bodies (markitdown → clean text). The writer then may ONLY use what's gathered here,
and the traceability gate rejects any number/name that isn't in it.

Pattern adopted from the RSS/news-pipeline repos in the inventory (dantech0xff/daily-news-broadcast,
RSSNext/Folo). firecrawl/crawl4ai are NOT vendored — they need keys / are heavy; RSS + stdlib is free.
Network is always best-effort with short timeouts — research never hangs a render.
"""
import os
import re
import json
import html
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# Load .env HERE, at import — the web sources below read FIRECRAWL_API_KEY / PAGESPEED_API_KEY directly,
# and research() runs BEFORE anything imports llm_engine (which is what usually loads .env). Without this,
# the FIRST (often only) research call in a process sees no key → _firecrawl_search silently returns [] →
# evergreen topics fall back to News RSS → wrong-subject grounding. Anchor the path to this file's repo root
# so it works regardless of CWD; load_dotenv never overrides vars already set, so it clobbers nothing.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

_UA = "Mozilla/5.0 (compatible; SEOSONA-research/1.0)"
# a real browser UA — DDG's keyless HTML search endpoint anomaly-blocks the bot UA above.
_UA_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
_TIMEOUT = float(os.environ.get("SEOSONA_RESEARCH_TIMEOUT", "10"))


def _get(url, timeout=_TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept-Language": "vi,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _strip_html(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s or "")
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def news_rss(query, hl="vi", gl="VN", n=8):
    """Google News RSS search (free, no key) → [{title, link, source, date, snippet}] (real, recent VN)."""
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
    items = []
    try:
        root = ET.fromstring(_get(url))
    except Exception as e:
        print(f"[researcher] RSS failed ({e})")
        return items
    for it in list(root.iter("item"))[:n]:
        def g(tag):
            el = it.find(tag)
            return (el.text or "").strip() if el is not None and el.text else ""
        src = it.find("source")
        items.append({"title": _strip_html(g("title")), "link": g("link"),
                      "source": (src.text.strip() if src is not None and src.text else ""),
                      "date": g("pubDate"), "snippet": _strip_html(g("description"))})
    return items


def trends_vn(geo="VN", n=12):
    """Google 'Trending Now' RSS (keyless) → real search-DEMAND queries in Vietnam right now, each with a
    traffic band + linked news. News-RSS tells us what's PUBLISHED; this tells us what people SEARCH —
    so topic selection becomes demand-driven. Same best-effort pattern as news_rss(); never raises.
    Returns [{query, traffic, news:[url,...]}]."""
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    ns = {"ht": "https://trends.google.com/trending/rss"}
    out = []
    try:
        root = ET.fromstring(_get(url))
    except Exception as e:
        print(f"[researcher] trends RSS failed ({e})")
        return out
    for it in list(root.iter("item"))[:n]:
        title = (it.findtext("title") or "").strip()
        if not title:
            continue
        traffic = (it.findtext("ht:approx_traffic", default="", namespaces=ns) or "").strip()
        news = [n_.text for n_ in it.findall("ht:news_item/ht:news_item_url", ns) if n_.text]
        out.append({"query": title, "traffic": traffic, "news": news})
    return out


def autocomplete(seed, hl="vi", gl="vn", gprop=""):
    """Keyless Google/YouTube autocomplete → the real long-tail queries people TYPE for a seed. gprop='yt'
    → YouTube-search demand (most relevant for a video factory). Returns [suggestion, ...] (best-effort)."""
    yt = gprop == "yt"
    url = ("https://suggestqueries.google.com/complete/search?"
           f"client={'youtube' if yt else 'firefox'}&ds={'yt' if yt else ''}"
           f"&hl={hl}&gl={gl}&q={urllib.parse.quote(seed)}")
    try:
        raw = _get(url).decode("utf-8", "ignore").strip()
        m = re.search(r"\((\[.*\])\)\s*;?\s*$", raw)      # YouTube client wraps JSONP: window.google.ac.h([...])
        data = json.loads(m.group(1) if m else raw)
        out = []
        for s in data[1]:                                 # firefox → "str"; youtube → ["query", 0, [...]]
            if isinstance(s, str):
                out.append(s)
            elif isinstance(s, (list, tuple)) and s and isinstance(s[0], str):
                out.append(s[0])
        return out
    except Exception:
        return []


def expand_keywords(seed, hl="vi", gl="vn", gprop="", breadth=6):
    """Fan a seed into real long-tail queries: base suggestions + a few 'seed <a..>' prefixes, deduped.
    Demand-driven topic/subtopic candidates grounded in what people actually search."""
    seen, out = set(), []
    for q in [seed] + [f"{seed} {c}" for c in "abcdgklmnst"[:breadth]]:
        for s in autocomplete(q, hl=hl, gl=gl, gprop=gprop):
            k = s.lower().strip()
            if k and k not in seen:
                seen.add(k); out.append(s)
    return out


def demand_topics(seed="SEO", geo="VN", n=12, gprop="yt", recency=True, days=30):
    """DEMAND-DRIVEN topic discovery — 'what should we make a video about?' grounded in real search demand,
    not guesswork. Merges keyless signals and keeps only on-domain candidates:
      • trends_vn()       → what Vietnam is searching RIGHT NOW (with a traffic band), filtered to our domain
      • expand_keywords() → the long-tail people TYPE for `seed` (gprop='yt' = YouTube-search demand)
      • recency_topics()  → what's HOT in the last `days` on keyless tech sources (HackerNews points, GitHub
                            stars, arXiv), engagement-ranked — the freshness axis a tech-NEWS factory lives on
                            (harvested clean-room from mvanhorn/last30days-skill, MIT).
    Returns a ranked, deduped list [{topic, source, signal}] (trending first — live traffic band; then hot
    recency; then long-tail). Best-effort — an empty list just means the network came back dry. Never raises."""
    out, seen = [], set()

    def _add(topic, source, signal=""):
        k = (topic or "").lower().strip()
        if k and k not in seen and len(k) > 2:
            seen.add(k); out.append({"topic": topic.strip(), "source": source, "signal": signal})

    # 1) live trends, on-domain only — match domain keywords as WHOLE WORDS on the query itself (NOT the
    # news URLs, where short tokens like "ai"/"seo" match spuriously inside "bai-viet"/"seoul"). Most daily
    # VN trends aren't SEO/marketing, so this is usually sparse — that's honest; the seed carries discovery.
    for t in trends_vn(geo=geo, n=max(n, 20)):
        if _domain_hit(t.get("query", "")):
            _add(t.get("query", ""), "trends", t.get("traffic", "") or "trending")

    # 2) long-tail search demand around the seed, on-domain only — a bare seed like "SEO" autocompletes to
    # "seoul"/"seok" (Korean names); the whole-word domain filter drops those, keeps "seo google", "seo là gì".
    # 2.5) fresh + high-engagement items from the last `days` (keyless tech sources). Ranks between live
    # trends and bare long-tail: these carry a real engagement signal (points/stars) and a recency window.
    if recency:
        for r in recency_topics(seed, days=days, n=n):
            _add(r["topic"], r["source"], r["signal"])

    # 3) long-tail search demand around the seed, on-domain only — a bare seed like "SEO" autocompletes to
    # "seoul"/"seok" (Korean names); the whole-word domain filter drops those, keeps "seo google", "seo là gì".
    for kw in expand_keywords(seed, gprop=gprop, breadth=6):
        if _domain_hit(kw):
            _add(kw, "yt" if gprop == "yt" else "autocomplete", "long-tail")

    return out[:n]


# ── Recency + engagement discovery (clean-room harvest of mvanhorn/last30days-skill, MIT) ──────────────
# The factory is a tech-NEWS factory: FRESHNESS is the whole point, yet trends_vn/expand_keywords are
# recency-blind. These add a "what broke in the last N days, ranked by real engagement" signal from KEYLESS
# tech sources — the same keyless-first discipline as the rest of researcher. Each is best-effort → [].
def _hn_recent(query, days, n=15):
    """HackerNews stories from the last `days` matching `query`, carrying points (engagement). Keyless (Algolia)."""
    cutoff = int(time.time()) - days * 86400
    url = (f"http://hn.algolia.com/api/v1/search?tags=story&query={urllib.parse.quote(query)}"
           f"&numericFilters=created_at_i>{cutoff}&hitsPerPage={n}")
    out = []
    try:
        for h in (json.loads(_get(url)).get("hits") or []):
            title = (h.get("title") or "").strip()
            if title:
                out.append({"title": title, "eng": int(h.get("points") or 0), "source": "hackernews"})
    except Exception:
        pass
    return out


def _github_recent(query, days, n=12):
    """GitHub repos PUSHED in the last `days` matching `query`, ranked by stars. Keyless search API (rate-limited)."""
    since = time.strftime("%Y-%m-%d", time.gmtime(time.time() - days * 86400))
    url = (f"https://api.github.com/search/repositories?q={urllib.parse.quote(query + ' pushed:>' + since)}"
           f"&sort=stars&order=desc&per_page={n}")
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            for it in (json.loads(r.read()).get("items") or []):
                desc = (it.get("description") or "").strip()
                title = (f"{it.get('full_name', '')}: {desc}" if desc else it.get("full_name", "")).strip(": ")
                if title:
                    out.append({"title": title, "eng": int(it.get("stargazers_count") or 0), "source": "github"})
    except Exception:
        pass
    return out


def _arxiv_recent(query, n=10):
    """Most-recent arXiv AI/ML/NLP papers matching `query` (submittedDate desc). Keyless Atom feed."""
    q = urllib.parse.quote(f"(cat:cs.AI OR cat:cs.CL OR cat:cs.LG) AND all:{query}")
    url = (f"http://export.arxiv.org/api/query?search_query={q}"
           f"&sortBy=submittedDate&sortOrder=descending&max_results={n}")
    out = []
    try:
        root = ET.fromstring(_get(url))
        ns = "{http://www.w3.org/2005/Atom}"
        for e in root.findall(f"{ns}entry"):
            t = e.find(f"{ns}title")
            if t is not None and t.text:
                out.append({"title": re.sub(r"\s+", " ", t.text).strip(), "eng": 0, "source": "arxiv"})
    except Exception:
        pass
    return out


def recency_topics(seed="AI", days=30, n=12):
    """What's HOT in the last `days` across keyless tech sources — fused, deduped, on-domain, engagement-ranked.
    Complements demand_topics' trend/long-tail with a RECENCY window (the freshness a tech-news factory needs).
    Returns [{topic, source, signal}]. Best-effort; never raises. (last30days-skill harvest, MIT clean-room.)"""
    seen = set()

    def _rank(items):                                 # engagement desc within a source, on-domain + deduped
        q = []
        for it in sorted(items, key=lambda x: x.get("eng", 0), reverse=True):
            title = it["title"]
            if not _on_domain({"title": title}):      # domain relevance gate (drops off-topic hot items)
                continue
            k = re.sub(r"[^a-z0-9 ]", "", title.lower())[:60]
            if not k or k in seen:
                continue
            seen.add(k); q.append(it)
        return q

    queues = [_rank(_hn_recent(seed, days)), _rank(_github_recent(seed, days)), _rank(_arxiv_recent(seed))]
    # round-robin merge so discussion (HN) + code (GitHub) + research (arXiv) are ALL represented, not just
    # whichever source has the biggest raw numbers.
    out, i = [], 0
    while len(out) < n and any(i < len(q) for q in queues):
        for q in queues:
            if i < len(q):
                it = q[i]
                sig = f"{it['source']}·{it['eng']}" if it["eng"] else it["source"]
                out.append({"topic": it["title"][:140], "source": it["source"], "signal": sig})
                if len(out) >= n:
                    break
        i += 1
    return out


def _firecrawl_text(url, max_chars=2000):
    """Cleaner article body via Firecrawl (main-content markdown) when FIRECRAWL_API_KEY is set.
    Returns '' if no key or on any failure — the caller falls back to the free fetch. Never raises."""
    key = os.environ.get("FIRECRAWL_API_KEY", "")
    if not key:
        return ""
    try:
        body = json.dumps({"url": url, "formats": ["markdown"], "onlyMainContent": True}).encode()
        req = urllib.request.Request("https://api.firecrawl.dev/v1/scrape", data=body,
                                     headers={"Authorization": f"Bearer {key}",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT * 2) as r:
            j = json.loads(r.read())
        md = ((j.get("data") or {}).get("markdown")) or ""
        return re.sub(r"\s+", " ", md).strip()[:max_chars]
    except Exception:
        return ""


def _article_text(url, max_chars=2000):
    """Clean text of one article. Firecrawl (main-content, if key present) → markitdown → strip.
    Best-effort with short timeouts; never raises so research can't hang or crash a render."""
    fc = _firecrawl_text(url, max_chars)                   # cleaner main-content when key is present
    if fc and len(fc) > 120:
        return fc
    try:
        raw = _get(url)
        try:
            from markitdown import MarkItDown
            import io
            txt = MarkItDown().convert_stream(io.BytesIO(raw), file_extension=".html").text_content
        except Exception:
            txt = _strip_html(raw.decode("utf-8", "ignore"))
        return re.sub(r"\s+", " ", txt).strip()[:max_chars]
    except Exception:
        return ""


# domain keywords — keep SEO/AI/marketing items, drop off-topic RSS noise (bóng đá, điểm chuẩn…)
_DOMAIN = ("seo", "google", "website", "marketing", "digital", "content", "ai", "trí tuệ nhân tạo",
           "thuật toán", "search", "traffic", "từ khoá", "từ khóa", "backlink", "thứ hạng", "ranking",
           "chuyển đổi", "quảng cáo", "thương hiệu", "social", "tiktok", "youtube", "chatgpt", "llm")


def _on_domain(item):
    # Reuse the careful whole-word + weak-token-corroboration matcher (_domain_hit), NOT a naive substring
    # test: a plain `"ai" in blob` false-matches "email"/"domain"/"campaign"/"training"/"maintain",
    # "search" matches "researcher", "seo" matches "seoul" — which polluted the research/hot-topic pool with
    # off-domain items (the #1 off-topic-drift risk). One matcher, one behaviour (also de-dups the logic).
    blob = item.get("title", "") + " " + item.get("snippet", "") + " " + item.get("source", "")
    return _domain_hit(blob)


# Whole-word domain matcher — for short free-text candidates (trend queries, autocomplete) where a plain
# substring test yields false hits ("seo" inside "seoul", "ai" inside a URL's "bai-viet"). \w boundaries
# handle Vietnamese diacritics (they count as word chars), so "seo google" hits but "seoul" doesn't.
#
# But whole-word "seo"/"ai" are STILL ambiguous: "seo" is a common Korean surname (→ "seo seung-jae", an
# athlete) and "ai" appears in names too. So these WEAK tokens only count WITH corroboration — a specific
# domain term, a Vietnamese-diacritic word (this is a VN factory), or a year — else they're rejected.
_WEAK = {"seo", "ai", "search"}
_STRONG = tuple(k for k in _DOMAIN if k not in _WEAK)
_STRONG_RE = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(k) for k in _STRONG) + r")(?!\w)", re.IGNORECASE)
_WEAK_RE = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(k) for k in _WEAK) + r")(?!\w)", re.IGNORECASE)
_VN_DIACRITIC_RE = re.compile(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", re.I)
_YEAR_RE = re.compile(r"(?<!\d)(?:19|20)\d\d(?!\d)")


# "ai" is uniquely treacherous: besides tech-AI it is also VN "who" AND part of "Ai Cập" (Egypt), so a VN
# diacritic — which EVERY Vietnamese phrase has — does NOT prove the AI topic ("úc vs ai cập" = Australia
# vs Egypt football leaked through as on-domain). A weak-"ai"-ONLY match therefore needs a real AI/tech
# CONTEXT term (tight list, clearly-AI) instead of a bare diacritic. "seo"/"search" keep diacritic/year
# corroboration — they are NOT common Vietnamese words, so the collision doesn't apply to them.
_AI_CTX_RE = re.compile(
    r"(?<!\w)(?:chatgpt|gpt|chatbot|generative|nhân tạo|trí tuệ|tạo sinh|machine learning|deep learning|"
    r"llm|mô hình ngôn ngữ|prompt|midjourney|gemini|copilot|tự động hoá|tự động hóa)(?!\w)", re.IGNORECASE)


def _domain_hit(text):
    t = text or ""
    if _STRONG_RE.search(t):                      # a specific, unambiguous domain term → on-domain
        return True
    m = _WEAK_RE.findall(t)                        # "seo"/"ai"/"search" alone → needs corroboration
    if m:
        if {x.lower() for x in m} == {"ai"}:      # ONLY "ai" matched → ambiguous (who / Ai Cập) → need AI context
            return bool(_AI_CTX_RE.search(t))
        return bool(_VN_DIACRITIC_RE.search(t) or _YEAR_RE.search(t))
    return False


_URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def _first_url(text):
    m = _URL_RE.search(text or "")
    return m.group(0).rstrip(".,)") if m else ""


# Generic domain + VN function words that don't distinguish a TOPIC — an item matching only these is merely
# on-domain, not on-topic. Used to RANK research items by topic relevance so a narrow query ("tốc độ tải")
# prefers on-topic articles over generic SEO noise (courses, software lists, algorithm news).
_TOPIC_STOP = set((
    "seo google marketing website web digital content ai search top cách để và của trong cho các một "
    "những khi nếu là hay với từ khoá khóa lên online tốt nhất mới miễn phí 2023 2024 2025 2026 2027"
).split())


def _topic_words(topic):
    return [w for w in re.findall(r"[\wÀ-ỹ]+", (topic or "").lower())
            if len(w) >= 2 and w not in _TOPIC_STOP]


def _topic_relevance(item, tws):
    blob = (item.get("title", "") + " " + item.get("snippet", "")).lower()
    return sum(1 for w in tws if w in blob)


def pagespeed_facts(url, strategy="mobile"):
    """REAL Core Web Vitals for a specific URL via PageSpeed Insights (free; PAGESPEED_API_KEY optional
    but raises the quota). Returns a Vietnamese fact line with hard numbers to ground an SEO/performance
    video — or '' on any failure. These are genuine measured numbers, so the traceability gate passes."""
    if not url:
        return ""
    api = ("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url="
           + urllib.parse.quote(url, safe="") + f"&strategy={strategy}&category=performance")
    key = os.environ.get("PAGESPEED_API_KEY", "")
    if key:
        api += "&key=" + key
    try:
        j = json.loads(_get(api, timeout=_TIMEOUT * 3))
        lh = j.get("lighthouseResult", {}) or {}
        score = int(round((lh.get("categories", {}).get("performance", {}).get("score", 0) or 0) * 100))
        au = lh.get("audits", {}) or {}
        def disp(k):
            return (au.get(k, {}) or {}).get("displayValue", "").strip()
        lcp, cls, fcp, tbt = disp("largest-contentful-paint"), disp("cumulative-layout-shift"), \
            disp("first-contentful-paint"), disp("total-blocking-time")
        bits = [f"điểm hiệu năng {score}/100" if score else ""]
        if lcp: bits.append(f"LCP {lcp}")
        if fcp: bits.append(f"FCP {fcp}")
        if cls: bits.append(f"CLS {cls}")
        if tbt: bits.append(f"TBT {tbt}")
        bits = [b for b in bits if b]
        return f"Chỉ số tốc độ ({strategy}) của {url}: " + ", ".join(bits) + "." if bits else ""
    except Exception:
        return ""


def web_search(query, n=8, region="vn-vi"):
    """Keyless WEB search (DuckDuckGo HTML via POST) → EVERGREEN how-to/guide results, unlike news_rss's
    recent-news bias (which drifts niche how-to topics off-subject — see the flagged research-source issue).
    POST bypasses DDG's GET anti-bot ('anomaly' page); DDG ad redirects (y.js/ad_domain) are skipped.
    Returns [{title, link, snippet, source}]; [] on failure. Best-effort, never raises."""
    try:
        data = urllib.parse.urlencode({"q": query, "kl": region}).encode()
        req = urllib.request.Request("https://html.duckduckgo.com/html/", data=data,
                                     headers={"User-Agent": _UA_BROWSER,
                                              "Content-Type": "application/x-www-form-urlencoded"})
        page = urllib.request.urlopen(req, timeout=_TIMEOUT * 2).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"[researcher] web search failed ({e})")
        return []
    if "anomaly" in page.lower():
        return []
    out = []
    for b in re.split(r'class="result__a"', page)[1:]:
        m = re.match(r'[^>]*href="([^"]+)"[^>]*>(.*?)</a>', b, re.S)
        if not m:
            continue
        link = html.unescape(m.group(1))
        if "y.js" in link or "ad_domain" in link:          # DDG paid-ad redirect → skip
            continue
        title = _strip_html(m.group(2))
        sm = re.search(r'result__snippet[^>]*>(.*?)</a>', b, re.S)
        snippet = _strip_html(sm.group(1)) if sm else ""
        if title:
            out.append({"title": title, "link": link, "snippet": snippet,
                        "source": urllib.parse.urlparse(link).netloc.replace("www.", "")})
        if len(out) >= n:
            break
    return out


def _semantic_filter(topic, items):
    """LLM gate: keep only items whose title/snippet ACTUALLY address the topic's INTENT, not just share a
    word — word-overlap can't tell 'cà phê Kinh' (a coffee-brand story) from 'local SEO for cafés'. Returns
    the on-intent items; [] if the LLM judges NONE relevant (→ the caller writes an on-topic-GENERIC script
    instead of an off-topic-specific one, which is the whole point). Best-effort: any failure / no real LLM
    → items UNCHANGED (never blocks research). Disable with SEOSONA_SEMANTIC_RESEARCH=0.

    Runs even on a SINGLE item: a lone off-intent article is the WORST case (it becomes the sole grounding
    for the whole video — this is exactly how the 'cà phê Kinh' brand story slipped through), so it must be
    validated, not waved past. Only an EMPTY list skips the gate."""
    if os.environ.get("SEOSONA_SEMANTIC_RESEARCH", "1") == "0" or not items:
        return items
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(__file__))
        llm = __import__("llm_engine")
        listing = "\n".join(f"{i}. {it.get('title', '')} — {(it.get('snippet') or '')[:90]}"
                            for i, it in enumerate(items))
        sysp = ("Bạn lọc bài viết theo Ý ĐỊNH của chủ đề. CHỈ giữ bài THỰC SỰ nói về chủ đề đó; BỎ bài chỉ "
                "trùng từ khoá nhưng khác ý định (vd chủ đề 'SEO local cho quán cà phê' thì BỎ bài kể chuyện "
                "một thương hiệu cà phê, vì nó không dạy SEO local). Trả JSON {\"keep\":[chỉ số các bài liên quan]}.")
        userp = f"CHỦ ĐỀ: {topic}\n\nDANH SÁCH BÀI:\n{listing}\n\nTrả DUY NHẤT {{\"keep\":[...]}}."
        out = llm.generate_json_strict(sysp, userp, require_key="keep")
        if isinstance(out, dict) and isinstance(out.get("keep"), list):
            idxs = [int(i) for i in out["keep"] if isinstance(i, (int, float)) and 0 <= int(i) < len(items)]
            kept = [items[i] for i in idxs]
            print(f"[researcher] semantic gate: kept {len(kept)}/{len(items)} on-topic")
            return kept                                   # may be [] → topic treated as unsourced (on-topic-generic)
    except Exception as e:
        print(f"[researcher] semantic gate skipped ({e})")
    return items


def _firecrawl_search(query, n=8, lang="vi", country="vn"):
    """Keyed web SEARCH (real, evergreen GUIDES — not news) via Firecrawl, when FIRECRAWL_API_KEY is set.
    Returns items in the SAME shape as news_rss() [{title, link, source, date, snippet}] so the rest of
    the pipeline is source-agnostic; [] if no key or on any failure — the caller falls back to News RSS.
    Never raises. This is the fix for evergreen how-to topics, where News RSS returns generic marketing
    news (a coffee brand's PR, trend predictions) instead of topic-specific content."""
    key = os.environ.get("FIRECRAWL_API_KEY", "")
    if not key:
        return []
    try:
        body = json.dumps({"query": query, "limit": n, "lang": lang, "country": country}).encode()
        req = urllib.request.Request("https://api.firecrawl.dev/v1/search", data=body,
                                     headers={"Authorization": f"Bearer {key}",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT * 2) as r:
            j = json.loads(r.read())
        out = []
        for d in (j.get("data") or [])[:n]:
            link = (d.get("url") or "").strip()
            src = urllib.parse.urlsplit(link).netloc.replace("www.", "")
            out.append({"title": _strip_html(d.get("title", "")), "link": link, "source": src,
                        "date": "", "snippet": _strip_html(d.get("description") or d.get("snippet") or "")})
        return [it for it in out if it["title"]]
    except Exception as e:
        print(f"[researcher] firecrawl search failed ({e})")
        return []


# Route by topic TYPE. Evergreen how-to/definition topics ("cách tối ưu…", "SEO local cho quán…") get
# generic recent NEWS from Google News RSS — the wrong-subject risk. Send those to web SEARCH (real guides).
# Time-bound topics (a year, or explicit news/trend words) genuinely want News RSS, so keep them there.
_NEWS_MARKERS = ("tin tức", "mới nhất", "cập nhật", "ra mắt", "sự kiện", "xu hướng", "vừa ", "hôm nay")


def _is_evergreen(topic):
    t = (topic or "").lower()
    if _YEAR_RE.search(t):                                   # a year → time-bound → News RSS is right
        return False
    return not any(m in t for m in _NEWS_MARKERS)


def research(topic, max_items=6, fetch_bodies=2, domain_hint="SEO marketing website Google digital"):
    """Topic → {raw_text, sources, items}. Runs the topic AND a domain-qualified variant, keeps only
    on-domain items (drops off-topic noise). raw_text = titles + snippets (+ a few article bodies) —
    the REAL corpus the script must be grounded in. Empty → caller treats the topic as unsourced.

    ROUTED by topic type: evergreen how-to topics ground on web SEARCH (Firecrawl → real guides); news/
    time-bound topics ground on Google News RSS. Web search falls back to News RSS if it's empty/keyless."""
    seen, items = set(), []

    def _gather(fetcher):
        for q in (topic, f"{topic} {domain_hint}".strip()):  # raw + disambiguated query
            for it in fetcher(q, max_items + 4):             # over-fetch so the relevance rank has candidates
                k = it.get("title", "")[:60]
                if k and k not in seen and _on_domain(it):
                    seen.add(k); items.append(it)

    if _is_evergreen(topic):                                 # evergreen → real how-to guides via web SEARCH
        _gather(lambda q, n: _firecrawl_search(q, n=n))      # cleaner bodies IF FIRECRAWL_API_KEY is set
        if not items:                                        # no key / dry → KEYLESS DDG web search (works, verified)
            _gather(lambda q, n: web_search(q, n=n))
    if not items:                                            # news topic, OR web search dry → Google News RSS
        _gather(lambda q, n: news_rss(q, n=n))
    # RANK by TOPIC relevance (title/snippet overlap with the topic's distinctive words), not just domain,
    # so a narrow query grounds on ON-TOPIC articles. On-domain FLOOR: if nothing is topic-relevant, keep
    # the generic items (better a loosely-grounded script than an unsourced one).
    tws = _topic_words(topic)
    if tws:
        items.sort(key=lambda it: _topic_relevance(it, tws), reverse=True)
        items = [it for it in items if _topic_relevance(it, tws) > 0] or items
    items = items[:max_items]
    items = _semantic_filter(topic, items)               # LLM gate: drop shared-word-but-off-intent articles
    if not items:
        return {"raw_text": "", "sources": [], "items": []}
    parts, sources = [], []
    for it in items:
        line = it["title"] + (". " + it["snippet"] if it["snippet"] else "")
        parts.append(line)
        if it["link"]:
            sources.append(it["link"])
    for it in items[:fetch_bodies]:                       # deepen with a few full bodies (best-effort)
        if it["link"]:
            body = _article_text(it["link"])
            if body and len(body) > 120:
                parts.append(body)
    # If the topic names a specific site, attach its REAL Core Web Vitals as hard, citable numbers.
    _url = _first_url(topic)
    if _url:
        ps = pagespeed_facts(_url)
        if ps:
            parts.append(ps)
            sources.append("PageSpeed Insights: " + _url)
    return {"raw_text": "\n".join(parts), "sources": sources, "items": items}


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) > 1 and sys.argv[1] == "--discover":
        seed = sys.argv[2] if len(sys.argv) > 2 else "SEO"
        cands = demand_topics(seed=seed)
        print(f"demand topics (seed: {seed}) — {len(cands)} candidate(s):")
        for c in cands:
            print(f"  • [{c['source']:>10}] {c['topic']}  ({c['signal']})")
        sys.exit(0)
    t = sys.argv[1] if len(sys.argv) > 1 else "SEO 2026 ở TP.HCM"
    r = research(t, max_items=6, fetch_bodies=1)
    print(f"topic: {t}\n  sources: {len(r['sources'])} | raw_text: {len(r['raw_text'])} chars")
    for it in r["items"][:5]:
        print(f"  • {it['title']}  [{it['source']}]")
