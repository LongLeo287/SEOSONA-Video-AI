# -*- coding: utf-8 -*-
"""Seedance 2.0 prompt-director — turn a script/scene idea into standalone cinematic AI-video prompts.

Encodes the Seedance 2.0 prompt GRAMMAR harvested from the vetted knowledge pack
(`2_KNOWLEDGE/seedance/` — 1 PDF guide + 2 Claude skills + 2 worked examples):

  · Global STYLE PREFIX (8K photoreal, contre-jour natural light, 60:30:10 colour) — pasted verbatim
    at the top of EVERY prompt so a copied prompt runs standalone in Seedance, no setup.
  · Block skeleton (never reorder): SUBJECT → LOCATION → [LAYOUT] → ACTION(timed SHOTs) →
    CAMERA(per-shot) → STYLE(60:30:10 for this shot) → CONSTRAINTS.
  · @tag Asset Registry (Seedance Elements) — every recurring person/prop/location gets an @tag +
    "matches input 100%"; @location is a STYLE REFERENCE ONLY, never a fixed keyframe.
  · FOV anchor table (degrees, discrete steps) + shot-size vocabulary + mixed camera language.
  · Consistency law: 1 prompt = ~15s (split long scenes Na/Nb/Nc), positive-only phrasing, camera
    always motivated, NO eye glow, slow-mo opt-in, avoid IP/real people/brands.

Output: standalone plain-text prompts (copy → paste into Seedance) + an editable shotlist HTML
deliverable (SEOSONA light brand) with checkboxes + copy buttons.

This module AUTHORS prompts deterministically (no external LLM required); an optional LLM enrich can
sharpen the acting/blocking language. It is the front-end for Engine #6 (`seedance_engine.py`), which
feeds these prompts to a Seedance provider when a key is configured.

  python 4_BRAIN/seedance_director.py --idea "a tired video editor pushing through a late-night edit"
  python 4_BRAIN/seedance_director.py --script beats.json --title "Toby Labs" --out out/shotlist.html
"""
import os
import sys
import json
import html
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ── The global Style Prefix (canonical, from the vetted guide). Pasted verbatim atop every prompt. ──
# Change only the Lighting/Color lines to re-tone (neon/studio); keep the rest for look consistency.
STYLE_PREFIX = (
    "Style: 8K cinematic. Photorealistic — no 3D render, no game engine, no game-cutscene aesthetic.\n"
    "Cinematography: naturalistic master cinematography.\n"
    "Lighting: Natural light only — contre-jour backlight, camera on shadow side, atmospheric haze. "
    "Key light from sky and windows only.\n"
    "Color: 60:30:10 — dominant / secondary / accent.\n"
    "Camera: Physical cine lens. 180° shutter motion blur.\n"
    "Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush, pore-shadow matching "
    "on-set light.\n"
    "Acting: top-tier cinematic — micro-pauses before reactions, precise eye-line, wet living eyes "
    "with catch-lights, visible breath and chest rise.\n"
    "Physics: Gravity and inertia respected — mass has real weight, correct contact shadows. "
    "No floating props.\n"
    "Composition: Rule of thirds + golden ratio. Every person moving from frame one.\n"
    "Continuity: Characters, props, environment identical across every cut. No identity drift.\n"
    "Technical: 24fps smooth motion. 8K detail. No jitter.\n"
    "Audio: Environmental SFX only. No music. No subtitles."
)

# ── FOV anchor table — discrete steps only (degrees for the prompt text, never mm, never arbitrary). ──
FOV_TABLE = [
    (180, "Fisheye — spherical distortion; POV, dream-state"),
    (107, "14–16mm ultra-wide — huge interiors, epic establish"),
    (84,  "20–24mm wide — establish, group blocking"),
    (63,  "28–35mm observational — reportage, wide observation"),
    (47,  "40–50mm neutral human perspective — universal establish, medium"),
    (29,  "75–85mm portrait compression — dialogue bust, medium-isolate"),
    (18,  "100–135mm natural portrait — close-portrait, identity-preserving"),
    (12,  "180–200mm tele-detail — hands, objects, detail-on-wide"),
    (8,   "300–400mm extreme compression — observation, broadcast"),
]
FOV_STEPS = [f for f, _ in FOV_TABLE]

