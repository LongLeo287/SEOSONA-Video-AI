# Legacy → V2 Capability-Gap Map & Port Plan

Date: 2026-07-15 · Analysis-only pass (no code changed). Grounds every claim in a real file:line.
Legacy = `D:\SEOSONA AI\SEOSONA Video` (READ-ONLY engine host). V2 = `D:\SEOSONA AI\seosona-video-os`
(READ-ONLY here — another agent is writing it). Companion to `LEGACY_CAPABILITY_MATRIX.md` (KEEP/WRAP
verdicts) and V2 `docs/LEGACY_ORGAN_MAP.md` (organ homes). This doc is the **wiring worklist**: for each
live legacy engine, is the V2 leg real, a throwing seam, missing, or deprecated — and the exact action.

## The one architectural fact that drives everything

V2 already split cleanly into two halves, and only ONE half is wired:

1. **`packages/engines/*` — the real spawn adapters ARE built.** `ttsAdapter.synthesize`
   (`packages/engines/src/ttsAdapter.ts:113`), `asrAdapter.transcribeWords` (`asrAdapter.ts:86`),
   `renderAdapter.renderTimeline` (`renderAdapter.ts:316`), and `mediaEngine.*` (`mediaEngine.ts`) each
   shell into the READ-ONLY legacy hermes venv python, honestly (0 silent fallback, `EngineFailure` on
   any problem). These call the exact live legacy functions: `voice_router.synthesize_voice`,
   `asr_router.transcribe_words`, `native_composer.make_video`.

2. **`services/workers/*Worker.ts` — most engine legs are throwing SEAMS not yet injected with (1).**
   Each worker has a BUILT deterministic core plus injectable interfaces defaulting to `notImplemented*`
   which throw `NotImplementedError` (e.g. `voiceDirectorWorker.VoiceSynth` at `voiceDirectorWorker.ts:71`).
   The comment on that seam even says "OmniVoice via engines ttsAdapter" — **the adapter it names already
   exists; nobody has written the ~10-line injector that hands `ttsAdapter.synthesize` to the seam.**

So the dominant port action is **WIRE**: connect an existing engines-package adapter (or a small new one
in the same pattern) into a worker seam via an injector + honest health-gate. Two seams already do this
the right way and are the template to copy: `renderWorker` requires an injected `RenderAdapterLike`
(`renderWorker.ts:44`, `videoFactoryApp.ts:70` passes it), and `researchWorker` DEFAULTS to the real
`createLegacyFetcher()` over legacy `researcher.py` (`researchWorker.ts:62`, `legacyBridge.ts:113`).

## Counts

| V2 status | Count | Meaning |
|---|---|---|
| **HAVE (real)** | 9 | V2 implements it for real (adapter built + wired, or pure-TS core done) |
| **SEAM** | 13 | V2 role exists; engine leg throws `NotImplementedError` — the WIRE targets |
| **MISSING** | 7 | valuable live legacy capability with no V2 role at all |
| **SKIP** | 6 | deprecated / quarantined — do NOT resurrect |

Note: several capabilities count once as HAVE at the *engine-adapter* level and again as SEAM at the
*worker-injection* level (e.g. OmniVoice: `ttsAdapter` is HAVE, `voiceDirectorWorker.VoiceSynth` is SEAM).
The table below is keyed by the unit that still needs an action, to avoid double-counting the work.

---

## HAVE — already real in V2 (no port work; verify only)

