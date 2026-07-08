# -*- coding: utf-8 -*-
"""Fine-tune OmniVoice on the CQA voice.

Writes a train_config.json (fine-tune hyperparameters sized for a single RTX 3060 12 GB) and
launches OmniVoice's trainer with CWD = the dataset workspace (so the manifest's relative,
space-free paths resolve — the repo lives under a path WITH spaces, which OmniVoice's naive
manifest split can't handle as absolute).

Fine-tunes FROM the pretrained base (`init_from_checkpoint = k2-fsa/OmniVoice`), not from scratch.

Usage (run with the OmniVoice venv is handled internally):
  python scripts/train_omnivoice_cqa.py --smoke          # ~20 steps, validate the loop
  python scripts/train_omnivoice_cqa.py --steps 3000     # real pilot fine-tune
  python scripts/train_omnivoice_cqa.py --resume output/checkpoint-500
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE = os.path.join(ROOT, "7_ASSETS", "voice", "training", "cqa_omnivoice")
VENV_PY = os.path.join(ROOT, "7_ASSETS", "voice", ".venv-omnivoice", "Scripts", "python.exe")
BASE = os.environ.get("SEOSONA_OMNIVOICE_MODEL", "k2-fsa/OmniVoice")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=400,
                    help="steps THIS phase (train in short phases + --resume so the machine stays usable)")
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--batch-tokens", type=int, default=2048, help="smaller = less VRAM/CPU (lighter footprint)")
    ap.add_argument("--grad-accum", type=int, default=2)
    ap.add_argument("--attn", default="sdpa", choices=["sdpa", "eager", "flex_attention"],
                    help="sdpa/eager are safe on Windows; flex_attention needs triton")
    ap.add_argument("--save-steps", type=int, default=500)
    ap.add_argument("--num-workers", type=int, default=2,
                    help="parallel data prep (needs shards≥workers). Windows works now: builder.py "
                         "patched (module-level length_fn + pin_memory=False). Keep modest so CPU stays free.")
    ap.add_argument("--resume", default=None, help="checkpoint dir to resume from, or 'latest'")
    ap.add_argument("--add-steps", type=int, default=0,
                    help="phased training: continue N MORE steps past the resumed checkpoint (sets "
                         "--steps = resumed_step + N). One phase per ping; save-steps caps the phase.")
    ap.add_argument("--smoke", action="store_true", help="~20 steps to validate the loop")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.save_steps = 20, 20

    # --resume latest → newest output/checkpoint-N; --add-steps → cumulative target for this phase.
    _resumed_step = 0
    if args.resume == "latest":
        import glob as _g, re as _re
        cks = [c for c in _g.glob(os.path.join(WORKSPACE, "output", "checkpoint-*"))
               if _re.search(r"checkpoint-(\d+)$", c)]
        args.resume = max(cks, key=lambda c: int(_re.search(r"(\d+)$", c).group(1))) if cks else None
    if args.resume:
        import re as _re
        m = _re.search(r"checkpoint-(\d+)$", args.resume.rstrip("/\\"))
        _resumed_step = int(m.group(1)) if m else 0
    if args.add_steps:
        args.steps = _resumed_step + args.add_steps
        args.save_steps = min(args.save_steps, args.add_steps)  # save at least once this phase
    print(f"[train] phase: resume={args.resume or 'BASE'} (step {_resumed_step}) → target {args.steps} steps")

    cfg = {
        "init_from_checkpoint": BASE,
        "resume_from_checkpoint": args.resume,
        "learning_rate": args.lr,
        "weight_decay": 0.01,
        "max_grad_norm": 1.0,
        "steps": args.steps,
        "seed": 42,
        "lr_scheduler_type": "cosine",
        "warmup_type": "ratio",
        "warmup_ratio": 0.03,
        "batch_tokens": args.batch_tokens,
        "gradient_accumulation_steps": args.grad_accum,
        "num_workers": args.num_workers,
        "mixed_precision": "bf16",
        "attn_implementation": args.attn,
        "logging_steps": 10,
        "eval_steps": max(50, args.save_steps),
        "save_steps": args.save_steps,
        "keep_last_n_checkpoints": 3,
    }
    cfg_dir = os.path.join(WORKSPACE, "configs")
    os.makedirs(cfg_dir, exist_ok=True)
    train_cfg = os.path.join(cfg_dir, "train_config.json")
    json.dump(cfg, open(train_cfg, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[train] wrote {train_cfg}\n{json.dumps(cfg, indent=2)}")

    data_cfg = os.path.join(cfg_dir, "data_config.json")
    if not os.path.isfile(data_cfg):
        sys.exit(f"[train] missing {data_cfg} — run build_omnivoice_dataset.py first.")

    # CWD = workspace so the manifest's relative paths resolve (space-free).
    cmd = [VENV_PY, "-m", "omnivoice.cli.train",
           "--train_config", "configs/train_config.json",
           "--data_config", "configs/data_config.json",
           "--output_dir", "output"]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               HF_HUB_DISABLE_SYMLINKS_WARNING="1")
    print(f"[train] launch (cwd={WORKSPACE}):\n  {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=WORKSPACE, env=env)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
