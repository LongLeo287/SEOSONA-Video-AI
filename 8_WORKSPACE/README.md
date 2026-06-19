# 8_WORKSPACE — Production Output

## Output Structure

Each pipeline run creates a project folder named after the **project/video name**.

```
8_WORKSPACE/
└── {ProjectName}/
    ├── {ProjectName}.mp4                    → Final rendered video
    ├── SRT/
    │   └── {ProjectName}.srt                → Standard SubRip subtitle file
    ├── Thumbnail/
    │   └── {ProjectName}_Thumbnail.jpg      → SEO-optimized cover image
    └── .temp/                               → Intermediate files (hidden)
```

### Repurpose Mode Output (Long → Short):

```
8_WORKSPACE/
└── {ProjectName}/
    ├── {ProjectName}_Part1.mp4
    ├── {ProjectName}_Part2.mp4
    ├── {ProjectName}_Part3.mp4
    ├── SRT/
    │   └── {ProjectName}_Matrix_Analysis.json
    ├── Thumbnail/
    │   ├── {ProjectName}_Part1_Thumbnail.jpg
    │   ├── {ProjectName}_Part2_Thumbnail.jpg
    │   └── {ProjectName}_Part3_Thumbnail.jpg
    └── .temp/
```

## CLI Commands

```bash
# Create new video (SEOSONA, vertical, named project)
python 4_BRAIN/workflow_router.py "script text" seosona 9:16 Huong_Dan_SEO_2026

# Repurpose long video (CQA, vertical)
python 4_BRAIN/workflow_router.py "D:/long_video.mp4" cqa 9:16 CQA_SEO_Tips

# Download from YouTube and repurpose
python 4_BRAIN/workflow_router.py "https://youtube.com/watch?v=xxx" seosona 9:16 YT_Repurpose
```

## Rules

- Folder name = Project name (set by user at runtime)
- File names inside = Project name (no generic names like "output.mp4")
- Temp files stored in `.temp/` — not auto-deleted
