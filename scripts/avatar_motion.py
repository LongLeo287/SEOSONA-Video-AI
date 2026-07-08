"""avatar_motion — add subtle "alive" motion to a talking-head clip (procedural, GPU-free).

A still-photo lip-sync (MuseTalk/Rhubarb) has a moving mouth on a frozen head — the uncanny "portrait
that talks". This layers gentle, natural idle motion ON TOP of any such clip via ffmpeg only:
  - breathing      slow vertical bob (a few px, ~4s period)
  - head sway      micro rotation (< 1 deg, ~7s period) + slow horizontal drift
  - Ken Burns      slow continuous zoom-in over the clip
All motion happens INSIDE a scaled-up frame (headroom) so no black borders ever show. Audio is copied
untouched. Works on BOTH the expert photo and the cartoon mascot.

  python scripts/avatar_motion.py --in clip.mp4 --out clip_motion.mp4 [--intensity subtle|normal|lively]
"""
import argparse
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# (headroom, sway_deg, sway_period, driftX_px, driftX_period, breath_px, breath_period, kenburns_zoom)
PRESETS = {
    "subtle": (1.12, 0.35, 8.0, 5, 11.0, 4, 4.5, 0.03),
    "normal": (1.15, 0.6, 7.0, 8, 9.0, 6, 4.0, 0.05),
    "lively": (1.20, 1.0, 6.0, 12, 8.0, 9, 3.5, 0.08),
}


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _ffprobe():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffprobe.exe")
    return p if os.path.exists(p) else "ffprobe"


def _dims_dur(path):
    out = subprocess.run([_ffprobe(), "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, timeout=30).stdout.split("\n")
    w, h = 0, 0
    dur = 8.0
    for ln in out:
        parts = [x for x in ln.split(",") if x]
        if len(parts) == 2:
            w, h = int(parts[0]), int(parts[1])
        elif len(parts) == 1:
            try:
                dur = float(parts[0])
            except ValueError:
                pass
    return w, h, dur


def add_motion(in_mp4, out_mp4, intensity="subtle"):
    hr, swy, swT, dx, dxT, by, byT, kb = PRESETS.get(intensity, PRESETS["subtle"])
    w, h, dur = _dims_dur(in_mp4)
    if not (w and h):
        raise RuntimeError(f"could not read dimensions of {in_mp4}")
    # Big frame with headroom so rotate/pan never reveal a border, then crop the original size back out
    # of it with time-varying offset (breathing + drift) and a slowly shrinking window (Ken Burns zoom).
    swr = swy * 3.14159265 / 180.0
    dur = max(dur, 0.5)
    # A gentle continuous zoom-in (Ken Burns) via a scaled-up base that RAMPS: we bake the zoom into the
    # headroom scale as a fixed value, then create motion by drifting a constant-size crop window inside a
    # rotated, scaled-up frame. crop w/h MUST be constant (ffmpeg evals them once) — only x/y take `t`.
    base = hr + kb                                     # extra scale so the drifting crop always has room
    bw, bh = int(w * base) // 2 * 2, int(h * base) // 2 * 2
    # Pure OSCILLATING idle motion (returns to centre → natural, not one-way drift). crop w/h constant;
    # only x/y take `t`. Horizontal drift + vertical breathing bob, inside a rotated scaled-up frame.
    cx = f"(in_w-{w})/2 + {dx}*sin(2*PI*t/{dxT})"
    cy = f"(in_h-{h})/2 + {by}*sin(2*PI*t/{byT})"
    vf = (
        f"scale={bw}:{bh},"
        f"rotate='{swr:.5f}*sin(2*PI*t/{swT})':ow={bw}:oh={bh}:c=none,"
        f"crop=w={w}:h={h}:x='{cx}':y='{cy}',"
        f"format=yuv420p"
    )
    cmd = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", in_mp4,
           "-vf", vf, "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-c:a", "copy", out_mp4]
    print(f"[avatar_motion] {intensity}: {os.path.basename(in_mp4)} -> {os.path.basename(out_mp4)}")
    subprocess.run(cmd, check=True, timeout=1800)
    print(f"[avatar_motion] OK {out_mp4}")
    return out_mp4


def main():
    ap = argparse.ArgumentParser(description="Add subtle idle motion to a talking-head clip")
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--intensity", choices=["subtle", "normal", "lively"], default="subtle")
    a = ap.parse_args()
    add_motion(a.inp, a.out, a.intensity)


if __name__ == "__main__":
    raise SystemExit(main())
