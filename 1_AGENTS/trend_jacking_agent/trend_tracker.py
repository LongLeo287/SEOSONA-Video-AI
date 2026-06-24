"""
Trend Jacking — autonomous trend → news-video trigger.

Fetches the latest SEO/tech trend from an RSS feed and (optionally) kicks the news
pipeline for it. Use as a cron entry, programmatically, or via the Telegram /trend
command.

    from trend_jacking_agent.trend_tracker import fetch_latest_trend, trigger_pipeline
    topic = fetch_latest_trend()
    trigger_pipeline(topic, dry_run=True)
"""
import os
import sys
import xml.etree.ElementTree as ET
import urllib.request
import subprocess

FEED_URL = os.environ.get("SEOSONA_TREND_FEED", "https://searchengineland.com/feed")
_FALLBACK = "Google Update thuật toán cốt lõi mới nhất"


def fetch_latest_trend(feed_url=None):
    """Return the title of the latest item in the RSS feed (or a fallback)."""
    url = feed_url or FEED_URL
    print(f"[Trend Tracker] Fetching latest trend from {url} …")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            root = ET.fromstring(response.read())
        for item in root.findall(".//item"):
            title_el = item.find("title")
            if title_el is not None and title_el.text:
                print(f"[Trend Tracker] Hot trend: {title_el.text}")
                return title_el.text.strip()
    except Exception as e:
        print(f"[Trend Tracker] RSS fetch failed: {e}")
    return _FALLBACK


def trigger_pipeline(trend_topic, dry_run=False):
    """Kick the news pipeline for a topic. dry_run prints the command instead."""
    print("\n" + "=" * 50)
    print(f"🔥 AUTO-TREND PIPELINE: {trend_topic}")
    print("=" * 50 + "\n")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    router_script = os.path.join(root_dir, "scripts", "workflow_video_news.py")
    if dry_run:
        print(f"[Dry Run] Would execute: python {router_script} \"{trend_topic}\"")
        return {"ok": True, "dry_run": True, "topic": trend_topic}
    proc = subprocess.run([sys.executable, router_script, trend_topic], cwd=root_dir)
    return {"ok": proc.returncode == 0, "topic": trend_topic, "returncode": proc.returncode}


def run(dry_run=False):
    """Fetch the latest trend and trigger the pipeline for it."""
    return trigger_pipeline(fetch_latest_trend(), dry_run=dry_run)


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
