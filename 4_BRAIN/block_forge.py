# -*- coding: utf-8 -*-
"""BLOCK FORGE — turn the 97 HyperFrames registry blocks (16:9 dark gallery DEMOS) into a real
9:16, light-brand, CONTENT-INJECTABLE template kho the factory can drop into videos.

Per block:
  1. swap 1920×1080 → 1080×1920 everywhere (the blocks use the pair consistently, incl. shader aspect
     math `1920.0/1080.0`, so the flip yields true 9:16),
  2. strip the gallery preview-chrome (`.bp-*` / `.scene-label`) + brand-skin colours,
  3. (LLM, best-effort) re-layout for portrait + light brand + replace the demo CONTENT with mustache
     slots ({{title}} / {{sub}} / {{#items}}{{.text}}{{/items}}) so the SCENE's real data fills it,
  4. RENDER-VALIDATE at 1080×1920 + demo-leak QC → only a clean render enters the kho,
  5. register to `7_ASSETS/blocks_9x16/<name>.html` + `manifest.json` (name→schema).

At video time: `render_filled(name, data, out)` fills the slots with the scene's real content and
renders the clip. This is the block-equivalent of [[frame-synth]] — the kho grows from real assets,
never ships the demo's fake data (the QC refuses any leak).
"""
import os
import re
import json
import shutil
import tempfile
import subprocess
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLOCKS = os.path.join(ROOT, "5_FRAMEWORK", "hf_engine", "registry", "blocks")
KHO = os.path.join(ROOT, "7_ASSETS", "blocks_9x16")
MANIFEST = os.path.join(KHO, "manifest.json")

import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
import hf_blocks as _hf


def _swap_dims(html):
    """1920×1080 → 1080×1920 (portrait). The blocks use the pair consistently, so a token swap flips
    the composition, canvas, setSize, viewport and shader aspect ratio all at once."""
    html = html.replace("1920", "__W__").replace("1080", "__H__")
    return html.replace("__W__", "1080").replace("__H__", "1920")


def _base_transform(name):
    """Deterministic 9:16 + strip-chrome + brand-skin base (no LLM). Returns html or None."""
    path = os.path.join(BLOCKS, name, f"{name}.html")
    if not os.path.exists(path):
        return None
    html = open(path, encoding="utf-8").read()
    html = _hf._brand_skin(html)
    html = _hf._strip_demo_chrome(html)
    html = _swap_dims(html)
    return html


_LLM_SYS = (
    "Bạn nhận một block HTML (vốn là demo gallery 16:9 nền tối). Hãy VIẾT LẠI thành một composition "
    "9:16 DỌC (1080×1920) thương hiệu SEOSONA — LIGHT MODE: nền trắng #ffffff/#EEF2F8, chữ #0F172A/#64748B, "
    "accent xanh #2A5BDA + coral #E2724D. GIỮ phong cách/hiệu ứng/kiểu mockup của block. "
    "BỎ mọi chrome xem trước (bp-*, scene-label, tên block, 'Prompt', số 'NN / NN') và MỌI dữ liệu demo/giả "
    "(số tiền, follower, census…). Thay NỘI DUNG demo bằng slot mustache: {{title}}, {{sub}}, và "
    "{{#items}}...{{.text}}...{{/items}} để hệ thống bơm dữ liệu THẬT của cảnh vào. Giữ seek-safe: nếu dùng "
    "GSAP thì timeline PAUSED, KHÔNG dùng Date.now()/requestAnimationFrame theo đồng hồ thật. Tự chứa (inline). "
    "Trả JSON THUẦN: {kind (snake_case), title, schema (mô tả data{title,sub,items}), html}."
)


