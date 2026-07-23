# Operating System Integration (SEOSONA OS Integration)

This repository is not a free-floating standalone application. It is tightly bound to and obeys every command from the "Heart" of the **SEOSONA OS** operating system (located at `~/.seosona` or `D:/SEOSONA OS`).

## 🔗 1. The Bridge Scripts
Located in the `scripts/` directory, these are the "cables" that communicate between the Video Factory and the OS.

<details open>
<summary><b>🔀 Expand the Communication Cables</b></summary>
<br>

- 🔌 **`seosona-project-bridge.cjs`**: The main network cable. Helps the OS recognize which Workflows this Repository has and command the launch of the corresponding Node.js flow.
- 🐍 **`seosona-python.cjs`**: The Python cable. Helps the Node.js environment call Python commands (PhoWhisper ASR, OmniVoice TTS) smoothly without environment variable errors.
- 🏥 **`seosona_doctor.py` & `seosona-project-audit.cjs`**: The doctor duo. Always run a health check of the project (check for missing libraries, verify the Node version) before hitting the Render button.
- 🏗️ **`4_BRAIN/native_composer.py`**: The native render engine — auto-generates HTML/CSS/GSAP, builds scenes + karaoke subtitles, and renders HyperFrames for the synthesized video flow (replacing the old retired `build_news_project.mjs`).

</details>

> [!CAUTION]
> **UAP EXCLUSIVE (Universal Autonomous Process)**
>
> The entire *Review Repo -> Clone Repo -> Analyze, learn -> Ingest, create, upgrade -> Clear Repo* process is the supreme prerogative of the SEOSONA OS operating system, used for self-evolution.
> The SEOSONA Video project is **absolutely forbidden** from owning, executing, or simulating this process (such as naming a directory `repo_analyzer`) in order to avoid collision and functional overlap at the OS level.

---

## 📜 2. Startup Contracts
Every time it starts up, the system is required to read and comply with the Parent Constitution files.

<details open>
<summary><b>⚖️ The Core Laws</b></summary>
<br>

- 🆔 **`seosona.project.json` (Project Manifest)**:
  The project's citizen ID. Clearly declares: the memory space belongs to `seosona-video`, the autonomy level is `project_edit`. Publishing videos to platforms (Publish) requires the User's permission.
- 🧠 **`AGENTS.md` (SEOSONA OS Rules)**:
  The contract requiring any AI Agent entering this project to point back to SEOSONA OS to read the soul (`~/.seosona/1_CORE/SOUL.md`) and the knowledge (`~/.seosona/2_KNOWLEDGE/MASTER_INDEX.md`) before working — these are SEOSONA **OS** paths (external), not this repo's.
- ✨ **`GEMINI.md` / `.clauderules` / `.cursorrules`**:
  The separate rule sets that force AI models (such as Gemini, Claude, Cursor) coding in this repo to strictly comply with SEOSONA's standards:
  - Must use the `seosona-task-intake` skill when receiving a task.
  - Must create `implementation_plan.md` before coding.
  - Must write `walkthrough.md` after completion.

</details>

> [!WARNING]
> Any source code modification that breaks the connection of the `Bridge` files or violates the `Contracts` above will throw the entire SEOSONA Video Factory out of the SEOSONA OS ecosystem and paralyze it completely.
