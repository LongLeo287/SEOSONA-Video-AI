"""
Publish Dispatch — route a finished product to one or more destinations.

Destinations: youtube, tiktok, facebook, google_drive.
Every destination is CREDENTIAL-GATED via 1_CONFIG/credentials_manager: if a key is
missing the destination is reported as "skipped" (never crashes the run). Real
uploads run only when the relevant credentials are present.

  from publish_dispatch import publish
  report = publish({"video": ".../out.mp4", "title": "...", "description": "...",
                    "tags": ["ai"], "thumbnail": ".../thumb.jpg"},
                   destinations=["google_drive", "youtube"])

Returns {destination: result_dict}. result_dict always has 'ok' and 'status'.
"""
import os
import sys
import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent.parent / "1_CONFIG"))

try:
    from credentials_manager import creds
except Exception:
    creds = None

ALL_DESTINATIONS = ["youtube", "tiktok", "facebook", "google_drive"]


def _skip(reason):
    return {"ok": False, "status": "skipped", "detail": reason}


def _to_google_drive(product):
    from gdrive_uploader import upload_to_drive
    res = upload_to_drive(product["video"], rename=product.get("title"))
    # also push the thumbnail if present
    if res.get("ok") and product.get("thumbnail") and os.path.exists(product["thumbnail"]):
        upload_to_drive(product["thumbnail"])
    return res


def _to_youtube(product):
    if not creds or not creds.has("youtube", "oauth_file"):
        return _skip("youtube.oauth_file not set (see 1_CONFIG/README.md)")
    from youtube_uploader import YouTubePublisherAgent
    ok = YouTubePublisherAgent().upload_video(
        video_path=product["video"],
        title=product.get("title", os.path.basename(product["video"])),
        description=product.get("description", ""),
        tags=product.get("tags"),
        privacy=product.get("privacy", "private"),
        thumbnail_path=product.get("thumbnail"),
    )
    return {"ok": bool(ok), "status": "uploaded" if ok else "upload_error"}


def _to_facebook(product):
    """Upload a video to a Facebook Page via the Graph API."""
    if not creds or not creds.has("facebook", "page_token", "page_id"):
        return _skip("facebook.page_token/page_id not set")
    try:
        import requests
    except ImportError:
        return {"ok": False, "status": "lib_missing", "detail": "pip install requests"}
    token = creds.get("facebook", "page_token")
    page_id = creds.get("facebook", "page_id")
    try:
        url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
        with open(product["video"], "rb") as fh:
            r = requests.post(
                url,
                data={"description": product.get("description", product.get("title", "")),
                      "access_token": token},
                files={"source": fh}, timeout=600,
            )
        ok = r.status_code == 200 and "id" in r.json()
        return {"ok": ok, "status": "uploaded" if ok else "upload_error",
                "detail": r.json() if not ok else r.json().get("id")}
    except Exception as exc:
        return {"ok": False, "status": "upload_error", "detail": str(exc)}


def _to_tiktok(product):
    """Initialise a TikTok Content Posting API upload (requires an approved app)."""
    if not creds or not creds.has("tiktok", "access_token"):
        return _skip("tiktok.access_token not set")
    try:
        import requests
    except ImportError:
        return {"ok": False, "status": "lib_missing", "detail": "pip install requests"}
    token = creds.get("tiktok", "access_token")
    try:
        size = os.path.getsize(product["video"])
        r = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"post_info": {"title": product.get("title", ""), "privacy_level": "SELF_ONLY"},
                  "source_info": {"source": "FILE_UPLOAD", "video_size": size,
                                  "chunk_size": size, "total_chunk_count": 1}},
            timeout=60,
        )
        data = r.json()
        return {"ok": r.status_code == 200, "status": "init_ok" if r.status_code == 200 else "init_error",
                "detail": data}
    except Exception as exc:
        return {"ok": False, "status": "upload_error", "detail": str(exc)}


_ROUTES = {
    "google_drive": _to_google_drive,
    "youtube": _to_youtube,
    "facebook": _to_facebook,
    "tiktok": _to_tiktok,
}


def publish(product, destinations=None, save_report_to=None):
    """Dispatch `product` to each destination. Returns {dest: result}."""
    if "video" not in product or not os.path.exists(product.get("video", "")):
        return {"_error": f"product['video'] missing or not found: {product.get('video')}"}
    destinations = destinations or ALL_DESTINATIONS
    report = {}
    for dest in destinations:
        fn = _ROUTES.get(dest)
        if not fn:
            report[dest] = {"ok": False, "status": "unknown_destination"}
            continue
        try:
            report[dest] = fn(product)
        except Exception as exc:
            report[dest] = {"ok": False, "status": "dispatch_error", "detail": str(exc)}
        tag = "OK" if report[dest].get("ok") else report[dest].get("status", "?")
        print(f"[publish] {dest:13s} -> {tag}")
    if save_report_to:
        with open(save_report_to, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    return report


if __name__ == "__main__":
    # `python publish_dispatch.py <video> [dest1,dest2]`
    if len(sys.argv) < 2:
        print("usage: python publish_dispatch.py <video> [dest1,dest2,...]")
    else:
        dests = sys.argv[2].split(",") if len(sys.argv) > 2 else None
        print(json.dumps(publish({"video": sys.argv[1], "title": "Test"}, dests), ensure_ascii=False, indent=2))
