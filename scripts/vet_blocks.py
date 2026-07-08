# -*- coding: utf-8 -*-
"""Vet the 97 HyperFrames registry blocks for SAFE factory use (real data only, no fake/demo leak).

For each block: brand-skin + strip preview-chrome → scan for leftover demo tokens (fake data) →
classify by tags. Writes a manifest the block_picker can trust. STATIC vet (no render) so it's fast;
render-verify the 'clean' shortlist separately.

Classes:
  reject_fakedata  — demo/fake data survives the strip (JS-embedded numbers, census, followers…) → OFF
  redundant_native — code/terminal/data/flow: native components already do this with REAL data → OFF
  ambient_fx       — pure visual effect / shader, no text or data → usable as a branded cutaway/bg
  clean_other      — passed QC, not obviously redundant → candidate (render-verify before enabling)
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
import hf_blocks as H

REDUNDANT_TAGS = {"code", "terminal", "vscode", "code-animation", "apple-terminal",
                  "data", "chart", "finance", "map", "geography", "choropleth", "flowchart", "diagram"}
FX_TAGS = {"transition", "shader", "webgl", "webgpu", "overlay", "sfx", "kinetic", "particles", "3d"}


def classify(name, tags, leaks):
    tset = set(tags)
    if leaks:
        return "reject_fakedata"
    if tset & REDUNDANT_TAGS:
        return "redundant_native"
    if tset & FX_TAGS:
        return "ambient_fx"
    return "clean_other"


def main():
    blocks = H.list_blocks()
    rows, buckets = [], {}
    for b in blocks:
        try:
            name, tags = b["name"], b.get("tags", [])
            html, leaks = H.prepare_block_html(name, strip=True)
            cls = "reject_fakedata" if html is None else classify(name, tags, leaks)
            rows.append({"name": name, "tags": tags, "class": cls, "leaks": leaks[:6]})
            buckets.setdefault(cls, []).append(name)
        except Exception as e:
            # one malformed block / a prepare_block_html failure must NOT crash the whole vet (→ no manifest
            # written → block_picker keeps trusting a stale one). Skip it, keep vetting the rest.
            print(f"[vet] skipped block {b.get('name', '?') if isinstance(b, dict) else b}: {e}")
    out = os.path.join(ROOT, "2_KNOWLEDGE", "hyperframes", "BLOCK_VET_MANIFEST.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"total": len(rows), "buckets": {k: v for k, v in buckets.items()}, "rows": rows},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"VET {len(rows)} blocks →")
    for k in ("ambient_fx", "clean_other", "redundant_native", "reject_fakedata"):
        v = buckets.get(k, [])
        print(f"  {k:18} {len(v):3}  {', '.join(v[:8])}{' …' if len(v) > 8 else ''}")
    print(f"\nmanifest → {out}")
    print("SAFE-TO-USE (ambient_fx + clean_other):", len(buckets.get("ambient_fx", [])) + len(buckets.get("clean_other", [])))


if __name__ == "__main__":
    main()
