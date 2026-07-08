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


def _readme_digest(md):
    """Extract GROUNDED facts from a README so the script is built on REAL substance (not the 1-line
    desc → fabrication). Returns {overview, features[], install[], sections[], words}. All verbatim."""
    if not md:
        return {}
    import re as _re
    # strip badges/img/html/code-fence noise for prose extraction (keep code for install)
    body = _re.sub(r"<[^>]+>", " ", md)
    body = _re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)          # images
    body = _re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)        # links → text
    lines = [l.rstrip() for l in body.splitlines()]
    # overview = first 1-3 real prose sentences (skip headings/badges/blank)
    overview = ""
    for l in lines:
        s = l.strip()
        if len(s) > 40 and not s.startswith(("#", "-", "*", ">", "|", "`", "!")) and not s.lower().startswith(("http", "npm", "pip", "git ")):
            overview = s
            break
    # features = bullets, but heading-AWARE: a bullet under a Table-of-Contents / contributing / license
    # section is NAVIGATION or meta, NOT a tool feature. Grabbing all bullets flatly polluted features with
    # "Installation, Contributing, License" (TOC anchors → plain text after link-strip), mis-grounding the
    # script. Skip bullets whose current section is clearly non-feature.
    _skip_h = ("table of contents", "contents", "mục lục", "contributing", "contributor",
               "license", "acknowledg", "credits", "changelog", "sponsor")
    features, _cur = [], ""
    for l in lines:
        _h = _re.match(r"^#{1,6}\s+(.*)", l.strip())
        if _h:
            _cur = _h.group(1).lower().strip()
            continue
        if any(k in _cur for k in _skip_h):
            continue
        if _re.match(r"^\s*[\-\*]\s+\S", l) and 8 < len(l.strip()) < 140:
            features.append(_re.sub(r"^[\-\*]\s+", "", l.strip())[:120])
        if len(features) >= 12:
            break
    sections = [ _re.sub(r"^#+\s*", "", l.strip())[:60] for l in lines if _re.match(r"^#{1,3}\s+\S", l) ][:14]
    install = []
    for m in _re.finditer(r"```[a-z]*\n(.*?)```", md, _re.S):
        blk = m.group(1)
        for cl in blk.splitlines():
            cl = cl.strip().lstrip("$ ").strip()
            if _re.match(r"^(pip |pip3 |npm |npx |yarn |git clone|conda |docker |uv |poetry |cargo |go install|brew )", cl):
                install.append(cl[:120])
        if len(install) >= 6:
            break

    # Prose/steps under a heading matching any keyword (until the next heading) — this is the SUBSTANCE
    # that turns "lý thuyết suông" into real how-it-works / how-to-use / what-it's-for content.
    def _under(keywords, maxn=6):
        out, grab = [], False
        for l in lines:
            s = l.strip()
            h = _re.match(r"^#{1,4}\s+(.*)", s)
            if h:
                grab = any(k in h.group(1).lower() for k in keywords)
                continue
            if grab and s and not s.startswith(("|", "!", "<", "```")):
                cl = _re.sub(r"^[\-\*\d\.\)]+\s*", "", s).strip()
                if 6 < len(cl) < 180:
                    out.append(cl[:180])
            if len(out) >= maxn:
                break
        return out

    usage = _under(["how to use", "usage", "getting started", "quick start", "how it works", "example"], 6)
    use_cases = _under(["use case", "application", "who is", "why ", "what can", "perfect for"], 4)
    return {"overview": overview[:400], "features": features, "install": install[:6],
            "sections": sections, "usage": usage, "use_cases": use_cases, "words": len(body.split())}


