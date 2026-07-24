# WHY BETTER — huytranvan2010/AI-auto-generate-video (deep quality-lens analysis)

**Analyst note:** repo CLONED (public) and read in full — every `src/*.ts`, the pipeline,
the SFX/audio tooling, the render/compose code, the `SKILL.md` authoring spec, `CATALOG.md`,
one full template (`frame-pentagram-stat`) and its NOTICE. This is **read, not inferred**,
except the finished-video *look* (I did not run a render — no OmniVoice server / GPU). Where I
infer from code rather than watching output, it's flagged.

- **Repo:** https://github.com/huytranvan2010/AI-auto-generate-video (`aicoding-template-video` v2.0.0)
- **Size:** ~1,730 LOC TypeScript (small, tight) + 11 vendored HTML templates
- **License:** **MIT** (Copyright 2026 AI Coding / Ho Quang Hai). Vendored templates are **Apache-2.0**
  (from nexu-io/html-video; 8 carry `NOTICE.md`, attribution required, commercial use allowed).
  → **VERDICT: ADOPT (clean-room-friendly).** MIT code is directly portable with attribution;
  Apache-2.0 templates are commercially usable if we keep the NOTICE. No copyleft, no NC clause.
- **Lineage:** direct descendant of `hoquanghai/Auto-Create-Video` (our memory already tags that
  as the "MIT HyperFrames VN twin"). Same engine (HyperFrames), same TTS (OmniVoice), same niche
  (Vietnamese 9:16 news shorts). **This is effectively a sibling of our own system**, and it made
  *different architectural bets* — that's what makes the comparison useful.

---

## The one-paragraph honest answer

It is **not a talking-head system and it renders no captions of its own** — so it is not a like-for-like
"better V2." It is a **faceless animated-poster generator**: every scene is a full-screen, art-directed,
**actually-animated** HTML template rendered to MP4 by Chromium, timed exactly to its narration, with a
**semantic SFX layer** mixed under the voice. It "feels better" than our V2 baseline for *that faceless
news-short format* because of four production choices V2's stated baseline lacks — **real per-frame motion,
art-directed full-screen templates, sound design, and sample-accurate audio/visual timing** — plus a
disciplined content-authoring skill. It is *narrower* than V2 (no footage, no speaker, no burned captions,
no b-roll — the `image-fetcher` is **dead code**), but *deeper* on motion + polish within its lane.

---

## 1. Their full pipeline (idea → output), tool by tool

`/create-template-video <url|.txt>` (Claude Code skill) → then 8 deterministic steps in
`src/render/template-pipeline.ts`:

| Stage | What they use | Detail |
|---|---|---|
| **Idea/fetch** | Claude Code skill + `WebFetch` | Skill fetches article → extracts title/content/ogImage/domain as JSON |
| **Script** | Claude (the agent) writes `script.json` | AI authors content + **chooses a template per scene**; Zod-validated (3–12 scenes, `scenes[0]=hook`, last=`outro`) |
| **Caption text** | plain join | `script.txt` = all `voiceText` joined — **handed to CapCut auto-caption; they do NOT burn subtitles** |
| **TTS** | **OmniVoice (local, keyless)** — *same engine as us* | per-scene mp3, `p-limit` concurrency, idempotent (reuse existing mp3), 4-try backoff |
| **Voice concat** | ffmpeg **concat filter** | 0.3s silence gaps + **8ms micro-fades** to kill boundary clicks; computes per-scene start times |
| **SFX** | **native semantic selector + ffmpeg amix** | 3-tier pick (override → VN/EN keyword → scene-type), deterministic hash, per-category volume/offset |
| **Visuals** | **HyperFrames 0.6.94 (HTML→MP4 via Chromium)** | each template = self-contained animated HTML; rendered at 30fps; idempotent per clip |
| **Timing fit** | ffmpeg `tpad` freeze / trim | **each clip stretched/trimmed to exactly its narration length** (+0.3s gap; outro holds 3s) |
| **Assembly** | ffmpeg concat demuxer + mux | uniform x264 crf18 clips → concat (stream copy) → mux voice (aac 192k), video length wins |
| **Image/b-roll** | **NONE** | `image-fetcher.ts` exists but is **never imported** — no stock, no b-roll, no imagery in the render |

**No image-gen, no video-gen, no stock API, no music/BGM, no editor.** The "asset" richness is entirely
in the **animated templates + SFX**. That's a much smaller surface than the task hypothesized.

