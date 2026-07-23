# -*- coding: utf-8 -*-
"""Stage 1 of the OmniVoice CQA fine-tune: cut clean voice clips from lecture media.

Per source file:
  ffmpeg → 24 kHz mono wav → PhoWhisper word timestamps (asr_router, cached) → group words
  into utterance clips by pause gaps → filter (duration + text) → write each clip as a wav in
  clips/ and append {"id","audio_path","text","duration"} to clips.jsonl.

clips.jsonl is the input to Stage 1b `encode_omnivoice_tokens.py`, which runs OmniVoice's
official `extract_audio_tokens` (HiggsAudio codec) to produce the token WebDataset the trainer
needs. (OmniVoice's trainer requires PRE-ENCODED audio tokens, not raw wav.)

Runs in the main (hermes) venv — needs only ffmpeg + asr_router + soundfile.

Usage:
  python scripts/build_omnivoice_dataset.py --sources "E:/2026/THÁNG 05/27.05/DONE" \
      --out 7_ASSETS/voice/training/cqa_omnivoice --max-clips 600
"""
import argparse, glob, hashlib, json, os, subprocess, sys, tempfile
from importlib import import_module

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))

SR = 24000
MEDIA_EXT = (".mp4", ".mp3", ".wav", ".m4a", ".mkv", ".aac", ".flac", ".mov")


def _ffmpeg():
    try:
        return import_module("native_composer")._ffmpeg_bin()
    except Exception:
        return "ffmpeg"


def _discover(sources, filt=None):
    files = []
    for s in sources:
        if os.path.isdir(s):
            for e in MEDIA_EXT:
                files += glob.glob(os.path.join(s, "**", "*" + e), recursive=True)
        elif os.path.isfile(s):
            files.append(s)
    if filt:  # keep only paths containing this substring (e.g. "DONE" = cleaned narration only)
        files = [f for f in files if filt.lower() in f.lower()]
    return sorted(set(files))


def _extract_wav(src, dst, head_sec=0):
    """24 kHz mono wav. head_sec>0 keeps only the first N seconds (breadth sampling across many
    files without demucs-ing whole multi-GB lectures)."""
    cmd = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error"]
    if head_sec:
        cmd += ["-t", str(head_sec)]
    cmd += ["-i", src, "-ac", "1", "-ar", str(SR), "-vn", dst]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return r.returncode == 0 and os.path.exists(dst)


def _isolate_vocals(wav, work):
    """Strip BGM/SFX → vocals-only via Demucs (--two-stems=vocals) so training clips are CLEAN speech
    (lecture videos have music/SFX). Demucs emits 44.1 kHz STEREO, so we ffmpeg it back to SR/mono to
    match the non-isolated path (else clips are the wrong format for token encoding). Returns the
    normalized vocals wav, or the input unchanged on failure."""
    import glob as _g
    od = os.path.join(work, "demucs")
    os.makedirs(od, exist_ok=True)
    try:
        subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-o", od, wav],
                       capture_output=True, text=True, errors="replace", timeout=2400)
        hits = _g.glob(os.path.join(od, "*", "*", "vocals.wav"))
        if not hits:
            return wav
        norm = os.path.join(work, "vocals_24k_mono.wav")
        r = subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                            "-i", hits[0], "-ac", "1", "-ar", str(SR), norm],
                           capture_output=True, text=True, errors="replace")
        return norm if (r.returncode == 0 and os.path.exists(norm)) else hits[0]
    except Exception as e:
        print(f"  ! demucs failed ({e}) — using raw audio"); return wav


