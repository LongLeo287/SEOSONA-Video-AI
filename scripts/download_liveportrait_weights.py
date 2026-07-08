"""Download LivePortrait's MIT weights ONLY (Engine #5 motion).

Skips pretrained_weights/insightface/* on purpose — InsightFace's models are non-commercial and we
replace its detector with MediaPipe (see face_analysis_diy.py swap). Only the Kuaishou MIT models are
pulled: the human landmark ONNX + the appearance/motion/warping/spade/stitching base models.

Run with the LivePortrait venv:
  2_KNOWLEDGE/external_toolkits/.venv-liveportrait/Scripts/python.exe scripts/download_liveportrait_weights.py
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LP = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "LivePortrait")
DST = os.path.join(LP, "pretrained_weights")

REPO = "KwaiVGI/LivePortrait"
FILES = [
    "liveportrait/landmark.onnx",
    "liveportrait/base_models/appearance_feature_extractor.pth",
    "liveportrait/base_models/motion_extractor.pth",
    "liveportrait/base_models/spade_generator.pth",
    "liveportrait/base_models/warping_module.pth",
    "liveportrait/retargeting_models/stitching_retargeting_module.pth",
]


def main():
    from huggingface_hub import hf_hub_download
    os.makedirs(DST, exist_ok=True)
    for f in FILES:
        print(f"[hf] {REPO}/{f}")
        hf_hub_download(repo_id=REPO, filename=f, local_dir=DST)
    print("[OK] LivePortrait MIT weights ->", DST)
    print("     (InsightFace models intentionally NOT downloaded — replaced by MediaPipe)")


if __name__ == "__main__":
    raise SystemExit(main())
