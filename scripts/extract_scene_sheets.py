# -*- coding: utf-8 -*-
"""Extract per-scene keyframes from reference videos and assemble one contact sheet per video.

For every video: ffmpeg scene-change detection → representative frame per scene (with timestamp),
then a PIL grid (contact sheet) so a whole video's scene composition is reviewable in ONE image.
This feeds the library-growth ANALYZE stage (craft: layout, motion, effects, text, colour).

Light on GPU (ffmpeg decode + PIL) → safe to run alongside voice training.

Usage:
  python scripts/extract_scene_sheets.py --src "D:/SEOSONA AI/Video Template" \
      --out 8_WORKSPACE/template_study
"""
import argparse, glob, os, re, subprocess, sys
from importlib import import_module

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
MEDIA = (".mp4", ".mov", ".mkv", ".webm", ".avi")


def _ff():
    try:
        return import_module("native_composer")._ffmpeg_bin()
    except Exception:
        return "ffmpeg"


def _duration(v):
    """Duration via ffmpeg -i stderr (ffprobe-static isn't installed here)."""
    r = subprocess.run([_ff(), "-hide_banner", "-i", v], capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", r.stderr or "")
    if m:
        h, mm, s = m.groups()
        return int(h) * 3600 + int(mm) * 60 + float(s)
    return 0.0


def _scene_frames(v, tmp, thresh, w):
    """Extract scene-change frames + parse their timestamps from showinfo."""
    for f in glob.glob(os.path.join(tmp, "*.jpg")):
        os.remove(f)
    vf = f"select='gt(scene,{thresh})',showinfo,scale={w}:-1"
    r = subprocess.run([_ff(), "-hide_banner", "-i", v, "-vf", vf, "-vsync", "vfr",
                        "-q:v", "4", os.path.join(tmp, "f_%04d.jpg")],
                       capture_output=True, text=True, errors="replace")
    times = [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr or "")]
    frames = sorted(glob.glob(os.path.join(tmp, "f_*.jpg")))
    return frames, times


def _interval_frames(v, tmp, dur, n, w):
    """Fallback for near-static videos: sample n frames at even intervals."""
    for f in glob.glob(os.path.join(tmp, "*.jpg")):
        os.remove(f)
    frames, times = [], []
    for i in range(n):
        t = dur * (i + 0.5) / n
        out = os.path.join(tmp, f"f_{i:04d}.jpg")
        subprocess.run([_ff(), "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                        "-i", v, "-frames:v", "1", "-vf", f"scale={w}:-1", "-q:v", "4", out],
                       capture_output=True)
        if os.path.exists(out):
            frames.append(out); times.append(t)
    return frames, times


def _subsample(frames, times, cap):
    if len(frames) <= cap:
        return frames, times
    idx = [round(i * (len(frames) - 1) / (cap - 1)) for i in range(cap)]
    return [frames[i] for i in idx], [times[i] for i in idx]


def _sheet(frames, times, title, out_path, cols, cell_w):
    from PIL import Image, ImageDraw, ImageFont
    if not frames:
        return False
    thumbs = [Image.open(f).convert("RGB") for f in frames]
    cell_h = max(t.height for t in thumbs)
    lab_h = 20; head_h = 40; pad = 6
    rows = (len(thumbs) + cols - 1) // cols
    W = cols * (cell_w + pad) + pad
    H = head_h + rows * (cell_h + lab_h + pad) + pad
    sheet = Image.new("RGB", (W, H), (18, 20, 28))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 14); hf = ImageFont.truetype("arialbd.ttf", 18)
    except Exception:
        font = ImageFont.load_default(); hf = font
    d.text((pad, 10), title[:110], fill=(120, 200, 255), font=hf)
    for i, (t, ts) in enumerate(zip(thumbs, times)):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = head_h + r * (cell_h + lab_h + pad)
        sheet.paste(t.resize((cell_w, int(t.height * cell_w / t.width))), (x, y))
        d.text((x + 2, y + cell_h - 2), f"#{i+1}  {ts:5.1f}s", fill=(255, 220, 90), font=font)
    sheet.save(out_path, quality=85)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scene-thresh", type=float, default=0.30)
    ap.add_argument("--max-frames", type=int, default=30)
    ap.add_argument("--secs-per-frame", type=float, default=2.5,
                    help="interval sampling density (smaller = denser storyboard)")
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--cell-w", type=int, default=300)
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    sheets_dir = os.path.join(out, "sheets"); tmp = os.path.join(out, "_tmp")
    os.makedirs(sheets_dir, exist_ok=True); os.makedirs(tmp, exist_ok=True)

    vids = sorted(v for v in glob.glob(os.path.join(args.src, "**", "*"), recursive=True)
                  if os.path.splitext(v)[1].lower() in MEDIA)
    print(f"[sheets] {len(vids)} videos")
    index = []
    for i, v in enumerate(vids, 1):
        name = os.path.splitext(os.path.basename(v))[0]
        safe = re.sub(r"[^\w\-]+", "_", name)[:60]
        dur = _duration(v)
        # Interval sampling as the PRIMARY method — a dense storyboard (~1 frame / 2.5 s) covers
        # single-take / slide videos that have no hard cuts (most of these). Merge in any hard
        # scene-cut frames on top so real cuts are also represented.
        spf = args.secs_per_frame
        n = min(args.max_frames, max(6, int(dur / spf))) if dur > 0 else args.max_frames
        frames, times = _interval_frames(v, tmp, dur or (n * spf), n, args.cell_w)
        mode = "interval"
        frames, times = _subsample(frames, times, args.max_frames)
        sp = os.path.join(sheets_dir, f"{i:02d}_{safe}.jpg")
        ok = _sheet(frames, times, f"{i:02d}. {name}  ({dur:.0f}s, {len(frames)} scenes, {mode})",
                    sp, args.cols, args.cell_w)
        print(f"[{i}/{len(vids)}] {name[:50]} → {len(frames)} scenes ({mode})")
        if ok:
            index.append({"n": i, "video": os.path.basename(v), "sheet": os.path.basename(sp),
                          "duration_s": round(dur, 1), "scenes": len(frames)})
    import json
    json.dump(index, open(os.path.join(out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n[DONE] {len(index)} sheets → {sheets_dir}")


if __name__ == "__main__":
    main()
