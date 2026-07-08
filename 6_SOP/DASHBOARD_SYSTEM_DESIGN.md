# SEOSONA Video — Dashboard System Design (v2.0)

**Status:** current-state design + forward architecture. Companion to `DASHBOARD_BUILD_PLAN.md` (phase history).
**Scope:** the whole `9_DASHBOARD` app — 19 views, ~27 endpoints, data flow, state, the Studio/Create path, reliability.
**One-line:** a local-first, read-mostly **control plane** over the autonomous video factory — observe everything, act on a few guarded things, and (next) *create* videos.

---

## 1. Requirements

### Functional
- **Observe** every part of the factory from one place: production, quality, queue, knowledge graph, health, learning, templates, files, processes.
- **Act** (guarded, local): refresh the knowledge brain, re-audit integrity, enqueue a video, preview a project.
- **Navigate** the second brain (recall) + the system graph.
- **(Next) Create**: a Studio view to generate/preview/edit/export a video (blueprint = nexu-io/html-video).

### Non-functional
- **Local-first, zero-network, no auth** (user decision — internal tool on one machine). Add auth/WSGI only when it becomes a remote app.
- **Read-mostly + cheap**: a view load = read local JSON/JSONL/dir-scan; sub-100ms typical.
- **Resilient to messy repo state**: dangling junctions, missing files, half-written JSONL lines must never 500 a view.
- **On-brand**: light default (video brand) + dark toggle; Be Vietnam Pro; blue/coral tokens.
- **Foundation for an app** (PWA-installable; portable via `PORT`).

### Constraints
- Solo operator; no build step (vanilla HTML/CSS/JS + Flask); the **autonomous loop owns `main`** and auto-respawns the daemon on :5050.
- Data is whatever the factory already writes — the dashboard adds **no new store**.

---

## 2. High-Level Design

```
┌──────────────────────── BROWSER (SPA, one index.html) ────────────────────────┐
│  Shell: sidebar (.sb-navlink[data-view]) → activateView(v) → lazy loader       │
│  Theme: data-theme (light default / dark), localStorage 'seosona-theme'        │
│  19 views · vis-network graph · toast · polling (Overview/Activity)            │
└───────────────▲───────────────────────────────────────────────────────────────┘
                │  fetch JSON (GET reads · POST actions)
┌───────────────┴──────────────── FLASK server.py (:5050, PORT-aware) ───────────┐
│  READ endpoints (pure, cached-by-nature)   ACTION endpoints (guarded, POST)     │
│  _read_json / os.walk(onerror) / kg.*      _run(UTF-8 env) subprocess           │
└───────────────▲───────────────────────────────────────────────────────────────┘
                │  read-only file access + query API
┌───────────────┴──────────────── DATA PLANE (files the factory already writes) ─┐
│ 3_MEMORY/*.jsonl|json  ·  logs/metrics/events.jsonl  ·  2_KNOWLEDGE/*.json      │
│ 0_INPUT_INBOX/production_queue.yaml  ·  8_WORKSPACE/**  ·  7_ASSETS/templates   │
│ query API: 4_BRAIN/knowledge_graph.py · 9_DASHBOARD/obs_metrics.py             │
└────────────────────────────────────────────────────────────────────────────────┘
```

**Key property:** the dashboard is a **projection layer**. It never owns data; it renders what the engine/loop emit. This is why it's cheap, safe to restart, and always truthful.

### Data flow (one view load)
`click .sb-navlink` → `activateView(v)` sets active + calls the view's lazy loader → `fetch('/api/x')` → Flask reads a local file / calls a query fn → JSON → renderer paints the view. No server-side session, no DB round-trip.

---

## 3. View taxonomy (all 19) → loader → endpoint → source

