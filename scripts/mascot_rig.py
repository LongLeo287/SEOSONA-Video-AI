"""Engine #4b — Mascot RIG: a 2D brand mascot that ACTS (hoat dong), in its own art style.

The flat mascot PNG is separated into layers and each frame the character performs — clear arm gestures
(wave, thumbs-pump, point), whole-body bounce/lean on speech emphasis, and a cartoon viseme mouth that
lip-syncs. The TEXT logo is a static layer (only the character moves). No photoreal pixels (never MuseTalk).

Clean layer separation without hole/ghost/shoulder-fade:
  - HANDS are cut by SKIN COLOUR in the left/right side regions (the tan thumbs-up), so moving them never
    touches the dark polo shoulders; the cut area sits over the transparent background -> clean.
  - The mouth is drawn onto the body BEFORE the per-frame transform, so it stays locked to the face.
  - Head "nod" comes from whole-body tilt/bob (no neck hole).

  .venv-musetalk/Scripts/python.exe scripts/mascot_rig.py --audio voice.mp3 --out act.mp4 [--image m.png] [--energy 1.2]
"""
import argparse
import json
import math
import os
import subprocess
import tempfile
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RHUBARB = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "rhubarb", "rhubarb.exe")
DEFAULT_MASCOT = os.path.join(ROOT, "7_ASSETS", "brand", "SEOSONA", "Mascot Logo Small_Transparent 03.png")
BG = (244, 247, 255, 255)
_OPEN = {"A": 0.0, "X": 0.0, "B": 0.28, "G": 0.28, "F": 0.34, "E": 0.5, "H": 0.5, "C": 0.66, "D": 1.0}


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _visemes(audio, work):
    wav = os.path.join(work, "in.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", audio, "-ar", "16000", "-ac", "1", wav], check=True)
    out = os.path.join(work, "visemes.json")
    subprocess.run([RHUBARB, "-r", "phonetic", "-f", "json", "-o", out, wav], check=True)
    d = json.load(open(out, encoding="utf-8"))
    return d["mouthCues"], d["metadata"]["duration"]


def _open_at(cues, t):
    for c in cues:
        if c["start"] <= t < c["end"]:
            return _OPEN.get(c["value"], 0.0)
    return 0.0


def _face(base):
    """Return (mouth_cx, mouth_cy, mouth_w, face_cx, face_cy, face_h) via MediaPipe, or None."""
    try:
        import mediapipe as mp
        # guard the WHOLE body (not just the import): MediaPipe process()/landmark access can raise on odd
        # inputs, and the contract is "None on failure" so the caller falls back to a default rig.
        W, H = base.size
        fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                             refine_landmarks=False, min_detection_confidence=0.3)
        res = fm.process(np.array(base.convert("RGB")))
        if not res.multi_face_landmarks:
            return None
        lm = res.multi_face_landmarks[0].landmark
        px = lambda i: (lm[i].x * W, lm[i].y * H)
        lc, rc, top, bot = px(61), px(291), px(13), px(14)
        allx = [p.x * W for p in lm]; ally = [p.y * H for p in lm]
        mcx = (lc[0] + rc[0]) / 2; mcy = (top[1] + bot[1]) / 2
        mouth_w = ((rc[0] - lc[0]) ** 2 + (rc[1] - lc[1]) ** 2) ** 0.5
        return mcx, mcy, max(8.0, mouth_w), (min(allx) + max(allx)) / 2, (min(ally) + max(ally)) / 2, max(ally) - min(ally)
    except Exception:
        return None


