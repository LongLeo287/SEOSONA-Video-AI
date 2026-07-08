# 0_SETUP — Root structure audit (2026-06-30)

Full analysis of the SEOSONA Video root (46 items). Verdict: **coherent but NOT clean — organic sprawl
+ redundancy + heavy gitignored disk**. The git REPO itself is moderate; the working-dir SIZE is what's
huge, and almost all of it is gitignored (not cloned).

## Size reality — repo vs disk
| | Size | In a clone? |
|---|---|---|
| **Git repo (tracked)** | **~143 MB · 2195 files** | YES — this is what people clone |
| Working dir total | ~3 GB+ | NO — mostly gitignored |

The 143 MB repo is driven by **`.agents/` (1015 files — vendored skill libraries) + `5_FRAMEWORK/`
(~138 MB — HyperFrames engine)**. The ~2.8 GB of extra disk is gitignored: `node_modules` (1.2 G),
`3_MEMORY/raw_data` (882 M vendored clones), `ffmpeg/` (303 M), `2_KNOWLEDGE` models, `7_ASSETS` venvs/
models, `videolingo` (6.9 M). So cloning the repo is ~143 MB, not GBs.

## Problems found
1. **Broken numbering.** The 0–9 "pipeline" convention has DUPLICATE prefixes: two `0_` (0_INPUT_INBOX,
   0_SETUP), two `1_` (1_AGENTS, 1_CONFIG), two `2_` (2_KNOWLEDGE, 2_SKILLS), two `9_` (9_DASHBOARD,
   9_PROMPTS). The numbers no longer read as a clean sequence → the intent is lost.
2. **Root sprawl (46 items).** A typical repo root is ~20–25. Extra top-level dirs: `docs/`, `deploy/`,
   `packages/` (the hyperframes shim), `tests/`, `logs/`, plus the numbered + named ones.
3. **Redundancy.**
   - Docs in 3 places: root `ARCHITECTURE.md`/`STRUCTURE.md` + `docs/01..05_*.md` + `2_KNOWLEDGE`.
   - `5_FRAMEWORK/` has THREE HyperFrames copies: `hf_core` (84 M) + `hf_engine` (54 M) + `hyperframes`
     (1.8 M) — likely overlapping vendored copies of the same engine (node_modules already has `hyperframes`).
4. **Gitignored disk bloat (reclaimable, NOT in repo):**
   - `ffmpeg/` (303 M) — a full standalone ffmpeg-8.1.1 build; **unused** (code uses node `ffmpeg-static`).
   - `3_MEMORY/raw_data/` (882 M) — vendored repo clones (MoneyPrinterTurbo, …) from the repos-daemon;
     **no live code references** them (reference material only).
   - `videolingo/` (6.9 M) — a leftover VideoLingo clone (REFERENCE only; we re-implemented its algo).

## Recommendations (prioritized)
### A. Safe disk reclaim — ✅ DONE 2026-06-30 (~1.19 GB reclaimed, no breakage)
- Deleted `ffmpeg/` (303 M) — first patched `seosona_bootstrap.check_and_install_ffmpeg` to prefer the
  bundled `node_modules/ffmpeg-static` (so the ffmpeg/ folder is never needed). Verified.
- Deleted `videolingo/` (6.9 M, leftover clone — 0 refs).
- Deleted `3_MEMORY/raw_data/` (882 M, vendored repo clones). The refs looked scary but were false alarms:
  `writer.py`'s `raw_data` is a function PARAMETER, and the OS audit checks `2_KNOWLEDGE/raw_data` (a
  different path, intact). `3_MEMORY`'s real content (brand_memory, context_bank, knowledge_graph…) kept.
- Verified after: workflow_router imports, native_composer ffmpeg/hyperframes resolution, OS-audit paths — all OK.
### B. Reduce the committed repo — ✅ MOSTLY DONE 2026-06-30 (5_FRAMEWORK 138M → 56M)
- Removed `hf_core/` (84 M, identical duplicate registry + upstream docs + captured shader demo).
- Pruned `hf_engine/node_modules` (8.2 M) + `hf_engine/packages` (14 M) — gitignored monorepo source,
  NOT used at render time (blocks are self-contained HTML + GSAP CDN; render uses root `node_modules`).
  Verified a SHADER block (glitch) still renders after.
- Removed `5_FRAMEWORK/hyperframes/` (1.8 M, 228 tracked — upstream docs/scripts/2 templates, 0 refs; live
  artifacts are `hf_engine/registry` + `2_KNOWLEDGE/hyperframes/`). `5_FRAMEWORK/README.md` updated to match.