| Group | View | Loader | Endpoint(s) | Data source |
|---|---|---|---|---|
| **Factory** | Overview | loadOverview (+8s poll) | `/api/metrics` | production_queue.yaml · 8_WORKSPACE · obs_metrics(events) |
| | Analytics | loadAnalytics | `/api/daily-trend` · `/api/system-stats` | events.jsonl · dir counts (os.walk) |
| | Factory | loadFactory | `/api/factory-metrics` | factory_metrics.jsonl · template_scores.json |
| | Library | loadLibrary | `/api/workspace` | 8_WORKSPACE/**.mp4 |
| | Queue | loadQueueDetail | `/api/metrics` | production_queue.yaml |
| | Activity | loadEvents (poll when open) | `/api/events` | logs/metrics/events.jsonl |
| **Intelligence** | Knowledge | recall(on-input) · loadGraphHealth | `/api/recall?q=` · `/api/graph-health` | knowledge_notes.json · knowledge_graph.json |
| | Learning | loadLearned · loadHot · loadAngles | `/api/learned` · `/api/hot-learnings` · `/api/angles` | events×metrics · HOT_LEARNINGS.md · recent_angles.jsonl |
| | System Map | buildGraph (vis-network) | `/api/graph` · `/api/graph-stats` | knowledge_graph.json |
| | Templates | loadTemplates | `/api/templates` | 7_ASSETS/templates/*.json |
| **System** | Health | loadHealth | `/api/knowledge-audit` · `/api/graph-health` | knowledge_audit.json · graph |
| | Kanban | loadKanban | `/api/kanban` | 8_WORKSPACE project states |
| | Preview Lab | loadPreviewProjects | `/api/workspace` · `/api/action/preview` · `/api/video/<p>` | 8_WORKSPACE |
| | Tasks | loadTasks | (events/quality) | events.jsonl |
| | Projects | loadProjects | `/api/workspace` | 8_WORKSPACE |
| **Meta** | Commands | loadCommands | `/api/npm-scripts` | package.json |
| | Wiki | renderWiki | — | static (in-page) |
| | Brand Kit | renderBrandKit | — | static tokens |
| | Settings | loadSettings | — | localStorage |

**Actions (POST, guarded):** `/api/action/refresh-brain` (regen graph+notes+SYSTEM_MAP), `/api/action/re-audit`, `/api/action/enqueue` (validated category + 1–400 chars → queue), `/api/action/preview`.

---

## 4. Deep dive

### API contract (conventions)
- **Reads = GET, pure, no side effects.** Shape: `{ <domain>: [...] , ... }` or a flat object. Always 200 with a sane empty default on missing data — **never 500 a view**. (`_read_json` returns a default; `os.walk(onerror=)` skips broken junctions — the class of bug that took Analytics down.)
- **Actions = POST, guarded.** Validate inputs (category whitelist, length bound), run repo scripts via `_run()` with `PYTHONUTF8=1` (so unicode prints don't crash on cp1252), return `{ok, code, tail[]}` + toast in UI. Idempotent where possible.
- **Errors:** endpoints catch and return `{...empty, error: str}` rather than throwing — the UI degrades to "—"/empty-state, never a blank screen.

### State management (client)
- **No framework.** State = the DOM + a few module globals (`currentView`, `graphBuilt`, theme). `activateView(v)` is the single switch; each view owns an idempotent loader.
- **Persistence:** `localStorage` for user prefs only (theme, sidebar state, default view, polling interval). No app data in the browser.
- **Freshness:** Overview + Activity poll (8s); everything else loads on view-open (lazy) + manual refresh. Rationale: only 2 surfaces are "live"; the rest change on the factory's minute-scale cadence, so poll-on-open is enough and keeps the tab quiet.

### Caching
- **Server:** none needed — file reads are µs–ms. The one in-memory cache is `knowledge_graph.py` (`_cache`/`_notes_cache`), invalidated by `kg.reload()` inside `refresh-brain`.
- **Client:** the service worker caches the **app shell only** (never `/api/*` or `/systemmap`) → instant reloads, always-live data.

### Reliability rules (learned, enforce)
1. **Never `Path.rglob` over `2_KNOWLEDGE`** (external_toolkits has dangling junctions → `FileNotFoundError`). Use `os.walk(p, onerror=lambda e: None)`.
2. **Every `activateView` branch must call its loader** (the Preview bug = a missing branch). A view without a loader shows a permanent "Loading…".
3. **JSONL readers skip bad lines** (half-written rows during a live render).
4. **The daemon is auto-respawned** by the loop; a stale instance can serve old UI. server.py honors `PORT` so a preview runs beside it; Flask debug-reloader picks up edits; templates re-read per request.

---

## 5. Scale & reliability

- **Load:** single user, single box. Biggest cost = dir scans (`system-stats` counted 29k+ files under 2_KNOWLEDGE). Fine now; if it lags, **scope counts to first-party dirs** or cache the count for 60s.
- **events.jsonl growth:** currently read-tail (last 50–60). If it grows large, rotate monthly or index by day (the `daily-trend` aggregation already only keeps 30 days).
- **Graph render:** vis-network physics is the heaviest client cost; already frozen after stabilization. For >1k nodes, switch to a pre-computed layout.
- **Failover:** none needed (local). Monitoring = the Health view auditing *itself* (broken refs/orphans) + the Activity feed. The dashboard IS the monitor.

---

## 6. The Studio / Create view (extensibility path)

Today the dashboard is **read + a few actions**. The blueprint (nexu-io/html-video studio, Apache-2.0, same hyperframes engine) turns it into a **create** surface. Design so this drops in as **one more view** without disturbing the projection model:

```
Studio view  ──▶  POST /api/studio/generate {topic|url, template, aspect, theme}
                    → enqueue a build (reuse make_video / video_engine) → job id
             ◀──  GET  /api/studio/job/<id>   (status: queued→rendering→done, poll)
             ◀──  GET  /api/video/<path>       (preview the MP4 — already exists)
                  POST /api/studio/frame-edit  {job, frame, {kicker,headline,sub}}  (optional human tweak)
```
- **Reuse:** `make_video.py` / `video_engine.py` (generation), `native_composer` (render), `hf_blocks.render_block` (per-frame preview — already a cheap no-LLM path), `/api/video/<path>` (serve).
- **Keep the philosophy:** faceless-autonomous stays the default; Studio is an **optional human-in-the-loop** mode (preview + light per-frame text edit + export), not a mandatory editor.
- **Boundary:** generation is long-running → must be a **job queue** (async), never a blocking request. This is the one place the "read-mostly" model bends — isolate it behind `/api/studio/*` + a jobs file so the rest stays pure.

---

## 7. Trade-offs (explicit)

| Decision | Chosen | Gave up | Why |
|---|---|---|---|
| No JS framework | vanilla + one index.html | component reuse, routing niceties | zero build, matches repo ethos, one file to reason about |
| No DB | read the files the factory writes | query power, joins | truthful by construction, nothing to sync, cheap |
| Local-only, no auth | simplicity | remote access | user decision; revisit for the app phase |
| Poll only 2 views | quiet tab | instant everywhere | factory changes at minute cadence; SSE is the upgrade if needed |
| 19 views in one file | everything discoverable | large file | acceptable for solo; split to per-view modules if it grows |
| Dark+light in-page CSS (~167KB) | instant theme, no FOUC | page weight | fine locally; extract to CSS files if it ships remote |

---

## 8. What to revisit as it grows
- **SSE/WebSocket** for the Activity feed + Studio job status (replaces polling) once "live" matters.
- **Split index.html** into per-view JS modules if the single file passes ~4–5k lines.
- **Scope/caching** for dir-count endpoints if `2_KNOWLEDGE` scans get slow.
- **Auth + WSGI (waitress)** the day it leaves localhost.
- **Jobs store** (a `3_MEMORY/studio_jobs.jsonl`) when Studio lands — the first piece of dashboard-owned state.

---

## Appendix — endpoint index (27)
Reads: `/`, `/systemmap`, `/api/metrics`, `/api/health`, `/api/graph`, `/api/graph-stats`, `/api/graph-health`, `/api/knowledge-audit`, `/api/factory-metrics`, `/api/recall`, `/api/learned`, `/api/events`, `/api/hot-learnings`, `/api/angles`, `/api/workspace`, `/api/daily-trend`, `/api/system-stats`, `/api/templates`, `/api/npm-scripts`, `/api/file-tree`, `/api/process-status`, `/api/kanban`, `/api/video/<path>`.
Actions: `/api/action/refresh-brain`, `/api/action/re-audit`, `/api/action/enqueue`, `/api/action/preview`.
