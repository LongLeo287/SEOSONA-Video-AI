# -*- coding: utf-8 -*-
"""OmniVoice engine — the SEOSONA + CQA brand voice (k2-fsa/OmniVoice, local, VN-trained 8482h).

Runs OmniVoice in its isolated torch-2.8 venv (`7_ASSETS/voice/.venv-omnivoice`) via subprocess —
the main render venv is torch 2.5, so this mirrors the LoRA bridge pattern. Default clone reference =
the cleaned Chí Quyết (CQA) voice; the SAME voice is used for both brands per the brand decision.

Output is post-processed to read cleanly: internal long silences trimmed (no dead gaps) and loudness
normalized. Returns the wav path, or None — OmniVoice is the ONLY voice engine (2026-07-14 decision),
so None means the render handles the no-voice case honestly (no fallback).

LICENSE NOTE: OmniVoice code is Apache-2.0 but the WEIGHTS are CC-BY-NC (Emilia training data — see
the k2-fsa/OmniVoice model card); the owner accepted this risk for voice quality (Phase-0 benchmark).
"""
import os
import sys
import subprocess
import tempfile
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_VENV = os.path.join(ROOT, "7_ASSETS", "voice", ".venv-omnivoice", "Scripts", "python.exe")
_DEFAULT_REF = os.path.join(ROOT, "7_ASSETS", "voice", "profiles", "cqa_omnivoice_ref.wav")
_DEFAULT_REF_TXT = os.path.join(ROOT, "7_ASSETS", "voice", "profiles", "cqa_omnivoice_ref.txt")
_MODEL = os.environ.get("SEOSONA_OMNIVOICE_MODEL", "k2-fsa/OmniVoice")


def available():
    return os.path.exists(_VENV)


def _ffmpeg():
    try:
        return import_module("native_composer")._ffmpeg_bin()
    except Exception:
        return "ffmpeg"


def _ref_text(reference_audio):
    """ref_text for a reference clip: the sibling .txt, else transcribe once (cached)."""
    sib = os.path.splitext(reference_audio)[0] + ".txt"
    if os.path.exists(sib):
        return open(sib, encoding="utf-8").read().strip()
    try:
        asr = import_module("2_SKILLS.srt_maker.asr_router")
        w = asr.transcribe_words(reference_audio, language="vi") or []
        t = " ".join(x["word"] for x in w)
        open(sib, "w", encoding="utf-8").write(t)
        return t
    except Exception:
        return ""


def _post_process(raw, out):
    """Trim internal long silences (no dead gaps) + loudnorm + 48k → the clean delivered wav."""
    r = subprocess.run(
        [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", raw,
         # (1) atrim start=0.1 kills the prompt-TTS ONSET ARTIFACT (a leading click/half-syllable that
         #     prompt-based clones emit before real speech — user: "voice thừa ngay đầu"). Real speech
         #     starts ~0.2s so 0.1s is safe. (2) KEEP natural sentence/scene pauses so the read BREATHES
         #     (user: "đọc 1 lèo"): cap remaining pauses at ~0.45s (was 0.18s = too rushed).
         "-af", "atrim=start=0.16,asetpts=PTS-STARTPTS,"
                "silenceremove=stop_periods=-1:stop_threshold=-34dB:stop_duration=0.45:"
                "start_periods=1:start_threshold=-34dB,loudnorm=I=-16:TP=-1.5,aresample=48000",
         out], capture_output=True)
    if r.returncode == 0 and os.path.exists(out):
        return out
    # if post-process fails, deliver the raw synth rather than nothing
    try:
        import shutil
        shutil.copy(raw, out)
        return out
    except Exception:
        return None


def _chunk_text(text, max_chars=1000):
    """Split a long script into ~max_chars TTS-safe chunks (pattern from nazdridoy/kokoro-tts, MIT):
    normalise whitespace → split at sentence ends → word-split any oversized sentence → greedily pack
    whole sentences up to the limit. A short script (news, < max_chars) returns a single chunk, so the
    common path is unchanged. This guards a minutes-long COURSE script against OmniVoice's context cap."""
    import re
    text = " ".join(str(text or "").split())
    if len(text) <= max_chars:
        return [text] if text else []
    units = []
    for p in re.split(r"(?<=[.!?…])\s+", text):
        if len(p) <= max_chars:
            units.append(p)
        else:                                        # one giant sentence → split at spaces
            piece = ""
            for w in p.split():
                if piece and len(piece) + len(w) + 1 > max_chars:
                    units.append(piece); piece = w
                else:
                    piece = (piece + " " + w).strip()
            if piece:
                units.append(piece)
    chunks, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) + 1 > max_chars:
            chunks.append(cur); cur = u
        else:
            cur = (cur + " " + u).strip()
    if cur:
        chunks.append(cur)
    return chunks