---

## 2. WHY the finished videos look/feel better — ranked

1. **Real per-frame motion (biggest).** Every template is animated CSS — keyframes with `cubic-bezier`
   easing: rule-lines scale in, giant numbers glow/rise, char-by-char word reveals, RGB-split glitch,
   floating aurora blobs, logo assemble + shimmer sweep. HyperFrames drives Chromium and captures the
   animation to MP4 at 30fps. The result is *motion design*, not a slideshow. (Verified in
   `frame-pentagram-stat/compositions/portrait.html` — real `@keyframes` + easing.)
2. **Art-directed full-screen template cards, chosen for variety.** 11 distinct professional looks
   (dark-neon Swiss grid, charcoal Vignelli, cyberpunk glitch, editorial poster, list, head-to-head
   comparison, aurora hero, brand outro). The **design is owned by the template**, not by a code
   fallback, and the skill instructs the AI to *rotate* templates so consecutive beats don't repeat.
3. **Sound design (SFX under the voice).** `sfx-selector.ts` picks a sound per scene by matching VN/EN
   keywords ("cảnh báo"→alert, "kỷ lục"→success, "ra mắt"→reveal) with scene-type fallbacks, at
   category-tuned volumes/offsets, mixed via ffmpeg `amix`. Even light SFX makes shorts feel produced.
4. **Sample-accurate audio↔visual timing.** Clips are fit to narration length; start times computed
   from **packet-counted** mp3 durations (see below), not ffprobe's bitrate estimate. Nothing drifts;
   the outro holds a deliberate 3s. This "everything lands on the beat" precision reads as quality.
5. **Correct duration + click-free audio (invisible but decisive).** `getDurationSec` counts MP3
   packets × samples-per-frame because OmniVoice's 24kHz MPEG-2 L3 fools `format=duration` by 30%+.
   Wrong here = every clip mistimed. Plus 8ms micro-fades remove concat clicks.
