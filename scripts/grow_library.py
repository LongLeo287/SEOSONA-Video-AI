# -*- coding: utf-8 -*-
"""grow_library — one entry point to GROW the 3 libraries (template · component · block).

This is the executable face of the Self-Improvement Loop (`6_SOP/SELF_IMPROVEMENT_LOOP.md`) for the
HyperFrames libraries. It automates the parts that CAN be automated — generate a template, preview a
block/component, register it in the selector, regenerate the catalog — and points you to the human/LLM
stages (DISCOVER → ANALYZE → DECIDE) for everything that needs judgment. It does NOT reinvent the loop;
it ties existing tools together (template_generator, hf_blocks, block_picker, template_picker, gen_catalog).

  python scripts/grow_library.py status
  python scripts/grow_library.py template "Top 7 lỗi SEO khiến tụt hạng" --scenes 7
  python scripts/grow_library.py block cinematic-zoom
  python scripts/grow_library.py component vignette

Process (nạp → học → tạo) per layer is documented in `2_KNOWLEDGE/hyperframes/LIBRARY_PIPELINE.md`.
"""
import os
import sys
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
TPL_DIR = os.path.join(ROOT, "7_ASSETS", "templates")
PREVIEW = os.path.join(ROOT, "8_WORKSPACE", "clones")


def _n_templates():
    return len([f for f in os.listdir(TPL_DIR) if f.endswith(".json")]) if os.path.isdir(TPL_DIR) else 0


def status():
    import hf_blocks, block_picker, template_picker
    print("== LIBRARY STATUS ==")
    print(f"  TEMPLATE : {_n_templates():>3} archetypes   · selector template_picker ({len(template_picker._RULES)} rules)")
    print(f"  BLOCK    : {len(hf_blocks.list_blocks()):>3} blocks       · selector block_picker ({len(block_picker._RULES)} rules)"
          f" · budget {os.environ.get('SEOSONA_BLOCK_BUDGET','4')}/video")
    comps = hf_blocks.list_components()
    caps = sum(1 for c in comps if c["kind"] == "caption")
    print(f"  COMPONENT: {len(comps):>3} ({caps} caption + {len(comps)-caps} effect) · render via hf_blocks.render_component")
    try:
        import effect_library as el
        s = el.status()
        print(f"  EFFECT   : {s['transitions']:>3} transitions + {s['text_effects']} text-effects + {s.get('effects',0)} overlays + {s['exits']} exits")
        print(f"             + {s.get('motion_profiles',0)} motion-profiles + {s.get('sfx_categories',0)} sfx-categories · selector effect_library (all rotated per-video)")
    except Exception as _e:
        print(f"  EFFECT   : (unavailable: {_e})")
    print("  Grow one:  grow_library.py template \"<brief>\" | block <name> | component <name>")


def add_template(brief, scenes):
    """TẠO a template archetype (SIL 6-BUILD) + remind to register (8-WIRE) + regen catalog (9-RECORD)."""
    import template_generator as gen
    path = gen.generate(brief, n=scenes)
    if not path:
        return
    name = os.path.splitext(os.path.basename(path))[0]
    _regen_catalog()
    print("  ✔ created + catalog updated.")
    print(f"  → WIRE: add a keyword rule to 4_BRAIN/template_picker.py _RULES so '{name}' auto-selects.")
    print(f"  → RECORD: note it in 2_KNOWLEDGE/INGESTION_LOG.md if it came from a learned source.")


def add_block(name):
    """VERIFY a block renders (SIL 7) + check it's wired in block_picker (SIL 8)."""
    import hf_blocks, block_picker
    if not any(b["name"] == name for b in hf_blocks.list_blocks()):
        print(f"  ✗ '{name}' not in registry/blocks. Drop its <name>/ dir there first (see LIBRARY_GROWTH.md).")
        return
    out = os.path.join(PREVIEW, f"preview_block_{name}.mp4")
    ok = hf_blocks.render_block(name, out)
    print(f"  render preview: {'OK → ' + out if ok else 'FAILED'}")
    wired = any(name == tpl for _, tpl in block_picker._RULES)
    print(f"  block_picker rule: {'present ✓' if wired else 'MISSING — add a keyword→' + name + ' rule so it auto-fires'}")


def add_component(name):
    """Preview a component (SIL 7) + show how to embed it (SIL 8)."""
    import hf_blocks
    if not any(c["name"] == name for c in hf_blocks.list_components()):
        print(f"  ✗ '{name}' not in registry/components.")
        return
    out = os.path.join(PREVIEW, f"preview_comp_{name}.mp4")
    ok = hf_blocks.render_component(name, out)
    print(f"  render demo: {'OK → ' + out if ok else 'FAILED'}")
    snip = hf_blocks.component_snippet(name)
    kind = "caption STYLE (needs text+timing fed in)" if name.startswith("caption-") else "EFFECT (paste snippet into a stage)"
    print(f"  kind: {kind} · snippet {'available' if snip else 'missing'} via hf_blocks.component_snippet('{name}')")


def _regen_catalog():
    import subprocess
    gc = os.path.join(ROOT, "scripts", "gen_catalog.py")
    if os.path.exists(gc):
        subprocess.run([sys.executable, gc], cwd=ROOT,
                       env=dict(os.environ, PYTHONUTF8="1"), capture_output=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Grow the 3 HyperFrames libraries (template/component/block).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    pt = sub.add_parser("template"); pt.add_argument("brief"); pt.add_argument("--scenes", type=int, default=7)
    pb = sub.add_parser("block"); pb.add_argument("name")
    pc = sub.add_parser("component"); pc.add_argument("name")
    a = ap.parse_args()
    if a.cmd == "status": status()
    elif a.cmd == "template": add_template(a.brief, a.scenes)
    elif a.cmd == "block": add_block(a.name)
    elif a.cmd == "component": add_component(a.name)
