# Seedance 2.0 — cinematic AI-video prompt system (kho)

Ingested 2026-07-11 from a vetted 5-file pack (`sources/`): 1 VN guide PDF + 2 Claude skills
(higgsfield shotlist-director, seedance-clean prompt-writer) + 2 worked examples. Seedance 2.0 is
ByteDance's photoreal text→video model (served via fal.ai / Replicate / BytePlus ModelArk).

This is a **new capability layer** for the factory: the other engines turn a photo/voice/footage into
a talking head; Seedance **generates cinematic b-roll/scene footage from text**. We adopted it as:

- **`4_BRAIN/seedance_director.py`** — the prompt-authoring CRAFT (this grammar, encoded). script/idea
  → standalone 15s prompts + an editable shotlist HTML (SEOSONA light brand).
- **`4_BRAIN/seedance_engine.py`** — Engine #6. Access-gated client that runs the prompts through a
  provider and stitches clips into a reel. No key → prompt-only (writes shotlist + prompts.txt), never
  a fake render.

## The grammar (one prompt = one ~15s clip, self-contained)

Every prompt carries the **Style Prefix verbatim at the top**, then blocks in this fixed order:

```
[STYLE PREFIX]                     # 8K photoreal, contre-jour natural light, 60:30:10 colour
SUBJECT   — @tag "matches input 100%" + goal + emotional beat. WB <Kelvin>. MULTISHOT.
LOCATION  — @location STYLE REFERENCE ONLY, not a keyframe; model extends the world.
[LAYOUT]  — @scheme (aerial layout) to lock positions across cuts (optional).
ACTION    — one-line intent, then timed SHOT 1/2/3 (0:00–0:15) each ending in a HARD CUT.
CAMERA    — per shot: shot-size + FOV° + move + motivation (mix locked-off/push-in/handheld/drone).
STYLE     — 60:30:10 palette for THIS shot + WB + light reinforcement.
CONSTRAINTS — 16:9, slow-mo opt-in, scale locks, continuity, NO eye glow (always).
```

### Consistency law (encoded as `seedance_director.lint_prompt`)
1 prompt = ~15s (split long scenes Na/Nb/Nc) · positive-only phrasing (state the target, never "no X")
· camera always motivated · @location = reference not keyframe · continuity lives in SUBJECT/ACTION
language, never a visible block · avoid IP/real people/brands · **NO eye glow** always.

### FOV anchor table (discrete degrees, never mm/arbitrary)
180° fisheye · 107° ultra-wide · 84° wide · 63° observational · 47° neutral · 29° portrait-compress ·
18° natural-portrait · 12° tele-detail · 8° extreme-compression. (Full table in `seedance_director.FOV_TABLE`.)

### Two style approaches in the sources
- **Style-Prefix** (PDF + shotlist-director) — one prefix block atop every prompt. **This is what we
  encoded** (canonical, VN-aligned, copy-and-run).
- **Distributed style** (seedance-clean) — no prefix; each style aspect lives in its home block, with a
  deeper optics/consistency protocol (multishot lens-lock stack, whip-pan timing, observation pattern).
  Kept as reference for advanced shots; not the default.

## Provider access (Engine #6)
`python 4_BRAIN/seedance_engine.py --status`. Render backends, preference order:
- **Paid API** (higher quality): `FAL_KEY` (fal.ai) · `REPLICATE_API_TOKEN` (Replicate) · `ARK_API_KEY`
  (BytePlus, stub). None currently configured.
- **`local` — LTX-Video, KEYLESS** (Lightricks, Apache-2.0). Open text→video model on the factory GPU
  (RTX 3060 12GB) via `enable_model_cpu_offload()` — no key, no per-clip cost. Runs in the existing
  torch 2.5 / diffusers 0.38 env (no isolated venv). **VERIFIED producing coherent cinematic b-roll**
  (laptop-on-desk scene, 768×512, 50 steps, ~1min/3s-clip on the 3060).

**Model choice matters (a real trap):** the base `Lightricks/LTX-Video` repo defaults to the **13B**
model (too big for 12GB), and loading a fitting 2B single-file transformer against that repo's newer
13B VAE/scheduler produces **pure noise-mush** (version mismatch, not a bug). The runner uses the
**matched 2B repo `Lightricks/LTX-Video-0.9.5`** (transformer+VAE+scheduler same version) and **reuses
the cached T5 text-encoder** (~18GB, identical across versions) so setup only fetches ~6GB more.
Also: keep **VAE tiling OFF** (it leaves a grid seam); it fits 12GB without it. LTX-2B does object/scene
b-roll well; faces come out softer.

Runner: `scripts/ltx_video.py` (`--setup` / `--ready` / `--prompt … --out … [--steps 40 --guidance 3]`).
`--setup` also disables the HF **Xet** backend (it hangs at 0 bytes on this Windows box). The engine
auto-selects `local` when ready (deterministic marker `7_ASSETS/models/ltx.ready`, written only on a
full download). No backend ready → PROMPT-ONLY. LTX dims via aspect: 16:9→768×512, 9:16→512×768,
1:1→512×512; frames re-rounded to 8k+1. Quality is below paid Seedance 2.0 but is real keyless footage.

## Talking-head craft mined from `sources/talking-head-edit-spec.vi.txt`
That one file is NOT Seedance generation — it's an edit spec for turning a talking-head clip into a
high-retention reel. Its craft was folded into `scripts/talking_head_edit.py` (opt-in):
- **`caption_chunk: 2`** — the ≤2-words-per-cue rule.
- **`bigword: true`** — layered background typography: a LARGE faint keyword plate rises behind the
  captions/cards on emphasis words → the foreground/background depth look.
- Documented gap: TRUE silhouette-occlusion (keyword masked by the speaker's outline) needs a per-frame
  person matte (mediapipe/rembg), unavailable in the default env — an upgrade, not faked.
