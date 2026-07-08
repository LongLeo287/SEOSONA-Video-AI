# SEOSONA Video Factory - System Architecture

## Overview

SEOSONA Video Factory is a multi-brand automated video production system connected to SEOSONA OS through `~/.seosona`. It supports scripted video creation, URL-based research, YouTube download/repurpose flows, subtitle generation, thumbnail generation, and HyperFrames rendering.

## Two-part model (system vs factory)

SEOSONA Video is **two parts** sharing one codebase. Adopt every repo/knowledge into the part it serves.

1. **THE SYSTEM** — brain & infrastructure: how it learns, decides, vets, schedules, guards,
   observes, improves. *Tiers:* `1_AGENTS` · `2_KNOWLEDGE` (knowledge + ingestion + REPO_VETTING_SOP
   + INGESTION_LOG + REPO_WATCHLIST) · `3_MEMORY` · `6_SOP` · `9_DASHBOARD` (obs + feedback) ·
   `scripts/` loop infra (queue_processor · loop_guard · discovery · daily_production) ·
   `4_BRAIN/llm_engine` routing · `1_CONFIG` + publisher · SEOSONA-OS/UAP integration.
   **Fitting repos:** ingestion tools (markitdown, gitingest), agent/skill catalogs, RAG/knowledge,
   model routers, observability.

