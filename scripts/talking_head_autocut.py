# -*- coding: utf-8 -*-
"""Talking-head AUTO-CUT — tighten raw footage by removing silence, filler words, and flubbed takes.

Completes the wire that `talking_head_analyze` always promised ("feed an auto-cut list into
talking_head_edit"): it DETECTED dead-air / duplicate-takes but nothing ever cut them — the editor
overlaid captions on the FULL untrimmed footage. This module turns those detections (plus VN/EN filler
words) into a real EDL: it drops the regions, re-encodes a tightened clip, and RE-TIMES the word list so
karaoke captions / cards stay perfectly in sync on the new shorter timeline.

Clean-room of the idea from browser-use/video-use (MIT): remove umm/uh/false-starts + silence gaps.
Uses the factory's OWN local transcript (asr_router / faster-whisper, keyless) — NOT ElevenLabs.

Pipeline: analyze(words) -> plan_cuts -> keep_segments -> ffmpeg select/aselect concat + retime_words.

  python scripts/talking_head_autocut.py --video raw.mp4 --words words.json \
      --out tight.mp4 --words-out words_tight.json [--silence 0.8 --no-fillers --keep-dupes]
"""
import os
import sys
import json
import argparse
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, os.path.join(ROOT, "4_BRAIN")):
    if p not in sys.path:
        sys.path.insert(0, p)
import native_composer as nc          # _ffmpeg_bin / _ffprobe_bin
import talking_head_analyze as tha    # detect_silences / detect_fillers / detect_duplicate_takes


