# bachdyon/video-automator-skills — Reference Analysis (Part A)

**Sources analysed (2026-07-15):**
1. `https://github.com/bachdyon/video-automator-skills` — fetched OK (README + skill catalogue).
2. `https://vas.bachdyon.com/skills` — **HTTP 403 Forbidden** (bot-blocked; also `vas.bachdyon.com/`
   root = 403). The JS-rendered catalogue could not be retrieved directly. **This is stated honestly, not
   fabricated.** The same skill inventory is recoverable from the GitHub README and from the prior VN
   synthesis report (`Video_Automator_Skills_Tong_Hop_Report.docx`), which both enumerate the catalogue;
   the inventory below is built from those two retrievable sources, and any item is flagged where the two
   disagree.

**Everything here is REFERENCE.** bachdyon's license forbids commercial vendoring; V2's own branding rule
forbids stamping their name on our product. We learn craft and skill-packaging discipline; we do **not**
copy code or prose, and we do **not** import their toolchain (it would drift V2 off its keyless/local,
HyperFrames-render, OmniVoice-voice doctrine).

---

## (a) Verified license

**PolyForm Noncommercial License 1.0.0.** Confirmed from the repo. It permits personal, educational and
research ("noncommercial") use only; any commercial use requires the author's permission. This **matches
and re-verifies** the prior SEOSONA verdict (NONCOMMERCIAL → REFERENCE). Practical consequence: we may
study it and learn from it, but we may not lift its code or ship its skills, and — per our own rule — we
would not want their branding on V2 regardless of license.

> License name as found: "PolyForm Noncommercial 1.0.0" (noncommercial-only grant).

---

## (b) What the repo actually is

Not a prompt library — an **agent-run video production OS**. It packages "skills" (modular capabilities)
plus structured artifacts and a Remotion/React renderer, and drives a brief/sample/asset set to a final
MP4. Its distinctive strength is an **asset-driven pipeline**: footage is analysed once into a semantic
index and reused across planning, mapping, coverage and render. Skills are packaged for multiple agent
frameworks (`.claude/skills/`, `.agents/skills/`, `.cursor/rules/`, `.junie/skills/`), with `skills/`,
`tools/`, `models/`, `raw_assets/`, `fonts/`, `setup/`, plus `showcases/` and `docs/` submodules. It
requires the official `remotion-best-practices` skill and integrates several **paid/cloud** APIs (Gemini,
OpenAI, fal.ai, KIE, HeyGen, AusyncLab, SocialKit, Klipy) — a key doctrine divergence from V2.

**Pipeline (their orchestration pattern):**
`$video-production-orchestrator` is the director/glue; `$video-job-manager` owns state and stale-tracking.
Linear, artifact-passing (files/TOML/JSON, not free-form chat), so every stage is debuggable and re-
renderable:
job workspace → reference-style VDS → creative plan → **voiceover-approval gate** → voice + word-level
transcript → asset generate/index → semantic mapping → shot-coverage → render-plan TOML → render + QA.
The **Asset Index** is the architectural centrepiece: content-hash (SHA-256) idempotency (unchanged files
aren't re-analysed), Gemini-vision semantics for images/video, Whisper+Gemini for audio, OpenAI-embedding
search over SQLite+sqlite-vec, queried by planner/mapper/coverage without re-analysis.

This **confirms the V2 roster's** own key insight ("Director is glue, not a monolith"; typed artifacts;
transcript-as-interface; most roles wire existing engines) — validation from a mature independent system.

---

## (c) They-have / we-have / GAP

