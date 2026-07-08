# Platform specs — captions, hashtags, upload rules (verified 2026)

Distilled during repo vetting (2026-07-02). Encode these as constants in a future `platform_specs.py`
and as the caption/hashtag rules the script/caption writer must respect. **Reality check:** every public
auto-post path except Telegram needs a **one-time platform audit/verification** — that's a platform
policy, not a code gap; no OSS repo removes it (cookie hacks risk bans → never use them).

## Caption / hashtag limits
| Platform | Caption max | Best length | Hashtags | Notes |
|---|---|---|---|---|
| **TikTok** | 4000 | 50–150 chars | **≤5 in caption** | Content Posting API; unaudited app = private (`SELF_ONLY`) only |
| **YouTube Shorts** | title ≤100 (first ~40 visible) · desc ≤5000 | punchy title | ~3 (`#Shorts` optional) | classified as a Short by duration ≤3min + vertical aspect |
| **Facebook Reels** | 5000 | 80–150 words | few | 9:16 native via `/video_reels` (NOT legacy `/videos`) |
| **Instagram Reels** | 2200 | short | ≤30 (use ~5) | ≤90s; Business/Creator account linked to a FB Page |

## Upload flows (official, free — audit-gated for public)
- **YouTube:** Data API v3 `videos.insert`, resumable upload (256KB-multiple chunks), scope `youtube.upload`.
  Upload cost dropped to ~100 units (Dec 2025) → ~100 uploads/day on the free 10k quota. Unverified app →
  uploads locked **private** until a one-time API audit.
- **TikTok:** Content Posting API — `/v2/post/publish/video/init/` → **PUT the binary to the returned
  `upload_url`** → **poll `/v2/post/publish/status/fetch/`**. Query `/creator_info/` for allowed privacy
  levels. (Our `publisher_agent._to_tiktok` currently only does `init` → never actually publishes = a bug.)
- **Facebook/Instagram Reels:** Graph API 3-phase — start (`upload_phase=start`) → upload → finish/publish.
  Supports `publish_time` for scheduling. (Our `_to_facebook` uses legacy `/videos` → should move to Reels.)
- **Telegram:** Bot API, token only, no review — the one instant path (already wired).

## Backlog (needs real tokens + business verification to build+test)
1. Fix `publisher_agent._to_tiktok` to complete init→upload→poll (reference: gitroomhq/postiz-app flow, AGPL → re-implement clean, don't vendor).
2. Upgrade `_to_facebook` to Reels 3-phase + add `_to_instagram` (pattern: XavierZambrano/facebook-reels-api, MIT).
3. A small drip/queue + this spec as `platform_specs.py` constants for the caption writer.
