# SEOSONA Video — Management Dashboard: phased build plan

**Goal (user):** One dashboard to MANAGE all of SEOSONA Video — embed `docs/SYSTEM_MAP.html` (graph/second-brain),
surface every data source, add management actions. **Foundation for a future app.** Big task → strict
phases, each shippable + verified in the browser before the next (to avoid errors).

## Grounding (from the 2 surveys, 2026-07-01)
- **Existing dashboard** = Flask `9_DASHBOARD/server.py` on :5050 (`npm run start:dashboard`, auto-daemon),
  routes `/` + `/api/metrics` + `/api/health`, `templates/index.html` (6 KPIs + 4 sections, 5s poll, no auth,
  local-only). → **EXTEND it, don't rebuild.**
- **Data sources (all local, read-only):** events.jsonl, factory_metrics.jsonl, template_scores.json,
  knowledge_graph.json, knowledge_notes.json, knowledge_audit.json, factory_ledger (computed),
  production_queue.yaml, 8_WORKSPACE, publish receipts. Query APIs: knowledge_graph / obs_metrics /
  feedback_loop / factory_metrics / factory_ledger (all Python, zero-network).
- **SYSTEM_MAP.html** = self-contained (mermaid + vis-network CDN, inline graph data). Embed via iframe (MVP)
  or feed `/api/graph`.
- **Design** = brand tokens in `brand_kit.py`/`DESIGN.md`; SYSTEM_MAP CSS is extractable → one
  `seosona-dashboard.css`. UX from 6 domain skills (esp. make-interfaces-feel-better 16 polish principles).
- **SEOSONA OS** = NO UI framework (bridge + memory namespace only) → **dashboard is STANDALONE**, local tokens.

## Tech decisions (bias: reliability / "tránh lỗi")
- **No build step** — vanilla HTML/CSS/JS on the existing Flask (matches repo ethos, no toolchain to break).
  Tailwind-via-CDN optional later; not for the foundation.
- **Extend Flask** — add read endpoints + (Phase 3) guarded action endpoints. Keep `/api/metrics` intact.
- **Standalone** — no OS dependency; optional OS memory read is a later enrichment.
- **Local-only** stays until a remote/app phase adds a token.

## Phases (each: BUILD → VERIFY in preview [no console errors, on-brand, tests green] → next)

**STATUS (2026-07-01): P0–P4 all built + verified in browser.** 7 views (Overview / System Map /
Knowledge / Health / Factory / Learning / Activity), embedded vis-network graph (243 nodes/245 edges),
recall, health+graph-integrity board, factory scoreboard + enqueue, learning + HOT_LEARNINGS + angles,
live event feed. 3 guarded actions (refresh-brain / re-audit / enqueue) all functional. PWA installable
(manifest + service worker). 0 console errors; 38/38 tests green. Run: `npm run start:dashboard` → :5050.

### Phase 0 — Foundation: design system + data API ✅
- Extract `9_DASHBOARD/static/seosona-dashboard.css` (brand tokens + card/pill/grid/nav + polish base).
- Add read endpoints to `server.py`: `/api/graph`, `/api/knowledge-audit`, `/api/factory-metrics`,
  `/api/ledger`, `/api/recall?q=`, `/api/learned`. All read local files/functions. `/api/metrics` untouched.
- VERIFY: each endpoint returns valid JSON; existing dashboard still loads; pytest green.

### Phase 1 — Shell: multi-view layout + nav ✅
- Rebuild `index.html` into a shell (brand header + sidebar/tab nav) on the new CSS. Views:
  Overview (existing KPIs), System Map, Knowledge, Health, Factory, Learning. Overview must not regress.
- VERIFY: renders in browser preview, nav switches views, 0 console errors, on-brand light-mode.

### Phase 2 — Core views (data → UI) ✅
- **System Map**: embed SYSTEM_MAP (iframe) or interactive graph via `/api/graph`.
- **Knowledge/Recall**: search box → `/api/recall` → accumulated knowledge live (second brain in the UI).
- **Health**: `/api/knowledge-audit` → broken refs / overlaps / undocumented / orphans board.
- **Factory**: factory-metrics + template leaderboard + queue + recent renders.
- **Learning**: ledger dimensions + effect `learned` + HOT_LEARNINGS.
- VERIFY per view: real data renders, no errors.

### Phase 3 — Management actions (view → control) ✅
- Guarded POST endpoints + buttons: refresh brain (`gen_knowledge_graph`+`gen_knowledge_notes`),
  re-audit (`knowledge_audit`), enqueue a video. Local-only, status-reported via toast. `_run()` forces
  UTF-8 stdio so scripts that print unicode don't crash under Windows cp1252. Enqueue is guarded
  (known category + bounded 1–400 char string) and writes `production_queue.yaml`.
- VERIFIED: validation returns 400 on bad input; re-audit + refresh-brain return code 0; enqueue persists
  and reflects in `/api/metrics` (self-test item added then queue restored to avoid loop pickup).

### Phase 4 — Polish + app foundation ✅
- Polish baked into CSS (staggered fadeUp, tabular-nums, shadows>borders, 40px hit-areas, no `transition:all`),
  responsive (<820px sidebar collapses). PWA: `manifest.webmanifest` + `sw.js` (app-shell cache, never
  caches `/api/*` or `/systemmap`) + `icon.svg` → installable = app foundation. Live Activity feed added.
- VERIFIED: manifest/sw/icon serve 200 with correct MIME; SW registers; mobile breakpoint active.
- Auth note: still local-only (0.0.0.0:5050, no auth) — add a token before any remote/app exposure.

## Guardrails
- Each phase verified in a real browser (preview) — DOM/console checks, not just screenshots.
- Don't regress `/api/metrics` or the auto-daemon. Keep zero-network + local-only.
- Don't commit (autonomous loop owns main; stage by exact path only if asked).
- Reference (not vendor) the UX/UI domain skills; brand tokens from brand_kit/DESIGN.md only.
