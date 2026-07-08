"""Engine #4c — Mascot PERFORM: real drawn-pose gesture animation (wave/point/present/thumbs/celebrate).

Given a set of drawn poses (same character, different gestures — see 7_ASSETS/brand/SEOSONA/mascot_poses,
produced from an AI pose sheet), this FACE-ALIGNS every pose to a common head anchor so switching between
them animates only the GESTURE (head stays put), sequences the gestures to the speech, cross-fades the
switches, lip-syncs a cartoon mouth, and adds a subtle emphasis bounce. Clean, on-model, no auto-rig
artifacts — the gestures are real artwork.

  .venv-musetalk/Scripts/python.exe scripts/mascot_perform.py --audio voice.mp3 --out act.mp4 [--energy 1.0]
"""
import argparse
import json
import math
import os
import subprocess
import tempfile
import shutil

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RHUBARB = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "rhubarb", "rhubarb.exe")
POSES_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "SEOSONA", "mascot_poses", "named")
BG = (244, 247, 255, 255)
CW, CH = 1080, 1440                                        # output canvas
ANCHOR = (CW // 2, int(CH * 0.34))                         # where every pose's face-centre is placed
FACE_H = 300                                               # every pose scaled so face height == this
_OPEN = {"A": 0.0, "X": 0.0, "B": 0.28, "G": 0.28, "F": 0.34, "E": 0.5, "H": 0.5, "C": 0.66, "D": 1.0}


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _visemes(audio, work):
    wav = os.path.join(work, "in.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", audio, "-ar", "16000", "-ac", "1", wav], check=True)
    out = os.path.join(work, "v.json")
    subprocess.run([RHUBARB, "-r", "phonetic", "-f", "json", "-o", out, wav], check=True)
    d = json.load(open(out, encoding="utf-8"))
    return d["mouthCues"], d["metadata"]["duration"]


def _open_at(cues, t):
    for c in cues:
        if c["start"] <= t < c["end"]:
            return _OPEN.get(c["value"], 0.0)
    return 0.0


def _facemesh():
    import mediapipe as mp
    return mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                           refine_landmarks=False, min_detection_confidence=0.2)


def _align_pose(path, fm):
    """Scale+translate a pose so its face centre lands on ANCHOR at FACE_H. Returns (rgba_canvas,
    mouth_xy, mouth_w, skinned_canvas) where skinned has the mouth covered for redrawing."""
    im = Image.open(path).convert("RGBA")
    W, H = im.size
    res = fm.process(np.array(im.convert("RGB")))
    if not res.multi_face_landmarks:
        return None
    lm = res.multi_face_landmarks[0].landmark
    ys = [p.y * H for p in lm]; xs = [p.x * W for p in lm]
    fcx, fcy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    fh = max(ys) - min(ys)
    px = lambda i: (lm[i].x * W, lm[i].y * H)
    lc, rc, tp, bt = px(61), px(291), px(13), px(14)
    mcx0, mcy0 = (lc[0] + rc[0]) / 2, (tp[1] + bt[1]) / 2
    mouth_w0 = ((rc[0] - lc[0]) ** 2 + (rc[1] - lc[1]) ** 2) ** 0.5
    sc = FACE_H / fh
    nw, nh = int(W * sc), int(H * sc)
    im2 = im.resize((nw, nh), Image.LANCZOS)
    # position so (fcx,fcy)*sc maps to ANCHOR
    ox = int(ANCHOR[0] - fcx * sc); oy = int(ANCHOR[1] - fcy * sc)
    canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    canvas.alpha_composite(im2, (ox, oy))
    mcx, mcy = mcx0 * sc + ox, mcy0 * sc + oy
    mouth_w = mouth_w0 * sc

    def ebox(ids):
        exs = [lm[i].x * W for i in ids]; eys = [lm[i].y * H for i in ids]
        return (min(exs) * sc + ox, min(eys) * sc + oy, max(exs) * sc + ox, max(eys) * sc + oy)
    reye = ebox([33, 133, 159, 145, 158, 153, 160, 144, 161, 163])   # character's right eye
    leye = ebox([362, 263, 386, 374, 385, 380, 387, 373, 388, 390])  # character's left eye
    esx = int((reye[0] + reye[2]) / 2); esy = int(reye[1] - (reye[3] - reye[1]) * 0.9)
    eyeskin = canvas.getpixel((max(0, min(CW - 1, esx)), max(0, min(CH - 1, esy))))

    # No skin patch. Draw the viseme mouth over the pose's own lips; nudge up to the lip line.
    return {"full": canvas, "skinned": canvas, "mouth": (mcx, mcy - mouth_w * 0.10),
            "mw": mouth_w, "eyes": [reye, leye], "eyeskin": eyeskin}


