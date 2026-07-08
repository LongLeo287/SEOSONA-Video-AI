# -*- coding: utf-8 -*-
"""Analytics Feedback Agent — Performance Ingest (OBSERVE stage).

Pulls real-world metrics (views, CTR, retention, likes) for PUBLISHED videos and
merges them into each video's production_manifest.json `performance` block, which
closes the factory loop (manifest variant ↔ market response → factory_ledger learns).

Graceful by design — this is the one stage that needs external credentials:
  • With creds (YouTube Data/Analytics API, etc.) → fetch real metrics.
  • Without creds → honest no-op that says exactly what's missing (never fakes data).
  • Manual mode (`--inject file.json`) lets you feed metrics by hand to test the loop
    end-to-end before any API is wired:  {"<video_id>": {"views":..., "ctr":..., "retention":...}}

See "OBSERVE" + §9 (open decisions) in 6_SOP/AUTONOMOUS_FACTORY_LOOP.md.
"""
import os, sys, json, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import production_manifest as pm


def _published_map(workspace_dir=None):
    """video_id -> {platform: platform_video_id} from each project's publish_report.json."""
    workspace_dir = workspace_dir or os.path.join(ROOT, "8_WORKSPACE")
    out = {}
    for rep in glob.glob(os.path.join(workspace_dir, "**", "publish_report.json"), recursive=True):
        try:
            data = json.load(open(rep, encoding="utf-8"))
            vid = os.path.basename(os.path.dirname(rep))
            out[vid] = data
        except Exception:
            pass
    return out


def _youtube_metrics(yt_video_id):
    """Fetch YouTube metrics if credentials are configured; else None (no fake data)."""
    cred = os.path.join(ROOT, "1_CONFIG", "credentials", "youtube.json")
    if not os.path.exists(cred):
        return None
    try:
        # Real implementation goes here once OAuth is set up (YouTube Analytics API:
        # views, estimatedMinutesWatched, averageViewPercentage, cardClickRate).
        # Kept as an explicit integration point — no guessing.
        from googleapiclient.discovery import build  # noqa: F401
        return None  # TODO: wire YouTube Analytics query with the stored OAuth token
    except Exception:
        return None


def ingest(workspace_dir=None, inject=None):
    """Merge available metrics into manifests. Returns a summary dict."""
    workspace_dir = workspace_dir or os.path.join(ROOT, "8_WORKSPACE")
    manifests = pm.scan(workspace_dir)
    # skip a manifest that lacks video_id rather than KeyError-crash the whole OBSERVE stage on one bad file
    by_id = {vid: m for m in manifests if (vid := m.get("video_id"))}
    updated, skipped = [], []

    if inject:  # manual metrics for testing the loop without live APIs
        data = json.load(open(inject, encoding="utf-8")) if isinstance(inject, str) else inject
        for vid, metrics in data.items():
            m = by_id.get(vid)
            if m:
                pm.set_performance(m["project_dir"], metrics)
                updated.append(vid)
            else:
                skipped.append(vid)
        return {"mode": "inject", "updated": updated, "skipped": skipped}

    published = _published_map(workspace_dir)
    if not published:
        print("[perf-ingest] no publish_report.json found — nothing published yet "
              "(publishing is Phase 4; OBSERVE activates once videos are live).")
    have_creds = os.path.exists(os.path.join(ROOT, "1_CONFIG", "credentials", "youtube.json"))
    if not have_creds:
        print("[perf-ingest] no analytics credentials (1_CONFIG/credentials/youtube.json). "
              "Skipping live fetch — use --inject <file.json> to test the loop, or add creds. "
              "(See §9 in AUTONOMOUS_FACTORY_LOOP.md.)")
        return {"mode": "noop", "reason": "no-credentials", "published": len(published)}

    for vid, rep in published.items():
        yt = (rep.get("youtube") or {}).get("video_id")
        metrics = _youtube_metrics(yt) if yt else None
        if metrics and by_id.get(vid):
            pm.set_performance(by_id[vid]["project_dir"], metrics)
            updated.append(vid)
        else:
            skipped.append(vid)
    return {"mode": "live", "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Ingest real-world performance into manifests")
    ap.add_argument("--inject", help="JSON file {video_id: {views,ctr,retention,...}} for manual testing")
    a = ap.parse_args()
    print(json.dumps(ingest(inject=a.inject), ensure_ascii=False, indent=2))
