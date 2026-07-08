# Mascot Live2D / Spine Rig — Specification

Goal: a fully-smooth, tween-animated SEOSONA mascot (Chí Quyết) that talks + gestures + emotes, driven
by our audio/script. Live2D Cubism (free tier exists) or Esoteric Spine. This spec is what the rigging
artist needs; the factory then plays the rig via its runtime (integration notes at the end).

## 1. Source artwork required (the ONE thing we must get first)
A **layered file (PSD or Cubism .cmo3 / Spine project)** of ONE front-facing pose, parts on SEPARATE
layers, each drawn COMPLETE (including the parts hidden behind others — the artist must paint behind):
- `hair_front`, `hair_back`
- `head` (face base), `ears`
- `brow_L`, `brow_R`  (separate — for expressions)
- `eye_L`, `eye_R`  → each split: `eyeball` + `eyelid_upper` + `eyelid_lower` + `eye_white` (for blink + look)
- `nose`
- `mouth` → drawn as a NEUTRAL closed mouth on its own layer (rigged open/closed via a mouth-form param)
- `neck`
- `torso` (black polo with the Seosona logo)
- `upper_arm_L`, `forearm_L`, `hand_L`   (split at elbow + wrist for bending)
- `upper_arm_R`, `forearm_R`, `hand_R`
- `glow` (the cyan outer stroke) as a backmost layer
Export at ≥2048px, transparent, art centered, T-pose-ish or relaxed arms (easiest to rig).

> Note: our current AI pose sheets are FLAT (one merged image per pose) — they can't be rigged directly.
> The artist needs the layered file. Prompt the AI/artist for "the same mascot as a LAYERED PSD, each
> body part on its own layer, parts painted complete behind overlaps."

## 2. Deformers / mesh (Cubism)
Add a mesh to each layer; set up:
- **Head**: rotation deformer (pivot at neck) for head turn/tilt ±15°; a warp deformer for slight squash.
- **Eyes**: `ParamEyeLOpen`/`ParamEyeROpen` (1→0 blink), `ParamEyeBallX/Y` (gaze).
- **Brows**: `ParamBrowLY`/`ParamBrowRY` + angle (for happy/surprised/serious).
- **Mouth**: `ParamMouthOpenY` (0 closed → 1 open) + `ParamMouthForm` (−1 frown → +1 smile). This is
  what our lip-sync drives.
- **Arms**: rotation deformers at shoulder + elbow + wrist per arm → `ParamArmL`/`ParamArmR` (and finger
  params if hands need thumbs-up vs point vs open). Model the KEY gestures as param presets.
- **Body**: subtle breathing warp (`ParamBreath`), body angle `ParamAngleX/Y/Z`.
- **Physics**: hair sway + slight arm follow (Cubism Physics) for natural secondary motion.

## 3. Parameters the FACTORY will drive (the runtime contract)
| Param | Source in our pipeline |
|---|---|
| `ParamMouthOpenY` | lip-sync: Rhubarb viseme openness / audio amplitude per frame |
| `ParamMouthForm` | sentiment (smile on positive lines) |
| `ParamEyeLOpen/ROpen` | auto-blink timer (~every 3s) + emphasis |
| `ParamAngleX/Y/Z` | gentle idle noise + nod on emphasis beats |
| `ParamBrowLY/RY` | expression (happy/surprised/serious) per script beat |
| `ParamArmL/ParamArmR` | gesture keyframes on script beats (wave, point, thumbs, count, present) |
| `ParamBreath` | continuous sine |

## 4. Motions to author (Cubism .motion3.json clips)
`idle`, `talk` (subtle), `wave`, `point_L`, `point_R`, `thumbs_up`, `thumbs_double`, `count_1/2/3`,
`present`, `arms_crossed`, `thinking`, `celebrate`, `surprised`, `agree_nod`. Each 0.5–1.5s, loopable.

## 5. Factory integration (what WE build once the rig exists)
- **Runtime**: Cubism Web SDK (pixi-live2d-display) in a headless Chromium (we already run Playwright)
  → drive the params per-frame from our lip-sync + director → capture frames → mux with the CQA voice.
  Alternatively Spine + spine-ts in the same headless-canvas capture path.
- **Driver**: reuse `mascot_perform.py`'s director (beats → gesture) + Rhubarb openness → param timeline;
  render via the runtime instead of pose-swap compositing.
- Deliverable: `scripts/mascot_live2d.py` (author the param timeline + headless-render). Built AFTER the
  rig `.model3.json` is delivered.

## 6. Effort / who does what
- **Artist (Cubism Editor, GUI — cannot be automated)**: §1 layered art + §2 deformers + §4 motions.
  ~1–3 days for a good talking-head+arms rig.
- **Us (code)**: §3 param contract + §5 runtime + driver. We integrate once the rig is delivered.

## When Live2D is worth it
Only if the mascot is a CENTRAL, frequently on-screen character. For occasional mascot stings, the
pose-swap engine (`mascot_perform.py`) or the LivePortrait-face hybrid is enough and needs no artist.
