# Phase 0 — Architecture Decision Records (V2 Core & Engines)

Format: context → decision → consequences. Status: ACCEPTED unless noted. Date: 2026-07-14.
These formalize blueprint §11–12 with the evidence produced since.

## ADR-001 — SEOSONA owns the core; external repos are engines-behind-adapters only

**Context.** 1,537-repo inventory (149 S-Core) showed no external project can be the Video OS;
legacy's pain came from orchestration/state ambiguity, not from primitives.
**Decision.** SEOSONA owns: JobContract + state machine, ResearchBundle, ScriptSpec, TimelineIR
(single render truth, rational timebase), ArtifactManifest, Evaluation/Approval, PublishReceipt,
learning loop. Every external capability sits behind an adapter exposing
`probe() / capabilities() / execute() / healthcheck() / cost / receipt`. One default engine per
boundary in Phase 1 — no parallel renderers/timelines/factories.
**Consequences.** Engine swap = adapter swap gated by contract tests + golden fixtures; providers
never write to final state; no silent fallback (every fallback records engine/version/reason).

## ADR-002 — Renderer: HyperFrames primary; FFmpeg/ffprobe the only MediaEngine

**Context.** HyperFrames is HTML-native, agent-friendly, seekable, and carried today's E2E
(fx01 quality 100/100). Remotion has license/business review pending; CapCut has no headless path.
**Decision.** HyperFrames = primary renderer behind a renderer adapter mapping TimelineIR → its
primitives. FFmpeg/ffprobe = the single media-execution engine via a typed argv adapter. OTIO =
import/export interchange only. Deterministic-render rules: seekable animation, seeded random, no
network-at-render; RenderReceipt records TimelineIR hash + tool versions + asset hashes.
**Consequences.** legacy native_composer is WRAPPED as the first adapter implementation, not
copied; golden-frame tests pin templates.

## ADR-003 — Voice: OmniVoice is the ONLY TTS engine (owner accepts CC-BY-NC weights)

**Context.** Phase-0 benchmark (evidence `8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md`):
all candidates fully intelligible; OmniVoice best timbre match to the CQA brand voice (0.997);
VieNeu is the only Apache-clean VN clone engine but owner chose quality. OmniVoice weights are
CC-BY-NC (Emilia) — risk explicitly accepted by the owner on 2026-07-14.
**Decision.** OmniVoice (k2-fsa, isolated venv, zero-shot + CQA clone) is the single voice engine.
NO backup engine: failed synth returns None and the job fails honestly. Voice cloning requires a
rights-cleared reference (consent gate carries into V2 as consent_id). VieNeu stays ON RECORD as
the license-clean alternative if the NC stance changes — re-entry only via a new benchmark.
**Consequences.** Commercial-publish policy QA must carry the NC flag on every voiced artifact;
revisit before any monetization decision that a lawyer would care about.

## ADR-004 — ASR: PhoWhisper-large (CT2 fp16) on faster-whisper; reject whisper.cpp + WhisperX

**Context.** Benchmark: bundled medium-ct2 int8 DEFECTIVE (repetition loops, WER 0.702);
PhoWhisper-large 0.041; field survey: language-specialized fine-tunes beat generic large-v3 for
accented non-English (FunClip→Paraformer, VN→PhoWhisper). whisper.cpp DTW word timestamps
unsupported for PhoWhisper fine-tunes; WhisperX's VN aligner is CC-BY-NC.
**Decision.** ONE model: `kiendt/PhoWhisper-large-ct2` (fp16) on faster-whisper/CTranslate2
(≥4.8.1 — Whisper align() fix), cuda auto-detect, env overrides only. No fallback model; empty
result = honest failure. **Amends blueprint §12.2** (drop whisper.cpp runtime + WhisperX layer).
**Consequences.** EN-heavy sources may transcribe worse (pin SEOSONA_PHOWHISPER_MODEL to a generic
CT2 repo per-run when needed); watchlist: Qwen3-ASR if its ForcedAligner adds Vietnamese.

## ADR-005 — GenVideo: prompt-first, paid-only, deferred

**Context.** Local LTX lane was proven working (Gate-0 clip) but costs 23.6GB + GPU contention;
owner priority is fastest production; paid API "decided later".
**Decision.** Engine #6 stays PROMPT-ONLY (director authors prompts + shotlists). Paid providers
(official accounts only) activate by adding a key; build order then follows
`6_SOP/LTX_BROLL_PLAN.md` (provenance sidecar → b-roll slot → QC gate → budget caps). GenVideo
remains a B-roll lane under SourceLock — never a renderer replacement.
**Consequences.** No GenVideo assets exist until a key decision; V2 Phase 4/6 unchanged.
