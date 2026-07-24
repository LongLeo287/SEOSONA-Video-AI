# Phase 0 — Legacy Capability Matrix (V2 rebuild gate item)

Date: 2026-07-14 · Source of truth for "what legacy can actually do, at what trust level, and its
V2 disposition". Verdicts follow blueprint §14 (KEEP-as-primitive / WRAP-adapter / REWRITE / RETIRED).
Trust levels: **PROVEN** (test/benchmark/E2E evidence today) · **WORKS** (runs in production, no
formal evidence) · **PARTIAL** (runs with known gaps) · **STUB** (exists, not runnable).

Evidence anchors: 323-test hermetic suite · Phase-0 benchmark `8_WORKSPACE/benchmarks/asr_tts_20260714/`
· E2E render 2026-07-14 (`8_WORKSPACE/ai-14all`, quality 100/100, ffprobe-verified) ·
`video_integration_audit` PASS 0 issues · factory audit `audit_video_factory_20260711_1958/`.

## Content pipeline (V2: services/workers — research/script)

| Capability | Legacy module | Trust | V2 verdict | Notes |
|---|---|---|---|---|
| Topic research + evidence | `4_BRAIN/researcher.py` | WORKS | WRAP | Firecrawl→DDG→RSS chain, semantic relevance gate; RSS drift = #1 content risk (flagged) |
| Demand topic discovery | `researcher.demand_topics` | WORKS | WRAP | keyless Trends VN + YT autocomplete; not auto-wired |
| 6-stage script writing + traceability | `4_BRAIN/script_writer.py` | WORKS | WRAP | fetch→analyze→reason→plan→write→verify; no-fabricated-numbers gate |
| Script schema (spoken/display split) | `4_BRAIN/script_schema.py` + `news_video_standards` | PROVEN | KEEP→contract | display↔pronunciation separation is the seed of ScriptSpec |
| LLM cascade (resilient) | `4_BRAIN/llm_engine.py` | WORKS | WRAP | two cascades, parse-or-continue, Z.ai+NVIDIA+Gemini+Ollama tiers |
| Content safety | writer rules + moderation | PARTIAL | REWRITE | VN substring-collision class fixed 3×; policy QA must be owned by V2 core |

## Audio (V2: packages/engines — TTS/ASR adapters)

| Capability | Legacy module | Trust | V2 verdict | Notes |
|---|---|---|---|---|
| Brand-voice TTS (zero-shot + clone) | `2_SKILLS/voice_cloner/` (OmniVoice ONLY) | PROVEN | WRAP | benchmark WER 0.000/timbre 0.997; **weights CC-BY-NC — owner-accepted**; fail-honest None |
| VN ASR word timestamps | `2_SKILLS/srt_maker/asr_router.py` (PhoWhisper-large-ct2 ONLY) | PROVEN | WRAP | benchmark 0.041 gold WER; cuda auto-detect; defective medium removed |
| Caption segmentation | `whisper_engine.group_words_to_segments` | PROVEN | KEEP | VideoLingo-derived, number-safe; tested |
| VN text normalization for TTS | VietNormalizer + PRONUNCIATION_LEXICON (digit-scoped) | PROVEN | KEEP | brand-acronym trap solved (digit-scoped rule) |
| Dub timing math | `4_BRAIN/dub_align.py` | PROVEN | KEEP | pure math + tests; GPL-clean-room; not yet wired to a full localize pipeline |
| BGM sourcing + ducking + credits | `2_SKILLS/bgm_sourcer` + `native_composer._bgm` | WORKS | WRAP | CC-BY attribution auto-written; md5-stable rotation |
| SFX library + per-component cues | `7_ASSETS/audio/sfx` + `_sfx_cues` | WORKS | KEEP asset + WRAP | beat-snapped in E2E run |

## Visual/render (V2: renderer adapter + TimelineIR)

