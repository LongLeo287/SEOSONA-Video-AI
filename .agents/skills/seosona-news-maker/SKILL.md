---
name: seosona-news-maker
description: >
  Make SYNTHESIZED SEOSONA videos (auto-generated) — news, knowledge explainers, repo/tool
  showcase — 9:16 (default) or 16:9, light-mode, AI voice (VieNeu clone), karaoke captions (RULE #1),
  components (bignum/repo/compare/terminal/steps/badges/stats/quote/tip/feature/chart/mockup/
  gittree/cta), SFX + BGM ducked. Use when the user says "make a news video / explainer /
  introduce a repo / make a video from a GitHub link / from a script". Engine: video_engine → native_composer.
  (To edit self-shot footage / talking-head → use the `talking-head-video-editor` skill.)
metadata:
  type: skill
  author: SEOSONA AI
  version: "2.0"
---

# 🎬 seosona-news-maker — auto-generated (synthesized) SEOSONA video

Skill for the **synthesized engine**: generate scenes from content (text / GitHub repo / news brief),
VieNeu AI voice, render brand-native with HyperFrames. This is 1 of 2 video-making engines:

- **This skill (synthesized)** — the machine builds scenes + AI voice. → news, explainers, showcase.
- **`talking-head-video-editor`** — edit self-shot/screen-rec footage, REAL voice. → reviews/tutorials/intros filmed by a person.

## 0. Engine + commands (verified to actually run)

| Task | Command |
|---|---|
| GitHub repo → video (auto template) | `npm run make:video -- <github_url_or_owner/name>` |
| Landscape 16:9 (YouTube) | `npm run make:video -- <url> --aspect 16:9` |
| Batch news (multiple repos, rotating templates) | `python 4_BRAIN/make_video.py --news urls.txt` |
| From a Vietnamese script / website URL | `npm run video:news -- "<script_or_url>" [project] [ratio]` |

**Aspect ratio:** default 9:16; set `"aspect":"16:9"` in the template JSON or `--aspect 16:9` (CLI) for landscape (1920×1080). Supports `9:16` · `16:9` · `1:1`.

**Output** (`8_WORKSPACE/<project>/`): `*.mp4` + `*.srt` (in `_captions_upload/`, to keep the player from auto-loading and overriding the karaoke) + `Thumbnail/thumbnail.png` + `publish_report.json` (if `SEOSONA_PUBLISH` is enabled) → all pass through the quality gate.

**Core:** `4_BRAIN/video_engine.py` (routing + quality gate) → `4_BRAIN/native_composer.py`
(voice via `voice_router` VieNeu, timing via `srt_maker/asr_router`, render with HyperFrames CLI,
mix SFX+BGM). Brand/voice/logo profiles are read from `system_config.yaml`.

## 1. Content — 2 ways

- **Automatic (1 command):** `make_video.py` automatically fetches real GitHub data + fills in Vietnamese prose per the template.
- **High quality (agent):** use the **`scene-composer`** skill to compose `content` (segments + 2-tone heading + scene_data) then call:
  - `native_composer.make_video_from_template(template, content, project_dir)` — based on one of the JSON templates.
  - `native_composer.make_video_custom(project_dir, scenes_spec)` — freely assemble scenes from the 14 components.

## 2. Template JSON (`7_ASSETS/templates/*.json`) — scene structure (component + accent + kicker)

`ai-news-flash` · `benchmark-news` · `data-news` (news/figures) · `insight-explainer` ·
`opinion-insight` · `seo-explainer` · `tutorial-gittree` (knowledge/explainers) ·
`repo-showcase` · `tool-walkthrough` · `resource-list` (repo/tool/library).
Save a good render as a new template: `native_composer.extract_template(...)`.

## 3. Components (14) for each scene
`bignum` (big number) · `repo` (repo card) · `compare` (2 columns) · `terminal` (commands) · `steps` (steps) ·
`badges` · `stats` (3 number cards) · `quote` · `tip` (💡) · `feature` · `chart` (bar) · `mockup` (browser) ·
`gittree` (git log) · `cta`. Accent: `blue` `green` `orange` (light-mode, brand palette).

## 🔴 HARD RULES
1. **TEXT/CAPTIONS = DISPLAY FORM, NOT PHONETIC**: write `AI` `24/7` `GitHub` correctly on screen; how it is READ is handled separately via the `lexicon` (native_composer uses `news_video_standards.PRONUNCIATION_LEXICON`). Captions show the DISPLAY word, not the sound.
2. **FULL HOOK AT FRAME 0**: scene 0 shows the full kicker + heading right at second 0 (frame 0 = platform thumbnail).
3. **KARAOKE in safe zone**: the word being spoken is highlighted yellow, keywords highlighted in accent; not flush against the bottom.
4. **LIGHT MODE ONLY**: no dark background; brand palette (blue `#2A5BDA`, coral `#E2724D`, green `#16A34A`). Scenes crossfade — no white frames.
5. **VOICE**: VieNeu (clone > "Trọng Hữu" preset) → fallback edge-tts; male, Southern Vietnamese. Do NOT write phonetics into the text.
6. **Varied SFX** + **BGM ducked** under the voice (already automatic in native_composer).
7. **VERIFY before delivery** (real data, no fabrication): no black frames (YAVG>12), loudness ~-16 LUFS, duration matches the brief, captions match brand spelling/figures, components not empty.

## Not done in this skill
- Do not edit self-shot footage / talking-head here → use the `talking-head-video-editor` skill.
- The ONLY engine is `native_composer` — do not recreate the old render pipeline.

*Skill exclusive to SEOSONA AI. Engine: video_engine → native_composer (HyperFrames-native, no external pipeline dependency).*
