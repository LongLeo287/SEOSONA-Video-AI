"""
Google Drive uploader — push a finished product to a Drive folder.

Auth: a Google service-account JSON (no interactive OAuth). Configure via the
credentials manager: google_drive.service_account_file + google_drive.folder_id
(env GDRIVE_SERVICE_ACCOUNT_FILE / GDRIVE_FOLDER_ID, or 1_CONFIG/credentials/google_drive.json).

Returns a uniform result dict; never raises for a missing config or missing libs —
it reports status so the dispatcher can continue with other destinations.
"""
import os
import sys
from pathlib import Path

# make the credentials manager importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "1_CONFIG"))
try:
    from credentials_manager import creds
except Exception:  # pragma: no cover - only if tier missing
    creds = None

_MIME = {
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".srt": "text/plain", ".json": "application/json",
}


def upload_to_drive(file_path, folder_id=None, rename=None):
    """Upload one file to Google Drive. Returns a result dict."""
    if not os.path.exists(file_path):
        return {"ok": False, "status": "missing_file", "detail": file_path}
    if creds is None:
        return {"ok": False, "status": "no_credentials_tier"}

    sa_file = creds.get("google_drive", "service_account_file")
    folder_id = folder_id or creds.get("google_drive", "folder_id")
    if not sa_file or not os.path.exists(sa_file):
        return {"ok": False, "status": "credentials_missing",
                "detail": "set google_drive.service_account_file (see 1_CONFIG/README.md)"}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return {"ok": False, "status": "lib_missing",
                "detail": "pip install google-api-python-client google-auth"}

    try:
        scopes = ["https://www.googleapis.com/auth/drive.file"]
        credentials = service_account.Credentials.from_service_account_file(sa_file, scopes=scopes)
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)

        name = rename or os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        meta = {"name": name}
        if folder_id:
            meta["parents"] = [folder_id]
        media = MediaFileUpload(file_path, mimetype=_MIME.get(ext, "application/octet-stream"), resumable=True)
        created = service.files().create(
            body=meta, media_body=media, fields="id, webViewLink"
        ).execute()
        return {"ok": True, "status": "uploaded", "id": created.get("id"),
                "link": created.get("webViewLink"), "name": name}
    except Exception as exc:
        return {"ok": False, "status": "upload_error", "detail": str(exc)}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else __file__
    print(upload_to_drive(target))
