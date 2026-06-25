# obscura

**Source**: obscura-headless-browser (SEOSONA OS skill)
**Category**: Browser automation / rendered extraction
**Used by**: `6_SOP/OBSCURA_BROWSER_AUTOMATION.md`, `7_ASSETS/templates/obscura-news-verified-template/`

## 📖 Description
`obscura` is a headless-browser runtime exposing a Chrome DevTools Protocol (CDP)
and MCP-compatible interface for rendered-page extraction and high-concurrency
scraping. It is treated as an **external runtime candidate**, not a primary engine:
Playwright/Chrome and the `scraper_agent` remain the default paths, and Obscura is a
benchmarked fallback for JS-heavy pages, batch scraping, and CDP/MCP browser tooling.

## 🎯 Why SEOSONA Video references it
The news pipeline sometimes needs verified, fully-rendered page content (the
`obscura-news-verified-template`) where a plain HTTP scrape misses JS-injected text.
Obscura is the documented escalation path for that case — used only after a visual
comparison shows the default runtime is insufficient.

## 🔒 Safety contract (from `6_SOP/OBSCURA_BROWSER_AUTOMATION.md`)
- Bind CDP/MCP to loopback by default; never expose HTTP MCP publicly without auth.
- Set explicit timeouts and concurrency caps.
- Respect robots.txt, terms of service, and contractual limits.
- Treat proxy credentials as secrets (kept in `1_CONFIG/`, never in code).

## 🔑 Distilled patterns
- CDP + MCP browser-tool surface → tool-based, agent-drivable automation.
- Fallback-after-comparison routing (primary runtime first, Obscura on miss).
- High-concurrency rendered scraping for verified news extraction.

---
*Status: Distilled. External runtime candidate; routing & safety governed by `6_SOP/OBSCURA_BROWSER_AUTOMATION.md`.*
