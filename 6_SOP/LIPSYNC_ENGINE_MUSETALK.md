# Engine #3b — MuseTalk lip-sync (mmcv-free)

**What it is.** A high-quality lip-sync engine: a face **image OR real video** + an audio track →
a clip where the mouth is re-drawn to match the audio. Unlike SadTalker (Engine #3, which
*synthesizes the whole head* from a still photo), MuseTalk does **latent-space inpainting of the
mouth region on the source pixels** — it keeps the real face and only redraws the lips, so it is
sharper and works on real footage, not just a portrait.

**Why it was blocked, and how it's unblocked.** Upstream MuseTalk uses DWPose (mmpose + mmcv +
mmdet) *only* to get face landmarks for the mouth crop. That OpenMMLab stack does not build on
Windows — the long-standing "Engine #3 blocked on mmcv". We replaced the landmark step with
**MediaPipe FaceMesh** (pure pip, self-contained), keeping the exact public API and crop formula.
The generator (VAE + UNet, via `diffusers`) is untouched. Result: **the entire inference path is
mmcv-free** and installs with plain pip.

## Layout
- Toolkit: `2_KNOWLEDGE/external_toolkits/MuseTalk/` (patched `musetalk/utils/preprocessing.py`;
  original preserved as `preprocessing_dwpose_original.py.bak`).
- Isolated venv: `2_KNOWLEDGE/external_toolkits/.venv-musetalk/` (torch 2.5.1+cu121, diffusers
  0.30.2, transformers 4.39.2, mediapipe 0.10.18 — **no mmcv/mmpose/mmdet/tensorflow**).
- Weights: `MuseTalk/models/` (musetalkV15/unet.pth + musetalk.json, sd-vae, whisper, face-parse).
  Fetch with `scripts/download_musetalk_weights.py` (skips dwpose — replaced — and syncnet — train-only).
- Engine wrapper: `scripts/lipsync_musetalk.py`.

## Use
```bash
# image (still portrait) OR video (real footage) + SEOSONA's own CQA voice → lip-synced clip
python scripts/lipsync_musetalk.py --face face.png  --audio voice.mp3 --out clip.mp4
python scripts/lipsync_musetalk.py --face host.mp4  --audio voice.mp3 --out clip.mp4 --fp16
# --bbox-shift N nudges the mouth crop up/down if the lips drift
```
Runs the toolkit in its venv as a subprocess (never touches the hermes / OmniVoice envs). Pairs with
the OmniVoice CQA clone — give it a face + `voice.mp3` and composite the result with the talking-head
engine's karaoke captions + element layer.

## Unified lip-sync service (HeyGen-shaped) — `4_BRAIN/lipsync_service.py`
One API over BOTH avatar types, modeled on HeyGen's lipsync API:
- `create(source, audio, avatar_type=, mode=, transcript=, qc=)` → job dict; `get(id)`, `list_jobs()`.
- `avatar_type="expert"` → MuseTalk (#3b, real face); `"mascot"` → Rhubarb (#4, 2D cartoon).
- `mode="speed"` (fp16 draft) | `"precision"` (fp32 + speech-enhanced audio) — HeyGen's speed/precision.
- Job lifecycle `pending→running→completed|failed`; output `video_url` + `caption_url` (SRT from the
  voiced transcript) + `duration` + `qc`. Jobs persist as JSON under `8_WORKSPACE/lipsync_jobs/`.
- The mascot engine runs under the MuseTalk venv (it has Pillow+numpy) — no base-env install.
```bash
python 4_BRAIN/lipsync_service.py --source expert.png --audio voice.mp3 --type expert --mode precision --transcript "..."
python 4_BRAIN/lipsync_service.py --audio voice.mp3 --type mascot     # mascot uses default image
python 4_BRAIN/lipsync_service.py --list
```

## Lip-sync QC — `scripts/lipsync_qc.py` (Rhubarb × MediaPipe)
Independent self-check: Rhubarb (MIT, CPU) gives the viseme-openness the audio implies per time;
MediaPipe measures the ACTUAL mouth aperture in the rendered clip; Pearson-correlate. Catches
frozen-mouth + desync. Calibrated (real data): matched ~0.25–0.33, mismatched ~ −0.25→0.14 → pass
threshold `corr≥0.20` (+ aperture spread ≥0.008 + face-detect ≥0.6). Auto-run on every expert job.

## Engine map
- #1 `native_composer` — faceless HTML+GSAP news (default factory path).
- #2 talking-head footage editor — recut real footage + karaoke + elements.
- #3 `portrait_avatar` (SadTalker) — still photo → synthesized talking head.
- **#3b `lipsync_musetalk` — image/video → mouth-inpaint lip-sync (higher fidelity).**
- #4 `mascot_talk` (Rhubarb) — 2D cartoon viseme mouth.
- **All lip-sync unified behind `lipsync_service.py` (expert+mascot, speed/precision, +QC+SRT).**

## Verified (2026-07-03)
Smoke test on the bundled `yongen.mp4` + audio → 8s 704×1216 H.264 + AAC clip; frames show the mouth
re-drawn per audio frame (open/closed varies) while eyes/hair/clothing stay identical and **no crop
seams** — i.e. the MediaPipe crop is well-placed and the VAE+UNet inpainting runs clean on the 3060.
Also drives from SEOSONA's own OmniVoice **CQA** clone (`cqa_omnivoice_ref.wav`).

## Gotchas fixed while building (all patched in this repo)
1. **mmcv/mmpose** → replaced with MediaPipe FaceMesh in `preprocessing.py`. *The one that mattered.*
2. **mediapipe 0.10.35 dropped the legacy `solutions` API** → pinned `mediapipe==0.10.18` (bundles FaceMesh, no extra model download).
3. **Windows cp1252 console** can't encode `→`/`✓`/`「」` → all engine + download prints made ASCII.
4. **YAML config with Windows `\` paths** → write forward-slash paths (backslash = YAML escape).
5. **inference.py built ffmpeg cmds with UNQUOTED paths** → broke on the space in `D:\SEOSONA AI\...`
   (0 frames → "integer modulo by zero"). Quoted all three `os.system` ffmpeg commands.

## Notes
- Windows console is cp1252 — keep engine prints ASCII (the patch + download script already do).
- `--fp16` recommended on the RTX 3060 (12 GB) for speed; drop it if you see NaNs.
