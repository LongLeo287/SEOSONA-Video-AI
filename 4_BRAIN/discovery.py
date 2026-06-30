# -*- coding: utf-8 -*-
"""SEOSONA Video — Discovery (Loop Engineering move #2).

The fix for the "blind loop": the loop should identify its own work, not have a human
hand-pick each item. Discovery reads a maintained source list, drops anything already
done (the processed-ledger) or already queued, and appends the NEW items to the
production queue — so a scheduled run picks up fresh work by itself.

Source = `0_INPUT_INBOX/sources.txt` (one per line; GitHub URL or a Vietnamese topic;
`#` lines ignored). Free/local; no network needed for the source list itself.

  python 4_BRAIN/discovery.py            # discover + enqueue new items
  python 4_BRAIN/discovery.py --dry-run  # show what would be added, change nothing

Called at the start of scripts/daily_production.py so each batch self-discovers.
"""
import os
import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[discovery] PyYAML required")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "0_INPUT_INBOX"
SOURCES = INBOX / "sources.txt"
FEEDS = INBOX / "feeds.txt"
QUEUE = INBOX / "production_queue.yaml"
LEDGER = INBOX / ".processed_ledger.txt"
CATEGORY = "news_videos"     # discovered items become news videos

# Relevance filter for auto-fetched feed items (SEOSONA domain = SEO / AI / marketing).
DOMAIN_KW = ["seo", "ai ", " ai", "search", "google", "marketing", "content", "llm",
             "gpt", "gemini", "claude", "agent", "rag", "prompt", "chatgpt", "ranking",
             "tìm kiếm", "nội dung", "từ khoá", "thương hiệu", "trí tuệ", "công nghệ",
             "chuyển đổi số", "quảng cáo", "website", "tiếp thị"]
# Hard cap on items enqueued per run (circuit-breaker mindset for an unattended feed).
MAX_NEW = int(os.environ.get("SEOSONA_DISCOVERY_MAX", "10"))
FEED_TOP = int(os.environ.get("SEOSONA_FEED_TOP", "5"))   # items pulled per feed


def _ledger():
    if not LEDGER.exists():
        return set()
    return set(x.strip() for x in LEDGER.read_text(encoding="utf-8").splitlines() if x.strip())


def _read_sources():
    if not SOURCES.exists():
        return []
    out = []
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def _read_feeds():
    if not FEEDS.exists():
        return []
    return [s.strip() for s in FEEDS.read_text(encoding="utf-8").splitlines()
            if s.strip() and not s.strip().startswith("#")]


# Reject obvious off-topic — esp. the football coach "Park Hang-seo" who collides with "seo".
EXCLUDE_KW = ["hang seo", "hang-seo", "park hang", "bóng đá", "world cup", "tuyển hàn",
              "hlv", "cầu thủ", "thể thao", "bàn thắng", "ngoại hạng"]


def _relevant(title):
    t = (title or "").lower()
    if any(x in t for x in EXCLUDE_KW):
        return False
    return any(k in t for k in DOMAIN_KW)


def _fetch_feed(url, top=FEED_TOP):
    """Fetch one RSS/Atom feed → [(title, link)]. Native (requests + xml), no extra dep.
    Best-effort: a dead/slow feed returns [] instead of raising (unattended-safe)."""
    import xml.etree.ElementTree as ET
    try:
        import requests
        r = requests.get(url, timeout=15, headers={"User-Agent": "SEOSONA-discovery/1.0"})
        root = ET.fromstring(r.content)
    except Exception as e:
        print(f"[discovery] feed failed: {url} ({type(e).__name__})")
        return []
    items = []
    for el in root.iter():
        tag = el.tag.split("}")[-1].lower()
        if tag not in ("item", "entry"):
            continue
        title, link = None, None
        for ch in el:
            ct = ch.tag.split("}")[-1].lower()
            if ct == "title" and ch.text:
                title = ch.text.strip()
            elif ct == "link":
                link = (ch.text or "").strip() or ch.attrib.get("href")
        if title:
            items.append((title, link or title))
        if len(items) >= top:
            break
    return items