| Capability | Legacy module | Trust | V2 verdict | Notes |
|---|---|---|---|---|
| HyperFrames brand composition + render | `4_BRAIN/native_composer.py` (~2900 lines) | PROVEN | WRAP (chokepoint) | E2E 100/100 today; THE render chokepoint; needs abs paths (known trap) |
| Unified engine entry | `4_BRAIN/video_engine.py` | WORKS | REWRITE | orchestration/state belongs to V2 control plane |
| Scene planning + components | `scene_composer`, `component_picker`, `frame_synth`, `director` | WORKS | WRAP | data-viz family render-verified; grown-frame floor rule |
| Effect/transition/text-effect library | `4_BRAIN/effect_library` + craft rules | PROVEN | KEEP | hermetic tests; 4-recipe entrance variety |
| Element layer (icons/badges → PNG) | `2_SKILLS/element_maker` | WORKS | KEEP | talking-head essence |
| Talking-head analyze/edit/autocut | `scripts/talking_head_*` | WORKS | WRAP | silence/filler/dup-take EDL + ASS karaoke; SourceLock-compatible |
| Footage transitions + draw-on | `footage_transition.py`, `svg_draw_on.py` | WORKS | KEEP | BSD-3 clean-room |
| Thumbnail (content→PNG) | `2_SKILLS/thumbnail_maker` (+frame_scorer) | WORKS | WRAP | html-escape hardened; best-frame picker |
| Image sourcing (photo per scene) | `2_SKILLS/image_sourcer` | PARTIAL | WRAP | built, not wired into a render engine |
| GenVideo b-roll | `4_BRAIN/seedance_engine`+`_director` | PARTIAL (prompt-only) | DEFER | local lane REMOVED 2026-07-14; paid adapters dormant until key |
| Lipsync/avatar line | — | RETIRED | RETIRED | deleted 2026-07-14 (~22.6GB); do NOT rebuild |

## QA / evaluation (V2: Technical/Craft/Policy split — REWRITE zone)

| Capability | Legacy module | Trust | V2 verdict | Notes |
|---|---|---|---|---|
| Metadata/technical gate | `quality_scorer` | PARTIAL | REWRITE | blueprint: "tự cho PASS quá dễ" — V2 needs evidence-based scorecards |
| Vision judge | `eval_judge` (Gemini→Ollama→agent) | WORKS | WRAP as evidence-provider | must NOT auto-approve in V2 |
| Caption readability lint | native_composer lint | PROVEN | KEEP | flagged 22 cues in today's E2E — honest lint |
| Render verify (silent/blank/duration) | `make_video` verify | PROVEN | KEEP | ran in E2E |
| Spec lint (blank-risk floor) | `spec_lint` + `_grown_kinds` | PROVEN | KEEP | tested |

## Ops / publish / learning (V2: control plane — REWRITE zone)

| Capability | Legacy module | Trust | V2 verdict | Notes |
|---|---|---|---|---|
| Workflow routing | `workflow_router` | WORKS | REWRITE | overlapping ownership — V2 Job state machine replaces |
| Queue + kill-tree timeouts | `queue_processor` | WORKS | WRAP pattern | layered timeout architecture is a keeper pattern |
| Factory loop (autonomous) | `factory_brain` + loop_guard + STOP | PARTIAL | REWRITE | git-race history; circuit breaker pattern keeps |
| Publish (YouTube/Drive) | `publisher` agents | PARTIAL | REWRITE | dry-run evidence only — V2 private-first + receipts |
| Analytics ingest | `performance_ingest` | STUB→PARTIAL | REWRITE | field semantics untrusted (blueprint) |
| Knowledge graph / recall | `knowledge_graph.py` + gen scripts | WORKS | WRAP | 393 nodes; regenerated today |
| Metrics ledger | `factory_ledger`, `factory_metrics` | PARTIAL | REWRITE | per-item resilience fixed; semantics to re-spec |

## Assets to migrate verbatim (blueprint §14.1)

23 JSON templates · 106 BGM + SFX library · 18 brand fonts · voice profile + CQA reference ·
scene components · HyperFrames catalog · brand kit (light-only palette #2A5BDA/#E2724D) ·
mascot pose art · test fixtures (`docs/v2_phase0/fixtures.json`, sha256-pinned).

## Known failure classes V2 must design against (from legacy scar tissue)

1. VN ASCII substring collisions (`\bkw\b` re.UNICODE) — recurred 6+ times
2. Import-only guard (body outside try) — 4×
3. Batch-item resilience (one bad item kills batch) — 5×
4. Timestamp overflow (divmod after ms-rounding)
5. Silent fallback / easy-PASS scoring — the #1 trust killer (V2 rule: fail honest, evidence or no PASS)
6. Stray outputs via relative paths (STRUCTURE.md placement rules, 2026-07-14)
7. Stale duplicate requirements resurrecting removed engines (root pointer pattern)
