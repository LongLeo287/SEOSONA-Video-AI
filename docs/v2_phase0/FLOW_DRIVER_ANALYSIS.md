# SEOSONA Flow — Connecting to its built-in MCP (AI Agent) server

**Goal:** let Claude Code / Cursor drive SEOSONA Flow's Gen panel programmatically —
"tell an AI agent to generate images/videos & build workflows on your account" — **without** clicking the
Chrome side panel.

**Answer:** SEOSONA Flow **already ships an MCP integration.** You do NOT build an MCP server. In the
extension: **Settings → "AI Agent / Bot" tab → "AI / MCP" sub-tab → "Connect AI Agent (MCP)"** → create a
token → paste the given config into your MCP client. This doc extracts, from the extension code, the
**exact transport, endpoint, auth, tool surface, and copy-paste registration** — plus the honest
preconditions.

Repo read: `D:\SEOSONA AI\SEOSONA Workflow\seosona-flow` (MV3, v1.1.37, ext id
`inkkgjebegapgbapigamkcclpblfdhjn`, Chrome Profile 16). **Fail-honest throughout.**

---

## TL;DR

- **Transport:** a **remote HTTP/SSE MCP server**, reached through the **`mcp-remote`** stdio↔HTTP adapter.
  It is **hosted by the SEOSONA backend**, NOT by the extension (an MV3 extension can't listen on a socket).
- **Endpoint:** `<API-host>/mcp` — the exact string the UI shows is **`http://localhost:8080/mcp`**
  (the dev backend). The host = whatever the extension's API base points to
  (`ApiBaseConfig.DEFAULT = http://localhost:8080/api/v1`, overridable via `chrome.storage.local.apiBaseUrl`;
  prod fallback host is `labs.seosona.vn`). Note the MCP path is **`/mcp` at the host root**, not under `/api/v1`.
- **Auth:** HTTP header **`Authorization: Bearer <token>`**. The `<token>` is created in the UI
  ("Create new token", shown once) and is a **SEOSONA backend token** — creating it requires being
  **logged in** and on a **Premium/supported plan** (the sub-tab shows a "requires Premium" lock otherwise).
- **The extension is the executor arm, not the server.** The backend MCP receives the agent's tool calls,
  pushes them to the extension over **SSE** (`ai_command`), the extension runs them on your logged-in Flow
  tab, and posts results back (`POST /mcp/result`). So a generation needs: **backend online + you logged in
  (Premium) + extension in ONLINE mode + the Flow tab open in a project + the executor context alive.**
- **Honest blocker:** on the **default local/offline build there is no `/mcp` server and SSE is disabled**,
  so token creation and connection won't work until a SEOSONA backend is reachable at the API host (run it
  locally on `:8080`, or use SEOSONA's hosted service). See §5.

---

## 1. The connect config the UI hands you (evidence)

`pages/settings.html` — "AI / MCP" sub-tab (`#mcpContainer`, default-active), section
"Connect AI Agent (MCP)" (`#mcpConnectGuide`, line ~1229) shows this **verbatim** config:
```json
{
  "mcpServers": {
    "seosonaflow": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8080/mcp", "--header", "Authorization:Bearer <token>"]
    }
  }
}
```
UI copy (line 1192 / 1225): *"Create a token and paste it into your MCP client config
(Authorization: Bearer). Do NOT share the token."* and *"Paste this into your MCP client config
(Claude Desktop: claude_desktop_config.json), then replace `<token>` with the token above."*

**This template is static** — `settings-page.js` only copies its literal text (`mcpConfigCopyBtn`, line 1239);
it does **not** substitute the live host or token. So **you replace `<token>` yourself**, and if your
backend isn't the dev `localhost:8080` you also swap the host (see §2).

### Token lifecycle (evidence)
`scripts/settings-page.js`:
- Create: `handleMcpCreateToken()` → `_telegramApiCall('POST', 'mcp/tokens', { label })` (line 1299).
- List: `_telegramApiCall('GET', 'mcp/tokens')` (line 1221).
- Revoke: `_telegramApiCall('DELETE', 'mcp/tokens/{id}')` (line 1331).
- `_telegramApiCall` sends `{action:'apiRequest', endpoint:'mcp/tokens', token: af_auth.token}` to
  `background.js`, which prefixes the API base → **`<API-base>/api/v1/mcp/tokens`**, and **requires
  `af_auth.token`** (i.e. you must be logged in). The token pane is hidden behind a **Premium gate**
  (`#mcpLocked`: "AI Agent connection requires Premium"). The connect guide only appears **after ≥1 token
  exists**.

---

## 2. Endpoint & host resolution (exact)

| Piece | Value | Source |
|---|---|---|
| MCP protocol endpoint | `http://localhost:8080/mcp` (dev) → generally `<scheme>://<API-host>/mcp` | `settings.html` template; host = API base host |
| API base (default) | `http://localhost:8080/api/v1` | `src/core/ApiBaseConfig.js:20 DEFAULT`; `background.js:73 API_BASE_DEFAULT` |
| API base (override) | `chrome.storage.local.apiBaseUrl` | `background.js:75-83` |
| Prod host (fallback) | `labs.seosona.vn` | `ApiBaseConfig.js` comment ("labs.seosona.vn fallback"); origin allowlist |
| Token mgmt endpoint | `<API-base>/api/v1/mcp/tokens` (POST/GET/DELETE) | `settings-page.js` + background `apiRequest` |
| Auth | header `Authorization: Bearer <token>` | `settings.html:1192`, template |

So: **dev** → `http://localhost:8080/mcp`; **prod** → most likely `https://labs.seosona.vn/mcp` (the same
host serving the API — confirm against your live backend, as only the dev host is hard-coded in the shipped
template).

---

## 3. Tool surface exposed to the agent

The MCP tool **definitions live on the backend server** (not in this repo), so the exact tool *names/JSON
schemas* aren't in the extension code. But the extension's executor whitelists the **command surface** the
backend maps those tools onto — this is the authoritative capability list
(`src/core/McpExecutor.js:48`):

```
gen_image, gen_video, upload_ref, run_workflow, create_project,
open_project, get_context, get_provider_status, delete_chat
```

**Generation args** (what a generate tool accepts), from `McpExecutor._executeFlowGen` (line 164) and
`_mapRatio`:
```jsonc
{
  "prompt": "…",            // or "prompts": ["…","…"] (multi — each → 1 result)
  "provider": "flow",       // "flow" | "chatgpt" | "grok"  (default flow)
  "model": "Nano Banana Pro",// Flow model label; omit = current UI selection
  "ratio": "16:9",          // 16:9→Ngang, 9:16→Dọc(default), 1:1→Vuông, 4:3, 3:4, or landscape/portrait/square
  "count": 1,               // images/prompt, 1..4 (image only; video=1)
  "refs": [], "refs_per_prompt": [[]], "ref_mode": "none", "reuse_refs": [], // reference images (local path via Claude Code CLI, or public URL)
  "duration": null, "video_input_type": "Frames", "voice": "slug"  // video-only
}
```
Result payload (`_sendResult`, line 770): `{ job_id, status, thumbnails[], result_count, batch }` or
`{ status:"failed", error_code, error_message }`. Error codes include `PROVIDER_TAB_NOT_READY`,
`EXTENSION_BUSY`, `DAILY_QUOTA_EXCEEDED`, `GEN_FAILED`, `CANCELLED`.

**Reference-image note (from the UI guide):** local files work only via **Claude Code (CLI)** (Desktop
can't send local files); public **image URLs** work on both (must open without login/cookie).

Auto-download of results to disk is governed by extension settings
(`mcpAutoDownload` + `mcpDownloadResolution` 1k/2k/4k + `mcpVideoDownloadResolution` 720p/1080p/4k +
`mcpDownloadFolder`), same panel — default **OFF** (MCP returns results to the agent; enable to also save).

---

## 4. Client registration (copy-paste)

Replace `<TOKEN>` with the token from the UI, and the host if not the dev default.

### (a) Claude Code — recommended: native HTTP transport
```bash
claude mcp add --transport http seosonaflow http://localhost:8080/mcp \
  --header "Authorization: Bearer <TOKEN>"
```
### (a′) Claude Code — via mcp-remote (matches the extension's own template; use if native HTTP misbehaves)
```bash
claude mcp add seosonaflow -- npx -y mcp-remote http://localhost:8080/mcp \
  --header "Authorization:Bearer <TOKEN>"
```
Verify: `claude mcp list` → `seosonaflow` connected; the `gen_image`/`gen_video`/`run_workflow`/… tools appear.

### (b) Generic MCP config (Claude Desktop `claude_desktop_config.json`, Cursor `~/.cursor/mcp.json`, `.mcp.json`)
Exactly the extension's template, token substituted:
```jsonc
{
  "mcpServers": {
    "seosonaflow": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8080/mcp", "--header", "Authorization:Bearer <TOKEN>"]
    }
  }
}
```
(For a prod backend, swap `http://localhost:8080/mcp` → `https://<your-seosona-host>/mcp`.)

`mcp-remote` (npm, MIT) is the stdio↔remote-HTTP bridge; `npx -y` fetches it on first run (Node required).

---

## 5. Preconditions & honest blockers (what must be true to actually generate)

1. **A SEOSONA backend must serve `/mcp` and `/api/v1/mcp/tokens`** at the API host. Dev = run it on
   `localhost:8080` (matches `API_BASE_DEFAULT`); prod = SEOSONA's hosted service. **On the plain
   local/offline extension build there is no such server** → token creation returns nothing (needs
   `af_auth.token`) and the endpoint is unreachable. This is the #1 blocker.
2. **You must be logged in + Premium.** The MCP token pane is gated (`#mcpLocked` "requires Premium");
   `mcp_enabled` is also re-checked in `McpExecutor` (`FEATURE_NOT_IN_PLAN`).
3. **Extension must be in ONLINE mode.** `SseClient.connect()` returns immediately when
   `SEOSONA_LOCAL_MODE !== false` (`src/core/SseClient.js:103`), so it never receives the backend's
   `ai_command` push and `ApiClient` blocks `mcp/result`. Online mode = set `SEOSONA_LOCAL_MODE=false` +
   configure `apiBaseUrl` (`RuntimeMode.js` header). Default is **local/offline**.
4. **The executor context must be alive + Flow ready.** The generation brain
   (`McpExecutor`/`PromptQueue`/`EditorExecutor`, all loaded by `pages/sidebar.html`) runs in the sidebar
   page — keep the extension active and **`labs.google/fx` open inside a project, logged in**
   (`ProjectHelper.isFlowProjectReady`, else `PROVIDER_TAB_NOT_READY`). One job at a time
   (`EXTENSION_BUSY`). Every gen spends your own Google Flow quota (no API key in the extension).

**Near "one button" reality:** once the backend is online + you're logged in Premium, it's:
create token → run `claude mcp add … --header "Authorization: Bearer <TOKEN>"` → keep a Flow project tab
open. If any of §5.1–5.4 isn't met, connection or generation fails with the error codes in §3.

---

## 6. Appendix — fallbacks if the first-party MCP isn't available (offline/no-backend)

If you can't run the SEOSONA backend, the built-in MCP can't be used. Options, in order (documented only —
no code shipped, per instruction not to build a server):

- **A. In-page eventBus hook (thin, reversible).** In the sidebar page, `window.eventBus.emit(
  'sse:ai_command', {command, args, job_id})` runs the exact same validated pipeline as a backend push
  (`McpExecutor.init` subscribes to it; `EventBus.js:36/20`). Reach it from outside via **CDP**
  (`--remote-debugging-port` + `Runtime.evaluate` on the `…/pages/sidebar.html` target) — no extension
  change — or via a **localhost-WS bridge module** added to the sidebar (opt-in, ~60 lines). Requires the
  side panel open. `_sendResult`'s backend POST no-ops in local mode.
- **B. Drive the real UI over CDP.** Set `#promptsArea` + `#genProvider`/`#genType`/`#imageModel`/
  `#videoModel`/`#aspectRatio`/`#quantitySelect`, then click `#startBtn` (Tạo; handler `GenTab.js:830`).
  Most robust; reuses all UI validation.
- **CDP relaunch (both A-CDP and B):** quit Chrome, then
  `chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\chrome-debug-seosona" --profile-directory="Profile 16"`
  (copy the profile first; Chrome ≥136 refuses remote debugging on the default user-data-dir).

Browser-control licenses (fallback only): Playwright **Apache-2.0**, playwright-mcp **Apache-2.0**,
browser-use **MIT**, chrome-remote-interface **MIT**, mcp-remote **MIT** — all commercial-safe.

**These are strictly fallbacks. The intended, first-party path is §1–§4: connect to the extension's own
MCP with a token.**
