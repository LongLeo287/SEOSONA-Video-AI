# Repo Batch-2 Triage — RAP Step 1 (dedup-first, metadata-only)

**Date:** 2026-07-16 · **Input:** 12-item batch (agent task). **Method:** Light-touch classification
only — NO cloning, NO CLI scans. Each item's README/about/license WebFetched cheaply (raw README/LICENSE/
package.json where the GitHub SPA shell hid the content). Prior SEOSONA verdicts (`REPO_BATCH_TRIAGE.md`,
`DEEP_RAP_REPORTS.md`, `INGESTION_LOG.md`) and roster coverage (`VIDEO_SKILL_AGENT_ROSTER.md`) cited
instead of re-derived. Where a license could not be cheaply confirmed it is marked
"unverified — confirm in deep-RAP" (no guessed licenses).

**Grounding — what V2 already has** (from the read docs): own native renderer with per-frame GSAP/WAAPI
motion on the HyperFrames seek engine (V2 OWNS the animation-engine lineage `5_FRAMEWORK/hf_engine`,
Apache-2.0); LLM content director (seam exists, being wired); Pexels b-roll; **SEOSONA Flow = keyless
LOCAL-MCP for AI image/video gen**; 10 visual modes; brand-locked Be Vietnam Pro (LIGHT palette).
Engine doctrine: **OmniVoice + PhoWhisper only; keyless/local preferred; noncommercial = REFERENCE;
paid-cloud gen + whole-editor apps = SKIP; avatar/lipsync line REMOVED.**

**Buckets:** A = owned/is-our-engine · B = already-vetted or roster-covered · C = skip (doctrine) ·
D = deep-RAP shortlist (survives to Step 2).

## Counts
| Bucket | Count |
|--------|-------|
| **A · OWNED / IS-OUR-ENGINE** | 0 |
| **B · ALREADY-VETTED / ROSTER-COVERED** | 3 |
| **C · SKIP (doctrine)** | 8 |
| **D · DEEP-RAP SHORTLIST** | 1 |
| **Total** | 12 |

---

## Per-item verdicts

| # | Item | License | Bucket | One-line rationale |
|---|------|---------|--------|--------------------|
| 1 | ruvnet/ruflo | MIT (LICENSE) | **C · SKIP** | Multi-agent "meta-harness" / swarm framework — off video-domain **and** an alternate agent runtime we don't adopt (we run on Claude Code; cf `oh-my-codex`, `AutoAgent`). |
| 2 | LukasNiessen/kubernetes-skill | MIT | **C · SKIP** | Kubernetes/DevOps hardening skill — entirely off-domain, no media component. |
| 3 | alchaincyf/nuwa-skill | MIT | **C · SKIP** | Distills public-figure mental models into text skills — cognitive, not video/media (hero animation is decorative only). |
| 4 | topviewai/skill | LICENSE.txt (type unstated — unverified) | **C · SKIP** | Wrapper for the **PAID** TopView.ai cloud (video + talking-avatar + voice-clone, credit-billed, needs API key). Breaks keyless-local doctrine; avatar/lipsync line already REMOVED. cf `Generative-Media-Skills`, `VideoClaw`, `reels-af`. |
| 5 | agentskills/agentskills | Apache-2.0 (code) / CC-BY-4.0 (docs) | **B · ROSTER-COVERED** | The open **SKILL.md spec/format** (Anthropic-origin) — canonical skill format already learned; cf prior B rows `anthropics/skills`, `openai/skills`. No video skills here (spec only). |
| 6 | HUANGCHIHHUNGLeo/claude-real-video | MIT | **D · DEEP-RAP** | Keyless LOCAL video **analysis**: scene-change keyframe extraction + dedup + transcript (yt-dlp + free whisper). The exact frame-sampling core of roster **#2 Reference-analyzer**; improves on fixed-interval sampling. See shortlist. |
| 7 | bradautomates/claude-video | MIT | **B · ALREADY-VETTED** | Prior verdict: INGESTION_LOG 2026-07-11 REFERENCE (video comprehension = perception, opposite of production). Already in Batch-1 triage B. |
| 8 | Anil-matcha/Open-Generative-AI | MIT | **C · SKIP** | Self-hosted image/video **studio app** that routes to 200+ mostly-PAID cloud models (Flux/Midjourney/Kling/Sora/Veo). Whole-app + paid-cloud gen vs keyless-local SEOSONA Flow; cf `videosos`, `OpenCut` (whole-editor Rejected). |
| 9 | mintdotgg/mint-threejs-skills | none stated (unverified — confirm in deep-RAP) | **C · SKIP** | Three.js (3D/WebGL) agent guidance tied to the paid Mint MCP for 3D asset gen. 3D/WebGL is off our 2D HTML/GSAP brand substrate; tied to a paid MCP; no license file. |
| 10 | romboHQ/tailwindcss-motion | MIT (package.json) | **B · ROSTER-COVERED** | Tailwind CSS-keyframe animation-preset plugin. Motion craft already owned (GSAP `springLand` + `effect_library` entrance-variety); roster #8 / motion craft; Tailwind runtime N/A. cf B rows `juliangarnier/anime`, `imskyleen/animate-ui`. **Revisit note below** — cleanest by-hand keyframe-recipe source *if* the WAAPI @keyframes seek path is built. |
| 11 | mcp.mint.gg (MCP endpoint) | proprietary paid service (credits/OAuth) | **C · SKIP** | Remote **paid** MCP generating 3D models/Worlds/PBR-materials/asset-packs/images/audio — **no video, no animation**. Doctrine-mismatch vs keyless-local SEOSONA Flow; overlap (images/audio) already covered keyless (Pexels + BGM/SFX sourcers). See mint.gg analysis below. |
| 12 | docs.mint.gg (docs) | same service as #11 | **C · SKIP** | Docs for the same Mint service — same verdict as #11. Reachable and read (not JS-blocked). |

