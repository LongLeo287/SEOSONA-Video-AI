# Repo watchlist — candidates from the ~1500-repo inventory

Systematic analysis of the classified inventory (`repo_inventory_classified_tiered_updated.xlsx`)
for repos relevant to SEOSONA Video that are NOT yet ingested. Each is run through
`6_SOP/REPO_VETTING_SOP.md` before adopting. Verdict legend:
**INGEST** (vet + bring in) · **REFERENCE** (link only) · **SKIP** (conflicts / over-engineer / dup).

## High-value tools (free) — likely INGEST after vetting
| Repo | Area | Why | Verdict |
|------|------|-----|---------|
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | SYSTEM/ingestion | any doc/PDF/page → clean markdown | ✅ **INGESTED** → `2_KNOWLEDGE/scripts/ingest_source.py` |
| [coderamp-labs/gitingest](https://github.com/coderamp-labs/gitingest) | SYSTEM | repo → text digest | ✅ **INGESTED** (pip + CLI) |
| [facebook/astryx](https://github.com/facebook/astryx) | FACTORY/design | MIT, 974⭐ — design-system/token patterns | ✅ **REFERENCE** (SEOSONA has own DESIGN.md; don't vendor React lib) |
| [tuanminhhole/openclaw-skill-infographic](https://github.com/tuanminhhole/openclaw-skill-infographic) | design/content | infographic generation skill — useful for cards/thumbnails | REFERENCE (vet license) |
| [google/agents-cli](https://github.com/google/agents-cli) | SYSTEM/QA | Apache-2.0, 3.6k⭐ — "Quality Flywheel" eval methodology | ✅ **INGESTED (pattern)** → `4_BRAIN/eval_judge.py` + `EVAL_FLYWHEEL.md`; Cloud/Vertex parts rejected |

## Knowledge / skills — REFERENCE (mine specific items by hand)
| Repo | Area | Note |
|------|------|------|
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | marketing/agents | specialized expert-agent library (may have SEO/marketing personas) |
| [f/prompts.chat](https://github.com/f/prompts.chat) | prompts | large prompt collection |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | skills catalog | 1000+ pointers incl. Corey Haines marketing stack (no SKILL.md to vendor) |

## Voice / TTS
- [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice) — **WATCH**: Apache-2.0, 600+ langs, active; needs hands-on VN quality test → only permissive path to a clone-voice backup. (VN test) — confirmed VN+clone but NO word-timing (no sync benefit) + torch2.8 conflict
 — already covered; alternatives are REFERENCE only
- In use: VieNeu-TTS (brand voice), PhoWhisper (ASR), edge-tts (fallback).
- Alternatives ([k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice), OpenBMB/VoxCPM): REFERENCE —
  brand voice is locked to VieNeu; revisit only if a quality gap appears.

## Full pipelines — SKIP (would conflict with native_composer)
- [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo),
  [krillinai/KrillinAI](https://github.com/krillinai/KrillinAI), JayWebtech/autoshorts,
  zhouxiaoka/autoclip — architecture reference only; do NOT adopt (don't rebuild the engine).

## Already ingested (do not re-evaluate)
nexu-io/open-design · digitalsamba/claude-code-video-toolkit · boraoztunc/skills ·
nextlevelbuilder/ui-ux-pro-max-skill · (see `INGESTION_LOG.md`).

> markitdown done. Next when resuming: SYSTEM → vet `gitingest`; FACTORY → check `facebook/astryx`
> license for design-system depth + `openclaw-skill-infographic` for thumbnail/card craft.

## Batch-1 triage (2026-06-30) — S+A video-relevant CANDIDATEs from inventory(34)

From 1463-repo inventory → 87 S+A video-relevant → 27 NEW candidates (29 already logged). Full triage CSV: `3_MEMORY/eval_results/batch1_triage.csv`. Each runs through the `capability-analyst` skill (SELF_IMPROVEMENT_LOOP) before adopting.

| Repo | Cat | Tier | Score | Why (tags) | Verdict |
|------|-----|------|-------|-----------|---------|
| [every-app/open-seo](https://github.com/every-app/open-seo) | seo | S | 94 | SEO stack; MCP; Agent skills; Keyword research; Rank tr | ✅ REFERENCE→ADOPTED pattern: tools need paid DataForSEO (SKIP), but built free/local `.agents/skills/video-seo-metadata` from its workflow shape |
| [chroma-core/chroma](https://github.com/chroma-core/chroma) | rag | S | 94 | Vector database; AI search infrastructure; RAG stack; E | ✅ **REFERENCE/SKIP** — vector-RAG; faceless video factory doesn't do retrieval (markitdown+gitingest cover ingestion) |
| [ArcReel/ArcReel](https://github.com/ArcReel/ArcReel) | video | S | 92 | Video generation; AI Agent workflow; Claude Agent SDK;  | ✅ **REFERENCE-pattern** (AGPL — analyze-only, not vendored) — gem = two-stage script (plan→scenes) → built `_gemini_outline`; image/character patterns N/A to faceless HTML |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | video | S | 95 | Agentic video production; 12 pipelines/52 tools/500 skills; 28.9k★ (user-flagged) | ✅ **ADOPT-pattern** (AGPL, 3-agent deep dig) — hook-patterns + narrative-variety + climax → `_gemini_outline` + VIDEO_CRAFT_RULES §7. Pipeline-manifest/tool-registry/checkpoint/playbook = REFERENCE-BACKLOG (over-build for solo) |
| [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | rag | S | 92 | Document parsing; PDF/OCR; Markdown/JSON; Agentic workf | ✅ **REFERENCE** — PDF/OCR; markitdown covers doc→md. Backlog: stronger OCR if infographics-from-scanned-PDF needed |
| [lumina-ai-inc/chunkr](https://github.com/lumina-ai-inc/chunkr) | rag | S | 91 | Document intelligence; Layout analysis; OCR; Semantic c | ✅ **SKIP-DUP** — semantic chunking for RAG retrieval; we ingest as blob → script, no chunking need |
| [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | rag | S | 90 | MCP; Codebase memory; Knowledge graph | ✅ **SKIP** (1.4GB) — codebase knowledge-graph for IDEs; wrong domain for a video factory |
| [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | rag | S | 90 | Persistent memory; Agent OS; Self-evolving knowledge | ✅ **ADOPT-knowledge** (Apache-2.0) — Reflect & Consolidate → SIL stage 10; cascade/observability/prompt-slots = BACKLOG |
| [feicaiclub/video-spec-builder](https://github.com/feicaiclub/video-spec-builder) | video | S | 90 | Video spec; Storyboard; HyperFrames; Claude Code/Cursor | ✅ REFERENCE (interactive skill ≠ our autonomous factory; idea backlog: component subtypes, scene-validate, 9:16 layout) |
| [StarTrail-org/PixelRAG](https://github.com/StarTrail-org/PixelRAG) | rag | S | 90 | Visual RAG; Screenshot tiles; Layout-aware retrieval | ✅ **REFERENCE/SKIP** — visual retrieval; not our problem. Backlog: pixelshot if source-screenshot overlays needed |
| [github/spec-kit](https://github.com/github/spec-kit) | skills | S | 90 | Spec-driven development; Planning; Engineering workflow | ✅ **REFERENCE** (MIT, 116k★) — spec→plan→tasks+constitution+test-first already covered by SIL + LLM_CODING_DISCIPLINE; templates = bloat for solo factory |
| [HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | video | S | 90 | Animated short drama; AI scriptwriting; Storyboarding;  | ✅ **ADOPTED pattern** (Apache, targeted brain) — two-stage decomposition → built native two-stage `_gemini_script`; image/drama machinery N/A |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | rag | S | 88 | Context compression; Token optimization; MCP | ✅ **REFERENCE** — token-compression N/A now (small prompts + free local Ollama; +60MB ML dep = bloat) |
| [yifanfeng97/Hyper-Extract](https://github.com/yifanfeng97/Hyper-Extract) | rag | S | 88 | LLM extraction; Knowledge graphs; Hypergraphs; Structur | ✅ **SKIP-DUP** — knowledge-graph extraction; different output shape (we make scripts, not graphs) |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | skills | S | 86 | Agent skill; Recency workflows | ✅ **ADOPT-pattern** (MIT, 100%) — entity-resolution + multi-source recency ranking → upgrade `discovery.py` to autonomous trending discovery (wiring = BACKLOG) |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | skills | S | 86 | Claude Code best practices; Commands/agents/skills/hook | ✅ REFERENCE→ADOPTED pattern: added "Execution Contract + Fail-Closed" to 3 personas + capability-analyst. Rest already covered by SIL |
| [opendataloader-project/opendataloader-pdf](https://github.com/opendataloader-project/opendataloader-pdf) | rag | S | 86 | PDF ingestion; RAG; Document loader | ✅ **REFERENCE** — PDF loader; markitdown covers it. Backlog: bounding-boxes if source-citation overlays needed |
| [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) | skills | A | 76 | Visual explanation; HTML artifact; Agent skill | ✅ **ADOPTED** knowledge (MIT, 100% skill) — depth tiers + overflow guard + tag-label → VIDEO_CRAFT_RULES §6 (rejected its CSS-keyframes stagger: not seek-safe) |
| [nemocake/claude-obsidian-assistant](https://github.com/nemocake/claude-obsidian-assistant) | rag | A | 76 | Obsidian; Claude workspace; Notes/memory | ⏳ analyze |
| [datalab-to/lift](https://github.com/datalab-to/lift) | rag | A | 76 | Document extraction; RAG prep; Data pipeline | ✅ **SKIP-DUP** (Apache code / OpenRAIL-M model, 100% read) — markitdown+gitingest cover it; schema-PDF→JSON = BACKLOG (license-risk flagged) |
| [tuanminhhole/openclaw-skill-learning-memory](https://github.com/tuanminhhole/openclaw-skill-learning-memory) | rag | A | 75 | OpenClaw; Learning memory; Skill memory | ✅ **SKIP-DUP** (MIT, 100% read) — thinner than our SIL; extracted session-close reflection → SIL stage 10a |
| [ant-design/ant-design](https://github.com/ant-design/ant-design) | design | A | 75 | React UI library; Enterprise design system; Components; | ✅ **SKIP** — React UI lib; we render HTML+GSAP video w/ own DESIGN.md |
| [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master) | skills | A | 74 | Claude skill; Prompt engineering; Context retention; Pr | ✅ **ADOPTED** (MIT, 5/5 read) — grounding/role/no-fabricate → hardened `_gemini_script` |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | skills | A | 73 | GSAP; Animation skills; Agent skills | ✅ REFERENCE (MIT; 90% dup with our motion-recipes; keep cloned for GSAP pattern lookup. immediateRender flash = non-issue here, frame-0 verified) |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | skills | A | 72 | Skill collection; AI education; prompt ops | ✅ **ADOPTED** — actually **MIT** (declared in SKILL.md; gh-api wrongly said no-license). 4 LLM-coding principles → `6_SOP/LLM_CODING_DISCIPLINE.md` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | skills | A | 72 | Agent skills; Automation helper (67k★) | ✅ **REFERENCE** (MIT) — lazy/reuse discipline = our Karpathy LLM_CODING_DISCIPLINE; 1 micro-gem (tagged-shortcut comments) adopted |
| [yaojingang/yao-meta-skill](https://github.com/yaojingang/yao-meta-skill) | skills | A | 57 | Meta-skill; Agent skills; Evaluation; Governance; Porta | ✅ **REFERENCE** (MIT) — enterprise skill-OS, over-built at ~20-skill scale; 1 gem (skill-qualification gate) → capability-analyst |
| [arm64x/PHP-Lazada-Affiliate-API-Tool](https://github.com/arm64x/PHP-Lazada-Affiliate-API-Tool) | seo | A | 46 | Vietnamese / Local market; SEO stack | ⏳ analyze |
