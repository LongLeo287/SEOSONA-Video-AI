# 04 — DATA CONTRACTS

> Schemas passed between stages, with real (redacted) example payloads pulled from `8_WORKSPACE/`.
> Legend: **CONFIRMED** (code/artifact evidence) · **INFERRED** · **UNKNOWN**.

## Formal schema definitions (CONFIRMED)

The only formal, validated schema is `4_BRAIN/script_schema.py` (pydantic, borrowed from a zod contract). It defines the render input contract:

```
CONTENT  (scene_composer.compose() -> native_composer consumes):
  { segments: [str],
    scenes:   [{ h1, h2, kicker?, data? }],
    lexicon?: {} }

TEMPLATE  (7_ASSETS/templates/*.json):
  { name, aspect, scenes: [{ component, accent, kicker_hint, hero }], ... }
```
Validators: `validate_content` / `validate_template` → `{ok, errors, warnings}`. Structural issues = ERRORS (block render); poster char-limits (kicker/h1/h2 ≤ 24) = WARNINGS. `ASPECTS={9:16,16:9,1:1}`, `ACCENTS={blue,green,orange}`, `SEGMENT_MAX_WORDS=45`. Voice text must be emoji/URL-free (RULE #1). — `4_BRAIN/script_schema.py:1-60`.

Other model files: `4_BRAIN/production_manifest.py` (variant-tagging manifest, QA keystone), `4_BRAIN/frame_study.py` (frame-component catalog). No SQL/ORM database exists — all state is JSON/JSONL/YAML on disk.

## Stage-by-stage contracts

| Stage | Producer | Contract (shape) | Consumer | Status |
|---|---|---|---|---|
| Input | user/CLI | raw str (text / github url / http url / media path) | `detect_input_type` → `(mode, input)` | CONFIRMED `video_engine.py:56` |
| Research | `researcher.research` | `{raw_text, sources[]}` | `script_writer.fetch` | CONFIRMED `researcher.py` |
| Analyze | `script_writer.analyze` | `KeyFacts` object | reason/plan | CONFIRMED `script_writer.py` |
| Reason | `angle_finder` | 4 candidate angles | plan | CONFIRMED |
| Script (A) | `script_writer.generate_script` | `(Script, VerifyResult, KeyFacts)`; scenes carry `{seg,h1,h2,comp_hint,block,fx}` | plan_scenes / (topic path drops it — see below) | CONFIRMED `script_writer.py:556` |
| Script (B) | `make_video.auto_content` | `content{segments,scenes[{h1,h2,data,comp_override}]}` | `fill_template` | CONFIRMED `make_video.py:498` |
| Scene plan | `video_engine.plan_scenes` | `(segments: [str], scenes: [{kicker,h1,h2,acc,hero,comp:(kind,data)|None,[fx],[block]}])` | make_video | CONFIRMED `video_engine.py:360,533` |
| Component | `component_picker` | `(kind, data)` per scene | HTML build | CONFIRMED |
| Template fill | `native_composer.fill_template` | `(segments, scenes)`; **raises if len(content.scenes)≠len(template.scenes)** | make_video | CONFIRMED `native_composer.py:3242` |
| Voice | `voice_router.synthesize_voice` | `assets/voice.mp3` | caption timing / mix | CONFIRMED |
| Pacing | native_composer | `_pacing.json` `{durations:[float], total:float}` | mix / caption | CONFIRMED (see example) |
| Word timestamps | `asr_router.transcribe_words` | `words.json` `[{word,start,end,duration}]` | caption timing (RULE#1 align) | CONFIRMED (see example) |
| Captions | native_composer | `_captions_upload/*_cc.srt` (SRT) | sidecar output | CONFIRMED |
| Render spec | native_composer | `proj/index.html` + assets | hyperframes CLI | CONFIRMED `native_composer.py:2924` |
| Raw video | hyperframes CLI | `_raw.mp4` (**absolute path required**) | ffmpeg mix | CONFIRMED `native_composer.py:2946` |
| Final video | ffmpeg mix | `FINAL.mp4` (1080×1920 H.264 + AAC) | thumbnail/QA/publish | CONFIRMED |
| Metrics | `factory_metrics` | one JSONL line (see example) | dashboard / ledger | CONFIRMED |
| Manifest | `production_manifest` | variant-tag manifest JSON | factory_brain / QA | CONFIRMED |
| QA | `quality_scorer.score_video` | `{score:int, verdict, ...}` | gate / publish | CONFIRMED `quality_scorer.py:24` |
| Analytics | `performance_ingest.ingest` | metrics dict | ledger | **STUB (live pull returns None)** `performance_ingest.py:47` |

## Redacted example payloads (real artifacts)

**`_pacing.json`** — per-scene voice durations (`8_WORKSPACE/TOBY_LABS_NEWS/_pacing.json`):
```json
{"durations": [5.14, 2.40, 5.64, 6.20, 3.56, 4.14, 6.68, 3.48, 3.16, 4.20, 2.36], "total": 46.96}
```

**`words.json`** — ASR word timestamps (`8_WORKSPACE/adsbootcamp_11_07/words.json`):
```json
[ {"word":"nếu","start":0.0,"end":0.32,"duration":0.32},
  {"word":"anh","start":0.32,"end":0.46,"duration":0.14},
  {"word":"em","start":0.46,"end":0.6,"duration":0.14} ]
```

**`factory_metrics.jsonl`** — one render flight record:
```json
{"repo":"f/prompts.chat","output":"prompts.chat - SEOSONA.mp4","size_mb":14.83,
 "dur_s":55.3,"ok":true,"issues":[],"template":"quick-tip","script":"llm",
 "lint_warns":5,"ts":"2026-07-06T15:01:03"}
```

**lipsync job record** (`8_WORKSPACE/lipsync_jobs/38b0fcd5763a.json`) — HeyGen-shaped, note **hardcoded absolute Windows paths** and a real QC block:
```json
{"id":"38b0fcd5763a","status":"completed","title":"expert-avatar precision demo",
 "avatar_type":"expert","mode":"precision","duration":8.36,
 "video_url":"D:\\SEOSONA AI\\SEOSONA Video\\8_WORKSPACE\\lipsync_jobs\\38b0fcd5763a\\output.mp4",
 "qc":{"frames_sampled":105,"face_detect_rate":1.0,"openness_corr":0.246, ...}}
```

## Contract defects (CONFIRMED)

1. **Verified `Script` discarded on the topic path.** `topic_to_video.py:121` builds a *verified* `Script` (with `h1/h2/comp_hint/block/fx`), then `:164` passes only joined narration text to `route()`; `plan_scenes` re-derives everything via a second LLM call. The rich, gate-passed structure never reaches the renderer. **Data loss + double LLM spend.**
2. **`fill_template` hard length coupling.** A content/template scene-count mismatch raises `ValueError` (hard abort) instead of degrading. `native_composer.py:3246`.
3. **Hardcoded absolute paths in job records.** lipsync job JSON stores machine-specific `D:\SEOSONA AI\...` paths — not portable across machines; consumers break if the repo moves. (Matches the known `native_composer` absolute-path requirement.)
4. **`render_seconds` field polluted by wall-clock timestamp.** factory_metrics/health show `render_seconds: 1.78e9` — an elapsed-seconds field receiving an epoch value; corrupts `avg_render_seconds`. See [FAILURE_ANALYSIS](06_FAILURE_ANALYSIS.md) MEDIUM-1.
5. **Anti-compression nulls component hints.** When the LLM over-compresses, `video_engine.py:374` sets `plan/_whints=None`, dropping the writer↔library coupling (`comp_hint/block/fx`) for that video.
6. **Analytics contract unfulfilled.** `performance_ingest._youtube_metrics` returns `None` (`:47 # TODO`), so the OBSERVE → learn contract only ever carries local-manifest / injected data, never real platform metrics. The learning ledger is therefore near-empty (`total_videos:1`).
