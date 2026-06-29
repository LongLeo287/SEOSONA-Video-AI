---
name: video-evaluator
description: Independent, skeptical gate that inspects a rendered MP4 (frames + audio) and approves or rejects it before publishing.
---

# Video Evaluator (maker-checker)

The render pipeline is the GENERATOR; this is the EVALUATOR. Per Loop Engineering, the
writer can't fairly judge its own work, so an independent skeptic must approve the output
before it ships. This skill assumes the video is BROKEN until proven otherwise and judges
**behavior** by inspecting the real MP4 — not just file metadata.

## Implementation
`4_BRAIN/evaluator.py` → `evaluate(video_path, brand)`. Free/local (ffmpeg/ffprobe + PIL).

## What it checks (behavioral, complements quality_scorer)
- Reuses `quality_scorer` for the technical/metadata score (no duplication).
- Audio is present, 48 kHz, and NOT silent (catches the "mất voice" class of bug).
- Frames are NOT blank/black (samples 3 points; catches empty-component / black-render bugs).
- Duration is within a sane band (15–95s).

A single behavioral failure → verdict `REJECT` regardless of the technical score
(skeptical posture). Returns `{ok, reasons[], score, duration}`.

## How it connects
- **Publish gate:** `video_engine.maybe_publish` calls it first; a REJECT blocks publishing
  and leaves the file for human review (override with `SEOSONA_SKIP_EVAL=1` for debugging).
- **Observability:** records an `evaluation` event to the hub (`9_DASHBOARD/obs_metrics`).

## Run
```
python 4_BRAIN/evaluator.py 8_WORKSPACE/.../FINAL.mp4   # exit 0 = PASS, 2 = REJECT
```

See `2_KNOWLEDGE/loop-engineering/README.md` (Generator/Evaluator).