| Legacy capability | Legacy entry | V2 home | Notes |
|---|---|---|---|
| OmniVoice TTS engine adapter | `voice_router.synthesize_voice` | `engines/ttsAdapter.ts:113` | consent-gated, tiny-wav guard; adapter real, worker not yet injected (see SEAM) |
| PhoWhisper ASR engine adapter | `asr_router.transcribe_words` | `engines/asrAdapter.ts:86` | `[]`=honest no-speech vs throw=broken; adapter real, workers not injected (SEAM) |
| native_composer render adapter | `native_composer.make_video` | `engines/renderAdapter.ts:316` | TimelineIR→(segments,scenes), sha256 receipt, capabilityDegradation; injected in `renderWorker` |
| ffmpeg media QA | `ffmpeg-static` | `engines/mediaEngine.ts` | typed-argv (no shell), loudnorm 2-pass, silence/probe; real |
| plan_scenes → timeline | `video_engine.plan_scenes` | `workers/timelineWorker.ts` + `renderAdapter.mapTimeline` | ScriptSpec→TimelineIR→legacy scene dict |
| Topic research chain | `researcher.py::research` | `legacyBridge.createLegacyFetcher` → `researchWorker` | DEFAULT-wired (real); Firecrawl→DDG→RSS |
| Traceable script writer (deterministic) | `youtube_seo`/skeleton | `workers/scriptWorker.ts` (`seo_writer`, built) | HOOK→…→CTA + claim-cite gate in TS |
| SEO packaging metadata | `youtube_seo` optimizer | `workers/packagingSpec.ts` (`seo_optimizer`, built) | title/desc/tags/thumb spec, tag dedupe |
| Caption-sync scoring / VN-safe tokenize | `whisper_engine.group_words` | `engines/captionSync.ts` | LCS sync score, NFC whole-token (no `ai∈hai`) |

---

## SEAM — WIRE these (the core of the port)

Each row: the worker seam interface (throws today) → the legacy engine that fulfils it → whether an
engines-package adapter already exists. **"adapter EXISTS"** means WIRE is just an injector + health-gate
(hours). **"adapter NEEDED"** means PORT a small spawn bridge in the `renderAdapter` pattern, then inject.

| # | V2 seam (throws) | file:line | Legacy engine · entry | Adapter? | Engine/venv needs | Pri | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `voiceDirectorWorker.VoiceSynth` | `voiceDirectorWorker.ts:71` | OmniVoice · `voice_router.synthesize_voice` | **EXISTS** `ttsAdapter` | hermes venv + GPU + consent id | **P1** | map `{text,out_wav,persona}`→adapter; supply consent_id |
| 2 | `voiceDirectorWorker.WordTimer` | `voiceDirectorWorker.ts:81` | PhoWhisper · `asr_router.transcribe_words` | **EXISTS** `asrAdapter` | hermes venv + (GPU auto) | **P1** | measured word timings from the synthesized wav |
| 3 | `cutEditorWorker.Transcriber` | `cutEditorWorker.ts:203` | PhoWhisper · `asr_router.transcribe_words` | **EXISTS** `asrAdapter` | hermes venv | **P1** | same adapter as #2; footage→WordCue[] |
| 4 | `renderWorker` adapter injection | `renderWorker.ts:44` | native_composer · `make_video` | **EXISTS** `renderAdapter` | hermes venv + ffmpeg (+GPU for voice) | **P1** | adapter real + accepted; confirm the composition root injects the REAL one, not a stub |
| 5 | `cutEditorWorker.EdlRenderer` | `cutEditorWorker.ts:213` | `scripts/talking_head_autocut.apply_cut` / `talking_head_edit.py` | NEEDED | ffmpeg (local, no GPU) | P2 | ffmpeg select/concat; `plan_cuts`/`keep_segments` already mirrored in the TS core |
| 6 | `assetSourcerWorker.AssetFetcher` | `assetSourcerWorker.ts:58` | `image_sourcer.source_for_concept` / `search_pexels` (`image_sourcer.py:379/189`) | NEEDED | network (Pexels), keyless-ish | P2 | can't run headless-offline → adapter + health-gate, real run on a networked host |
| 7 | `musicSfxWorker.BgmFetcher` | `musicSfxWorker.ts:131` | `bgm_sourcer.source_bgm` (`bgm_sourcer.py:92`) | NEEDED | network (Openverse/Jamendo) | P2 | CC-BY credits must round-trip into `Credits` |
| 8 | `thumbnailWorker.FrameGrabber` | `thumbnailWorker.ts:110` | `frame_scorer.best_frame` (`frame_scorer.py:89`) | NEEDED | ffmpeg + PIL (local) | P2 | Laplacian/entropy best-frame; local, runnable headless |
| 9 | `thumbnailWorker.ThumbnailRenderer` | `thumbnailWorker.ts:120` | `thumbnail_maker.make_thumbnail` (`thumbnail_maker.py:288`) | NEEDED | playwright/PIL (local) | P2 | html-escape hardened already in legacy |
| 10 | `copywriterWorker.LegacyScriptWriter` | `copywriterWorker.ts:129` | `script_writer.generate_script` (`script_writer.py:556`) | NEEDED | network (LLM cascade) | P2 | cited/traceable leg; deterministic skeleton already built in TS |
| 11 | `publishWorker.PlatformPublisher` | `publishWorker.ts:172` (`youtubeUploaderAdapter` named at `:186`) | legacy `youtube_uploader.upload` | partial (named, throws) | YouTube OAuth + **human gate** | P3 | prohibited to auto-post; stays human-gated by design |
| 12 | `reporterWorker.MetricsSource` | `reporterWorker.ts:252` | `performance_ingest` / `factory_ledger` | NEEDED | network (platform APIs) | P3 | flywheel reducer it feeds is BUILT |
| 13 | `referenceAnalyzer` + `qaCheckerWorker` VLM leg | roster `partial` (`roster.ts:24`,`:48`) | `eval_judge` (Gemini→Ollama→agent) | NEEDED | network/local VLM | P2 | build-once/use-twice; must be evidence-provider, never auto-PASS |