Counting the **functional** skills (excluding the ~14 pre-made video **templates**, which all map to our
single archetype role #8): **≈33 functional skills**. Mapped against the 16-role V2 roster:

| bachdyon skill | Capability | V2 coverage | Verdict |
|----------------|-----------|-------------|---------|
| `$video-production-orchestrator` | End-to-end director/glue | #1 Director agent | **HAVE** (build native glue) |
| `$video-job-manager` | Job state, metadata, **stale-tracking** | OS orchestrator + partial re-render (KeepVoice) | **HAVE** (formalize stale-invalidation contract) |
| `$video-design-spec-builder` | Sample video → reusable design spec | #2 Reference-analyzer ⚓ | **HAVE** (EXTRACT planned) |
| `$video-creative-planner` | Brief → script/scene-intents/overlay/asset-reqs | #3 Script + #4 Scene-planner | **HAVE** |
| `$knowledge-share-video-content` | Explainer scriptwriting | #3 Script agent | **HAVE** |
| `$video-render-plan-builder` | Plan+transcript+assets → render TOML | #14 Render-factory contract | **HAVE** |
| `$video-renderer` | Final MP4 from plan (Remotion) | #14 `native_composer`/HyperFrames | **HAVE** (different engine) |
| `$video-quality-auditor` | Audit overlays/safe-area/readability | #11 QA/checker ⚓ | **HAVE** (BUILD planned) |
| `$video-visual-aesthetics` | Lock visual direction/composition/motion | #4/#8 (director.py + libs) | **HAVE** |
| `$typography-style-selector` | Font pairing/scale/weight | #5/#8 | **HAVE** |
| `$job-to-template` | Completed job → reusable template | #8 Template + library growth | **HAVE** |
| `$add-job-to-showcases` | Archive finished output | OS storage/run-dir | **HAVE** |
| `$asset-semantic-extractor` | Raw media → semantic index | image_sourcer fetches; no owned-library **index** | **GAP** |
| `$semantic-asset-mapper` | Transcript/scene → best indexed asset | partial (image_sourcer per-scene) | **GAP** |
| `$shot-coverage-planner` | Fill coverage gaps (cutaway/hold/Ken-Burns/slowdown) | director.py motion + autocut (partial) | **GAP** (coverage-decision logic) |
| `$overlay-subject-placement` | Vision overlay placement, avoid subject | static safe-zone only | **GAP** (dynamic, subject-aware) |
| `$overlay-video-preparer` | Prep overlay/effect video (alpha/screen) | effect_library + composer | **HAVE** |
| `$fal-image-generator` | AI image (fal.ai, **paid**) | real-photo `image_sourcer` (keyless) | SKIP (doctrine: paid gen) |
| `$create-edit-image-gpt-image-2` | Image gen/edit (KIE, **paid**) | — | SKIP (paid gen) |
| `$create-video-seedance-2-0` | Seedance video (KIE, **paid**) | Engine #6 (prompt-only unless keyed) | **HAVE** (prompt path) |
| `$klipy-meme-search` | GIF/sticker/meme fetch (**paid key**) | — | GAP-minor / SKIP (keyed) |
| `$animated-svg` | SVG → HTML animation | HyperFrames + svg_draw_on | **HAVE** |
| `$png-to-svg-convertio` | PNG→SVG (Convertio, cloud) | — | SKIP (cloud utility) |
| `$ausynclab-voice` | Cloud narration | #6 OmniVoice (local GPU) | **HAVE** (better; local) |
| `$free-tts` (VieNeu-TTS) | Local TTS fallback | #6 OmniVoice (VieNeu is our license-clean backup) | **HAVE** |
| `$capcut-tts` | CapCut TTS/STT (**unofficial**) | OmniVoice + PhoWhisper | **HAVE** (avoid unofficial) |
| `$word-timestamps-extractor` | Word-level transcript | PhoWhisper-large-ct2 | **HAVE** |
| `$audio-deduplicate` | Remove restart/dup speech | talking_head_autocut (dup-take cut) | **HAVE** |
| `$video-audio-extractor` | Extract audio track | ffmpeg (native) | **HAVE** |
| `$subtitle-screen-splitter` | Split captions to fit screen | caption chunking | **HAVE** |
| `$subtitle-punch-tag-shortform` | Word-synced punch captions | karaoke word-pop + accent | **HAVE** |
| `$video-compress-under-25mb` | Compress under platform limit | — | **GAP-minor** (utility) |
| `$video-downloader` (TikTok/TikWM) | Download source clips | source_footage (yt-dlp) | **HAVE** |
| `$youtube-fast-download` (yt-dlp) | Download YouTube/Shorts | source_footage | **HAVE** |
| `$socialkit-api` | Transcript/stats/summary/downloads (**paid**) | #16 Reporter (planned) | GAP → #16 (keyless variant) |
| `$filepost-file-upload` | CDN upload | #15 Publisher infra | GAP → #15 |
| `$heygen-asset-upload` | Upload for HeyGen | (avatar line removed) | SKIP |
| `$heygen-photo-avatar-video` | Photo → talking-head avatar (**paid**) | **deliberately removed** (lipsync/avatar line) | SKIP (doctrine: line deleted 2026-07-14) |
| `$telegram-send` | Send to Telegram | #15 Publisher (multi-platform) | GAP → #15 |
| `$remotion-best-practices` | Remotion rules (required) | HyperFrames engine | SKIP (different engine) |
| **~14 `*-template` skills** | Pre-made archetypes (3d-explainer, stickman, personal-brand, podcast ×4, theanh28, outfit ×2, english-split, threads ×2, mindset-pitch) | #8 archetype library (43-frame) | **HAVE** (add missing archetypes as needed) |

**Tally (functional skills):** ~33 total → **~22 already covered (HAVE)**, **~7 SKIP** (paid gen /
unofficial / avatar line we removed / Remotion / cloud utilities — doctrine mismatch, not gaps), and
**~4–6 genuine GAPs** worth building (adapted to our keyless/local doctrine).

### The GAPs worth building (doctrine-compatible, adapt-not-vendor)
1. **Semantic asset index** (`asset-semantic-extractor` + `semantic-asset-mapper`) — a content-hash-
   idempotent, locally-computed VLM+embedding index of an **owned footage library**, so a transcript /
   scene-intent resolves to the best reusable clip. V2 has `image_sourcer` (fetch a *new* photo per
   scene) but **no reusable index of owned footage**. The DOCX report calls this the repo's biggest
   differentiator. → extends roster #7 (+#4).
2. **Shot-coverage planner** (`shot-coverage-planner`) — when footage is missing or duplicated, decide
   the fix: cutaway, hold, Ken-Burns, slowdown. V2 has motion (director.py) and dead-air cutting
   (autocut) but not the coverage-*decision* layer. → #4/#9.
3. **Subject-aware / dynamic overlay placement** (`overlay-subject-placement`, sharpened by LoHa Studio
   Mode) — place overlays to avoid the face/mic dynamically, and shrink the speaker frame to open card
   space, instead of a fixed safe-zone. → #5/#11.
4. **Compress-under-platform-limit** utility — a small but real gap. → #14/#15.
5. **Multi-platform publish + analytics** (`filepost`/`telegram`/`socialkit`) — already the roster's
   NEW roles #15 (Publisher, human-gated public post) and #16 (Reporter) — build **keyless** where their
   versions are paid.

### Explicitly SKIP (already have, or doctrine mismatch — **not** gaps)
Voice (OmniVoice > their cloud/unofficial TTS), ASR word-timestamps (PhoWhisper), punch/karaoke captions,
subtitle splitting, templates/archetypes (43-frame library), render (HyperFrames vs their Remotion),
thumbnail, script-writing, dedup/autocut, downloader, and Engine #6 Seedance prompting. And hard-skip:
**paid generation** (fal/KIE GPT-image/Seedance-fast), **HeyGen avatar** (the lipsync/avatar line was
deliberately deleted on 2026-07-14 — do NOT rebuild), **CapCut unofficial flow**, and **Remotion** (we
use HyperFrames).

---

## (d) Orchestration pattern — what to learn

- **Artifact-passing over chat.** Every stage reads/writes a typed file (TOML/JSON), so stages are
  debuggable, re-renderable, and **stale-markable** when an input changes. V2 already has partial
  re-render; formalising the typed `ProductionPlan`/`ProductionCommand` contract + stale-invalidation is
  the lesson.
- **A mandatory human gate mid-pipeline** (their voiceover-approval before any expensive gen/render) —
  matches V2's human-gate discipline; a good place for our approval step.
- **Content-hash idempotency** on every asset so nothing is re-analysed needlessly — worth adopting in
  the semantic-index GAP.
- **Reference-analysis and QA are the same core run in two directions** (their design-spec-builder vs
  quality-auditor) — exactly the roster's "#2 ≡ #11, build once, use twice" insight, independently
  confirmed.

## (e) Recommendation — LEARN / SKIP / GAP

- **LEARN (extract craft, adapt to our engines):** the typed-artifact + stale-invalidation contract; the
  content-hash semantic asset index; the coverage-decision vocabulary (cutaway/hold/Ken-Burns/slowdown);
  subject-aware overlay placement; the mid-pipeline approval gate. Plus, from the Seedance pack shipped
  alongside, the enriched prompt grammar (see `SKILL_TEMPLATE_ANALYSIS.md` §6).
- **SKIP (already have / doctrine mismatch):** all voice/ASR/caption/template/render/thumbnail/download
  skills; and hard-skip paid gen, HeyGen avatar, CapCut, Remotion.
- **GAP (build, keyless/local):** semantic asset index (#7), coverage planner (#4/#9), subject-aware
  overlay (#5/#11), compress utility (#14/#15), and the already-planned publish (#15) + reporter (#16).

**Every recommendation is extract-craft-adapt-to-our-engines — never vendor their code, never their
brand, never their toolchain.** Provenance is recorded in `2_KNOWLEDGE/INGESTION_LOG.md`, not on any
shipped skill.
