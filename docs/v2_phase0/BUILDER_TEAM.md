# Builder Team (the Creators) — Team 2 of the repo-upgrade flywheel

The second team. It does NOT analyze repos (that's RAP). It takes an **approved** analysis + the
user's decision and BUILDS the real thing — a skill, agent, tool, pipeline, SOP, framework, or engine
adapter — with tests, wiring, and a build report. RAP = analyst; Builders = creators; the **user sits
in the middle** and stays in control.

## The flywheel (who does what)
```
TEAM 1  RAP (Analyst)         repo → RepoAnalysis (KnowledgeItem + verdict + recommendation) → STOP
   ↓  report
YOU     Decision gate          read · approve · select the form · EDIT the plan · or reject
   ↓  approved plan
TEAM 2  Builders (Creators)    bring the right artifact out → build + test + wire + report → record
   ↓  build report
YOU     Review                 accept / request changes  (core engines: + benchmark before default)
```
RAP never triggers a Builder. Only YOUR approved decision does. Separation of concerns = safety.

## The team roster (one specialist per artifact FORM you named)
The Builder Router reads your decision `{form, target, edits}` and dispatches ONE specialist:

| You choose form | Builder | Produces (V2 home) | Honest output |
|---|---|---|---|
| **skill** | SkillBuilder | craft rule / scene-grammar entry / `.agents` skill (`packages/creative`) | rule + a test |
| **agent** | AgentBuilder | `AgentDefinition` + registry entry (+ worker binding) (`packages/agents`) | BUILT or PLANNED if binding not ready |
| **tool** | ToolBuilder | a `packages/shared` util or a CLI probe-adapter | BUILT + test |
| **pipeline** | PipelineBuilder | a `services/workers` worker or a stage sequence | BUILT with tests / honest SCAFFOLD |
| **SOP** | SOPBuilder | a `docs/*.md` procedure wired to the playbook index | doc + cross-links |
| **framework/module** | FrameworkBuilder | a new `packages/*` module | BUILT/SCAFFOLD labeled |
| **engine adapter** | AdapterBuilder | `packages/engines` adapter + **draft ADR** | PARTIAL until benchmark → then DECIDED |
| **prompt/template** | PromptBuilder | `PromptPackage` / template registry entry (`packages/creative`) | typed entry + test |

## What every Builder does (the same 6 steps, honest)
1. **Intake + RE-ANALYZE (build-focused)** — read `{RepoAnalysis, KnowledgeItem, your decision + edits}`,
   then do the Builder's OWN deeper pass on the EXACT target: RAP analyzed the repo generally; the
   Builder re-reads the specific files/functions it will extract, works out how to adapt them to V2's
   contracts + conventions, and plans the artifact. (RAP's KI + "Take" section is the map, license
   already cleared; the Builder digs the precise hole.) If you gave a direct order instead of a report,
   the Builder analyzes against that order. This is the "nhận lệnh → đọc report hoặc lệnh → phân tích
   lại → build đúng phân loại" step.
2. **Generate** — produce the artifact in the chosen form, conforming to V2 contracts + conventions
   (adjusts the extracted logic to fit — "học/bóc tách/tạo/điều chỉnh").
3. **Test** — write real tests. BUILT = tests pass; otherwise an honest SCAFFOLD boundary
   (`NotImplementedError`), never a fake.
4. **Wire** — connect it to the real V2 path that uses it (never orphaned — the legacy scar).
5. **Report** — a build report for you: what was built, tests + result, where it's wired, what was
   dropped/deferred. On a branch/diff you can review.
6. **Record** — a typed `GeneratedArtifact {adoption_ref, form, target, path, status, tests_ref, wired}`
   → `knowledge/memoryStore`; append INGESTION_LOG. (RAP already deleted the clone.)

## The builder ENGINE — how builders generate correct, tested, wired code (research 2026-07-15)
Central insight: a strong builder is a **two-layer deterministic engine** with the LLM *on top*, never
in the byte-level edit. The LLM writes the PLAN and the CODEMOD; deterministic layers do the file writes.

**Layer 1 — Scaffold (new files):** template → typed answers → files, on a **staged virtual FS** (Nx
`Tree` model: all mutations in memory, atomic flush only on success = free dry-run + reviewable diff +
never-clobber via `KeepExisting`/`ThrowIfExisting`).
**Layer 2 — AST-inject (wire it in — the hard part):** insert imports/exports/registry entries into
EXISTING files *semantically*, **anchored + idempotent** (a `// <builder:registry>` anchor + a
`skip_if`/"already present?" guard → re-run is a no-op). `ts-morph` (MIT) for type-aware TS inserts;
`magicast` (MIT, recast-based) for formatting-preserving config/array/object edits; Hygen `inject` for
text-anchor cases. **Never regex-append into source.** Most generator breakage is bad WIRING, not bad files.

**The generate→verify loop (Aider/Sweep model):** architect model *plans* → editor model emits **diffs**
(never whole-file), restricted to an **editable-file allowlist** → typecheck+lint+**tests** → feed
failures back → fix → repeat until green or budget. **Green before you ever see it** (Sweep). For a PORT,
the LLM writes a **ts-morph codemod** (replayable/auditable), not pasted code (Codemod.com/OpenRewrite model).

**Three-tier tests (the honesty gate):** (1) **golden/characterization** tests snapshot the SOURCE repo's
behavior → prove the extracted artifact is semantically equivalent (the #1 test for "ported from repo X");
(2) **fast-check property tests** (MIT) for invariants, with the shrunk counterexample fed into the fix
loop; (3) validated LLM example tests. Golden = fidelity, property = invariants, LLM = readable specifics.

**Reviewable by default:** builders never write to main — emit a **git branch + draft PR** with an honest
report (what scaffolded, what injected + anchors hit, test pass/fail counts, coverage, skipped/failed
steps — no green-washing). Rollback = don't merge.

**Artifact shapes each builder emits (current standards):**
- SkillBuilder / AgentBuilder → a **`SKILL.md`** dir (YAML `name`+`description` [the trigger-matcher —
  highest-leverage field], `scripts/`+`references/`+`assets/`, progressive disclosure) and/or a typed
  **LangGraph node** (agent = node, typed state dict) for a runtime worker.
- PipelineBuilder → a **data-defined stage** (Dagster/Prefect asset model: declare typed in/out + deps,
  DAG derives itself — mirrors legacy `4_BRAIN/pipeline_dag.py`) + AST-inject to register it in the DAG.
- AdapterBuilder → a `packages/engines` adapter (probe/execute/healthcheck/receipt) + draft ADR.

**Tooling stack (all MIT/Apache/BSD — safe to vendor):** ts-morph · magicast · Hygen/Plop · Nx devkit
(`Tree`) · jscodeshift/GritQL · fast-check · Aider(loop) · OpenHands SDK · LangGraph/CrewAI · Dagster/
Prefect(patterns) · OpenRewrite(recipe-as-data discipline) · self-improving-agent (draft-PR reference).

## Canonical Template System — ONE mold per form (every creation identical, maintainable)
The rule that makes the whole team manageable: **a Builder never free-forms. It fills the ONE golden
template for that form.** So every skill is structurally identical to every other skill, every agent to
every agent — and maintenance/upgrade means learning ONE shape, not N snowflakes. Grounded in the best
authoring conventions learned from repos (Claude SKILL.md, LangGraph typed nodes, Dagster assets, Nx
generator/migration split).

### The Template Registry (`packages/builder/templates/`, versioned)
One golden template per form, each a fixed skeleton + required fields + a MANDATORY test + a defined
wiring anchor + a doc stub. A Builder can only produce an artifact that conforms to its template.

| Form | Golden template (fixed skeleton) | Wiring point | Grounded in |
|---|---|---|---|
| **skill** | `<name>/SKILL.md` (YAML `name`,`description`[what+WHEN=trigger],`license`,`allowed-tools`; body) + `scripts/` + `references/` + `assets/` + `<name>.test.ts` | skill index | Claude Agent Skills |
| **agent** | `agents/<role>.ts` (typed `AgentDefinition`: id,role,description,inputs,outputs,binding,status) + `<role>.test.ts` | `agents/roster.ts` (AST-inject) | AgentDefinition + LangGraph node |
| **tool** | `shared/<tool>.ts` (pure typed util OR CLI probe-adapter) + `<tool>.test.ts` | `shared/index.ts` export | — |
| **pipeline** | `workers/<stage>.ts` (typed in→out stage + worker fn, data-defined) + `<stage>.test.ts` | DAG/stage registry (inject) | Dagster/Prefect asset |
| **SOP** | `docs/SOP_<NAME>.md` — FIXED sections: Purpose · Trigger · Steps · Gates · Evidence · Owner · Review-date | SOP index link | legacy SOP shape |
| **framework** | `packages/<name>/` = `package.json` + `src/index.ts` + `README.md` + `test/` | workspaces + tsconfig paths (inject) | Nx package model |
| **adapter** | `engines/<name>Adapter.ts` (probe/execute/healthcheck/receipt) + `<name>-adapter.test.ts` + **draft ADR** | engines registry | V2 adapter contract |
| **prompt** | `PromptPackage`/template registry entry (typed) + test | creative registry | — |

### Three properties that make it maintainable + upgradeable
1. **Uniformity** — every artifact of a form shares one skeleton, one field set, one test location, one
   wiring anchor. You learn it once; you find anything by convention.
2. **Versioned templates + migrations (Nx model)** — a template is `v1`. Upgrading it to `v2` ships a
   **codemod migration** that rewrites ALL existing instances of that form to the new shape (generators
   create, migrations upgrade — never a manual sweep). This is the "dễ nâng cấp": upgrade the mold once,
   migrate every artifact automatically.
3. **Conformance lint** — a check (`builder:conform`) that ANY artifact (freshly generated OR existing)
   matches its template: required fields present, test file exists + passes, wired at the anchor, docs
   stub present. Runs in CI. Non-conforming = fail. Uniformity is ENFORCED, not hoped.

### How a Builder uses it
Intake → pick the form's golden template → fill its blanks from the extracted+adapted logic (never add
ad-hoc structure) → Layer-1 scaffold the template files → Layer-2 AST-inject at the fixed anchor →
generate the mandatory test → run `builder:conform` + tests → draft-PR + report. Result: the artifact is
indistinguishable in SHAPE from every prior artifact of that form.

## Recognition & the NO-ORPHAN guarantee (does the system auto-notice what we add?)
The legacy scar: modules built but never wired (LTX/seedance, talking-head had 0 call sites). V2 answers
this STRUCTURALLY — "recognition" = registration in a typed registry, and wiring is enforced, not hoped:

1. **Registries are the recognition surface** — a thing exists to V2 only when it's registered: agents →
   `agents/roster.ts`, tools → `shared/index.ts`, workers/stages → the DAG/stage registry, engines →
   engines registry, analyses/artifacts → `knowledge/memoryStore`. Explicit, not magic folder-scanning
   (implicit auto-wiring is exactly what broke silently in legacy).
2. **The Builder auto-wires (Layer-2 inject)** — every Builder-created artifact is registered at its
   anchor as part of creation. Creation without wiring is impossible in the happy path.
3. **conform-lint ENFORCES wiring** — `builder:conform` fails an artifact that isn't wired at its anchor;
   run in CI, an unwired artifact cannot merge.
4. **Connectivity audit (to add) — the global guarantee** — a `v2:connectivity` check (mirroring legacy
   `video_integration_audit` + the orphaned-pass detector) that walks every registry and asserts each
   registered capability is REACHABLE from an entry point (no orphans), and that no capability file exists
   UNregistered (no dead code). Runs in CI → dropping/orphaning something fails the build. **This closes
   the "mất kết nối / bỏ ở đâu đó" gap for good.**

So: Builder-made things auto-register + are enforced-wired; manual additions are caught by the
connectivity audit. Nothing sits dead and unnoticed once the audit is in CI.

## Governance (you stay in control)
- **Before**: nothing is built until YOU approve the analysis, pick the form, and (optionally) edit the
  plan. This is the "đọc, duyệt, chọn, sửa" gate.
- **During**: Builders emit BUILT-with-tests or honest SCAFFOLD — never "done" without tests + wire.
- **Core boundary**: an engine adapter (voice/ASR/render/genvideo) can be BUILT, but it does NOT become
  the DEFAULT until a benchmark + a second approval (an ADR). *(That decision cost a benchmark this session.)*
- **After**: you review the build report; accept or request changes.
- **Autonomy (optional, later)**: under FactoryPolicy L2+, NON-core artifacts (skills, SOPs, agent defs)
  can auto-wire after tests pass; core always waits for you.

## Today vs later
- **Today**: a Builder is a build-agent (the kind already used this session) or me, acting on ONE approved
  `RepoAnalysis`. Fully functional now — you approve, I dispatch the right builder, it produces + tests + wires.
- **Later**: codified as `packages/builder` (a Builder Router + the specialist builders) so the team is a
  first-class V2 capability the orchestrator can run under policy.

## Boundary with RAP (do not blur again)
RAP: analyze → report. Builders: build → report. The user: decide, between them. Three owners, three
responsibilities. RAP has no build power; Builders have no analysis power; neither decides — you do.
