"""
OmniVoice (k2-fsa/OmniVoice) TTS engine adapter for SEOSONA Video.

Apache-2.0, multilingual zero-shot TTS (646 languages incl. Vietnamese, lang code
`vi`/`vie`). Voice CLONING is the reliable Vietnamese path (voice *design* is ZH/EN
only). Documented synthesis API: model.generate(text=, ref_audio=, ref_text=) -> a
list of waveforms; take audio[0] and write at 24000 Hz.

Exposes synthesize(...) for the dispatcher in fish_audio_api.clone_voice(), plus a
CLI. Pairs with the omnivoice-vi dataset (cached voice.pt prompts) — see
2_KNOWLEDGE/repos/omnivoice-vi-dataset.md.
"""

import os
import sys
import argparse

SAMPLE_RATE = 24000  # OmniVoice output rate


def _load_model():
    import torch
    from omnivoice import OmniVoice
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    return OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=device, dtype=dtype)


def _to_waveform(audio):
    """OmniVoice returns a list/batch of waveforms; normalize to a 1-D numpy array."""
    try:
        import numpy as np
    except ImportError:
        np = None
    if isinstance(audio, (list, tuple)):
        audio = audio[0]
    # torch tensor -> numpy
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    if np is not None:
        audio = np.asarray(audio).squeeze()
    return audio


def synthesize(script_text, audio_out, voice=None, reference_audio=None, ref_text=None):
    """Synthesize speech with OmniVoice. Returns audio_out on success, None on failure.

    voice: optional path to a cached voice.pt prompt (omnivoice-vi profiles).
    reference_audio + ref_text: zero-shot voice cloning inputs.
    """
    try:
        import soundfile as sf
    except ImportError:
        print("[OmniVoice] soundfile not installed.")
        return None
    try:
        model = _load_model()
    except Exception as e:  # noqa: BLE001
        print(f"[OmniVoice] could not load model: {e}")
        return None

    try:
        kwargs = {"text": script_text}
        # Prefer a cached prompt embedding (fast path) if provided.
        if voice and os.path.exists(voice):
            kwargs["voice"] = voice
        elif reference_audio:
            kwargs["ref_audio"] = reference_audio
            if ref_text:
                kwargs["ref_text"] = ref_text

        if hasattr(model, "generate"):
            audio = model.generate(**kwargs)
        elif reference_audio and hasattr(model, "voice_clone"):
            audio = model.voice_clone(ref_audio=reference_audio, ref_text=ref_text or "", gen_text=script_text)
        else:
            print("[OmniVoice] no usable synthesis API on the model.")
            return None

        wav = _to_waveform(audio)
        sr = int(getattr(model, "sample_rate", SAMPLE_RATE) or SAMPLE_RATE)
        sf.write(audio_out, wav, samplerate=sr)
        print(f"[OmniVoice] saved -> {audio_out} ({sr} Hz)")
        return audio_out
    except Exception as e:  # noqa: BLE001
        print(f"[OmniVoice] synthesis failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="OmniVoice TTS Engine for SEOSONA Video")
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ref_audio", default=None)
    parser.add_argument("--ref_text", default=None)
    parser.add_argument("--voice", default=None, help="Cached voice.pt prompt (omnivoice-vi)")
    args = parser.parse_args()
    out = synthesize(args.text, args.output, voice=args.voice,
                     reference_audio=args.ref_audio, ref_text=args.ref_text)
    sys.exit(0 if out else 1)


if __name__ == "__main__":
    main()
