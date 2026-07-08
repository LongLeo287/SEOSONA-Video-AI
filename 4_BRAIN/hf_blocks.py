# -*- coding: utf-8 -*-
"""HyperFrames block bridge — make the 97-block registry USABLE by the factory.

The vendored library at `5_FRAMEWORK/hf_engine/registry/blocks` (cinematic-zoom, code-snippet-*,
liquid-glass-*, …) was catalogued but unused: `native_composer` renders only ~14 hand-built components.
This module renders ANY registry block to a standalone clip the factory can drop in as a b-roll /
cutaway / transition (e.g. course_video's b-roll overlay, or a news cutaway). Reuses the same
HyperFrames CLI + ffmpeg that native_composer renders with. See `2_KNOWLEDGE/hyperframes/FACTORY_BLOCK_PALETTE.md`.

    from hf_blocks import list_blocks, render_block
    render_block("cinematic-zoom", "out.mp4")            # → a clip you can overlay
"""
import os
import json
import shutil
import tempfile
import subprocess
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLOCKS = os.path.join(ROOT, "5_FRAMEWORK", "hf_engine", "registry", "blocks")
COMPONENTS = os.path.join(ROOT, "5_FRAMEWORK", "hf_engine", "registry", "components")

# SEOSONA brand (light-mode): blue #2A5BDA, coral #E2724D, ink #16224A, green #16A34A.
# Auto brand-skin: remap the kit's recurring ACCENT colours (gold/purple/cyan/MS-blue used for
# highlights, glows, transitions) to brand — but LEAVE code-syntax greys/darks + macOS traffic-light
# dots alone (those are structural, re-colouring them looks wrong). Best-effort, on by default.
import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
from brand_kit import BLUE as _BLUE, CORAL as _CORAL   # single source of truth (brand_kit.py)
_SKIN_MAP = {
    "#f7b801": _CORAL, "#3d348b": _BLUE, "#b392f0": _BLUE, "#0078d4": _BLUE,
    "#79b8ff": _BLUE, "#00d4ff": _BLUE, "#00ffff": _BLUE, "#7c3aed": _BLUE,
    "#a0a0c0": "#6B7AA8", "#f97583": _CORAL, "#e07a5f": _CORAL, "#ff2e63": _CORAL,
}


def _brand_skin(html):
    """Remap the block's recurring accent colours to the SEOSONA palette (case-insensitive)."""
    import re
    def repl(m):
        return _SKIN_MAP.get(m.group(0).lower(), m.group(0))
    return re.sub(r"#[0-9a-fA-F]{6}", repl, html)


# ---------------------------------------------------------------------------
# SAFE-USE gate — the registry blocks are GALLERY demos: they ship (a) block-preview CHROME
# ("Cinematic Zoom / Prompt / SCENE A / 07 / 14") and (b) hardcoded FAKE data ($5,169 count-up, fake
# census, follower counts). Rule (from the user): never leak the demo's numbers/chrome into a real
# video — a block may only appear once its demo content is STRIPPED and a QC gate confirms nothing
# fake remains. `_strip_demo_chrome` blanks the known preview-chrome text; `demo_leak` scans for any
# leftover demo token → a block that still leaks is REFUSED (returns None from render_block_safe).
# ---------------------------------------------------------------------------
# preview-chrome text classes (the gallery wrapper) — blank their inner text, keep structure/effect.
_CHROME_CLASSES = ("scene-label", "bp-name", "bp-plabel", "bp-prompt", "bp-desc", "bp-number",
                   "bp-title", "bp-label", "block-name", "block-label", "watermark", "preview-label")
# demo tokens that must NEVER reach a real video (chrome phrases + specific fake data seen in the audit).
_DEMO_TOKENS = (
    "scene a", "scene b", "prompt to change", "07 / 14", "use cinematic", "cinematic zoom",
    "monthly revenue", "conversion rate", "jan–jun", "population density", "u.s. census",
    "census", "$5,169", "$5,", "followers", "follower", "figma.com", "pythom", "greet.js",
    "8.2k", "12.8 km", "45 min", "dark modern vs code", "code diff", "logo outro", "flowchart",
    "spotify", "instagram", "reddit", "playlist", "now playing",
)


def _strip_demo_chrome(html):
    """Blank the inner TEXT of the gallery preview-chrome elements (keeps layout + effect intact)."""
    import re
    out = html
    cls = "|".join(_CHROME_CLASSES)
    # <tag ... class="… chrome …" …> INNER </tag>  → blank INNER (non-greedy, single element)
    out = re.sub(r'(<([a-zA-Z0-9]+)[^>]*class="[^"]*(?:' + cls + r')[^"]*"[^>]*>)(.*?)(</\2>)',
                 lambda m: m.group(1) + m.group(4), out, flags=re.S)
    return out


def demo_leak(html):
    """Return the list of demo tokens still present (case-insensitive). Empty = safe to use."""
    low = html.lower()
    return [t for t in _DEMO_TOKENS if t in low]


def prepare_block_html(name, strip=True):
    """Load a block's HTML, brand-skin it, strip demo chrome. Returns (html, leaks). `leaks` non-empty
    ⇒ the block still shows demo/fake content and must NOT be used as-is."""
    path = os.path.join(BLOCKS, name, f"{name}.html")
    if not os.path.exists(path):
        return None, ["<missing html>"]
    html = open(path, encoding="utf-8").read()
    html = _brand_skin(html)
    if strip:
        html = _strip_demo_chrome(html)
    return html, demo_leak(html)