def fetch_github(repo):
    """repo = 'owner/name' or a github URL → real metadata + README digest (free API, no key needed).
    The README digest (overview/features/install/sections) is the SUBSTANCE the script is grounded in —
    without it the writer only has a 1-line desc and fabricates."""
    repo = repo.strip().rstrip("/")
    if "github.com/" in repo:
        repo = repo.split("github.com/", 1)[1]
    repo = "/".join(repo.split("/")[:2])
    try:
        _res = subprocess.run(["gh", "api", f"repos/{repo}"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=30)   # bound it: an unattended
        # batch must not hang forever if `gh api` stalls (the README fetch below is already timeout=30).
        # TimeoutExpired is an Exception → caught below → returns an {"error":…} the caller aborts on.
        out = _res.stdout
        j = json.loads(out) if (out or "").strip() else {}
        # A 404 (missing/typo'd/deleted repo), 403/rate-limit, or auth failure makes `gh api` print the
        # ERROR BODY ({"message":"Not Found"}) to STDOUT — which json.loads accepts, so a hollow dict
        # (stars=0, desc="") would sail through WITHOUT an "error" key and the caller builds an EMPTY
        # video. Require a DEFINITIVE repo field; otherwise surface it as an error the caller aborts on.
        if _res.returncode != 0 or not (j.get("full_name") or j.get("id")):
            return {"error": (j.get("message") or (_res.stderr or "").strip() or "gh api failed")[:200],
                    "full": repo}
        stars = j.get("stargazers_count", 0)
        # REAL README (raw text) → the grounded knowledge source
        readme = ""
        try:
            readme = subprocess.run(["gh", "api", f"repos/{repo}/readme",
                                     "-H", "Accept: application/vnd.github.raw"],
                                    capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=30).stdout or ""
        except Exception:
            pass
        return {
            "owner": (j.get("owner") or {}).get("login", repo.split("/")[0]),
            "name": j.get("name", repo.split("/")[-1]),
            "full": j.get("full_name", repo),
            "desc": j.get("description") or "",
            "stars": stars,
            "stars_h": f"{stars:,}",
            "forks": j.get("forks_count", 0),
            "open_issues": j.get("open_issues_count", 0),
            "lang": j.get("language") or "",
            "license": ((j.get("license") or {}).get("spdx_id") or "").replace("NOASSERTION", ""),
            "topics": j.get("topics") or [],
            "url": j.get("html_url", f"https://github.com/{repo}"),
            "homepage": (j.get("homepage") or "").strip(),
            "readme": readme[:8000],
            "readme_facts": _readme_digest(readme),
        }
    except Exception as e:
        return {"error": str(e), "full": repo}


def repo_data_slots(gh, *, btn="Tải miễn phí", extra_tags=None):
    """Auto-build the repo-card / ★ bignum / license-badges data from GitHub metadata."""
    tags = [t for t in [gh.get("lang"), gh.get("license"), "Mã nguồn mở"] if t]
    tags += (extra_tags or [])
    # Defensive .get (a partial gh dict must NOT crash the render); stars_h falls back to the raw count.
    stars = gh.get("stars_h") or f"{gh.get('stars', 0):,}"
    return {
        "repo": {"owner": gh.get("owner", ""), "name": gh.get("name") or gh.get("full", ""),
                 "stars": stars, "desc": gh.get("desc", ""), "tags": tags[:4], "btn": btn},
        "stars_bignum": {"big": stars, "label": "★  GITHUB STARS"},
        # lang badge ONLY when a real language is detected — the old "ĐA NỀN TẢNG" (cross-platform) fallback
        # was an UNSUPPORTED claim (a missing language ≠ cross-platform). Show fewer badges, not a fake one.
        "badges": [x for x in [
            "MIỄN PHÍ", gh.get("license") or "OPEN SOURCE", "MÃ NGUỒN MỞ",
            (gh.get("lang") or "").upper()] if x][:4],
    }


def compose(template_name, *, segments, headings, scene_data=None, kickers=None, lexicon=None,
            comp_overrides=None):
    """Assemble a `content` dict for a template.

    segments  : list[str]  — display script, one per scene (RULE #1 display form)
    headings  : list[(h1, h2)] — 2-tone heading per scene
    scene_data: dict[int -> data] — component data per scene index (filled by repo_data_slots
                or hand-written for terminal/compare/steps)
    kickers   : dict[int -> str] — optional kicker overrides (else template kicker_hint)
    """
    scene_data = scene_data or {}
    kickers = kickers or {}
    comp_overrides = comp_overrides or {}
    scenes = []
    for i, (h1, h2) in enumerate(headings):
        sc = {"h1": h1, "h2": h2}
        if i in kickers:
            sc["kicker"] = kickers[i]
        if i in scene_data:
            sc["data"] = scene_data[i]
        if i in comp_overrides:                  # let content swap a scene's component (e.g. inject a 2nd shot)
            sc["comp_override"] = comp_overrides[i]
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
