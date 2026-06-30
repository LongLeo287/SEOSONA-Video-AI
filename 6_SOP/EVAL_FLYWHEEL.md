# Eval Flywheel — qualitative QA for videos (Gemini-as-judge)

Adopted from **google/agents-cli**'s "Quality Flywheel" (free/local-only). It adds the
**qualitative** QA layer the metadata gates can't do: `quality_scorer.py` checks ffprobe
metadata (duration, bitrate, captions) and `evaluator.py` checks behaviour (audio not
silent, frames not blank). Neither can hear *"the Vietnamese is awkward"* or see *"the
scenes all look the same"*. The judge does — with Gemini vision, for free.

## What it scores (1–5 each, rubric in `4_BRAIN/eval_judge.py`)
| Dimension | Catches |
|---|---|
| `narration_vn` | English dumps, slug spam, garbled/awkward Vietnamese |
| `brand_fit` | not-light-mode, wrong colours, unprofessional |
| `visual_variety` | repetitive scenes, no real images/data |
| `coherence` | broken hook → body → CTA flow |
| `readability` | overflowing / cut-off on-screen text |

Pass = mean ≥ 3.6 **and** no single dim ≤ 2.

## How to use

**A) Grade ONE video** (after making it):
```
python 4_BRAIN/eval_judge.py "8_WORKSPACE/<name>/<name> - SEOSONA.mp4"
```
Prints the 5 scores + notes; returns a verdict dict.

**B) Run the whole eval set** (regression check after pipeline changes):
```
npm run eval            # judge the videos that already exist in the set (cheap, no GPU)
npm run eval:render     # (re)render any missing one first, then judge all
```
The set is `1_CONFIG/eval_datasets/news_eval.json` (edit to add/remove repos). Results are
written timestamped to `3_MEMORY/eval_results/results_<ts>.json` + a printed summary.

## The flywheel (when a video scores low)
1. **Grade** → see which dimension failed + the note.
2. **Locate the fix:** narration → `make_video` script/lexicon · brand/visual → `native_composer` · readability → fitText / template.
3. **Fix → re-render → re-grade.** Repeat until it passes. Compare against the last
   `results_*.json` to confirm you didn't regress other dimensions.

## Notes / guardrails
- **It is NOT auto-run on every render** (on purpose) — it spends a Gemini call (+ images),
  and the free tier is shared with the news-script generation. Run it as a periodic
  regression check, or on a video you want a second opinion on.
- **Fallback chain when Gemini is down (user's rule "Gemini hết quota → bạn hoặc LLM local xử lý"):**
  `eval_judge` tries **Gemini vision → local Ollama vision → agent-review**. To enable the
  local tier: `ollama serve` + `ollama pull llava` (or qwen2.5vl) + set
  `SEOSONA_OLLAMA_VISION=llava`. If BOTH are unavailable it dumps the frames + narration +
  rubric to `3_MEMORY/eval_results/agent_review/<video>/request.json`, and the **coding agent
  (Claude) grades them in-session** and writes `verdict.json` there.
- Free/local. The Google-Cloud parts of agents-cli (Vertex eval service, BigQuery, GEPA
  optimize) were intentionally NOT adopted.
