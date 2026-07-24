# SEOSONA Video OS V2 — System Record (paste-ready for Google Doc + Sheet)

Single authoritative record of the V2 system as built. **Part 1** is prose/tree for the Blueprint
Doc; **Part 2** is tables for the tracker Sheet. Repo: `D:\SEOSONA AI\seosona-video-os` (git, 5 commits).
Legacy `D:\SEOSONA AI\SEOSONA Video` = READ-ONLY reference + engine host. Date: 2026-07-15.
Verified: `npm test` = 280/280 green.

---
# PART 1 — for the Google Doc (Blueprint)

## What V2 is
An autonomous video-creation OS. Not a one-shot pipeline: a policy-governed loop (OODA) that decides
what to produce, runs it through typed contracts with honest failure, and learns from its own output.
SEOSONA owns the core (contracts, timeline truth, state, creative, knowledge); every external engine —
including the legacy factory — is invoked only through adapters.

## Folder tree (12 workspaces)
```
seosona-video-os/
├── packages/
│   ├── contracts/     Zod schemas = every data contract (Job, MediaRef, ResearchBundle, ScriptSpec,
│   │                  TimelineIR, ArtifactSet, RenderReceipt, Evaluation, PublishReceipt, ApprovalDecision,
│   │                  IngestResult, AnalysisReport, PerformanceSnapshot, MemoryRecord, LearningDecision,
│   │                  NarrativeBible, PersonalizationProfile, PromptPackage, FactoryPolicy, Event)
│   ├── timeline-ir/   TimelineIR — single render truth (rational timebase, validate, contentHash, diff)
│   ├── engines/       Adapters over the read-only legacy engines: TTS(OmniVoice,consent-gated),
│   │                  ASR(PhoWhisper), media(ffmpeg argv), captionSync, renderReceipt
│   ├── shared/        config · logger · errors · telemetry · ids · runContext · CredentialsProvider
│   ├── creative/      brandKit · archetypes · sceneGrammar · template/prompt registries
│   ├── storage/       ObjectStore + FsObjectStore (content-addressed)
│   ├── knowledge/     memoryStore · learningFlywheel · knowledgeRegistry (Knowledge/Memory/Learning Core)
│   └── agents/        AgentRegistry — 10-role roster, typed, validated (no dangling bindings)
├── services/
│   ├── control-plane/ Job state machine (fail-closed) · event ledger · artifactStore · paidAssetGuard
│   ├── orchestrator/  Factory Brain: OODA runTurn · policyEngine(L0–L3) · circuitBreaker · queue · scheduler
│   └── workers/       Pipeline stages: research·script·packaging·ingest (built) + analyze·timeline·
│                      render·qa·publish·analytics (scaffold, typed I/O, NotImplemented)
├── apps/studio/       Human review/approval UI (placeholder; declares JobView·ReviewDecision boundary)
├── config/            factory_policy.json · .env.example (engine-host contract)
├── docs/              ARCHITECTURE.md · LEGACY_ORGAN_MAP.md · SETUP.md · phase gate docs · evidence/
└── runs/              (gitignored) runs/<job_id>/{intake,artifacts,events.jsonl} + _inbox/
```

## The layers (top to bottom)
1. **Autonomy** (`orchestrator`) — the OODA loop. Observe metrics+policy → Orient (learnings+explore split)
   → Decide (budget-bounded batch) → Act (create+enqueue jobs). Governed by FactoryPolicy (L0 manual →
   L3 full), kill-switch, circuit breaker, budget caps. NEVER fakes a render: a job hitting a scaffold
   worker is recorded `blocked_on` on the ledger.
2. **Control** (`control-plane`) — per-job state machine (intake→…→published), fail-closed transitions,
   append-only event ledger, content-addressed artifact store, paid-asset guard (no paid asset before
   script approval).
3. **Work** (`workers`) — one worker per pipeline stage; deterministic where possible, honest stubs where
   an engine/LLM is needed.
4. **Engines** (`engines`) — adapters wrapping legacy OmniVoice / PhoWhisper / FFmpeg / HyperFrames.
   0 silent fallback: fail → throw/None/[].
5. **Core data** (`contracts`, `timeline-ir`) — schemas make state legible; TimelineIR is the one render truth.
6. **Creative + Knowledge** (`creative`, `knowledge`) — brand/archetype/scene rules; memory + learning loop.
7. **Foundation** (`shared`, `storage`, `config`) — cross-cutting primitives, content-addressed I/O, policy/env.

## Data flow (one artifact per edge)
Intake→**JobContract** · Ingest→**MediaRef** · Analyze→**AnalysisReport** · Research→**ResearchBundle** ·
Script→**ScriptSpec**(claim-traced) · Approve→**ApprovalDecision** · Plan/Timeline→**TimelineIR** ·
Render→**ArtifactSet + RenderReceipt** · Evaluate→**Evaluation**(Technical/Craft/Policy) · Review→**ApprovalDecision** ·
Publish→**PublishReceipt** · Analytics→**PerformanceSnapshot** → learn → **LearningDecision → MemoryRecord** (loop).

## In / Out
- **Input**: a JobContract (from topic/URL/brief) enters via control-plane; sources are MediaRefs in the ObjectStore.
- **Output**: content-addressed artifacts in ObjectStore + a per-job `runs/<job_id>/` dir. Never written to CWD.
- **Inbox**: `runs/_inbox/` drained by the orchestrator queue (per-item isolation + dead-letter).

