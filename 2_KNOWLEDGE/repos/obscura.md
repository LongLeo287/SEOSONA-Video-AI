# Obscura Repository Capability Card

Source: https://github.com/h4ckf0r0day/obscura
Snapshot: `cb6ed24d98dc9fc7f6aca5349ebbcc07242fe0ad`
Fit: High
Integration mode: External runtime benchmark plus browser automation fallback

## Why It Fits

Obscura is relevant to SEOSONA Video's scraping, research, screenshot, and B-roll capture layers. It provides a lightweight Rust headless browser, JavaScript rendering, CDP compatibility, parallel scraping, proxy support, stealth mode, and an MCP browser automation server.

## Local Routing

- Keep Playwright as the primary screenshot and browser verification engine.
- Evaluate Obscura for high-concurrency rendered text extraction and research scraping.
- Bind MCP or CDP servers to loopback only unless a separate authenticated deployment is approved.
- Fall back to full Chrome/Playwright for pixel-perfect screenshots, complex login flows, or unsupported browser APIs.

## SEOSONA OS Links

- `~/.seosona/2_KNOWLEDGE/frameworks/browser_automation/obscura_headless_browser/SKILL.md`
- `~/.seosona/2_KNOWLEDGE/raw_data/ingested_data/obscura_headless_browser/README.md`
- `~/.seosona/3_MEMORY/knowledge_items/repo_batch_2026_06_19_yutu_obscura.md`

## Recommended Project Use

Use Obscura as a benchmarked optional runtime for `scraper_agent` and `visual_fetcher` after a small target-site comparison against Playwright.

TASK COMPLETED