---

## D · DEEP-RAP SHORTLIST (1), RANKED

RAP dedup discipline keeps this small and honest: 11 of 12 are off-domain, prior-verdict, paid-cloud, or
already-covered. The one genuinely-new, roster-relevant, license-usable survivor:

### 1. HUANGCHIHHUNGLeo/claude-real-video → roster **#2 Reference-analyzer** (⚓ anchor) + **#11 QA-checker**
- **Why new/valuable:** roster #2 Reference-analyzer's frame-sampling core is currently only README-grounded
  (named sources `ai-video-editor`, `video-frames-skill`, never cloned). This repo is a **clean, MIT,
  keyless-local** implementation of exactly that core: **scene-change** keyframe extraction (not naive fixed
  1 fps), near-duplicate removal via sliding-window compare, a "settled-local" detector that catches text-
  overlay / UI-change frames global pixel diff misses, plus transcript + timestamps + contact-sheet. This is
  the cheapest-possible "read a reference video → sparse meaningful frames + word-level transcript" front-end
  that #2 (extract EditFormula) and #11 (run #2 on our own output) both need.
- **Extract (never vendor):** the **scene-change + dedup + settled-local frame-selection heuristic** →
  feed our native Reference-analyzer's VLM step with *meaningful* frames only (cheaper, better formula
  extraction). Reuse the same sparse-frame+transcript reader for the QA-checker's self-scoring pass.
- **Doctrine fit:** keyless + local (yt-dlp + **free** whisper/faster-whisper — swap to our PhoWhisper-ct2);
  no cloud upload of source. The **"crv Pro" $19–$29 paid tier** (camera-motion / emotion analysis) is a
  separate add-on we ignore — the core we want is free MIT.
- **License read:** **MIT** (WebFetched) — adoptable clean-room; confirm LICENSE file in deep-RAP.
- **Dedup vs prior:** distinct from `bradautomates/claude-video` (B, perception-only, no scene-change/dedup
  technique) and from Batch-1's roster-#2 note — this contributes the *actual frame-selection algorithm* #2
  was missing. **Confirm in deep-RAP: source-verify the scene-change/settled-local logic + MIT LICENSE.**

---

## mint.gg MCP (items 11 + 12) — asset-gen alternative assessment (task-requested)

**What it is:** Mint is a hosted AI agent + **remote MCP server** (`https://mcp.mint.gg/mcp`, OAuth) that
generates/retrieves creative assets: **Images, 3D Models, 3D "Worlds", PBR Materials, Asset Packs, Audio
(SFX/UI/ambience/music), and mobile room/object Captures.** Text/image/StreetView/listing prompts →
preview → final. `mint-threejs-skills` (#9) is its Three.js companion skill.

**Is it a viable asset-gen alternative/supplement to SEOSONA Flow? — NO (skip).**
- **No video, no animation.** Its docs explicitly cover images/3D/audio, **not** video or motion — so it
  cannot supply the b-roll/clip layer our video pipeline needs. That alone rules it out as a Flow replacement.
- **Paid + remote + OAuth.** It runs on Credits / optional plans / top-ups behind OAuth on a third-party
  server — the opposite of SEOSONA Flow's **keyless, local** MCP doctrine. Adopting it re-introduces a paid
  cloud dependency V2 deliberately avoids.
- **The overlap we could theoretically use is already covered keyless:** still images → Pexels sourcer;
  music → BGM sourcer (Openverse/Jamendo CC); SFX → `7_ASSETS/audio/sfx`. Mint adds nothing keyless here.
- **Its unique outputs (3D Models / Worlds / PBR Materials) are off-substrate** — V2's renderer is 2D HTML/
  GSAP brand-locked; 3D/WebGL is not our look and not in the 10 visual modes.
- **Honest supplement caveat:** *if* V2 ever adds a 3D/interactive-world format (not on the roadmap), Mint
  is a capable hosted 3D+audio source — but as a paid remote service it stays a REFERENCE, not an adoption,
  and never replaces the keyless-local Flow.

---

## Honest notes (fail-honest record)

- **Metadata-only, no clones.** Verdicts rest on WebFetched README/LICENSE/package.json + cited prior
  verdicts. No CLI scans, no fabricated licenses.
- **GitHub SPA shells:** items 1,3,4,5,9,10 first returned only the nav shell; re-fetched via
  `raw.githubusercontent.com` README/LICENSE/package.json to classify honestly.
- **Unverified licenses (flagged, do not gate the bucket):** #4 topviewai (LICENSE.txt type unread — but
  paid-cloud gates it C regardless), #9 mint-threejs (no license file found — C on substrate/paid-MCP
  grounds regardless). The only place license matters for adoption is the D survivor **#6 claude-real-video
  (MIT)** — reconfirm the LICENSE in deep-RAP before any clean-room extraction.
- **All 12 links reachable** (mint.gg MCP endpoint + docs both read successfully — not JS-blocked).
- **Special-attention items resolved:** claude-real-video = **D** (video *analysis* technique for #2, not a
  gen threat to our why-better findings); claude-video = **B** (prior REFERENCE); tailwindcss-motion +
  mint-threejs = motion/3D already covered or off-substrate (**B / C**); mint.gg MCP = **C** (paid, remote,
  no-video — not a cleaner asset source than keyless-local Flow).

**File written:** `D:\SEOSONA AI\SEOSONA Video\docs\v2_phase0\REPO_BATCH2_TRIAGE.md`