## Locked engine decisions (ADR-001…005)
Renderer=HyperFrames + FFmpeg-only media · Voice=OmniVoice ONLY (CC-BY-NC weights, owner-accepted, no
backup) · ASR=PhoWhisper-large-ct2 ONLY (whisper.cpp + WhisperX rejected) · GenVideo=prompt-only/paid-later
· Lipsync/avatar=retired. Adding any engine requires a new benchmark + ADR.

---
# PART 2 — for the Google Sheet (tracker)

## Tab: Phase status
| Phase | Gate | Status | Evidence |
|---|---|---|---|
| P0 Inventory truth | matrix + 10 fixtures + ADR + benchmark | ✅ PASS | docs/v2_phase0/ |
| P1 Contracts/Core | 1 fixture thru typed contracts; fail-closed | ✅ PASS | commit 0a0e807 |
| P2 Research/Content | 100% claim-trace; approve before paid | ✅ PASS | commit b1c2c1b |
| P3 Audio/Render | caption sync + audio QA + receipt + 0 fallback | ✅ PASS | commit 8d2f6de + live gate |
| P3b Render adapter | TimelineIR→HyperFrames + deterministic rerender | ⬜ NEXT | renderWorker scaffold |
| P4 QA/Review | 8/10 reviewer-approved | ⬜ NEEDS USER | — |
| P5 Publish/Learning | real publish receipts + metrics | ⬜ NEEDS USER | — |
| P6 Expansion | GenVideo/scale | ⬜ deferred | — |

## Tab: Module registry (input → output · status · phase)
| Module | Layer | Input | Output | Status |
|---|---|---|---|---|
| contracts | core | — | zod schemas/types | BUILT |
| timeline-ir | core | ShotPlan/assets | TimelineIR | BUILT |
| control-plane | control | Command+Event | Job state + ledger | BUILT |
| orchestrator/policyEngine | autonomy | FactoryPolicy+Job | gate decision | BUILT |
| orchestrator/circuitBreaker | autonomy | run outcomes | trip/reset | BUILT |
| orchestrator/queue | autonomy | inbox items | drained + dead-letter | BUILT |
| orchestrator/factoryTurn | autonomy | metrics+policy | TurnReport | BUILT (scaffold Act boundary) |
| orchestrator/scheduler | autonomy | — | run trigger | PARTIAL (Cron scaffold) |
| agents/registry | agents | — | 10 AgentDefinitions | BUILT |
| knowledge/memoryStore | knowledge | MemoryRecord | append-only ledger | BUILT |
| knowledge/learningFlywheel | knowledge | PerformanceSnapshot[] | LearningDecision[] | BUILT |
| knowledge/knowledgeRegistry | knowledge | records | lookup/validate | BUILT |
| creative (brandKit/archetypes/sceneGrammar/registries) | creative | brief | typed creative data | BUILT |
| storage/ObjectStore | foundation | file | sha256 address | BUILT |
| shared (config/logger/errors/telemetry/ids/runContext/creds) | foundation | env | primitives | BUILT |
| engines/ttsAdapter | engine | text+consent_id | wav | PARTIAL (needs engine host) |
| engines/asrAdapter | engine | wav | word timings | PARTIAL |
| engines/mediaEngine | engine | media file | probe/loudness/argv | BUILT (needs ffmpeg) |
| engines/captionSync | engine | script+asr | sync score | BUILT |
| workers/research·script·packaging·ingest | work | prior artifact | next artifact | BUILT |
| workers/analyze·timeline·render·qa·publish·analytics | work | typed | typed | SCAFFOLD |
| apps/studio | ui | control-plane state | review decision | SCAFFOLD |
| **totals** | | | | **BUILT 20 · PARTIAL 3 · SCAFFOLD 7** |

## Tab: Engine decisions (ADR)
| Boundary | Choice | Rejected | ADR |
|---|---|---|---|
| Renderer | HyperFrames + FFmpeg-only | Remotion(review), CapCut | 002 |
| Voice | OmniVoice ONLY (NC-accepted, no backup) | VieNeu, F5-VN, edge-tts | 003 |
| ASR | PhoWhisper-large-ct2 ONLY | whisper.cpp, WhisperX(NC), medium(defective) | 004 |
| GenVideo | prompt-only, paid-later | local LTX (too heavy) | 005 |
| Lipsync/avatar | retired | MuseTalk/SadTalker/LivePortrait | — |

## Tab: Sheet drift to fix (IMPORTANT)
The Sheet `V2_Core_Engine` tab still says whisper.cpp/WhisperX=ADOPT and VieNeu=CONDITIONAL —
this CONTRADICTS ADR-003/004 (benchmark-decided). Update that tab to match Part 2 above.

## Cross-references (source of truth in-repo)
- Structure+dataflow: `seosona-video-os/docs/ARCHITECTURE.md`
- Legacy→V2 organ map: `seosona-video-os/docs/LEGACY_ORGAN_MAP.md`
- Lessons learned: `docs/v2_phase0/LEGACY_LESSONS.md`
- Capability matrix + ADR + fixtures + repo adoption: `docs/v2_phase0/`
- Setup/env: `seosona-video-os/docs/SETUP.md`
