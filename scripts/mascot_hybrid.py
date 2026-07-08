"""Engine #4d — Mascot HYBRID: LivePortrait smooth HEAD motion + pose-swap gesture BODY + synced mouth.

Best mascot without Live2D/artist: the head TILTS/NODS smoothly (LivePortrait, region="pose" so it never
fights our lip-sync), the arms perform real drawn GESTURES (named pose library), a cartoon mouth lip-syncs
(matched to the mascot's own lips) and the eyes blink. Fully automatic from just an audio file.

Chain:  audio → LivePortrait(named/idle.png, head-motion template, region=pose) = smooth head
        → per frame: gesture-pose body + keyed+cut LP head + synced cartoon mouth + blink.

  .venv-musetalk/Scripts/python.exe scripts/mascot_hybrid.py --audio v.mp3 --out out.mp4 \
        [--head-motion 0.8] [--hold 1.7] [--head-clip pre.mp4]
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import shutil

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
import mediapipe as mp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
RHUBARB = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "rhubarb", "rhubarb.exe")
POSES_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "SEOSONA", "mascot_poses", "named")
DRIVE_TEMPLATE = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "LivePortrait",
                              "assets", "examples", "driving", "d0.mp4")
BG = (244, 247, 255, 255)
CW, CH = 1080, 1440
ANCHOR = (CW // 2, int(CH * 0.34)); FACE_H = 300
_OPEN = {"A": 0.0, "X": 0.0, "B": 0.28, "G": 0.28, "F": 0.34, "E": 0.5, "H": 0.5, "C": 0.66, "D": 1.0}
_FM = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=False,
                                      min_detection_confidence=0.2)


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _visemes(audio, work):
    wav = os.path.join(work, "in.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", audio,
                    "-ar", "16000", "-ac", "1", wav], check=True)
    out = os.path.join(work, "v.json")
    subprocess.run([RHUBARB, "-r", "phonetic", "-f", "json", "-o", out, wav], check=True)
    d = json.load(open(out, encoding="utf-8"))
    return d["mouthCues"], d["metadata"]["duration"]


def _open_at(cues, t):
    for c in cues:
        if c["start"] <= t < c["end"]:
            return _OPEN.get(c["value"], 0.0)
    return 0.0


def _key_bg(im, eat=3):
    rgb = np.array(im.convert("RGB")).astype(int)
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mx = np.maximum(np.maximum(R, G), B); mn = np.minimum(np.minimum(R, G), B)
    isbg = (mn > 170) & ((mx - mn) < 38)
    lbl, _ = ndimage.label(isbg)
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))); border.discard(0)
    bg = ndimage.binary_dilation(np.isin(lbl, list(border)), iterations=eat)
    return Image.fromarray(np.dstack([np.array(im.convert("RGB")), np.where(bg, 0, 255).astype(np.uint8)]), "RGBA")


def _align(im):
    """Scale+translate so the face maps to ANCHOR at FACE_H. Returns (canvas, (mcx,mcy), mw) or None."""
    im = im.convert("RGBA"); W, H = im.size
    r = _FM.process(np.array(im.convert("RGB")))
    if not r.multi_face_landmarks:
        return None
    lm = r.multi_face_landmarks[0].landmark
    ys = [p.y * H for p in lm]; xs = [p.x * W for p in lm]
    fcx, fcy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2; fh = max(ys) - min(ys)
    px = lambda i: (lm[i].x * W, lm[i].y * H)
    lc, rc, tp, bt = px(61), px(291), px(13), px(14)
    mcx0, mcy0 = (lc[0] + rc[0]) / 2, (tp[1] + bt[1]) / 2
    mw0 = ((rc[0] - lc[0]) ** 2 + (rc[1] - lc[1]) ** 2) ** 0.5
    sc = FACE_H / fh
    im2 = im.resize((int(W * sc), int(H * sc)), Image.LANCZOS)
    ox, oy = int(ANCHOR[0] - fcx * sc), int(ANCHOR[1] - fcy * sc)
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); c.alpha_composite(im2, (ox, oy))

    def ebox(ids):
        exs = [lm[i].x * W for i in ids]; eys = [lm[i].y * H for i in ids]
        return (min(exs) * sc + ox, min(eys) * sc + oy, max(exs) * sc + ox, max(eys) * sc + oy)
    eyes = [ebox([33, 133, 159, 145, 158, 153, 160, 144]), ebox([362, 263, 386, 374, 385, 380, 387, 373])]
    ex = int((eyes[0][0] + eyes[0][2]) / 2); ey = int(eyes[0][1] - (eyes[0][3] - eyes[0][1]) * 0.9)
    eyeskin = c.getpixel((max(0, min(CW - 1, ex)), max(0, min(CH - 1, ey))))
    return c, (mcx0 * sc + ox, mcy0 * sc + oy - mw0 * sc * 0.10), mw0 * sc, eyes, eyeskin


_YY, _XX = np.mgrid[0:CH, 0:CW]


def _erase_head(canvas):
    """Remove the pose's OWN head+hair (an ellipse around the anchor) so only the LivePortrait head shows —
    otherwise the two heads overlap (double outline). Keeps neck/shoulders/arms (outside the ellipse)."""
    cx, cy = ANCHOR[0], ANCHOR[1] - FACE_H * 0.05
    rx, ry = FACE_H * 0.76, FACE_H * 0.90
    d = ((_XX - cx) / rx) ** 2 + ((_YY - cy) / ry) ** 2
    m = np.clip(1.4 - d, 0.0, 1.0)                       # 1 inside, soft ramp to 0 at the ellipse edge
    a = np.array(canvas)
    a[:, :, 3] = (a[:, :, 3] * (1.0 - m)).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def _draw_mouth(dr, cx, cy, mw, op):
    """Mascot-matched talking mouth (muted lips, no white teeth); only when open."""
    if op <= 0.14:
        return
    cx, cy = int(cx), int(cy)
    rim = (150, 85, 63); interior = (122, 66, 56); lowerlip = (206, 138, 115)
    hw = int(mw * (0.28 + 0.08 * op)); hh = max(2, int(mw * (0.08 + 0.18 * op)))
    box = [cx - hw, cy - hh, cx + hw, cy + hh]
    dr.ellipse(box, fill=interior)
    dr.chord([cx - hw, cy + int(hh * 0.15), cx + hw, cy + hh + int(hh * 0.6)], 12, 168, fill=lowerlip)
    dr.ellipse(box, outline=rim, width=max(2, int(mw * 0.07)))


def _blink_amount(t):
    ph = t % 3.1
    if ph < 0.14:
        return max(0.0, 1.0 - abs(2 * (ph / 0.14) - 1))
    return 0.0


def _draw_blink(dr, eyes, skin, amt):
    if amt <= 0.05:
        return
    for (x0, y0, x1, y1) in eyes:
        eh = y1 - y0; lidb = y0 + eh * (0.12 + 0.9 * amt)
        dr.ellipse([x0 - 3, y0 - eh * 0.25, x1 + 3, lidb], fill=skin)
        dr.line([x0, lidb, x1, lidb], fill=(70, 45, 38), width=max(2, int((x1 - x0) * 0.07)))


def _director(cues, dur, hold):
    fps0 = 50; n = int(dur * fps0)
    raw = [_open_at(cues, i / fps0) for i in range(n)]; k = 6
    sm = [sum(raw[max(0, i - k):i + k + 1]) / len(raw[max(0, i - k):i + k + 1]) for i in range(n)]
    beats, last = [], -1
    for i in range(2, n - 2):
        if sm[i] > 0.30 and sm[i] >= sm[i - 1] and sm[i] > sm[i + 1] and (i / fps0 - last) > hold:
            beats.append(i / fps0); last = i / fps0
    g = ["talk_explain", "point_right", "thumbs_up", "count_2", "hand_chest",
         "point_left", "talk_explain", "thumbs_double", "count_3", "shrug"]
    tl = [(0.0, "wave")]; gi = 0
    for b in beats:
        if 1.2 < b < dur - 1.2:
            tl.append((b, g[gi % len(g)])); gi += 1
    if dur > 1.5:
        tl.append((max(dur - 1.0, tl[-1][0] + 0.4), "celebrate"))
    tl.sort(); return tl


def _make_head_clip(dur, head_motion, work):
    """Auto-generate the smooth head clip: LivePortrait(idle, d0, region=pose) looped to dur."""
    import liveportrait_motion as lp
    out = os.path.join(work, "head.mp4")
    lp.animate(os.path.join(POSES_DIR, "idle.png"), out, driving=DRIVE_TEMPLATE,
               amount=head_motion, loop_to=dur + 0.2, region="pose")
    return out


def make(audio, out_mp4, head_clip=None, head_motion=0.8, hold=1.7, fps=25):
    work = tempfile.mkdtemp(prefix="hybrid_")
    fdir = os.path.join(work, "f"); os.makedirs(fdir, exist_ok=True)
    try:
        cues, dur = _visemes(os.path.abspath(audio), work)
        if not head_clip:
            print("[mascot_hybrid] generating LivePortrait head clip (region=pose)...")
            head_clip = _make_head_clip(dur, head_motion, work)

        cap = cv2.VideoCapture(head_clip); heads = []
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            heads.append(_align(_key_bg(Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))))
        cap.release()
        heads = [h for h in heads if h is not None]
        if not heads:
            raise RuntimeError("no usable LivePortrait head frames")

        need = ["idle", "wave", "talk_explain", "point_right", "point_left", "thumbs_up", "thumbs_double",
                "count_2", "count_3", "hand_chest", "shrug", "celebrate"]
        poses = {}
        for nm in need:
            p = os.path.join(POSES_DIR, f"{nm}.png")
            if os.path.exists(p):
                a = _align(Image.open(p))
                if a:
                    poses[nm] = _erase_head(a[0])     # headless body (LP head replaces it → no double head)
        # "idle" is the fallback body every frame (poses.get(name, poses["idle"]) below evaluates poses["idle"]
        # unconditionally) — without it the render KeyError-crashes cryptically. Fail with a clear message,
        # matching the sibling mascot_perform's guard.
        if "idle" not in poses:
            raise RuntimeError("need at least the idle pose (POSES_DIR/idle.png)")
        tl = [(t, nm) for (t, nm) in _director(cues, dur, hold) if nm in poses] or [(0.0, "idle")]

        neck_y = int(ANCHOR[1] + FACE_H * 0.86)          # cover the erased pose-head region fully
        hmask = Image.new("L", (CW, CH), 0)
        ImageDraw.Draw(hmask).rectangle([0, 0, CW, neck_y], fill=255)
        hmask = hmask.filter(ImageFilter.GaussianBlur(18))
        empty = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))

        nframes = int(dur * fps); XF = 0.05
        for i in range(nframes):
            t = i / fps; op = _open_at(cues, t)
            j = max([k for k in range(len(tl)) if tl[k][0] <= t] or [0])
            name = tl[j][1]; prev = tl[j - 1][1] if j > 0 else name
            since = t - tl[j][0]
            blend = min(1.0, since / XF) if since < XF and prev != name else 1.0
            body = poses.get(name, poses["idle"])
            if blend < 1.0 and prev in poses:
                body = Image.blend(poses[prev], body, blend)

            hd, (mcx, mcy), mw, eyes, eyeskin = heads[i % len(heads)]
            headcut = Image.composite(hd, empty, hmask)

            canvas = Image.new("RGBA", (CW, CH), BG)
            canvas.alpha_composite(body)        # gesture body
            canvas.alpha_composite(headcut)     # smooth LivePortrait head (pose motion only)
            dr = ImageDraw.Draw(canvas)
            _draw_mouth(dr, mcx, mcy, mw, op)                       # synced cartoon mouth
            _draw_blink(dr, eyes, eyeskin, _blink_amount(t))       # eye blink
            canvas.convert("RGB").save(os.path.join(fdir, f"f_{i:05d}.jpg"), quality=90)

        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(fps),
                        "-i", os.path.join(fdir, "f_%05d.jpg"), "-i", os.path.abspath(audio),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", os.path.abspath(out_mp4)], check=True)
        print(f"[mascot_hybrid] OK {out_mp4} ({nframes}f {dur}s, {len(heads)} head frames)")
        return out_mp4
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Mascot HYBRID: LivePortrait head + pose gestures + synced mouth (auto)")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--head-clip", default=None, help="optional pre-made LivePortrait head clip; else auto-generated")
    ap.add_argument("--head-motion", type=float, default=0.8, help="head tilt/nod intensity 0.3..1.2")
    ap.add_argument("--hold", type=float, default=1.7, help="seconds to hold each gesture (bigger = calmer)")
    ap.add_argument("--fps", type=int, default=25)
    a = ap.parse_args()
    make(a.audio, a.out, head_clip=a.head_clip, head_motion=a.head_motion, hold=a.hold, fps=a.fps)


if __name__ == "__main__":
    raise SystemExit(main())
