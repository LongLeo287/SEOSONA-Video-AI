# Operating Constitution (SOP Index)

No line of code running in the SEOSONA Video system may violate these 23 iron laws. All SOP files are stored in the `6_SOP/` directory. Click each group to see the detailed laws (the list below covers representative SOPs and may not cover all 23 — for example there are also `REFERENCE_TO_VIDEO_SOP.md`, `TEMPLATE_MAP.md`...).

<details>
<summary><b>🛠️ Group 1: System Operations Laws</b></summary>
<br>

Defines how Servers, Agents, and APIs talk to each other.

- ⚙️ **`MASTER_OPERATION.md`**: The Supreme Operating Procedure of the system.
- 🚧 **`SEOSONA_WORKFLOW_BOUNDARY_MAP.md`**: Map of the boundaries the flows must not cross.
- 🔌 **`SEOSONA_VIDEO_RECONNECTION_MAP.md`**: Diagram for reconnecting the system's circuits when they break.
- 🧩 **`HYPERFRAMES_INTEGRATION.md`**: HyperFrames integration procedure.
- 🏭 **`SEOSONA_VIDEO_AUTONOMOUS_TEMPLATE_FACTORY.md`**: Factory for automatically casting video template models.

</details>

<details>
<summary><b>🎨 Group 2: Aesthetics & Ethics Laws (Design & Ethics)</b></summary>
<br>

Defines rules for colors, aspect ratios, and the ethical boundaries of the AI.

- 💎 **`UX_UI_DESIGN_GUIDELINES.md`**: Aesthetic standards (no garish colors, no ugly fonts, spacing rules).
- 🎙️ **`brand_voice_sop.md`**: Positioning of the SEOSONA brand voice.
- 🖼️ **`thumbnail_sop.md`**: Laws on contrast and face area on Thumbnails.
- 🎠 **`carousel_sop.md`**: Design laws for a Carousel slide post (LinkedIn/Insta).
- ⚖️ **`voice_cloning_tts_sop.md`**: Ethical principle: Only clone internal voices, political impersonation strictly forbidden.

</details>

<details>
<summary><b>🎬 Group 3: Production & Content Laws</b></summary>
<br>

The secrets for keeping viewers and meeting multi-platform SEO standards.

- 🎥 **`video_production_sop.md`**: Basic end-to-end production line.
- 🧠 **`SEO_CONTENT_STRATEGY.md`**: Hook strategy and viewer retention.
- 🗣️ **`VOICE_TTS_ENGINE_ROUTING.md`**: Voice routing law: **OmniVoice is the ONLY engine** (2026-07-14) — no backup, a failed synth returns None. Single router, no dead branches; VieNeu/edge-tts/F5/kokoro/sherpa/LoRA/fish removed.
- 🕵️‍♂️ **`tech_news_faceless_sop.md`**: Formula for repackaging tech news (faceless).
- ✂️ **`repurposer_sop.md`**: Law for recycling a long video into 5 short videos.
- 🏷️ **`youtube_seo_sop.md`**: Formula for stuffing Keywords into YouTube descriptions.
- ▶️ **`YOUTUBE_CHANNEL_OPERATIONS_MCP.md`**: Handbook for automated YouTube channel administration.
- ✅ **`publishing_checklist.md`**: The 10-point critical checklist to verify before hitting the Publish button.
- 🚨 **`EVAL_FLYWHEEL.md`**: qualitative QA — `eval_judge.py` (Gemini-vision) + `evaluator.py` (blank/black-frame + loudness gate) score every video and feed the flywheel.

</details>
