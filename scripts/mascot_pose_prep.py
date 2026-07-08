"""Prepare mascot pose assets: key the baked checkerboard bg -> clean alpha, then extract each character
as a full, tightly-cropped transparent PNG via connected-components (handles ANY grid layout, never clips
arms, drops the text labels). Run on one or more AI pose sheets.

  .venv-musetalk/Scripts/python.exe scripts/mascot_pose_prep.py <sheet1.png> <sheet2.png> ...
Outputs -> 7_ASSETS/brand/SEOSONA/mascot_poses/<sheetstem>_<NN>.png
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "7_ASSETS", "brand", "SEOSONA", "mascot_poses")


def make_transparent(im, edge_eat=3):
    """Border-connected light-gray/white checkerboard -> alpha 0. Dilating the bg mask by `edge_eat`px
    eats the anti-aliased light fringe at the character outline so no halo remains on a dark background."""
    rgb = np.array(im.convert("RGB")).astype(int)
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mx = np.maximum(np.maximum(R, G), B); mn = np.minimum(np.minimum(R, G), B)
    isbg = (mn > 168) & ((mx - mn) < 38)                 # light + near-gray = the checkerboard/white
    lbl, _ = ndimage.label(isbg)
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]])))
    border.discard(0)
    bg = np.isin(lbl, list(border))
    bg = ndimage.binary_dilation(bg, iterations=edge_eat)  # eat the light fringe
    rgb2 = np.array(im.convert("RGB"))
    rgb2[bg] = 255                                         # neutralise transparent-area RGB (no checker bleed)
    out = np.dstack([rgb2, np.where(bg, 0, 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA")


def extract(sheet_path):
    stem = os.path.splitext(os.path.basename(sheet_path))[0]
    stem = stem.replace("Gemini_Generated_Image_", "").replace("-clean", "")[:10]
    im = make_transparent(Image.open(sheet_path))
    W, H = im.size
    a = np.array(im.split()[3])
    mask = a > 80
    mask = ndimage.binary_closing(mask, iterations=2)      # unify glow/anti-alias into one character blob
    lbl, n = ndimage.label(mask)
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.where(lbl == i)
        h = ys.max() - ys.min() + 1
        area = len(ys)
        if h > 0.16 * H and area > 0.006 * W * H:          # tall + substantial = a character (not a label)
            comps.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
    comps.sort(key=lambda c: (round(c[1] / (0.14 * H)), c[0]))  # reading order: row band, then left->right
    saved = 0
    for k, (x0, y0, x1, y1) in enumerate(comps, 1):
        pad = 6
        crop = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad + 1), min(H, y1 + pad + 1)))
        crop.save(os.path.join(OUT, f"{stem}_{k:02d}.png"))
        saved += 1
    print(f"  {os.path.basename(sheet_path)} -> {saved} characters (prefix {stem}_)")
    return saved


def main():
    os.makedirs(OUT, exist_ok=True)
    sheets = sys.argv[1:]
    if not sheets:
        print("usage: mascot_pose_prep.py <sheet.png> ..."); return 1
    total = sum(extract(s) for s in sheets)
    print(f"done: {total} poses -> {OUT}")


if __name__ == "__main__":
    raise SystemExit(main())
