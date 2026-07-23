# SOP: Tech-News Faceless Video Production

Mandatory standard operating procedure for all AI Agents and Human Editors producing "Faceless Tech-News" videos for SEOSONA / Chi Quyet Academy.

> **Related, deliberately SEPARATE:** [`COURSE_VIDEO_SOP.md`](COURSE_VIDEO_SOP.md) shares the brand
> boilerplate (light-mode iron rule · 9:16 · Male-Southern voice) but is a DISTINCT mode: news = fast
> multi-scene + **karaoke word-level captions (65-75%)**; course = slow + **anchor captions (bottom
> 15-20%, no karaoke)** + light-theme code. Not merged (would lose the caption/pacing distinction).

## 1. Iron Rule: 100% LIGHT MODE (No Dark Backgrounds)

- **USE LIGHT COLORS ONLY.** Dark Mode is strictly prohibited.
- All backgrounds must be bright and clean (White `#FFFFFF` or Light Blue `#F4F7FF`). Text must be dark (Navy `#0F172A`).
- Any AI Agent setting dark color codes (`#000000`, `#1A1A1A`) is a critical violation.

## 2. Format & Multi-Scene Standard

- **Aspect Ratio:** Default is strictly 9:16 (1080×1920) vertical. No other aspect ratio should be used unless explicitly overridden.
- **Multi-Scenes Required:** Video must NOT use a single background from start to finish. Minimum 3-5 different scenes stitched together. Each scene lasts ~5-10 seconds with Slide or Crossfade transitions.
- **OODA Loop Constraint:** The system will aggressively reject and auto-rewrite any scene whose script exceeds 15 seconds (roughly ~30-40 words). Keep sentences short and punchy.
- **Duration:** 30 to 60 seconds.
- **Language:** Visible script, subtitles, scene copy, and thumbnail copy must be Vietnamese. Approved technical terms may remain in their correct original spelling.
- **Pronunciation:** English/technical terms must be handled through the pronunciation lexicon, never by writing phonetics into the visible script.

## 3. Typography Standard (Subtitles)

- **Style:** "Karaoke Word-level" — words appear one-by-one in sync with voiceover.
- **Safe Zone:** Always anchored at 65%-75% height from top. Never let text fall into the bottom 25% zone.
- **Highlight Color:** SEOSONA Orange or Royal Blue.
- **Font:** Extra-bold sans-serif. No glowing outlines.
- **Sync Gate:** SRT and embedded subtitle cards must use exact display words from the script, not the pronunciation text sent to TTS.

## 3.1 Voice Standard

- **Required Voice:** the OmniVoice-cloned Chí Quyết (CQA) brand voice (same voice for both brands).
- **Engine:** OmniVoice (k2-fsa, local, VN-native) via `voice_router.synthesize_voice` — the ONLY engine.
- **No Backup:** a failed synth returns None honestly. (VieNeu/edge-tts/F5/LoRA/fish/kokoro/sherpa all removed as of 2026-07-14.)
- **No Female Fallback:** Do not use female presets for news videos.

## 4. Motion & Animation

- **Graphic Cards:** Graphics appear with `Elastic Pop` or `Slide Up` effects.
- **Ken Burns Effect:** All static images must apply slow zoom (105%) to prevent frame freeze.
- **Transitions:** Every scene change must have a visible wipe/slide/crossfade transition and a matching whoosh/swipe SFX.
- **Audio Bed:** Final production videos require background music and SFX. Generated tones are allowed only as fallback when the asset library is empty.

## 5. Branding Rules

- **Watermark:** SEOSONA or CQA logo always anchored at top-left corner.

## 6. Final Delivery Gate

- Main MP4 exists and probes as H.264 video + AAC audio.
- Thumbnail PNG exists in `8_WORKSPACE/<ProjectName>/Thumbnail/`.
- SRT exists in `8_WORKSPACE/<ProjectName>/SRT/` and words match the display script.
- Production manifest reports voice, BGM, and at least one SFX track.
- Do not use `SEOSONA_SKIP_THUMBNAIL=1` for final delivery.
