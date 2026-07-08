"""Download the MuseTalk V1.5 inference weights (Engine #3b).

Pulls ONLY what the inference path needs. Skips:
  - dwpose/*  → replaced by MediaPipe (musetalk/utils/preprocessing.py), not needed
  - syncnet/* → training/eval only

Run with the musetalk venv:
  2_KNOWLEDGE/external_toolkits/.venv-musetalk/Scripts/python.exe scripts/download_musetalk_weights.py
"""
import os
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "MuseTalk", "models")

for sub in ("musetalkV15", "sd-vae", "whisper", "face-parse-bisent"):
    os.makedirs(os.path.join(MODELS, sub), exist_ok=True)


def _hf(repo, filename, local_dir):
    from huggingface_hub import hf_hub_download
    dst = os.path.join(MODELS, local_dir)
    print(f"[hf] {repo}/{filename} -> {local_dir}/")
    hf_hub_download(repo_id=repo, filename=filename, local_dir=dst)


def _url(url, dst_rel):
    dst = os.path.join(MODELS, dst_rel)
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        print(f"[skip] {dst_rel} (exists)"); return
    print(f"[url] {url} -> {dst_rel}")
    urllib.request.urlretrieve(url, dst)


def main():
    # MuseTalk V1.5 UNet + its config (unet is the ~3.4GB lip-sync generator).
    # filename keeps the "musetalkV15/" prefix, local_dir=MODELS → lands at models/musetalkV15/...
    _hf("TMElyralab/MuseTalk", "musetalkV15/unet.pth", "")
    _hf("TMElyralab/MuseTalk", "musetalkV15/musetalk.json", "")

    # SD-VAE (ft-mse) — the latent encoder/decoder
    _hf("stabilityai/sd-vae-ft-mse", "config.json", "sd-vae")
    _hf("stabilityai/sd-vae-ft-mse", "diffusion_pytorch_model.bin", "sd-vae")

    # Whisper-tiny — audio feature extractor MuseTalk conditions on
    for f in ("config.json", "pytorch_model.bin", "preprocessor_config.json"):
        _hf("openai/whisper-tiny", f, "whisper")

    # Face-parsing (BiSeNet) — for jaw-aware blending of the inpainted mouth
    _hf("ManyOtherFunctions/face-parse-bisent", "79999_iter.pth", "face-parse-bisent")
    _url("https://download.pytorch.org/models/resnet18-5c106cde.pth",
         "face-parse-bisent/resnet18-5c106cde.pth")

    print("\n[OK] MuseTalk inference weights ready under", MODELS)


if __name__ == "__main__":
    raise SystemExit(main())
