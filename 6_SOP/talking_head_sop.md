# Talking-Head Video SOP (Engine #2 — footage-based, REAL voice)

SEOSONA Video has **two** production engines. This SOP covers the **footage** engine
(the synthesized engine is `video_production_sop.md` / `tech_news_faceless_sop.md`).

| | Synthesized (engine #1) | **Talking-head (engine #2 — this SOP)** |
|---|---|---|
| Source | text / GitHub / news brief | a real video the creator filmed / screen-recorded |
| Voice | VieNeu AI voice | the creator's **REAL** voice (kept from the footage) |
| Visual | machine-built HyperFrames scenes | the original footage + burned captions/cards |
| Use for | news, explainers, repo showcase | reviews, tutorials, personal intros, courses |
| Skill | `seosona-news-maker` | `talking-head-video-editor` |

## When to use
The user hands you a **filmed clip** (talking to camera or a screen-record with their
voice) and wants it turned into a captioned short/long video — NOT a machine-narrated
one. Keep their real voice; add karaoke captions + accent cards + ducked BGM/SFX.

## Pipeline (2 steps)
```bash
# 1) transcribe the footage's real audio → word-timed transcript (PhoWhisper)
npm run talkinghead:transcribe -- "<path/to/footage.mp4>"

# 2) edit: burn ASS karaoke captions + term/bullet/stat cards, mix ducked BGM + SFX
npm run talkinghead:edit -- "<path/to/footage.mp4>"
```
Core: `scripts/talking_head_transcribe.py` (ASR via `2_SKILLS/srt_maker/asr_router.py`,
PhoWhisper) → `scripts/talking_head_edit.py` (builds an ASS subtitle track with `\k`
karaoke timing + cards, burns it via ffmpeg, mixes BGM sidechain-ducked under the real
voice + SFX from `7_ASSETS/audio/sfx/`).

## Key rules
- **Keep the real voice** — never re-synthesize. The footage audio IS the narration.
- **Resolution follows the footage** — works for BOTH 9:16 and 16:9 (no forced aspect;
  the source dimensions are preserved).
- **RULE #1 still applies to captions** — display form on screen ("SEO", "82%"); the
  ASR transcript is corrected to the display spelling, not phonetic.
- **Captions in the safe zone** — karaoke not jammed at the very bottom; one line at a
  time; current word highlighted, keywords in accent colour.
- **BGM ducked** under the voice (sidechain) so the creator's speech stays clear; SFX
  subtle on cuts/cards.
- **Brand law holds** — light-mode card styling, SEOSONA/CQA accents per brand.

## VERIFY before delivery
- Real voice intact + in sync with captions (no drift).
- Captions = display spelling, correct numbers/terms, no overflow.
- Loudness ~-16 LUFS; BGM never buries the voice; no black frames.
- Output resolution == source resolution (9:16 or 16:9).

## Not this engine
- Machine-narrated / text→video → use `seosona-news-maker` + `video_production_sop.md`.
- This engine does NOT use VieNeu (no AI voice) — it edits existing footage only.
