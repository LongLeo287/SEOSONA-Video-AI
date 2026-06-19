# SEOSONA Video Factory — System Architecture

## Overview

SEOSONA Video Factory is a multi-brand automated video production system connected to SEOSONA OS (`~/.seosona`). It supports 2 brands: **SEOSONA** (Business) and **Chí Quyết Academy** (Creator).

## Architecture Diagram

```mermaid
graph TD
    subgraph INPUT["INPUT"]
        A1["Text Script"]
        A2["YouTube URL"]
        A3["SRT File"]
        A4["MP4 File"]
    end

    subgraph BRAIN["4_BRAIN"]
        B1["workflow_router.py"]
        B2["pipeline_manager.py"]
        B3["quality_scorer.py"]
    end

    subgraph AGENTS["1_AGENTS"]
        C1["editor_agent"]
        C2["repurposer_agent"]
        C3["researcher_agent"]
        C4["scraper_agent"]
        C5["writer_agent"]
        C6["quality_reviewer"]
        C7["seo_optimizer"]
        C8["publisher_agent"]
    end

    subgraph SKILLS["2_SKILLS"]
        D1["tts_generator"]
        D2["voice_cloner"]
        D3["srt_maker"]
        D4["srt_parser"]
        D5["visual_fetcher"]
        D6["thumbnail_maker"]
        D7["video_clipper"]
        D8["yt_downloader"]
        D9["script_writer"]
        D10["metadata_extractor"]
    end

    subgraph FRAMEWORK["5_FRAMEWORK"]
        E1["moviepy_wrapper"]
    end

    subgraph ASSETS["7_ASSETS"]
        F1["sfx/ (pops + transitions)"]
        F2["icons/"]
        F3["fonts/"]
        F4["logos/"]
        F5["mockups/"]
        F6["brand_guideline/"]
    end

    subgraph OUTPUT["8_WORKSPACE"]
        G1["{ProjectName}.mp4"]
        G2["SRT/{ProjectName}.srt"]
        G3["Thumbnail/{ProjectName}_Thumbnail.jpg"]
    end

    INPUT --> B1
    B1 --> B2
    B2 --> AGENTS
    B2 --> SKILLS
    SKILLS --> FRAMEWORK
    FRAMEWORK --> ASSETS
    FRAMEWORK --> G1
    SKILLS --> G2
    SKILLS --> G3
    B3 --> G1
```

## Workflow Pipelines

### Mode 1: Create (New Video)
```
Text → TTS/Voice Clone → Whisper (SRT) → Visual Fetcher → MoviePy Render → Quality Check → Output
```

### Mode 2: Repurpose (Long → Short)
```
MP4/SRT → SRT Parser → SRT Analyzer Agent → Video Clipper → MoviePy Render → Thumbnail → Output
```

### Mode 3: Download (YouTube → Short)
```
URL → yt-dlp → Audio Extract → Whisper → SRT Analyzer → Clipper → Output
```

## Directory Structure

```
D:\SEOSONA Video\
├── 1_AGENTS/          → AI Agents (Analysis, Review, SEO, Publishing)
├── 2_SKILLS/          → Technical Skills (TTS, Whisper, Clipper, yt-dlp)
├── 3_MEMORY/          → Project Memory (Logs, Errors, Knowledge, Brand)
├── 4_BRAIN/           → Orchestration (Router, Pipeline, Scorer)
├── 5_FRAMEWORK/       → Render Engine (MoviePy, Effects, Typography, Audio)
├── 6_SOP/             → Standard Operating Procedures
├── 7_ASSETS/          → Asset Library (SFX, Icons, Fonts, Logos, Mockups)
├── 8_WORKSPACE/       → Production Output
├── system_config.yaml → Multi-brand Configuration
├── requirements.txt   → Python Dependencies
└── ARCHITECTURE.md    → This file
```

## Iron Rules

1. **Tech-Editorial Minimalism** — Maximum white space, professional layout. Minimal text, massive size, Be Vietnam Pro font. NO 3D/colorful icons.
2. **Multi-Brand** — SEOSONA (Dark Navy #1A2DB5 / Tech Minimalism) vs CQA (Royal Blue/Pop).
3. **File Name = Project Name** — All outputs must carry the project/video name.
4. **Standard SRT Format** — No JSON for subtitles. SubRip (.srt) only.
5. **Randomized Effects** — SFX and transitions must vary, never repeat the same one.
