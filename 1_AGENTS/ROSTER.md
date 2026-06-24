# SEOSONA Video Factory — Agent Roster

12 agents (each in its own dir with a `.py` entry point, importable via `__init__.py`).
Status reflects the actual pipeline as of 2026-06-24 — **WIRED** = dispatched by the
pipeline/workflows; **orphan** = present but not yet dispatched.

| Agent | Directory | Role | Status |
|-------|-----------|------|:------:|
| **Repurposer** | `repurposer_agent/` | SRT hook analysis, long-to-short matrix | ✅ WIRED (pipeline_manager) |
| **Scraper** | `scraper_agent/` | Web content extraction, HTML parsing | ✅ WIRED (pipeline_manager) |
| **SEO Writer** | `seo_writer_agent/` | Scraped-data → video script (5-part) | ✅ WIRED (pipeline_manager) |
| **Carousel Writer** | `carousel_writer_agent/` | Social carousel copy | ✅ WIRED (workflow_social_post) |
| **Social Media** | `social_media_agent/` | Platform captions (PAS) | ✅ WIRED (workflow_social_post) |
| **Analytics Feedback** | `analytics_feedback_agent/` | Post-mortem analytics & system feedback | ✅ WIRED (workflow_router EVALUATE) |
| **Thumbnail Tester** | `thumbnail_tester_agent/` | Thumbnail A/B testing | ✅ WIRED (workflow_thumbnail) |
| **Editor** | `editor_agent/` | Scene validation + Light-Mode-Only enforcement | ✅ WIRED (pipeline_manager profile) |
| **Publisher** | `publisher_agent/` | Upload finished products → YouTube/TikTok/Facebook/Google Drive (cred-gated) | ✅ WIRED (pipeline STEP 8 + telegram /publish) |
| **Hermes** | `hermes_agent/` | Remote-control brain (Telegram) + pre-render script QA | ✅ WIRED (telegram_remote.py) |
| **SEO Optimizer** | `seo_optimizer/` | YouTube title/description/tags/hashtags + JSON-LD | ✅ WIRED (pipeline STEP 8 metadata enrichment) |
| **Trend Jacking** | `trend_jacking_agent/` | Live RSS trend → auto-trigger a news video | ⏳ orphan (autonomous cron entry) |

`personas/` — persona definitions used by the agents.

> **Quarantined** (moved to `_QUARANTINE/duplicate_agents/`, no longer in this tier):
> `writer_agent` (superseded by seo_writer), `researcher_agent` (dup of scraper +
> trend_jacking), `quality_reviewer` (now the wired `4_BRAIN/quality_scorer.py`).

## Rules
- Each agent reads `system_config.yaml` for the brand profile before execution.
- **Light Mode Only** — never use dark backgrounds in any output (enforced by Editor).
- Source language is Vietnamese; English technical terms stay visually correct.
- To wire an orphan agent: dispatch it from `4_BRAIN/workflow_router.py` /
  `pipeline_manager.py` at the right pipeline stage, then update its row above.
