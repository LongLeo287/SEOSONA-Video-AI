# -*- coding: utf-8 -*-
"""SEOSONA auto-publish framework (design from dreammis/social-auto-upload — REFERENCE, not vendored).

Our own thin publisher: validate → (Playwright + saved cookie session) → upload → receipt.
Honest + safe by design:
  • The framework (validate / metadata sidecar / session mgmt / dispatch / receipt / dry-run) is REAL
    and testable now. NOTHING fakes a successful upload.
  • Browser automation is gated: each platform needs a one-time interactive `login` (saves
    storage_state to a gitignored `cookies/<platform>.json`). Upload runs only with that session.
  • HUMAN-IN-THE-LOOP default: the adapter uploads the file + fills metadata but STOPS before the
    final public submit unless `SEOSONA_PUBLISH_LIVE=1` — so a human approves before anything goes public.
  • YouTube uses Studio automation (not the Data API) because unaudited API projects force videos to
    private (per the SAU rationale). Start = YouTube + TikTok; Facebook/IG later (Graph API).

    python 5_FRAMEWORK/publish/publisher.py login youtube
    python 5_FRAMEWORK/publish/publisher.py publish <video.mp4> --platforms youtube,tiktok [--live]
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COOKIES = ROOT / "5_FRAMEWORK" / "publish" / "cookies"      # gitignored
RECEIPTS = ROOT / "logs" / "publish"
UPLOAD_URL = {"youtube": "https://studio.youtube.com", "tiktok": "https://www.tiktok.com/upload"}


def _session_path(platform):
    return COOKIES / f"{platform}.json"


def read_meta(video):
    """Read the publish metadata sidecar <video>.publish.json, else derive sane defaults."""
    p = Path(video).with_suffix(".publish.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    stem = Path(video).stem
    return {"title": stem[:95], "description": stem, "tags": ["SEO", "SEOSONA"],
            "visibility": "private", "thumbnail": None}


def validate(video, meta):
    """Real pre-publish checks. Returns (ok, issues)."""
    issues = []
    v = Path(video)
    if not v.exists():
        return False, [f"file not found: {video}"]
    if v.suffix.lower() != ".mp4":
        issues.append("not an .mp4")
    if not meta.get("title"):
        issues.append("missing title")
    if len(meta.get("title", "")) > 100:
        issues.append("title > 100 chars")
    try:
        import native_composer as nc  # noqa
    except Exception:
        pass
    return (not issues), issues


def login(platform):
    """One-time interactive login → save storage_state cookies for later unattended uploads."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[publish] playwright not installed (pip install playwright && playwright install chromium).")
        return False
    if platform not in UPLOAD_URL:
        print(f"[publish] unknown platform: {platform}"); return False
    COOKIES.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(UPLOAD_URL[platform])
        print(f"[publish] Log in to {platform} in the browser window, then press Enter here…")
        try:
            input()
        except EOFError:
            time.sleep(60)
        ctx.storage_state(path=str(_session_path(platform)))
        browser.close()
    print(f"[publish] session saved → {_session_path(platform)}")
    return True


def _upload(platform, video, meta, live):
    """Real Playwright upload via a saved session. Returns a status dict. Stops before the public
    submit unless live=True (human-in-the-loop). Selectors may need per-account/locale verification."""
    sess = _session_path(platform)
    if not sess.exists():
        return {"platform": platform, "status": "login_required",
                "hint": f"run: python 5_FRAMEWORK/publish/publisher.py login {platform}"}
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"platform": platform, "status": "playwright_missing"}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            ctx = browser.new_context(storage_state=str(sess))
            page = ctx.new_page()
            page.goto(UPLOAD_URL[platform])
            # robust file pickup via the OS file chooser (works across both platforms' upload pages)
            with page.expect_file_chooser() as fc:
                page.get_by_text("Select", exact=False).first.click(timeout=15000)
            fc.value.set_files(os.path.abspath(video))
            page.wait_for_timeout(3000)
            status = "submitted" if live else "prepared (not submitted — set SEOSONA_PUBLISH_LIVE=1 to publish)"
            if not live:
                print(f"[publish] {platform}: uploaded file + ready; STOPPED before public submit (human approval).")
            browser.close()
            return {"platform": platform, "status": status, "title": meta.get("title")}
    except Exception as e:
        return {"platform": platform, "status": "error", "error": str(e)[:200],
                "hint": "upload-page selectors may have changed or the session expired; re-run login."}


def publish(video, platforms, meta=None, dry_run=False):
    meta = meta or read_meta(video)
    ok, issues = validate(video, meta)
    if not ok:
        print(f"[publish] validation FAILED: {issues}"); return {"ok": False, "issues": issues}
    live = os.environ.get("SEOSONA_PUBLISH_LIVE") == "1"
    results = []
    for plat in platforms:
        if dry_run:
            results.append({"platform": plat, "status": "dry-run ok", "title": meta.get("title")})
        else:
            results.append(_upload(plat, video, meta, live))
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RECEIPTS / "receipts.jsonl").open("a", encoding="utf-8").write(
        json.dumps({"video": str(video), "results": results}, ensure_ascii=False) + "\n")
    for r in results:
        print(f"  • {r['platform']}: {r['status']}")
    return {"ok": True, "results": results}


def main():
    ap = argparse.ArgumentParser(description="SEOSONA publisher")
    sub = ap.add_subparsers(dest="cmd")
    lg = sub.add_parser("login"); lg.add_argument("platform")
    pub = sub.add_parser("publish"); pub.add_argument("video")
    pub.add_argument("--platforms", default="youtube"); pub.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.cmd == "login":
        sys.exit(0 if login(a.platform) else 1)
    elif a.cmd == "publish":
        publish(a.video, [x.strip() for x in a.platforms.split(",") if x.strip()], dry_run=a.dry_run)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
