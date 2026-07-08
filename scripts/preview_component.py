# -*- coding: utf-8 -*-
"""Render ONE native_composer scene component to a PNG for craft review (no video / no voice).

Wraps `native_composer._component(kind, data, acc, pal)` in the real `_css` + a centered scene
frame and screenshots it with Playwright. Light (Chromium only) → safe to run beside training.

Usage (data is a Python literal / JSON passed inline by the caller script, so this is mostly
imported):  from preview_component import preview; preview("compare", {...}, "out.png")
"""
import os, sys, tempfile
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
nc = import_module("native_composer")


def preview(kind, data, out_png, *, brand="seosona", acc_role="blue", kicker="", title="", W=1080, H=1920):
    from playwright.sync_api import sync_playwright
    pal = nc.ACCENT_PALETTE.get(brand, nc.ACCENT_PALETTE["seosona"])
    acc = pal.get(acc_role, acc_role)
    comp = nc._component(kind, data, acc, pal)
    css = nc._css(brand, W, H)
    head = ""
    if kicker:
        head += f'<div class="kicker" style="background:{acc}1a;color:{acc};align-self:center;margin-bottom:20px">{kicker}</div>'
    if title:
        head += f'<div class="head" style="text-align:center;margin-bottom:36px"><span class="l1">{title}</span></div>'
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}\n'
            f'#root{{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:120px 80px}}'
            f'</style></head><body><div id="root">{head}{comp}</div></body></html>')
    tmp = os.path.join(tempfile.gettempdir(), "_comp_preview.html")
    open(tmp, "w", encoding="utf-8").write(html)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)) or ".", exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto("file:///" + tmp.replace("\\", "/"), wait_until="networkidle")
        pg.screenshot(path=out_png, type="png")
        b.close()
    return out_png


if __name__ == "__main__":
    # smoke: render the upgraded compare (VS badge + winner glow) both modes, both brands
    out = os.path.join(ROOT, "8_WORKSPACE", "template_study", "component_previews")
    d_vs = {"left": ("Thủ công", ["Mất thời gian", "Dễ sai", "Khó bảo trì"]),
            "right": ("Với AI Agent", ["Tự động", "Chính xác", "Mở rộng dễ"])}
    d_ba = {"mode": "beforeafter", "left": ("3 TIẾNG", ["Căn chỉnh tay", "Sửa từng dòng"]),
            "right": ("3 PHÚT", ["Mô tả 1 câu", "AI dựng xong"])}
    preview("compare", d_vs, os.path.join(out, "compare_vs_seosona.png"), brand="seosona",
            kicker="SO SÁNH", title="Thủ công hay tự động?")
    preview("compare", d_ba, os.path.join(out, "compare_beforeafter_cqa.png"), brand="cqa",
            kicker="TRƯỚC / SAU", title="Nhanh hơn bao nhiêu?")
    print("previews →", out)
