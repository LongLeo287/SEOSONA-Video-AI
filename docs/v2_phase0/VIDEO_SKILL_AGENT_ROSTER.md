# Video-Production OS — Skill + Agent Roster (to build via the Builder)

The coordination team the OS command center needs to plan a video and command the Factory. Grounded
in real video-agent repos (2026-07-15 research). Anchors: **Director agent** (⚓ glue) +
**Reference-analyzer skill** (⚓ "soi video mẫu → công thức edit"). Each is BUILT via the Builder's
canonical AgentDefinition/skill templates → uniform, tested, auto-wired, conform-linted.

## Key architectural insights (from the research)
1. **The Director is GLUE, not a monolith** — every published system (ViMax MIT, MovieAgent, FilmAgent)
   makes "director" ONE persona in a crew that emits a TYPED plan. Keep planning (agent) separate from
   rendering (Factory). Our Director = an AgentDefinition that orchestrates the crew → a `ProductionCommand`.
2. **Reference-analysis (#2) ≡ QA-checker (#11)** — extract-formula-from-ref and check-output-against-formula
   share the SAME VLM+scene-detect core, run in two directions. BUILD ONCE, use twice.
3. **Transcript-as-interface** (video-use/freecut) — the agent reads a word-level transcript + occasional
   filmstrip PNG, never raw frames → cheap deterministic hard-cuts-per-audio + EDL. Fits our local-ASR stance.
4. **Most of the roster WIRES existing SEOSONA engines** (via the Factory) — only the Director glue,
   Reference-analyzer, and QA-checker are genuinely NEW. Good: the OS team is mostly assembly, not from-scratch.

## The roster (14 roles; ⚓ = anchor; disposition vs existing SEOSONA)
| # | Role | A/S | INPUT → OUTPUT | Source repo | Disposition | Pri |
|---|------|-----|----------------|-------------|-------------|-----|
| 1 | **Director agent** ⚓ | AGENT | `{brief, refFormula?, brandKit, archetype}` → `ProductionPlan{shotlist[], timing, style, captionStyle, voiceSpec, assetQueries[], renderCmd}` | ViMax, MovieAgent | **BUILD native** (glue over SEOSONA engines) | P1 |
| 2 | **Reference-analyzer skill** ⚓ | SKILL | `videoUrl` → `EditFormula{layout, subtitleStyle, perSecondTimeline[], transitions[], cutRate, palette, archetype}` | ai-video-editor, video-frames-skill | **EXTRACT** (scene-detect + interval-sample + VLM) | P1 |
| 3 | Script/copywriter agent | AGENT | `{topic, refFormula?, brandVoice}` → `Script{hook, beats[], vo_text, onScreenText[]}` | ShortGPT | SEOSONA `script_writer.py` → WIRE | P1 |
| 4 | Scene-planner/storyboard skill | SKILL | `Script` → `Shotlist[]{sceneId, dur, camera, motion, assetQuery, textRole}` | ViMax, VideoAgent | `director.py`/`plan_scenes` → EXTEND | P1 |
| 5 | Subtitle-stylist skill | SKILL | `{words[], style}` → ASS/SRT | opensource-clipping | ASS karaoke → PARAMETRIZE styles | P2 |
| 6 | Voice-director skill | SKILL | `{vo_text, personaSpec}` → `{voice.mp3, wordTimings[]}` | MoneyPrinterTurbo | `voice_router`/OmniVoice → WIRE | P1 |
| 7 | Asset-sourcer skill | SKILL | `assetQuery` → `{mediaPath, license, attribution}` | MoneyPrinterTurbo, VideoAgent | `image_sourcer` → EXTEND to b-roll | P2 |
| 8 | Template/archetype skills | SKILL | `{content, archetype}` → `TemplateSpec` | Remotion skills, HyperFrames | SEOSONA libs → ADD missing archetypes | P2 |
| 9 | Cut/EDL agent | AGENT | `{footage, transcript}` → `EDL{keeps[], cuts[]}` | video-use, freecut | `talking_head_autocut` → EXTEND | P2 |
| 10 | Music/SFX skill | SKILL | `{mood, beats[]}` → `{bgm.mp3, sfxCues[], credits}` | opensource-clipping | `bgm_sourcer`+`_sfx_cues` → WIRE | P2 |
| 11 | **QA/checker agent** ⚓ | AGENT | `{renderedVideo, EditFormula\|brief}` → `QAReport{score, mismatches[], fixes[]}` | eval_judge + reuse #2 | **BUILD** (run #2 on own output) | P1 |
| 12 | Thumbnail skill | SKILL | `{video, title}` → thumbnail.png | opensource-clipping | `thumbnail_maker` → WIRE | P3 |
| 13 | Repurpose skill | SKILL | `longVideo` → `Clip[]{start,end,score,crop}` | AI-Youtube-Shorts-Generator | EXTRACT (virality scoring + crop) | P3 |
| 14 | Render-factory skill | SKILL | `ProductionPlan` → video.mp4 | Remotion, HyperFrames | `native_composer`/`video_engine` IS the factory → formalize contract | P1 |
| 15 | **Publisher agent** | AGENT | `{video, meta, platforms[]}` → `PublishReport{postUrls[], status}` | legacy `youtube_uploader` | **BUILD** (multi-platform: TikTok/Reels/Shorts/Threads/YT) — public post = human-gated | P2 |
| 16 | **Reporter agent** | AGENT | `{postUrls[]}` → `PerfReport{views,retention,winners[]}` → feeds Director | legacy `performance_ingest`/`factory_ledger` | **BUILD** (post-publish analytics → learning loop) | P3 |
| 17 | **Semantic asset index** ⭐ | SKILL | `footageLib` → `AssetIndex{hash, tags[], embedding}` ; `query` → `matches[]` | bachdyon (REFERENCE) | **BUILD keyless** (content-hash + local VLM/embedding index of OWNED footage — the missing half of #7) | P2 |
| 18 | Shot-coverage planner | SKILL | `Shotlist` → `Coverage{gaps[], fill:cutaway\|hold\|kenburns\|slow}` | bachdyon (REFERENCE) | EXTEND #4 (decide coverage when footage is thin) | P3 |
| 19 | Dynamic overlay placement | SKILL | `{frame, subjectBox}` → `safeRects[]` | bachdyon (REFERENCE) | EXTEND #5/#11 (subject-aware, beyond static safe-zone) | P3 |

GAPs #17–19 came from the bachdyon REFERENCE analysis (see `BACHDYON_REFERENCE_ANALYSIS.md`) — build keyless/local, adapted to SEOSONA engines, never vendored.

## North-star vision coverage (the "own an AI video agent" scope the user stated)
The full **content-workshop pipeline** is longer than production alone:
`nhận ý tưởng → nội dung → dựng → kiểm tra → LƯU TRỮ → ĐĂNG ĐA NỀN TẢNG → BÁO CÁO`.
Roles #1–14 cover *idea→checked video*. The vision adds the tail: **storage** (already the OS
`storage` package + run-dir), **publish** (#15, NEW), **report/learning-loop** (#16, NEW). "Sản xuất
nhiều video cùng lúc" = orchestrator queue+daemon (BUILT). "Bạn = giao việc + duyệt" = OS command
center + human gates (BUILT).

### The 7 named formats → concrete archetypes (role #8, not generic)
tin-tức (news) · podcast · kể-chuyện (storytelling) · nhân-hiệu (personal-brand talking-head) ·
Threads · bán-hàng (sales/DR) · short-form (TikTok/Reels/Shorts). Each = a `TemplateSpec` archetype
with its own hard-rules seed; new formats can be added later (tool-independent, per the vision's
"không bị đóng khung trong một mẫu").

## TOP 8 to build first (minimum viable video OS)
1. **Director agent** ⚓ (glue) → 2. **Reference-analyzer skill** ⚓ (soi mẫu) → 3. Render-factory contract (wire native_composer) → 4. Script agent (wire script_writer) → 5. Scene-planner (extend director.py) → 6. Voice-director (wire OmniVoice, return word-timings) → 7. **QA-checker agent** (reuse #2 on own output = self-correcting loop) → 8. Subtitle-stylist (parametrize ASS karaoke).

Anchors #1 Director + #2 Reference-analyzer + #14 Render-factory = the MVP: analyze a reference → plan →
command the Factory. #11 QA closes the loop by reusing the analyzer.

## License notes
ViMax + MoneyPrinterTurbo = MIT (adopt/extract). MovieAgent/ShortGPT/AI-Youtube-Shorts = unclear →
pattern EXTRACT only, verify before copying. HyperFrames = noncommercial per prior SEOSONA verdict →
learn craft, don't lift code (we drive it as the render Factory, not vendor it).

## 🔒 BRANDING STANDARD — SEOSONA-owned, no third-party names (user rule)
"chuẩn hóa đừng gắn tên của những người khác vào của tôi." Every generated skill/agent/contract:
- `metadata.author` = **SEOSONA** (never LoHa Tech / bachdyon / higgsfield / any third party).
- NO third-party personal/studio/product brand in `name`, `description`, filename, headings, or body.
  Banned: LoHa(-Tech), bachdyon, higgsfield, "ViralCrawl", `hermes_terminal`/`hermes_chat`
  (→ rename generic: `terminal_mockup`, `chat_mockup`), any "© X" footer.
- Template files in `D:\SEOSONA AI\SKILL TEMPLATE` are **CRAFT SOURCES ONLY**: learn the technique,
  WRITE FRESH prose — never copy their sentences verbatim (noncommercial/others' copyright → verbatim
  copy = license-laundering AND stamps their identity on the product).
- External ENGINE/product names (Seedance, HyperFrames, OmniVoice, ffmpeg) appear only where naming the
  actual tool driven, as a capability — never as the skill's brand. Capability names: `reference-analyzer`,
  `shotlist-director`, `render-factory` (NOT "loha-video-maker", NOT "seedance-clean").
- Provenance (repo a technique came from + license) lives in the **vetting/ingestion log**, not on the
  shipped skill. Product stays clean; the honesty-record stays separate. (This matches the noncommercial-
  REFERENCE discipline: we vendor neither their code nor their name.)

## CANONICAL SKILL FORMAT — structure learned from the user's templates (`D:\SEOSONA AI\SKILL TEMPLATE`)
(Format only — the IDENTITY is SEOSONA's per the branding standard above.)
The Builder's skill template MUST match the user's proven format (model: `loha-video-maker_SKILL.md`):
```
--- YAML: name · description (incl. "Dùng khi user nói…" = the trigger) · metadata{type,author,version} ---
# <emoji> <skill-name> — one line
## Prerequisites (what it needs: engines, venvs, assets)
## Modes + Spec formats (concrete JSON schemas the skill consumes)
## Run (the exact command)
## 🔴 RULE CỨNG (bài học — VI PHẠM = LÀM LẠI)   ← the lessons-from-mistakes section, MANDATORY
```
The **RULE CỨNG (hard rules from mistakes)** section is the highest-value part — it encodes the lessons
(e.g. "TEXT/PHỤ ĐỀ ≠ PHIÊN ÂM", "HOOK FULL Ở FRAME ĐẦU", "VERIFY trước khi giao — KHÔNG bịa", karaoke
safe-zone, cards don't cover the face, diverse SFX). Every generated skill carries this section (it is the
conform-lint's "hard rules present" check + matches the OS fail-honest invariant).

**Archetypes already in the user's folder** (→ the Template/archetype skills #8, and their hard-rules seed):
faceless-scene-slides (spec.json + scenes.json + sfx.json → run_video) · footage-edit (neon cards + karaoke +
UI mockup cutaways) · shotlist-director (higgsfield/seedance) · audio-driven-broll-montage (TikTok audio +
raw-clip illustration, black bg + rounded frame) · talking-head · 2D-anime-sticker · expert-short-form.

**Planning discipline** (`plan skill.txt`, → fold into the master-prompt): review/audit → a long staged plan →
work for other models to execute → **"Data First, Plan Second"** (plan from real project data, not assumptions)
→ spin up fresh-context subagents to verify execution matched the plan. (This is exactly the session's method.)

**Source repo** = `bachdyon/video-automator-skills` (the mature agent in the user's screenshots; already
cloned+deep-read; **noncommercial → REFERENCE**: learn the craft/skill-packaging, do not vendor code).

## How these get built (Builder discipline)
Each role → an AgentDefinition (agents) or a skill (SKILL.md) generated from the canonical template →
uniform shape, mandatory test, auto-wired to the registry (no orphan), conform-linted. The Director's
output `ProductionPlan`/`ProductionCommand` is what the OS sends DOWN to the Factory (`FactoryApp`).
