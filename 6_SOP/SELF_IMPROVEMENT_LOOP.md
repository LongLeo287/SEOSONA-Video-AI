# 🔄 SEOSONA Self-Improvement Loop (SIL) — how the system learns & upgrades itself

The ONE governing loop for **analyzing → learning → ingesting → creating → upgrading**
the SEOSONA Video **system + factory**. This is the **umbrella** that ties the existing
pieces together — it does **NOT** duplicate them. Each stage links to the doc/tool that
already owns the detail.

> Scope split (no overlap):
> - **This doc** = the *capability* loop — how we absorb an external repo/idea into the system.
> - [`AUTONOMOUS_FACTORY_LOOP.md`](AUTONOMOUS_FACTORY_LOOP.md) = the *production* loop — how the
>   factory makes better VIDEOS from real performance (OBSERVE→ORIENT→DECIDE→ACT). Different loop.
> - [`REPO_VETTING_SOP.md`](REPO_VETTING_SOP.md) = the DECIDE-stage checklist (owned there).
> - [`EVAL_FLYWHEEL.md`](EVAL_FLYWHEEL.md) = the VERIFY-stage qualitative judge.

Learned from **SEOSONA OS — Universal Assimilation Pipeline** (`~/.seosona/docs/03_uap_pipeline.md`:
finder → auditor → **security** → assimilator → creator). Two disciplines we adopt from it and
were missing here: **(1) factual source-code analysis (ignore READMEs)** and **(2) a security
scan + quarantine before anything is brought in.**

---

## The stages (1–9 = per item; 10 = periodic upkeep)

