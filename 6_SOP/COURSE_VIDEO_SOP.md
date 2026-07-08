# SOP — Course / knowledge video (repurpose, talking-head)

Course/knowledge videos are **fundamentally different from news**. News is *generated* from text
(native_composer animated scenes). A course video **repurposes real lecture footage** — we keep the
expert on camera (real voice), just cut it tight and add captions. Never generate a fake course video.

## Pipeline (4 steps — `scripts/course_video.py`, npm `video:course`)
1. **Analyse the video → SRT.** Transcribe the footage (PhoWhisper via `2_SKILLS/srt_maker/asr_router`).
   If you already have the SRT, pass `--srt` to skip.
2. **SRT → content cut-plan.** The BRAIN is the user's proven prompt `9_PROMPTS/COURSE_SPLICE_PROMPT.md`
   — **non-linear splicing** into a 5-act short (HOOK → NỖI ĐAU → TIP/TRICK → CASE STUDY → ĐÚC KẾT),
   100% raw text preserved, captions corrected separately, one SRT isolated per script.
   `4_BRAIN/course_planner.py` produces the cut-plan three ways (best→fallback):
   - **Manual bridge (matches the user's ChatGPT/Gemini workflow):**
     `--emit-prompt` writes the prompt+SRT → run on ChatGPT/Gemini → save the answer →
     `--from-matrix <answer>` parses its ```json block (or table) → non-linear cut-plan.
   - **Auto LLM:** if Ollama/key is reachable, the planner calls it with the same prompt.
   - **Deterministic:** filler-trim (in-order) so the pipeline never blocks.
   Plan segments carry `{part, start, end, raw, display, value, topcard, broll}`.
3. **Cut + splice footage → one coherent lesson.** `--aspect 9:16` (default — course videos are 9:16):
   a 16:9 source is blurred-padded so the speaker sits in the middle band. `--max-height` / `keep` for 16:9.
4. **3-zone talking-head finish** (`scripts/talking_head_edit.py`): **TOP** content cards (header pill +
   icon bullet-chips + stat + b-roll) · **MIDDLE** speaker · **BOTTOM** karaoke. Captions use the
   corrected `display` text; cards from `topcard`; screenshots/screen-rec from `broll`. Real voice +
   ducked BGM + varied SFX (whoosh/swipe/pop/swish at splice points). No AI TTS.

## Templates (3-zone, cloned from `2_KNOWLEDGE/style_references/talking_head/`)
- **header** `{tag,title}` — accent tag pill + bold headline.
- **bullet** `{rows:[{icon,kw,text}]}` — sequential icon chips (▸●✓★ + accent keyword).
- **stat** `{title,sub}` — big number + label. **term** `{title,sub}`.
- **b-roll** `broll:[{src,mode:full|pip,t,dur}]` — overlay a real screenshot/screen-rec (full covers
  the speaker; pip = framed corner). Authored per-segment in the splice matrix; auto-placed by `course_video`.
- Caption style via `--style` (clean_tutorial/authority_news/karaoke_neon/tiktok_bold). Render preset
  `SEOSONA_X264_PRESET` (default veryfast). Output: thumbnail + production_manifest + `(9x16)` filename.

## Run
```
# Manual bridge (recommended — uses your ChatGPT/Gemini prompt):
npm run video:course -- <lecture.srt> --emit-prompt          # → <lecture>.splice_prompt.txt
#   run that on ChatGPT/Gemini, save the answer to answer.txt, then:
npm run video:course -- <lecture.mp4> --srt <lecture.srt> --from-matrix answer.txt --out lesson.mp4

# Fully local (auto LLM if Ollama running, else deterministic):
npm run video:course -- <lecture.mp4>                 # auto-transcribe + sibling .srt
npm run video:course -- <lecture.srt> --plan-only     # inspect the cut-plan on an SRT alone
```

## Aesthetic — B2B expert, light-only (folded in from the retired video_course_sop doc)
- **Strictly light theme** — dark backgrounds PROHIBITED; white/`#F8FAFC` bg + navy text; code snippets use
  a LIGHT syntax theme (GitHub Light) even for coding tutorials. (Same brand contract as news — see `brand_kit`.)
- **9:16 default**, pacing slower + more educational than news; emphasise clear diagrams + readable cards.
- **Voice** = the teacher's REAL footage voice (no TTS). If a preset is ever needed it is Male Southern.
- **Caption style** = karaoke by default; for a calmer "anchor" reading experience (long lessons) pass
  `--style clean_tutorial` (the old anchor-mode is now a caption STYLE option, not a separate rule).
- Meets the delivery gate in `video_production_sop.md` (auto-cleanup, quality report).

## Notes
- Source footage is REQUIRED for steps 3–4. `--plan-only` / SRT-only runs stop after step 2.
- Topic backlog + the SEOSONA teaching voice: `2_KNOWLEDGE/course_content/CATALOG.md` (47 real topics).
- For a tighter short, enable an LLM (Ollama) so the planner selects the lesson core instead of just
  trimming filler. Without an LLM it keeps all substantive cues (a clean, full-length lesson).
- Verified: planner on real SRTs (D:\SRT); splice cut+concat (exact duration). Full E2E needs the
  source videos (only SRTs were provided so far).
