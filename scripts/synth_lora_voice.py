# -*- coding: utf-8 -*-
"""Synthesize speech with the fine-tuned Chí Quyết LoRA voice (VieNeu-TTS-0.3B + LoRA).

PROVEN PATH (2026-06-29): timbre similarity 0.973 to the source voice — beats the
zero-shot reference clone (0.944). The LoRA bakes the voice into the weights, so
inference uses the TRAIN-format prompt (phones → speech codes, NO reference), then
the engine's own `_decode` (a hand-rolled codec decode produced silence — use _decode).

ENV: must run in the isolated training venv (torch 2.8 + neucodec), NOT the inference
hermes env (torch 2.5 segfaults on neucodec). See [[dependency-freshness-and-envs]].

    <.venv-train>/python scripts/synth_lora_voice.py "Văn bản tiếng Việt" -o out.wav

Production wiring (TODO): native_composer runs in the hermes env, so to use this voice
it must SUBPROCESS out to the .venv-train python running this script (cross-env bridge),
then read the returned wav. Keep VieNeu zero-shot as the fallback.
"""
import sys, os, argparse

REPO = os.path.join(os.path.dirname(__file__), "..", "2_KNOWLEDGE", "external_toolkits", "VieNeu-TTS")
REPO = os.path.abspath(REPO)
DEFAULT_ADAPTER = os.path.join(REPO, "finetune", "output", "VieNeu-TTS-0.3B-LoRA")
BASE = "pnnbao-ump/VieNeu-TTS-0.3B"

_TTS = None
def _engine(adapter):
    global _TTS
    if _TTS is None:
        sys.path.insert(0, os.path.join(REPO, "src"))
        from vieneu.standard import VieNeuTTS
        dev = "cuda"
        try:
            import torch
            dev = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            pass
        t = VieNeuTTS(backbone_repo=BASE, backbone_device=dev,
                      codec_repo="neuphonic/neucodec", codec_device=dev, gguf_filename=None)
        t.load_lora_adapter(adapter)
        _TTS = t
    return _TTS


def synth(text, out_path, adapter=DEFAULT_ADAPTER, temperature=0.4, top_k=50):
    import soundfile as sf
    from vieneu_utils.phonemize_text import phonemize_with_dict
    tts = _engine(adapter)
    sr = getattr(tts, "sample_rate", 24000) or 24000
    phones = phonemize_with_dict(text)
    prompt = f"<|TEXT_PROMPT_START|>{phones}<|TEXT_PROMPT_END|><|SPEECH_GENERATION_START|>"
    output_str = tts._infer_torch(tts.tokenizer.encode(prompt), temperature=temperature, top_k=top_k)
    wav = tts._decode(output_str)          # engine's correct codes→audio decode
    sf.write(out_path, wav, sr)
    return out_path, len(wav) / sr


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        try: _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    ap = argparse.ArgumentParser(description="Synthesize with the Chí Quyết LoRA voice")
    ap.add_argument("text")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--adapter", default=DEFAULT_ADAPTER)
    ap.add_argument("--temperature", type=float, default=0.4)
    a = ap.parse_args()
    p, dur = synth(a.text, a.out, a.adapter, a.temperature)
    print(f"[synth_lora_voice] {p} ({dur:.1f}s)")