def _skin_hand_mask(im, side, face_box):
    """Mask of the tan thumbs-up hand on one side (excludes the dark polo + the face)."""
    W, H = im.size
    arr = np.array(im.convert("RGB")).astype(np.int16)
    alp = np.array(im.split()[3])
    R, G, Gr, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 1], arr[:, :, 2]
    skin = (R > 150) & (G > 90) & (G < 200) & (B > 60) & (B < 170) & (R >= G) & (G >= B - 10) & (alp > 40)
    fx0, fy0, fx1, fy1 = face_box
    ys, xs = np.mgrid[0:H, 0:W]
    inface = (xs > fx0) & (xs < fx1) & (ys > fy0) & (ys < fy1)
    band = (ys > 0.24 * H) & (ys < 0.60 * H)               # hand vertical band
    sidem = (xs > 0.55 * W) if side == "r" else (xs < 0.45 * W)
    m = (skin & band & sidem & ~inface).astype(np.uint8) * 255
    return Image.fromarray(m).filter(ImageFilter.GaussianBlur(6))


def _cut(im, mask):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    lay.paste(im, (0, 0), Image.composite(im.split()[3], Image.new("L", im.size, 0), mask))
    return lay


def _erase(im, mask):
    a = np.array(im).copy()
    e = np.array(mask).astype(np.float32) / 255.0
    a[:, :, 3] = (a[:, :, 3] * (1.0 - e)).astype(np.uint8)
    return Image.fromarray(a)


def _draw_mouth(dr, cx, cy, mouth_w, op):
    """A natural cartoon talking mouth in the mascot's palette: wider-than-tall, soft dark-red interior,
    thin upper-teeth arc, a hint of lower lip. No big black hole, no hard white block."""
    cx, cy = int(cx), int(cy)
    lip = (146, 74, 62)                                      # mascot lip line colour
    lw = max(2, int(mouth_w * 0.045))
    if op <= 0.06:                                          # closed → gentle smile
        w = int(mouth_w * 0.44)
        dr.arc([cx - w, cy - int(mouth_w * 0.20), cx + w, cy + int(mouth_w * 0.34)], 12, 168, fill=lip, width=lw)
        return
    hw = int(mouth_w * (0.34 + 0.10 * op))                  # talking mouth is WIDER than tall
    hh = max(2, int(mouth_w * (0.10 + 0.20 * op)))
    box = [cx - hw, cy - hh, cx + hw, cy + hh]
    dr.ellipse(box, fill=(120, 62, 58))                     # soft dark-red interior (not black)
    # upper teeth: a thin white band following the top curve
    dr.chord([cx - hw + lw, cy - hh + lw, cx + hw - lw, cy + int(hh * 0.5)], 185, 355, fill=(250, 248, 244))
    # lower-lip hint
    dr.chord([cx - hw, cy + int(hh * 0.35), cx + hw, cy + hh + int(hh * 0.4)], 20, 160, fill=(168, 96, 84))
    dr.ellipse(box, outline=lip, width=lw)                  # lip outline last