---

## MISSING — valuable live legacy, no V2 role → propose a role/fold-in

| Legacy capability | Legacy entry | Proposal | Pri |
|---|---|---|---|
| Element layer (icons/badges/emoji → transparent PNG/webm) — "talking-head essence" | `element_maker.render_element` / `render_element_clip` (`element_maker.py:371/393`) | New engine adapter + FOLD-IN to `scenePlannerWorker`/`timelineWorker` as an overlay-clip generator; today `renderAdapter` drops overlay effects (see LEARNING) | P2 |
| Native effect/transition/text-effect library | `4_BRAIN/effect_library` + `footage_transition.py` + `svg_draw_on.py` | FOLD-IN to TimelineIR: `renderAdapter.capabilityDegradation` currently DROPS `clip.effects`/`transform`/`source_range` (`renderAdapter.ts:193-204`) — effects are silently unused unless native_composer re-derives them. Needs an IR→effect_library mapping | P2 |
| Carousel content generator | `carousel_generator.generate_carousel_slides` (`carousel_maker/...py:663`) | `carousel_writer` roster row is `planned` (`roster.ts:129`) with no worker → BUILD worker + adapter | P3 |
| Demand/trend topic discovery | `researcher.demand_topics` | `trend_jacking` roster row is `planned` (`roster.ts:138`) → wire a `demand_topics` bridge (mirror `createLegacyFetcher`) | P3 |
| Dub/localization timing | `4_BRAIN/dub_align.py` (pure math, tested, GPL-clean-room) | No V2 role. FOLD-IN as a localize step when a dub pipeline is scoped; low urgency | P3 |
| Semantic asset index of OWNED footage | (none live — GAP #17 in roster doc) | `assetIndexWorker.ts` exists as a worker but has no legacy engine; content-hash + local embedding index — BUILD keyless | P2 |
| Knowledge-graph recall (queryable second brain) | `knowledge_graph.py` recall/find/related | V2 `knowledge/knowledgeRegistry` is `partial` (organ map); FOLD-IN graph recall later | P3 |

---

## SKIP — deprecated/quarantined (do NOT resurrect; confirmed against memory)

| Legacy area | State | Evidence |
|---|---|---|
| Lipsync/avatar line (MuseTalk/SadTalker/LivePortrait/Rhubarb/mascot engines + weights) | DELETED 2026-07-14 (~22.6GB) | git status shows `D 4_BRAIN/lipsync_service.py`, `D scripts/lipsync_musetalk.py`, `D scripts/download_musetalk_weights.py`, `D scripts/download_liveportrait_weights.py`, `D scripts/avatar_motion.py` |
| VieNeu / sherpa / openai-whisper voice+ASR | QUARANTINED (OmniVoice + PhoWhisper only) | `D 2_SKILLS/srt_maker/sherpa_vn_engine.py`, `D 2_SKILLS/voice_cloner/vieneu_engine.py`, `D .../setup_vieneu_env.ps1`, `D .../vn_text_frontend.py` |
| fish_audio TTS | removed (don't rebuild) | memory `no-recreate-deprecated-systems` |
| Local LTX / GenVideo lane (Seedance local) | local lane REMOVED 2026-07-14; paid adapters DORMANT until key | `LEGACY_CAPABILITY_MATRIX.md:48`; seedance = DEFER not port |
| `pipeline_manager` | retired to `_QUARANTINE`; engine is `video_engine`→`native_composer` | memory `render-engine-video-engine` |
| `download_local_models.py` | deleted | git status `D scripts/download_local_models.py` |

---

## Ranked P1 WIRE list — critical path from "typed plan" to "real video"

These are the seams that, once wired, let V2 actually **voice + time + render for real** instead of
throwing. All are cheap because the engines-package adapter already exists — the work is an injector +
health-gate, not a new bridge.

1. **`renderWorker` real-adapter injection** (`renderWorker.ts:44` ← `engines/renderAdapter.renderTimeline`).
   Unblocks: the whole render leg. The adapter is real and the worker already accepts it; confirm the
   production composition root (`videoFactoryApp` construction / any CLI entrypoint) injects the REAL
   `renderAdapter`, not a test stub. **Health-gate:** `renderAdapter.probe` (`renderAdapter.ts:116`) —
   needs hermes venv + native_composer + ffmpeg (+GPU for the voice sub-step). Real run only on the engine host.

2. **`voiceDirectorWorker.VoiceSynth` → `ttsAdapter.synthesize`** (`voiceDirectorWorker.ts:71`).
   Unblocks: real brand voice-over. Injector maps `{text,out_wav,persona}`→`{text,out_wav,consent_id}` and
   returns `{voicePath,duration_ms}`. **Must pass a real consent_id** — the adapter throws `ConsentRequired`
   without one (`ttsAdapter.ts:114`). **Needs hermes venv + GPU** → wire + `probe` health-gate, run on host.

3. **`voiceDirectorWorker.WordTimer` → `asrAdapter.transcribeWords`** (`voiceDirectorWorker.ts:81`).
   Unblocks: MEASURED karaoke word timings (upgrades the estimated timings the timeline currently carries).
   Same adapter powers #4. **Needs hermes venv.**

4. **`cutEditorWorker.Transcriber` → `asrAdapter.transcribeWords`** (`cutEditorWorker.ts:203`).
   Unblocks: real footage→transcript for the talking-head auto-cut EDL (the TS `plan_cuts`/`retime_words`
   core is already built and tested). Reuses the #3 adapter verbatim.

5. **`referenceAnalyzer`/`qaCheckerWorker` VLM leg → `eval_judge`** (`roster.ts:24`,`:48`).
   Unblocks: the self-correcting QA loop (analyze reference → render → score own output). Build-once,
   use-twice. **Guardrail:** evidence-provider only — it must never auto-PASS (the #1 legacy trust-killer).

P1 sequencing: **#1 render + #2/#3 voice/timing** together produce the first end-to-end real video from a
typed plan. #4 extends it to the footage engine; #5 closes the learning loop. Everything in P2 (asset,
bgm, thumbnail, cut-render, script-cite) enriches but does not block a first real render.

### What genuinely can't run headless here (wire = adapter + honest health-gate, real run on engine host)
- **Voice (#2), any render that voices (#1)** — GPU + hermes venv + CQA weights (CC-BY-NC, owner-accepted).
- **ASR (#3,#4)** — hermes venv (CUDA auto-detected; CPU works but slow).
- **Asset/BGM/script-writer/metrics (SEAM 6,7,10,12)** — network (Pexels/Openverse/LLM/platform APIs).
- Local-runnable headless: **FrameGrabber (#8, ffmpeg+PIL)**, **ThumbnailRenderer (#9, playwright/PIL)**,
  **EdlRenderer (#5, ffmpeg)** — these can be wired AND exercised on this machine.

Each adapter must expose a filesystem-only `probe()` (the `ttsAdapter.probe`/`renderAdapter.probe` pattern)
so the OS blocks HONESTLY ("engine host unavailable: <reasons>") instead of faking output.

---

## Craft / knowledge worth LEARNING into V2 (not code)

These are non-code assets/rules; port as V2 `MemoryRecord`s / `sceneGrammar` / brand contract, per the
organ map's "Knowledge Core" (still `BUILDING`):

- **`9_PROMPTS/MASTER_VIDEO_SPEC.md`** — the single content+SEO playbook; the seed for the copywriter's
  retention skeleton and packaging rules.
- **`2_KNOWLEDGE/VIDEO_CRAFT_RULES.md`** — hard craft rules (organ map row already flags it → seed craft
  `MemoryRecord`s + `creative/sceneGrammar`).
- **Brand contract** — light-only palette #2A5BDA / #E2724D (memory `brand-colors-light-only`); dark mode
  forbidden; must live in a V2 brand-kit contract, not scattered.
- **The "RULE CỨNG (bài học)" corpus** — TEXT/PHỤ ĐỀ ≠ PHIÊN ÂM, HOOK full at frame 0, cards don't cover
  the face, karaoke safe-zone, diverse SFX, VERIFY-before-deliver (no fabricated numbers). These are the
  conform-lint's "hard rules present" check (see `VIDEO_SKILL_AGENT_ROSTER.md:94`).
- **Scar-tissue failure classes** (`LEGACY_CAPABILITY_MATRIX.md:79-87`) — VN ASCII substring collisions,
  import-only guard, batch-item resilience, timestamp overflow, easy-PASS scoring, stray relative-path
  outputs. V2 already designs against some (captionSync NFC whole-token; store-root injection); the list
  should be a standing V2 design-review checklist.

---

## Surprises / contradictions vs the memory & roster

1. **The roster says "21 roles" (task) but the built roster is 17 entries** (`roster.ts` ROSTER array:
   director, reference_analyzer, copywriter, qa_checker, cut_editor, scraper, seo_writer, seo_optimizer,
   repurposer, publisher, social_media, carousel_writer, trend_jacking, analytics_feedback, reporter,
   hermes_remote = 16 + directorWorker crew). `VIDEO_SKILL_AGENT_ROSTER.md` lists 14 (+GAP #15–19 = 19).
   The "21" likely counts workers (`services/workers/src` has 27 worker files) or seams, not roster agents.
   Flagging the discrepancy — the roster doc and the worker set are not 1:1.

2. **The engines adapters are further along than "PARTIAL with seams" implies.** tts/asr/render/media are
   REAL, tested spawn bridges — the gap is purely the *injection wiring* into worker seams, which is the
   cheapest possible port. This is good news: V2 is closer to a real render than "seams throw everywhere"
   suggests.

3. **`researchWorker` is already default-wired to legacy `researcher.py`** (`researchWorker.ts:62`) — so
   the RSS-drift content risk (memory `content-safety-layer`) rides along into V2 unchanged. Wire the
   semantic-relevance gate too, or V2 inherits the #1 legacy content bug.

4. **Effects are silently unused at the IR level.** `renderAdapter.capabilityDegradation` records that it
   DROPS `clip.effects`/`transform`/`source_range` (`renderAdapter.ts:193-204`). The legacy `effect_library`
   / `director` motion is real and tested, but a TimelineIR effect currently reaches native_composer only if
   native_composer itself re-derives it. This is honest (degradation is recorded), but it means the
   effect/element craft is a MISSING IR feature, not a wired one — worth explicit scoping.

5. Could not confirm the production composition root actually injects the REAL `renderAdapter` (vs a stub)
   — `videoFactoryApp` *accepts* it as a dep (`videoFactoryApp.ts:29`) but I did not find the top-level
   entrypoint that constructs it with `@seosona/engines`. Flagged as P1 item #1 to verify, not assume.

---

## File written
`D:\SEOSONA AI\SEOSONA Video\docs\v2_phase0\LEGACY_TO_V2_PORT_PLAN.md` (this file). Not git-committed
(factory loop watches legacy).