2. **THE FACTORY** — the video production line: topic → script → voice + captions → render →
   SFX/BGM → evaluate → output → publish. *Tiers:* `0_INPUT_INBOX` · `4_BRAIN` engine
   (video_engine · native_composer · scene_writer) · `2_SKILLS` (voice/srt/clipper/thumbnail) ·
   `5_FRAMEWORK` HyperFrames · `7_ASSETS` (DESIGN.md/fonts/sfx/bgm) · `2_KNOWLEDGE/domain_skills`
   + `hyperframes/craft` (content/motion craft) · `8_WORKSPACE` outputs.
   **Fitting repos:** video/motion craft, TTS, SEO/copywriting/design knowledge, templates,
   infographic/thumbnail craft. (Full video pipelines = SKIP; they'd replace the engine.)

> Rule of thumb: *does it make the SYSTEM smarter, or the FACTORY's videos better?* → put it
> there, via `6_SOP/REPO_VETTING_SOP.md`, logged in `INGESTION_LOG.md`. See `REPO_WATCHLIST.md`.

## Architecture Diagram

```mermaid
graph TD
    subgraph INPUT["Input"]
        A1["Text script"]
        A2["Website URL"]
        A3["YouTube URL"]
        A4["SRT or MP4 file"]
    end

    subgraph BRAIN["4_BRAIN"]
        B1["workflow_router.py (SuperGraph + quality gate)"]
        B2["video_engine.py (unified entry)"]
        B2b["native_composer.py (renderer)"]
        B2c["scene_composer.py (content brain)"]
        B3["quality_scorer.py"]
    end

    subgraph AGENTS["1_AGENTS"]
        C2["scraper_agent"]
        C5["repurposer_agent"]
        C6["seo_writer_agent"]
        C6b["seo_optimizer"]
        C7["trend_jacking_agent"]
        C8["publisher_agent"]
    end

    subgraph SKILLS["2_SKILLS"]
        D2["tts_generator"]
        D3["voice_cloner"]
        D4["srt_maker (asr_router)"]
        D6["yt_downloader"]
        D8["video_clipper"]
        D9["thumbnail_maker"]
        D10["translator / carousel_maker"]
    end

    subgraph FRAMEWORK["5_FRAMEWORK"]
        E1["hf_core"]
        E2["hf_cards / master_template"]
        E3["hyperframes catalog blocks"]
        E4["hf_engine (vendored, gitignored)"]
    end

    subgraph PROMPTS["9_PROMPTS"]
        Direction TB
        aida(aida_writer)
        seo(seo_writer)
        pas(pas_caption)
        carousel(carousel_schema)
        thumbnail(thumbnail_prompts)
        repurpose(repurpose_srt)
    end

    subgraph ASSETS["7_ASSETS"]
        F1["logos"]
        F2["fonts"]
        F3["sfx"]
        F4["bgm"]
        F5["brand assets"]
    end

    subgraph OUTPUT["8_WORKSPACE"]
        G1["Project MP4"]
        G2["SRT file"]
        G3["Thumbnail PNG"]
        G4["publish_ready JSON"]
    end

    INPUT --> B1
    B1 --> B2
    B2 --> AGENTS
    B2 --> B2c
    B2c --> B2b
    B2 --> SKILLS
    B2b --> FRAMEWORK
    B2b --> F1
    B2b --> F2
    B2b --> F3
    B2b --> F4
    B2b --> G1
    SKILLS --> G2
    SKILLS --> G3
    C8 --> G4
    B3 --> G1
```

## Workflow Pipelines

### Create

```text
Text -> TTS or voice clone -> word timing/SRT -> scene planning -> HyperFrames render -> thumbnail -> QA
```

### Scrape

```text
Website URL -> scraper/research extraction -> script generation -> visual capture or B-roll -> HyperFrames render -> thumbnail -> QA
```

### Download

```text
YouTube URL -> yt-dlp wrapper -> downloaded media -> repurpose flow
```

### Repurpose

```text
MP4/SRT -> subtitle parsing -> highlight or edit-plan analysis -> clipper -> HyperFrames render -> thumbnail -> QA
```

### Publish

```text
Rendered package -> publisher_agent metadata package -> yutu candidate adapter -> YouTube channel operation
```

## SEOSONA OS Capability Links

- YouTube channel operations: `~/.seosona/2_KNOWLEDGE/frameworks/multimedia_production/youtube_channel_operations_mcp/SKILL.md`
- Obscura browser automation: `~/.seosona/2_KNOWLEDGE/frameworks/browser_automation/obscura_headless_browser/SKILL.md`
- Project memory namespace: `~/.seosona/3_MEMORY/projects/seosona-video/`

Project scripts resolve these anchors through `scripts/seosona-project-bridge.cjs`.
Do not bypass the project bridge for autonomy intake, doctor, route, manifest, or
validation commands.

## Directory Contract

```text
1_AGENTS/       AI role modules for research, editing, SEO, QA, and publishing
2_KNOWLEDGE/    Project-level capability cards and external repository notes
2_SKILLS/       Technical implementation modules
3_MEMORY/       Local runtime memory and ignored operational traces
4_BRAIN/        Unified video engine (video_engine + native_composer + scene_composer), routing, scoring
5_FRAMEWORK/    HyperFrames render layer (hf_core, hf_cards/master_template, catalog blocks)
6_SOP/          Standard operating procedures
7_ASSETS/       Logos, fonts, SFX, BGM, and brand assets
8_WORKSPACE/    Generated ephemeral outputs (MP4, SRT) and analytics logs
9_PROMPTS/      Centralized LLM prompt templates (AIDA, PAS, Repurpose, Carousel)
scripts/        Project bridge, runtime, and audit tooling
```

## Reconnection Contract

The current anti-drift map is `6_SOP/SEOSONA_VIDEO_RECONNECTION_MAP.md`.

- `npm run seosona:doctor` is a lightweight project binding check.
- `npm run seosona:doctor -- --strict` additionally fails on global OS graph findings.
- `scripts/seosona-python.cjs` runs only the requested Python command by default.
- Set `SEOSONA_PYTHON_BOOTSTRAP=1` only when the local machine intentionally needs bootstrap/install behavior.
- `npm run autonomy:intake` must go through the project bridge so it can survive a stale `~/.seosona` junction.

## Iron Rules

1. **HyperFrames & Open Design (Nexu-io) are the CORE** of the render system. The engine `4_BRAIN/native_composer.py` builds HyperFrames compositions programmatically and renders natively via the HyperFrames CLI — all compositions follow the open design standards.
2. **Light Mode Only** — the SEOSONA brand is light-mode (blue `#2A5BDA`, coral `#E2724D`); dark backgrounds are forbidden. The renderer enforces this; scenes crossfade so there is never a blank frame.
3. **JSON templates** in `7_ASSETS/templates/*.json` define scene STRUCTURE only (component + accent + kicker hint); content fills them via `native_composer.fill_template`. Manage templates with `native_composer.save_template`/`extract_template` + the `scene-composer` agent skill. The legacy HTML template factory is retired (removed).
4. FFmpeg is the underlying media processing library (voice/BGM/SFX mix, loudnorm, clip cutting).
5. yt-dlp is the primary media ingestion dependency for YouTube downloads.
6. Playwright is primary for scrape screenshots (headless capture of source pages/B-roll).
7. yutu is the preferred future YouTube channel operations adapter.
8. Secrets stay in `.env` or external credential stores, never in Git or memory logs.
9. Generated media and production workspaces remain ignored unless explicitly promoted as samples.
