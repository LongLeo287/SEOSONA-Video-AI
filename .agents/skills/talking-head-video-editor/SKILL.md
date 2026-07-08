---
name: talking-head-video-editor
description: >
  build and edit talking-head videos, self-shot videos, screen-recordings or raw footage into 9:16 vertical or 16:9 landscape videos with word-aligned transcript, karaoke captions, platform-specific caption styles, neon cards, callouts, mockup ui cutaways, background music, sfx and a verify step before delivery. use when the user says edit a video, build a talking-head, make video captions, add karaoke captions, add a card/callout, build a review video, tutorial, product intro, app demo, or edit self-shot video with edit_footage.py, hyperframes and ffmpeg.
---

# Talking-head Video Editor

## Goal

Use this skill to turn self-shot footage or screen-recording into a finished video with captions, cards, callouts, mockup UI, background music and SFX. Do not use the faceless scene-slides workflow (that is `seosona-news-maker`), do not auto-generate an AI voice, use the REAL VOICE from the footage.

## Real engine (already built in the project)

- **2 scripts:** `scripts/talking_head_transcribe.py` (= `npm run talkinghead:transcribe`) and `scripts/talking_head_edit.py` (= `npm run talkinghead:edit`). Reuses `asr_router` (PhoWhisper) + `native_composer._ffmpeg_bin/_bgm/_sfx` + the SFX library.
- **Aspect ratio:** KEEP the footage's native resolution → automatically supports **both 9:16 and 16:9** (no config needed).
- **Caption:** karaoke `\k` + card rendered with **ASS subtitle**, burned in with ffmpeg (no alpha-render needed).
- **Output:** `final.mp4` + ASS alongside it. SFX in `sfx_events.file` accepts a **mnemonic name** (`whoosh`/`pop`/`ding`/`success`/`notify`/`swipe`) → auto-mapped to the SFX library; or an absolute path.
- The `enter`/`width`/`duration` fields in `cards.json` are currently accepted but not yet used (reserved); `--composition` is accepted but ignored.

## Required inputs

- Main footage: `.mp4`, prefer 9:16 if posting to TikTok/Reels/Shorts; 16:9 if posting to YouTube or a long demo.
- Word-level transcript: create it with `npm run talkinghead:transcribe`, then fix brand spelling → `words_fixed.json`.
- Edit config file: `cards.json` (footage, caption_bottom, music, music_vol, keywords, cards, sfx_events).
- Optional (ADVANCED, not yet wired in the repo): UI screenshot/mockup HyperFrames, `capture_shot.ps1` — skip the Section B mockup part if you do not have the tooling.

## Required inputs

- Main footage: `.mp4`, prefer 9:16 if posting to TikTok/Reels/Shorts; 16:9 if posting to YouTube or a long demo.
- Word-level transcript: created from the footage with `transcribe_video.py`, then fix brand spelling into `words_fixed.json`.
- Edit config file: `cards.json`, containing footage, duration, caption zone, music, keywords, cards and sfx_events.
- Optional: real screenshots, UI mockup HyperFrames, cutaway clips, logos, app assets, or supplementary screen-recordings.

## Standard workflow

### 1. Transcribe and fix the transcript

Run:

```bash
npm run talkinghead:transcribe -- --video <mp4> --out selfshot
# (= python scripts/talking_head_transcribe.py --video <mp4> --out selfshot)
```

The main result is `words.json`. Before building, always create `words_fixed.json` by fixing common recognition errors:

- brand/app: `Cloud` -> `Claude`, `herme` -> `Hermes`, `Chat GBT` -> `ChatGPT`.
- terminology: keep the correct display form in the caption, e.g. `AI`, `24/7`, `9Router`, `email`, `API`.
- figures: keep them short and easy to read on screen, e.g. `40`, `24/7`, `3 bước`.

### 2. Choose a caption style before writing cards

Pick 1 main style for the whole video, then use cards/callouts to emphasize points. Don't mix too many styles in one short video.

