# -*- coding: utf-8 -*-
"""License-first template manifest (pattern from nexu-io/html-video, Apache-2.0).

Make HyperFrames craft components / templates AGENT-READABLE and attribution-clean: each ships a
`template.manifest.json` with (1) an input JSON-schema (which slots an LLM must fill), and (2) 3-layer
provenance + SPDX so commercial-use is verifiable by construction. A machine-readable companion to
`2_KNOWLEDGE/INGESTION_LOG.md`.

    python 2_KNOWLEDGE/scripts/template_manifest.py scaffold <template_dir> --name X --license MIT
    python 2_KNOWLEDGE/scripts/template_manifest.py validate <template_dir>
"""
import os
import sys
import json
import argparse

PERMISSIVE = {"MIT", "Apache-2.0", "BSD-3-Clause", "Unlicense", "CC0-1.0", "ISC"}


def scaffold(template_dir, name, license_id="MIT", origin="", upstream="", transform=""):
    """Write a template.manifest.json skeleton next to a template."""
    os.makedirs(template_dir, exist_ok=True)
    manifest = {
        "name": name,
        "inputs": {  # JSON-schema-ish: slots an agent fills
            "type": "object",
            "properties": {
                "title": {"type": "string", "maxLength": 60, "example": "Tiêu đề"},
                "accent": {"type": "string", "enum": ["cyan", "violet", "gold", "green"]},
            },
            "required": ["title"],
        },
        "output": {"aspect": "9:16", "format": "html-hyperframes"},
        "provenance": {  # 3 layers
            "L1_origin": origin or "<real-world origin of the visual idea>",
            "L2_upstream": upstream or "<upstream OSS skill/repo + its license>",
            "L3_transform": transform or "<how it was adapted for SEOSONA>",
        },
        "license": {"spdx": license_id, "commercial_ok": license_id in PERMISSIVE},
    }
    out = os.path.join(template_dir, "template.manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[manifest] scaffolded → {out} (commercial_ok={manifest['license']['commercial_ok']})")
    return out


def validate(template_dir):
    """Check a template's manifest: schema present, provenance filled, license declared + permissive."""
    p = os.path.join(template_dir, "template.manifest.json")
    if not os.path.exists(p):
        print(f"[manifest] MISSING: {p}"); return False
    m = json.load(open(p, encoding="utf-8"))
    issues = []
    if not m.get("name"):
        issues.append("no name")
    if not (m.get("inputs") or {}).get("properties"):
        issues.append("no input schema")
    prov = m.get("provenance") or {}
    for k in ("L1_origin", "L2_upstream", "L3_transform"):
        if not prov.get(k) or prov[k].startswith("<"):
            issues.append(f"provenance {k} not filled")
    lic = (m.get("license") or {}).get("spdx")
    if not lic:
        issues.append("no license")
    elif lic not in PERMISSIVE:
        issues.append(f"license {lic} not permissive (verify commercial use)")
    if issues:
        print(f"[manifest] ⚠ {template_dir}: " + "; ".join(issues)); return False
    print(f"[manifest] ✅ {template_dir}: valid + commercial-safe ({lic})"); return True


def main():
    ap = argparse.ArgumentParser(description="HyperFrames template manifest")
    sub = ap.add_subparsers(dest="cmd")
    sc = sub.add_parser("scaffold"); sc.add_argument("dir"); sc.add_argument("--name", required=True)
    sc.add_argument("--license", default="MIT"); sc.add_argument("--origin", default="")
    sc.add_argument("--upstream", default=""); sc.add_argument("--transform", default="")
    va = sub.add_parser("validate"); va.add_argument("dir")
    a = ap.parse_args()
    if a.cmd == "scaffold":
        scaffold(a.dir, a.name, a.license, a.origin, a.upstream, a.transform)
    elif a.cmd == "validate":
        sys.exit(0 if validate(a.dir) else 1)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