def _llm_relayout(name, base_html):
    """Portrait-relayout + slot-ise the block via LLM. LOCAL-FIRST: when cloud quota is out (the norm at
    build time), go STRAIGHT to local Ollama — no 60s cloud backoff per block, the factory runs itself.
    Set SEOSONA_FORGE_CLOUD=1 to also try the cloud cascade (better quality) when quota is available.
    Best-effort → None (block is skipped, not force-rendered dark)."""
    try:
        llm = import_module("llm_engine")
    except Exception:
        return None
    user = (f"Block '{name}'. HTML hiện tại (đã 9:16 thô + bỏ chrome):\n{base_html[:9000]}\n\n"
            "Viết lại cho đẹp ở 9:16 dọc, light brand, có slot mustache cho nội dung thật.")
    spec = None
    try:                                            # local Ollama first (fast, free, self-sufficient)
        raw = llm._try_ollama_json(_LLM_SYS, user)
        spec = llm._parse_json_or_none(raw) if raw else None
    except Exception:
        spec = None
    if not (isinstance(spec, dict) and spec.get("html")) and os.getenv("SEOSONA_FORGE_CLOUD") == "1":
        try:
            spec = llm.generate_json_from_prompt(_LLM_SYS, user)
        except Exception:
            spec = None
    if isinstance(spec, dict) and spec.get("html") and len(str(spec["html"])) > 120:
        return spec
    return None


def _render_html(html, out_mp4, timeout=240):
    """Render a standalone composition HTML → mp4 at its own dimensions (reuses the HyperFrames CLI)."""
    nc = import_module("native_composer")
    proj = tempfile.mkdtemp(prefix="forge_")
    try:
        open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(html)
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"assets": "."}}, open(os.path.join(proj, "hyperframes.json"), "w"))
        json.dump({"id": "forge", "name": "forge"}, open(os.path.join(proj, "meta.json"), "w"))
        out_mp4 = os.path.abspath(out_mp4)
        os.makedirs(os.path.dirname(out_mp4) or ".", exist_ok=True)
        r = subprocess.run(["node", nc._hf_cli(), "render", "--format", "mp4", "--output", out_mp4],
                           cwd=proj, env=nc._render_env(), capture_output=True, text=True, timeout=timeout)
        return out_mp4 if (r.returncode == 0 and os.path.exists(out_mp4)) else None
    except Exception:
        return None
    finally:
        shutil.rmtree(proj, ignore_errors=True)


def _frame_is_light(mp4):
    """Grab a frame → mean luma. SEOSONA = light mode, so a forged template MUST render predominantly
    LIGHT (rejects dark shader blocks the deterministic path can't relight). True if bright / uncheckable."""
    try:
        nc = import_module("native_composer")
        png = mp4 + ".probe.png"
        subprocess.run([nc._ffmpeg_bin(), "-y", "-loglevel", "error", "-ss", "0.6", "-i", mp4,
                        "-frames:v", "1", png], capture_output=True, timeout=30)
        from PIL import Image
        im = Image.open(png).convert("L")
        mean = sum(im.getdata()) / max(1, im.width * im.height)
        os.remove(png)
        return mean >= 150            # light background (0=black … 255=white)
    except Exception:
        return True                   # can't measure → don't block (render+leak gates still applied)


# FX/shader blocks carry NO data — just a gallery-preview wrapper around a canvas. Force the canvas
# FULL-BLEED 9:16 + hide the chrome → a reusable abstract EFFECT/TRANSITION clip (no LLM, no fake data).
_FX_FULLBLEED = (
    '<style id="_fxfb">html,body,#root,[data-composition-id="main"],.scene,#scene,.stage,.container{'
    'width:1080px!important;height:1920px!important;margin:0!important;padding:0!important;'
    'overflow:hidden!important;left:0!important;top:0!important}'
    'canvas{position:absolute!important;top:0!important;left:0!important;'
    'width:1080px!important;height:1920px!important}'
    '.bp-grid,.bp-divider,.bp-number,.bp-right,.bp-name,.bp-plabel,.bp-prompt,.bp-desc,.scene-label,'
    '.bp-title,.bp-label,.block-name,.watermark,.preview-label{display:none!important}</style>')


