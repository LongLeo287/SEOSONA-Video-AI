"""Engine #4 — Talking Mascot: a 2D brand mascot lip-syncs to a SEOSONA voice (no GPU).

Rhubarb Lip-Sync (MIT) turns the voice into phoneme→viseme timings; we cover the mascot's drawn
smile and paint a viseme-driven mouth per frame (Pillow), composite on the brand-light bg, then
mux the original voice. Fits the faceless brand better than a photorealistic stranger's face, and
needs no GPU — pairs with the photorealistic path (SadTalker/MuseTalk, [[portrait-avatar-engine]]).

  python scripts/mascot_talk.py --audio voice.mp3 --out mascot_talk.mp4 [--image mascot.png]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import shutil
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RHUBARB = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "rhubarb", "rhubarb.exe")
MASCOT = os.path.join(ROOT, "7_ASSETS", "brand", "logos", "Chi Quyet Academy Mascot Logo.png")
BG = (244, 247, 255, 255)   # brand light --bg #F4F7FF

# Fallback mouth center (fraction of image) for the legacy default mascot, used only if MediaPipe can't
# find a face. Real mascots differ → we AUTO-LOCATE the mouth per image (see _locate_mouth).
MX, MY = 0.510, 0.362
# rhubarb 9 shapes → (half-width ratio, height ratio) RELATIVE TO THE DETECTED MOUTH WIDTH. A/X closed.
# Cartoon-native: a closed smile arc, or an open mouth (dark interior + teeth) scaled to the real mouth.
VISEME = {
    "A": (0.50, 0.00), "X": (0.50, 0.00),          # closed / rest → smile arc
    "B": (0.48, 0.16), "G": (0.44, 0.14),          # slight open (consonants, f/v)
    "C": (0.52, 0.40), "H": (0.50, 0.38),          # medium (e, L)
    "D": (0.54, 0.62),                              # wide open (a)
    "E": (0.42, 0.46),                             # round-ish (o)
    "F": (0.34, 0.30),                             # pucker (u/w)
}


def _locate_mouth(base):
    """Auto-locate the mascot's mouth via MediaPipe FaceMesh (works on cartoon faces too).
    Returns (cx, cy, mouth_w_px) in image pixels, or None if no face/mediapipe."""
    try:
        import numpy as np
        import mediapipe as mp
        # keep the WHOLE body guarded: MediaPipe's process()/landmark access can raise on odd inputs, and
        # the contract is "None on any failure" so make_talking_mascot falls back to a default mouth spot.
        W, H = base.size
        rgb = np.array(base.convert("RGB"))
        fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                             refine_landmarks=False, min_detection_confidence=0.3)
        res = fm.process(rgb)
        if not res.multi_face_landmarks:
            return None
        lm = res.multi_face_landmarks[0].landmark
        def px(i):
            return lm[i].x * W, lm[i].y * H
        lc, rc = px(61), px(291)                          # mouth corners
        top, bot = px(13), px(14)                         # inner lips
        cx = (lc[0] + rc[0] + top[0] + bot[0]) / 4.0
        cy = (top[1] + bot[1]) / 2.0
        mouth_w = ((rc[0] - lc[0]) ** 2 + (rc[1] - lc[1]) ** 2) ** 0.5
        return int(cx), int(cy), max(8.0, mouth_w)
    except Exception:
        return None


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _visemes(audio, work):
    """Rhubarb phonetic recognizer (language-independent → safe for Vietnamese)."""
    wav = os.path.join(work, "in.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", audio, "-ar", "16000", "-ac", "1", wav], check=True)
    out = os.path.join(work, "visemes.json")
    subprocess.run([RHUBARB, "-r", "phonetic", "-f", "json", "-o", out, wav], check=True)
    d = json.load(open(out, encoding="utf-8"))
    return d["mouthCues"], d["metadata"]["duration"]


def _viseme_at(cues, t):
    for c in cues:
        if c["start"] <= t < c["end"]:
            return c["value"]
    return "X"


def _skin_color(im, cx, cy, h):
    # sample skin just above the mouth (upper lip / philtrum) to build the cover patch
    return im.getpixel((cx, int(cy - 0.055 * h)))


def make_talking_mascot(audio, out_mp4, image=None, fps=25, crop=None):
    image = image or MASCOT
    work = tempfile.mkdtemp(prefix="mascot_")
    frames_dir = os.path.join(work, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    try:
        cues, dur = _visemes(os.path.abspath(audio), work)
        base = Image.open(image).convert("RGBA")
        W, H = base.size

        loc = _locate_mouth(base)
        if loc:
            cx, cy, mouth_w = loc
            print(f"[mascot_talk] mouth auto-located at ({cx},{cy}), width {mouth_w:.0f}px")
        else:
            cx, cy, mouth_w = int(MX * W), int(MY * H), 0.10 * W
            print("[mascot_talk] no face detected — using fallback mouth position")
        lw = max(2, int(mouth_w * 0.045))            # cartoon outline weight, scaled to the mouth

        # "clean" face = mascot with its drawn smile covered by a local skin patch (sampled above the mouth)
        skin = base.getpixel((cx, max(0, int(cy - 0.5 * mouth_w))))
        clean = base.copy()
        ImageDraw.Draw(clean).ellipse(
            [cx - mouth_w * 0.62, cy - mouth_w * 0.42, cx + mouth_w * 0.62, cy + mouth_w * 0.42], fill=skin)

        nframes = int(dur * fps)
        for i in range(nframes):
            t = i / fps
            v = _viseme_at(cues, t)
            ow, oh = VISEME.get(v, VISEME["X"])       # ratios of mouth_w
            frame = clean.copy()
            dr = ImageDraw.Draw(frame)
            hw, hh = int(ow * mouth_w), max(1, int(oh * mouth_w))
            lip = (120, 60, 60, 255)
            if oh <= 0.02:               # closed → a soft cartoon smile arc
                dr.arc([cx - hw, cy - int(mouth_w * 0.28), cx + hw, cy + int(mouth_w * 0.28)],
                       20, 160, fill=lip, width=lw)
            else:                         # open → dark interior + white teeth strip + outline
                dr.ellipse([cx - hw, cy - hh, cx + hw, cy + hh], fill=(90, 40, 40, 255))
                dr.rectangle([cx - int(hw * 0.8), cy - hh, cx + int(hw * 0.8), cy - int(hh * 0.45)],
                             fill=(255, 250, 245, 255))
                dr.ellipse([cx - hw, cy - hh, cx + hw, cy + hh], outline=lip, width=lw)
            out = Image.new("RGBA", base.size, BG)
            out.alpha_composite(frame)
            img = out.convert("RGB")
            if crop:
                img = img.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
            img.save(os.path.join(frames_dir, f"f_{i:05d}.jpg"), quality=90)

        # frames + voice → mp4
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                        "-framerate", str(fps), "-i", os.path.join(frames_dir, "f_%05d.jpg"),
                        "-i", os.path.abspath(audio),
                        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",   # yuv420p needs even dims
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", os.path.abspath(out_mp4)], check=True)
        print(f"[mascot_talk] ✓ {out_mp4}  ({nframes} frames, {dur}s)")
        return out_mp4
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Talking mascot (Rhubarb visemes → animated mouth)")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--image", help="mascot PNG (default: Chi Quyet Academy Mascot)")
    ap.add_argument("--fps", type=int, default=25)
    a = ap.parse_args()
    make_talking_mascot(a.audio, a.out, image=a.image, fps=a.fps)


if __name__ == "__main__":
    raise SystemExit(main())
