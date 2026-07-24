# -*- coding: utf-8 -*-
"""Phase-0 fixture manifest generator (V2 rebuild gate item).

Selects the 10 ground-truth fixtures the blueprint requires, records checksum + probed
properties for each, and writes docs/v2_phase0/fixtures.json — the immutable reference set
that Phase-1 contracts and golden tests will run against.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs", "v2_phase0")
FFMPEG = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")

# id, path (repo-relative), kind, why it is in the set
FIXTURES = [
    ("fx01_faceless_news_fresh", "8_WORKSPACE/ai-14all/ai-14all - SEOSONA.mp4", "final_video",
     "E2E render on the CONSOLIDATED pipeline (2026-07-14): OmniVoice + PhoWhisper-large + HyperFrames"),
    ("fx02_faceless_news_toby", "8_WORKSPACE/TOBY_LABS_NEWS/FINAL.mp4", "final_video",
     "pre-consolidation faceless news render — regression baseline"),
    ("fx03_faceless_news_selfsuff", "8_WORKSPACE/NEWS_SELFSUFF/FINAL.mp4", "final_video",
     "faceless news, different template rotation"),
    ("fx04_repo_video_promptschat", "8_WORKSPACE/prompts.chat/prompts.chat - SEOSONA.mp4", "final_video",
     "repo→video path with real homepage screenshot"),
    ("fx05_talking_head_reel", "8_WORKSPACE/adsbootcamp_11_07/_reasm_cache.mp4", "footage_video",
     "talking-head source-locked footage (priority production line)"),
    ("fx06_real_speech_short", "7_ASSETS/voice/training/cqa_omnivoice/clips/cqa000000.wav", "speech_audio",
     "real CQA speech 14s — ASR fixture (transcript NOT gold; PhoWhisper-derived)"),
    ("fx07_real_speech_dense", "7_ASSETS/voice/training/cqa_omnivoice/clips/cqa000400.wav", "speech_audio",
     "real CQA speech 13.4s, dense/fast delivery — the clip that exposed the defective medium-ct2 collapse"),
    ("fx08_brand_voice_ref", "7_ASSETS/voice/profiles/cqa_omnivoice_ref.wav", "speech_audio",
     "THE brand-voice clone reference (with sibling .txt transcript)"),
    ("fx09_tts_gold_sentence", "8_WORKSPACE/benchmarks/asr_tts_20260714/tts/omni_zs/s01.wav", "tts_audio",
     "gold-text TTS output — round-trip WER fixture (known text s01)"),
    ("fx10_thumbnail", "8_WORKSPACE/ai-14all/Thumbnail/thumbnail_frame.png", "image",
     "thumbnail artifact from the consolidated pipeline"),
]


def sha256(path, cap=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def probe(path):
    """duration/streams via ffmpeg -i (works for wav/mp4/png poorly — png returns None)."""
    try:
        r = subprocess.run([FFMPEG, "-i", path, "-hide_banner"], capture_output=True, text=True)
        out = r.stderr or ""
        dur = None
        for line in out.splitlines():
            if "Duration:" in line:
                t = line.split("Duration:")[1].split(",")[0].strip()
                hh, mm, ss = t.split(":")
                dur = round(int(hh) * 3600 + int(mm) * 60 + float(ss), 2)
        streams = [line.strip().split(": ", 1)[1][:60] for line in out.splitlines()
                   if "Stream #" in line]
        return dur, streams
    except Exception:
        return None, []


def main():
    os.makedirs(OUT, exist_ok=True)
    entries, missing = [], []
    for fid, rel, kind, why in FIXTURES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            missing.append(fid)
            print(f"[fixtures] MISSING {fid}: {rel}")
            continue
        dur, streams = probe(p)
        entries.append({
            "id": fid, "path": rel.replace("\\", "/"), "kind": kind, "why": why,
            "bytes": os.path.getsize(p), "sha256": sha256(p),
            "duration_s": dur, "streams": streams,
        })
        print(f"[fixtures] {fid}: {os.path.getsize(p):,} B, {dur}s")
    manifest = {"name": "v2_phase0_fixtures", "created": "2026-07-14",
                "note": "Ground-truth set for V2 Phase-1 contract + golden tests. Files are "
                        "IMMUTABLE references — verify sha256 before use.",
                "fixtures": entries, "missing": missing}
    out = os.path.join(OUT, "fixtures.json")
    json.dump(manifest, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[fixtures] {len(entries)}/10 -> {out}" + (f" (MISSING: {missing})" if missing else ""))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
