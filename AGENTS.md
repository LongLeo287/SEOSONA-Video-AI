# SEOSONA Project Rules

This project is bound to SEOSONA OS through `seosona.project.json`.

## Startup Contract

1. Resolve SEOSONA OS through `~/.seosona`.
2. Read `~/.seosona/1_CORE/SOUL.md`.
3. Read `~/.seosona/2_KNOWLEDGE/MASTER_INDEX.md`.
4. Query `~/.seosona/1_CORE/scripts/seosona_capability_bridge.js` for routing.
5. Check project memory at `~/.seosona/3_MEMORY/projects/seosona-video/`.
6. Run project health with `npm run seosona:doctor` when available.

## Project Connector

- Manifest: `seosona.project.json`
- Memory namespace: `seosona-video`
- Autonomy level: `project_edit`
- Publish/deploy actions require explicit user intent.

## Making Videos (HyperFrames is the core engine)

For ANY video task, use the HyperFrames stack already in this repo — do not hand-roll HTML:

1. Load the `seosona-video-operator` skill (`.agents/skills/seosona-video-operator/SKILL.md`) — the hub that routes to everything.
2. Use the `/hyperframes` slash command (and `-core`, `-animation`, `-cli`, `-creative`, `-media`, `-registry`, plus workflow skills) to author compositions.
3. Consult the knowledge base `2_KNOWLEDGE/hyperframes/` (start at its `README.md`) for the HTML schema, package APIs, and rendering.
4. Pull ready-made blocks/transitions/captions from the catalog: `npx hyperframes add <name>` — see `2_KNOWLEDGE/hyperframes/catalog/CATALOG_INDEX.md`.
5. Render via `4_BRAIN/pipeline_manager.py` (or `/hyperframes-cli`); config + decisions in `6_SOP/RENDER_ENGINE_DECISION.md`.

TASK COMPLETED