# Shot-size → a sensible FOV default + a camera-move that motivates it. Mixed to keep rhythm rich.
SHOT_SIZES = {
    "EWS": (84, "establish"), "WS": (63, "wide"), "MS": (47, "medium"),
    "MCU": (29, "bust"), "CU": (18, "close"), "ECU": (12, "detail"),
}
# A rotation of motivated camera moves (the guide: mix locked-off / push-in / handheld / drone…).
CAMERA_MOVES = [
    ("over-the-shoulder, chest height, slow subtle push-in", "pulls us into the focus"),
    ("medium side profile, eye level, locked-off with a faint handheld breath", "lets the moment land"),
    ("front three-quarter, slightly low, slow drift back to neutral", "motivated by a shift in intent"),
    ("wide static, eye-level, locked off", "lets the space and silence sit"),
    ("low-angle dolly-in, waist to chest", "rises with the realization"),
    ("handheld follow from behind, camera lags half a beat", "we chase the subject through the space"),
]
CUT_TYPES = ("HARD CUT", "SMASH CUT", "MATCH CUT", "INSERT CUT")

# Consistency-law checklist keys (used by lint_prompt). Each maps to a human message.
_CHECKS = {
    "style_prefix": "Style Prefix pasted verbatim at the top",
    "subject": "SUBJECT block with @tag 'matches input 100%'",
    "location_ref": "LOCATION marked 'STYLE REFERENCE ONLY, not a keyframe'",
    "timecodes": "ACTION split into timed SHOTs ending in a cut",
    "camera": "CAMERA gives angle + height + movement + reason per shot",
    "palette": "STYLE gives a 60:30:10 palette for this shot",
    "constraints": "CONSTRAINTS has aspect ratio + NO eye glow",
}


def fov_for(shot_size):
    """Nearest legal FOV step for a shot size (defaults to a neutral 47°)."""
    return SHOT_SIZES.get(str(shot_size).upper(), (47, ""))[0]


def _tag(name):
    """Normalise an @tag: strip a leading @, lower-kebab, prefix @."""
    n = str(name or "").strip().lstrip("@").lower().replace(" ", "-")
    return "@" + n if n else ""


# ───────────────────────────── prompt assembly ─────────────────────────────

