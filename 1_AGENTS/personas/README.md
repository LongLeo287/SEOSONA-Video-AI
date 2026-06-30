# Personas — agent role definitions (SEOSONA Video)

Role playbooks the orchestrator (or you) adopt for a task. Brand-scoped to video; free/local.

| Persona | Use for | Source |
|---|---|---|
| `orchestrator_agent.md` | top-level task routing | native |
| `visual_designer.md` | brand/visual design decisions | native |
| `researcher.md` | deep technical research + synthesis before adopting a tool/repo/pattern (ANALYZE) | ported from SEOSONA OS, adapted |
| `scout.md` | fast locate code/assets/symbols across the repo (parallel Glob/Grep) | ported from SEOSONA OS, adapted |
| `security-auditor.md` | scan external repos + own generated artifacts before ingest/render (SECURITY) | ported from SEOSONA OS, adapted |

These fill the **analyze/learn** gap (Video previously leaned on generic Explore agents).
They are the brains inside the `.agents/skills/capability-analyst` skill, which runs the
`6_SOP/SELF_IMPROVEMENT_LOOP.md`. Heavier/bulk analysis (1500-repo inventory, OSINT) DELEGATES
to SEOSONA OS UAP via `scripts/inject_os_capabilities.py` — don't re-implement it here.
