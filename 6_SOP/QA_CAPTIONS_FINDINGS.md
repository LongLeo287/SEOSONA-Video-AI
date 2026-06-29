# QA — Captions (RULE #1) & timing sync  ·  2026-06-29 (Phase 2, Task 4)

Harness: `scripts/_qa_captions.py` (fast, no voice) + real renders + ASR probes.

## ✅ RULE #1 — SOLID (8/8 diverse scripts pass)
Tested: numbers, English terms, `24/7` ratio, short, long-dense, punctuation,
acronym-heavy (GEO/AEO/SEO), mixed. For every case the on-screen caption words ==
the **display words** (never the phonetic spoken form). The lexicon expands display→
spoken only for the voice (`SEO→séo`, `E-E-A-T→i i ây ti`, `24/7→…`), and
`align_tts_boundaries_to_display_words` maps timings back onto display words.
Timing is monotonic and non-overlapping. RULE #1 is structurally guaranteed.

## ⚠️ Timing sync — fragile, root-caused
Added a **caption-sync diagnostic** to `native_composer.make_video`:
`[caption-sync] ✓ real …` or `⚠ ESTIMATED timing — ASR N < spoken M`.

Real renders showed the aligner often falls back to **evenly-estimated** timing
(captions still show display words and advance smoothly, but can drift from the voice).

Root cause (proven by probes):
1. **VieNeu clone instability** — the SAME script renders 122 / 174 / 214 / 116 wpm
   across takes; low-quality takes come out slurred and ASR returns *gibberish*
   (e.g. a 96.5s take → "ồ ô đây vũ ly … iraq …", 61 garbage words for ~187 spoken).
   A CLEAN fresh take ASRs correctly ("làm … thời ấy ai cần một lộ trình rõ ràng …").
   This same instability drives the pacing variance.
2. **Index-based 1:1 alignment** — the aligner assumes ASR returns exactly the
   `tts_words` sequence 1:1 by index. Real ASR re-segments freely (`séo`→"diesel"),
   so even a clean take often can't satisfy the per-word grouping → estimate fallback.
3. atempo speed-up is NOT the cause — ASR on a clip before vs after `atempo=1.35`
   was identical.

## Fixes applied (2026-06-29)
**Robust alignment — DONE** (`align_tts_boundaries_to_display_words`). Was all-or-nothing
(one missed word → whole scene dumped to a flat 0..duration estimate). Now:
- **partial-real**: keep real ASR timing for every display word that matched; linearly
  interpolate the gaps (monotonic, non-overlapping). One missed word no longer wrecks sync.
- **plausibility guard**: if ASR words < 0.6× spoken, or < 0.5× display words got timing,
  don't trust garbage per-word timings — spread display words smoothly over the real
  speech **envelope** (`_estimate_word_data(span=…)`), but only when the envelope covers
  >40% of the clip (else flat full-duration). Verified: perfect→real, partial→interpolated,
  garbage(short or full-span)→smooth, RULE #1 always preserved.
- This is **voice-clone-independent** (pure caption-timing logic).

## Still recommended (deferred — user owns voice clone)
1. **Clone stability** — the biggest remaining win (fixes BOTH sync quality and pacing
   variance): retry a take when ASR plausibility is low (the `[caption-sync]` diagnostic
   already flags it), and/or longer/cleaner reference. **User is handling voice clone
   separately**, so the retry hook is left for when that work lands.
