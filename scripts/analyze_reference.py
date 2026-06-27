# -*- coding: utf-8 -*-
"""Step 1 of the REFERENCE -> VIDEO pipeline.

Analyze a reference video into a structured "analysis bundle" that the
Scene-Composer (step 2) turns into a scenes.json for native_composer (step 3).

Deterministic — no AI here. It extracts:
  - format meta: width/height/aspect, fps, duration, integrated loudness (LUFS)
  - scene boundaries: ffmpeg scene-change detection -> timestamps
  - one representative frame per detected scene (for the vision step)
  - transcript: PhoWhisper/whisper word- and segment-level (script + timing)

Usage:
  node scripts/seosona-python.cjs scripts/analyze_reference.py "<video>" [out_dir]
"""
import os, re, sys, json, subprocess, math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def ffprobe_meta(video):
    out = _run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-show_entries", "format=duration", "-of", "json", video]).stdout
    j = json.loads(out or "{}")
    st = (j.get("streams") or [{}])[0]
    w, h = int(st.get("width", 0)), int(st.get("height", 0))
    num, den = (st.get("r_frame_rate", "30/1").split("/") + ["1"])[:2]
    fps = round(float(num) / float(den or 1), 3)
    dur = round(float((j.get("format") or {}).get("duration", 0)), 2)
    g = math.gcd(w, h) or 1
    aspect = f"{w//g}:{h//g}" if w and h else "?"
    # map to the nearest standard the engine supports
    std = {"9:16": ["9:16"], "16:9": ["16:9"], "1:1": ["1:1"], "4:5": ["4:5"]}
    near = aspect if aspect in std else (
        "9:16" if h > w*1.2 else "16:9" if w > h*1.2 else "1:1")
    return {"width": w, "height": h, "aspect": aspect, "aspect_std": near, "fps": fps, "duration": dur}


def loudness(video):
    err = _run(["ffmpeg", "-hide_banner", "-i", video, "-af", "ebur128=framelog=quiet", "-f", "null", "-"]).stderr
    m = re.search(r"Integrated loudness:\s*\n?\s*I:\s*(-?[\d.]+)\s*LUFS", err) or re.search(r"I:\s*(-?[\d.]+)\s*LUFS", err)
    return float(m.group(1)) if m else None


def detect_scenes(video, dur, threshold=0.30):
    err = _run(["ffmpeg", "-hide_banner", "-i", video,
                "-filter:v", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"]).stderr
    times = sorted(set(round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", err)))
    bounds = [0.0] + [t for t in times if 0.4 < t < dur - 0.2] + [round(dur, 2)]
    scenes = []
    for i in range(len(bounds) - 1):
        s, e = bounds[i], bounds[i + 1]
        if e - s < 0.4:
            continue
        scenes.append({"index": len(scenes), "start": round(s, 2), "end": round(e, 2),
                       "dur": round(e - s, 2), "mid": round((s + e) / 2, 2)})
    return scenes


def scenes_from_transcript(words, dur, gap=0.55, min_dur=2.0):
    """Faceless scene-slide videos transition smoothly (no hard cuts) — scenes map to
    spoken segments. Group words by pauses, then merge tiny segments to >= min_dur."""
    if not words:
        return []
    groups, cur = [], [words[0]]
    for prev, w in zip(words, words[1:]):
        if w["start"] - prev["end"] > gap:
            groups.append(cur); cur = [w]
        else:
            cur.append(w)
    groups.append(cur)
    # merge short groups into the previous one
    merged = []
    for g in groups:
        if merged and (g[-1]["end"] - g[0]["start"] < min_dur or
                       merged[-1][-1]["end"] - merged[-1][0]["start"] < min_dur):
            merged[-1].extend(g)
        else:
            merged.append(g)
    scenes = []
    for g in merged:
        s, e = g[0]["start"], g[-1]["end"]
        scenes.append({"index": len(scenes), "start": round(s, 2), "end": round(e, 2),
                       "dur": round(e - s, 2), "mid": round((s + e) / 2, 2),
                       "text": " ".join(w["word"] for w in g)})
    return scenes


def extract_frames(video, scenes, outdir):
    os.makedirs(outdir, exist_ok=True)
    for sc in scenes:
        out = os.path.join(outdir, f"scene_{sc['index']:02d}.png")
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(sc["mid"]),
              "-i", video, "-frames:v", "1", "-vf", "scale=540:-1", out])
        sc["frame"] = os.path.relpath(out, ROOT).replace("\\", "/")


def transcript(video):
    try:
        sys.path.insert(0, ROOT)
        asr = __import__("2_SKILLS.srt_maker.asr_router", fromlist=["x"])
        words = asr.transcribe_words(video, language="vi")
        for w in words:
            w["start"] = round(w["start"], 2); w["end"] = round(w["end"], 2)
        # group into sentences for readability
        text = " ".join(w["word"] for w in words)
        return {"words": words, "text": text}
    except Exception as e:
        return {"words": [], "text": "", "error": str(e)}


def analyze(video, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    meta = ffprobe_meta(video)
    meta["loudness_lufs"] = loudness(video)
    tx = transcript(video)
    scenes = detect_scenes(video, meta["duration"])
    method = "hard-cut"
    if len(scenes) < 3 and tx.get("words"):
        # smooth-transition / faceless video — derive scenes from spoken segments
        scenes = scenes_from_transcript(tx["words"], meta["duration"])
        method = "transcript-pause"
    meta["scene_method"] = method
    extract_frames(video, scenes, os.path.join(out_dir, "frames"))
    bundle = {
        "source": os.path.abspath(video),
        "meta": meta,
        "scene_count": len(scenes),
        "scenes": scenes,
        "transcript": tx,
        "_next": "Feed frames/ + transcript to the Scene-Composer (step 2) -> scenes.json",
    }
    path = os.path.join(out_dir, "analysis.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)
    print(f"[analyze] {meta['width']}x{meta['height']} ({meta['aspect']} -> {meta['aspect_std']}) | "
          f"{meta['fps']}fps | {meta['duration']}s | {meta['loudness_lufs']} LUFS")
    print(f"[analyze] scenes detected: {len(scenes)} | frames -> {out_dir}/frames/")
    print(f"[analyze] transcript words: {len(tx['words'])}")
    print(f"[analyze] bundle -> {path}")
    return path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: analyze_reference.py <video> [out_dir]"); raise SystemExit(2)
    video = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "8_WORKSPACE", "_ref_analysis")
    analyze(video, out_dir)
