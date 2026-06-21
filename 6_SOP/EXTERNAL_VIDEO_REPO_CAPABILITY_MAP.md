# External Video Repository Capability Map

Created: 2026-06-19

This SOP maps external video repositories into SEOSONA Video without duplicate engines, parallel workflows, or unclear legal risk. It is the routing decision layer for the 2026-06-19 repository batch.

## Canonical Role Locks

| Layer | Canonical SEOSONA Video component | External repos allowed to influence it | Rule |
|---|---|---|---|
| Web Scraping & Data | `1_AGENTS/scraper_agent/` (NEW) | unclecode/crawl4ai, firecrawl/firecrawl, ScrapeGraphAI/Scrapegraph-ai, DIYgod/RSSHub | crawl4ai is primary for HTML to Markdown. RSSHub for scheduled news. |
| Browser Automation & Screen Record | `2_SKILLS/visual_fetcher/` (NEW) | browser-use/browser-use, microsoft/playwright, browserbase/stagehand | browser-use for dynamic AI interaction. playwright for exact screenshots/scrolls. |
| Browser Automation & Scraping Runtime | `1_AGENTS/scraper_agent/`, `2_SKILLS/visual_fetcher/` | h4ckf0r0day/obscura | Obscura is a benchmarked optional runtime for rendered extraction, CDP automation, and MCP browser tools. |
| Rendering | `5_FRAMEWORK/hf_core/` and `5_FRAMEWORK/hf_cards/` | heygen-com/hyperframes, nexu-io/html-video, midrender/revideo | HyperFrames remains primary. revideo acts as programmable screen composition if needed. |
| Media ingest | `2_SKILLS/yt_downloader/yt_dlp_engine.py` | yt-dlp/yt-dlp, alexta69/metube, imputnet/cobalt, averygan/reclip | yt-dlp wrapper is primary. UI/downloader apps are NOT copied. |
| Transcription and captions | `2_SKILLS/srt_maker/whisper_engine.py` | Huanshere/VideoLingo, WEIFENG2333/VideoCaptioner, chubbyguan/chubbyskills | Improve segmentation, correction, alignment, translation, and subtitle-first routing. |
| Clipping and repurposing | `2_SKILLS/video_clipper/clipper.py` | browser-use/video-use, zhouxiaoka/autoclip, Augani/openreel-video | Add highlight logic and edit-plan validation around the existing clipper. video-use is canonical for screen-based clipping. |
| Long-form short-video generation | `4_BRAIN/pipeline_manager.py` | harry0703/MoneyPrinterTurbo, xuanyustudio/LocalMiniDrama | Distill pipeline patterns only. |
| Design system and scene planning | `5_FRAMEWORK/hf_core/.skills/` | nexu-io/open-design, safishamsi/graphify, dexhunter/seedance2-skill | Use as planning, prompt, and graph references. |
| Agent self-operation | `.agents/skills/seosona-video-operator/`, `4_BRAIN/video_integration_audit.py`, `4_BRAIN/video_template_factory.py` | nousresearch/hermes-agent | Distill self-improving skills, memory, subagents, scheduled work, and operating-loop patterns without importing the full desktop app stack. |
| Multimedia runtime | runtime toolchain | FFmpeg/FFmpeg | Use FFmpeg as external binary/CLI dependency only. |
| Restricted asset cleanup | none | GargantuaX/gemini-watermark-remover | Do not add as an operational skill for third-party watermark removal. |
| YouTube Channel Operations | `1_AGENTS/publisher_agent/`, future YouTube adapter | eat-pray-ai/yutu | yutu is the preferred external runtime candidate for YouTube upload, metadata, captions, comments, playlists, thumbnails, and MCP channel operations. |

## Priority Routing

### P0 - Already integrated or canonical

- heygen-com/hyperframes: already mirrored into the HyperFrames framework area and pinned for deterministic rendering.
- yt-dlp/yt-dlp: already represented by the downloader skill.
- FFmpeg/FFmpeg: already part of the expected runtime layer.
- eat-pray-ai/yutu: ingested into SEOSONA OS as `youtube-channel-operations-mcp`; connect as an external publishing runtime only after OAuth is configured.
- h4ckf0r0day/obscura: ingested into SEOSONA OS as `obscura-headless-browser`; benchmark before promoting over Playwright.
- nousresearch/hermes-agent: reference for autonomous agent operation, persistent skill/memory loops, subagents, and scheduled jobs. Use as method extraction only; do not import the full desktop/messaging stack.