def list_blocks(tag=None):
    """List available registry blocks (name, title, tags, duration). Filter by `tag` if given."""
    out = []
    if not os.path.isdir(BLOCKS):
        return out
    for name in sorted(os.listdir(BLOCKS)):
        meta = os.path.join(BLOCKS, name, "registry-item.json")
        if not os.path.exists(meta):
            continue
        try:
            d = json.load(open(meta, encoding="utf-8"))
        except Exception:
            continue
        tags = d.get("tags", []) or []
        if tag and tag not in tags:
            continue
        out.append({"name": name, "title": d.get("title", name), "tags": tags,
                    "duration": d.get("duration"), "dimensions": d.get("dimensions")})
    return out


def list_components(tag=None):
    """List the 25 registry COMPONENTS — caption STYLES (the sub/subtitle look, NOT the text) + visual
    EFFECTS (grain, vignette, motion-blur, transitions). `kind` = 'caption' | 'effect'."""
    out = []
    if not os.path.isdir(COMPONENTS):
        return out
    for name in sorted(os.listdir(COMPONENTS)):
        meta = os.path.join(COMPONENTS, name, "registry-item.json")
        if not os.path.exists(meta):
            continue
        try:
            d = json.load(open(meta, encoding="utf-8"))
        except Exception:
            continue
        tags = d.get("tags", []) or []
        if tag and tag not in tags:
            continue
        out.append({"name": name, "title": d.get("title", name),
                    "kind": "caption" if name.startswith("caption-") else "effect", "tags": tags})
    return out


def _render(name, src, entry_name, out_mp4, timeout=300, strip_qc=False):
    """Copy a registry item dir → temp project, use `entry_name` as the composition, brand-skin, render.
    strip_qc=True (blocks): also strip preview-chrome + REFUSE if any demo/fake token still leaks."""
    if not os.path.isdir(src):
        print(f"[hf_blocks] unknown: {name}")
        return None
    nc = import_module("native_composer")
    proj = tempfile.mkdtemp(prefix="hfreg_")
    try:
        for f in os.listdir(src):
            s = os.path.join(src, f)
            if os.path.isfile(s):
                shutil.copy(s, proj)
            elif os.path.isdir(s):
                shutil.copytree(s, os.path.join(proj, f))
        entry = os.path.join(proj, entry_name)
        if os.path.exists(entry):
            html = open(entry, encoding="utf-8").read()
            if os.environ.get("SEOSONA_BLOCK_BRAND", "1") == "1":   # auto brand-skin (on by default)
                html = _brand_skin(html)
            if strip_qc:
                html = _strip_demo_chrome(html)
                leaks = demo_leak(html)
                if leaks:                      # fake/demo content survives → NEVER put it in a real video
                    print(f"[hf_blocks] REFUSED '{name}' — demo/fake content leaks: {leaks[:5]}")
                    return None
            open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(html)
        if not os.path.exists(os.path.join(proj, "index.html")):
            print(f"[hf_blocks] no {entry_name} for '{name}'")
            return None
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"assets": "."}}, open(os.path.join(proj, "hyperframes.json"), "w"))
        json.dump({"id": name, "name": name}, open(os.path.join(proj, "meta.json"), "w"))
        out_mp4 = os.path.abspath(out_mp4)
        os.makedirs(os.path.dirname(out_mp4) or ".", exist_ok=True)
        r = subprocess.run(["node", nc._hf_cli(), "render", "--format", "mp4", "--output", out_mp4],
                           cwd=proj, env=nc._render_env(), capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0 and os.path.exists(out_mp4):
            print(f"[hf_blocks] rendered '{name}' → {out_mp4}")
            return out_mp4
        print(f"[hf_blocks] render failed (rc={r.returncode}): {(r.stderr or '')[-300:]}")
        return None
    finally:
        shutil.rmtree(proj, ignore_errors=True)


def render_block(name, out_mp4, timeout=300):
    """Render registry block `name` to a clip (its `<name>.html` composition), with demo-chrome STRIP +
    fake-data QC (refuses if any demo token leaks). Returns path or None."""
    return _render(name, os.path.join(BLOCKS, name), f"{name}.html", out_mp4, timeout, strip_qc=True)


def render_component(name, out_mp4, timeout=300):
    """Render a registry COMPONENT's demo (`demo.html`) to a clip — preview/use a caption style or effect."""
    return _render(name, os.path.join(COMPONENTS, name), "demo.html", out_mp4, timeout)


def component_snippet(name, brand=True):
    """Return a component's embeddable snippet HTML (`<name>.html`), brand-skinned by default. Effects
    (vignette/grain/shimmer) paste into a composition's stage; caption styles still need text+timing fed in."""
    p = os.path.join(COMPONENTS, name, f"{name}.html")
    if not os.path.exists(p):
        print(f"[hf_blocks] no snippet for component '{name}'")
        return None
    html = open(p, encoding="utf-8").read()
    return _brand_skin(html) if brand else html


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        for b in list_blocks(sys.argv[2] if len(sys.argv) > 2 else None):
            print(f"  {b['name']:<34} {b['title']}  {b['tags']}")
    else:
        name = sys.argv[1] if len(sys.argv) > 1 else "cinematic-zoom"
        out = os.path.join(ROOT, "8_WORKSPACE", "clones", f"block_{name}.mp4")
        print("result:", render_block(name, out))