| Style | Use when | Caption rule |
|---|---|---|
| `karaoke_neon` | sales videos, app reviews, tool intros, content that needs retention | bottom caption, active word in yellow, keywords in accent color, chunks of 5-7 words |
| `clean_tutorial` | how-to videos, screen demos, content that needs clarity | concise 1-2 line caption, few effects, prioritize not covering the UI |
| `tiktok_bold` | strong hook, viral clips, fast short-form | large text, short 3-5 word phrases, emphasize verbs/figures, cards appear early |
| `authority_news` | news, analysis, market updates | solid caption, little bounce, use a lower-third/headline card instead of many stickers |
| `review_compare` | tool comparison, pricing, features, before-after | moderate caption, bullet/compare/stat cards at the right moment of speech |
| `screen_demo` | app/web videos with a lot of UI | place the caption low or off the safe zone, full-screen mockup/cutaway, don't let cards cover important UI |

Safe default settings:

- `caption_bottom`: `380` to `390` for 9:16.
- `--caption-chunk`: `6` for typical talking-head; `4-5` for fast TikTok; `7-8` for slow tutorials.
- Keywords in the caption must match words in the transcript so the accent highlighting is stable.

### 3. Write `cards.json`

Minimal template:

```json
{
  "footage": "assets/footage.mp4",
  "duration": 108,
  "caption_bottom": 380,
  "music": "tech",
  "music_vol": 0.10,
  "keywords": ["claude", "hermes", "ai"],
  "cards": [
    {
      "type": "term",
      "title": "Claude là gì?",
      "sub": "AI viết code và xử lý tài liệu",
      "accent": "cyan",
      "enter": "right",
      "left": 600,
      "top": 150,
      "width": 460,
      "t": 2.0,
      "dur": 7.5
    }
  ],
  "sfx_events": [
    {"file": "whoosh.wav", "t": 2.0, "db": -14}
  ]
}
```

Standard card types:

- `term`: explain a term, tool, concept or brand name.
- `bullet`: list 2-4 points; use `rows` and `cue` to sync with keywords.
- `stat`: emphasize a figure, KPI, price, time, percentage, before/after.
- `steps`: numbered how-to rows (revealed in sequence).
- `checklist`: a process/list whose rows carry a **completion STATE** and an optional **progress bar** — the primary "graphic" device in the reference reels (org panels, CEO-agent loop). Two INDEPENDENT axes: the card's **border = semantic role**, the **✓ / green fill = state**. Schema:
  ```json
  {"type":"checklist","role":"info","title":"CEO AGENT","t":2,"dur":11,"left":80,"top":300,"progress":true,
   "rows":[{"text":"Phân tích mục tiêu","done_at":1.2},{"text":"Tạo ticket","done_at":3.2}]}
  ```
  - **Animated** (a `done_at` in seconds-from-`t` on each row): the row shows as *doing* (amber numbered badge) then flips to *done* (green ✓) at `done_at`; rows reveal as the previous one completes (a real state machine). With `progress:true` a bar fills in lockstep (fraction = done/total). Use for "how the loop runs" beats.
  - **Static** (no `done_at`): give each row `"state":"done"|"doing"|"todo"` for a fixed snapshot; `progress` fills to done/total.
  - Rows also support `"state":"affirm"` (green ✓ "do this") and `"state":"negate"` (coral ✕ "not this") — the negation/checklist motif; `kw` overrides a row's badge label (else the row number). Optional `bar_width`.
- `badge`: a persistent corner STEP marker (ref "BƯỚC N") — `{label, sub?, role, done?, t, dur, left, top}`; set `done:true` to prefix a green ✓. Keep it dwelling for the whole step.
- `section`: an eyebrow chapter pill (ref "● ① TƯ VẤN LUẬT") — `{label, num?, splash?, role, t, dur, left, top}`; `num` prepends a circled digit ①..⑨, `splash:true` shows a big centred number for ~1 s on entry then docks into the pill.
- `reason`: a reasoning line "cause → effect" (ref) — `{cause, effect, role, t, dur, left, top}`. **NB:** the text fields are `cause`/`effect`, NOT `left`/`right` — `left`/`top` are the card's position.

