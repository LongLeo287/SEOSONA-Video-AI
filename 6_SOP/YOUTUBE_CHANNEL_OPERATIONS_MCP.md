# YouTube Channel Operations MCP SOP

This SOP connects SEOSONA Video publishing workflows to the `yutu` repository and the SEOSONA OS `youtube-channel-operations-mcp` skill.

## Scope

Use this SOP for YouTube uploads, metadata optimization, captions, thumbnails, playlists, comments, channel branding, and post-publish channel operations.

## Operating Lanes

| Lane | Operations | Confirmation |
|---|---|---|
| Retrieval | list, search, inspect videos/channels/comments/playlists/captions | no extra confirmation |
| Modifier | upload, update metadata, set thumbnail, add captions, create playlists, pin comments | confirm target channel and target asset |
| Destroyer | delete videos/playlists/comments/captions/channel sections/watermarks | explicit user confirmation required |

## Credential Rules

- Store YouTube OAuth material outside Git.
- Treat `YUTU_CREDENTIAL`, `YUTU_CACHE_TOKEN`, and `YUTU_LLM_API_KEY` as secrets.
- Do not write OAuth token JSON into `3_MEMORY`, `8_WORKSPACE`, reports, or chat output.
- Prefer minimum necessary OAuth scopes.

## Activation

1. Render and review the video package.
2. Prepare `publish_ready_<platform>.json` through `publisher_agent`.
3. Route YouTube operations through the OS skill:
   `~/.seosona/2_KNOWLEDGE/frameworks/multimedia_production/youtube_channel_operations_mcp/SKILL.md`.
4. Use `yutu` as an external runtime. Do not vendor upstream code into this project.

TASK COMPLETED
