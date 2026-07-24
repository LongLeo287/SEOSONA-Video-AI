# Legacy → V2: Lessons Learned (review, học hỏi, rút kinh nghiệm)

What the legacy factory (`D:\SEOSONA AI\SEOSONA Video`) taught us, and the EXACT V2 design choice
each lesson forced. Every lesson is a real scar (test failures, user reports, this session's audits),
not a hypothetical. This is the rationale layer behind ARCHITECTURE.md + the ADRs.

## Part A — Failures to design AGAINST (each → a V2 guarantee)

| # | Legacy failure (real) | Root cause | V2 guarantee |
|---|---|---|---|
| 1 | `quality_scorer` gave PASS too easily; silent engine fallbacks hid breakage | success measured by "did it render", not by evidence | **Fail-honest core**: `Evaluation` schema REJECTS `verdict:'pass'` with empty/failed checks; voice returns `None`, ASR returns `[]`, adapters `throw EngineFailure` — 0 silent fallback (proven by tests) |
| 2 | `4_BRAIN` mixed orchestration + render + content; two LLM cascades; overlapping `workflow_router` | grouped by "kind of thing", no ownership boundary | **One owner per capability**: boundary-based packages; SEOSONA owns contracts/timeline/state/creative; engines only behind adapters |
| 3 | root `requirements.txt` (stale dup) would reinstall removed engines via `seosona_doctor` | duplicated source of truth | **Single source of truth**: root req is a pointer; `FactoryPolicy`/config are one schema; engine choice is a closed ADR |
| 4 | stray output folders (`D:\d`, `test_carousel_v2`, `selfshot`) littered the tree | relative paths resolved against CWD | **Addressed I/O**: content-addressed `ObjectStore` + injected `runs/<job_id>/`; never write to CWD (STRUCTURE.md rules) |
| 5 | VN ASCII substring collisions (`ai`∈`hai`, `seo`∈`seoul`) — recurred 6+ times | `kw in text` on short tokens | **Whole-token matching** everywhere (captionSync, archetypeRouter); real VN word-seg (underthesea) on the P1 adoption list |
| 6 | import-only guard (try wraps import, body unguarded) — 4× broke degrade-to-None | guard scope wrong | **Typed adapters** with explicit `probe()` + guarded body + honest throw |
| 7 | one malformed item crashed the whole batch — 5× | unguarded `float()/get()` in a loop | **Per-item isolation** (queue/dead-letter in orchestrator + control-plane) |
| 8 | `HH:MM:SS,mmm` overflow when a fraction rounded up | fields computed independently | **Rational timebase** in TimelineIR; round-to-ms-then-divmod |
| 9 | engine sprawl (many TTS/ASR, dead `if engine==` branches) | added engines without a decision gate | **Closed engine decision**: adding an engine needs a new benchmark + ADR; no dead branches |
| 10 | license blind spots (OmniVoice mislabeled Apache; WhisperX vi-aligner is NC) | license not tracked per engine | **License recorded per engine** (ADR-003/004 + MODELS.md); policy QA carries the NC flag onto every voiced artifact |
| 11 | stubs called "integrated" (BytePlus stub, analytics TODO, dry-run publish) | optimism over evidence | **Honest status**: `NotImplementedError{module,contract,phase}`, no fabricated returns; BUILT/PARTIAL/SCAFFOLD labels everywhere |
| 12 | autonomous loop committed to `main` and swept manual git edits | ambient loop + shared working tree | **Separate V2 repo**, no ambient loop; orchestrator actions are deliberate + logged |
| 13 | machine-specific persisted paths broke portability | hardcoded absolute paths | **Injected roots** via env contract (`SEOSONA_LEGACY_ROOT`, `STORE_ROOT`…); no machine-path literals in modules |
| 14 | metadata gate couldn't see craft/content quality → bad videos scored 100 | one scalar gate | **QA split** Technical / Craft / Policy scorecards; vision judge = evidence NOT approver; human owns release |
| 15 | heavy local engines fought the speed goal (LTX 23GB, lipsync 22GB, GPU contention) | "adopt because it works" without a cost/fit gate | **Right-sized adapters**: engines behind adapters, heavy/paid lanes explicit + deferred, hardware-fit is a decision criterion |

## Part B — What legacy got RIGHT (preserve verbatim in V2)

These are proven primitives — the rebuild keeps them, only re-homed behind contracts:
- **Single render chokepoint** (`native_composer`) → one renderAdapter, never scattered ffmpeg.
- **Karaoke word-level captions** + **display↔pronunciation separation** → ScriptSpec spoken_lines vs display_words; caption sync from ASR word timing (E2E-proven, 0.94).
- **Effect library + VIDEO_CRAFT_RULES** → `creative/sceneGrammar` + seed craft-rule MemoryRecords.
- **Content-addressed instinct** (checksum artifacts) → generalized into `ObjectStore`.
- **Circuit breaker + STOP kill-switch** (`loop_guard`) → orchestrator circuit breaker + `FactoryPolicy.kill_switch`.
- **Layered subprocess timeouts** (`queue_processor` kill-tree) → orchestrator queue timeouts; don't add naive per-call timeouts that break long renders.
- **Recall-before-re-derive** (`knowledge_graph`) → `knowledge/knowledgeRegistry` + `memoryStore`.
- **Light-brand-only discipline** (#2A5BDA/#E2724D, no dark mode) → `creative/brandKit` frozen constants.
- **Graduated autonomy** (`factory_policy.yaml` L0–L3 + budget + explore-ratio) → `FactoryPolicy` schema, the OS's safety governor.
- **Traceability gate** (no fabricated numbers; every stat → a claim) → ScriptSpec zod refine: factual beats must reference existing claim_ids (P2-proven).

## Part C — The meta-lesson

Legacy failed not on craft (its videos are good — the render primitives are excellent) but on
**trust and boundaries**: you couldn't tell what was real vs stubbed, who owned a capability, or
whether a PASS meant anything. V2's whole shape is a response to that one lesson — **contracts make
state legible, honest failure makes quality legible, and boundaries make ownership legible.** Keep
the craft, fix the trust.

## Provenance
Scars sourced from: `LEGACY_CAPABILITY_MATRIX.md` (§Known failure classes), the auto-memory bug-class
notes (vn-substring-collision, import-only-guard, batch-item-resilience, timestamp-overflow,
no-recreate-deprecated-systems, autonomous-loop-git-race, stray-folders-path-mangling), the
2026-07-14 consolidation audits, and the ADRs. Every "V2 guarantee" above is enforced by a test or a
schema in `D:\SEOSONA AI\seosona-video-os` (or is on the labeled build backlog).
