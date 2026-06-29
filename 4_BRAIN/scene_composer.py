# -*- coding: utf-8 -*-
"""SEOSONA Scene-Composer (step 2/ADAPT) — turn a topic into `content` for a template.

The factory's content brain. It does the DETERMINISTIC plumbing automatically:
  - fetch_github(repo)   → real stars/desc/lang/license/topics (free GitHub API)
  - build the data slots (repo card, ★ stat, license badges) from that data
The CREATIVE parts (Vietnamese script segments + 2-tone headings + terminal lines +
compare points) are supplied by the caller — the Scene-Composer AGENT (an LLM, e.g.
Claude in the agent loop) writes them per `.agents/skills/scene-composer/SKILL.md`.
This keeps real data accurate (no hallucinated stars) while the prose stays natural.

Output `content` feeds native_composer.make_video_from_template(template, content, dir).
No voice config here — the engine uses the locked brand voice. No paid APIs.
"""
import os, sys, json, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def fetch_github(repo):
    """repo = 'owner/name' or a github URL → real metadata (free API, no key needed)."""
    repo = repo.strip().rstrip("/")
    if "github.com/" in repo:
        repo = repo.split("github.com/", 1)[1]
    repo = "/".join(repo.split("/")[:2])
    try:
        out = subprocess.run(["gh", "api", f"repos/{repo}"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        j = json.loads(out)
        stars = j.get("stargazers_count", 0)
        return {
            "owner": (j.get("owner") or {}).get("login", repo.split("/")[0]),
            "name": j.get("name", repo.split("/")[-1]),
            "full": j.get("full_name", repo),
            "desc": j.get("description") or "",
            "stars": stars,
            "stars_h": f"{stars:,}",
            "lang": j.get("language") or "",
            "license": ((j.get("license") or {}).get("spdx_id") or "").replace("NOASSERTION", ""),
            "topics": j.get("topics") or [],
            "url": j.get("html_url", f"https://github.com/{repo}"),
            "homepage": (j.get("homepage") or "").strip(),
        }
    except Exception as e:
        return {"error": str(e), "full": repo}


def repo_data_slots(gh, *, btn="Tải miễn phí", extra_tags=None):
    """Auto-build the repo-card / ★ bignum / license-badges data from GitHub metadata."""
    tags = [t for t in [gh.get("lang"), gh.get("license"), "Mã nguồn mở"] if t]
    tags += (extra_tags or [])
    return {
        "repo": {"owner": gh["owner"], "name": gh["name"], "stars": gh["stars_h"],
                 "desc": gh["desc"], "tags": tags[:4], "btn": btn},
        "stars_bignum": {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
        "badges": [x for x in [
            "MIỄN PHÍ", gh.get("license") or "OPEN SOURCE", "MÃ NGUỒN MỞ",
            (gh.get("lang") or "ĐA NỀN TẢNG").upper()] if x][:4],
    }


def compose(template_name, *, segments, headings, scene_data=None, kickers=None, lexicon=None):
    """Assemble a `content` dict for a template.

    segments  : list[str]  — display script, one per scene (RULE #1 display form)
    headings  : list[(h1, h2)] — 2-tone heading per scene
    scene_data: dict[int -> data] — component data per scene index (filled by repo_data_slots
                or hand-written for terminal/compare/steps)
    kickers   : dict[int -> str] — optional kicker overrides (else template kicker_hint)
    """
    scene_data = scene_data or {}
    kickers = kickers or {}
    scenes = []
    for i, (h1, h2) in enumerate(headings):
        sc = {"h1": h1, "h2": h2}
        if i in kickers:
            sc["kicker"] = kickers[i]
        if i in scene_data:
            sc["data"] = scene_data[i]
        scenes.append(sc)
    content = {"segments": segments, "scenes": scenes, "lexicon": lexicon or {}}

    # Validate the content contract before it reaches the renderer (fail fast with a
    # clear message; idea borrowed from the zod schema in AI-auto-generate-video).
    try:
        import os, sys
        sys.path.insert(0, os.path.dirname(__file__))
        import script_schema
        v = script_schema.validate_content(content)
        for w in v["warnings"]:
            print(f"[scene_composer] WARN: {w}")
        if not v["ok"]:
            raise ValueError("invalid content: " + "; ".join(v["errors"]))
    except ImportError:
        pass   # schema module optional — never block on its absence
    return content
