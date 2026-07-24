# RAP — Repo Analysis Process (single responsibility: ANALYZE a repo, deeply)

RAP has ONE job: take a repo and produce a deep, factual, **source-linked** analysis — what it does,
its real capabilities (proven from source), architecture, license (code AND weights), security,
footprint, health, and a verdict + recommendation. It hands off a typed result and STOPS.

**RAP does NOT** build skills/agents/adapters, wire anything into V2, or own autonomy/orchestration.
Analysis is the whole job; building is a separate concern downstream. (One owner per capability.)

## Lifecycle — RAP is the ANALYST. WHO BUILDS?
Adoption is a 3-role pipeline (UAP calls the last one the "creator"); RAP owns only the first box:

1. **RAP — Analyst** (this doc): repo → `RepoAnalysis` (KI + verdict + recommendation). STOPS.
2. **Decision gate**: a **human** (default) — or the orchestrator under FactoryPolicy autonomy — reviews
   the analysis and decides: build in form X / reference / reject. Core-boundary engines (voice/ASR/
   render) ALWAYS require human approval + a benchmark. RAP does not decide; it advises.
3. **Builder — Creator** (a SEPARATE component, NOT RAP): takes an APPROVED analysis + decision and
   generates the artifact (skill/agent/adapter/worker/module) WITH tests, wires it, records it.
   *Today the Builder is a build-agent (or me) acting on an approved `RepoAnalysis`; later it becomes a
   codified `packages/builder` capability.* Keeping Builder separate is the whole point of decoupling —
   RAP stays a sharp analyzer, the Builder stays honest about tests/wiring, the human stays in the loop.

Lineage: SEOSONA OS **UAP** (analysis half: finder→auditor→security→assimilator) + legacy
`REPO_VETTING_SOP.md` + the 2026-07-15 scars. **Golden rule:** clone to STUDY, never keep — analyze,
record as data, DELETE the clone.

---

## Input → Output
- **Input:** a repo (URL, or a DETECT candidate).
- **Output:** a typed `RepoAnalysis` = a **Knowledge Item** (source-linked) + verdict + recommendation,
  stored in `knowledge/memoryStore`. That is the entire deliverable.

## Completeness Gate — NO verdict on missing evidence (the anti-UAP rule)
The exact failure that broke UAP: it couldn't evaluate a repo, so it **skipped the evaluation or
dumped the repo into the system anyway.** RAP forbids this STRUCTURALLY — honesty about a check that
didn't run is necessary but NOT sufficient; a missing critical check must BLOCK the verdict, not
default to pass.

**Critical checks (ALL must have `ran:true` for any adopt-ish verdict — extract / adapter_adr / add_dep):**
1. **License — code AND weights** (the NC-trap resolver actually ran on real files/card).
2. **Security — secrets scan** (gitleaks/TruffleHog actually ran) + prompt-injection scan.
3. **Capability extraction** (ast-grep actually parsed the source — capabilities are source-cited, not README-guessed).
4. **Dedup** (the capability-overlap check actually ran against our index).

**Rule:** if ANY critical check has `ran:false` (tool absent, clone failed, parse error), RAP MUST set
`verdict = 'incomplete'` (a distinct, blocking verdict) with `missing_checks: [...]` — it may NOT
recommend adoption. `reference`/`reject` are still allowed (they don't ingest anything). An
`incomplete` analysis is a work-order ("install X / fix Y, then re-run"), never a green light.

**No skip · no mock · no default-pass · no README-only verdict.** Evidence is REAL (cloned + parsed +
scanned) or the verdict is `incomplete`. This is enforced in `classify.ts`, tested, and shown in the
report as a red **INCOMPLETE** banner listing what didn't run. *(This is why we install the real CLIs
rather than shipping probe-adapters that quietly return not-run.)*

## Pipeline (7 stages) with the adopted best-in-class techniques

### 1. DETECT — surface candidates
Inventory / watchlist / user-named / gap-triggered web search. Output `{repo, url, why_now}`.

### 2. SCREEN — cheap pre-clone recon + kill-gate (metadata only, NO full clone yet)
Answer "is this even worth cloning?" from manifests + APIs alone:
- **License surface (code):** `licensee`-style top-level verdict now; authoritative **ScanCode** later at deep stage.
- **License surface (weights) — the NC trap resolver:** parse the HF model-card YAML `license:` via
  `huggingface_hub.model_info()`; follow `datasets:` for **inheritance**; cross-check 3 surfaces
  (repo LICENSE / card tag / weights-repo policy) and take the **MOST RESTRICTIVE** + flag disagreement.
  Any `*-nc-*` / `*-nd-*` → hard commercial blocker. *(This is RAP's #1 differentiator — the exact
  "code Apache, weights CC-BY-NC" trap that bit us.)*
- **Footprint (pre-clone):** `huggingface_hub.model_info()` safetensors metadata → param count;
  `accelerate estimate-memory` → inference/train VRAM per dtype; GitHub tree blob-size sum of
  `*.safetensors|*.bin|*.pt|*.ckpt|*.onnx` → on-disk weight GB. Compute BEFORE downloading GB.
