# Workflows and Graphics Frameworks

This document lists the high-level orchestration systems (Workflows) and the rendering Frameworks of SEOSONA Video.

## 🧠 21 Workflows (Agentic Workflows)
Located in `.agents/skills/`. These are the combination of Agents (Layer 1) and Python Skills (Layer 2) to form end-to-end automation machines.

<details>
<summary><b>🎬 Full-Package Video Production Group (8 Workflows)</b></summary>
<br>

- 🌟 **`seosona-news-maker`**: Super Native Pipeline that creates 9:16 TikTok news videos extremely fast and clean.
- 👤 **`faceless-explainer`**: Process for making fully faceless news/explainer videos.
- 🚀 **`product-launch-video`**: Builds product advertising videos with flashy effects.
- 💻 **`pr-to-video`**: Turns a line of new code (Github Pull Request) into a feature explainer video.
- 🌐 **`website-to-video`**: Takes a tour of any website and records the screen automatically into a video.
- 🎞️ **`general-video`**: Fallback render tool for all custom video cases.
- 🤖 **`heygen-native-api`**: Calls HeyGen v2 API to generate a talking virtual Avatar.
- 👕 **`heygen-skills`**: HeyGen Avatar fine-tuning commands (Position, Green Screen, Wardrobe).

</details>

<details>
<summary><b>⚙️ HyperFrames & Graphics Group (9 Workflows)</b></summary>
<br>

- 🎛️ **`hyperframes`**: Central control station of the HyperFrames Engine.
- 🌀 **`hyperframes-animation`**: Library of motion, bounce, and rotation effects (GSAP, CSS Keyframes).
- ⌨️ **`hyperframes-cli`**: Command-line toolset (init, render, publish, lint).
- 🧱 **`hyperframes-core`**: The HTML/CSS structural contract that every file must comply with.
- 🎨 **`hyperframes-creative`**: Art director (decides color palette, fonts, layout).
- 🎵 **`hyperframes-media`**: Transfer station that polishes assets before feeding them into the casting mold.
- 🧩 **`hyperframes-registry`**: Manages UI blocks/components (such as code cards, statistics cards).
- ⚛️ **`remotion-to-hyperframes`**: Reverse-translates Remotion's React code into HyperFrames HTML code.
- 📊 **`motion-graphics`**: Generator for Kinetic Typography and animated Data-Visualization imagery.

</details>

<details>
<summary><b>🔤 Effects & Management Group (4 Workflows)</b></summary>
<br>

- 🅰️ **`embedded-captions`**: Burns subtitles tightly into an existing video (Cinematic/Karaoke effects).
- 🏷️ **`graphic-overlays`**: Pastes floating info cards (Card, Lower-third) onto the original video.
- 🎬 **`scene-composer`**: The content brain — picks a JSON template and pours the script into the frame via `native_composer.fill_template`.
- 🧠 **`seosona-video-operator`**: Central control circuit that commands all remaining flows.

</details>

---

## 🎨 9 Graphics Frameworks (Frameworks)
Located in `5_FRAMEWORK/`. Where static HTML files transform into masterpieces at 60 frames/second.

<details>
<summary><b>🖥️ Expand the Frameworks list</b></summary>
<br>

1. **`hf_engine/registry`**: The canonical HyperFrames block + component library (97 blocks, 25 components).
   `4_BRAIN/hf_blocks.py` renders any block to a clip; the actual render uses the npm `hyperframes` CLI.
2. **`hf_producer_render.mjs`**: Optional Producer-API render helper (legacy; the live engine is `native_composer`).
3. **`publish/`**: Playwright publish framework (gated, human-in-loop).

*(Removed/retired and no longer present: `hf_cards`, `hf_core`, `html_renderer` (its 2 live thumbnail
templates moved to `2_SKILLS/thumbnail_maker/templates/`), `hyperframes` (upstream docs), `loop-source-seosona-clone`,
`moviepy_wrapper`. Rendering is handled by `native_composer` via the HyperFrames CLI.)*
8. **`news_loop_path_hyperframes`**: Animated background running an infinite loop for news videos.
9. **`news_spatial_hyperframes`**: Simulated 3D space for vertical 9:16 aspect ratio videos.

</details>
