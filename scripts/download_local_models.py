"""
Pre-download / warm the local models SEOSONA Video uses, so the first render isn't
slowed by a cold model fetch.

Primary (and only) TTS engine: VieNeu (local, Apache-2.0). Initializing it downloads
the model weights from HuggingFace into the local cache. (Kokoro was removed — it was
an English engine and is no longer part of the system.)
"""
import sys


def warm_vieneu():
    print("[models] Warming up VieNeu TTS (downloads weights on first run)...")
    try:
        from vieneu import Vieneu
        Vieneu(mode="v3turbo")
        print("[models] VieNeu v3turbo ready (weights cached).")
        return True
    except ImportError:
        print("[models] 'vieneu' is not installed. Install it in the voice environment "
              "first, then re-run (see 2_SKILLS/voice_cloner).")
        return False
    except Exception as e:
        print(f"[models] VieNeu warm-up failed: {e}")
        return False


def setup_nvidia_nim():
    print("\n[models] Optional - Nvidia NIM (local LLM via OpenAI-compatible API).")
    print("  Add to .env:  NVIDIA_NIM_API_KEY=nvapi-...")
    print("  local_llm_engine.py will use it for script processing.\n")


if __name__ == "__main__":
    ok = warm_vieneu()
    setup_nvidia_nim()
    print("[models] Local model setup complete." if ok else
          "[models] Setup finished with warnings (VieNeu not warmed).")
    sys.exit(0 if ok else 1)
