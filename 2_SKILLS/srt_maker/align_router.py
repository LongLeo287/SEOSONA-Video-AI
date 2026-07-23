#!/usr/bin/env python
"""align_router — Vietnamese FORCED ALIGNMENT: (wav, known text) -> measured word timestamps.

author: SEOSONA  ·  place at  <LEGACY_ROOT>/2_SKILLS/srt_maker/align_router.py

The V2 seam `@seosona/engines` `alignAdapter.alignWords(wav, text)` calls
`align_router.align_words(wav, text)` and expects on stdout:
    SEOSONA_ALIGN_RESULT:[{"word": "...", "start": <sec>, "end": <sec>}, ...]

Forced alignment KNOWS the words (the script V2 fed to OmniVoice) — it only measures WHEN each is
spoken. Source-agnostic: an OmniVoice voice-CLONE wav aligns like any recording.

Implementation: torchaudio.functional.forced_align + merge_tokens over a Vietnamese wav2vec2-CTC
model (`nguyenvulebinh/wav2vec2-base-vietnamese-250h`). torchaudio ships forced_align as a compiled
wheel (no C++ build needed), and the VN model's own tokenizer handles Vietnamese vocab (tone
diacritics). Deps (torch/torchaudio/transformers) are already in the legacy hermes venv.

Never fabricates — any failure raises, and the V2 seam then keeps the honest syllable estimate.
"""
import json
import re
import sys

MODEL = "nguyenvulebinh/wav2vec2-base-vietnamese-250h"
_STATE = None


def _load():
    global _STATE
    if _STATE is None:
        import torch
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        proc = Wav2Vec2Processor.from_pretrained(MODEL)
        model = Wav2Vec2ForCTC.from_pretrained(MODEL).to(device).eval()
        _STATE = (proc, model, device)
    return _STATE


def align_words(wav_path: str, text: str):
    """Return [{'word': str, 'start': float_sec, 'end': float_sec}] for the words of `text`."""
    if not text or not text.strip():
        return []
    import torch
    import torchaudio
    import torchaudio.functional as AF

    proc, model, device = _load()

    wav, sr = torchaudio.load(wav_path)
    if wav.shape[0] > 1:
        wav = wav.mean(0, keepdim=True)  # mono
    if sr != 16000:
        wav = AF.resample(wav, sr, 16000)
        sr = 16000
    num_samples = wav.shape[1]

    with torch.inference_mode():
        iv = proc(wav.squeeze(0).cpu().numpy(), sampling_rate=16000, return_tensors="pt").input_values.to(device)
        logits = model(iv).logits[0]                   # (T, V)
        emission = torch.log_softmax(logits, dim=-1)   # (T, V)
    n_frames = emission.shape[0]
    if n_frames == 0:
        return []
    sec_per_frame = (num_samples / sr) / n_frames

    vocab = proc.tokenizer.get_vocab()                 # token -> id
    delim = "|" if "|" in vocab else None
    blank_id = proc.tokenizer.pad_token_id if proc.tokenizer.pad_token_id is not None else 0

    # target token ids + each word's [start,end) index range within the target list.
    words = [w for w in re.split(r"\s+", text.lower().strip()) if w]
    targets, ranges = [], []
    for i, w in enumerate(words):
        s = len(targets)
        for ch in w:
            tid = vocab.get(ch)
            if tid is not None:                        # skip a char the model's vocab lacks (stays robust)
                targets.append(tid)
        if len(targets) > s:
            ranges.append((w, s, len(targets)))
        if delim is not None and i < len(words) - 1:
            targets.append(vocab[delim])
    if not targets or not ranges:
        return []

    tgt = torch.tensor([targets], dtype=torch.int32, device=device)
    aligned, scores = AF.forced_align(emission.unsqueeze(0), tgt, blank=blank_id)
    spans = AF.merge_tokens(aligned[0], scores[0], blank=blank_id)  # one span per target token, in order

    out = []
    for (w, s, e) in ranges:
        if e - 1 >= len(spans):
            break
        out.append({
            "word": w,
            "start": round(spans[s].start * sec_per_frame, 3),
            "end": round(spans[e - 1].end * sec_per_frame, 3),
        })
    return out


def main() -> None:
    wav_path, text = sys.argv[1], sys.argv[2]
    print("SEOSONA_ALIGN_RESULT:" + json.dumps(align_words(wav_path, text), ensure_ascii=False))


if __name__ == "__main__":
    main()
