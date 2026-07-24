# 00 — EXECUTIVE SUMMARY

**System:** SEOSONA Video — an autonomous Vietnamese video production factory.
**Audit date:** 2026-07-11 19:58 · **Branch:** `main` · **HEAD:** `87c6bb7` · **Mode:** read-only, no changes.
**Legend:** CONFIRMED (code/log evidence) · INFERRED (deduced) · MISSING (no evidence found).

## What the system is trying to do

Turn a single input — a topic, a script, a website URL, a GitHub repo, or existing footage — into a finished, brand-consistent 9:16 Vietnamese short video (voiceover + karaoke captions + animated graphics + SFX/BGM + thumbnail), score it, and (aspirationally) publish it to YouTube/TikTok and learn from performance. It is architected as **two parts sharing one codebase**: THE SYSTEM (brain/infra: routing, LLM cascade, knowledge graph, queue, dashboard) and THE FACTORY (the render production line). **CONFIRMED** (`ARCHITECTURE.md`, code).

## Where the end user starts and ends

- **Start:** a CLI/npm command — e.g. `npm run video:news -- "<topic/script/url>"`, `npm run make:video -- <github-url>`, `npm run video:discover`, or by filling `0_INPUT_INBOX/production_queue.yaml` and running `npm run start:queue` / `npm run daily`. There is **no authoring GUI**; the only UI is a read-only Flask dashboard (port 5050). **CONFIRMED**.
- **End:** `8_WORKSPACE/<project>/FINAL.mp4` (1080×1920 H.264 + AAC) plus `_cc.srt`, a thumbnail PNG, and a render manifest. Publishing exists but has only ever run in **dry-run**. **CONFIRMED**.

## Headline finding (reframes the whole audit)

**The factory is not broken — it demonstrably produces valid videos end-to-end.** `3_MEMORY/factory_metrics.jsonl` holds 30 render records (28 `ok:true`); ffprobe confirms real, playable 9:16 MP4s (e.g. `TOBY_LABS_NEWS/FINAL.mp4` 47s, `prompts.chat - SEOSONA.mp4` 55s); QA and a Gemini-vision judge scored them 92–100 PASS; the live dashboard reports **45 videos on disk**. **CONFIRMED.**

The reason the output isn't "good enough" is **not** a render failure. It is three things:
1. **The quality gate is lenient and self-referential** — every video self-scores 97–100 PASS, yet narration runs at **212–228 WPM** (healthy band 130–180). The gate measures file mechanics, not craft. **CONFIRMED.**
2. **The feedback loop is open** — never truly published, and live analytics ingest is a stub (`return None`). The system has no ground-truth signal of what's actually good. **CONFIRMED.**
3. **The premium capabilities are built but unwired or dependency-blocked** — talking-head, AI b-roll (Seedance/LTX), and lip-sync/avatar engines exist but don't participate in the one-command pipeline, so the auto output is capped at a single animated-card style. **CONFIRMED.**

## Functions that already exist and work (CONFIRMED, wired)

- Input routing + type detection; 6-stage verified script writer with a traceability gate; scene planning + component/template fill.
- Voice (OmniVoice→VieNeu router), PhoWhisper word-level ASR, RULE#1 caption alignment + karaoke.
- HyperFrames + ffmpeg render chokepoint (`native_composer.make_video`), effect/transition/SFX library, BGM sidechain-ducking, −14 LUFS loudness, thumbnails.
- 6-tier LLM cascade (Gemini→Z.ai→NVIDIA→OpenAI→Ollama→Claude) with a keyless offline floor; content-moderation gate; quality scorer + independent evaluator + Gemini-vision judge.
- Operations: queue processor (retry/isolation/timeout), daily scheduler, loop-guard + STOP kill-switch, JSONL flight recorder, Flask observability dashboard.

## Functions expected but not working / not finished

| Capability | State | Evidence |
|---|---|---|
| Publish to platform | INFERRED never real | only `receipts.jsonl` "dry-run ok", views 0 |
| Real performance analytics → learning | MISSING (stub) | `performance_ingest.py:47 return None # TODO`; ledger `total_videos:1` |
| Craft-aware QA (pacing/legibility/occlusion) | MISSING | `quality_scorer` measures mechanics only; WPM out of band passes |
| Talking-head as a factory archetype | RECONNECT | built (`talking_head_edit`, `cinematic_reel.py`) but course/standalone only |
| Generative AI b-roll in the auto path | RECONNECT | Seedance/LTX ready (weights present) but CLI-only, unwired |
| Lip-sync / avatar engines | RECONNECT + blocked | `.venv-musetalk/-sadtalker/-liveportrait` MISSING on disk |
| OmniVoice brand voice in production | INFERRED inactive | records show off-brand `vieneu:*` |
| BytePlus/ModelArk Seedance provider | STUB | `seedance_engine.py:197` raises |

## Three biggest blockers · three things that work · first step

- **Blockers:** (1) open feedback loop — never published, no real analytics; (2) lenient/self-referential QA that green-lights craft-flawed videos; (3) premium engines (talking-head, AI b-roll, avatar) unwired or venv-blocked.
- **Working well:** (1) the render chokepoint reliably ships valid 9:16 MP4s; (2) verified script writer + LLM cascade with keyless floor; (3) operations layer (queue, loop-guard, dashboard, flight recorder).
- **First step:** make the QA gate measure *craft* (bundled ffprobe + enforce 130–180 WPM + caption/loudness/variety) so the factory can finally distinguish a good video from a merely-passable one — the prerequisite for every later improvement.

See [06_FAILURE_ANALYSIS](06_FAILURE_ANALYSIS.md), [07_VIDEO_QUALITY_GAPS](07_VIDEO_QUALITY_GAPS.md), and [08_GAPS_VS_TARGET_FACTORY](08_GAPS_VS_TARGET_FACTORY.md) for detail and fix order.