def _asr_cached(src, wav, cache_dir, language="vi"):
    """ASR words for a source, cached by path+size+language+wav-mtime so rebuilds (or a switch to
    demucs-cleaned audio / another language) don't reuse a stale transcript."""
    key = hashlib.md5((src + str(os.path.getsize(src)) + language +
                       str(int(os.path.getmtime(wav)))).encode("utf-8")).hexdigest()[:16]
    cp = os.path.join(cache_dir, key + ".json")
    if os.path.exists(cp):
        return json.load(open(cp, encoding="utf-8"))
    asr = import_module("2_SKILLS.srt_maker.asr_router")
    words = asr.transcribe_words(wav, language=language) or []
    json.dump(words, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return words


# CQA speaks Vietnamese but drops in English SEO/tech terms with a strong accent, so ASR mis-hears
# them ("entity"→"NTT/NTV", "schema"→"su sổ"). For the fine-tune to PRONOUNCE these correctly, the
# training TEXT must carry the real English spelling paired with his accented audio. This map rewrites
# the known mis-hearings back to canonical English. Domain = his SEO course (safe, no false positives).
_DEFAULT_TERMS = {
    r"\bNT[TV]\b": "entity", r"\bnt[tv]\b": "entity", r"\ben ?ti ?ti\b": "entity",
    r"\bsu sổ\b": "schema", r"\bsi ma\b": "schema", r"\bsơ ?ma\b": "schema",
    r"\bcon ?ten\b": "content", r"\bkeo ?vớt\b": "keyword", r"\bki ?vớt\b": "keyword",
    r"\bbách ?linh\b": "backlink", r"\bô ?pên\b": "open", r"\bin ?đéc\b": "index",
}


def _load_terms(path):
    m = dict(_DEFAULT_TERMS)
    if path and os.path.exists(path):
        m.update(json.load(open(path, encoding="utf-8")))
    import re as _re
    return [(_re.compile(k, _re.IGNORECASE), v) for k, v in m.items()]


def _fix_terms(text, compiled):
    n = 0
    for rx, repl in compiled:
        text, c = rx.subn(repl, text)
        n += c
    return text, n


def _group_words_to_clips(words, min_sec, max_sec, gap, min_chars):
    clips, cur = [], []

    def flush(ws):
        if not ws:
            return
        start, end = ws[0]["start"], ws[-1]["end"]
        text = " ".join(w["word"] for w in ws).strip()
        if min_sec <= (end - start) <= max_sec and len(text) >= min_chars:
            clips.append({"start": start, "end": end, "text": text})

    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or (w["end"] - cur[0]["start"]) > max_sec):
            flush(cur); cur = []
        cur.append(w)
    flush(cur)
    return clips


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+", default=[])
    ap.add_argument("--sources-file", default=None, help="text file: one media path per line (curated set)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-clips", type=int, default=0)
    ap.add_argument("--max-per-file", type=int, default=0,
                    help="cap clips taken from each source (breadth sampling across many files)")
    ap.add_argument("--head-sec", type=int, default=0,
                    help="only process the first N seconds of each source (fast breadth build)")
    ap.add_argument("--min-sec", type=float, default=2.0)
    ap.add_argument("--max-sec", type=float, default=14.0)
    ap.add_argument("--gap", type=float, default=0.6)
    ap.add_argument("--min-chars", type=int, default=12)
    ap.add_argument("--filter", default=None, help="only sources whose path contains this (e.g. DONE)")
    ap.add_argument("--isolate-vocals", action="store_true",
                    help="Demucs vocal separation (strip BGM/SFX) before ASR/clip — for lecture media with music")
    ap.add_argument("--language", default="vi", help="ASR language for transcript (vi | en)")
    ap.add_argument("--terms-map", default=None,
                    help="JSON of extra {regex: replacement} term fixes (merged onto the built-in SEO map)")
    ap.add_argument("--no-fix-terms", action="store_true", help="disable English term correction")
    args = ap.parse_args()

    terms = [] if args.no_fix_terms else _load_terms(args.terms_map)

    # 2026-07-14 single-ASR consolidation: PhoWhisper-large is the ONLY model. For a non-VI dataset
    # build, transcripts may degrade on English speech — pin SEOSONA_PHOWHISPER_MODEL to a generic
    # Whisper CT2 repo for that one run instead of keeping a second engine wired in.
    if args.language != "vi":
        print(f"[dataset] language={args.language}: single-ASR is PhoWhisper-large (VN-tuned). "
              "For EN sources, set SEOSONA_PHOWHISPER_MODEL to a generic Whisper CT2 repo for this run.")

    import soundfile as sf
    out = os.path.abspath(args.out)
    clips_dir = os.path.join(out, "clips"); cache_dir = os.path.join(out, "asr_cache")
    os.makedirs(clips_dir, exist_ok=True); os.makedirs(cache_dir, exist_ok=True)

    src_args = list(args.sources)
    if args.sources_file:
        src_args += [l.strip() for l in open(args.sources_file, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if not src_args:
        ap.error("provide --sources and/or --sources-file")
    sources = _discover(src_args, args.filter)
    print(f"[dataset] {len(sources)} source file(s)" + (f" (filter={args.filter})" if args.filter else ""))
    jsonl = open(os.path.join(out, "clips.jsonl"), "w", encoding="utf-8")
    tmp_wav = os.path.join(tempfile.gettempdir(), "_ov_src.wav")
    n = 0; total_sec = 0.0; fixes = 0

    for si, src in enumerate(sources, 1):
        if args.max_clips and n >= args.max_clips:
            break
        print(f"[{si}/{len(sources)}] {os.path.basename(src)}")
        if not _extract_wav(src, tmp_wav, head_sec=args.head_sec):
            print("  ! ffmpeg failed — skip"); continue
        wav = tmp_wav
        if args.isolate_vocals:
            wav = _isolate_vocals(tmp_wav, os.path.join(out, "_demucs_work"))
            print("  vocals isolated (demucs)" if wav != tmp_wav else "  (demucs no-op → raw)")
        try:
            words = _asr_cached(src, wav, cache_dir, language=args.language)
        except Exception as e:
            print(f"  ! ASR failed ({e}) — skip"); continue
        if not words:
            print("  ! no words — skip"); continue
        clips = _group_words_to_clips(words, args.min_sec, args.max_sec, args.gap, args.min_chars)
        print(f"  {len(words)} words → {len(clips)} clips")
        audio, sr = sf.read(wav, dtype="float32")
        per = 0
        for c in clips:
            if args.max_clips and n >= args.max_clips:
                break
            if args.max_per_file and per >= args.max_per_file:
                break
            a, b = int(c["start"] * sr), int(c["end"] * sr)
            seg = audio[a:b]
            if len(seg) < int(args.min_sec * sr):
                continue
            key = f"cqa{n:06d}"
            wav_path = os.path.join(clips_dir, key + ".wav")
            sf.write(wav_path, seg, sr, subtype="PCM_16")
            dur = (b - a) / sr
            text, nf = _fix_terms(c["text"], terms) if terms else (c["text"], 0)
            fixes += nf
            jsonl.write(json.dumps({"id": key, "audio_path": wav_path,
                                    "text": text, "duration": round(dur, 3)},
                                   ensure_ascii=False) + "\n")
            n += 1; per += 1; total_sec += dur

    jsonl.close()
    print(f"\n[DONE] {n} clips, {total_sec/60:.1f} min, {fixes} term fixes → {os.path.join(out, 'clips.jsonl')}")
    print("Next: python scripts/encode_omnivoice_tokens.py --out " + args.out)


if __name__ == "__main__":
    main()
