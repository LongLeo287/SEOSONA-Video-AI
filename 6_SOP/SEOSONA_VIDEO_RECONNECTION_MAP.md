# SEOSONA Video Reconnection Map

Created: 2026-06-22

## Purpose

This document is the project-level connection map for SEOSONA Video. It exists
to prevent routing drift between SEOSONA OS, project agents, project skills,
HyperFrames vendor snapshots, reusable templates, runtime memory, and generated
workspace outputs.

## Operating Principle

HyperFrames is the canonical renderer and composition model for SEOSONA Video.
Everything else is an adapter around it:

- `4_BRAIN/` owns workflow routing, orchestration, timing, and quality gates (governed by Supergraph DAG and OODA Loop).
- `1_AGENTS/` owns the intelligent workforce (Editor, Scraper, Writer, and Machine Learning Analytics).
- `.agents/skills/` owns operator-facing video workflow instructions.
- `5_FRAMEWORK/hf_core/` owns the active local HyperFrames framework snapshot.
- `5_FRAMEWORK/hf_engine/` is an upstream/vendor reference and package source.
- `5_FRAMEWORK/hf_cards/` owns reusable card and stat-card render projects.
- `7_ASSETS/video_templates/` owns reusable, promoted production templates.
- `8_WORKSPACE/` owns generated outputs and must stay disposable.
- `9_PROMPTS/` owns all externalized LLM prompts (AIDA, PAS, Carousel, Repurpose).
- `6_SOP/` owns SEOSONA-specific operating decisions.

Do not create another active HyperFrames runtime tree. If an external source is
ingested, sync it into the existing HyperFrames area or document it as a
reference-only source.

## Canonical Entry Points

| Area | Command | Owner |
|---|---|---|
| Project binding health | `npm run seosona:doctor` | `scripts/seosona-project-bridge.cjs` |
| Strict OS graph validation | `npm run seosona:doctor -- --strict` | `~/.seosona/1_CORE/scripts/seosona_capability_bridge.js` |
| Capability routing | `npm run seosona:route -- "<query>"` | `scripts/seosona-project-bridge.cjs` |
| Autonomy intake | `npm run autonomy:intake -- --task "<task>"` | project bridge resolved OS script |
| Full project audit | `npm run seosona:audit` | `scripts/seosona-project-audit.cjs` |
| Integration audit | `npm run video:audit:integration` | `4_BRAIN/video_integration_audit.py` |
| Video production | `npm run video:news -- <script_or_url> [project] [ratio]` | `4_BRAIN/workflow_router.py` (Supergraph Entrypoint) |
| Template export | `npm run video:template:export -- <workspace_project> "<name>"` | `4_BRAIN/video_template_factory.py` |

## Resolver Contract

Project scripts must resolve SEOSONA OS through the project bridge. The allowed
resolution order is:

1. `${SEOSONA_ROOT}`
2. `seosona.project.json` `osRoot`
3. `~/.seosona`
4. Relative sibling fallback from the project root

Project code must not assume a physical drive path. Runtime logs may display
resolved absolute paths, but committed system files must use portable anchors or
project-relative paths.

## Doctor And Bootstrap Separation

`npm run seosona:doctor` is a lightweight binding check. It must not install
packages, update dependencies, download models, or change browser caches.

`scripts/seosona_doctor.py` is a bootstrapper. Run it only when intentionally
preparing the local machine. Python commands may opt into the bootstrapper by
setting `SEOSONA_PYTHON_BOOTSTRAP=1`.

## Audit Semantics

Project audit failures should block production only when they affect the
SEOSONA Video core:

- project manifest and bridge
- HyperFrames SOP and operator skills
- runtime script portability
- production asset restorability
- voice/subtitle/audio quality gates
- local publish safety
- project doctor health

External OS capabilities such as optional publishing, scraping, or historical
repo-ingestion artifacts are warnings unless the current workflow explicitly
requires them.

## Agent And Skill Boundaries

Use `.agents/skills/seosona-video-operator/SKILL.md` as the project-level
operator contract. It may route into HyperFrames domain skills:

- `hyperframes`
- `hyperframes-core`
- `hyperframes-animation`
- `hyperframes-creative`
- `hyperframes-media`
- `hyperframes-registry`
- `product-launch-video`
- `faceless-explainer`
- `embedded-captions`
- `graphic-overlays`
- `motion-graphics`
- `general-video`

Legacy Python modules in `2_SKILLS/` are implementation adapters. They should
not define separate production policy when a project SOP already owns it.

## Known Global OS Warning

If strict OS validation reports a path portability issue outside this project,
keep the project doctor green and record the issue as an upstream OS finding.
Patch OS core files only when the task explicitly authorizes OS core changes.

TASK COMPLETED
