"""
Localizer — translate + dub a source video into a SEOSONA-voiced target language.

Full chain, reusing the existing switchable routers (no new engines):
  1. ASR     : 2_SKILLS.srt_maker.asr_router (PhoWhisper primary) → words → segments
  2. Translate: 2_SKILLS.translator.translate_router (LLM primary, Google backup)
  3. Dub      : 2_SKILLS.voice_cloner.voice_router (VieNeu clone of the brand voice)
  4. Assemble : time-fit each dubbed segment to the original timing (ffmpeg atempo) and
                composite → a translated .srt + a dubbed .wav aligned to the source.

  from repurposer_agent.localizer import localize_video
  out = localize_video("input_en.mp4", src_lang="en", tgt_lang="vi", brand="seosona")
  # -> {"srt": ".../localized.srt", "audio": ".../dubbed.wav", "segments": N}

Every stage degrades gracefully (missing translator → source text; VieNeu fails →
edge-tts fallback inside voice_router). Returns {"error": ...} only on a hard failure.
"""
import os
import sys
from importlib import import_module

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _p in (_ROOT, os.path.join(_ROOT, "2_SKILLS"), os.path.join(_ROOT, "1_AGENTS")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _brand_reference(brand):
    """Resolve the brand's VieNeu reference audio from system_config.yaml."""
    try:
        import yaml
        cfg = yaml.safe_load(open(os.path.join(_ROOT, "system_config.yaml"), encoding="utf-8"))
    except Exception:
        return None, "vi-VN-NamMinhNeural"
    def _find(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == brand and isinstance(v, dict) and isinstance(v.get("voice"), dict):
                    return v["voice"]
                r = _find(v)
                if r:
                    return r
        elif isinstance(d, list):
            for v in d:
                r = _find(v)
                if r:
                    return r
        return None
    voice = _find(cfg) or {}
    ref = voice.get("reference_audio")
    if ref and not os.path.isabs(ref):
        ref = os.path.join(_ROOT, ref)
    return (ref if ref and os.path.exists(ref) else None), voice.get("fallback_voice", "vi-VN-NamMinhNeural")


def _ts(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60); ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _fit_clip(path, slot, max_speed=1.5):
    """Speed a dub clip up (ffmpeg atempo, pitch-preserving) to fit its time slot."""
    try:
        from moviepy.editor import AudioFileClip
        dur = AudioFileClip(path).duration
    except Exception:
        return path, 0.0
    if dur <= slot * 1.05 or slot <= 0:
        return path, dur
    factor = min(dur / slot, max_speed)
    out = path.replace(".wav", "_fit.wav")
    import subprocess
    rc = subprocess.run(["ffmpeg", "-y", "-i", path, "-filter:a", f"atempo={factor:.3f}", out],
                        capture_output=True).returncode
    if rc == 0 and os.path.exists(out):
        try:
            from moviepy.editor import AudioFileClip
            return out, AudioFileClip(out).duration
        except Exception:
            return out, slot
    return path, dur


def localize_video(media_path, src_lang="en", tgt_lang="vi", brand="seosona", out_dir=None):
    if not os.path.exists(media_path):
        return {"error": f"media not found: {media_path}"}
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(media_path)), "localized")
    os.makedirs(out_dir, exist_ok=True)

    # 1. ASR -> segments
    asr = import_module("2_SKILLS.srt_maker.asr_router")
    srt = import_module("2_SKILLS.srt_maker")
    words = asr.transcribe_words(media_path, language=src_lang)
    if not words:
        return {"error": "ASR produced no words"}
    segments = srt.group_words_to_segments(words)
    print(f"[Localizer] {len(segments)} segments from ASR.")

    # 2. Translate
    tr = import_module("2_SKILLS.translator.translate_router")
    segments = tr.translate_segments(segments, src=src_lang, tgt=tgt_lang)

    # 3+4. Dub each translated segment with the brand voice + time-fit
    vr = import_module("2_SKILLS.voice_cloner.voice_router")
    ref, fallback_voice = _brand_reference(brand)
    try:
        from moviepy.editor import AudioFileClip, CompositeAudioClip
    except Exception as e:
        return {"error": f"moviepy unavailable: {e}"}

    clips, srt_lines = [], []
    for i, seg in enumerate(segments, 1):
        text = seg.get("text_translated") or seg.get("text", "")
        srt_lines += [str(i), f"{_ts(seg['start'])} --> {_ts(seg['end'])}", text, ""]
        if not text.strip():
            continue
        seg_wav = os.path.join(out_dir, f"seg_{i:04d}.wav")
        res = vr.synthesize_voice(text, seg_wav, brand=brand, engine="vieneu",
                                  reference_audio=ref, fallback_voice=fallback_voice)
        if not res or not os.path.exists(seg_wav):
            continue
        fitted, _ = _fit_clip(seg_wav, max(0.3, float(seg["end"]) - float(seg["start"])))
        try:
            clips.append(AudioFileClip(fitted).set_start(float(seg["start"])))
        except Exception:
            pass

    srt_path = os.path.join(out_dir, "localized.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(chr(10).join(srt_lines))

    audio_path = None
    if clips:
        audio_path = os.path.join(out_dir, "dubbed.wav")
        try:
            comp = CompositeAudioClip(clips)
            comp.write_audiofile(audio_path, fps=44100, logger=None)
            comp.close()
        except Exception as e:
            print(f"[Localizer] audio assemble failed: {e}")
            audio_path = None
        for c in clips:
            try: c.close()
            except Exception: pass

    print(f"[Localizer] done: srt={srt_path} audio={audio_path}")
    return {"srt": srt_path, "audio": audio_path, "segments": len(segments)}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Localize (translate+dub) a video into the SEOSONA brand voice")
    ap.add_argument("media"); ap.add_argument("--src", default="en"); ap.add_argument("--tgt", default="vi")
    ap.add_argument("--brand", default="seosona")
    a = ap.parse_args()
    print(localize_video(a.media, a.src, a.tgt, a.brand))
