# SKILL TEMPLATE — Craft Analysis (REFERENCE only)

**Scope:** every file in `D:\SEOSONA AI\SKILL TEMPLATE` (12 files) analysed 2026-07-15.
**Discipline:** these are **craft sources**, not code to vendor. Learn the technique, write fresh
prose, strip third-party identity, do **not** import their toolchain. Provenance + license live in the
vetting log (`2_KNOWLEDGE/INGESTION_LOG.md`), never stamped on a shipped SEOSONA skill.
**Branding rule enforced:** no LoHa / bachdyon / higgsfield / ViralCrawl / `hermes_*` names carried into
V2; external engine names (Seedance, HyperFrames, OmniVoice, ffmpeg) appear only as the *capability being
driven*, never as a skill's brand. Roster role numbers refer to `VIDEO_SKILL_AGENT_ROSTER.md` (16 roles).

---

## Quick map (file → lesson → roster role → disposition)

| # | File | What it is | Highest-value craft to EXTRACT | Third-party names to STRIP | Foreign toolchain to NOT import | Maps to V2 engine / role | Disposition |
|---|------|-----------|-------------------------------|----------------------------|--------------------------------|--------------------------|-------------|
| 1 | `bachdyon.txt` | Two source links (repo + catalog) | See `BACHDYON_REFERENCE_ANALYSIS.md` | bachdyon | — | Whole roster | REFERENCE |
| 2 | `2D Anime Sticker Composite Funny Short Video.txt` | A single Seedance 2.0 prompt (live-action + flat 2D chibi sticker composite, POV cooking gag) | Timecoded 4-shot beat structure filling a fixed clip length; cartoon-SFX sync per beat; "real hand + flat 2D sticker never relit" composite rule as an *explicit lock* | Seedance | Seedance paid gen | Engine #6 `seedance_director.py` (#1 Director → #14 Factory) | REFERENCE (one worked prompt) |
| 3 | `EXPERT SHORT-FORM VIDEO.txt` | System prompt: SRT → non-linear short-form production script (VN) | **Non-linear splicing**: cherry-pick strongest lines across a long transcript into hook→pain→tip→case-study→CTA; 100% raw-dialogue preservation, fix spelling **only** in the on-screen-text column; per-line timecode + FX/SFX/transition column | — | — | Script agent (#3), Repurpose (#13), Subtitle-stylist (#5) | EXTRACT (structure + splicing rule) |
| 4 | `huong-dan-prompt-seedance-2.0_1.pdf` | VN reference guide: Seedance 2.0 prompt grammar (6 pp) | 1 prompt = 1 clip ~15s, fill the clip (no dead air); verbatim Style-Prefix atop; `@tag` Element registry; **location = style reference, not keyframe**; camera always with a *reason*; act via concrete behaviour not emotion words; 60:30:10 color; slow-mo opt-in; `@scheme` aerial-layout to pin positions | Seedance | Seedance paid gen, KIE | Engine #6 `seedance_director.py` (already partly built; PDF confirms grammar) | REFERENCE (grammar already ingested; re-verified) |
| 5 | `higgsfield-seedance-shotlist-director.skill` (zip → `SKILL.md`) | A skill: script → editable **shotlist HTML** (checkbox + copy + localStorage), one 15s prompt per beat | Director-not-transcriber framing; mise-en-scène/geo-spatial blocking; continuity held in-language (never a visible block); per-scene one checkbox even when split 3a/3b/3c; self-contained HTML artifact for hand-off | higgsfield, Seedance; dark `#0e0e10` palette | Their HTML/CSS verbatim; dark theme | Engine #6 shotlist output (already built in `seedance_director.py`, SEOSONA **light** brand) | REFERENCE (pattern already adopted) |
| 6 | `prompt-writter.skill` (zip → `seedance-clean/SKILL.md`) | The most advanced Seedance prompt system: **distributed-style** (no top prefix), FOV-in-degrees anchor table, optical technique stack | **FOV anchor table** (discrete degrees 8°–180° ↔ shot purpose); "**write the visible**" (measurable, not mood words); **positive-only** phrasing; quantify — speed in km/h, atmosphere in %/meters, giants by human-height; **hidden-camera / observation optical stack** (foreground occlusion + haze + super-tele); **4-mechanism extreme-FOV consistency stack**; **anti-impact crack locks**; camera block in 3rd position | Seedance | Seedance paid gen | Engine #6 `seedance_director.py` — **fold these refinements in** (see §"Build backlog") | EXTRACT (net-new refinements) |
| 7 | `loha-video-maker_SKILL.md` | The canonical SKILL format: faceless scene-slides + footage-edit, 2 modes, hard-rules | **Canonical SKILL shape** (YAML name/description-with-trigger/metadata → Prereqs → Modes+JSON schemas → Run → **RULE CỨNG**); **TEXT ≠ PHIÊN ÂM** (display text vs pronunciation lexicon are separate); HOOK full at frame 0 (= platform thumbnail); one component per scene; VERIFY-before-deliver (extract frame, loudness ~-16 LUFS, duration, no-fake) | LoHa Tech, 9Router, ViralCrawl, Hermes, F5-TTS | `build_scene_slides.py`, `run_video.ps1`, `edit_footage.py`, `.venv-f5`, F5-TTS, HyperFrames-as-their-repo | Format template for **every** generated skill; maps to `native_composer` + OmniVoice + PhoWhisper | EXTRACT (format + hard-rules) |
| 8 | `LOHA-VIDEO-NEON_Huong-Dan.md` | Student guide: talking-head footage → studio-grade short (neon cards, mockups, studio mode) | **Studio Mode auto-shrink**: the speaker frame *shrinks itself* to make room for a card (keep aspect, never crop the face); cards placed **opposite the face**; full-screen mockup cutaway ⇒ no card at the same instant; **spelling-fix pass is mandatory** (worst error = wrong caption); typing pre-baked span-by-span (seek-safe) | LoHa Tech, ViralCrawl, UltraViewer example, Whisper large-v3, F5 | `build_studio_neon.py`, `transcribe_v2.py`, `.venv`/`.venv-f5`, `capture_shot.ps1`, `loha-video-pipeline` | Talking-head engine (`talking_head_edit.py`) + QA (#5/#11) — **adopt dynamic auto-shrink** | EXTRACT (auto-shrink craft) |
| 9 | `Video_Automator_Skills_Tong_Hop_Report.docx` (zip → `word/document.xml`) | A prior VN synthesis report on bachdyon VAS + Seedance + talking-head node spec | Full pipeline map (job → VDS → creative plan → **voiceover-approval gate** → voice/transcript → asset index → mapping → coverage → render → QA); **Asset Index** as the differentiator (content-hash idempotent, VLM semantics, embedding search, reuse across stages); talking-head node = original-footage **hard lock** + 2-word captions | bachdyon, VAS, HeyGen, AusyncLab, CapCut, KIE, fal, Gemini/OpenAI keys | Gemini/OpenAI-dependent index, CapCut unofficial flow, HeyGen avatar, Remotion | Confirms roster; **local semantic asset index** = GAP for #7/#4 | REFERENCE (synthesis; not authored by us) |
| 10 | `talking-head.txt` | A talking-head editing brief (VN) — the "cinematic reel" prompt | Preserve subject/audio/wardrobe/background **absolutely**, add layers only; ≤2 words per caption synced to speech; **bold cinematic layered typography** (keyword plates behind speaker, partially masked = depth); **extract palette from the footage**, gradient/glow to *blend not clash*; SFX synced to emphasis beats with ducking | — | — | Talking-head engine (`bigword`/`caption_chunk:2` already built) + Subtitle-stylist (#5) | EXTRACT (palette-from-footage + masked-depth) |
| 11 | `template video 2.txt` | A user brief: TikTok-audio-driven b-roll montage (black bg + rounded illustration frame) | **Audio-driven montage archetype**: borrow one audio track, illustrate each spoken line with the *emotionally-richest* cut of raw footage that matches meaning; black bg + rounded framed viewport (10% side / 30% top-bottom margins) | (TikTok handles in URLs) | — | Archetype #8 (new: audio-driven-broll-montage) + Asset-sourcer/Cut (#7/#9) | REFERENCE (archetype seed) |
| 12 | `plan skill.txt` | A 4-line planning meta-prompt | **"Data First, Plan Second"** — plan from real project data/structure/history, not assumptions; long staged plan → work for other models → spin fresh-context subagents to verify execution matched the plan | — | — | Director/OS planning discipline (#1) | EXTRACT (planning method) |

---

## Per-file detail

### 2 · `2D Anime Sticker Composite Funny Short Video.txt` — Seedance worked prompt
A single ready-to-run Seedance 2.0 prompt for a comedic POV-cooking clip compositing a photoreal human
hand with a flat 2D chibi "sticker" character. **Reusable craft:** (a) the clip is divided into four
timecoded shots (0–3s / 3–5s / 5–8s / 8–10s), each with its own beat and its own SFX cue — proof of the
"fill every second, timecode every shot" rule; (b) the composite constraint ("maintains pure 2D flat
texture throughout, **not relit** by real lighting") is stated as an explicit lock, the way Seedance
prompts must pin failure-prone details. **For V2:** a fixture example only; the grammar is encoded in
`seedance_director.py`. Strip "Seedance" as a brand (it is the driven capability). No toolchain.

### 3 · `EXPERT SHORT-FORM VIDEO.txt` — non-linear SRT → production script
A VN system prompt that turns a raw `.SRT` into a high-retention short by **non-linear splicing**:
cherry-pick the strongest lines scattered across the source, stack them into a fast-paced arc
(HOOK 0–5s → PAIN 5–15s → TIP/step-by-step 15–45s → CASE STUDY 45–75s → SUMMARY+CTA 75–90s), and emit a
multi-column table (section · exact timecode · **raw** dialogue verbatim · visual/on-screen-text ·
FX/SFX/transition). Two hard rules worth adopting: **100% raw dialogue preservation** (never paraphrase
the spoken column; fix spelling only in the on-screen-text column) and **strict file isolation** (one
script from one source only). **For V2:** upgrades the Script agent (#3) and the Repurpose skill (#13)
with a concrete retention skeleton + the raw-vs-display split that mirrors LoHa's TEXT≠PHIÊN ÂM lesson.

### 4 · `huong-dan-prompt-seedance-2.0_1.pdf` — Seedance grammar reference (6 pp)
The canonical VN grammar guide. Core laws: **1 prompt = 1 clip ~15s**, fill it (split long scenes into
Na/Nb/Nc, each self-contained with its own Style-Prefix); **location is a style reference, not a fixed
keyframe** (the model extends the world, the subject moves through it); **camera always has angle +
height + movement + a reason**; **act by concrete behaviour** ("eyes wide, lips parted, half-beat freeze"
— not "he's surprised"); **60:30:10** dominant/secondary/accent color per shot; slow-mo is opt-in;
avoid named IP/real people/brands; `@tag` every recurring person/prop/location and use `@scheme`
(top-down aerial layout) to pin positions across cuts. The fixed block order is
SUBJECT → LOCATION → [LAYOUT] → ACTION (timed SHOTs + Hard cut) → CAMERA → STYLE → CONSTRAINTS
(16:9, slow-mo?, scale locks, continuity, **NO eye glow**). **For V2:** already encoded in Engine #6;
this pass re-verifies it firsthand. REFERENCE.

### 5 · `higgsfield-seedance-shotlist-director.skill` — script → shotlist HTML
A skill that reads a script "as a director, not a transcriber" and emits a single **self-contained HTML
shotlist** — collapsible global Style-Prefix, numbered scenes, per-scene checkbox that persists in
`localStorage`, per-prompt copy button, each prompt a 15s block (CUT 1/2/3 with lens+move+beat). Craft to
keep: mise-en-scène/geo-spatial blocking ("she sits across from him, knees touching under the table"
beats "they sit and talk"); **continuity tracked in your head, never written as a visible block**; one
checkbox per scene even when split 3a/3b/3c; revisions re-render the same file. **For V2:** the shotlist
HTML artifact is already adopted in `seedance_director.py` at SEOSONA **light** brand — their dark
`#0e0e10`/`#d4a259` palette and their HTML/CSS are **not** copied. Strip "higgsfield". REFERENCE.

### 6 · `prompt-writter.skill` (seedance-clean) — advanced Seedance system
The richest of the three Seedance sources and the one with **net-new** technique beyond what Engine #6
currently encodes:
- **Distributed style, not a prefix** — every style aspect (lighting/color/optics/physics/acting) lives
  inside the block it governs; only technical format (resolution/grain/fps) stacks as a suffix; the
  prompt opens on SCENE CONTEXT, never a style block.
- **FOV anchor table** — use discrete degrees (180°/107°/84°/63°/47°/29°/18°/12°/8°) mapped to shot
  purpose, in the prompt text (mm only for the writer's head). **Camera block in 3rd position** — moved
  to the end, FOV is ignored; to the front, it fights identity.
- **Write the visible** — translate every abstraction into something measurable; **positive-only**
  phrasing (state the target, never the prohibition); **quantify** — speed in km/h, atmosphere in
  %/meters, giants by "as tall as N humans stacked", left/right from the camera, atmosphere builds in
  steps across shots.
- **Optical techniques** — hidden-camera/observation stack (foreground occlusion 20–30% + haze +
  super-tele 8–12°); sports-broadcast tremor; detail-on-wide "snake cam"; compressed-air-column tele.
- **Special protocols** — 4-mechanism consistency stack for extreme-FOV multishots; whip-pan timing
  (<0.8s renders as a hard cut, no blur); mixed time-speed = hard cuts only between speed modes;
  anti-impact "pressure-based crack" locks.
**For V2:** fold the FOV-degree table, distributed-style option, positive-only + quantification rules,
and the optical/consistency protocols into `seedance_director.py`'s grammar + `lint_prompt`. EXTRACT.

### 7 · `loha-video-maker_SKILL.md` — the canonical SKILL format
The single most structurally important file: it is the **proven skill shape** the V2 Builder templates
already mirror — YAML (`name` · `description` including the "Dùng khi user nói…" trigger · `metadata`)
→ Prerequisites → Modes with concrete JSON schemas → exact Run command → **RULE CỨNG (lessons from
mistakes)**. The RULE CỨNG section is the highest-value part and is mandatory on every generated V2 skill.
Key lessons to carry (as fresh prose, SEOSONA-authored): **TEXT ≠ PHIÊN ÂM** (on-screen text is the
display form — `24/7`, `41`, brand casing — while pronunciation is handled separately by a lexicon; never
write phonetic spellings into text that doubles as a caption — this is exactly V2's
`vietnormalizer-digit-scoped` + `display-title-acronyms` doctrine); HOOK fully visible at frame 0 (the
platform grabs frame 0 as thumbnail); one component per scene; karaoke in a safe zone (not flush to the
edge); cards never overlap or cover the face; diverse SFX (never one repeated sound); **VERIFY before
delivery, never fabricate** (extract a frame and check it isn't black, measure ~-16 LUFS, confirm
duration, confirm captions/mockups) = V2's fail-honest invariant. **Strip:** LoHa Tech, 9Router,
ViralCrawl, Hermes, F5-TTS branding; rename `terminal`/`chat` mockups generically. **Do not import:**
`build_scene_slides.py`, `run_video.ps1`, `edit_footage.py`, `.venv-f5`, F5-TTS. V2 equivalents:
`native_composer` (render), OmniVoice (voice), PhoWhisper-large-ct2 (ASR). EXTRACT (format + hard-rules).

### 8 · `LOHA-VIDEO-NEON_Huong-Dan.md` — talking-head studio guide
A student guide for turning self-shot talking-head footage into a studio-grade short. The standout craft
V2 does **not** yet fully have: **Studio Mode auto-shrink** — when a card appears, the speaker frame
*shrinks itself* (keeping aspect ratio, never cropping the face) into a neon-gradient background to open
room for the card, and cards are placed **opposite the face**; a full-screen mockup cutaway means **no
card at the same instant**. This is a *dynamic* exclusion strategy strictly better than V2's current
*static* safe-zone for talking-head overlays. Also reinforced: the mandatory spelling-fix pass (wrong
caption = worst error), context-priming the ASR with a domain-term prompt, and pre-baking typing
span-by-span so it survives render-seek (V2's known `tl.call()`-is-unsafe lesson). **Strip:** LoHa Tech,
ViralCrawl, the UltraViewer example, Whisper-large-v3 (V2 uses PhoWhisper), F5. **Do not import:**
`build_studio_neon.py`, `transcribe_v2.py`, `capture_shot.ps1`, the `.venv`/`.venv-f5` split,
`loha-video-pipeline`. Maps to `talking_head_edit.py` + QA role (#5/#11). EXTRACT (auto-shrink).

### 9 · `Video_Automator_Skills_Tong_Hop_Report.docx` — prior VN synthesis
A prior report (not authored by SEOSONA) synthesising bachdyon VAS + the Seedance pack + a talking-head
node spec. Useful as an independent confirmation of the pipeline and skill inventory (see
`BACHDYON_REFERENCE_ANALYSIS.md`). Two things worth lifting as *architecture ideas* (adapted to our
keyless/local doctrine): (a) the **Asset Index** — a content-hash-idempotent, VLM-semantic, embedding-
searchable index of a footage library that all downstream stages (plan/map/coverage) query without
re-analysing — the report calls this the repo's biggest differentiator; (b) the **talking-head node
hard-lock** — the original footage is an immutable base layer (no crop/recolor/retouch/audio change),
overlays render on top only, captions ≤2 words mapped to `word_id`+timecode, never paraphrased.
**Strip/avoid:** the report's dependence on Gemini/OpenAI keys, CapCut's unofficial flow, HeyGen avatar,
Remotion. REFERENCE (independent synthesis; the Asset-Index idea → GAP for #7/#4).

### 10 · `talking-head.txt` — cinematic-reel editing brief
The brief behind V2's already-built `bigword` + `caption_chunk:2`. Craft still worth reinforcing:
**extract the palette directly from the footage** (logo/shirt/background tones) and build text/graphics
gradients + glow to *integrate*, not clash; keyword plates sit **behind** the speaker, partially masked
by the subject for a premium depth/3D effect (only when a reliable subject mask exists — else fall back
to safe placement); one motion-graphic per emphasised beat; SFX synced to emphasis with ducking so the
original voice is never buried; absolute preservation of subject/audio/wardrobe/background. Maps to the
talking-head engine + Subtitle-stylist (#5). EXTRACT (palette-from-footage + masked-depth-with-fallback).

### 11 · `template video 2.txt` — audio-driven b-roll montage brief
A user brief describing an **archetype** V2 can add: borrow one audio track (a TikTok voice), then
illustrate each spoken line with the emotionally-richest, meaning-matched cut of raw footage, presented
on a **black background inside a rounded-corner illustration frame** (≈10% side margins, ≈30% top/bottom).
Maps to a new archetype under role #8 (audio-driven-broll-montage) plus Asset-sourcer (#7) and Cut/EDL
(#9) for meaning-matched clip selection. REFERENCE (archetype seed; the TikTok URLs are the user's, not
a dependency).

### 12 · `plan skill.txt` — planning meta-prompt
Four lines encoding a planning discipline: audit the whole project first; produce a long staged plan
broken into phases with work items for other models to execute; **"Data First, Plan Second"** — plan from
the project's real data/structure/history, not assumptions; then spin up fresh-context subagents to
verify the execution matched the plan. This *is* the method this very Phase-0 session uses; fold it into
the Director/OS planning discipline (#1). EXTRACT (method, no branding).

---

## Build backlog seeded by this analysis (adapt-to-our-engines, never vendor)

1. **Enrich Engine #6 grammar** (`seedance_director.py` + `lint_prompt`) with the `prompt-writter` net-new
   refinements: FOV-in-degrees anchor table, distributed-style option, positive-only + km/h/%/meters
   quantification, hidden-camera/observation optical stack, extreme-FOV 4-mechanism consistency, anti-
   impact locks, camera-block-in-3rd-position lint. (from files 4/5/6) — SEOSONA light brand kept.
2. **Talking-head dynamic auto-shrink + subject-aware overlay** (`talking_head_edit.py`, QA #5/#11):
   shrink the speaker frame to open card space, place cards opposite the detected face, suppress cards
   during full-screen cutaways — upgrade from static safe-zone. (from files 8/9/10)
3. **Local semantic asset index + transcript→asset mapper + coverage-gap planner** (#7 extend + #4/#9):
   content-hash-idempotent index of an owned footage library, keyless/local VLM+embedding (our doctrine),
   feeding meaning-matched clip selection and cutaway/hold/Ken-Burns/slowdown coverage decisions. (from
   files 9/11)
4. **Short-form non-linear splice skeleton** (Script #3 / Repurpose #13): hook→pain→tip→case→CTA line-
   splicing with raw-dialogue preservation + spelling-fix only in on-screen text. (from file 3)
5. **Palette-from-footage caption styling** (Subtitle-stylist #5): derive caption/graphic gradient + glow
   from the footage palette so overlays blend. (from file 10)

All of the above are **extract-craft-adapt**: no third-party code, no third-party brand, no foreign
venv/CLI, SEOSONA light-brand and keyless/local doctrine preserved.
