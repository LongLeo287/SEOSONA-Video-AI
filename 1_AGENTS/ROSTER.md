# SEOSONA Video Factory — Agent Roster

10 agents (each in its own dir with a `.py` entry point, importable via `__init__.py`).
Status reflects the actual pipeline as of 2026-06-24 — **WIRED** = dispatched by the
pipeline/workflows; **orphan** = present but not yet dispatched.

| Agent | Directory | Role | Status |
|-------|-----------|------|:------:|
| **Repurposer** | `repurposer_agent/` | SRT hook analysis, long-to-short matrix | ✅ WIRED (video_engine) |
| **Scraper** | `scraper_agent/` | Web content extraction, HTML parsing | ✅ WIRED (video_engine) |
| **SEO Writer** | `seo_writer_agent/` | Scraped-data → video script (5-part) | ✅ WIRED (video_engine) |
| **Carousel Writer** | `carousel_writer_agent/` | Social carousel copy | ✅ WIRED (workflow_social_post) |
| **Social Media** | `social_media_agent/` | Platform captions (PAS) | ✅ WIRED (workflow_social_post) |
| **Analytics Feedback** | `analytics_feedback_agent/` | Post-mortem analytics & system feedback | ✅ WIRED (workflow_router EVALUATE) |
| **Publisher** | `publisher_agent/` | Upload finished products → YouTube/TikTok/Facebook/Google Drive (cred-gated) | ✅ WIRED (video_engine STEP 8 + telegram /publish) |
| **Hermes** | `hermes_agent/` | Remote-control brain (Telegram) + pre-render script QA | ✅ WIRED (telegram_remote.py) |
| **SEO Optimizer** | `seo_optimizer/` | YouTube title/description/tags/hashtags + JSON-LD | ✅ WIRED (video_engine STEP 8 metadata enrichment) |
| **Trend Jacking** | `trend_jacking_agent/` | Live RSS trend → auto-trigger a news video | ✅ WIRED (telegram /trend + standalone/cron entry) |

`personas/` — reference persona docs (orchestrator, visual_designer). Reference only —
not loaded by any agent at runtime; the real rules live in code/SOPs.

> **Quarantined** (removed, no longer in this tier):
> `writer_agent` (superseded by seo_writer), `researcher_agent` (dup of scraper +
> trend_jacking), `quality_reviewer` (now the wired `4_BRAIN/quality_scorer.py`),
> `editor_agent` (light-mode is now structural in native_composer — enforcement no
> longer needed; `ooda_loop.py` retired with it).
>
> **Cut for lean profile** (removed): `thumbnail_tester_agent`
> (AI A/B thumbnail scoring — workflow_thumbnail now picks the primary layout), and
> `repurposer_agent/localizer.py` + the `translator` skill (the localize/dub feature).

## Rules
- Each agent reads `system_config.yaml` for the brand profile before execution.
- **Light Mode Only** — never use dark backgrounds in any output (enforced structurally by `native_composer`: the theme system is light-only).
- Source language is Vietnamese; English technical terms stay visually correct.
- To wire an orphan agent: dispatch it from `4_BRAIN/workflow_router.py` /
  `4_BRAIN/video_engine.py` at the right pipeline stage, then update its row above.
