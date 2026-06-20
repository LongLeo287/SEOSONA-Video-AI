# Obscura Browser Automation SOP

This SOP connects SEOSONA Video research, scraping, and rendered-page extraction workflows to the `obscura-headless-browser` SEOSONA OS skill.

## Scope

Use Obscura only as an external runtime candidate for rendered extraction, CDP-compatible browser automation, MCP browser tools, and high-concurrency scraping.

## Routing

| Need | Primary Runtime | Obscura Role |
|---|---|---|
| Pixel-perfect screenshot | Playwright/Chrome | fallback only after visual comparison |
| Rendered text extraction | Playwright or scraper agent | benchmark candidate |
| Batch scraping | scraper agent | candidate for high-concurrency JS pages |
| MCP browser tools | Codex/browser tools | optional external MCP server |

## Safety

- Bind CDP/MCP to loopback by default.
- Do not expose HTTP MCP publicly without authentication and origin restrictions.
- Set explicit timeouts and concurrency caps.
- Respect robots, terms of service, and contractual limits.
- Treat proxy credentials as secrets.

## Activation

1. Run a one-page extraction comparison against Playwright.
2. Verify required CDP methods for the target workflow.
3. Use Obscura only when it improves speed, memory, or scraping reliability.
4. Log benchmark results before making it a default runtime.

TASK COMPLETED
