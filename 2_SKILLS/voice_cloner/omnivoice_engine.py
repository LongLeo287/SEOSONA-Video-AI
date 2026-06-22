import os
import sys
import argparse
import soundfile as sf
import torch
from omnivoice import OmniVoice

def main():
    parser = argparse.ArgumentParser(description="OmniVoice TTS Engine for SEOSONA Video")
    parser.add_argument("--text", type=str, required=True, help="Text to synthesize")
    parser.add_argument("--output", type=str, required=True, help="Output WAV file path")
    parser.add_argument("--ref_audio", type=str, default=None, help="Reference audio for voice cloning")
    parser.add_argument("--ref_text", type=str, default=None, help="Transcript of reference audio")
    
    args = parser.parse_args()

    print("[OmniVoice] Loading model (k2-fsa/OmniVoice)...")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    try:
        model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=device, dtype=dtype)
    except Exception as e:
        print(f"[OmniVoice] Error loading model: {e}")
        sys.exit(1)

    print(f"[OmniVoice] Synthesizing text: '{args.text}'")
    
    try:
        if args.ref_audio and args.ref_text:
            print(f"[OmniVoice] Using voice cloning with ref: {args.ref_audio}")
            audio = model.voice_clone(ref_audio=args.ref_audio, ref_text=args.ref_text, gen_text=args.text)
        else:
            print("[OmniVoice] No reference audio provided, generating standard voice...")
            # If standard generation method exists, use it, otherwise warn.
            # Usually omnivoice requires ref for zero-shot. We will just use voice_clone with a default.
            if hasattr(model, 'generate'):
                audio = model.generate(text=args.text)
            else:
                print("[OmniVoice] Error: OmniVoice typically requires ref_audio and ref_text for cloning.")
                sys.exit(1)

        sf.write(args.output, audio, samplerate=model.sample_rate)
        print(f"[OmniVoice] Audio saved to {args.output}")
        
    except Exception as e:
        print(f"[OmniVoice] Error during synthesis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
