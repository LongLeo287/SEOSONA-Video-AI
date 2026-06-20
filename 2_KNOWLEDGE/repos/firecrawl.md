# Firecrawl
- **Source**: https://github.com/firecrawl/firecrawl
- **Stars**: ~20k+
- **Tier**: A
- **Domain**: scraper (API, Markdown extraction, Agent)
- **Ingested**: 2026-06-20
- **Status**: ingested

## Core Value
Firecrawl is a purpose-built API for LLMs and AI Agents to search, scrape, and interact with the web. It automatically handles JS-rendering, proxies, and anti-bot systems, returning clean, token-efficient Markdown or structured JSON.

## Key Architecture / Patterns

### Scrape to Markdown
```python
from firecrawl import Firecrawl
app = Firecrawl(api_key="fc-YOUR_API_KEY")
# Returns LLM-ready markdown, bypassing JS/Cloudflare automatically
result = app.scrape('firecrawl.dev', formats=["markdown"])
```

### Agentic Extraction
It has a built-in agent (`app.agent(prompt="Find founders of X", schema=Schema)`) that autonomously explores websites to extract specific structured data without needing exact URLs upfront.

### MCP & Skill Integration
Provides an MCP server (`firecrawl-mcp-server`) and `firecrawl-cli` skill to instantly give Claude Code or any agent framework the ability to browse the web.

## What SEOSONA Video Learned
1. **Markdown-First Scraping**: For our SEOSONA OS and Video agents, parsing raw HTML wastes tokens. A service or pattern like Firecrawl (turning the DOM directly into readable Markdown) is the preferred way to ingest context.
2. **Web Context as a Skill**: We can implement Firecrawl as a core skill (`2_SKILLS/web_context/`) to give our Video Script writers the ability to instantly research live topics.

## Cleared
YES — raw repo deleted after ingestion