- Canonical block source = `hf_engine/registry` (97 blocks), now bridged via `4_BRAIN/hf_blocks.py`.
- STILL TODO (risky): prune unused `.agents/` skills (1015 files) — per-skill only.

### Workspace disk — ✅ DONE 2026-06-30 (8_WORKSPACE 9.1G → ~0.1G, gitignored)
- Deleted embedded-captions frame buffers (`frames_fg`/`frames_bg`/`_wx_out`, ~5.0 G — regenerated each
  render) + the two course E2E test dirs (`course916`, `course_congcuseo`) + stale analysis clones
  (`codebase-memory-mcp`, `ai-14all`, 50 M). Kept `n8n/` (a judge sample referenced in eval_judge docstring).
- The `course916` lock was TWO orphaned ffmpeg (PIDs from 08:07 + 08:43, ~1.7 G RAM each) still running an
  old course-mix that had hung for 4 h — killed them, then the dir deleted cleanly.
- ROOT CAUSE FOUND + FIXED: `talking_head_edit.py`'s final burn+mix feeds `-filter_complex` from INFINITE
  inputs (BGM `-stream_loop -1` + PNG b-roll `-loop 1`). `-shortest` is unreliable across a filtergraph fed
  by an endless input (e.g. `sidechaincompress` keeps the looped BGM as its MAIN stream, so `[ao]` never
  EOFs; a `-loop 1` PNG overlay never EOFs either) → the encode runs FOREVER. FIX: probe the footage
  duration and add a hard `-t <dur>` output cap (bounds the output regardless) + a subprocess `timeout`
  backstop. Verified: the same infinite-input mix now terminates instantly with the correct duration.
  (native_composer's news mix is NOT affected — its video is a finite `-map 0:v` copy and `[ao]` is bounded
  by `amix=duration=first`; no infinite filtergraph video inputs.)
### Knowledge base — ✅ DONE 2026-06-30 (2_KNOWLEDGE 626M → 63M, all gitignored)
- `external_toolkits/` 658M → 34M: cleared the VETTED, NON-code-dep analysis clones (logged in
  `INGESTION_LOG.md`, insights already re-implemented natively or captured) — `Toonflow-app` 194M,
  `OpenMontage` 150M (AGPL — clone removal is also license hygiene), `cc-best-practice` 147M, `ArcReel` 51M,
  `ant-design` 66M (a React UI lib auto-cloned mid-session by the ingestion daemon), `open-seo`, `yao-meta-skill`,
  `spec-kit`, `visual-explainer`, `gsap-skills`, `lift_temp`. Confirmed FIRST that **no code imports from
  `external_toolkits`** (refs are attribution comments / doc citations only). KEPT 10 small actively-cited refs
  (AI-auto-generate-video, VieNeu-TTS, agents-cli, EverOS, video-spec-builder, claude-code-video-toolkit, …).
- Removed all nested `.git/` from the kept reference clones (~23 M clone history; not submodules — no `.gitmodules`).
- Deleted `style_references/talking_head/` (70 M — reels; user has the originals at `D:\SEOSONA AI\video talking heads`)
  + `repos/hyperframes-main.md` (54 M upstream dump; live artifacts = `hf_engine/registry` + `2_KNOWLEDGE/hyperframes/`).
- NOTE: a repo-ingestion daemon (`3_MEMORY/ingestion_queue.json`) auto-clones watchlist repos into
  `external_toolkits` — queue is currently empty + processed repos won't re-clone, but it's a source of accumulation.

### Memory store — ✅ DONE 2026-06-30 (3_MEMORY 2.7G → 2.8M)
- Removed the orphaned `chroma_db/` (2.7 G — a `seosona_repos` vector store, 789 embeddings, bloated to 2.4 G
  + a 210 M dirty journal from an interrupted write) AND uninstalled the `chromadb` lib: NO live code used it
  (the doc described it but it was never wired). Updated `docs/07_BRAIN_KNOWLEDGE_MEMORY.md` (dropped the entry).
  Per [[no-recreate-deprecated-systems]] — removed the dead subsystem, not just the data.

### Session grand total 2026-06-30: ~12.4 GB reclaimed (8_WORKSPACE 9.0G + chroma_db 2.7G + KB 0.56G + 5_FRAMEWORK 0.1G)

### C. Structure tidy (cosmetic, ref-heavy — do carefully or just document)
- Either RENUMBER to a clean sequence or DROP the numbers (named domains). Renaming touches many refs +
  the OS audit `requiredFiles` → safer to DOCUMENT the intended order than to rename.
- Fold root `ARCHITECTURE.md`/`STRUCTURE.md` into `docs/` (1 OS-audit ref on ARCHITECTURE.md → update it).

None of A/B/C is required for the system to RUN — it works today. They're hygiene. Execute on approval.
