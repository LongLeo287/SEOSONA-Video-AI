"""
On-screen text translation — the image axis (koharu) the audio dub can't reach.

The localizer handles speech (PhoWhisper → translate → VieNeu dub). This handles text
BURNED INTO the image — foreign title cards, hardsubs, signage, thumbnails — via koharu
(mayocream/koharu, GPL-3.0): detect → OCR → translate → inpaint original out → re-render.

koharu is a separate GPL binary (Rust); it is invoked as an isolated subprocess so its
copyleft never touches SEOSONA's own code. Point KOHARU_BIN at the built binary.

  from repurposer_agent.onscreen_translate import translate_onscreen
  out = translate_onscreen("thumbnail_en.png", tgt="vi")   # -> translated image path or None

Graceful: if koharu isn't installed it returns None with a clear message (never crashes).
Pairs with local Gemma as koharu's translation backend (see OS local-llm-gemma).
"""
import os
import shutil
import subprocess
from pathlib import Path


def _koharu_bin():
    return os.environ.get("KOHARU_BIN") or shutil.which("koharu")


def translate_onscreen(image_path, tgt="vi", out_path=None):
    """Translate on-screen text in a single image via koharu. Returns out path or None."""
    if not os.path.exists(image_path):
        print(f"[onscreen] image not found: {image_path}")
        return None
    binary = _koharu_bin()
    if not binary:
        print("[onscreen] koharu not found. Build it from github.com/mayocream/koharu and set "
              "KOHARU_BIN, then re-run. Skipping (non-blocking).")
        return None
    out_path = out_path or str(Path(image_path).with_suffix("")) + f".{tgt}.png"
    # koharu CLI is invoked as an isolated GPL subprocess. Flag names may vary by version;
    # override the template via SEOSONA_KOHARU_ARGS if needed.
    args_tmpl = os.environ.get(
        "SEOSONA_KOHARU_ARGS",
        "--input {input} --output {output} --target-lang {tgt}")
    cmd = [binary] + args_tmpl.format(input=image_path, output=out_path, tgt=tgt).split()
    try:
        rc = subprocess.run(cmd, capture_output=True, text=True, timeout=300).returncode
        if rc == 0 and os.path.exists(out_path):
            print(f"[onscreen] koharu translated {image_path} -> {out_path}")
            return out_path
        print(f"[onscreen] koharu run failed (rc={rc}); check SEOSONA_KOHARU_ARGS for your version.")
        return None
    except Exception as e:
        print(f"[onscreen] koharu error: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(translate_onscreen(sys.argv[1], tgt=sys.argv[2] if len(sys.argv) > 2 else "vi"))
    else:
        print("usage: python onscreen_translate.py <image> [target_lang]")
