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
