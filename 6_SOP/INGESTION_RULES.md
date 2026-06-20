# INGESTION RULES — SEOSONA Video
# Universal Assimilation Protocol (UAP) — Enforced Rules
# Version: 1.0 | Created: 2026-06-20

This document is the **binding law** for all repo ingestion in SEOSONA Video.
Any agent or human performing ingestion MUST follow these rules without exception.

---

## RULE 1 — DEDUP CHECK (Mandatory First Step)

Before creating ANY file, ALWAYS check `2_KNOWLEDGE/INGESTION_INDEX.md`:
- If the repo is listed with status `ingested` or `cleared` → STOP, skip it
- If status is `pending` → continue from where it was left off
- If the repo is NOT listed → add it first, then proceed

**Violation**: Creating duplicate knowledge files wastes tokens and causes drift.

---

## RULE 2 — NO OVERWRITE

NEVER overwrite existing files in `2_SKILLS/`, `1_AGENTS/`, `6_SOP/`, or `4_BRAIN/`.

If a capability already exists and new repo adds value:
- Option A: MERGE the new knowledge into the existing file (add a versioned section)
- Option B: Create `<existing_name>_supplement.md` with just the delta

**Example**: If `2_SKILLS/voice_cloner/` already exists from F5-TTS analysis,
and WeClone adds new patterns → add a `## WeClone Supplement` section to the existing file.

---

## RULE 3 — SINGLE SOURCE OF TRUTH

Each capability domain has exactly ONE authoritative file:
| Domain | Owner File |
|--------|------------|
| Voice Cloning | `2_SKILLS/voice_cloner/voice_cloner.md` |
| TTS Engine | `6_SOP/VOICE_TTS_ENGINE_ROUTING.md` |
| Scraping | `2_SKILLS/scraper_agent/scraper_capability.md` |
| B-Roll / Visuals | `2_SKILLS/b_roll_fetcher/b_roll_capability.md` |
| Subtitle/SRT | `2_SKILLS/srt_maker/srt_capability.md` |
| Audio Mixing | `2_SKILLS/audio_mixer/audio_mix_capability.md` |
| SEO Writing | `1_AGENTS/seo_writer_agent/seo_writer_capability.md` |
| Publishing | `1_AGENTS/publisher_agent/publish_capability.md` |
| Pipeline Routing | `4_BRAIN/pipeline_manager.py` |

Adding a new repo's knowledge = EDITING the owner file, NOT creating a new one.

---

## RULE 4 — KNOWLEDGE FILE FORMAT

Every repo ingested into `2_KNOWLEDGE/repos/` MUST use this exact template:

```markdown
# [Repo Name]
- **Source**: https://github.com/...
- **Stars**: [number at time of ingestion]
- **Tier**: [A | B | C]
- **Domain**: [tts | video | scraper | seo | agent | framework | ui | other]
- **Ingested**: [YYYY-MM-DD]
- **Status**: [pending | ingested | cleared]

## Core Value
[2-4 sentences: what this repo does and why it matters for SEOSONA Video]

## Key Architecture / Patterns
[The most important code patterns, data structures, or design decisions]
[Include short code snippets if they illustrate a critical pattern]

## What SEOSONA Video Learned
[Concrete, actionable knowledge extracted. NOT a copy-paste, but a distillation]

## Integration Applied
[What file was modified or created based on this repo. Exact file paths.]

## Cleared
[YES/NO — was the raw repo folder deleted after ingestion?]
```

---

## RULE 5 — TIERING CRITERIA

| Tier | Stars | Direct Relevance | Action |
|------|-------|-----------------|--------|
| A | Any | Core video/TTS/agent pipeline | Deep read all source files, full integration |
| B | >100 | Indirect (UI patterns, agent patterns) | README + key files only, selective integration |
| C | Any | Not relevant to SEOSONA Video | Log URL to `5_RESEARCH/reference_repos.md`, delete raw immediately |

**Relevance test**: Does this repo directly improve video creation, TTS quality, scraping, SEO writing, or publishing pipeline? If NO → Tier C.

---

## RULE 6 — MANDATORY CLEAR

After a repo reaches status `ingested`:
1. Delete `3_MEMORY/raw_data/repos/<repo_name>/` directory entirely
2. Update `INGESTION_INDEX.md` status to `cleared`
3. Append one line to `3_MEMORY/logs/ingestion_log.md`:
   ```
   [YYYY-MM-DD HH:MM] CLEARED <repo_name> | Tier: A/B/C | Integrated into: <file_path>
   ```

**Exception**: Tier A repos with model weights, training data, or large binaries are cleared immediately regardless of ingestion status (weights stay if moved to `7_ASSETS/models/`).

---

## RULE 7 — NO HARDCODED PATHS

All paths in generated Skill/Agent/SOP files MUST use:
- `${SEOSONA_ROOT}` for project root
- Relative paths from the project dir
- NEVER: `D:\LongLeo\...` or any absolute machine path

---

## RULE 8 — MEMORY LOG REQUIRED

Every ingestion session MUST append to `3_MEMORY/logs/ingestion_log.md`.
Format:
```
[DATE] SESSION START — N repos queued
[DATE] INGESTED <repo> | Tier: X | -> <target_file>
[DATE] CLEARED <repo>
[DATE] SKIPPED <repo> | Reason: already ingested / Tier C / duplicate
[DATE] SESSION END — N ingested, N cleared, N skipped
```

---

## ENFORCEMENT

This file is READ by the system at the start of every ingestion task.
If any rule is violated, the agent MUST stop, revert the violation, and restart.

TASK COMPLETED
