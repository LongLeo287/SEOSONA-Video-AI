# -*- coding: utf-8 -*-
"""LTX-Video local text→video runner — keyless AI cinematic footage (the local provider for Engine #6).

LTX-Video (Lightricks, Apache-2.0) is an open text-to-video diffusion model that runs LOCALLY on the
GPU — no API key, no per-clip cost. It fits a 12GB card (RTX 3060) via `enable_model_cpu_offload()` +
VAE tiling. `seedance_director.py` authors the prompt; this runner renders it; `seedance_engine.py`
selects it as the `local` provider when the weights are present.

Runs in the SAME env as the factory (torch 2.5 + diffusers 0.38 already installed — verified) — no
isolated venv needed. Weights live in the HuggingFace cache (~15GB, OUTSIDE the repo).

  python scripts/ltx_video.py --setup                       # download weights (one-time, ~15GB)
  python scripts/ltx_video.py --prompt "a founder demos an AI SEO tool" --out out/clip.mp4 \
      --width 704 --height 480 --frames 121 --fps 24 --steps 30 --seed 7
"""
import os
import sys
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# MATCHED 2B diffusers repo — transformer + VAE + scheduler are all the SAME version, so the denoising
# schedule and latent decode line up. (Mixing a 2B single-file transformer with the base repo's newer
# 13B VAE/scheduler produced pure noise-mush — a version mismatch, not a code bug.) The 2B fits 12GB.
MODEL_ID = os.environ.get("SEOSONA_LTX_MODEL", "Lightricks/LTX-Video-0.9.5")
# The T5-XXL text encoder (~18GB) is identical across LTX versions → reuse the one already cached from
# the base repo instead of re-downloading it with the matched repo.
BASE_ID = os.environ.get("SEOSONA_LTX_BASE", "Lightricks/LTX-Video")
# From MODEL_ID pull only the small matched pieces; the big text_encoder is reused from BASE_ID.
_NEEDED = ["transformer/*", "vae/*", "scheduler/*", "tokenizer/*", "model_index.json"]
# The HF Xet large-file backend hangs at 0 bytes on this Windows box (small files OK, big shards stall);
# force plain-HTTPS resolve so the weight download actually progresses. Verified: VAE 351MB landed in
# seconds with Xet off vs 0 bytes in minutes with it on.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
# Deterministic readiness flag — written ONLY when a full setup() download completes. `local_files_only`
# alone gives false positives on a partial cache, so the engine keys off this marker instead.
MARKER = os.path.join(ROOT, "7_ASSETS", "models", "ltx.ready")


def _round32(v, lo=256):
    v = max(lo, int(v))
    return v - (v % 32)


def _frames_ok(n):
    """LTX wants num_frames = 8*k + 1."""
    n = max(9, int(n))
    return n - ((n - 1) % 8)


def ltx_ready():
    """True only after a full setup() completed (deterministic marker — no partial-cache false positive)."""
    return os.path.exists(MARKER)


def setup(revision=None):
    """Download the matched 2B pieces (transformer+vae+scheduler+tokenizer, ~6GB) from MODEL_ID and
    ensure BASE_ID's T5 text_encoder (~18GB, reused) is present. Idempotent. Writes MARKER on success."""
    from huggingface_hub import snapshot_download
    print(f"[ltx] downloading matched 2B pieces from {MODEL_ID} (transformer+vae+scheduler, ~6GB)…")
    path = snapshot_download(MODEL_ID, revision=revision, allow_patterns=_NEEDED)
    print(f"[ltx] ensuring reused T5 text-encoder from {BASE_ID} (~18GB, one-time)…")
    snapshot_download(BASE_ID, allow_patterns=["text_encoder/*", "tokenizer/*"])
    os.makedirs(os.path.dirname(MARKER), exist_ok=True)
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write(f"{MODEL_ID}\ntext_encoder<-{BASE_ID}\n{path}\n")
    print(f"[ltx] weights ready at: {path}\n[ltx] marker: {MARKER}")
    return path


def generate(prompt, out_mp4, *, width=768, height=512, frames=121, fps=24, steps=40,
             guidance=3.0, seed=None, negative=None, offload="model"):
    """Render ONE clip from a text prompt with LTX-Video (2B). Returns out_mp4."""
    import torch
    from diffusers import LTXPipeline
    from diffusers.utils import export_to_video
    from transformers import T5EncoderModel

    W, H, N = _round32(width), _round32(height), _frames_ok(frames)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
    print(f"[ltx] loading matched 2B pipeline from {MODEL_ID} + reused T5 from {BASE_ID} "
          f"(bf16, {offload}-offload)…")
    # reuse the already-cached T5 (same weights across LTX versions); all other components come matched
    # from the 2B repo → no version-mix mush.
    text_encoder = T5EncoderModel.from_pretrained(BASE_ID, subfolder="text_encoder", torch_dtype=torch.bfloat16)
    pipe = LTXPipeline.from_pretrained(MODEL_ID, text_encoder=text_encoder, torch_dtype=torch.bfloat16)
    # VRAM fit for a 12GB card: keep only the active module on GPU + tile the VAE.
    if offload == "sequential":
        pipe.enable_sequential_cpu_offload()        # smallest VRAM, slowest — the safe fallback
    else:
        pipe.enable_model_cpu_offload()             # module-swap; fits 12GB when ~11GB is free
    # VAE tiling leaves a repeating grid seam on LTX output → keep it OFF by default (the VAE runs alone
    # under model-offload so it fits 12GB). Enable only if a big frame/res render OOMs on VAE decode.
    if os.environ.get("SEOSONA_LTX_VAE_TILING") == "1":
        try:
            pipe.vae.enable_tiling()
        except Exception:
            pass

    gen = None
    if seed is not None:
        gen = torch.Generator(device="cuda").manual_seed(int(seed))
    neg = negative or ("worst quality, blurry, jittery, distorted, watermark, text, "
                       "low resolution, deformed, glitch")
    print(f"[ltx] generating {W}x{H} · {N} frames · {steps} steps · guidance {guidance} …")
    result = pipe(prompt=prompt, negative_prompt=neg, width=W, height=H,
                  num_frames=N, num_inference_steps=int(steps), guidance_scale=float(guidance),
                  generator=gen)
    frames_out = result.frames[0]
    export_to_video(frames_out, out_mp4, fps=int(fps))
    print(f"[ltx] DONE: {out_mp4} ({len(frames_out)} frames @ {fps}fps = {len(frames_out)/fps:.1f}s)")
    return out_mp4


def main():
    ap = argparse.ArgumentParser(description="LTX-Video local text->video runner")
    ap.add_argument("--setup", action="store_true", help="download weights (one-time)")
    ap.add_argument("--ready", action="store_true", help="print READY/NOT-READY and exit")
    ap.add_argument("--prompt")
    ap.add_argument("--out")
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=512)
    ap.add_argument("--frames", type=int, default=121)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--guidance", type=float, default=3.0)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--offload", default="model", choices=["model", "sequential"])
    a = ap.parse_args()

    if a.ready:
        print("READY" if ltx_ready() else "NOT-READY"); return
    if a.setup:
        setup(); return
    if not a.prompt or not a.out:
        ap.error("--prompt and --out are required to generate")
    generate(a.prompt, a.out, width=a.width, height=a.height, frames=a.frames,
             fps=a.fps, steps=a.steps, guidance=a.guidance, seed=a.seed, offload=a.offload)


if __name__ == "__main__":
    main()
