"""
SEOSONA Video — Voice Router (single source of truth for TTS).

Two real paths only, with an HONEST fallback:

  1. VieNeu (primary · local · Apache-2.0 · code-switch native via sea-g2p):
       - clone from a brand reference audio (PREFERRED — keeps the exact brand voice), or
       - a preset voice if no reference.
       Reads Vietnamese correctly AND pronounces English terms in English
       ("AI Agent là tác nhân…" → "AI Agent" stays English).

  2. edge-tts (FALLBACK ONLY): the configured male Vietnamese voice. This is a
       NORTHERN voice and NOT the brand voice — it runs only if VieNeu can't, and
       it is logged loudly so a fallback is never mistaken for the brand voice.

Rebuilt 2026-06-24. The old fish_audio_api.py router had dead branches
(fish_audio/f5tts/cosyvoice/omnivoice all fell through to edge-tts) and duplicate
engines (2× VieNeu, 2× F5, a stray English Kokoro) — all since removed. This router
routes only what actually works.
"""
import os
import subprocess
import glob
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _ffmpeg():
    for c in glob.glob(os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg*")):
        if os.path.exists(c):
            return c
    return "ffmpeg"


def _lora_synth(text, audio_out):
    """Brand voice via the fine-tuned Chí Quyết LoRA (timbre ~0.98). OPT-IN only
    (SEOSONA_VOICE=lora). Runs in the isolated training venv (torch 2.8; neucodec
    segfaults on this env's torch 2.5) via subprocess, then transcodes to audio_out.
    Returns audio_out on success, None on any miss → caller falls back to VieNeu."""
    venv_py = os.path.join(ROOT, "7_ASSETS", "voice", "training", ".venv-train", "Scripts", "python.exe")
    script = os.path.join(ROOT, "scripts", "synth_lora_voice.py")
    adapter = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "VieNeu-TTS",
                           "finetune", "output", "VieNeu-TTS-0.3B-LoRA", "adapter_model.safetensors")
    if not (os.path.exists(venv_py) and os.path.exists(script) and os.path.exists(adapter)):
        print("[Voice Router] LoRA voice unavailable (venv/adapter missing) — using VieNeu.")
        return None
    tmp_wav = audio_out + ".lora.wav"
    try:
        env = dict(os.environ); env["PYTHONIOENCODING"] = "utf-8"
        r = subprocess.run([venv_py, script, text, "-o", tmp_wav],
                           env=env, timeout=600, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(tmp_wav):
            print(f"[Voice Router] LoRA synth failed (rc={r.returncode}) — falling back to VieNeu.")
            return None
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                        "-i", tmp_wav, audio_out], check=True)
        os.remove(tmp_wav)
        print(f"[Voice Router] Engine: Chí Quyết LoRA voice -> {audio_out}")
        return audio_out
    except Exception as e:
        print(f"[Voice Router] LoRA path error ({e}) — falling back to VieNeu.")
        return None


# ---------------------------------------------------------------------------
# SINGLE APPROVED VOICE POLICY
# The brand voice is ONE approved male preset — "Trọng Hữu" (user-selected
# 2026-06-25). All other VieNeu presets (female AND the other male ones) are
# removed from use: any requested voice is coerced to this single approved one.
# The edge fallback is locked to the approved male Vietnamese voice.
# To change the brand voice, edit APPROVED_VOICE (must be a real VieNeu preset).
# ---------------------------------------------------------------------------
APPROVED_VOICE = "Trọng Hữu"
MALE_VIENEU_PRESETS = {APPROVED_VOICE}   # the only voice allowed
DEFAULT_MALE_PRESET = APPROVED_VOICE
MALE_EDGE_VOICE = "vi-VN-NamMinhNeural"


def _coerce_male_preset(voice):
    """Return an approved MALE VieNeu preset, never a female/unknown one."""
    name = str(voice).strip() if voice else ""
    if name in MALE_VIENEU_PRESETS:
        return name
    if name:
        print(f"[Voice Router] '{name}' is not an approved MALE preset -> using {DEFAULT_MALE_PRESET}.")
    return DEFAULT_MALE_PRESET


def _has_vieneu():
    try:
        import vieneu  # noqa: F401
        return True
    except ImportError:
        return False


def _edge_fallback(text, audio_out, fallback_voice, reason):
    print(f"[Voice Router] FALLBACK -> edge-tts ({fallback_voice}) -- {reason}.")
    print("[Voice Router] WARNING: this is the NORTHERN fallback, NOT the brand voice.")
    tts = import_module("2_SKILLS.tts_generator.tts_engine")
    return tts.generate_voice_with_subtitles(text, audio_out, voice=fallback_voice)


def synthesize_voice(
    text,
    audio_out,
    *,
    brand="seosona",
    engine="vieneu",
    preset_voice=None,
    reference_audio=None,
    fallback_voice="vi-VN-NamMinhNeural",
    require_male_southern=False,
):
    """Generate the brand voice. VieNeu primary (clone > preset); edge-tts honest fallback.

    Returns audio_out on VieNeu success, the edge-tts result (path or (path, word_boundaries))
    on fallback, or None only if even the fallback fails.
    """
    # MALE-ONLY: never emit a female voice. Coerce the preset to an approved male
    # one and lock the edge fallback to the approved male voice.
    preset_voice = _coerce_male_preset(preset_voice)
    if fallback_voice != MALE_EDGE_VOICE:
        print(f"[Voice Router] fallback voice coerced to male {MALE_EDGE_VOICE}.")
        fallback_voice = MALE_EDGE_VOICE

    # OPT-IN: fine-tuned Chí Quyết LoRA brand voice (SEOSONA_VOICE=lora). Highest
    # fidelity; on any miss it falls through to the VieNeu path below (unchanged default).
    if os.environ.get("SEOSONA_VOICE", "").lower() == "lora":
        lora = _lora_synth(text, audio_out)
        if lora:
            return lora

    if engine != "vieneu":
        return _edge_fallback(text, audio_out, fallback_voice,
                              f"engine '{engine}' is no longer supported — use 'vieneu'")

    if not _has_vieneu():
        return _edge_fallback(text, audio_out, fallback_voice, "VieNeu is not installed")

    # Cloning is deferred until a >=3s reference exists; vieneu_engine auto-uses the
    # male preset when the reference is missing/too short. Always pass both so the
    # clone activates automatically once a real reference clip is dropped in.
    mode = "clone>preset" if reference_audio else f"preset '{preset_voice}'"
    print(f"[Voice Router] Engine: VieNeu ({mode}) | brand: {brand} | male voice: {preset_voice}")
    vieneu = import_module("2_SKILLS.voice_cloner.vieneu_engine")
    result = vieneu.synthesize(text, audio_out, voice=preset_voice, reference_audio=reference_audio)
    if result:
        return result
    return _edge_fallback(text, audio_out, fallback_voice, "VieNeu generation failed")


# Backward-compatible alias for the previous call site.
clone_voice = synthesize_voice
