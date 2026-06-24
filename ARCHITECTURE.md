# SEOSONA Video Factory - System Architecture

## Overview

SEOSONA Video Factory is a multi-brand automated video production system connected to SEOSONA OS through `~/.seosona`. It supports scripted video creation, URL-based research, YouTube download/repurpose flows, subtitle generation, thumbnail generation, and HyperFrames rendering.

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
        B1["workflow_router.py"]
        B2["pipeline_manager.py"]
        B3["quality_scorer.py"]
    end

    subgraph AGENTS["1_AGENTS"]
        C1["researcher_agent"]
        C2["scraper_agent"]
        C3["writer_agent"]
        C4["editor_agent"]
        C5["repurposer_agent"]
        C6["seo_optimizer"]
        C7["quality_reviewer"]
        C8["publisher_agent"]
    end

    subgraph SKILLS["2_SKILLS"]
        D1["script_writer"]
        D2["tts_generator"]
        D3["voice_cloner"]
        D4["srt_maker"]
        D5["srt_parser"]
        D6["yt_downloader"]
        D7["visual_fetcher"]
        D8["video_clipper"]
        D9["thumbnail_maker"]
        D10["metadata_extractor"]
    end

    subgraph FRAMEWORK["5_FRAMEWORK"]
        E1["hf_core"]
        E2["hf_cards"]
        E3["html_renderer"]
        E4["moviepy_wrapper legacy helpers"]
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
    B2 --> SKILLS
    SKILLS --> FRAMEWORK
    FRAMEWORK --> F1
    FRAMEWORK --> F2
    FRAMEWORK --> F3
    FRAMEWORK --> G1
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
4_BRAIN/        Workflow routing, orchestration, and scoring
5_FRAMEWORK/    HyperFrames, HTML renderer, and legacy media helpers
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

1. **HyperFrames & Open Design (Nexu-io) are the CORE** of the Render and dynamic UI system. All frame processing workflows (html_renderer) must be based on their open design standards.
2. The package `seosona-frame-showcase-landscape-16-9-frame-pack` is designated as the **Standard Master Template** (at `5_FRAMEWORK/hf_cards/master_template`).
3. Based on that, the system generated a dedicated **Master Template 9:16** (at `5_FRAMEWORK/hf_cards/master_template_9_16`). This is the default design prioritized when users request Tiktok/Shorts videos. Whenever a new format or Frame Pack is initialized, the system must clone from these `master_template` directories to ensure design standards.
4. FFmpeg is the underlying media processing library (audio overlay/concat).
5. yt-dlp is the primary media ingestion dependency for YouTube downloads.
5. Playwright remains primary for exact screenshots (headless rendering of HyperFrames DOM).
6. yutu is the preferred future YouTube channel operations adapter.
7. Secrets stay in `.env` or external credential stores, never in Git or memory logs.
8. Generated media and production workspaces remain ignored unless explicitly promoted as samples.

TASK COMPLETED
