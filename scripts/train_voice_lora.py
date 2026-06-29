# -*- coding: utf-8 -*-
"""Orchestrate the VieNeu LoRA fine-tune end-to-end against a prepared dataset.

Given a dataset dir built by build_voice_dataset.py (raw_audio/ + metadata.csv),
this wires it into the cloned VieNeu repo and runs the repo's own scripts in order:
    filter_data.py  → metadata_cleaned.csv  (drop bad clips / digit-acronym text)
    encode_data.py  → metadata_encoded.csv  (NeuCodec speech codes, GPU)
    train.py        → LoRA adapter in finetune/output/<run_name>/   (GPU)

The repo scripts hardcode `finetune/dataset/`, so we junction (or copy) the prepared
dataset there and run with cwd = repo root + PYTHONPATH = repo/src.

Usage:
    python scripts/train_voice_lora.py --dataset 7_ASSETS/voice/training/chiquyet \
        [--max-steps 5000] [--skip-prep]
"""
import os, sys, subprocess, argparse, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "VieNeu-TTS")


def wire_dataset(dataset_src):
    """Point repo/finetune/dataset at the prepared dataset (junction, else copy)."""
    ds = os.path.join(REPO, "finetune", "dataset")
    dataset_src = os.path.abspath(dataset_src)
    if os.path.islink(ds) or os.path.isdir(ds):
        if os.path.islink(ds) or _is_junction(ds):
            os.unlink(ds)
        else:
            shutil.rmtree(ds)
    os.makedirs(os.path.dirname(ds), exist_ok=True)
    # Windows directory junction needs no admin; fall back to copytree.
    try:
        subprocess.run(["cmd", "/c", "mklink", "/J", ds, dataset_src], check=True,
                       capture_output=True, text=True)
        print(f"[train] junction {ds} -> {dataset_src}")
    except Exception as e:
        print(f"[train] junction failed ({e}); copying dataset ...")
        shutil.copytree(dataset_src, ds)


def _is_junction(p):
    try:
        return os.path.isdir(p) and os.readlink(p) is not None
    except OSError:
        return False


def run(script, env=None):
    print(f"\n===== running {script} =====")
    e = dict(os.environ)
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONPATH"] = os.path.join(REPO, "src") + os.pathsep + REPO + os.pathsep + e.get("PYTHONPATH", "")
    if env:
        e.update(env)
    subprocess.run([sys.executable, script], cwd=REPO, env=e, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="prepared dataset dir (raw_audio + metadata.csv)")
    ap.add_argument("--max-steps", type=int, default=None, help="override training max_steps")
    ap.add_argument("--skip-prep", action="store_true", help="skip filter+encode (data already encoded)")
    args = ap.parse_args()

    wire_dataset(args.dataset)

    if args.max_steps:
        cfg = os.path.join(REPO, "finetune", "configs", "lora_config.py")
        txt = open(cfg, encoding="utf-8").read()
        import re
        txt = re.sub(r"'max_steps':\s*\d+", f"'max_steps': {args.max_steps}", txt)
        open(cfg, "w", encoding="utf-8").write(txt)
        print(f"[train] max_steps -> {args.max_steps}")

    if not args.skip_prep:
        run(os.path.join("finetune", "data_scripts", "filter_data.py"))
        run(os.path.join("finetune", "data_scripts", "encode_data.py"),
            env={"CUDA_VISIBLE_DEVICES": "0"})
    run(os.path.join("finetune", "train.py"), env={"CUDA_VISIBLE_DEVICES": "0"})

    out = os.path.join(REPO, "finetune", "output", "VieNeu-TTS-0.3B-LoRA")
    print(f"\n[train] DONE. LoRA adapter -> {out}")


if __name__ == "__main__":
    main()
