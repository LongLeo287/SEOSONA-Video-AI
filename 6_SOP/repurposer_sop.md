# SOP: Long-to-Short Video Repurposer

*Inherited from SEOSONA OS Skill: `seo_marketing/video_content` — "1 Video → 10 Content Pieces"*

**Scope:** this SOP covers only the two things unique to repurposing — **(1) ingesting a long source** and
**(2) fanning one source into many outputs**. The actual cut-plan (the 5-act non-linear splice matrix,
100%-raw-text rule, transition SFX, one-SRT isolation) is **NOT duplicated here** — it is the SAME engine
as the course path: see **`COURSE_VIDEO_SOP.md`** (`course_planner.py` + `9_PROMPTS/COURSE_SPLICE_PROMPT.md`).

## 1. Ingestion (the unique front-end)
```
Long Video (Podcast / Course / Webinar)
  → Auto-Ingestion (YouTube URL · Google Drive URL · Local Folder Path)
  → Download & Extraction (yt-dlp or ffmpeg)
  → Transcription (PhoWhisper → .srt, via 2_SKILLS/srt_maker/asr_router)
  → hand off to the COURSE_VIDEO_SOP cut-plan → clip → 9:16 re-frame
  → Multi-output distribution (below)
```
- **Auto-cut sources:** ingest from YouTube URLs, Google Drive URLs, and local folders.
- **Default aspect:** all cut clips default to `9:16` (16:9 source is center-cropped / blur-padded).

## 2. Distribution — 1 Video → 10 Content Pieces (the unique back-end)
1. Full video (original)
2. YouTube Shorts (30–60s)
3. TikTok (different hook)
4. Instagram Reels (different audio/music)
5. Blog post (transcript → structured article)
6. Twitter/X thread (key points)
7. LinkedIn article (professional angle)
8. Email newsletter (summary + link)
9. Podcast episode (audio only)
10. Infographic (key stats)

## 3. Output Structure
```
8_WORKSPACE/{ProjectName}/
├── {ProjectName}_Part1.mp4 …
├── SRT/{ProjectName}_Matrix_Analysis.json
└── Thumbnail/{ProjectName}_Part1_Thumbnail.jpg …
```

> The cut-plan prompt lives in `9_PROMPTS/COURSE_SPLICE_PROMPT.md` (canonical). The older
> `9_PROMPTS/video_scripts/repurpose_analyzer_prompt.md` is a superseded fork — prefer COURSE_SPLICE_PROMPT.