def build_prompt(scene, *, style_prefix=None):
    """Assemble ONE standalone 15-second Seedance 2.0 prompt from a scene dict.

    scene keys (all optional except subject+shots):
      subject   : str  — who/what is in frame (the acting goal + emotional beat)
      subject_tag / tags : an @tag (str) or {tag: description} for recurring elements
      wb        : int  — white balance Kelvin (default 5600)
      location  : str  — mood/architecture/light (rendered as STYLE REFERENCE ONLY)
      location_tag : str — @location element name
      layout_tag : str — @scheme aerial layout to lock positions (optional)
      intent    : str  — one-line action intent
      shots     : [ {t0,t1,size,beat,cut}, ... ]  — timed beats filling 15s
      camera    : [str,...]           — per-shot camera line (auto-filled if absent)
      palette   : {dom,sec,acc}       — 60/30/10 colour roles for this shot
      constraints : [str,...]         — extra hard rules (aspect/scale/continuity)
      aspect    : "16:9" | "9:16"     — default 16:9
    """
    sp = style_prefix or STYLE_PREFIX
    out = [sp, ""]

    # SUBJECT — @tag + goal + emotional beat + WB + MULTISHOT
    subj = str(scene.get("subject", "")).strip()
    stag = _tag(scene.get("subject_tag"))
    wb = int(scene.get("wb", 5600))
    subj_line = "SUBJECT — "
    if stag:
        subj_line += f"{stag} (matches input 100%), "
    subj_line += subj if subj else "the subject of this shot"
    subj_line += f". WB {wb}K. MULTISHOT."
    out.append(subj_line)
    out.append("")

    # LOCATION — style reference only
    loc = str(scene.get("location", "")).strip()
    ltag = _tag(scene.get("location_tag"))
    loc_line = "LOCATION — "
    if ltag:
        loc_line += f"{ltag} is a STYLE REFERENCE ONLY, not a fixed keyframe. "
    else:
        loc_line += "STYLE REFERENCE ONLY, not a fixed keyframe. "
    loc_line += (loc if loc else "the environment of this scene") + \
        ". The model may freely extend the world; the subject moves through the space — not pinned to the input frame."
    out.append(loc_line)
    out.append("")

    # LAYOUT (optional) — @scheme aerial layout to lock spatial positions across cuts
    laytag = _tag(scene.get("layout_tag"))
    if laytag:
        out.append(f"LAYOUT — use {laytag} (aerial layout) as the position reference so recurring "
                   f"elements stay in their exact place across cuts.")
        out.append("")

    # ACTION — one-line intent, then timed SHOTs filling 15s, each ending in a cut
    shots = list(scene.get("shots", []))
    intent = str(scene.get("intent", "")).strip() or "a single continuous beat"
    out.append(f"ACTION — {intent}.")
    cams = list(scene.get("camera", []))
    palette = scene.get("palette") or {}
    for i, sh in enumerate(shots):
        t0 = sh.get("t0", i * 5)
        t1 = sh.get("t1", min(15, t0 + 5))
        beat = str(sh.get("beat", "")).strip() or "the beat continues"
        cut = str(sh.get("cut", "HARD CUT")).strip()
        out.append(f"SHOT {i+1} (0:{int(t0):02d}–0:{int(t1):02d}) — {beat}. {cut}.")
    out.append("")

    # CAMERA — per shot: angle + height + lens (FOV°) + movement + motivation
    cam_parts = []
    for i, sh in enumerate(shots):
        size = str(sh.get("size", "MS")).upper()
        fov = sh.get("fov") or fov_for(size)
        if i < len(cams) and cams[i]:
            move, why = cams[i], ""
        else:
            move, why = CAMERA_MOVES[i % len(CAMERA_MOVES)]
        line = f"SHOT {i+1}: {size} at {fov}° FOV, {move}"
        if why:
            line += f" — {why}"
        line += "."
        cam_parts.append(line)
    out.append("CAMERA — " + " ".join(cam_parts))
    out.append("")

    # STYLE — 60:30:10 palette for this shot + WB + light reinforcement
    dom = palette.get("dom", "natural daylight neutrals")
    sec = palette.get("sec", "warm skin and wood tones")
    acc = palette.get("acc", "a single saturated accent")
    style_line = (f"STYLE — Dominant {dom} 60% / Secondary {sec} 30% / Accent {acc} 10%. WB {wb}K. "
                  f"Reinforce the key light (window/sun direction) and soft atmospheric haze.")
    out.append(style_line)
    out.append("")

    # CONSTRAINTS — aspect + slow-mo + scale/legibility + continuity + NO eye glow (always)
    aspect = scene.get("aspect", "16:9")
    hard = [aspect, "NO slow-motion" if not scene.get("slow_mo") else "SPEED-RAMPING only at the marked beat, then ramp back"]
    hard += list(scene.get("constraints", []))
    hard.append("human-scale props, normal size")
    hard.append("continuity held across all cuts (same face, wardrobe, props, light)")
    hard.append("NO eye glow")
    out.append("CONSTRAINTS — " + ". ".join(hard) + ".")

    return "\n".join(out).strip() + "\n"


def build_prose(scene):
    """A single natural-language descriptive prompt for prose-style video models (LTX-Video etc.).

    Seedance 2.0 wants the structured block prompt (build_prompt); LTX and most open t2v models want a
    plain descriptive sentence — the block directives (SUBJECT:/CAMERA:/CONSTRAINTS:) are noise to them.
    This distils the same scene into one vivid description + cinematic tail.
    """
    subj = str(scene.get("subject", "")).strip()
    loc = str(scene.get("location", "")).strip()
    shots = scene.get("shots", [])
    action = ""
    if shots:
        action = str(shots[0].get("beat", "")).strip()
        action = action.split("—")[-1].strip() if "—" in action else action
    # dedupe near-identical fragments (author_from_script sets subject == first-shot text → avoid repeat)
    parts, seen = [], []
    for p in [subj, loc, action]:
        pl = p.lower().strip()
        if p and not any(pl in s or s in pl for s in seen):
            parts.append(p); seen.append(pl)
    body = ", ".join(parts) if parts else str(scene.get("intent", "a cinematic scene"))
    tail = ("cinematic, photorealistic, natural light, shallow depth of field, "
            "slow gentle camera push-in, highly detailed, sharp focus")
    return f"{body}. {tail}."


