# SEOSONA Video Factory — Agent Roster

| # | Agent | Directory | Role | Brand |
|:--|:------|:----------|:-----|:------|
| 1 | **Editor Agent** | `editor_agent/` | Scene validation, color checks, light mode enforcement | Both |
| 2 | **Repurposer Agent** | `repurposer_agent/` | SRT analysis, hook extraction, short-form matrix | Both |
| 3 | **Researcher Agent** | `researcher_agent/` | Trending topics, keyword-to-video ideas, article scraping | Both |
| 4 | **Scraper Agent** | `scraper_agent/` | Web content extraction, HTML parsing, multi-URL batch | Both |
| 5 | **Writer Agent** | `writer_agent/` | Video script generation using 5-part structure | Both |
| 6 | **Quality Reviewer** | `quality_reviewer/` | Pre-publish quality gate (score 0-100) | Both |
| 7 | **SEO Optimizer** | `seo_optimizer/` | YouTube Title, Description, Tags, Hashtags generation | Both |
| 8 | **Publisher Agent** | `publisher_agent/` | Multi-platform publish metadata packaging | Both |

## Rules

- Each agent resides in its own directory with at least one `.py` entry point.
- Agents must read `system_config.yaml` for brand profile before execution.
- Agents must never use dark backgrounds in any output (Light Mode Only).
- All agents are importable via `__init__.py` in each directory.
