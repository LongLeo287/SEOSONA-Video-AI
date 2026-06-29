# -*- coding: utf-8 -*-
"""SEOSONA Video — Dependency Freshness Check.

Operating principle (user, 2026-06-29): the core libraries / engines must be kept
CURRENT — checked continuously, never left stale (e.g. HyperFrames must not lag the
latest release). This reports installed-vs-latest for the engines that matter, so
"are we up to date?" is one command, not a guess.

    python scripts/check_freshness.py            # report
    python scripts/check_freshness.py --json      # machine-readable

It only REPORTS (never auto-upgrades) — bumping the render engine or torch can break
renders/inference, so upgrades stay a reviewed step (verify a render after bumping
HyperFrames; keep torch pinned for the inference env — training uses its own venv).
"""
import json, sys, subprocess, urllib.request

# The engines/libraries that define the system. Keep this list curated, not noisy.
NPM = ["hyperframes", "@hyperframes/producer", "@hyperframes/shader-transitions"]
PY = ["vieneu", "faster-whisper", "transformers", "torch", "demucs", "librosa",
      "soundfile", "edge-tts", "playwright", "openai", "neucodec", "peft", "sea-g2p"]


def _npm_latest(pkg):
    try:
        return subprocess.run(["npm", "view", pkg, "version"], capture_output=True,
                              text=True, shell=(sys.platform == "win32"), timeout=30).stdout.strip()
    except Exception:
        return None


def _npm_installed(pkg):
    import os
    p = os.path.join("node_modules", *pkg.split("/"), "package.json")
    try:
        return json.load(open(p, encoding="utf-8")).get("version")
    except Exception:
        return None


def _py_installed(pkg):
    import importlib.metadata as m
    try:
        return m.version(pkg)
    except Exception:
        return None


def _pypi_latest(pkg):
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=20) as r:
            return json.load(r)["info"]["version"]
    except Exception:
        return None


def check():
    rows = []
    for pkg in NPM:
        rows.append({"eco": "npm", "name": pkg,
                     "installed": _npm_installed(pkg), "latest": _npm_latest(pkg)})
    for pkg in PY:
        rows.append({"eco": "pip", "name": pkg,
                     "installed": _py_installed(pkg), "latest": _pypi_latest(pkg)})
    for r in rows:
        i, l = r["installed"], r["latest"]
        r["status"] = ("missing" if not i else "unknown" if not l else
                       "current" if i.split("+")[0] == l else "OUTDATED")
    return rows


if __name__ == "__main__":
    rows = check()
    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=2)); sys.exit(0)
    print("=" * 58)
    print(" SEOSONA Video — dependency freshness")
    print("=" * 58)
    outdated = 0
    for r in rows:
        mark = {"current": "OK ", "OUTDATED": "!! ", "missing": "?? ", "unknown": " . "}[r["status"]]
        if r["status"] == "OUTDATED":
            outdated += 1
        print(f"  {mark}{r['eco']:3} {r['name']:32} {str(r['installed']):16} -> {r['latest']}")
    print("=" * 58)
    print(f"  {outdated} outdated. Review before upgrading engines (render/torch can break).")
