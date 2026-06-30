#!/usr/bin/env python3
"""Skill-library linter — validate OUR OWN skills' SKILL.md files.

Pattern from yusufkaraaslan/Skill_Seekers (MIT) SkillQualityChecker, re-implemented native + lean.
Catches malformed skills (no frontmatter / no name / no description / empty body) before they ship.
The skill-side complement to the other automated gates: scripts/security_scan.py (external repos)
and make_video._lint_script (video narration). Static, offline, zero-dependency.

  python scripts/skill_lint.py      (exit 1 if any skill needs fixing)  /  npm run skill:lint
"""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _lint_one(path):
    issues = []
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m:
        return ["thiếu YAML frontmatter (---...---)"]
    fm, body = m.group(1), m.group(2)
    if not re.search(r"^name:\s*\S", fm, re.M):
        issues.append("thiếu 'name'")
    if not re.search(r"^description:\s*(\S|[>|])", fm, re.M):
        issues.append("thiếu 'description'")
    if len(body.strip()) < 80:
        issues.append(f"body quá ngắn ({len(body.strip())} ký tự — skill rỗng?)")
    return issues


def lint():
    pats = [os.path.join(ROOT, ".agents", "skills", "*", "SKILL.md"),
            os.path.join(ROOT, "2_KNOWLEDGE", "domain_skills", "*", "SKILL.md")]
    files = sorted(f for p in pats for f in glob.glob(p))
    bad = 0
    for f in files:
        iss = _lint_one(f)
        if iss:
            bad += 1
            print(f"  ⚠ {os.path.relpath(f, ROOT)}\n      - " + "\n      - ".join(iss))
    status = "✓ all OK" if bad == 0 else f"{bad} cần sửa"
    print(f"[skill-lint] {len(files)} skills · {len(files) - bad} OK · {status}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if lint() > 0 else 0)