def _draw_mouth(dr, cx, cy, mw, op):
    """Talking mouth MATCHED to the mascot's own minimal-lip style (sampled from the art): muted tan-pink
    lips, dark red-brown mouth line, NO white teeth. Only drawn when open; closed shows the pose's own lips."""
    if op <= 0.14:
        return
    cx, cy = int(cx), int(cy)
    rim = (150, 85, 63)          # mascot mouth-line colour
    interior = (122, 66, 56)     # soft dark red-brown (not black, no teeth)
    lowerlip = (206, 138, 115)   # mascot lip colour
    hw = int(mw * (0.28 + 0.08 * op)); hh = max(2, int(mw * (0.08 + 0.18 * op)))
    box = [cx - hw, cy - hh, cx + hw, cy + hh]
    dr.ellipse(box, fill=interior)
    # subtle lighter lower-lip curve (matches the mascot's lighter lower lip); a faint tongue tint
    dr.chord([cx - hw, cy + int(hh * 0.15), cx + hw, cy + hh + int(hh * 0.6)], 12, 168, fill=lowerlip)
    dr.ellipse(box, outline=rim, width=max(2, int(mw * 0.07)))


def _blink_amount(t):
    """Quick natural blink ~every 3.1s (triangular pulse, ~0.14s)."""
    ph = t % 3.1
    bt = 0.14
    if ph < bt:
        x = ph / bt
        return max(0.0, 1.0 - abs(2 * x - 1))
    return 0.0


def _draw_blink(dr, eyes, skin, amt):
    """Close the eyelids by `amt` (0 open .. 1 shut): skin lid slides down over the eye + a lash line."""
    if amt <= 0.05:
        return
    for (x0, y0, x1, y1) in eyes:
        eh = y1 - y0
        lidb = y0 + eh * (0.12 + 0.9 * amt)
        dr.ellipse([x0 - 3, y0 - eh * 0.25, x1 + 3, lidb], fill=skin)     # skin upper-lid
        dr.line([x0, lidb, x1, lidb], fill=(70, 45, 38), width=max(2, int((x1 - x0) * 0.07)))  # lash line


def _director(cues, dur):
    """Return a list of (time, pose_name) — greeting wave, gesture on emphasis beats, celebrate to close."""
    # emphasis beats = local maxima of a smoothed openness (phrase starts)
    fps0 = 50
    n = int(dur * fps0)
    raw = [_open_at(cues, i / fps0) for i in range(n)]
    k = 6
    sm = [sum(raw[max(0, i - k):i + k + 1]) / len(raw[max(0, i - k):i + k + 1]) for i in range(n)]
    beats = []
    last = -1
    for i in range(2, n - 2):
        # hold each gesture ~1.7s (like a real presenter) so switches read as deliberate, not jittery
        if sm[i] > 0.30 and sm[i] >= sm[i - 1] and sm[i] > sm[i + 1] and (i / fps0 - last) > 1.7:
            beats.append(i / fps0); last = i / fps0
    # richer acting rotation over the NAMED library (talk / point / thumbs / count / thinking / present)
    gestures = ["talk_explain", "point_right", "thumbs_up", "count_2", "hand_chest",
                "point_left", "talk_explain", "thumbs_double", "count_3", "shrug"]
    tl = [(0.0, "wave")]                                   # greet
    gi = 0
    for b in beats:
        if b < 1.2 or b > dur - 1.2:
            continue
        tl.append((b, gestures[gi % len(gestures)])); gi += 1
    if dur > 1.5:
        tl.append((max(dur - 1.0, tl[-1][0] + 0.4), "celebrate"))
    tl.sort()
    return tl