### P1 - High-value method extraction

- browser-use/video-use: extract agentic edit-plan patterns: filler removal, dead-space trimming, transition intent, color-grading directives, caption overlays, and self-evaluation loops.
- Huanshere/VideoLingo: extract subtitle segmentation, alignment, translation, and dubbing workflow ideas.
- WEIFENG2333/VideoCaptioner: extract LLM subtitle correction and translation-review patterns.
- zhouxiaoka/autoclip: extract highlight-selection heuristics for short-form repurposing.
- nexu-io/open-design: extract design-system and agent-skill organization patterns for video templates.
- safishamsi/graphify: extract project-to-knowledge-graph patterns for video workflow traceability.

### P2 - Useful references, no direct import

- harry0703/MoneyPrinterTurbo: study end-to-end short-video orchestration; avoid importing its full app stack.
- nexu-io/html-video: keep as alternate HTML-video reference and template source; HyperFrames remains primary.
- Augani/openreel-video: reference browser-editor UX and timeline concepts.
- xuanyustudio/LocalMiniDrama: reference offline story-to-video pipeline.
- chatfire-AI/huobao-drama: reference short-drama automation stages.
- waooAI/waoowaoo: reference professional film-production workflow staging.
- dexhunter/seedance2-skill: use as prompt-engineering reference for B-roll or generated scene planning.
- chubbyguan/chubbyskills: reference subtitle-first Chinese content ingestion patterns.

### P3 - Low-value or duplicate for this project

- alexta69/metube: web UI around yt-dlp; duplicate of the canonical downloader role.
- imputnet/cobalt: downloader web app; duplicate of media ingestion and higher compliance risk.
- averygan/reclip: downloader UI; duplicate unless its UX is needed later.
- HoangTran0410/douyin-dowload-all-video: narrow, low-activity downloader script; do not import.

### Blocked

- GargantuaX/gemini-watermark-remover: do not operationalize for third-party or unclear-rights assets. Only rights-cleared owned-asset cleanup may be considered, and even then it requires an explicit compliance note in the task log.

## Anti-Overlap Rules

1. One primary renderer: HyperFrames.
2. One primary downloader: yt-dlp through the existing downloader skill.
3. One primary video runtime: FFmpeg through external CLI calls.
4. Full external applications are reference sources, not project dependencies.
5. Add adapters only when they reduce manual work in an existing SEOSONA Video layer.
6. Use metadata-only probing before any external media download.
7. Preserve subtitles before ASR when a platform provides captions.
8. Do not add watermark-removal capability unless rights are explicit and documented.

## Recommended Next Adapters

| Adapter | Source inspiration | Target file area | Purpose |
|---|---|---|---|
| `edit_plan_schema` | browser-use/video-use, autoclip | `4_BRAIN/` or `2_SKILLS/video_clipper/` | A JSON edit-plan contract for cuts, crops, overlays, captions, and QA checks. |
| `caption_quality_pass` | VideoLingo, VideoCaptioner | `2_SKILLS/srt_maker/` | Segment readability, punctuation repair, translation review, and alignment checks. |
| `highlight_ranker` | autoclip, video-use | `2_SKILLS/video_clipper/` | Score long-video moments before cutting shorts. |
| `scene_graph_manifest` | graphify, open-design | `5_FRAMEWORK/hf_core/` | Store render scenes, assets, text, timings, and dependencies as a queryable graph. |
| `video_template_factory` | HyperFrames, LoHa video-maker | `4_BRAIN/video_template_factory.py` | Export verified HyperFrames render outputs into clone-safe reusable templates. |
| `video_integration_audit` | Hermes-style operating checks, HyperFrames, LoHa | `4_BRAIN/video_integration_audit.py` | Audit local source snapshots, skills, SOPs, assets, voice policy, and template readiness. |

## Validation Checklist

- Check existing KI before adding new repo knowledge.
- Keep all project artifacts in English.
- Use relative paths inside persisted docs and JSON.
- Record whether each repo is canonical, reference-only, duplicate, or blocked.
- Run JSON validation after creating Knowledge Items.