6. **Content discipline (the skill).** `SKILL.md` mandates 8–12 scenes, **one idea per scene**, 6–10s
   on screen for fast pacing, and a thorough **Vietnamese-TTS number-spelling table** (write "GPT năm
   chấm năm" so TTS doesn't say "năm rưỡi"); emoji allowed in on-screen `inputs` but **banned in
   `voiceText`**. Tight, well-paced scripts *feel* more professional regardless of render.

> Note: the task hypothesized "stock matched to script" and "music+ducking." **Neither is true** —
> there is no b-roll and no music/BGM at all. The polish is animation + SFX + timing, not assets.

---

## 3. What's transferable → mapped to a concrete V2 improvement

All MIT — portable clean-room with attribution. Ranked by leverage:

| # | Their thing | Adopt as | V2 change |
|---|---|---|---|
| A | **HyperFrames HTML→animated-MP4 render** | **directly adoptable pattern** | Replace V2's "Playwright → static PNG + ffmpeg fades" with an **animated** render step: either invoke the pinned `hyperframes` CLI, or use Playwright's **video/screencast capture** of the animated page over the scene's duration. This is the single highest-impact change. |
| B | `fitClipToDuration` + per-scene start-time computation (`video-tools.ts`) | **port verbatim (MIT)** | Give V2 sample-accurate per-scene fit (tpad freeze / trim) instead of raw caption segmentation. |
| C | `getDurationSec` packet-count + `concatWithSilence` micro-fades (`audio-tools.ts`) | **port verbatim (MIT)** | Fixes OmniVoice duration error (we use the same engine → we have the same bug latent) and kills concat clicks. |
| D | `sfx-selector.ts` 3-tier + `mixSfxOntoVoice` amix | **port + reuse our existing `7_ASSETS/audio/sfx`** | Add a real sound-design layer to the native path. Our legacy `native_composer._sfx_cues` already does per-component SFX — this is a cleaner selector to converge on. |
| E | 11 Apache-2.0 animated templates + `CATALOG.md` slot schema | **vendor (keep NOTICE)** | Instant art-directed template library for a faceless-poster mode; the `CATALOG.md` slot-doc pattern is a good contract for our LLM seam. |
| F | `SKILL.md` authoring rules (one-idea scenes, VN number table, emoji separation) | **learn-only → fold into V2's LLM prompt** | Directly upgrades V2's *weak deterministic card/filler plan* once the LLM seam is wired. Our memory already flags VN number-normalization; their table is more complete for the *authoring* side. |
| G | The **"AI writes content JSON / deterministic code renders pixels"** split | **architectural principle** | Same reproducible-render discipline V2 is aiming for; their Zod `TemplateScriptSchema` is a clean reference for our script contract. |

**Directly adoptable (MIT, copy-with-attribution):** B, C, D (code), E (Apache-2.0 templates).
**Learn-only / adapt:** A (invoke their engine or replicate the capture approach), F, G.

---

## 4. The whole capability V2 structurally lacks

**Full-screen, per-frame-*animated*, art-directed scene rendering.** V2's stated baseline renders
elements as **static Playwright PNGs** composited with **ffmpeg fades** — there is no motion inside a
frame, only cross-dissolves between them. Theirs renders **animated HTML to video** so every scene has
intrinsic motion. Coupled with the **AI-content / deterministic-render split producing byte-reproducible
clips**, this is the one capability class V2 has *no equivalent of today*. (Everything else they do —
SFX, timing, VN TTS handling — V2 either has in the legacy system or can bolt on cheaply.)

---

## 5. Honest verdict — better, or just different?

**Mostly different, better only within its narrow lane.**

**Where theirs genuinely wins (faceless animated news-poster shorts):** real motion, art-directed
template variety, sound design, sample-accurate timing, and tighter content authoring. For that exact
product, yes — it will out-look V2's static-PNG-plus-fades baseline.

**Where V2 is already even or clearly ahead:**
- **Talking-head / real footage** — theirs has *no* footage path, *no* speaker, *no* face reframe.
  V2's entire footage engine (PhoWhisper ASR, face-centered reframe, rembg text-behind-speaker) has
  **no counterpart here**. Different product.
- **Burned captions** — **they burn none**; they punt to CapCut auto-caption. V2 burns ASS karaoke
  captions. Genuine V2 advantage.
- **B-roll / imagery** — they have **none** (dead `image-fetcher`). V2 has an image-sourcer + element
  library. V2 ahead.
- **Music/BGM** — they have none; V2's legacy system has a BGM sourcer with CC attribution. V2 ahead.
- **Ecosystem** — V2/legacy has knowledge graph, eval flywheel, cover-frame scorer, template/component/
  block libraries. Theirs is a lean single-purpose pipeline.

**Net:** don't rebuild around it — **harvest** it. Take the *render-motion approach* (A), the *timing +
duration correctness* (B, C), the *SFX layer* (D), and the *authoring discipline* (F). Those four close
the exact gaps in the V2 baseline while keeping V2's real advantages (footage, burned captions, b-roll,
BGM, ecosystem). It's a sibling that made one bet better than us — animation — and several bets we
already beat.

---

## Top 3–5 concrete reasons → V2 improvement (the executive list)

1. **Animated HTML→MP4 (Chromium) vs static PNG + fades** → adopt an animated render step (HyperFrames
   CLI or Playwright video capture). *Biggest gap.*
2. **Fit-clip-to-narration + computed scene start times** → port `video-tools.fitClipToDuration` and the
   timing loop; kills drift.
3. **Semantic SFX layer (3-tier + amix ducking)** → port `sfx-selector.ts` + `mixSfxOntoVoice`; wire our
   existing `7_ASSETS/audio/sfx`.
4. **Packet-counted MP3 duration + micro-fade concat** → port `audio-tools`; we run the *same* OmniVoice
   so we share the latent 30% duration bug.
5. **Art-directed template library + content-authoring skill** → vendor the 11 Apache-2.0 templates and
   fold `SKILL.md`'s one-idea-per-scene + VN number table into V2's LLM seam.

**Biggest capability gap:** per-frame *animated*, art-directed, reproducible full-scene rendering — V2 has none.

**License:** MIT code (ADOPT) + Apache-2.0 templates (ADOPT with NOTICE). No copyleft/NC.

**Doc path:** `D:\SEOSONA AI\SEOSONA Video\docs\v2_phase0\WHYBETTER_huytranvan.md`

**Read vs inferred:** all pipeline/render/audio/SFX/skill/template *code* was **read**. The finished-video
*look* is **inferred from the code** (CSS keyframes + HyperFrames capture + SFX mix) — I did not run a
render (no OmniVoice server / GPU in this session).
