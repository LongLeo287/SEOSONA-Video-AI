#!/usr/bin/env python3
"""Lightweight repo/skill security scanner — the SIL stage-3 SECURITY gate, automated.

Patterns distilled from NVIDIA/SkillSpector (Apache-2.0, 11.5k*) — re-implemented natively as
the cheap, high-signal SUBSET (regex + a simple Python-AST walk), NOT its full ~1500-LOC
framework (no MCP server / Docker / LangGraph / YARA / taint-tracking — those are BACKLOG).
Static, offline, zero-dependency. Run BEFORE adopting any external repo/skill:

    python scripts/security_scan.py 2_KNOWLEDGE/external_toolkits/<repo>

Verdict: SAFE (<=20) / CAUTION (<=50) / DO_NOT_ADOPT (>50). A high score = quarantine + log
as rejected (SELF_IMPROVEMENT_LOOP stage 3). Findings are advisory — a human still reviews.
"""
import ast
import glob
import os
import re
import sys

# (rule_id, severity, regex, message) — text patterns (any file)
_TEXT_RULES = [
    ("P1", "HIGH",
     r"ignore\s+(?:all\s+)?previous\s+instructions?|bypass\s+(?:safety|security|guard)|"
     r"you\s+are\s+now\s+.*(?:jailbreak|unrestricted|unfiltered)|"
     r"disregard\s+(?:your\s+)?(?:policy|guidelines?|safety)", "prompt-injection / instruction override"),
    ("P2", "HIGH",
     r"<!--.{0,80}(?:system|ignore|instruction|exfiltrat|secret).{0,80}-->|"
     r"[​‌‍⁠﻿]|[\U000e0000-\U000e007f]",
     "hidden instruction (HTML-comment / zero-width / unicode-tag smuggling)"),
    ("AR1", "HIGH",
     r"\b(?:never|do\s+not|don'?t)\s+(?:refuse|decline)\b|\balways\s+(?:comply|obey)\b|"
     r"no\s+request\s+is\s+(?:off-limits|forbidden)", "anti-refusal / jailbreak framing"),
    ("E2", "HIGH",
     r"os\.environ(?:\.get)?\s*[\[(]\s*['\"][^'\"]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)|"
     r"for\s+\w+\s*,\s*\w+\s+in\s+os\.environ\.items", "secret / env-var harvesting"),
    ("E1", "MEDIUM",
     r"requests\s*\.\s*(?:post|put)\s*\(\s*['\"]https?://|curl\s+.*(?:-d|--data)\b|"
     r"https?://(?:api|data|collect|analytics|webhook)\.", "external data transmission"),
    ("E3", "MEDIUM",
     r"(?:glob|os\.walk|listdir|find)\b.{0,40}(?:\.env|\.ssh|\.aws|id_rsa|credentials)",
     "filesystem secret enumeration"),
    ("SC2", "HIGH",
     r"curl\s+[^|]*\|\s*(?:sudo\s+)?(?:ba)?sh|wget\s+[^|]*\|\s*(?:python|node|sh)\b",
     "remote code execution (curl | bash)"),
    ("SC3", "HIGH",
     r"(?:exec|eval)\s*\(\s*(?:base64\.)?b64decode|marshal\.loads\s*\(|"
     r"(?:exec|eval)\s*\(\s*bytes\.fromhex|[A-Za-z0-9+/=]{220,}",
     "obfuscated code (b64/hex exec / huge blob)"),
    ("AS1", "HIGH",
     r"(?:open|Path|cat)\s*\(?\s*['\"]?[^'\"\n]{0,40}\.(?:claude|codex|gemini|aws|ssh)/|"
     r"~/\.(?:ssh|aws)/(?:id_rsa|credentials)", "agent-config / credential file access"),
]
_TEXT = [(rid, sev, re.compile(rx, re.I | re.M), msg) for rid, sev, rx, msg in _TEXT_RULES]

_AST_DANGER = {"exec", "eval", "compile", "__import__"}
_AST_OS = {"system", "popen", "execl", "execv", "execlp", "spawnl", "spawnv"}
_SCORE = {"CRITICAL": 50, "HIGH": 25, "MEDIUM": 10, "LOW": 5}
_SCAN_EXT = (".py", ".md", ".js", ".ts", ".sh", ".txt", ".yaml", ".yml", ".json", ".toml", ".cjs", ".mjs")


def _scan_text(rel, txt, out):
    for rid, sev, rx, msg in _TEXT:
        m = rx.search(txt)
        if m:
            out.append({"rule": rid, "sev": sev, "msg": msg, "file": rel,
                        "line": txt[:m.start()].count("\n") + 1})


def _scan_ast(rel, txt, out):
    try:
        tree = ast.parse(txt)
    except Exception:
        return
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Name) and f.id in _AST_DANGER:
            out.append({"rule": "AST", "sev": "CRITICAL" if f.id in ("exec", "eval") else "MEDIUM",
                        "msg": f"dangerous call {f.id}()", "file": rel, "line": n.lineno})
        elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            if f.value.id == "os" and f.attr in _AST_OS:
                out.append({"rule": "AST", "sev": "HIGH", "msg": f"os.{f.attr}()", "file": rel, "line": n.lineno})
            elif f.value.id == "subprocess":
                out.append({"rule": "AST", "sev": "MEDIUM", "msg": f"subprocess.{f.attr}()", "file": rel, "line": n.lineno})


def scan(root):
    out = []
    if os.path.isfile(root):
        paths = [root]
    else:
        paths = [p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True)
                 if os.path.isfile(p) and ".git" + os.sep not in p]
    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        if ext not in _SCAN_EXT:
            continue
        try:
            if os.path.getsize(p) > 2_000_000:
                continue
            txt = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        rel = os.path.relpath(p, root) if os.path.isdir(root) else p
        _scan_text(rel, txt, out)
        if ext == ".py":
            _scan_ast(rel, txt, out)
    score = sum(_SCORE.get(f["sev"], 0) for f in out)
    if any(f["file"].endswith(".py") for f in out):       # executable code → weight up (SkillSpector x1.3)
        score = int(score * 1.3)
    score = min(score, 100)
    rec = "SAFE" if score <= 20 else "CAUTION" if score <= 50 else "DO_NOT_ADOPT"
    return {"score": score, "recommendation": rec, "findings": out}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    r = scan(target)
    print(f"[security_scan] {target}")
    print(f"  score={r['score']}/100 -> {r['recommendation']} ({len(r['findings'])} findings)")
    for f in sorted(r["findings"], key=lambda x: -_SCORE.get(x["sev"], 0))[:40]:
        print(f"  [{f['sev']:<8}] {f['rule']:<4} {f['file']}:{f['line']} - {f['msg']}")
    sys.exit(0 if r["recommendation"] != "DO_NOT_ADOPT" else 2)