Colour: prefer a semantic **`role`** on any card (`emphasis`/`success`/`danger`/`caution`/`info`/`baseline` → the light-brand hue, from `brand_kit.ROLES`) so the border carries MEANING — e.g. a "cost/pain" card = `danger` (coral), a "solution" card = `success` (green), a topic = `emphasis` (blue). Legacy accents `cyan`/`violet`/`gold`/`green`/`blue`/`coral` still work. Use 1 main role + at most 1 secondary per video to avoid clutter. (Craft basis: `2_KNOWLEDGE/style_references/talking_head/CRAFT-STUDY-2026-07.md` + `per_video/`.)

### 4. Place cards/callouts so they don't cover the face

- For talking-head: place the card in the empty area opposite the face, usually above the shoulder or on the still-empty side of the frame.
- Each card has its own time window; don't show multiple cards at once if the video is short.
- Don't let a card cover the caption, eyes, mouth, important UI, or the main product.
- If using a full-screen mockup/cutaway, don't show a card at the same time.
- The first card should appear within the first 1-3 seconds if the video has a sales or viral hook.

### 5. Build an animated UI mockup when the video needs an app demo

Use a mockup when the footage is only talking-head but the content is talking about an app/web/tool that needs illustrating.

Procedure:

1. Take a real screenshot if possible:

```powershell
capture_shot.ps1 -Url <url> -Out <abs.png>
```

Capture the homepage or a public page; avoid the login page. If you hit a 403, captcha, or blank screen, switch pages or draw a mockup.

2. Draw each UI as a separate HyperFrames HTML file: 1080x1920, with `#stage` and `window.__timelines["main"]`.
3. Animation uses only `tl.set()` and `tl.to()`. Do not use `tl.call()` because render-seek may not run it.
4. Typewriter effects must be pre-baked per `<span opacity="0">`, then enabled with `tl.set(span,{opacity:1}, t)`.
5. Render each mockup into a clip, then overlay the cutaway at the right moment with ffmpeg:

```bash
[i]setpts=PTS+START/TB[ci]
overlay=enable='between(t,START,END)'
```

6. After you have `combined_visual`, re-mux the original voice then run `edit_footage.py` to add cards, karaoke captions and SFX.

For app demo videos, you must prepare at least 2-3 different mockups or illustrations, one screen per feature. Don't use a single mockup for the whole video.

### 6. Run edit footage

Run:

```bash
npm run talkinghead:edit -- --spec cards.json --video <mp4> --words words_fixed.json --out final.mp4 --caption-chunk 6
# (= python scripts/talking_head_edit.py --spec cards.json --video <mp4> --words words_fixed.json --out final.mp4 --caption-chunk 6)
```

Don't use the scene-slides `--post` for this workflow. If you change the caption/card but not the footage, just update `cards.json` or `words_fixed.json` and re-run the edit command.

## Quick style recipes

### Talking-head app review

- Style: `karaoke_neon` or `tiktok_bold`.
- Caption: `caption_bottom: 380`, `--caption-chunk 5-6`.
- Cards: `term` at the hook, `bullet` for 3 benefits, `stat` for price/speed/result.
- SFX: `whoosh` for card entry, `pop` for bullets, `ding/success` for results.

### Tutorial screen-recording

- Style: `clean_tutorial` or `screen_demo`.
- Caption: chunks of 6-8 words, avoid covering the menu bar, buttons, terminal or form.
- Cards: few, use a callout in the right spot instead of a large card.
- Mockup: only overlay when you need to zoom into an important action.

### Sales / service-intro video

- Style: `tiktok_bold` for the hook, then `karaoke_neon`.
- Cards: hook in the first 1-2 seconds; benefit cards appear when the speaker mentions the right point.
- Caption: accent keywords for the problem, solution, numbers, CTA.
- SFX: varied but no denser than 1 effect every 2-4 seconds.

