# -*- coding: utf-8 -*-
"""Stage 1b: encode clip audio → HiggsAudio codec tokens (the format OmniVoice's trainer needs).

Runs OmniVoice's official `extract_audio_tokens` on clips.jsonl (from build_omnivoice_dataset.py)
to produce token WebDataset shards, then writes a SPACE-FREE RELATIVE manifest + data_config.

Why the custom manifest: the tool's own data.lst uses os.path.abspath, and OmniVoice's manifest
parser splits each line on whitespace expecting exactly 4 tokens — the repo path has spaces, so
absolute paths break it. We rebuild the manifest from the known shard patterns with paths RELATIVE
to the workspace (training runs with CWD = workspace).

Runs in the .venv-omnivoice (HiggsAudio tokenizer + torch 2.8 + GPU).

Usage:
  python scripts/encode_omnivoice_tokens.py --out 7_ASSETS/voice/training/cqa_omnivoice
"""
import argparse, glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VENV_PY = os.path.join(ROOT, "7_ASSETS", "voice", ".venv-omnivoice", "Scripts", "python.exe")
TOKENIZER = os.environ.get("SEOSONA_HIGGS_TOKENIZER", "eustlb/higgs-audio-v2-tokenizer")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--samples-per-shard", type=int, default=1000)
    ap.add_argument("--min-shards", type=int, default=8,
                    help="split into ≥N shards so DataLoader num_workers can parallelize (shards ≥ workers)")
    ap.add_argument("--min-sec", type=float, default=2.0)
    ap.add_argument("--max-sec", type=float, default=15.0)
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    clips_jsonl = os.path.join(out, "clips.jsonl")
    if not os.path.isfile(clips_jsonl):
        sys.exit(f"missing {clips_jsonl} — run build_omnivoice_dataset.py first")

    # duration map for the manifest's num_seconds
    dur = {}
    for line in open(clips_jsonl, encoding="utf-8"):
        d = json.loads(line); dur[d["id"]] = float(d.get("duration", 0.0))

    audios = os.path.join(out, "audios"); txts = os.path.join(out, "txts")
    os.makedirs(audios, exist_ok=True); os.makedirs(txts, exist_ok=True)

    # 1) encode → token shards. Windows-safe: 1 worker, no loader workers.
    cmd = [VENV_PY, "-m", "omnivoice.scripts.extract_audio_tokens",
           "--input_jsonl", "clips.jsonl",
           "--tar_output_pattern", "audios/shard-%06d.tar",
           "--jsonl_output_pattern", "txts/shard-%06d.jsonl",
           "--tokenizer_path", TOKENIZER,
           "--samples_per_shard", str(args.samples_per_shard),
           "--min_num_shards", str(args.min_shards), "--nj_per_gpu", "1", "--loader_workers", "0",
           "--min_length", str(args.min_sec), "--max_length", str(args.max_sec),
           "--shuffle", "false", "--skip_errors"]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               HF_HUB_DISABLE_SYMLINKS_WARNING="1")
    print(f"[encode] {' '.join(cmd)}  (cwd={out})")
    r = subprocess.run(cmd, cwd=out, env=env)
    if r.returncode != 0:
        sys.exit(f"[encode] extract_audio_tokens failed (rc={r.returncode})")

    # 2) rebuild a space-free RELATIVE manifest by scanning the produced shards
    shards = sorted(glob.glob(os.path.join(audios, "shard-*.tar")))
    if not shards:
        sys.exit("[encode] no shards produced")
    manifest_path = os.path.join(out, "manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as mf:
        for tar in shards:
            stem = os.path.splitext(os.path.basename(tar))[0]          # shard-000000
            lj = os.path.join(txts, stem + ".jsonl")
            ids = [json.loads(l)["id"] for l in open(lj, encoding="utf-8") if l.strip()]
            secs = sum(dur.get(i, 0.0) for i in ids)
            mf.write(f"audios/{stem}.tar txts/{stem}.jsonl {len(ids)} {secs:.2f}\n")
    print(f"[encode] manifest → {manifest_path}")

    # 3) data_config.json (relative; training runs with CWD=workspace)
    cfg_dir = os.path.join(out, "configs"); os.makedirs(cfg_dir, exist_ok=True)
    data_cfg = {"train": [{"manifest_path": ["manifest.txt"], "repeat": 1}],
                "dev": [{"manifest_path": ["manifest.txt"], "repeat": 1}]}
    json.dump(data_cfg, open(os.path.join(cfg_dir, "data_config.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[encode] {len(shards)} shard(s) → {os.path.join(cfg_dir, 'data_config.json')}")
    print("Next: python scripts/train_omnivoice_cqa.py --smoke")


if __name__ == "__main__":
    main()
