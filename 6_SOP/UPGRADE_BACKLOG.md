# Upgrade backlog — from the REPO VIDEO.txt vetting (2026-06-29)

~50 repos analysed (4 parallel subagents, clone→study→delete per `REPO_VETTING_SOP.md`). Most are
SKIP (whole apps/pipelines that conflict with native_composer, or no/incompatible license). The
items below passed vetting and are worth building — prioritized by ROI ÷ risk. Done items struck.

## Done this round
- **F5-TTS backup voice** ❌ NOT built / removed — planned as f5_backup.py but never kept (base weights
  are CC-BY-NC non-commercial). Voice arch is now OmniVoice (primary) → VieNeu (backup); edge-tts + F5
  both removed. (Answer to "is F5 better?": for Vietnamese, NO — VieNeu is the backup.)

## High ROI, low risk — build next
1. ✅ **Caption segmentation port** → `4_BRAIN/caption_segment.py` (talking_head_edit `smart_chunk`)
   max-length re-split (~42 chars/line) → break VN captions at natural points, not mid-phrase. Port
   natively into `course_video`/`talking_head_edit` (add `underthesea` VN parse). No new heavy deps.
2. ✅ **Pre-render edit-spec lint** → `4_BRAIN/spec_lint.py`
   first 3s, text density ≤8 EN words / 12 chars per screen, ≤3 numbers/screen, no empty frame >0.5s,
   only last scene may fade-out, inversion-flash ≤2 & ≥8s apart. Checkable rules → a `lint_spec()` gate
   before render (wire into evaluator/quality_scorer).
3. ✅ **Hook loop-back validator** → in `spec_lint.lint_course`
   a ≥4-char hook keyword (rewatch-loop closure). Add to content_moderation / scene gate before TTS.
4. ◻ **Multi-take pick** → NOT built (planned: a best_take.py under voice_cloner; ref-prep already = build_voice_ref.py)
   segment for the VieNeu reference; generate N takes, auto-pick best by speaker-embedding cosine
   (the metric that scored seosona_ref13 at 0.944). Reduces bad-take variance. Engine-agnostic.

## Medium — build when the phase comes
5. ✅ **Auto-publish framework** → `5_FRAMEWORK/publish/publisher.py` (gated, human-in-loop)
   thin publisher `5_FRAMEWORK/publish/<platform>_publisher.py`, Playwright + saved cookie sessions,
   start YouTube + TikTok (YouTube Studio automation, NOT Data API — API force-locks to private). Human
   approval before public. Gate behind loop_guard/STOP. Facebook/IG later (Graph API).
6. ✅ **Footage sourcing** → `scripts/source_footage.py` (yt-dlp)
   wrapper. Treat downloads as reference/B-roll (copyright/ToS caution).
7. ✅ **4-angle ideation** → `4_BRAIN/angle_finder.py`
   temporal/cross-domain) + cliché blocklist + pairwise judge → fills the variant/angle-discovery gap
   in the autonomous-factory north-star. Mine the user's own SRT/repo corpus for non-obvious angles.

## Low / reference-only
8. ✅ **License-first template manifest** → `2_KNOWLEDGE/scripts/template_manifest.py`
   component (input JSON-schema + SPDX/provenance) — makes components agent-readable + attribution clean.
9. **sherpa-onnx VN ASR** (MIT engine): DEFER — 30M is ~10× lighter than PhoWhisper but no word
   timestamps + accuracy downgrade. Add as the LAST `asr_router` fallback only if a no-GPU/streaming
   need appears. PhoWhisper stays primary.

## Rejected (see INGESTION_LOG "Rejected")
fish-speech (non-commercial + torch2.8) · coqui (dead, no VN) · GPT-SoVITS/MOSS/voice-pro/voicebox
(no VN) · capcut-tts-api (no license) · VideoCaptioner (GPL) · opencut/palmier/capcut-cli/openreel
(manual editors conflict with native_composer) · MoneyPrinterTurbo & drama/toon generators (whole
pipelines / off-domain). OmniVoice → REPO_WATCHLIST (VN test).
