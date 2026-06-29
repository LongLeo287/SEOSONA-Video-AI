# Chí Quyết Voice & Style Profile (CQA branch)

Derived from **47 real lectures (~19.6 hours)** in `D:\SRT` (timing-based — the
transcripts have wrong/extra words + gaps, so this captures RHYTHM + STYLE, not exact
wording). Use this for the **CQA branch only** (courses / lectures / knowledge) — the
LoRA clone voice + the script style. The SEOSONA news branch stays formal + VieNeu.

## Rhythm / pacing (measured)
| Metric | Value |
|---|---|
| Speaking rate | **~268 WPM** (median segment 280) — FAST, energetic |
| Segment length | ~2.0s · ~9 words |
| Pause between phrases | **~0.30s median** (0.49s mean) — near-continuous, few long gaps |

> Implication: CQA scripts should be DENSE + fast. The news pacing (~85 WPM, formal)
> is wrong for CQA — a Chí Quyết lecture flows quickly with short breaths.

## Style markers (his signature — per 1000 words)
- **`cái`** 60 — heavy colloquial filler ("cái việc…", "cái content…")
- **`thì`** 24 · **`mà`** 15 · **`á`** 11 · **`rồi`** 9 — casual connective flow
- **`anh em`** 22 — ALWAYS addresses the audience as "anh em" (bro/folks), never formal "các bạn"
- **`ví dụ`** 3 — teaches by concrete examples
- Occasional `nha` / `nhá` / `đúng không` / `đúng rồi` — friendly check-ins

## How to write a CQA script (Gemini prompt rules)
1. **Voice:** first person, talking to **"anh em"**, warm + confident teacher.
2. **Pace:** dense, fast; short sentences; minimal filler pauses.
3. **Texture:** sprinkle natural `cái / thì / á / rồi` (don't overdo) — it reads as HIM.
4. **Teach by example:** open a point, give a `ví dụ`, land the takeaway.
5. **Open:** "rồi, xin chào anh em… chào mừng anh em quay lại khóa học Chí Quyết Academy".
6. RULE #1 still holds: display text vs spoken; English terms pronounced via lexicon.

## Wiring
- Voice: `2_SKILLS/voice_cloner/voice_router.py`. The Chí Quyết LoRA is **opt-in**
  (`SEOSONA_VOICE=lora`) until a verified adapter exists — **until then CQA temporarily
  uses the Gia Bảo preset** like news (the v1 clone wasn't good enough; v2 is training).
  Re-enable the brand-default gate once the new adapter passes listening QA. See
  [[voice-clone-reference]].
- This profile should be injected into the Gemini system prompt for CQA course videos
  (`npm run video:course`) so the SCRIPT matches his delivery, not just the timbre.