| # | Stage | What happens | Uses (existing — don't reinvent) |
|---|-------|--------------|----------------------------------|
| 1 | **DISCOVER** | Find candidate repos/ideas/upgrades | `2_KNOWLEDGE/REPO_WATCHLIST.md`, `REPO_INVENTORY.md`, `.agents/skills/video-discovery`, `scripts/check_freshness.py`, `6_SOP/UPGRADE_BACKLOG.md` |
| 2 | **ANALYZE (factual + DEEP)** | **Clone + read the ACTUAL source** (entry points, configs, core modules) — NOT the README. Then **DIG**: extract the HIDDEN value (see below). Bulk/unknown → route via SEOSONA OS UAP | OS UAP `02_auditor`; Explore agent |
| 2b | **DEEP EXTRACTION (mandatory)** | A whole-repo "REFERENCE/dup" verdict is NOT the end — repos hide adoptable specifics. Before concluding, list the top extractable items: exact **config values / magic numbers / thresholds**, **prompt text + few-shot examples**, **recipes/snippets**, **data files / lexicons / catalogs**, **edge-case & error handling**, **undocumented features**, **schemas/field lists**. For EACH: ADOPT (where it plugs in) or SKIP (why). "Dup" applies per-item, not to the whole repo. | researcher persona; `capability-analyst` |
| 2c | **SCALE the dig to repo SIZE (don't pretend 1 agent read a giant repo)** | **MAP first** (`scout`: file count, LOC, languages, top dirs). Then route: **Small** (≤~60 files / ≤~15k LOC) → one agent reads it fully. **Big** → `gitingest`/`markitdown` make a full-text DIGEST, then **FAN-OUT** one agent PER subtree/module (src/, plugins/, skills/, data/, configs/) → synthesize their gem lists (no single agent can hold a huge repo). **Huge / many repos** → **DELEGATE to SEOSONA OS UAP** (clones + factual source analysis + AAAK at scale) and pull the KI. State the coverage honestly ("read 8/8 modules" vs "sampled"). | `scout`; `gitingest`; OS UAP |
| 3 | **SECURITY** | **Run `npm run security:scan <repo>`** (`scripts/security_scan.py`, from NVIDIA/SkillSpector) → score + SAFE/CAUTION/DO_NOT_ADOPT (flags prompt-injection, hidden instructions, secret-harvest, curl\|bash, b64-exec, os.system, credential access). DO_NOT_ADOPT → **quarantine, log rejected, stop**. Then eyeball (regex+AST, not a sandbox) | `scripts/security_scan.py`; OS UAP `02b_security`; VETTING step 5 |
| 4 | **DECIDE** | Run the 7-step gate (relevance · license · quality · dedup · security · location · connect). Filters: **free/local**, **permissive license**, **brand-fit**, **no overlap**. Verdict: INGEST / REFERENCE / SKIP | [`REPO_VETTING_SOP.md`](REPO_VETTING_SOP.md) |
| 5 | **ADAPT (brand)** | Take the **PATTERN, not the artifact**. Re-skin to the SEOSONA brand: **light-mode only**, blue `#2A5BDA` / coral `#E2724D`, Be Vietnam Pro. Never import cloud/paid code (Vertex/BigQuery/etc.) | `7_ASSETS/brand/SEOSONA/DESIGN.md`; [[brand-colors-light-only]] |
| 6 | **BUILD (native)** | Implement SEOSONA-native (reuse-first; extend, don't fork). Don't vendor anything that conflicts with `native_composer`/engines | `2_KNOWLEDGE/REPO_VETTING_SOP.md` step 4 (dedup) |
| 7 | **VERIFY** | NO claim without evidence: tests pass (`pytest`), **extract a frame and look** (`ffmpeg -ss` → Read the PNG), run the judge (`npm run eval`), or listen. Any LLM step uses the **3-tier fallback: Cloud (Gemini) → Local (Ollama) → agent/native** — never blocks on quota | `4_BRAIN/evaluator.py`, `eval_judge.py`, [`EVAL_FLYWHEEL.md`](EVAL_FLYWHEEL.md) |
| 8 | **WIRE** | Connect it: npm script, SOP index, `factory_brain` if it's a factory stage. **No orphans** | `package.json`, `6_SOP/README.md`, `4_BRAIN/factory_brain.py` |
| 9 | **RECORD** | Log it so it's never re-evaluated or orphaned: `INGESTION_LOG.md` (+ WATCHLIST/INVENTORY), a memory note, a commit. Bulky clones live in gitignored `2_KNOWLEDGE/external_toolkits/` (reference) or are wiped (OS "zero host bloat") | `2_KNOWLEDGE/INGESTION_LOG.md`; auto-memory |
| 10 | **REFLECT & CONSOLIDATE (periodic, not per-item)** | **(a) Session-close reflection** (from `openclaw-skill-learning-memory`, MIT): at the end of a work session, self-check — *did we learn something new?* (→ memory note) · *did we build a reusable pattern?* (→ propose a skill, with evidence) · *is any memory now stale/contradicted?* (→ fix or delete). **(b) Consolidate** (from `EverMind-AI/EverOS`, Apache-2.0): when several entries teach the SAME thing (e.g. 3 repos → same motion trick), MERGE them into one coherent note + mark the originals superseded — so knowledge doesn't fragment. Keep the audit trail (don't silently erase). | `INGESTION_LOG.md`; auto-memory; this loop |

> **Backlog patterns learned but NOT built** (no-bloat — adopt only on real need; EverOS cloned at `2_KNOWLEDGE/external_toolkits/EverOS` for reference): a **cascade daemon** (file-watcher → SQLite queue → index rebuild) to auto-index new skills; **structured observability** (structlog event logs + latency metrics) for long autonomous runs; **YAML prompt-slots** (override LLM prompts without code edits). Each is real but heavy — build deliberately when a concrete need appears, not speculatively.

---

## Hard rules (violate = redo) — the constitution this loop enforces

1. **System files in English** (Vietnamese only inside video CONTENT).
2. **No duplication** — if a capability exists, extend it; never rebuild ([[no-recreate-deprecated-systems]]).
3. **Connect everything** — no orphan files; wire + index it (stage 8).
4. **No fakes / no mockups** — real data, real verification.
5. **One place per thing** — knowledge → `2_KNOWLEDGE/`, skill → `.agents/skills/` or `domain_skills/`, engine → `5_FRAMEWORK/`.
6. **Reference SEOSONA-OS** for heavy lifting (UAP, security) instead of re-implementing it.
7. **Brand-kept** — light-mode, brand palette + fonts, always (stage 5).
8. **Free / local first** — permissive license; reject cloud/paid lock-in.
9. **Verify before you claim** — frame/test/eval/ear evidence (stage 7).
10. **3-tier fallback** for every LLM call — Cloud → Local Ollama → agent/native (quota never stops the loop).
11. **Dig deeper — don't stop at "REFERENCE".** A surface verdict ("it's a dup / a whole app") is lazy: repos hide adoptable specifics (configs, prompts, recipes, data, edge-cases, schemas). Always do the item-level DEEP EXTRACTION (stage 2b) and harvest the gems, even when the whole is rejected.

---

## Running it

- **Ad-hoc (a specific repo, like today):** walk stages 2→9 by hand (Explore agent for ANALYZE,
  vetting SOP for DECIDE, frame/eval for VERIFY, INGESTION_LOG for RECORD).
- **Bulk inventory:** DISCOVER from the watchlist → route through SEOSONA OS UAP (it does
  ANALYZE+SECURITY+assimilate at scale) → pull English KI via `scripts/inject_os_capabilities.py`.
- **Upkeep:** `npm run freshness` (deps) + `UPGRADE_BACKLOG.md` feed stage 1 continuously.

> This loop is itself a SEOSONA capability — it should eventually run semi-autonomously
> (a "librarian" pass over the watchlist), the same way `factory_brain` runs production.