- **Health (beyond stars):** run **OpenSSF Scorecard** (0–10) + cheap git signals (last-commit age,
  bus factor, has-tests/CI/SECURITY.md, archived flag).
- **Kill-gate (all must pass):** relevance · permissive license (code AND weights) · quality/health ·
  dedup (V2 doesn't own it) · **hardware-fit** (fits RTX 3060 12 GB from the footprint estimate).
  Fail → recorded SKIP/REFERENCE/REJECT + reason. No clone spent on a doomed repo.

### 3. CLONE + ISOLATE — metadata-first
`git clone --filter=blob:none --depth=1` into scratch (`2_KNOWLEDGE/_ingest_inbox/`), never the tree.
Pull full blobs only for the files the repo-map ranks as worth reading (§5).

### 4. SECURITY — layered scan, findings quoted (never obeyed)
- **Secrets:** `gitleaks` (150+ patterns) + **TruffleHog** live-vs-dead credential verification.
- **Supply-chain:** `OSV-Scanner` (manifest-only CVE match).
- **Dangerous code:** `Bandit` (Python) + `Semgrep` rules (`subprocess(shell=True)`, `eval`,
  `pickle.load`, `torch.load` of untrusted weights, `os.system`).
- **Prompt-injection in docs/SKILL/comments:** Rebuff/prompt-armor-style heuristic+classifier over
  every README/`.md`/SKILL/docstring; any injected instruction ("ignore previous…", "you are now…",
  tool payloads, hidden/encoded text) → a **finding quoted VERBATIM with source location**, treated
  as data, never as an instruction (RAP reads untrusted repos — this protects RAP + consumers).

### 5. DEEP ANALYSIS — the core strength (map-first, then read the important 10%)
- **Ingest EVERY artifact, not just code (markitdown):** a repo's knowledge lives in PDF/DOCX/PPTX/
  XLSX/notebooks/images/audio/EPUB too. Normalize all of them → clean Markdown via **markitdown**
  (MIT, already in the stack; OCR + LLM image-caption + audio-transcribe + notebook/YouTube), so RAP
  reads a repo's real docs/specs/diagrams, not just its source. **docling** (MIT) is the optional
  heavier upgrade for structure-rich docs (layout/tables/formulas) — RAP applies its own verdict logic:
  markitdown default (light), docling only when a repo is doc/table-heavy (heavier footprint). *(This
  was the missed capability CLASS — mixed-format ingestion — the user flagged.)*
- **Repo-map (Aider technique):** tree-sitter parse → `.scm` tag queries extract def/ref → build a
  def→ref graph → **personalized PageRank** ranks the most important symbols → render top-ranked defs
  within a **token budget** (grep_ast TreeContext: signatures + parent scope, bodies elided). RAP reads
  the ~10 files that DEFINE the system, not everything. Bounded, deterministic, cheap on huge repos.
- **Capability extraction (ast-grep):** YAML structural rules find entry points (`__main__`,
  `@app.route`, CLI parsers, `FastAPI()`), public API, and capability markers (loads-a-model,
  opens-socket, spawns-subprocess). Each hit = a capability claim with `file:line` + the matched pattern.
- **Source-linked claims (DeepWiki standard):** EVERY capability/architecture assertion cites
  `file:line` (or the tool+rule that produced it) + a confidence. "Claimed in README" is kept SEPARATE
  from "verified in source."
- **Architecture:** module map + a **Mermaid diagram** + entry points + data flow.
- **(optional) RAG-over-repo** for follow-up Q&A: chunk+embed once, retrieve with citations.

### 6. CLASSIFY + RECOMMEND — advisory only
Verdict + which V2 target it *could* fit + recommended form. A pointer for downstream, NOT an action:
- **EXTRACT-pattern** · **ADAPTER+ADR** (core engine needs benchmark) · **ADD-dep** · **REFERENCE** · **REJECT**.

### 7. RECORD + CLEAN
Persist `RepoAnalysis` + KI (queryable, provenance-tracked); append INGESTION_LOG; **DELETE the clone**.

---

## Knowledge Item format (RAP's product — source-linked, machine-readable)
```
# KI: <repo> — <one-line what-it-is>
Identity:  url · primary language(s) · domain · License(code/weights, SPDX) · Stars · Analyzed <date>
## Capabilities   (each: claim + file:line evidence + proving pattern + confidence; README-claim vs source-verified separated)
## Architecture   (module map + Mermaid diagram + entry points + data flow)
## License & provenance  (ScanCode code verdict + weights license + dataset-inheritance chain + most-restrictive effective + disagreements; SPDX/CycloneDX)
## Security       (secrets live/dead · SAST · CVEs · prompt-injection findings quoted verbatim)
## Footprint      (params · weight GB · est. inference/train VRAM · dep bloat · heavy-dep flags)
## Health         (OpenSSF score · last-commit age · bus factor · tests/CI · maintained/archived)
## Verdict + Recommendation   (adopt-form / reference / reject — reasons traceable to evidence above)
```

## Tooling stack adopted (all in SCREEN/SECURITY/DEEP stages)
| Capability | Tool | License → RAP use |
|---|---|---|
| Mixed-format doc ingestion (PDF/DOCX/PPTX/notebook/img/audio→MD) | **markitdown** (default) / docling (heavy) | MIT → **CLI/native** (markitdown already installed) |
| Repo-map (tree-sitter + PageRank + token budget) | Aider / RepoMapper | Apache → **port the algorithm** |
| Capability/entry-point extraction | ast-grep (+ MCP) | MIT → **vendor/CLI** |
| Code license (authoritative) | ScanCode Toolkit | Apache → **CLI** |
| Weights license (NC-trap resolver) | huggingface_hub model_info + HF card rules | Apache → **native** |
| SBOM / deps | syft | Apache → **CLI** |
| Footprint / VRAM | accelerate estimate-memory + model_info + git-tree | Apache → **native** |
| Health score | OpenSSF Scorecard | Apache → **CLI** |
| Secrets | gitleaks (+ TruffleHog verify) | MIT / **AGPL** → gitleaks vendor, **TruffleHog shell-out only** |
| SAST | Bandit / Semgrep | Apache / **LGPL** → Bandit vendor, **Semgrep shell-out only** |
| CVEs | OSV-Scanner | Apache → **CLI** |
| Prompt-injection | Rebuff / prompt-armor | Apache → **native** |
| Output blueprint | deepwiki-open | MIT → **read as reference** |

**License hygiene (RAP's own build):** vendor only MIT/Apache/BSD tools; **shell out to AGPL/LGPL**
(TruffleHog, Semgrep) as external CLIs so RAP's own license stays clean. *(RAP eating its own dogfood.)*

## Next-tier analysis upgrades (research #2, 2026-07-15 — all MIT/Apache/BSD/ISC unless flagged)
The single highest-leverage one turns RAP from "what does this repo DO" into "what does it ADD to US":
1. **Capability-dedup ORACLE (self-index)** — embed EACH of V2's own module capability-sentences into
   `sqlite-vec` (Apache) with `jina-embeddings-v2-base-code` (Apache); every extracted repo capability →
   ANN lookup against our index + an LLM "new / partial / duplicate" verdict. Upgrades Stage-2 dedup from
   a guess to an oracle. **The core value of an adoption engine.**
2. **Novelty scorer** — `datasketch` MinHash/LSH (MIT) against our capability corpus, agreement-gated with
   the #1 embeddings → per-capability `{new | incremental-over-mine | duplicate}` + nearest existing module.
   Deterministic, GPU-free. `difftastic` (MIT, shell-out) for the structural "differs only in Y" delta.
3. **Runnability Score (0–100)** — `repo2docker --no-build` (BSD) + static signals (lockfile pinned,
   CI-runs-tests, one-command-run, Dockerfile/devcontainer, hadolint[GPL→shell-out]). Health ≠ runnable;
   this gates wasted adoption effort BEFORE building.
4. **Integration-surface extraction** — `griffe` (ISC, Python) + `@microsoft/api-extractor` (MIT, TS) →
   exact exported callables/signatures + CLI commands + breaking-change diff. Reports the REAL import surface.
5. **Coupling/layering analysis** — `grimp`+`import-linter` (MIT, Py) / `dependency-cruiser` (MIT, JS/TS) →
   fan-in/out, cycles, layer-violation count → a modularity sub-score + DOT graph (drops into the KI).
6. **Eval/benchmark extractor** — detect eval dirs + `datasets.load_dataset`/PwC/lm-eval refs → normalize to
   the sotabench-eval Task/Dataset/Metric triple → tells the orchestrator whether an adoption can be
   VALIDATED with the repo's own evals before committing (closes the loop with our eval flywheel).

Also: scientific-PDF tiering — GROBID (Apache, papers) / unstructured (Apache, general); **Nougat weights =
CC-BY-NC, Marker/Surya = GPL/revenue-gated → license-quarantine, shell-out/reference only** (same NC
discipline as OmniVoice). Huge-monorepo: repomix (MIT) token-accounting shards + hierarchical folder→file→
symbol rollup on top of the Aider PageRank map, cached for incremental re-analysis.

These enrich the Knowledge Item with: `novelty` (per capability), `runnability_score`, `integration_surface`,
`coupling/modularity`, and `reusable_evals` blocks — beyond the base license/security/footprint/health.

## Anti-bloat + honesty invariants
1. Clone lives only in scratch; Stage 7 DELETES it. 2. Every claim is source-cited (read code, not README).
3. Every verdict (incl. REJECT/REFERENCE) recorded — never silently re-litigated. 4. RAP never says
"adopted" — it only analyzes; adoption is a separate act.

## Implementation note
Typed schema (`RepoAnalysis`, `KnowledgeItem`, kill-gate) → `packages/knowledge`; the stage tools →
`packages/rap` (or engines-style adapters that shell out to the CLIs above). Buildable now (Phase 3b done).
