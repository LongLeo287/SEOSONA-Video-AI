# Anatomy of the Soul: Brain, Memory, and Knowledge

If the Workflows are the "Hands and Feet", then this is the "Soul" that gives SEOSONA Video the ability to reason on its own and evolve over time.

## 🧠 1. Central Nervous System (`4_BRAIN/`)
The home of the Language Processing and static Logic Analysis cores (Render not yet touched). Click to see the cores in detail:

<details open>
<summary><b>⚙️ The Core Reasoning Engines</b></summary>
<br>

- 🧠 **`llm_engine.py` (29.6KB)**: The heart of the system. Contains the algorithms for calling APIs, managing the Context Window, Rate Limit, and Retry Logic when communicating with large language models (OpenAI, Anthropic).
- 🚉 **`video_engine.py`**: The unified gateway of the render pipeline (`run_pipeline(script_text, brand, mode, aspect_ratio, project_name)`). Decides which data file goes into which pipe and orchestrates the entire process.
- 🎨 **`native_composer.py`**: the real renderer — voice + RULE #1 subtitles + native HyperFrames render + BGM-ducking/SFX mixing + partial re-render (`redo=visual/voice/mix/thumb`). Templates are managed by `template_generator.py` + `template_picker.py`.
- 🧩 **`scene_composer.py`**: The content brain, selects and arranges scenes before passing them to `native_composer`.
- 🔀 **`workflow_router.py`**: Routes work, wrapping `video_engine` in a SuperGraph DAG + quality gate. It reads the incoming facts and decides: *"Ah, this is a code-parsing post, let's call the PR-to-Video flow"*.
- 🎯 **`intent_router.py`**: The "Intent" router. Tries to understand what the user or parent system really wants through ambiguous text flows.
- 💯 **`quality_scorer.py`**: The ruthless scoring machine. Returns a score (Scale 0-10) of whether the script or frame meets quality requirements.
- 🏗️ **`template_generator.py`**: Grows the template library — generates a NEW scene-arc archetype JSON from a brief (used by `scripts/grow_library.py` + `workflow_router`). Part of the nạp→học→tạo library loop.
- 🔌 **`seosona_bootstrap.py`**: Auto-bootstrap on import — checks env + loads config so every entry point starts from a known-good state.
- 🕸️ **`knowledge_graph.py`**: The queryable "second brain" — `recall/find/neighbors/related/stats/health/learned` over the structure graph + content notes (built by `scripts/gen_knowledge_graph.py` + `gen_knowledge_notes.py`; audited by `scripts/knowledge_audit.py`).

> [!NOTE]
> `pipeline_manager.py`, `video_capability_bridge.py`, and `video_template_factory.py` are RETIRED and have been removed from the project. Rendering now goes through `video_engine.py` → `native_composer.py`; templates are JSON files in `7_ASSETS/templates/` managed by `template_generator.py` + `template_picker.py` + the `scene-composer` skill (grown via `grow_library`).

</details>

---

## 💾 2. Memory Storage Space (`3_MEMORY/`)
The system does not lose its memory after shutdown. It records every experience into this directory.

<details>
<summary><b>📂 Long-term Memory Structure</b></summary>
<br>

- 🕸️ **`knowledge_graph/`**: Knowledge graph. A spider-web map linking entities together (e.g.: "Video A" `is made by` "Flow B" `based on` "Trend C").
- 🏦 **`context_bank/`**: Context Bank. Records successful contexts and prompts for reuse.
- 📚 **`project_log/` & `video_history/`**: Historical logs of each shipped video.
- 🚨 **`error_log/`**: The place that keeps network-drop and RAM-overflow errors so the system can self-analyze and fix mistakes on the next run.

</details>

---

## 📖 3. The Knowledge Vault (`2_KNOWLEDGE/`)
The home of the rules for ingesting input Data (Ingestion).

<details>
<summary><b>📥 Ingestion Sources</b></summary>
<br>

- 📑 **`INGESTION_INDEX.md`**: The supreme rule on ingesting external data (Web, PDF, Notion, Github) into the system safely and without information poisoning.
- 📦 **`raw_data/`**: The staging area for piles of raw data (messy HTML, uncleaned Text files) before being analyzed by `scraper_agent` / `trend_jacking_agent`.
- 🐙 **`repos/`**: Contains the source code of Github Repositories cloned down to be prepared as material for the `PR-to-Video` flow.

</details>
