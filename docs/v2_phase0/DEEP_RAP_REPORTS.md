# Deep-RAP Reports — Step 2 (real clone + real-CLI scan) of the Bucket-D shortlist

**Date:** 2026-07-15 · **Harness:** `seosona-video-os/scripts/rap-run.mjs` → `analyzeRepoDetailed`
(genuine `git clone --filter=blob:none --depth 1` → native license/footprint/health/prompt-injection
stages → **real CLIs** gitleaks + bandit + ast-grep + osv-scanner → completeness gate → `renderReport`
→ RECORD stage DELETES the clone). **No mock, no skip, no fabricated verdict** — this is the discipline
RAP exists to enforce (the anti-UAP rule).

**Evidence (raw report + analysis JSON per repo) lives in the OS repo** — this doc is the human summary:
`seosona-video-os/docs/evidence/rap_report_<slug>.md` + `rap_<slug>.json`. Every verdict, license,
gate-ledger, and finding below is copied from those machine-written artifacts, not re-derived.

**Completeness gate (the anti-UAP rule):** an adopt-ish verdict (extract/adapter_adr/add_dep) may only
stand when ALL five critical checks actually RAN — `license_code`, `license_weights`, `secrets_scan`,
`capability_extraction`, `dedup`. If any is missing (e.g. ast-grep can't source-verify a docs-only repo),
the verdict is forced to **`incomplete`** (a work-order, not a green light) — never a default-pass.

---

## Consolidated result table

| # | Repo | Verdict | Verified license | Gate complete? | Extract → roster role |
|---|------|---------|------------------|----------------|-----------------------|
| 1 | HKUDS/ViMax | **extract** | **MIT** (LICENSE in clone) | ✅ all 5 ran | typed crew-decomposition + shotlist schema → **#1 Director**, **#4 Scene-planner** |
| 2 | Leonxlnx/taste-skill | **incomplete** | **MIT** | ❌ `capability_extraction` (docs-only) | aesthetic-taste rules (prose, MIT) → **#5 / #8 / #11** (manual craft-harvest, not code-extract) |
| 3 | zhouxiaoka/autoclip | **extract** | **MIT** | ✅ all 5 ran | long→short LLM highlight-scoring pipeline → **#13 Repurpose** |
| 4 | SamurAIGPT/AI-Youtube-Shorts-Generator | **reference** | **UNKNOWN / no LICENSE file** | ✅ all 5 ran | **license-blocked — no extraction**; learn-only |
| 5 | charlie947/social-media-skills | **incomplete** | **MIT** | ❌ `capability_extraction` (docs-only) | per-platform posting + post-scoring rules (prose, MIT) → **#15 Publisher / #16 Reporter** |

**#3-vs-#4 dedup for role #13 Repurpose → KEEP autoclip (#3).** Reasons below (§4).

---

## 1. HKUDS/ViMax — `extract` → roster #1 Director (⚓) + #4 Scene-planner

- **Verified license:** **MIT** (resolver read the clone's `LICENSE`; `code_spdx = MIT`, effective = MIT).
- **Gate:** ✅ COMPLETE — all 5 critical checks ran (`license_code`, `license_weights`, `secrets_scan`,
  `capability_extraction`, `dedup`). `missing_checks = []`.
- **Scans:** gitleaks **clean** (0 secrets); bandit/ast-grep/osv-scanner all spawned. **Prompt-injection: 2
  findings — both BENIGN**: zero-width characters inside emoji `print(f"✔️…")` status lines
  (`pipelines/novel2movie_pipeline.py:L730` etc.), i.e. an emoji-rendering artifact, not an injected
  instruction. Not a blocker.
- **Health:** has tests, last commit ~2d old (actively maintained). 23 source-verified capabilities.
- **What RAP's generic ast-grep surfaced:** CLI entry points + argparse in `main_agent.py`,
  `main_idea2video.py`, `main_script2video.py` — proof the crew/pipeline modules are real. The specific
  crew-decomposition + typed plan (the actual value) was pinned from the clone's file tree:
  - **The crew** = `agents/` — one specialist persona per file: `screenwriter.py`, `script_planner.py`,
    `scene_extractor.py`, `event_extractor.py`, `character_extractor.py`, `storyboard_artist.py`,
    `camera_image_generator.py`, `global_information_planner.py`, `best_image_selector.py`. This is the
    "**Director is glue, crew emits a TYPED plan**" pattern the whole V2 MVP hangs on.
  - **The typed plan schema** = `interfaces/shot_description.py` (the shotlist/shot-description type) +
    `agent_runtime/models.py` (agent data models).
  - **The glue** = `pipelines/{idea2video,novel2movie,script2video}_pipeline.py` — sequences the crew
    into a single run.
- **EXTRACT → where:** the crew-role decomposition (`agents/*.py` role split) and the typed shotlist
  schema (`interfaces/shot_description.py`) → inform our **native Director glue** (`ProductionPlan{shotlist[],
  timing, style, captionStyle, voiceSpec, assetQueries[], renderCmd}`) over SEOSONA engines, and the
  **Scene-planner** (`agents/scene_extractor.py` + `script_planner.py` → extend `director.py`/`plan_scenes`).
- **Adapt-to-our-engines (never vendor):** take the SHAPE (which specialist roles exist, what the plan type
  carries), NOT ViMax's model/API stack — it wires MiniMax/OpenRouter/yunwu paid video generators; our
  Director commands OmniVoice + HyperFrames + our asset-sourcer. `metadata.author = SEOSONA`; no third-party
  names in the shipped agent.

## 2. Leonxlnx/taste-skill — `incomplete` (honest) → craft for #5 / #8 / #11

- **Verified license:** **MIT** (`code_spdx = MIT`).
- **Gate:** ❌ INCOMPLETE — `missing_checks = ["capability_extraction"]`. **Honest reason:** this is a
  **markdown-only SKILL repo** (all `skills/*/SKILL.md` prose, no parseable source) → ast-grep produced
  **0 source-verified capabilities**, so the code-oriented completeness gate cannot bless an adopt verdict.
  This is the gate working correctly, not a scan failure: `license_code`, `license_weights`, `secrets_scan`,
  `dedup` all RAN; gitleaks/bandit/osv all **clean (0 findings)**.
- **Disposition:** RAP verdict is `incomplete` (no code to source-verify). The craft, however, is MIT prose
  and is adoptable as **REFERENCE via manual harvest** — the license does NOT block it; only the code-gate
  can't enumerate it. Treat as a craft source, rewrite fresh (branding standard).
- **What to harvest (MIT prose, file pointers from the repo tree):**
  - `skills/taste-skill/SKILL.md` — the core aesthetic-taste heuristics (typography pairing/scale, spacing,
    hierarchy, contrast).
  - Style-archetype rules: `skills/minimalist-skill/SKILL.md`, `skills/brutalist-skill/SKILL.md`,
    `skills/soft-skill/SKILL.md`, `skills/redesign-skill/SKILL.md`, `skills/stitch-skill/DESIGN.md`.
  - `skills/brandkit/SKILL.md` — brand-kit / palette discipline.
  - **SKIP (off-core / paid):** `skills/imagegen-frontend-web|mobile`, `skills/image-to-code-skill`,
    `skills/gpt-tasteskill` (image-gen / GPT-tooling bits) — keep the *rules*, ignore the tooling.
- **EXTRACT → where:** typography/spacing/hierarchy heuristics → parametrize our ASS caption styles (**#5
  Subtitle-stylist**) and archetype `TemplateSpec` polish (**#8**); reuse as a **QA-aesthetics rubric**
  (**#11**). Keep SEOSONA LIGHT palette; write prose fresh (no verbatim copy — branding standard).

## 3. zhouxiaoka/autoclip — `extract` → roster #13 Repurpose

- **Verified license:** **MIT** (`code_spdx = MIT`).
- **Gate:** ✅ COMPLETE — all 5 checks ran, `missing_checks = []`. 21 ast-grep source-verified caps,
  240 source-cited capabilities total (rich real codebase). Health: has tests + CI, ~42d old, 0 owned-overlap
  in dedup (`any_new = true` — V2 does not already own highlight-scoring).
- **Scans (informational, do NOT block extract — findings are in vendored code/deps, we clean-room the
  pattern):** gitleaks **1** finding, bandit **278**, osv-scanner **270** dependency CVEs, prompt-injection
  **1**. These live in the repo's bundled Flask/Celery backend + its dependency tree; since we re-implement
  the *scoring heuristic* natively (not vendor the backend), they are context, not a gate failure. Flagged
  here for honesty — if any code were ever lifted, the gitleaks hit + CVE surface must be re-examined first.
- **The extractable capability (long→short highlight SCORING):** the repo is a real pipeline app
  (`backend/execute_real_pipeline.py`, `backend/api/v1/pipeline_control.py`, `backend/api/v1/processing.py`,
  `backend/api/v1/clips.py`, `backend/utils/video_processor.py`) that downloads a long YouTube/Bilibili
  video, transcribes it, and uses an **LLM to score + rank candidate highlight windows** into short clips.
  This is exactly the **virality/highlight-scoring signal V2 lacks** — our `talking_head_autocut` only
  removes dead-air/filler; it does not *pick the best window*.
- **EXTRACT → where:** the highlight-scoring + segment-ranking heuristics (the pipeline's scoring step) →
  build keyless **#13 Repurpose**: swap autoclip's paid DashScope LLM for our resilient `llm_engine`
  cascade, download via our yt-dlp path, keep the score→rank→cut logic. NOT vendored — clean-room the
  heuristic over our engines.
- **Adapt note:** ignore the whole Flask/Celery/desktop app scaffolding (that is where the CVEs/secrets
  live); take only the score-and-select algorithm shape.

## 4. SamurAIGPT/AI-Youtube-Shorts-Generator — `reference` (LICENSE BLOCKED)

- **Verified license:** **UNKNOWN — the clone has NO LICENSE file.** The `license_code` resolver RAN and
  honestly found no OSI-permissive (or any) license → `effective_most_restrictive = "unknown"` →
  `screen.license_ok = false`. Under default copyright, absence of a license means **all rights reserved**:
  the code may NOT be copied or adapted.
- **Gate:** ✅ COMPLETE — all 5 checks ran (`missing_checks = []`). This is a **definitive `reference`**,
  not an `incomplete`: the resolver reached a real conclusion (no license), it did not fail to run.
- **Scans:** gitleaks clean (0), bandit 3, osv-scanner 32 CVEs. Caps surfaced: `main.py`,
  `shorts_generator/local/clipper.py` (the crop/clip logic).
- **Verdict statement (plain):** **the missing license blocks extraction.** We do NOT copy or adapt its
  code (virality scoring or the 9:16 speaker-crop/reframe in `clipper.py`). It is **learn-only**: we may
  study that auto-face-crop-to-9:16 is a desirable capability, but any implementation must be written
  clean-room from our own approach (or a permissively-licensed source), never derived from this repo.

## 5. charlie947/social-media-skills — `incomplete` (honest) → craft for #15 / #16

- **Verified license:** **MIT** (`code_spdx = MIT`).
- **Gate:** ❌ INCOMPLETE — `missing_checks = ["capability_extraction"]`. **Same honest reason as
  taste-skill:** markdown-only SKILL repo (all `skills/*/SKILL.md` prose) → ast-grep found 0 source-verified
  capabilities. `license_code`, `license_weights`, `secrets_scan`, `dedup` all RAN; all scanners **clean (0
  findings)**. The gate correctly refuses an adopt verdict on prose.
- **Disposition:** RAP verdict `incomplete` (nothing to source-verify); the per-platform *knowledge* is MIT
  prose, harvestable as REFERENCE. License clears; only the code-gate can't enumerate it.
- **What to harvest (MIT prose, file pointers) — the two NEWEST roster roles have the thinnest sources:**
  - **#16 Reporter (analytics/learning-loop):** `skills/post-scorer/SKILL.md` (a real post-SCORING rubric)
    + `skills/analytics-dashboard/SKILL.md` (metric interpretation) → seed the Reporter's
    view/retention/winner analysis.
  - **#15 Publisher (per-platform posting craft):** `skills/post-formatter/SKILL.md`,
    `skills/post-writer/SKILL.md`, `skills/hook-generator/SKILL.md`, `skills/reels-scripting/SKILL.md`,
    `skills/profile-optimizer/SKILL.md`, `skills/pinned-comment/SKILL.md`, `skills/content-matrix/SKILL.md`,
    `skills/niche-research/SKILL.md` → per-platform cadence/format playbooks.
  - **SKIP (paid tooling):** `skills/gemini-carousel`, `skills/gemini-infographic` (paid Gemini image-gen),
    and any `graphic-designer`/`youtube-thumbnail` step that calls a paid API — **keep the knowledge, drop
    the tools** (we build keyless; public posting stays human-gated per roster #15).
- **EXTRACT → where:** the platform-specific posting/cadence + post-scoring/analytics *knowledge* → seed the
  **#15 Publisher** and **#16 Reporter** playbooks. Their Apify + Gemini tooling is PAID → out.

---

## §4 — Dedup decision: autoclip (#3) vs AI-Youtube-Shorts-Generator (#4) for role #13 Repurpose

Both target the SAME roster role #13 (long→short highlight extraction). RAP dedup discipline = keep ONE.

**WINNER: zhouxiaoka/autoclip (#3). Drop #4.**

| Criterion | #3 autoclip | #4 AI-Youtube-Shorts-Generator |
|-----------|-------------|-------------------------------|
| Verified license | **MIT** (clean, adoptable) | **UNKNOWN / no LICENSE** (all-rights-reserved) |
| RAP verdict | **extract** (gate complete) | **reference** (license-blocked) |
| Scoring signal | **LLM highlight-scoring + segment-ranking pipeline** (full download→transcribe→score→rank→cut) | virality score + 9:16 speaker-crop only |
| Maintained / quality | tests + CI, ~42d old, 6k★ | no tests/CI, ~23d old |
| Extractability | code adaptable clean-room (MIT) | **not adaptable** — code cannot be copied |

**Why:** #4's only extraction path is blocked by its missing license — we cannot lift its virality-scoring
or crop code. #3 is MIT AND carries the richer scoring signal (a real score→rank→select pipeline vs #4's
scorer+crop). So #3 wins on BOTH the license and the scoring-signal axes the task named. The one thing #4
*conceptually* adds — auto 9:16 speaker-crop/reframe — is a **learn-only idea**: if V2 wants it, implement
it clean-room from our own (or a permissively-licensed) source, never derived from #4.

---

## Honest notes (fail-honest record)

- **Real clones, real CLIs, real gate.** All 4 scanners (gitleaks, bandit, ast-grep, osv-scanner) spawned on
  every repo; every clone was DELETED by the RECORD stage (`clone_deleted = true` in each JSON). No verdict
  was fabricated or forced — each is exactly what `analyzeRepoDetailed` returned.
- **Two `incomplete` verdicts are HONEST, not failures.** taste-skill (#2) and social-media-skills (#5) are
  docs-only SKILL repos; ast-grep legitimately source-verifies nothing in prose, so the completeness gate
  returns `incomplete` (per its anti-UAP rule). Their MIT craft is still harvestable manually as REFERENCE —
  the block is the code-gate's inability to source-verify prose, NOT the license and NOT a scan that didn't
  run (all other four checks ran clean on both).
- **One license-block:** AI-Youtube-Shorts-Generator (#4) has no license file → `reference` (learn-only). No
  extraction. Stated plainly above.
- **autoclip scan findings** (1 secret / 270 CVEs / 278 bandit) are in its bundled backend + dependency tree,
  not in the scoring heuristic we clean-room — recorded for honesty; must be re-examined if any code is ever
  lifted verbatim (it will not be).