def split_long(scene, total_seconds):
    """Split a >15s scene into standalone 15s sub-scenes (Na/Nb/Nc), each carrying continuity."""
    if total_seconds <= 15:
        return [scene]
    n = int((total_seconds + 14) // 15)
    shots = list(scene.get("shots", []))
    # distribute shots evenly across the n sub-scenes
    per = max(1, (len(shots) + n - 1) // n) if shots else 0
    subs = []
    for k in range(n):
        chunk = shots[k * per:(k + 1) * per] if shots else []
        if not chunk:                       # ensure each sub has at least a held beat
            chunk = [{"t0": 0, "t1": 15, "size": "MS",
                      "beat": scene.get("intent", "the beat holds")}]
        # renormalise timecodes to 0–15 within the sub-scene
        base = chunk[0].get("t0", 0)
        norm = [{**s, "t0": max(0, s.get("t0", 0) - base), "t1": min(15, s.get("t1", 15) - base)} for s in chunk]
        subs.append({**scene, "shots": norm, "_label": f"{scene.get('label','')}{chr(97+k)}"})
    return subs


# ───────────────────────────── deterministic authoring ─────────────────────────────

def author_from_script(title, beats, *, aspect="16:9"):
    """Turn a list of narration beats (strings, or {text,...}) into scene skeletons.

    Deterministic — one scene per beat, ~15s each, with a 3-shot arc (establish → develop → land) and
    a mixed camera plan. This is the honest no-LLM path; LLM enrich can sharpen the language later.
    """
    scenes = []
    for i, b in enumerate(beats):
        text = b.get("text", "") if isinstance(b, dict) else str(b)
        text = text.strip()
        if not text:
            continue
        extra = b if isinstance(b, dict) else {}
        # a generic 3-beat arc that fills 15s — the operator refines the concrete acting per shot
        sizes = ["WS", "MS", "MCU"] if i == 0 else ["MS", "MCU", "CU"]
        shots = [
            {"t0": 0,  "t1": 5,  "size": sizes[0], "beat": f"establish — {text}"},
            {"t0": 5,  "t1": 10, "size": sizes[1], "beat": "develop the moment — a concrete gesture, eye-line, a held micro-pause"},
            {"t0": 10, "t1": 15, "size": sizes[2], "beat": "land the beat — the smallest true reaction (a blink, a breath, a jaw shift)"},
        ]
        scenes.append({
            "label": str(i + 1),
            "desc": text,
            "subject": extra.get("subject") or text,
            "subject_tag": extra.get("subject_tag"),
            "location": extra.get("location", ""),
            "location_tag": extra.get("location_tag"),
            "intent": extra.get("intent", text),
            "wb": extra.get("wb", 5600),
            "palette": extra.get("palette", {}),
            "shots": extra.get("shots", shots),
            "aspect": aspect,
            "constraints": extra.get("constraints", []),
        })
    return {"title": title or "Untitled", "scenes": scenes}


def lint_prompt(text):
    """Return the list of consistency-law checks a prompt FAILS (empty = clean). Advisory."""
    t = text or ""
    fails = []
    if "Style: 8K" not in t and "STYLE PREFIX" not in t.upper():
        fails.append(_CHECKS["style_prefix"])
    if "SUBJECT —" not in t:
        fails.append(_CHECKS["subject"])
    if "STYLE REFERENCE ONLY" not in t:
        fails.append(_CHECKS["location_ref"])
    if "SHOT 1" not in t or not any(c in t for c in CUT_TYPES):
        fails.append(_CHECKS["timecodes"])
    if "° FOV" not in t and "FOV" not in t:
        fails.append(_CHECKS["camera"])
    if "60%" not in t or "10%" not in t:
        fails.append(_CHECKS["palette"])
    if "NO eye glow" not in t:
        fails.append(_CHECKS["constraints"])
    return fails


# ───────────────────────────── shotlist HTML deliverable ─────────────────────────────

def shotlist_html(title, scenes, *, style_prefix=None):
    """Editable shotlist HTML (SEOSONA light brand): checkbox per scene (localStorage), collapsible
    Style Prefix, copy-ready prompt block per shot. Self-contained (inline CSS/JS)."""
    sp = style_prefix or STYLE_PREFIX
    esc = html.escape

    scene_html = []
    for sc in scenes:
        label = esc(str(sc.get("label", "")))
        desc = esc(str(sc.get("desc", sc.get("subject", ""))))
        total = float(sc.get("duration", len(sc.get("shots", [])) * 5 or 15))
        subs = split_long(sc, total) if total > 15 else [sc]
        blocks = []
        for k, sub in enumerate(subs):
            plabel = f"{label}{chr(97+k)}" if len(subs) > 1 else label
            prompt = build_prompt(sub, style_prefix=sp)
            blocks.append(
                f'<div class="prompt-block"><div class="prompt-label">'
                f'<span>Prompt {esc(plabel)} · 15s</span>'
                f'<button class="copy-btn">Copy</button></div>'
                f'<pre class="prompt">{esc(prompt)}</pre></div>'
            )
        scene_html.append(
            f'<div class="scene"><div class="scene-header">'
            f'<input type="checkbox" data-scene="{label}">'
            f'<div class="scene-num">{label}.</div>'
            f'<div class="scene-desc">{desc}</div></div>'
            + "".join(blocks) + "</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Seedance Shotlist</title>
<style>
:root {{ --bg:#F6F8FD; --panel:#fff; --panel-2:#F0F3FB; --border:#DDE4F0; --text:#16224A;
  --text-dim:#5B6B8C; --accent:#2A5BDA; --coral:#E2724D; --done:#3BA55D; }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,"Segoe UI",system-ui,sans-serif;line-height:1.5;padding:32px 20px 80px}}
.container{{max-width:920px;margin:0 auto}}
h1{{font-size:26px;font-weight:700;margin:0 0 4px;letter-spacing:-.02em}}
.subtitle{{color:var(--text-dim);font-size:14px;margin-bottom:24px}}
.howto{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px 18px;font-size:13px;color:var(--text-dim);margin-bottom:20px}}
details.style-prefix{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin-bottom:24px}}
details.style-prefix summary{{cursor:pointer;font-weight:700;color:var(--accent);user-select:none}}
details.style-prefix pre{{margin:12px 0 0;padding:14px;background:var(--panel-2);border-radius:8px;font-family:"SF Mono",Consolas,monospace;font-size:12px;white-space:pre-wrap}}
.scene{{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:16px}}
.scene-header{{display:flex;align-items:flex-start;gap:12px;margin-bottom:12px}}
.scene-header input[type=checkbox]{{width:20px;height:20px;margin-top:2px;accent-color:var(--done);cursor:pointer;flex-shrink:0}}
.scene-num{{font-size:18px;font-weight:800;color:var(--accent);min-width:40px}}
.scene-desc{{font-size:15px;flex:1}}
.scene.done .scene-desc{{text-decoration:line-through;color:var(--text-dim)}}
.prompt-block{{background:var(--panel-2);border:1px solid var(--border);border-radius:8px;margin-top:10px;overflow:hidden}}
.prompt-label{{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-bottom:1px solid var(--border);font-size:12px;color:var(--text-dim);text-transform:uppercase;letter-spacing:.05em}}
.copy-btn{{background:transparent;color:var(--accent);border:1px solid var(--border);border-radius:6px;padding:4px 12px;font-size:11px;cursor:pointer;text-transform:uppercase;letter-spacing:.05em;font-family:inherit}}
.copy-btn:hover{{border-color:var(--accent)}}
.copy-btn.copied{{color:var(--done);border-color:var(--done)}}
pre.prompt{{margin:0;padding:14px 16px;font-family:"SF Mono",Consolas,monospace;font-size:12px;white-space:pre-wrap}}
</style></head><body><div class="container">
<h1>{esc(title)}</h1>
<div class="subtitle">Director's Shotlist · Seedance 2.0 · SEOSONA</div>
<div class="howto">Tick từng cảnh khi quay xong — tiến độ tự lưu. Bấm <b>Copy</b> để lấy nguyên prompt (đã kèm Style Prefix) dán thẳng vào Seedance.</div>
<details class="style-prefix"><summary>Global Style Prefix (áp cho mọi prompt)</summary><pre>{esc(sp)}</pre></details>
{''.join(scene_html)}
</div><script>
document.querySelectorAll('.scene input[type=checkbox]').forEach(cb=>{{
 const key='seedance-scene-'+cb.dataset.scene+'-done';
 if(localStorage.getItem(key)==='1'){{cb.checked=true;cb.closest('.scene').classList.add('done');}}
 cb.addEventListener('change',()=>{{localStorage.setItem(key,cb.checked?'1':'0');cb.closest('.scene').classList.toggle('done',cb.checked);}});
}});
document.querySelectorAll('.copy-btn').forEach(b=>{{
 b.addEventListener('click',()=>{{const p=b.closest('.prompt-block').querySelector('pre.prompt');
  navigator.clipboard.writeText(p.textContent).then(()=>{{b.classList.add('copied');const o=b.textContent;b.textContent='Copied';setTimeout(()=>{{b.classList.remove('copied');b.textContent=o;}},1400);}});}});
}});
</script></body></html>"""


def author_and_write(title, beats, out_html, *, aspect="16:9"):
    """Convenience: beats → shotlist HTML + a plain prompts.txt sidecar. Returns (html_path, txt_path)."""
    doc = author_from_script(title, beats, aspect=aspect)
    scenes = doc["scenes"]
    os.makedirs(os.path.dirname(os.path.abspath(out_html)) or ".", exist_ok=True)
    open(out_html, "w", encoding="utf-8").write(shotlist_html(doc["title"], scenes))
    txt = os.path.splitext(out_html)[0] + ".prompts.txt"
    with open(txt, "w", encoding="utf-8") as f:
        for sc in scenes:
            total = float(sc.get("duration", len(sc.get("shots", [])) * 5 or 15))
            for k, sub in enumerate(split_long(sc, total) if total > 15 else [sc]):
                lbl = f"{sc.get('label','')}{chr(97+k)}" if total > 15 else sc.get("label", "")
                f.write(f"===== SCENE {lbl} — {sc.get('desc','')} =====\n")
                f.write(build_prompt(sub) + "\n\n")
    return out_html, txt


def _self_check():
    """Headless smoke test: author a sample, assert prompts lint clean, write an HTML to scratch."""
    beats = [
        {"text": "a tired video editor pushing through the last edit of a long night",
         "subject": "a tired video editor in his early 30s, dark circles, stubble, a wrinkled hoodie",
         "subject_tag": "editor", "location_tag": "editing-room", "wb": 4800,
         "location": "a cramped dark editing suite, dual monitors glowing, one warm desk lamp",
         "palette": {"dom": "cool blue monitor glow", "sec": "warm desk-lamp amber", "acc": "deep shadow black"}},
        "he leans back, exhales, then commits to one more pass",
    ]
    doc = author_from_script("Self Check", beats)
    assert len(doc["scenes"]) == 2, "expected 2 scenes"
    p0 = build_prompt(doc["scenes"][0])
    fails = lint_prompt(p0)
    assert not fails, f"prompt failed lint: {fails}"
    assert "@editor (matches input 100%)" in p0
    assert "STYLE REFERENCE ONLY" in p0
    assert "° FOV" in p0 and "NO eye glow" in p0
    # long-scene split
    long_sc = {**doc["scenes"][0], "duration": 40}
    subs = split_long(long_sc, 40)
    assert len(subs) == 3, f"40s → 3 subs, got {len(subs)}"
    out = os.path.join(os.environ.get("TEMP", "."), "seedance_selfcheck.html")
    h, t = author_and_write("Self Check", beats, out)
    assert os.path.exists(h) and os.path.exists(t)
    print(f"[seedance_director] self-check OK | 2 scenes | prompt lint clean | split 40s->3 | html={h}")
    return True


def main():
    ap = argparse.ArgumentParser(description="Seedance 2.0 prompt-director — script → standalone prompts + shotlist HTML")
    ap.add_argument("--idea", help="a one-line idea → a single scene prompt printed to stdout")
    ap.add_argument("--script", help="beats.json (list of strings or {text,subject,...})")
    ap.add_argument("--title", default="Untitled")
    ap.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1"])
    ap.add_argument("--out", help="write an editable shotlist HTML here")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        _self_check(); return
    if a.idea:
        doc = author_from_script(a.title, [a.idea], aspect=a.aspect)
        print(build_prompt(doc["scenes"][0]))
        return
    if a.script:
        beats = json.load(open(a.script, encoding="utf-8"))
        out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.script)), "shotlist.html")
        h, t = author_and_write(a.title, beats, out, aspect=a.aspect)
        print(f"[seedance_director] wrote {h}\n[seedance_director] wrote {t}")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
