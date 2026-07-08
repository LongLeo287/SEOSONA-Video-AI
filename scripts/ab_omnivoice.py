# -*- coding: utf-8 -*-
"""A/B the fine-tuned OmniVoice checkpoint vs zero-shot — is the CQA clone closer to the source?

Synthesizes the SAME line two ways (fine-tuned checkpoint + zero-shot base), then scores each
against the real CQA reference by MFCC timbre cosine similarity (higher = closer to the source
voice), and saves both wavs for a listening test (the real judge). GPU — run only when training
is NOT running (it needs the VRAM).

Usage:
  python scripts/ab_omnivoice.py                       # latest checkpoint
  python scripts/ab_omnivoice.py --checkpoint 7_ASSETS/voice/training/cqa_omnivoice/output/checkpoint-500
"""
import argparse, glob, os, re, sys, tempfile
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)  # so `2_SKILLS.voice_cloner.*` imports resolve
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
WS = os.path.join(ROOT, "7_ASSETS", "voice", "training", "cqa_omnivoice")
REF = os.path.join(ROOT, "7_ASSETS", "voice", "profiles", "cqa_omnivoice_ref.wav")
TEST = "Chào anh em, hôm nay chúng ta sẽ tối ưu nội dung chuẩn SEO cho website bằng AI."


def _latest_ckpt():
    cks = glob.glob(os.path.join(WS, "output", "checkpoint-*"))
    cks = [c for c in cks if re.search(r"checkpoint-(\d+)$", c)]
    return max(cks, key=lambda c: int(re.search(r"(\d+)$", c).group(1))) if cks else None


def _mfcc_sim(a, b):
    """Cosine similarity of mean-MFCC timbre vectors of two wavs (0..1). librosa if present,
    else a mel-spectrogram fallback via numpy."""
    import numpy as np, soundfile as sf
    def feat(p):
        y, sr = sf.read(p, dtype="float32")
        if y.ndim > 1: y = y.mean(1)
        try:
            import librosa
            m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            return m.mean(1)
        except Exception:
            # crude fallback: log-magnitude spectrum mean (timbre-ish)
            f = np.abs(np.fft.rfft(y[: sr * 3] if len(y) > sr * 3 else y))
            f = np.log1p(f)
            n = 20; step = max(1, len(f) // n)
            return np.array([f[i*step:(i+1)*step].mean() for i in range(n)])
    va, vb = feat(a), feat(b)
    import numpy as np
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))


def _synth(text, out, model=None):
    eng = import_module("2_SKILLS.voice_cloner.omnivoice_engine")
    old = os.environ.get("SEOSONA_OMNIVOICE_MODEL")
    if model:
        os.environ["SEOSONA_OMNIVOICE_MODEL"] = model
    else:
        os.environ.pop("SEOSONA_OMNIVOICE_MODEL", None)
    try:
        return eng.synthesize(text, out, reference_audio=REF)
    finally:
        if old is not None:
            os.environ["SEOSONA_OMNIVOICE_MODEL"] = old
        else:
            os.environ.pop("SEOSONA_OMNIVOICE_MODEL", None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--text", default=TEST)
    args = ap.parse_args()
    ck = args.checkpoint or _latest_ckpt()
    if not ck or not os.path.isdir(ck):
        sys.exit("no checkpoint found — train first")
    out = os.path.join(WS, "ab"); os.makedirs(out, exist_ok=True)
    ft = os.path.join(out, "finetuned.wav"); zs = os.path.join(out, "zeroshot.wav")
    print(f"[A/B] checkpoint = {os.path.basename(ck)}")
    print("[A/B] synth fine-tuned…"); _synth(args.text, ft, model=os.path.abspath(ck))
    print("[A/B] synth zero-shot…"); _synth(args.text, zs, model=None)
    if not (os.path.exists(ft) and os.path.exists(zs)):
        sys.exit("[A/B] a synth failed")
    s_ft = _mfcc_sim(ft, REF); s_zs = _mfcc_sim(zs, REF)
    print("\n===== A/B RESULT (timbre similarity vs CQA source, higher = closer) =====")
    print(f"  fine-tuned ({os.path.basename(ck)}): {s_ft:.4f}   → {ft}")
    print(f"  zero-shot  (base):                   {s_zs:.4f}   → {zs}")
    print(f"  VERDICT: fine-tune {'WINS ✓ (closer to CQA)' if s_ft > s_zs else 'does NOT beat zero-shot yet'} "
          f"(Δ {s_ft - s_zs:+.4f}). Listen to both to confirm.")


if __name__ == "__main__":
    main()
