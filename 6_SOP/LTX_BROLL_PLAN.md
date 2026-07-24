# GenVideo B-roll Lane — plan (updated 2026-07-14: LOCAL LANE REMOVED)

## Decision history

- 2026-07-14 (morning): LTX-Video local lane audited — built but orphaned; Gate-0 render verified
  (3 s 704×448 clip in ~40 s GPU after pruning 7.5 GB unused cache files).
- **2026-07-14 (user decision): the LOCAL lane is REMOVED entirely.** Rationale: the goal is the
  fastest, best video production — local generation costs 23.6 GB disk, minutes of GPU per clip,
  and competes for the same 12 GB VRAM the render pipeline uses. Deleted: `scripts/ltx_video.py`,
  the `local` adapter in `seedance_engine.py`, `7_ASSETS/models/ltx.ready`, and both HF caches
  (`Lightricks/LTX-Video` 17.7 GB + `LTX-Video-0.9.5` 5.9 GB). Do NOT rebuild the local lane.

## What remains (Engine #6 today)

- `4_BRAIN/seedance_director.py` — script → per-scene grammar-encoded prompts + shotlist HTML.
  Fully functional, zero cost.
- `4_BRAIN/seedance_engine.py` — PROMPT-ONLY mode by default: `make_reel()` writes prompts +
  shotlist honestly (never fakes a render). Paid adapters (fal.ai / Replicate; BytePlus stub)
  auto-activate when a key appears in env/.env.

## When the paid API is enabled (later, per user: "gắn API trả phí thì sẽ tính sau")

1. Add ONE key (FAL_KEY or REPLICATE_API_TOKEN — official accounts only, see the SECURITY note in
   seedance_engine.py; never marketplace resellers).
2. Run the same build phases previously planned for the local lane, unchanged in shape:
   - provenance sidecar `<clip>.gen.json` (prompt, provider, model, seed, cost, checksum),
   - wire into the talking_head_edit b-roll slot + faceless cutaway (opt-in flag, prompt-hash cache
     under `7_ASSETS/broll/` so paid clips are NEVER regenerated for the same prompt),
   - QC gate (ffprobe technical + eval_judge vision; one-variable retakes, max 2, then fall back to
     image_sourcer stock — fail honest),
   - budget guard: hard cap clips-per-video + $ per day logged to the production manifest.
3. V2 mapping: this lane becomes the isolated GenVideo provider adapter (blueprint §10:
   ContinuityLedger + PromptPackage + GeneratedAssetSet, Phase 4/6).