def _fetch_all_feeds():
    """All feeds → list of candidate queue items (the link/URL), filtered for relevance."""
    feeds = _read_feeds()
    if not feeds:
        return []
    cand = []
    for url in feeds:
        for title, link in _fetch_feed(url):
            if _relevant(title):
                cand.append(link)
                print(f"  ~ {title[:60]}")
            else:
                print(f"  · (off-topic) {title[:50]}")
    return cand


def _fetch_github_trending(days=None, per_topic=None):
    """Autonomous trending-repo discovery (pattern adopted from mvanhorn/last30days, MIT:
    entity-resolution → targeted multi-source recency ranking). Applied to OUR domain: SEOSONA
    makes tech-news ABOUT trending GitHub repos, so query GitHub per-topic for repos created in
    the last N days, sorted by stars → feed the queue. No static list needed. Uses the `gh` CLI
    (already a dependency). Best-effort: no gh / offline / rate-limit → [] (unattended-safe).
    Toggle off with SEOSONA_TREND=0; tune via SEOSONA_TREND_TOPICS / _DAYS / _PER."""
    if os.environ.get("SEOSONA_TREND", "1") == "0":
        return []
    import subprocess, json, datetime
    days = days or int(os.environ.get("SEOSONA_TREND_DAYS", "30"))
    per_topic = per_topic or int(os.environ.get("SEOSONA_TREND_PER", "3"))
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    min_stars = os.environ.get("SEOSONA_TREND_STARS", "150")
    topics = [t.strip() for t in os.environ.get(
        "SEOSONA_TREND_TOPICS", "ai-agent,llm,rag,mcp,text-to-video,agentic-ai").split(",") if t.strip()]
    out, seen = [], set()
    for tp in topics:
        q = f"topic:{tp} created:>{since} stars:>{min_stars}"
        try:
            r = subprocess.run(
                ["gh", "api", "-X", "GET", "search/repositories",
                 "-f", f"q={q}", "-f", "sort=stars", "-f", "order=desc", "-f", f"per_page={per_topic}"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
            data = json.loads(r.stdout or "{}")
        except Exception as e:
            print(f"[discovery] trending '{tp}' failed ({type(e).__name__})")
            continue
        for it in (data.get("items") or [])[:per_topic]:
            url, full, stars = it.get("html_url"), it.get("full_name", ""), it.get("stargazers_count", 0)
            if url and url not in seen and "longleo" not in full.lower() and "seosona" not in full.lower():
                seen.add(url)
                out.append(url)
                print(f"  ★ trending {full} ({stars}★ · topic:{tp})")
    return out


def discover(dry_run=False):
    # Static sources (curated) + RSS feeds + AUTONOMOUS GitHub-trending discovery.
    sources = _read_sources() + _fetch_all_feeds() + _fetch_github_trending()
    if not sources:
        print(f"[discovery] no sources/feeds — nothing to discover.")
        return []
    if not QUEUE.exists():
        print(f"[discovery] queue file missing: {QUEUE}")
        return []
    queue = yaml.safe_load(QUEUE.read_text(encoding="utf-8")) or {}
    current = [str(i).strip() for i in (queue.get(CATEGORY) or []) if str(i).strip()]
    ledger = _ledger()

    added, skipped, seen = [], [], set()
    for s in sources:
        if s in seen:
            continue                                  # de-dup within this run
        seen.add(s)
        if f"{CATEGORY}::{s}" in ledger:
            skipped.append((s, "already done"))
        elif s in current:
            skipped.append((s, "already queued"))
        elif len(added) >= MAX_NEW:
            skipped.append((s, f"over per-run cap ({MAX_NEW})"))   # bounded, unattended-safe
        else:
            added.append(s)

    print(f"[discovery] {len(seen)} candidates · {len(added)} new (cap {MAX_NEW}) · {len(skipped)} skipped")
    for s in added:
        print(f"  + {s}")
    if added and not dry_run:
        placeholders = [i for i in (queue.get(CATEGORY) or []) if not str(i).strip()]
        queue[CATEGORY] = current + added + placeholders   # keep template placeholders last
        tmp = QUEUE.with_suffix(".yaml.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(queue, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp, QUEUE)
        print(f"[discovery] enqueued {len(added)} item(s) → {QUEUE.name}")
    elif dry_run:
        print("[discovery] dry-run — queue not modified")
    return added


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    discover(dry_run=a.dry_run)