### Analysis / news video

- Style: `authority_news`.
- Cards: use a headline/lower-third, little motion.
- Caption: steady rhythm, don't use too many emojis or bounce.
- SFX: light, mostly whoosh/ding at transitions.

## Mandatory rules

1. Text in the caption/card must be the correct display form, don't write phonetics into the transcript or on-screen text.
2. `caption_bottom` always keeps the 380-390 safe zone for 9:16, unless the UI forces you to avoid that area.
3. Cards, mockups and captions must not overlap each other; with a full-screen mockup cutaway, don't show a card at the same time.
4. SFX must be varied: `whoosh`, `pop`, `coin`, `ding`, `success`, `notify`, `swipe`; don't repeat one sound for every event.
5. Videos longer than 120 seconds must use merged single-clip captions if the pipeline has patched `build_captions`, to avoid dropping clips.
6. Large batches should be split into 6-8 videos per session to avoid context overflow or gateway errors.
7. The export filename should be the post caption with diacritics plus hashtags, e.g.: `<Vietnamese hook with diacritics> #seosonavideo #xuhuong #ai #tool #automation (9x16).mp4`. Don't use Windows-forbidden characters: `< > : " / \ | ? *`.

## Verify checklist before delivery

Always verify with real data, don't guess:

- Extract frames at multiple marks: video start, mid-video, a section with a card, a section with a mockup, near the end of the video.
- Check that frames are not black; if measuring with ffmpeg, YAVG should be greater than 12.
- Measure loudness near `-16 LUFS` if exporting for social.
- Confirm the duration matches the brief and is at least 45 seconds for a standard intro/review video.
- Check that the caption has the correct brand spelling, figures, terminology and no dropped words.
- Check that cards/mockups don't cover the face, don't cover the caption, don't hide important UI.
- Confirm SFX is not too loud, not monotonously repetitive and does not cover the speech.

## Course / knowledge videos — 3-zone repurpose (SEOSONA, 9:16)