def make(audio, out_mp4, image=None, fps=25, energy=1.2):
    image = image or DEFAULT_MASCOT
    work = tempfile.mkdtemp(prefix="mascotrig_")
    fdir = os.path.join(work, "f"); os.makedirs(fdir, exist_ok=True)
    try:
        cues, dur = _visemes(os.path.abspath(audio), work)
        im = Image.open(image).convert("RGBA")
        W, H = im.size
        f = _face(im)
        if not f:
            raise RuntimeError("no face found in mascot")
        mcx, mcy, mouth_w, fcx, fcy, fh = f
        face_box = (fcx - fh * 0.5, fcy - fh * 0.6, fcx + fh * 0.5, fcy + fh * 0.7)

        # layers: TEXT (static, bottom), HANDS (skin, gesture), BODY (everything else, bounces)
        text_m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(text_m).rectangle([0, int(0.66 * H), W, H], fill=255)
        text_m = text_m.filter(ImageFilter.GaussianBlur(4))
        text_lay = _cut(im, text_m)
        rhand = _skin_hand_mask(im, "r", face_box)
        lhand = _skin_hand_mask(im, "l", face_box)
        # body = image minus text minus hands
        body = _erase(_erase(im, text_m), rhand)
        body = _erase(body, lhand)
        rlay, llay = _cut(im, rhand), _cut(im, lhand)
        # pivots at the wrist/base of each hand (bottom-inner of the hand band)
        rpiv = (0.60 * W, 0.55 * H); lpiv = (0.40 * W, 0.55 * H)

        def xform(layer, dy, sc, tilt, extra_deg=0.0, pivot=None):
            lay = layer
            if extra_deg:
                lay = lay.rotate(extra_deg, resample=Image.BICUBIC, center=pivot)
            if tilt:
                lay = lay.rotate(tilt, resample=Image.BICUBIC, center=(W / 2, 0.42 * H))
            if sc != 1.0:
                nw, nh = int(W * sc), int(H * sc)
                lay = lay.resize((nw, nh), Image.LANCZOS)
                c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                c.paste(lay, ((W - nw) // 2, int((H - nh) / 2 + dy)), lay); return c
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            c.paste(lay, (0, int(dy)), lay); return c

        # CLEAN whole-body performance (no hand cutting → no artifacts). The character bounces, leans,
        # squashes & anticipates on speech emphasis, reading as an energetic performer in its own art.
        body_full = _erase(im, text_m)                                    # everything except the text
        nframes = int(dur * fps)
        raw = [_open_at(cues, i / fps) for i in range(nframes)]
        # smoothed emphasis envelope for the BODY (natural, not per-syllable jitter); mouth uses raw
        k = 4
        smooth = [sum(raw[max(0, i - k):min(nframes, i + k + 1)]) / len(raw[max(0, i - k):min(nframes, i + k + 1)])
                  for i in range(nframes)]
        for i in range(nframes):
            t = i / fps
            op = raw[i]                                                   # raw → precise lip-sync
            em = smooth[i]                                                # smoothed → body performance
            op1 = smooth[max(0, i - 2)]
            bob = (-8 * math.sin(2 * math.pi * t / 1.0) - 22 * em) * energy     # bigger bounce
            # squash & stretch: taller+narrower on a pop, wider+shorter on landing
            pop = em * energy
            sx = 1.0 + (0.010 * math.sin(2 * math.pi * t / 1.0) - 0.03 * pop)
            sy = 1.0 + (0.010 * math.sin(2 * math.pi * t / 1.0) + 0.05 * pop)
            lean = (4.5 * math.sin(2 * math.pi * t / 2.4)) * energy         # gentle continuous lean/sway

            bcopy = body_full.copy()
            _draw_mouth(ImageDraw.Draw(bcopy), mcx, mcy, mouth_w, op)
            lay = bcopy
            if lean:
                lay = lay.rotate(lean, resample=Image.BICUBIC, center=(W / 2, 0.55 * H))
            nw, nh = max(2, int(W * sx)), max(2, int(H * sy))
            lay = lay.resize((nw, nh), Image.LANCZOS)
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            c.paste(lay, ((W - nw) // 2, int((H - nh) / 2 + bob)), lay)

            canvas = Image.new("RGBA", (W, H), BG)
            canvas.alpha_composite(text_lay)                              # static text behind
            canvas.alpha_composite(c)
            canvas.convert("RGB").save(os.path.join(fdir, f"f_{i:05d}.jpg"), quality=90)

        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                        "-framerate", str(fps), "-i", os.path.join(fdir, "f_%05d.jpg"),
                        "-i", os.path.abspath(audio),
                        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", os.path.abspath(out_mp4)], check=True)
        print(f"[mascot_rig] OK {out_mp4}  ({nframes} frames, {dur}s)")
        return out_mp4
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Mascot RIG — a 2D mascot that acts (gestures + performance)")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--image", default=None)
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--energy", type=float, default=1.2)
    a = ap.parse_args()
    make(a.audio, a.out, image=a.image, fps=a.fps, energy=a.energy)


if __name__ == "__main__":
    raise SystemExit(main())
