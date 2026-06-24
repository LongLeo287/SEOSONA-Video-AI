"""
SEOSONA Video — Central Credentials Manager
============================================
Single source of truth for every API key, token, password, OAuth file, and
account id used to publish/upload finished products and to run remote control.

Resolution order for every secret (first hit wins):
  1. Environment variable (root .env is auto-loaded here)
  2. 1_CONFIG/credentials/<platform>.json   (structured per-platform secret file)
  3. default / None   -> the caller decides (skip + warn), never crash

WHAT IS COMMITTED: this loader + the *.example.json templates only.
WHAT IS SECRET:    1_CONFIG/credentials/*.json (gitignored) + root .env.

Usage:
    from credentials_manager import creds
    token = creds.get("telegram", "bot_token")
    if creds.has("google_drive", "service_account_file"): ...
    cfg = creds.require("facebook", "page_token", "page_id")   # raises if missing
"""
import os
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CRED_DIR = Path(__file__).resolve().parent / "credentials"

# Load the root .env (keeps every existing load_dotenv('../../.env') call working).
try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except Exception:
    pass

# Logical (platform, field) -> environment variable name.
_ENV_MAP = {
    # core APIs
    ("openai", "api_key"): "OPENAI_API_KEY",
    ("pexels", "api_key"): "PEXELS_API_KEY",
    ("fish_audio", "api_key"): "FISH_AUDIO_API_KEY",
    # publish destinations
    ("youtube", "data_api_key"): "YOUTUBE_DATA_API_KEY",
    ("youtube", "oauth_file"): "YOUTUBE_OAUTH_FILE",
    ("tiktok", "access_token"): "TIKTOK_ACCESS_TOKEN",
    ("facebook", "page_token"): "FB_PAGE_TOKEN",
    ("facebook", "page_id"): "FB_PAGE_ID",
    ("google_drive", "service_account_file"): "GDRIVE_SERVICE_ACCOUNT_FILE",
    ("google_drive", "folder_id"): "GDRIVE_FOLDER_ID",
    # remote control
    ("telegram", "bot_token"): "TELEGRAM_BOT_TOKEN",
    ("telegram", "chat_id"): "TELEGRAM_CHAT_ID",
    # image-gen gateway (infographics/posters via Recraft/Flux/Ideogram)
    ("9router", "api_key"): "NINE_ROUTER_API_KEY",
    ("9router", "base_url"): "NINE_ROUTER_BASE_URL",
}


class CredentialManager:
    def get(self, platform, field, default=None):
        """Resolve one secret: env var first, then credentials/<platform>.json."""
        env_name = _ENV_MAP.get((platform, field))
        if env_name:
            v = os.environ.get(env_name)
            if v:
                return v
        f = _CRED_DIR / f"{platform}.json"
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get(field):
                    return data[field]
            except Exception:
                pass
        return default

    def has(self, platform, *fields):
        """True only if every requested field resolves to a non-empty value."""
        return all(self.get(platform, f) for f in fields)

    def require(self, platform, *fields):
        """Return {field: value} or raise an actionable error naming the fix."""
        missing = [f for f in fields if not self.get(platform, f)]
        if missing:
            raise RuntimeError(
                f"[credentials] '{platform}' missing {missing}. Fix: set the env var "
                f"in .env, or fill 1_CONFIG/credentials/{platform}.json "
                f"(copy 1_CONFIG/credentials/{platform}.example.json)."
            )
        return {f: self.get(platform, f) for f in fields}

    def status(self):
        """Per-platform/field configured-or-not — for doctor / dashboard."""
        out = {}
        for (p, fl) in _ENV_MAP:
            out.setdefault(p, {})[fl] = bool(self.get(p, fl))
        return out


creds = CredentialManager()


if __name__ == "__main__":
    print("SEOSONA Video - credential status:")
    for plat, fields in sorted(creds.status().items()):
        marks = " ".join(f"{k}={'YES' if v else '--'}" for k, v in fields.items())
        print(f"  {plat:14s} {marks}")