Knowledge/course videos REPURPOSE a real lecture (don't generate). Standard layout cloned from the
reference reels (`2_KNOWLEDGE/style_references/talking_head/`): **TOP = content cards** (header pill +
icon bullet-chips + stat + b-roll) · **MIDDLE = speaker** · **BOTTOM = karaoke**. Always **9:16**
(1080×1920); a 16:9 source is blurred-padded so the speaker sits in the middle band.

Pipeline (`scripts/course_video.py`, npm `video:course`): video → SRT (PhoWhisper-medium) →
**cut-plan** (`9_PROMPTS/COURSE_SPLICE_PROMPT.md` non-linear 5-act matrix → `4_BRAIN/course_planner.py`)
→ splice 9:16 → captions+cards via this engine. Two caption engines: `--captions talkinghead` (ASS,
default) or `--captions embedded` (the `embedded-captions` skill: rail + person-matting).

**Card templates (spec `cards`)** — rendered as ASS pills (BorderStyle-3 box):
- `header` — `{tag, title}`: accent tag pill + bold headline (top-band section header).
- `bullet` — `{title?, rows:[{icon,kw,text}]}`: each row is its own rounded chip (icon ▸●✓★ + accent
  keyword + text), revealed SEQUENTIALLY. Group-B's icon-bullet look.
- `stat` — `{title,sub}`: big accent number + label. `term` — `{title,sub}`.
- accents cyan/violet/gold/green; place in the TOP band (clear of the centered speaker).

**B-roll / layout composites (spec `broll`)** — `[{src, mode, t, dur, top?, left?, width?}]`: overlay a real
screenshot/screen-rec in the content zone for that beat. The "show the tool while I talk" pattern. Images
loop; clips play once. Render preset via `SEOSONA_X264_PRESET` (default `veryfast`). Modes:
- `full` — fills the content zone; add `"frame":true` for a blue-bordered **device-mockup** wrapper.
- `pip` — small blue-framed corner picture-in-picture.
- `split` — **presenter-top / screen-rec-below** demo layout: the b-roll fills the lower band, the speaker
  stays in the top strip; `split_ratio` (default 0.36) sets the seam. Use for step-by-step tool demos.
- `inset` — **Mode-B**: the footage is REPLACED by a light brand gradient (`bg`, default `0xEEF3FF`) and the
  speaker becomes a rounded blue-bordered inset card (`width`/`height`/`left`/`top`); no `src` needed (reuses
  the footage). Use for thesis/bridge beats where a header card sits above the speaker.

Caption placement: `caption_bottom` sets the vertical offset; `caption_align` (2=bottom-centre default, 8=top,
5=mid-float) lets a video float captions mid-frame over the chest (the reels' non-bottom convention).

**Visual ELEMENTS (spec `elements`)** — the dense on-brand element layer (icon-tiles, emojis, badges,
sparkles, arrows, chips, stat pops) popped over the footage synced to each phrase — the thing that makes a
talking-head watch. `[{type, ..params.., t, dur, x, y, w?}]`; each is rendered to a transparent PNG by
`2_SKILLS/element_maker/element_maker.py` and composited with a fade at its beat (top band / beside the face,
never over the mouth). Types: `icon_tile` (glassy tile + line-icon + optional `badge` check/x/warn/q/number +
`label`) · `chip` · `badge` · `emoji` · `sparkle` · `arrow` · `ring` · `big_stat` · `tile3d` (glossy pseudo-3D
app-tile) · `phone` (device bezel, optional `src` screenshot) · `bracket` (HUD corners) · `marker` (highlight
swipe). `icon` accepts a concept word (VN/EN, e.g. "thời gian"/"seo"/"bóng đèn") or a Lucide name; `role` =
emphasis/success/danger/caution/info gives the colour. **Auto-grow:** an unknown concept is resolved on demand
(`element_resolver`: alias → learned cache → fuzzy → local LLM), its Lucide SVG **auto-fetched** into
`7_ASSETS/brand/icons/` and the mapping **learned** — so any new word/case gets an on-brand element and the pool
enriches itself. Pattern: a **problem set** = icon_tiles with a coral `"badge":"x"`, the **solution** = a green
`"badge":"check"` tile; accumulate them across beats. Full catalogue + icon/emoji aliases:
`2_SKILLS/element_maker/element_library.json`; taxonomy: `2_KNOWLEDGE/style_references/talking_head/element_inventory/`.
**Motion:** entrance rise/slide/drop+fade by default; `rich_motion:true` renders every element as an animated
transparent-clip (pop/bounce/spin). **`count_up`** (number 0→value) and **`lottie`** (`src` = a LottieFiles
animation in `7_ASSETS/brand/lottie/`, or a concept alias like "ăn mừng"→fireworks) are ALWAYS animated clips.
**Auto (default, no authoring):** `element_picker` scans the narration and auto-places tiles/emoji + a **count_up
on a spoken number** + a **lottie on a celebration beat** ("thành công/tuyệt vời/…") — a plain talking-head gets
the whole dense, animated element layer for free. All NATIVE/headless (no CapCut).
Example: `{"type":"icon_tile","icon":"thời gian","role":"caution","badge":"x","label":"Mất thời gian","t":2,"dur":6,"x":60,"y":240,"w":210}`.

The cut-plan's matrix carries per-segment `topcard {tag,headline,bullets}` + `broll {src,mode}`;
`course_video` auto-places them (header+bullets in the top band, b-roll over the speaker, karaoke at
the bottom). See `6_SOP/COURSE_VIDEO_SOP.md`.

## Not done in this skill

- Do not create faceless scene-slides with `build_scene_slides.py`.
- Do not auto-generate voice with VieNeu/F5 for this video, unless the user requests a separate voice-over workflow.
- Do not use phonetic text to fix pronunciation in the caption.
- Do not post-process scene-slides or use scene-slides commands on talking-head footage.
