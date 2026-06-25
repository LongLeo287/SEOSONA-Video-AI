# yutu

**Source**: https://github.com/eat-pray-ai/yutu
**Category**: A — YouTube automation / publishing
**Wired into**: `1_AGENTS/publisher_agent/` (YouTube upload + channel ops)

## 📖 Description
`yutu` is a fully-featured, scriptable command-line tool for the YouTube Data API v3.
It exposes every major resource (videos, playlists, playlistItems, thumbnails,
captions, comments, channels, subscriptions, activities) as composable subcommands,
which makes it usable both as a standalone CLI and as an MCP server. Because every
action is a single deterministic command, it slots cleanly into an autonomous
publishing pipeline where the agent constructs the call and inspects the JSON result.

## 🎯 Why SEOSONA Video uses it
The publisher tier needs headless, non-interactive YouTube operations: upload a
rendered `.mp4`, set title/description/tags (from `seo_optimizer/youtube_seo.py`),
attach a generated thumbnail, set the privacy status, and read back basic analytics.
`yutu`'s one-command-per-action model is the reference pattern for
`publisher_agent/youtube_uploader.py` — OAuth client credentials live in `1_CONFIG/`,
never hardcoded.

## 🔑 Distilled patterns
- One deterministic subcommand per API resource → easy to drive from an agent.
- OAuth2 client-secret + token-cache flow; credentials kept out of the repo.
- JSON in / JSON out → results are machine-parseable for the EVALUATE node.
- Can run as an MCP server for tool-based invocation.

## 📦 Dependencies
Go binary (no Python runtime). Requires a Google Cloud project with the
YouTube Data API v3 enabled and an OAuth client.

---
*Status: Distilled. Reference for `publisher_agent` YouTube operations. Publish actions require explicit user intent (see `seosona.project.json`).*