def _synth_one(text, ref, rtext, language, out_wav):
    """One OmniVoice subprocess call → out_wav, or None on failure/timeout."""
    cmd = [_VENV, "-m", "omnivoice.cli.infer", "--model", _MODEL, "--language", language,
           "--text", text, "--ref_audio", os.path.abspath(ref), "--ref_text", rtext, "--output", out_wav]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", HF_HUB_DISABLE_SYMLINKS_WARNING="1")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=env, timeout=int(os.environ.get("SEOSONA_OMNIVOICE_TIMEOUT", "1200")))
    except subprocess.TimeoutExpired:
        print("[OmniVoice] chunk timeout.")
        return None
    if r.returncode != 0 or not os.path.exists(out_wav):
        print(f"[OmniVoice] chunk failed (rc={r.returncode}). {r.stderr[-160:] if r.stderr else ''}")
        return None
    return out_wav


def _concat_wavs(wavs, out):
    """ffmpeg-concat the chunk wavs in order → out (re-encode fallback if stream-copy fails)."""
    # keep the concat list beside `out` (a per-call unique dir) so parallel renders don't share it
    lst = os.path.join(os.path.dirname(os.path.abspath(out)) or tempfile.gettempdir(), "omnivoice_concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for w in wavs:
            f.write("file '%s'\n" % os.path.abspath(w).replace("\\", "/"))
    base = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst]
    if subprocess.run(base + ["-c", "copy", out], capture_output=True).returncode != 0 or not os.path.exists(out):
        subprocess.run(base + [out], capture_output=True)
    return out if os.path.exists(out) else None


def synthesize(text, audio_out, *, reference_audio=None, ref_text=None, language="vi"):
    """Synthesize `text` in the brand (CQA) voice via OmniVoice. Returns audio_out or None. Long scripts
    are auto-chunked (sentence-greedy) with an adaptive-shrink retry so a course-length read never
    truncates on the model's context cap; short scripts stay a single call (unchanged)."""
    if not available():
        print("[OmniVoice] venv not found — falling back.")
        return None
    ref = reference_audio if (reference_audio and os.path.exists(reference_audio)) else _DEFAULT_REF
    if not os.path.exists(ref):
        print("[OmniVoice] no reference clip — falling back.")
        return None
    rtext = ref_text or _ref_text(ref)
    chunks = _chunk_text(text)
    if not chunks:
        return None
    # per-call unique work dir: the factory runs renders as PARALLEL subprocesses that share the system
    # temp, so fixed names (omnivoice_raw.wav / _chunk_NNN.wav / _concat.txt) would collide across renders
    # → one video's voice overwriting another's. Isolate every synthesis in its own dir.
    _work = tempfile.mkdtemp(prefix="omnivoice_")
    raw = os.path.join(_work, "raw.wav")
    print(f"[OmniVoice] synth (brand voice, ref={os.path.basename(ref)}, {len(chunks)} chunk"
          f"{'s' if len(chunks) > 1 else ''})…")
    if len(chunks) == 1:                              # common path (news) — one call, as before
        if not _synth_one(chunks[0], ref, rtext, language, raw):
            print("[OmniVoice] synth failed — falling back.")
            return None
    else:
        wavs = []
        for i, ch in enumerate(chunks):
            w = os.path.join(_work, f"chunk_{i:03d}.wav")
            if _synth_one(ch, ref, rtext, language, w):
                wavs.append(w)
                continue
            # ADAPTIVE SHRINK (kokoro-tts idea): a chunk that overflowed → re-split ~60% and retry. EVERY
            # sub-piece must succeed — check THIS chunk's own output, not the global `wavs` (the old check
            # `if not wavs` only tripped when the FIRST chunk failed, so a failed MIDDLE chunk was silently
            # dropped → a missing narration section desynced from the captions). Fail the synth instead.
            got = []
            for j, s in enumerate(_chunk_text(ch, max_chars=max(200, int(len(ch) * 0.6)))):
                sw = os.path.join(_work, f"chunk_{i:03d}_{j:02d}.wav")
                if not _synth_one(s, ref, rtext, language, sw):
                    print(f"[OmniVoice] chunk {i} (sub-piece {j}) unrecoverable — falling back (no partial audio).")
                    return None
                got.append(sw)
            if not got:
                print(f"[OmniVoice] chunk {i} unrecoverable — falling back.")
                return None
            wavs.extend(got)
        if not _concat_wavs(wavs, raw):
            print("[OmniVoice] concat failed — falling back.")
            return None
    os.makedirs(os.path.dirname(os.path.abspath(audio_out)) or ".", exist_ok=True)
    return _post_process(raw, audio_out)


if __name__ == "__main__":
    txt = sys.argv[1] if len(sys.argv) > 1 else "Xin chào, đây là SEOSONA."
    out = os.path.join(tempfile.gettempdir(), "omnivoice_engine_demo.wav")
    print("result:", synthesize(txt, out))
