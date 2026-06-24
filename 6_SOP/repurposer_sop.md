# SOP: Long-to-Short Video Repurposer

*Inherited from SEOSONA OS Skill: `seo_marketing/video_content` — "1 Video → 10 Content Pieces"*

## 1. Pipeline Overview

```
Long Video (Podcast/Course/Webinar)
  → Auto-Ingestion (YouTube URL / Google Drive URL / Local Folder Path)
  → Download & Extraction (yt-dlp or ffmpeg)
  → Transcription (Whisper → .srt)
  → SRT Analysis (Agent + Splicing Matrix Prompt)
  → Video Clipping (MoviePy/ffmpeg)
  → Re-render & Re-frame (Strictly Default to 9:16 Aspect Ratio)
  → Multi-platform Publishing
```

**Iron Rule for Repurposing:**
- **Auto-Cut Sources:** The router can seamlessly ingest from `YouTube URLs`, `Google Drive URLs`, and `Local Folders`.
- **Default Aspect Ratio:** All resulting cut clips MUST default to `9:16` vertical format. The engine will automatically center-crop or pad the 16:9 source to fit the vertical screen.

## 2. SRT Analysis Prompt

Master prompt file: `9_PROMPTS/video_scripts/repurpose_analyzer_prompt.md`

### 5-Part Splicing Matrix

| Segment | Purpose | Duration |
|:--------|:--------|:---------|
| HOOK | Most shocking/engaging line | 5-10s |
| PAIN POINT | Consequences / Algorithm warnings | 10-15s |
| TIP/TRICK | Concrete solutions, actionable blueprint | 15-20s |
| CASE STUDY | Real-world examples, specific niches | 10-15s |
| CONCLUSION | Punchline + CTA | 5-10s |

## 3. Splicing Rules

- **Non-linear Splicing**: Cherry-pick lines from any timestamp in the source.
- **100% Raw Text Preservation**: No typo correction during rough cut stage.
- **Strict File Isolation**: Each script uses only ONE SRT file.
- **Transition SFX**: Insert Whoosh/Glitch at every splice point.

## 4. Repurposing Matrix (1 Video → 10 Content Pieces)

1. Full YouTube video (original)
2. YouTube Shorts (30-60s)
3. TikTok (different hook)
4. Instagram Reels (different audio/music)
5. Blog post (transcript → structured article with headings)
6. Twitter/X thread (key points)
7. LinkedIn article (professional angle)
8. Email newsletter (summary + link)
9. Podcast episode (audio only)
10. Infographic (key stats)

## 5. Output Structure

```
8_WORKSPACE/{ProjectName}/
├── {ProjectName}_Part1.mp4
├── {ProjectName}_Part2.mp4
├── {ProjectName}_Part3.mp4
├── SRT/
│   └── {ProjectName}_Matrix_Analysis.json
└── Thumbnail/
    ├── {ProjectName}_Part1_Thumbnail.jpg
    ├── {ProjectName}_Part2_Thumbnail.jpg
    └── {ProjectName}_Part3_Thumbnail.jpg
```