def make(audio, out_mp4, fps=25, energy=1.0):
    work = tempfile.mkdtemp(prefix="perform_")
    fdir = os.path.join(work, "f"); os.makedirs(fdir, exist_ok=True)
    try:
        cues, dur = _visemes(os.path.abspath(audio), work)
        fm = _facemesh()
        need = ["idle", "wave", "talk_explain", "point_right", "point_left", "thumbs_up",
                "thumbs_double", "ok_sign", "count_2", "count_3", "hand_chest", "shrug",
                "arms_wide", "thinking", "celebrate"]
        poses = {}
        for nm in need:
            p = os.path.join(POSES_DIR, f"{nm}.png")
            if os.path.exists(p):
                a = _align_pose(p, fm)
                if a:
                    poses[nm] = a
        if "idle" not in poses:
            raise RuntimeError("need at least the idle pose")
        tl = _director(cues, dur)
        tl = [(t, nm) for (t, nm) in tl if nm in poses] or [(0.0, "idle")]

        XF = 0.05                                          # near-cut transition (snappy, no dissolve ghost)
        nframes = int(dur * fps)
        raw = [_open_at(cues, i / fps) for i in range(nframes)]
        kk = 4
        sm = [sum(raw[max(0, i - kk):i + kk + 1]) / len(raw[max(0, i - kk):i + kk + 1]) for i in range(nframes)]

        def cur_pose(t):
            idx = 0
            for j, (tt, nm) in enumerate(tl):
                if tt <= t:
                    idx = j
            return idx

        for i in range(nframes):
            t = i / fps
            op = raw[i]; em = sm[i]
            j = cur_pose(t)
            name = tl[j][1]
            prev = tl[j - 1][1] if j > 0 else name
            since = t - tl[j][0]
            blend = min(1.0, since / XF) if since < XF and prev != name else 1.0

            # BODY LOCKED IN PLACE — no zoom, no bob. Only the gesture (pose), mouth and eyes animate.
            blink = _blink_amount(t)

            def render(pname):
                P = poses[pname]
                body = P["skinned"].copy()
                d = ImageDraw.Draw(body)
                _draw_mouth(d, P["mouth"][0], P["mouth"][1], P["mw"], op)
                _draw_blink(d, P["eyes"], P["eyeskin"], blink)
                return body

            frame = render(name)
            if blend < 1.0 and prev in poses:
                frame = Image.blend(render(prev), frame, blend)

            out = Image.new("RGBA", (CW, CH), BG)
            out.alpha_composite(frame)
            out.convert("RGB").save(os.path.join(fdir, f"f_{i:05d}.jpg"), quality=90)

        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                        "-framerate", str(fps), "-i", os.path.join(fdir, "f_%05d.jpg"),
                        "-i", os.path.abspath(audio), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", os.path.abspath(out_mp4)], check=True)
        print(f"[mascot_perform] OK {out_mp4}  ({nframes}f {dur}s) poses={list(poses)} beats={len(tl)}")
        return out_mp4
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Mascot PERFORM — real drawn-pose gestures + lip-sync")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--energy", type=float, default=1.0)
    a = ap.parse_args()
    make(a.audio, a.out, fps=a.fps, energy=a.energy)


if __name__ == "__main__":
    raise SystemExit(main())