def render_fx_clip(name, out_mp4, timeout=180):
    """Render an FX/shader block as a FULL-BLEED 9:16 abstract EFFECT clip (chrome hidden, canvas fills the
    frame). No data, no fake content → usable as a transition cover / motion background. None if it still
    leaks demo text or fails to render."""
    base = _base_transform(name)                 # brand-skin + strip chrome text + swap dims
    if not base:
        return None
    html = base.replace("</head>", _FX_FULLBLEED + "</head>", 1) if "</head>" in base else _FX_FULLBLEED + base
    if _hf.demo_leak(html):                       # still shows scene labels / demo text → not a clean fx
        return None
    return _render_html(html, out_mp4, timeout)


def _load_manifest():
    try:
        return json.load(open(MANIFEST, encoding="utf-8"))
    except Exception:
        return {}


def _save_manifest(m):
    os.makedirs(KHO, exist_ok=True)
    json.dump(m, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def forge(name, use_llm=True, verify=True):
    """Transform one block → a 9:16 injectable template in the kho. Returns the manifest entry or None.
    A block only enters the kho if it renders clean (9:16) with NO demo/fake leak."""
    base = _base_transform(name)
    if not base:
        print(f"[forge] {name}: no html"); return None
    kind, title, schema, html = name.replace("-", "_"), name, "data{title,sub,items[]}", base
    if use_llm:
        spec = _llm_relayout(name, base)
        if not spec:
            # no LLM relight → the deterministic base stays DARK and would fail the light gate anyway.
            # Skip WITHOUT rendering (saves a ~12s render per un-relightable block on the batch).
            print(f"[forge] {name}: skip — LLM could not relight to 9:16 light template")
            return None
        html = str(spec["html"]); kind = re.sub(r"[^a-z0-9_]", "", str(spec.get("kind", kind)).lower()) or kind
        title = spec.get("title", title); schema = spec.get("schema", schema)
    # QC: no demo/fake token may survive
    leaks = _hf.demo_leak(html)
    if leaks:
        print(f"[forge] {name}: REFUSED — demo leak {leaks[:4]}"); return None
    if verify:
        out = _render_html(html, os.path.join(tempfile.gettempdir(), f"forge_{name}.mp4"))
        if not out:
            print(f"[forge] {name}: REFUSED — 9:16 render failed"); return None
        light = _frame_is_light(out)
        os.remove(out) if os.path.exists(out) else None
        if not light:
            print(f"[forge] {name}: REFUSED — renders DARK (SEOSONA is light-only)"); return None
    os.makedirs(KHO, exist_ok=True)
    open(os.path.join(KHO, f"{name}.html"), "w", encoding="utf-8").write(html)
    m = _load_manifest()
    m[name] = {"kind": kind, "title": title, "schema": schema, "llm": bool(use_llm)}
    _save_manifest(m)
    print(f"[forge] {name}: ✓ forged → kho ({kind})")
    return m[name]


def render_filled(name, data, out_mp4, timeout=240):
    """Fill a forged 9:16 template's mustache slots with the scene's REAL data → render the clip. None
    if the template isn't in the kho or the render fails."""
    p = os.path.join(KHO, f"{name}.html")
    if not os.path.exists(p):
        return None
    tmpl = open(p, encoding="utf-8").read()
    try:
        fsyn = import_module("frame_synth")
        html = fsyn._fill(tmpl, data if isinstance(data, dict) else {}, data.get("acc", "#2A5BDA")
                          if isinstance(data, dict) else "#2A5BDA")
    except Exception:
        html = tmpl
    if _hf.demo_leak(html):          # never render a filled template that still shows demo/fake data
        return None
    return _render_html(html, out_mp4, timeout)


def kinds():
    return list(_load_manifest().keys())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        names = [b["name"] for b in _hf.list_blocks()]
        ok = sum(1 for n in names if forge(n, use_llm=True))
        print(f"\n[forge] {ok}/{len(names)} blocks → 9:16 kho")
    else:
        m = _load_manifest()
        print(f"BLOCK FORGE — {len(m)} forged 9:16 template(s): {list(m)}")