def _probe_dur(video):
    r = subprocess.run([nc._ffprobe_bin(), "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", video], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _merge(regions):
    """Sort + merge overlapping/adjacent [start,end] regions into a clean non-overlapping list."""
    regions = sorted((float(s), float(e)) for s, e in regions if float(e) > float(s))
    out = []
    for s, e in regions:
        if out and s <= out[-1][1] + 1e-3:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def plan_cuts(words, *, silence_s=0.8, silence_pad=0.15, min_cut=0.12,
              drop_fillers=True, drop_dupes=True, filler_pad=0.03, duration=None):
    """Return (cuts, report): cuts = merged [start,end] regions to REMOVE.

    - silence: cut the gap but leave `silence_pad` of breathing room on each side; skip if the
      remaining cut would be shorter than `min_cut`.
    - fillers: cut each filler word span (small pad).
    - dupes: cut take1 (the flubbed earlier take), keep take2.
    """
    rep = tha.analyze(words, silence_s)
    cuts = []
    for s in rep["silences"]:
        a, b = s["start"] + silence_pad, s["end"] - silence_pad
        if b - a >= min_cut:
            cuts.append((a, b))
    if drop_fillers:
        for f in rep["fillers"]:
            cuts.append((max(0.0, f["start"] - filler_pad), f["end"] + filler_pad))
    if drop_dupes:
        for d in rep["duplicate_takes"]:
            cuts.append((d["take1"][0], d["take1"][1]))
    if duration:
        cuts = [(max(0.0, s), min(duration, e)) for s, e in cuts]
    cuts = _merge(cuts)
    rep["cuts"] = cuts
    rep["removed_s"] = round(sum(e - s for s, e in cuts), 2)
    return cuts, rep


def keep_segments(duration, cuts):
    """Invert cut regions → the [start,end] segments to KEEP, in order."""
    segs, cur = [], 0.0
    for s, e in _merge(cuts):
        if s > cur + 1e-3:
            segs.append((cur, s))
        cur = max(cur, e)
    if cur < duration - 1e-3:
        segs.append((cur, duration))
    return segs


def retime_words(words, cuts):
    """Drop words inside any cut region + shift the rest onto the tightened timeline."""
    cuts = _merge(cuts)

    def removed_before(t):
        return sum(e - s for s, e in cuts if e <= t + 1e-6)

    def inside(w):
        ws, we = float(w["start"]), float(w["end"])
        mid = (ws + we) / 2.0
        return any(s - 1e-6 <= mid <= e + 1e-6 for s, e in cuts)

    out = []
    for w in words:
        if inside(w):
            continue
        shift = removed_before(float(w["start"]))
        out.append({**w, "start": round(float(w["start"]) - shift, 3),
                    "end": round(float(w["end"]) - shift, 3)})
    return out


def apply_cut(video_in, keep_segs, out_mp4, *, crf=18, preset=None):
    """ffmpeg select/aselect concat: keep only `keep_segs`, re-stamp timestamps → a tight continuous clip."""
    if not keep_segs:
        raise RuntimeError("no keep segments (everything was cut?) — aborting")
    expr = "+".join(f"between(t\\,{s:.3f}\\,{e:.3f})" for s, e in keep_segs)
    vf = f"[0:v]select='{expr}',setpts=N/FRAME_RATE/TB[v]"
    af = f"[0:a]aselect='{expr}',asetpts=N/SR/TB[a]"
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
    cmd = [nc._ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", "-i", video_in,
           "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", preset or os.environ.get("SEOSONA_X264_PRESET", "veryfast"),
           "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out_mp4]
    subprocess.run(cmd, check=True, timeout=max(600, len(keep_segs) * 30))
    return out_mp4


def autocut(video_in, words, out_mp4, *, silence_s=0.8, drop_fillers=True, drop_dupes=True):
    """Full pass: plan cuts → tighten footage → return (out_mp4, retimed_words, report). No-op-safe:
    if nothing to cut, copies the source and returns the original words."""
    dur = _probe_dur(video_in)
    cuts, rep = plan_cuts(words, silence_s=silence_s, drop_fillers=drop_fillers,
                          drop_dupes=drop_dupes, duration=dur)
    if not cuts:
        print("[autocut] nothing to cut — footage already tight")
        import shutil
        shutil.copy(video_in, out_mp4)
        return out_mp4, list(words), rep
    keep = keep_segments(dur, cuts)
    kept_s = round(sum(e - s for s, e in keep), 2)
    print(f"[autocut] {len(cuts)} cut region(s) = {rep['removed_s']}s removed "
          f"({len(rep['silences'])} silence, {len(rep['fillers'])} filler, "
          f"{len(rep['duplicate_takes'])} dup) | {dur:.1f}s → {kept_s:.1f}s")
    apply_cut(video_in, keep, out_mp4)
    new_words = retime_words(words, cuts)
    rep["duration_before"], rep["duration_after"] = round(dur, 2), kept_s
    rep["words_before"], rep["words_after"] = len(words), len(new_words)
    print(f"[autocut] retimed {len(words)} → {len(new_words)} words → {out_mp4}")
    return out_mp4, new_words, rep


def main():
    ap = argparse.ArgumentParser(description="Auto-cut talking-head footage (silence + filler + dup takes)")
    ap.add_argument("--video", required=True)
    ap.add_argument("--words", required=True, help="words.json (word-level transcript)")
    ap.add_argument("--out", required=True, help="tightened .mp4")
    ap.add_argument("--words-out", help="write the re-timed words.json here (default: <out>.words.json)")
    ap.add_argument("--silence", type=float, default=0.8, help="silence-gap threshold seconds")
    ap.add_argument("--no-fillers", action="store_true", help="do NOT cut filler words")
    ap.add_argument("--keep-dupes", action="store_true", help="do NOT cut duplicate takes")
    ap.add_argument("--report", help="write the cut report JSON here")
    a = ap.parse_args()

    words = json.load(open(a.words, encoding="utf-8"))
    video = a.video if os.path.isabs(a.video) else os.path.abspath(a.video)
    out = a.out if os.path.isabs(a.out) else os.path.abspath(a.out)
    _, new_words, rep = autocut(video, words, out, silence_s=a.silence,
                                drop_fillers=not a.no_fillers, drop_dupes=not a.keep_dupes)
    wout = a.words_out or (os.path.splitext(out)[0] + ".words.json")
    json.dump(new_words, open(wout, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[autocut] wrote re-timed words → {wout}")
    if a.report:
        json.dump(rep, open(a.report, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
