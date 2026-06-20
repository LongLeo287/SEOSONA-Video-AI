# browser-use
- **Source**: https://github.com/browser-use/browser-use
- **Stars**: ~15k+
- **Tier**: A
- **Domain**: browser-agent (LLM-driven browser automation)
- **Ingested**: 2026-06-20
- **Status**: ingested

## Core Value
Browser Use gives LLMs a real browser action space. It translates Python API commands to a Rust core, driving a Playwright browser harness. Models can navigate, click, type, and extract data based on natural language tasks. 

## Key Architecture / Patterns

### Core Agent Loop
```python
from browser_use.beta import Agent, BrowserProfile, ChatBrowserUse

agent = Agent(
    task="Find the number of stars of the browser-use repo",
    llm=ChatBrowserUse(model='openai/gpt-5.5'),
    browser_profile=BrowserProfile(headless=False)
)
history = await agent.run()
```

### Model Selection
- **ChatBrowserUse**: Built-in optimized model class (`bu-30b-a3b-preview` or `gpt-5.5` etc). 
- Can wrap any standard Langchain chat model. 

### Stealth & Captcha
- Local headless/headful browsing available.
- For intense scraping/anti-bot (Cloudflare, CAPTCHA), it connects to `cloud.browser-use.com` which provides rotated proxies and stealth fingerprints.

### Custom Tools
Agents can be extended with standard python `@tools.action` functions.

## What SEOSONA Video Learned
1. **Agentic Web Navigation**: Instead of hardcoding Selenium scripts that break, we can use an LLM-driven browser agent to research topics, download assets, or even upload videos to platforms with difficult APIs.
2. **Cloudflare Bypass**: If traditional scraping fails, a managed stealth browser (or at least `BrowserProfile` configuration) is required.
3. **Integration**: We can integrate this for "Automated Asset Sourcing" (e.g., finding the best B-roll videos from stock sites via natural language).

## Cleared
YES — raw repo deleted after ingestion
