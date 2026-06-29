# -*- coding: utf-8 -*-
"""SEOSONA Native Composer — the brand video engine (HyperFrames-native).

Replaces the old hand-built `_write_hyperframes_render_project`. Given a list of
display `segments` (script) + `scenes` (kicker / 2-tone heading / component+data),
it: generates the VieNeu male voice, times captions to DISPLAY words (SOP RULE #1),
builds a SEOSONA-brand HyperFrames composition (persistent logo, kicker pill,
2-tone heading, rich components, footer, karaoke pill, CTA outro), renders natively,
then mixes SFX + normalises loudness.

Reuses the existing, working stack: voice_router/vieneu_engine, srt_maker.asr_router,
news_video_standards (display↔pronunciation + RULE #1 alignment).
"""
import os, sys, json, shutil, subprocess, html, re, time

# Vietnamese voice names / captions are printed during a render. On a non-UTF-8
# Windows console (cp1252) those prints raise UnicodeEncodeError and kill the
# render. Force UTF-8 on our streams so a render never dies on a log line.
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if os.path.dirname(__file__) not in sys.path: sys.path.insert(0, os.path.dirname(__file__))
import news_video_standards as nvs

# ---------------------------------------------------------------- brand kit
# Sampled from the SEOSONA brand carousel (7_ASSETS/brand/SEOSONA/*.jpg):
# primary blue #2A5BDA, coral accent #E2724D, logo green #16A34A. Light mode only.
BLUE, GREEN, ORANGE = "#2A5BDA", "#16A34A", "#E2724D"
BRAND = {
    "logo": "7_ASSETS/brand/logos/Seosona_Logo.png",
    "bgm": "7_ASSETS/audio/bgm/bgm_tech_ambient.mp3",
    "footer": ('<span class="dotg">●</span> <span class="b1">SEOSONA AI</span>'
               '<span class="sep">·</span> <span class="b2">Share to be shared more</span>'),
    "accents": {"blue": BLUE, "green": GREEN, "orange": ORANGE},
    "ink": "#0F172A",
}
FONTS = [("BVP-Black.ttf", 900, "Black"), ("BVP-XBold.ttf", 800, "ExtraBold"),
         ("BVP-Bold.ttf", 700, "Bold"), ("BVP-SemiBold.ttf", 600, "SemiBold"),
         ("BVP-Medium.ttf", 500, "Medium")]

# Per-brand footer line (logo + voice come from system_config.yaml profile). Light
# mode + the tuned accent palette are shared by both brands (brand law).
FOOTERS = {
    "seosona": BRAND["footer"],
    "cqa": ('<span class="dotg">●</span> <span class="b1">Chi Quyết Academy</span>'
            '<span class="sep">·</span> <span class="b2">Học SEO thực chiến</span>'),
}


def _load_profile(brand="seosona"):
    """Read the brand profile (logo + voice config) from system_config.yaml.
    Falls back to a SEOSONA-shaped default if the file/brand is missing — the
    engine must never crash on a config gap."""
    default = {"logo": "Seosona_Logo.png",
               "voice": {"engine": "vieneu", "model": "Gia Bảo",
                         "reference_audio": "",  # news = stable preset, NOT a clone (clone = CQA only)
                         "required_gender": "male", "required_accent": "southern",
                         "fallback_voice": "vi-VN-NamMinhNeural"}}
    try:
        import yaml
        with open(os.path.join(ROOT, "system_config.yaml"), encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return (cfg.get("profiles", {}) or {}).get(brand, default) or default
    except Exception as e:
        print(f"[native_composer] profile load failed ({e}); using SEOSONA default.")
        return default


def _esc(s): return html.escape(str(s))
def _hf_cli(): return os.path.join(ROOT, "node_modules", "hyperframes", "dist", "cli.js")


def _resolve_bin(name):
    """Absolute path to ffmpeg/ffprobe. Prefer the bundled node binaries (always
    present after npm install), then the vendored ffmpeg build, then PATH. The
    HyperFrames node renderer + our mix step both need a concrete path because
    ffmpeg may only be on the MSYS/bash PATH, not the Windows PATH node/python see."""
    exe = name + (".exe" if os.name == "nt" else "")
    candidates = [
        os.path.join(ROOT, "node_modules", f"{name}-static", exe),                 # ffmpeg-static
        os.path.join(ROOT, "node_modules", f"{name}-static", "bin", "win32", "x64", exe),  # ffprobe-static
    ]
    import glob as _glob
    candidates += _glob.glob(os.path.join(ROOT, "ffmpeg", "**", "bin", exe), recursive=True)
    for c in candidates:
        if os.path.exists(c):
            return c
    return name  # fall back to PATH lookup


def _ffmpeg_bin(): return _resolve_bin("ffmpeg")
def _ffprobe_bin(): return _resolve_bin("ffprobe")


def _render_env():
    """Env for the HyperFrames render subprocess: point it at concrete ffmpeg/ffprobe."""
    env = dict(os.environ)
    env["HYPERFRAMES_FFMPEG_PATH"] = _ffmpeg_bin()
    env["HYPERFRAMES_FFPROBE_PATH"] = _ffprobe_bin()
    return env

# ---------------------------------------------------------------- SFX library
# Curated from the "Sound Effects Pack" by scripts/build_sfx_library.sh.
# Mixed per-component at scene timestamps so the video feels produced like the
# reference videos (whoosh on cut, impact on a number, keys under a terminal).
SFX_DIR = os.path.join(ROOT, "7_ASSETS", "audio", "sfx")
SFX = {
    # 6 transition variants rotate across cuts so no two consecutive sound alike
    "transition": ["transition/swish_01.mp3", "transition/whoosh_01.mp3", "transition/swish_03.mp3",
                   "transition/swish_02.mp3", "transition/whoosh_02.mp3", "transition/whoosh_03.mp3"],
    "impact_soft": "impact/impact_soft.mp3", "impact_deep": "impact/impact_deep.mp3",
    "impact_hit": "impact/impact_hit.mp3",
    "ui_positive": "ui/positive.mp3", "ui_click": "ui/click.mp3", "ui_success": "ui/success.mp3",
    "ui_pop": "ui/pop.mp3", "ui_notify": "ui/notify.mp3",
    "typing": "typing/keyboard.mp3",
    "riser_short": "riser/riser_short.mp3", "riser_long": "riser/riser_long.mp3",
}
# component kind -> (sfx key, volume, lead-seconds-before-reveal). Distinct sounds per
# component so a video's SFX palette is varied, not one beep repeated.
_COMP_SFX = {
    "bignum":  ("impact_deep", 0.46, 0.05),
    "repo":    ("impact_soft", 0.40, 0.05),
    "badges":  ("ui_success", 0.42, 0.0),
    "cta":     ("ui_success", 0.5, 0.0),
    "steps":   ("ui_pop", 0.42, 0.0),
    "compare": ("ui_click", 0.38, 0.0),
    "stats":   ("impact_hit", 0.44, 0.05),
    "quote":   ("ui_positive", 0.3, 0.0),
    "tip":     ("ui_notify", 0.4, 0.0),
    "feature": ("ui_pop", 0.42, 0.0),
    "chart":   ("impact_soft", 0.42, 0.05),
    "mockup":  ("ui_pop", 0.42, 0.0),
}

def _sfx(key_or_rel):
    rel = SFX.get(key_or_rel, key_or_rel)
    return os.path.join(SFX_DIR, rel)

# ---------------------------------------------------------------- BGM (by mood)
# Drop royalty-free / licensed tracks here, one per mood. IMPORTANT: viral/chart
# songs are copyrighted — muxing them into the file risks mute/takedown (esp. Ads);
# prefer the platform's native sound library for those. BGM is ducked under the
# voice at mix time (sidechain), so narration always stays clear.
BGM_DIR = os.path.join(ROOT, "7_ASSETS", "audio", "bgm")
BGM = {"tech": "bgm_tech_ambient.mp3", "news": "bgm_news.mp3",
       "insight": "bgm_insight.mp3", "upbeat": "bgm_upbeat.mp3",
       "default": "bgm_tech_ambient.mp3"}

def _bgm(mood="tech"):
    p = os.path.join(BGM_DIR, BGM.get(mood, BGM["default"]))
    return p if os.path.exists(p) else os.path.join(BGM_DIR, BGM["default"])

# ---------------------------------------------------------------- progressive reveal
# Multi-item components reveal item-by-item (build-on) as the scene plays, each with a
# pop SFX — instead of showing everything at once.
def _reveal_count(comp):
    if not comp: return 0
    kind, d = comp
    if kind in ("steps", "feature", "badges", "chart"): return len(d.get("items", []))
    if kind == "stats": return len(d.get("items", [])[:3])
    if kind == "mockup": return len(d.get("tiles", [])) if d.get("tiles") else 0
    if kind == "compare":
        return len(d.get("left", (None, []))[1]) + len(d.get("right", (None, []))[1])
    return 0

def _reveal_plan(st, en, n):
    """Return (start, interval, times[]) spreading n item-reveals across the scene span."""
    if n < 2: return None
    start = st + 0.45
    span = max(0.6, (en - st) - 0.8)
    interval = min(0.55, max(0.22, span / n))
    return start, interval, [round(start + j * interval, 3) for j in range(n)]

def _sfx_cues(groups, scenes, TOTAL):
    """Build (time, file, volume) SFX cues from scene timing + component kinds.
    - transition swish/whoosh at every scene change (alternating)
    - per-component accent (impact on bignum, ui on badges/cta, click on steps)
    - keyboard bed under a terminal scene
    - a short riser lifting into scene 0's hook
    Returns [] gracefully if a cue file is missing (SFX stays optional)."""
    cues = []
    SFX_GAIN = 0.6   # global SFX level — keep accents subtle under the voice (not loud)
    def add(t, key, vol):
        p = _sfx(key)
        if os.path.exists(p): cues.append((max(0.0, round(t, 3)), p, round(vol * SFX_GAIN, 3)))
    for i, sc in enumerate(scenes):
        grp = groups[i] if i < len(groups) else []
        if not grp: continue
        st = grp[0]["start"]
        if i == 0:
            add(0.0, "riser_short", 0.3)            # subtle lift into the hook
        else:
            key = SFX["transition"][(i - 1) % len(SFX["transition"])]
            add(st - 0.15, key, 0.42)               # whoosh/swish on the cut
        comp = sc.get("comp")
        kind = comp[0] if comp else None
        reveal = st + (0.0 if i == 0 else 0.24)     # .comp tween lands at st+0.24
        en = grp[-1]["end"]
        n = _reveal_count(comp)
        plan = _reveal_plan(st, en, n)
        if kind == "terminal":
            add(reveal, "typing", 0.22)             # keyboard bed
        elif plan:                                  # build-on list: a soft pop per item
            for t in plan[2]:
                add(t, "ui_pop", 0.34)
        elif kind in _COMP_SFX:
            key, vol, lead = _COMP_SFX[kind]
            add(reveal - lead, key, vol)
    return cues

# ---------------------------------------------------------------- components
_BIGNUM_RE = re.compile(r'^(\D*?)(\d[\d.,]*)(.*)$', re.S)

def _split_bignum(s):
    """Split a bignum value into (prefix, numeric-core, suffix) so the numeric part can
    be COUNTED UP at render time (Recipe 1, the money-counter idea). Returns None when
    there's no countable number (e.g. "Google + AI") — those keep the plain pop only.
    Examples: "5 bước"→("","5"," bước") · "$10K"→("$","10","K") · "80%"→("","80","%")."""
    m = _BIGNUM_RE.match(str(s))
    if not m:
        return None
    pre, num, post = m.group(1), m.group(2), m.group(3)
    core = num.replace(",", "")
    try:
        val = float(core)
    except ValueError:
        return None
    if val < 2:                       # ticking to 0/1 reads as a glitch, not a count-up
        return None
    decimals = len(core.split(".")[1]) if "." in core else 0
    return {"pre": pre, "num": num, "post": post,
            "target": val, "decimals": decimals, "comma": ("," in num or val >= 1000)}


def _component(kind, d, acc, pal=None):
    if pal is None:
        pal = ACCENT_PALETTE["seosona"]
    if kind == "bignum":
        # Recipe 1: pair the number with an accent-tinted radial glow so it has visual
        # weight instead of floating in empty space (craft/data-in-motion.md). The glow +
        # the entrance pop + a count-up (numeric values) are animated in the tween loop.
        spec = _split_bignum(d["big"])
        if spec:   # render the number as a span starting at 0 — the tween ticks it to target
            inner = f'{_esc(spec["pre"])}<span class="bn-num">0</span>{_esc(spec["post"])}'
        else:
            inner = _esc(d["big"])
        return (f'<div class="c-bignum"><div class="bgglow" style="background:radial-gradient(circle,{acc}29 0%,transparent 68%)"></div>'
                f'<div class="big" style="color:{acc}">{inner}</div><div class="biglabel">{_esc(d["label"])}</div></div>')
    if kind == "repo":
        tags = "".join(f'<span class="tag">{_esc(t)}</span>' for t in d.get("tags", []))
        return (f'<div class="c-repo"><div class="repo-top"><div class="gh">◉</div>'
                f'<div class="repo-name"><b>{_esc(d["owner"])}</b> / {_esc(d["name"])}</div>'
                f'<div class="stars" style="background:{acc}">★ {_esc(d["stars"])}</div></div>'
                f'<div class="repo-desc">{_esc(d["desc"])}</div><div class="tags">{tags}</div>'
                f'<div class="repo-btn" style="background:{acc}">{_esc(d.get("btn","Xem ngay"))}</div></div>')
    if kind == "compare":
        # Bad side = coral (var(--coral)); winner side = brand blue (pal["blue"]) so CQA
        # renders #4A60E9 and SEOSONA renders #2A5BDA, not the same hardcoded color.
        lt, li = d["left"]; rt, ri = d["right"]
        lrows = "".join(f'<div class="crow x ritem">✕ {_esc(x)}</div>' for x in li)
        rrows = "".join(f'<div class="crow v ritem" style="color:{pal["blue"]}">✓ {_esc(x)}</div>' for x in ri)
        return (f'<div class="c-compare"><div class="col bad"><div class="ctitle bad">{_esc(lt)}</div>{lrows}</div>'
                f'<div class="col hi" style="border-color:{pal["blue"]}"><div class="ctitle" style="color:{pal["blue"]}">{_esc(rt)}</div>{rrows}</div></div>')
    if kind == "terminal":
        rows = ""
        for k2, txt in d["lines"]:
            if k2 == "$": rows += f'<div class="tline"><span class="prompt">$</span> {_esc(txt)}</div>'
            else: rows += f'<div class="tline ok" style="color:{acc}">✓ {_esc(txt)}</div>'
        return (f'<div class="c-term"><div class="term-bar"><span class="dot r"></span><span class="dot y"></span>'
                f'<span class="dot g"></span><span class="term-title">{_esc(d.get("title","~/seosona"))}</span></div>'
                f'<div class="term-body">{rows}</div></div>')
    if kind == "steps":
        rows = "".join(f'<div class="step ritem"><span class="snum" style="background:{acc}">{i+1}</span>'
                       f'<div><b>{_esc(t)}</b><span>{_esc(s)}</span></div></div>' for i,(t,s) in enumerate(d["items"]))
        return f'<div class="c-steps">{rows}</div>'
    if kind == "badges":
        return '<div class="c-badges">' + "".join(
            f'<span class="badge ritem" style="border-color:{acc};color:{acc}">{_esc(x)}</span>' for x in d["items"]) + '</div>'
    if kind == "stats":
        # up to 3 number cards side by side. data: {"items":[(num,label), ...]}
        cells = "".join(f'<div class="stat ritem"><div class="stnum" style="color:{acc}">{_esc(n)}</div>'
                        f'<div class="stlab">{_esc(l)}</div></div>' for n, l in d["items"][:3])
        return f'<div class="c-stats">{cells}</div>'
    if kind == "quote":
        # big pull-quote for opinion/insight videos. data: {"text":..., "by":...}
        by = f'<div class="qby">— {_esc(d["by"])}</div>' if d.get("by") else ""
        return (f'<div class="c-quote"><div class="qmark" style="color:{acc}">&#8220;</div>'
                f'<div class="qtext">{_esc(d["text"])}</div>{by}</div>')
    if kind == "tip":
        # 💡 callout box for the key takeaway. data: {"text":...} or {"title":..,"text":..}
        title = f'<div class="tiptitle" style="color:{acc}">{_esc(d["title"])}</div>' if d.get("title") else ""
        return (f'<div class="c-tip" style="border-color:{acc}"><div class="tipicon">&#128161;</div>'
                f'<div>{title}<div class="tiptext">{_esc(d["text"])}</div></div></div>')
    if kind == "feature":
        # emoji/icon + title (+sub) grid — more visual than steps. data: {"items":[(emoji,title,sub),...]}
        rows = "".join(f'<div class="feat ritem"><span class="femoji">{_esc(e)}</span>'
                       f'<div><b>{_esc(t)}</b>{("<span>"+_esc(s)+"</span>") if s else ""}</div></div>'
                       for e, t, s in d["items"])
        return f'<div class="c-feature">{rows}</div>'
    if kind == "chart":
        # horizontal bar chart (data viz). data: {"title":.., "items":[(label, pct0-100, disp), ...]}
        # disp optional (text shown on the bar); each bar can have its own color via 4th elem.
        cols = [acc, pal["green"], pal["orange"], pal["blue"]]
        rows = ""
        for i, it in enumerate(d["items"]):
            lab, pct = it[0], max(3, min(100, float(it[1])))
            disp = it[2] if len(it) > 2 else f"{int(it[1])}%"
            col = it[3] if len(it) > 3 else cols[i % len(cols)]
            rows += (f'<div class="chrow ritem"><div class="chlab">{_esc(lab)}</div>'
                     f'<div class="chtrack"><div class="chfill" style="width:{pct:.0f}%;background:{col}">'
                     f'<span class="chval">{_esc(disp)}</span></div></div></div>')
        title = f'<div class="chtitle">{_esc(d["title"])}</div>' if d.get("title") else ""
        return f'<div class="c-chart">{title}{rows}</div>'
    if kind == "mockup":
        # browser/app window chrome — looks like a real screenshot/dashboard.
        # data: {"url":"site.com", "tiles":[(num,label),...]} (mini-dashboard)  OR
        #       {"url":.., "lines":["...", ...]} (content rows)
        url = d.get("url", "seosona.ai")
        if d.get("tiles"):
            body = '<div class="mktiles">' + "".join(
                f'<div class="mktile ritem"><div class="mktnum" style="color:{acc}">{_esc(n)}</div>'
                f'<div class="mktlab">{_esc(l)}</div></div>' for n, l in d["tiles"][:4]) + '</div>'
        else:
            body = '<div class="mklines">' + "".join(f'<div class="mkline">{_esc(x)}</div>' for x in d.get("lines", [])) + '</div>'
        return (f'<div class="c-mockup"><div class="mkbar"><span class="mkdot r"></span>'
                f'<span class="mkdot y"></span><span class="mkdot g"></span>'
                f'<span class="mkaddr">{_esc(url)}</span></div><div class="mkbody">{body}</div></div>')
    if kind == "cta":
        return (f'<div class="c-cta"><img class="cta-logo" src="assets/logo.png"/>'
                f'<div class="cta-line">{_esc(d.get("line","Theo dõi SEOSONA để xem thêm"))}</div>'
                f'<div class="cta-btn" style="background:{acc}">{_esc(d.get("btn","👉 Theo dõi ngay"))}</div></div>')
    if kind == "gittree":
        # Git commit graph rendered as a vertical `git log --graph` — pure text/flow
        # (colored dots on a connector line, commit id, branch tag, HEAD badge). Built
        # this way ON PURPOSE: absolutely-positioned / SVG / image content does NOT
        # composite inside a scene in the HyperFrames pipeline, but normal-flow text
        # (like the terminal/steps cards) always renders. Newest commit on top.
        # data: {commits:[{id,x,y,branch}], branches:{name:color}, head:id}
        bcol = d.get("branches", {})
        commits = sorted(d["commits"], key=lambda c: c.get("x", 0), reverse=True)
        rows = ""
        for c in commits:
            col = bcol.get(c["branch"], acc)
            head = '<span class="glhead">HEAD</span>' if c["id"] == d.get("head") else ""
            rows += (f'<div class="glrow"><span class="gldot" style="background:{col}"></span>'
                     f'<b class="glid">{_esc(c["id"])}</b>'
                     f'<span class="gltag" style="color:{col};background:{col}1f">{_esc(c["branch"])}</span>{head}</div>')
        return (f'<div class="c-gitlog"><div class="gltitle"><span class="glprompt">$</span> git log --graph</div>'
                f'<div class="glrows">{rows}</div></div>')
    return ""


# ---------------------------------------------------------------- CSS
# LIGHT MODE ONLY — brand-accurate tokens sampled from the SEOSONA carousel:
# soft blue-tinted bg, navy ink, white cards on a light-blue border, coral-tinted
# "before" card + blue-tinted "after" card for compare, navy karaoke pill.
THEMES = {
    # SEOSONA — professional, blue-tinted (sampled from the brand carousel).
    "seosona": {"bg": "radial-gradient(125% 80% at 50% 0%,#EDF3FB 0%,#F5F9FF 45%,#FFFFFF 100%)",
              "ink": "#16224A", "ink2": "#3A4A6B", "muted": "#6B7A99", "card": "#ffffff",
              "cardb": "#E3E9F5", "tagbg": "#EEF3FC", "tagtx": "#3A4A6B", "dots": "#CBD8F0",
              "footerbg": "#ffffff", "footertx": "#3A4A6B", "kara": "#16224A", "karatx": "#FFFFFF",
              "ghbg": "#16224A", "ghtx": "#ffffff", "fb": "#2A5BDA", "dotc": "#16A34A",
              "coral": "#E2724D", "badbg": "#FFF7F4", "badbd": "#F4D6CC", "hibg": "#EEF3FC"},
    # CQA (Chi Quyết Academy) — fun, creator-focused, indigo. Still 100% light mode.
    "cqa": {"bg": "radial-gradient(125% 80% at 50% 0%,#E9EDFF 0%,#F4F7FF 45%,#FFFFFF 100%)",
              "ink": "#1A1D2B", "ink2": "#3A3F55", "muted": "#6B7088", "card": "#ffffff",
              "cardb": "#E4E8F7", "tagbg": "#EEF1FE", "tagtx": "#3A3F55", "dots": "#C9D2F2",
              "footerbg": "#ffffff", "footertx": "#3A3F55", "kara": "#1A1D2B", "karatx": "#FFFFFF",
              "ghbg": "#1A1D2B", "ghtx": "#ffffff", "fb": "#4A60E9", "dotc": "#10B981",
              "coral": "#FB7185", "badbg": "#FFF5F6", "badbd": "#FBD5DB", "hibg": "#EEF1FE"},
}
THEMES["light"] = THEMES["seosona"]   # back-compat alias (the `theme` arg is always light-mode)
ACCENT_PALETTE = {
    "seosona": {"blue": "#2A5BDA", "green": "#16A34A", "orange": "#E2724D"},
    "cqa":     {"blue": "#4A60E9", "green": "#10B981", "orange": "#F59E0B"},
}


def _theme(brand="seosona"):
    """Light-mode token set for a brand (falls back to SEOSONA)."""
    return THEMES.get(brand, THEMES["seosona"])


def _resolve_acc(acc, brand="seosona"):
    """Accent role ('blue'/'green'/'orange') -> brand hex; a raw hex passes through.
    Light mode only; the actual palette is chosen by BRAND (SEOSONA vs CQA)."""
    return ACCENT_PALETTE.get(brand, ACCENT_PALETTE["seosona"]).get(acc, acc)


_ACC_ORDER = ["blue", "green", "orange"]
def _rotate_acc(role, shift):
    """Rotate an accent ROLE by shift (0..2) so the SAME template renders with a
    different colour scheme per video → videos don't look identical. Deterministic."""
    if shift and role in _ACC_ORDER:
        return _ACC_ORDER[(_ACC_ORDER.index(role) + shift) % 3]
    return role


def _auto_shift(output):
    """Derive a stable 0..2 accent shift from the output name (per-topic variety)."""
    base = os.path.basename(output or "")
    return (sum(ord(c) for c in base) % 3) if base else 0


def _css(brand="seosona", W=1080, H=1920):
    t = _theme(brand)
    faces = "".join(f"@font-face{{font-family:BVP;src:url('assets/{f}');font-weight:{w}}}" for f,w,_ in FONTS)
    vars_ = ";".join(f"--{k}:{v}" for k, v in t.items())
    css = faces + "\n*{margin:0;padding:0;box-sizing:border-box;font-family:BVP,Arial,sans-serif}\n" + \
        "#root{" + vars_ + ";width:1080px;height:1920px;position:relative;overflow:hidden;background:var(--bg);color:var(--ink)}\n" + """
.dots{position:absolute;inset:0;background-image:radial-gradient(var(--dots) 1.4px,transparent 1.4px);background-size:42px 42px;opacity:.30}
.brandlogo{position:absolute;top:60px;left:72px;width:300px;z-index:60}
.scene{position:absolute;left:0;top:0;width:1080px;height:1920px;padding:230px 80px 470px;display:flex;flex-direction:column;align-items:center}
/* Ambient background depth (house-style.md "Background is not empty"): a breathing
   accent glow + an oversized faint ghost word behind the content. z-index keeps them
   under the text. */
.scbg{position:absolute;inset:0;z-index:0;overflow:hidden;pointer-events:none}
.scglow{position:absolute;left:50%;top:34%;width:1000px;height:1000px;transform:translate(-50%,-50%);border-radius:50%}
.scghost{position:absolute;left:50%;top:58%;transform:translateX(-50%);font-weight:900;font-size:300px;line-height:1;white-space:nowrap;letter-spacing:-6px;text-transform:uppercase}
.scene>.kicker,.scene>.head,.scene>.comp{position:relative;z-index:1}
.kicker{font-weight:800;font-size:30px;letter-spacing:3px;padding:14px 30px;border-radius:999px;text-transform:uppercase}
.head{margin-top:38px;text-align:center;line-height:1.08}
.head .l1{display:block;font-weight:900;font-size:80px;letter-spacing:-1px}
.head .l2{display:inline-block;position:relative;font-weight:900;font-size:80px;letter-spacing:-1px}
.l2u{position:absolute;left:2px;right:2px;bottom:-14px;height:8px;border-radius:4px;transform:scaleX(0);transform-origin:left center}
.comp{margin-top:64px;width:100%;display:flex;justify-content:center}
.c-bignum{text-align:center;position:relative}.c-bignum .big{font-weight:900;font-size:225px;line-height:1;letter-spacing:-4px;position:relative;z-index:1}
.c-bignum .bgglow{position:absolute;left:50%;top:44%;width:780px;height:780px;transform:translate(-50%,-50%);border-radius:50%;z-index:0;pointer-events:none}
.c-bignum .biglabel{margin-top:18px;font-weight:800;font-size:34px;letter-spacing:2px;color:var(--muted);position:relative;z-index:1}
.scene.hero .head .l1{color:#fff}
.scene.hero .c-bignum .big{color:#fff!important}
.scene.hero .c-bignum .biglabel{color:#ffffffd9}
.c-repo{width:880px;background:var(--card);border:1px solid var(--cardb);border-radius:34px;padding:48px;box-shadow:0 30px 70px rgba(20,40,90,.10)}
.repo-top{display:flex;align-items:center;gap:20px}
.gh{width:64px;height:64px;border-radius:16px;background:var(--ghbg);color:var(--ghtx);font-size:38px;display:flex;align-items:center;justify-content:center}
.repo-name{font-size:38px;font-weight:600;flex:1;color:var(--ink)}.repo-name b{font-weight:800}
.stars{color:#fff;font-weight:800;font-size:30px;padding:12px 22px;border-radius:999px}
.repo-desc{margin-top:30px;font-size:34px;font-weight:500;color:var(--ink2);line-height:1.4}
.tags{margin-top:30px;display:flex;flex-wrap:wrap;gap:16px}
.tag{background:var(--tagbg);color:var(--tagtx);font-weight:700;font-size:27px;padding:12px 24px;border-radius:14px}
.repo-btn{margin-top:38px;color:#fff;font-weight:800;font-size:34px;text-align:center;padding:24px;border-radius:18px}
.c-compare{display:flex;gap:30px;width:900px}
.col{flex:1;background:var(--card);border:1px solid var(--cardb);border-radius:28px;padding:40px 34px}
.col.bad{background:var(--badbg);border:2px solid var(--badbd)}
.col.hi{border-width:3px;background:var(--hibg);box-shadow:0 24px 60px rgba(42,91,218,.14)}
.ctitle{font-weight:900;font-size:40px;margin-bottom:24px;color:var(--ink)}.ctitle.bad{color:var(--coral)}
.crow{font-weight:600;font-size:32px;margin:18px 0;line-height:1.3;color:var(--ink2)}.crow.x{color:var(--coral)}
.c-term{width:900px;background:#0B1220;border-radius:26px;overflow:hidden;box-shadow:0 30px 70px rgba(8,15,35,.30)}
.term-bar{background:#161E2E;padding:22px 28px;display:flex;align-items:center;gap:14px}
.dot{width:20px;height:20px;border-radius:50%}.dot.r{background:#FF5F57}.dot.y{background:#FEBC2E}.dot.g{background:#28C840}
.term-title{color:#7C8AA5;font-weight:700;font-size:28px;margin-left:14px}
.term-body{padding:40px 38px;font-family:monospace}
.tline{color:#D6DEEC;font-size:33px;margin:18px 0;font-weight:500}.prompt{color:#5B8CFF;font-weight:800}.tline.ok{font-weight:800}
.c-steps{width:880px;display:flex;flex-direction:column;gap:26px}
.step{display:flex;align-items:center;gap:26px;background:var(--card);border:1px solid var(--cardb);border-radius:22px;padding:30px 36px;box-shadow:0 14px 34px rgba(20,40,90,.07)}
.snum{flex:none;width:64px;height:64px;border-radius:16px;color:#fff;font-weight:900;font-size:36px;display:flex;align-items:center;justify-content:center}
.step b{display:block;font-size:36px;font-weight:800;color:var(--ink)}.step span{display:block;font-size:28px;color:var(--muted);font-weight:500;margin-top:4px}
.c-badges{display:flex;flex-wrap:wrap;gap:24px;justify-content:center;width:880px}
.badge{border:3px solid;font-weight:800;font-size:36px;padding:22px 38px;border-radius:18px;background:var(--card)}
.c-stats{display:flex;gap:26px;width:900px}
.stat{flex:1;background:var(--card);border:1px solid var(--cardb);border-radius:26px;padding:44px 20px;text-align:center;box-shadow:0 18px 44px rgba(20,40,90,.08)}
.stnum{font-weight:900;font-size:96px;line-height:1;letter-spacing:-2px}
.stlab{margin-top:16px;font-weight:700;font-size:28px;color:var(--muted);line-height:1.25}
.c-quote{width:900px;background:var(--card);border:1px solid var(--cardb);border-radius:30px;padding:54px 56px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.qmark{font-weight:900;font-size:140px;line-height:0.6;height:70px}
.qtext{font-weight:800;font-size:52px;line-height:1.3;color:var(--ink)}
.qby{margin-top:28px;font-weight:700;font-size:32px;color:var(--muted)}
.c-tip{width:900px;display:flex;gap:28px;align-items:flex-start;background:var(--card);border:2px solid;border-radius:26px;padding:42px 48px;box-shadow:0 18px 44px rgba(20,40,90,.08)}
.tipicon{font-size:60px;line-height:1;flex:none}
.tiptitle{font-weight:800;font-size:32px;letter-spacing:1px;margin-bottom:12px}
.tiptext{font-weight:600;font-size:40px;line-height:1.35;color:var(--ink2)}
.c-feature{width:880px;display:flex;flex-direction:column;gap:26px}
.feat{display:flex;align-items:center;gap:28px;background:var(--card);border:1px solid var(--cardb);border-radius:22px;padding:30px 38px;box-shadow:0 14px 34px rgba(20,40,90,.07)}
.femoji{font-size:60px;line-height:1;flex:none}
.feat b{display:block;font-size:38px;font-weight:800;color:var(--ink)}.feat span{display:block;font-size:28px;color:var(--muted);font-weight:500;margin-top:4px}
.c-chart{width:900px;background:var(--card);border:1px solid var(--cardb);border-radius:30px;padding:48px 52px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.chtitle{font-weight:900;font-size:40px;color:var(--ink);margin-bottom:36px}
.chrow{margin:26px 0}
.chlab{font-weight:700;font-size:32px;color:var(--ink2);margin-bottom:12px}
.chtrack{height:62px;background:var(--tagbg);border-radius:14px;overflow:hidden}
.chfill{height:100%;border-radius:14px;display:flex;align-items:center;justify-content:flex-end;min-width:90px}
.chval{color:#fff;font-weight:800;font-size:30px;padding-right:22px}
.c-mockup{width:920px;background:var(--card);border:1px solid var(--cardb);border-radius:26px;overflow:hidden;box-shadow:0 30px 70px rgba(20,40,90,.16)}
.mkbar{background:var(--tagbg);padding:22px 30px;display:flex;align-items:center;gap:14px}
.mkdot{width:20px;height:20px;border-radius:50%}.mkdot.r{background:#FF5F57}.mkdot.y{background:#FEBC2E}.mkdot.g{background:#28C840}
.mkaddr{margin-left:18px;background:var(--card);border:1px solid var(--cardb);border-radius:999px;padding:10px 30px;font-size:28px;color:var(--muted);font-weight:600;flex:1;text-align:center}
.mkbody{padding:44px 40px}
.mktiles{display:flex;flex-wrap:wrap;gap:24px}
.mktile{flex:1 1 40%;background:var(--hibg);border-radius:20px;padding:34px 28px;text-align:center}
.mktnum{font-weight:900;font-size:72px;line-height:1}.mktlab{margin-top:12px;font-weight:700;font-size:28px;color:var(--muted)}
.mklines .mkline{font-size:34px;font-weight:600;color:var(--ink2);padding:18px 0;border-bottom:1px solid var(--cardb)}
.mklines .mkline:last-child{border-bottom:none}
.c-cta{display:flex;flex-direction:column;align-items:center;gap:34px}
.cta-logo{width:560px}.cta-line{font-weight:800;font-size:48px;color:var(--ink);text-align:center}
.cta-btn{color:#fff;font-weight:800;font-size:42px;padding:28px 56px;border-radius:999px}
.c-gitlog{width:880px;background:var(--card);border:1px solid var(--cardb);border-radius:28px;padding:46px 56px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.gltitle{font-family:monospace;font-size:32px;font-weight:700;color:var(--muted);margin-bottom:36px}
.glprompt{color:var(--fb);font-weight:800}
.glrows{border-left:5px solid var(--cardb);margin-left:21px;display:flex;flex-direction:column;gap:34px}
.glrow{display:flex;align-items:center;gap:22px;margin-left:-22px}
.gldot{width:38px;height:38px;border-radius:50%;flex:none;box-shadow:0 0 0 7px var(--card)}
.glid{font-family:monospace;font-size:42px;font-weight:900;color:var(--ink)}
.gltag{font-size:28px;font-weight:800;padding:8px 20px;border-radius:999px}
.glhead{margin-left:auto;background:var(--coral);color:#fff;font-weight:800;font-size:24px;letter-spacing:1px;padding:8px 16px;border-radius:9px}
.footer{position:absolute;left:50%;transform:translateX(-50%);bottom:230px;background:var(--card);border:1px solid var(--cardb);border-radius:999px;
 padding:20px 40px;font-weight:700;font-size:30px;color:var(--ink2);box-shadow:0 12px 34px rgba(20,40,90,.10);white-space:nowrap}
.footer .dotg{color:var(--dotc);margin-right:12px}.footer .b1{color:var(--fb);font-weight:800}.footer .b2{color:var(--dotc);font-weight:700}.footer .sep{color:var(--cardb);margin:0 14px}
.kara{position:absolute;left:50%;transform:translateX(-50%);bottom:300px;background:var(--kara);border-radius:20px;padding:20px 38px;max-width:880px;box-shadow:0 18px 40px rgba(8,15,35,.40)}
.kara span{color:var(--karatx);font-weight:700;font-size:36px;letter-spacing:-.5px;margin:0 7px}
"""
    # Parameterize for aspect. CSS is authored for portrait 1080x1920; for other
    # resolutions scale the canvas + vertical spacing/anchors proportionally (vs) and
    # horizontal padding (hs) so content fits without overflow. Portrait = no-op.
    vs, hs = H / 1920.0, W / 1080.0
    css = css.replace("width:1080px;height:1920px", f"width:{W}px;height:{H}px")  # #root + .scene
    css = css.replace("padding:230px 80px 470px",
                      f"padding:{int(230*vs)}px {int(80*hs)}px {int(470*vs)}px")  # .scene
    css = css.replace("bottom:230px", f"bottom:{int(230*vs)}px")  # .footer
    css = css.replace("bottom:300px", f"bottom:{int(300*vs)}px")  # .kara
    if vs < 0.95:  # landscape / non-portrait: shrink the whole scene content to fit height
        css += f"\n.scene>.kicker,.scene>.head,.scene>.comp{{transform:scale({vs:.3f});transform-origin:center top}}"
    return css

# ---------------------------------------------------------------- main API
_DIMS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}


def make_video(project_dir, segments, scenes, *, lexicon=None, output=None,
               target_lufs=-14, voice="Trọng Hữu", theme="light", music="tech",
               accent_shift=None, brand="seosona", aspect="9:16"):
    _t0 = time.time()   # render wall-clock for the observability hub (Phase 6)
    # accent_shift rotates the whole colour scheme so two videos from the SAME
    # template don't look identical. None -> auto-derive a stable shift from the topic.
    if accent_shift is None:
        accent_shift = _auto_shift(output)
    profile = _load_profile(brand)        # logo + voice come from system_config.yaml
    vcfg = profile.get("voice", {}) or {}
    _pal = ACCENT_PALETTE.get(brand, ACCENT_PALETTE["seosona"])
    os.makedirs(project_dir, exist_ok=True)
    proj = os.path.join(project_dir, "proj"); assets = os.path.join(proj, "assets")
    os.makedirs(assets, exist_ok=True)
    # assets (BGM no longer goes into the HF render — it is ducked under the voice
    # at mix time in step 6 so narration always stays clear)
    for f, _, _ in FONTS:
        src = os.path.join(ROOT, "7_ASSETS/brand/fonts", "BeVietnamPro-" + dict((x[0], x[2]) for x in FONTS)[f] + ".ttf")
        if os.path.exists(src): shutil.copy(src, os.path.join(assets, f))
    logo_src = os.path.join(ROOT, "7_ASSETS/brand/logos", profile.get("logo", "Seosona_Logo.png"))
    if not os.path.exists(logo_src):
        logo_src = os.path.join(ROOT, BRAND["logo"])
    shutil.copy(logo_src, os.path.join(assets, "logo.png"))

    # 1) voice (pronunciation form) via VieNeu male
    lex = dict(nvs.PRONUNCIATION_LEXICON); lex.update(lexicon or {})
    import re
    def pron(s):
        for k in sorted(lex, key=len, reverse=True):
            s = re.sub(r'(?<![A-Za-z0-9])'+re.escape(k)+r'(?![A-Za-z0-9])', lex[k], s)
        return s
    display_full = " ".join(segments)
    voice_path = os.path.join(assets, "voice.mp3")
    # Route through voice_router (single source of truth): it enforces the single
    # approved brand voice + honest edge fallback. `voice` is advisory — the router
    # coerces any preset to APPROVED_VOICE.
    vr = __import__("2_SKILLS.voice_cloner.voice_router", fromlist=["x"])
    ref = vcfg.get("reference_audio")
    ref = os.path.join(ROOT, ref) if ref else None
    ref = ref if (ref and os.path.exists(ref)) else None   # clone auto-activates when a real clip exists
    vr.synthesize_voice(
        " ".join(pron(s) for s in segments), voice_path,
        brand=brand,
        engine=vcfg.get("engine", "vieneu"),
        preset_voice=vcfg.get("model") or voice,
        reference_audio=ref,
        fallback_voice=vcfg.get("fallback_voice", "vi-VN-NamMinhNeural"),
        require_male_southern=(str(vcfg.get("required_gender", "")).lower() == "male"
                               and str(vcfg.get("required_accent", "")).lower() == "southern"),
    )

    # 2) timing → DISPLAY words (RULE #1)
    from moviepy.editor import AudioFileClip
    dur = AudioFileClip(voice_path).duration
    # Auto-pace (WPM-aware, ported from claude-code-video-toolkit tools/pacing.py):
    # a cloned voice inherits pace from its reference and can overshoot the 45–60s
    # target. Speeding it up to a fixed 58s rushes DENSE scripts (>200 wpm = a tongue
    # twister). So we target the LONGER of 58s or the duration that keeps the voice
    # under a comfortable ceiling — better a 66s video than a rushed 58s one. atempo
    # preserves pitch. Done BEFORE ASR so captions/scenes time to the final voice.
    # BIDIRECTIONAL — a cloned voice's pace varies wildly take-to-take (we've seen the
    # same script come out 122 wpm AND 214 wpm). So correct in BOTH directions:
    #   too fast (>~MAX_WPM) → slow down (atempo<1, floored at 0.85 to avoid artifacts)
    #   too slow/long        → speed up (atempo>1, capped 1.35)
    MAX_WPM, MIN_ATEMPO = 175.0, 0.85   # toolkit: 170–210 wpm reads as "fast"; 0.85 = artifact floor
    nwords = len(nvs.tokenize_words(display_full))
    wpm0 = round(nwords / dur * 60, 1) if dur else 0.0
    wpm_dur = (nwords / MAX_WPM * 60.0) if nwords else dur   # duration that yields MAX_WPM
    rate = None
    if wpm0 > MAX_WPM + 8 and dur > 0:                       # rushed clone → stretch toward MAX_WPM
        rate = max(MIN_ATEMPO, round(dur / wpm_dur, 3))
    elif dur > max(58.0, wpm_dur) + 6:                       # comfortable but long → tighten to ~58s
        rate = min(1.35, round(dur / max(58.0, wpm_dur), 3))
    if rate and abs(rate - 1.0) > 0.02:
        sped = os.path.join(assets, "voice_p.mp3")
        subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", "-i", voice_path,
                        "-filter:a", f"atempo={rate}", sped], check=True)
        shutil.move(sped, voice_path)
        dur = AudioFileClip(voice_path).duration
        print(f"[pace] {nwords}w {wpm0}→{round(nwords/dur*60,1) if dur else 0} wpm | atempo {rate} | → {dur:.1f}s")
    else:
        print(f"[pace] {nwords}w {wpm0} wpm | {dur:.1f}s — within comfort band, no change")
    asr = __import__("2_SKILLS.srt_maker.asr_router", fromlist=["x"])
    words = asr.transcribe_words(voice_path, language="vi")
    for w in words: w["duration"] = w["end"] - w["start"]
    plan = nvs.prepare_tts_script(display_full)
    dwords = nvs.align_tts_boundaries_to_display_words(plan, words, dur)
    # Caption-sync QC: the aligner needs ≥1 ASR boundary per spoken word, else it falls
    # back to EVENLY-ESTIMATED timing (captions still show display words — RULE #1 — but
    # drift from the voice). Surface which path was taken so sync quality is observable.
    _ntts, _nasr = len(plan.tts_words), len(words)
    _ratio = round(_nasr / _ntts, 2) if _ntts else 0.0
    if _nasr < _ntts:
        print(f"[caption-sync] ⚠ ESTIMATED timing — ASR {_nasr} < spoken {_ntts} words "
              f"(ratio {_ratio}); captions show display words but may drift from voice.")
    else:
        print(f"[caption-sync] ✓ real word-level timing (ASR {_nasr} ≥ spoken {_ntts}).")

    # 3) scene boundaries from word counts
    counts = [len(nvs.tokenize_words(s)) for s in segments]
    groups, idx = [], 0
    for c in counts:
        groups.append(dwords[idx:idx+c]); idx += c
    TOTAL = dur + 1.6   # extra tail so the CTA (last scene) holds & doesn't feel rushed

    # 4) build HTML
    # Scenes CROSSFADE so there is never a blank frame: each scene mounts a touch
    # before its words and stays until the next has fully faded in; the wrapper
    # opacity fades out exactly as the next fades in. Inner elements only slide
    # (the wrapper owns opacity). Scene 0 is static & full at frame 0 (RULE #2).
    starts = [(groups[i][0]["start"] if i < len(groups) and groups[i] else i*3.0)
              for i in range(len(scenes))]
    appear = lambda i: 0.0 if i == 0 else max(0.0, starts[i] - 0.25)
    scene_html, tweens = [], []
    for i, sc in enumerate(scenes):
        ap = appear(i)
        nxt = appear(i+1) if i+1 < len(scenes) else None
        gone = (nxt + 0.45) if nxt is not None else TOTAL
        d = max(1.0, gone - ap)
        acc = _resolve_acc(_rotate_acc(sc.get("acc", "blue"), accent_shift), brand); cid = f"sc{i}"
        comp = _component(sc["comp"][0], sc["comp"][1], acc, _pal) if sc.get("comp") else ""
        comp_kind = sc["comp"][0] if sc.get("comp") else None
        # HERO scene = full-bleed accent background + white text (breaks the "always
        # light + centered card" sameness). kicker/heading use white; component picks
        # white via .scene.hero CSS overrides.
        hero = bool(sc.get("hero"))
        scls = "scene clip hero" if hero else "scene clip"
        sstyle = f' style="background:linear-gradient(157deg,{acc} 0%,{_theme(brand)["ink"]} 165%)"' if hero else ""
        kstyle = "color:#fff;background:#ffffff2e" if hero else f"color:{acc};background:{acc}1f"
        l2style = "color:#fff" if hero else f"color:{acc}"
        # Ambient depth layer: breathing glow + oversized faint ghost word (the kicker).
        if hero:
            glowbg, ghostcol = "radial-gradient(circle,#ffffff2b 0%,transparent 70%)", "#ffffff14"
        else:
            glowbg, ghostcol = f"radial-gradient(circle,{acc}1f 0%,transparent 70%)", "#0F172A0A"
        scbg = (f'<div class="scbg"><div class="scglow" style="background:{glowbg}"></div>'
                f'<div class="scghost" style="color:{ghostcol}">{_esc(sc["kicker"])}</div></div>')
        scene_html.append(
            f'<div class="{scls}" id="{cid}"{sstyle} data-start="{ap:.2f}" data-duration="{d:.2f}" data-track-index="{2+(i%2)*3}">'
            f'{scbg}'
            f'<div class="kicker" style="{kstyle}">{_esc(sc["kicker"])}</div>'
            f'<h1 class="head"><span class="l1">{_esc(sc["h1"])}</span><span class="l2" style="{l2style}">{_esc(sc["h2"])}<i class="l2u" style="background:{"#fff" if hero else acc}"></i></span></h1>'
            f'<div class="comp">{comp}</div></div>')
        if i == 0:
            tweens.append(f'tl.set("#{cid}",{{opacity:1}},0);')
            tweens.append(f'tl.set("#{cid} .kicker",{{y:0}},0);tl.set("#{cid} .head",{{y:0}},0);tl.set("#{cid} .comp",{{y:0,scale:1}},0);')
        else:
            tweens.append(f'tl.fromTo("#{cid}",{{opacity:0}},{{opacity:1,duration:0.32,ease:"power1.out"}},{ap:.2f});')
            tweens.append(f'tl.fromTo("#{cid} .kicker",{{y:-24}},{{y:0,duration:0.45,ease:"power2.out"}},{ap:.2f});')
            tweens.append(f'tl.fromTo("#{cid} .head",{{y:28}},{{y:0,duration:0.5,ease:"power3.out"}},{ap+0.06:.2f});')
            tweens.append(f'tl.fromTo("#{cid} .comp",{{y:34,scale:0.97}},{{y:0,scale:1,duration:0.55,ease:"power3.out"}},{ap+0.12:.2f});')
        # Marker underline draws under the accent heading word (craft/references/css-patterns.md
        # "highlight/sketch" modes, re-skinned): a hand-drawn accent rule that sweeps in.
        ut = 0.50 if i == 0 else ap + 0.60
        tweens.append(f'tl.fromTo("#{cid} .l2u",{{scaleX:0}},{{scaleX:1,duration:0.50,ease:"power2.out"}},{ut:.2f});')
        # Ambient motion (motion-principles.md): a slow glow breathe + ghost drift across the
        # scene so the background is alive, not "nothing loaded". sine.inOut over the scene.
        adur = min(max(d, 2.0), 7.0)
        tweens.append(f'tl.fromTo("#{cid} .scglow",{{scale:0.92,opacity:0}},{{scale:1.12,opacity:1,duration:{adur:.2f},ease:"sine.inOut"}},{ap:.2f});')
        tweens.append(f'tl.fromTo("#{cid} .scghost",{{x:-26,opacity:0}},{{x:26,opacity:1,duration:{adur:.2f},ease:"sine.inOut"}},{ap:.2f});')
        # Recipe 1 (craft/motion-recipes-seosona.md): a bignum should TICK/POP + grow its
        # glow, not just slide up — gives the number impact. Glow grows on every scene; the
        # pop is skipped on the hero scene 0 (which already has its own intro set at t=0).
        if comp_kind == "bignum":
            gt = 0.30 if i == 0 else ap + 0.45
            tweens.append(f'tl.fromTo("#{cid} .c-bignum .bgglow",{{scale:0.5,opacity:0}},{{scale:1,opacity:1,duration:0.70,ease:"power2.out"}},{gt:.2f});')
            # Count-up for numeric values ("5 bước", "$10K", "80%"): tick 0→target. GSAP
            # fires onUpdate under .seek(), so the counter renders frame-by-frame.
            bspec = _split_bignum(sc["comp"][1].get("big", "")) if sc.get("comp") else None
            land = None
            if bspec:
                cstart = 0.40 if i == 0 else ap + 0.40
                cdur = 1.30
                numexpr = ("o.v.toFixed(%d)" % bspec["decimals"]) if bspec["decimals"] else "Math.round(o.v)"
                commaexpr = "n=n.replace(/\\B(?=(\\d{3})+(?!\\d))/g,',');" if bspec["comma"] else ""
                tweens.append(
                    ';(function(){var el=document.querySelector("#%s .bn-num");if(!el)return;'
                    'var o={v:0};tl.to(o,{v:%s,duration:%.2f,ease:"power2.out",onUpdate:function(){'
                    'var n=String(%s);%sel.textContent=n;}},%.2f);})();'
                    % (cid, repr(bspec["target"]), cdur, numexpr, commaexpr, cstart))
                land = cstart + cdur
            if i != 0:
                if land is not None:   # subtle +8% landing pop synced to the count finishing
                    tweens.append(f'tl.to("#{cid} .c-bignum .big",{{scale:1.08,duration:0.14,ease:"power2.out"}},{land-0.02:.2f});')
                    tweens.append(f'tl.to("#{cid} .c-bignum .big",{{scale:1.0,duration:0.40,ease:"power2.out"}},{land+0.12:.2f});')
                else:                  # non-numeric bignum → entrance pop
                    pt = ap + 0.55
                    tweens.append(f'tl.fromTo("#{cid} .c-bignum .big",{{scale:0.84}},{{scale:1.06,duration:0.36,ease:"back.out(2.2)"}},{pt:.2f});')
                    tweens.append(f'tl.to("#{cid} .c-bignum .big",{{scale:1.0,duration:0.50,ease:"power2.out"}},{pt+0.34:.2f});')
        # BUILD-ON: reveal multi-item content one-by-one as the scene plays (synced with
        # the per-item pop SFX in _sfx_cues), instead of showing the whole card at once.
        grp_i = groups[i] if i < len(groups) else []
        rplan = _reveal_plan(grp_i[0]["start"], grp_i[-1]["end"], _reveal_count(sc.get("comp"))) if grp_i else None
        if rplan:
            rstart, rint, _ = rplan
            # Vary entrance DIRECTION + EASE per item (Recipe 2, craft/motion-recipes-seosona.md)
            # instead of every .ritem sliding up identically — that uniformity is what made
            # videos feel "giống nhau". Deterministic (index-based, no random); same reveal
            # times as before (rstart + k*rint) so the per-item pop SFX stays in sync.
            tweens.append(
                ';(function(){var _it=document.querySelectorAll("#%s .ritem");'
                'var _E=[{x:-44,ease:"expo.out",duration:0.50},{y:26,ease:"power3.out",duration:0.46},'
                '{x:44,ease:"expo.out",duration:0.50},{scale:0.90,ease:"back.out(1.4)",duration:0.55}];'
                '_it.forEach(function(el,k){var e=Object.assign({opacity:0},_E[k%%_E.length]);'
                'tl.from(el,e,%.2f+k*%.3f);});})();' % (cid, rstart, rint))
            # Chart bars GROW left→right via a clip-path wipe (craft/data-in-motion.md: a
            # number needs visual weight; a bar that fills reads as data, not static text).
            # clip-path wipe (not scaleX) so the value label never distorts.
            if comp_kind == "chart":
                tweens.append(
                    ';(function(){var _b=document.querySelectorAll("#%s .chfill");'
                    '_b.forEach(function(el,k){tl.fromTo(el,{clipPath:"inset(0 100%% 0 0)"},'
                    '{clipPath:"inset(0 0%% 0 0)",duration:0.62,ease:"power2.out"},%.2f+k*%.3f+0.05);});})();'
                    % (cid, rstart, rint))
        if nxt is not None:
            # Old scene fully GONE by the moment the next mounts (data-start=nxt) → the
            # two are NEVER on screen together (no double-text/ghosting at all). The new
            # then fades in from the light branded bg; the ~1 transition frame is bg+dots,
            # never black. EXIT STYLE rotates per scene (fade / slide-left / slide-up /
            # scale-down) so cuts aren't all the same crossfade — but always non-overlapping.
            _EXITS = ["", ",x:-64", ",y:-52", ",scale:0.92"]
            ex = _EXITS[i % len(_EXITS)]
            tweens.append(f'tl.to("#{cid}",{{opacity:0{ex},duration:0.34,ease:"power2.in"}},{nxt-0.34:.2f});')

    # karaoke chunks (~4 words), alternating tracks
    chunks = []
    for si, grp in enumerate(groups):
        acc = _resolve_acc(_rotate_acc(scenes[si].get("acc", "blue") if si < len(scenes) else "blue", accent_shift), brand)
        for j in range(0, len(grp), 4):
            sub = grp[j:j+4]
            if sub: chunks.append({"start": sub[0]["start"], "end": sub[-1]["end"], "acc": acc, "words": sub})
    kara_html = []
    for ci, ch in enumerate(chunks):
        spans = "".join(f'<span id="k{ci}_{wi}">{_esc(w["word"])}</span>' for wi, w in enumerate(ch["words"]))
        st = round(ch["start"], 2)
        nxt = round(chunks[ci+1]["start"], 2) if ci+1 < len(chunks) else round(TOTAL, 2)
        # ONE sub at a time: each chunk lasts exactly until the next starts, all on a
        # SINGLE track (3). The old code alternated tracks 3/4 + a +0.45 tail, so two
        # subtitle pills overlapped on screen ("2 sub text"). Fixed here.
        d = round(max(0.4, nxt - st), 2)
        kara_html.append(f'<div class="kara clip" id="kc{ci}" data-start="{st:.2f}" data-duration="{d:.2f}" data-track-index="3">{spans}</div>')
        for wi, w in enumerate(ch["words"]):
            tweens.append(f'tl.set("#k{ci}_{wi}",{{color:"{ch["acc"]}",fontWeight:800}},{w["start"]:.2f});')
            tweens.append(f'tl.set("#k{ci}_{wi}",{{color:"#E5E7EB",fontWeight:700}},{w["end"]:.2f});')

    js = "window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});" + "".join(tweens) + 'window.__timelines["main"]=tl;'
    VW, VH = _DIMS.get(aspect, (1080, 1920))
    res = "portrait" if VH >= VW else "landscape"
    doc = (f'<!doctype html><html lang="vi" data-resolution="{res}"><head><meta charset="UTF-8"/>'
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{_css(brand, VW, VH)}</style></head><body>'
           f'<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.2f}" data-width="{VW}" data-height="{VH}">'
           f'<div class="dots"></div>'
           f'<audio id="voice" class="clip" data-start="0" data-duration="{TOTAL:.2f}" data-track-index="0" src="assets/voice.mp3" data-volume="1"></audio>'
           f'<img class="brandlogo" src="assets/logo.png"/>'
           f'{"".join(scene_html)}'
           f'<div class="footer">{FOOTERS.get(brand, BRAND["footer"])}</div>'
           f'{"".join(kara_html)}<script>{js}</script></div></body></html>')
    json.dump({"$schema":"https://hyperframes.heygen.com/schema/hyperframes.json","paths":{"blocks":"compositions","components":"compositions/components","assets":"assets"}}, open(os.path.join(proj,"hyperframes.json"),"w"))
    json.dump({"id":"seosona-video","name":"SEOSONA Video"}, open(os.path.join(proj,"meta.json"),"w"))
    open(os.path.join(proj,"index.html"),"w",encoding="utf-8").write(doc)

    # 5) lint + render native
    cli = _hf_cli()
    renv = _render_env()   # point the node renderer at concrete ffmpeg/ffprobe binaries
    subprocess.run(["node", cli, "lint"], cwd=proj, env=renv)
    # ABSOLUTE — the HF render runs with cwd=proj, so a relative --output would nest
    # the file inside proj/ and the SFX step below (run from a different cwd) would
    # not find it, silently failing the render. Keep all output paths absolute.
    raw = os.path.abspath(os.path.join(project_dir, "_raw.mp4"))
    subprocess.run(["node", cli, "render", "--format", "mp4", "--output", raw], cwd=proj, check=True, env=renv)

    # 6) MIX = voice (from raw) + BGM ducked under voice (sidechain) + component SFX,
    #    then loudnorm + brickwall limiter. Inputs: [0]=raw(voice video), [1]=bgm
    #    (looped), [2..]=SFX. BGM sidechain-ducks to the voice so narration is always
    #    clear; SFX sit between. The final alimiter GUARANTEES no clipping.
    out = os.path.abspath(output or os.path.join(project_dir, "FINAL.mp4"))
    cues = _sfx_cues(groups, scenes, TOTAL)
    bgm = _bgm(music)
    inputs = ["-i", raw, "-stream_loop", "-1", "-i", bgm]
    # Voice is the HERO of the mix: boost it and keep BGM well under it so narration is
    # never buried. BGM ducks further under the (boosted) voice via sidechain.
    filt = ["[0:a]asplit=2[v0][vkey]",
            "[v0]volume=1.3[vmain]",
            "[1:a]volume=0.18[bg0]",
            "[bg0][vkey]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[bgduck]"]
    mixn = ["[vmain]", "[bgduck]"]
    for i, (t, path, vol) in enumerate(cues):
        inputs += ["-i", path]
        ms = int(t * 1000)
        filt.append(f"[{i+2}]volume={vol},adelay={ms}|{ms}[s{i}]"); mixn.append(f"[s{i}]")
    # alimiter first catches big transients, then loudnorm LAST sets loudness AND
    # hard-limits TRUE peak to its TP target (dBTP) — guarantees TP < 0 on every channel.
    # loudnorm resamples to a high internal rate; aresample back to 48k so the output is
    # a STANDARD 48 kHz stream. A 96 kHz AAC plays fine in ffmpeg but is SILENT in many
    # players/platforms (web, mobile, social) — that reads as "no voice".
    fc = ";".join(filt) + ";" + "".join(mixn) + \
        f"amix=inputs={len(mixn)}:normalize=0:duration=first[mix];" \
        f"[mix]alimiter=limit=0.95:level=disabled,loudnorm=I={target_lufs}:TP=-1.5:LRA=11,aresample=48000[ao]"
    subprocess.run([_ffmpeg_bin(),"-y","-hide_banner","-loglevel","error",*inputs,"-filter_complex",fc,
                    "-map","0:v","-map","[ao]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000",out], check=True)

    # 7) DISPLAY-word SRT (RULE #1) — one cue per scene, aligned to narration timing.
    # Captions are baked into the video too, but a sidecar .srt is needed for upload
    # platforms + repurpose. Written next to the final mp4.
    try:
        # Sidecar SRT goes in a subs/ subfolder, NOT next to the mp4 — a same-named .srt
        # auto-loads in players and shows a SECOND big subtitle over the baked karaoke.
        # Players (VLC etc.) AUTO-LOAD a .srt that matches the video name, even from
        # sub-folders named subs/ subtitles/ — that shows a 2nd big subtitle over the
        # baked karaoke. So: a NON-searched folder (_captions_upload) AND a base name
        # that does NOT match the video (suffix _cc). The karaoke IS the on-screen sub.
        subs_dir = os.path.join(os.path.dirname(out) or ".", "_captions_upload"); os.makedirs(subs_dir, exist_ok=True)
        srt_path = os.path.join(subs_dir, os.path.splitext(os.path.basename(out))[0] + "_cc.srt")
        _write_srt(srt_path, groups, segments)
        print(f"SRT:   {srt_path}")
    except Exception as e:
        print(f"[native_composer] SRT write skipped: {e}")

    # 8) THUMBNAIL — grab a representative frame (scene-0 hook is full at frame 0; take a
    # moment in so motion has settled) → <project_dir>/Thumbnail/thumbnail.png.
    try:
        thumb_dir = os.path.join(os.path.dirname(out) or ".", "Thumbnail")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb = os.path.join(thumb_dir, "thumbnail.png")
        grab_t = min(2.0, max(0.5, (TOTAL or 4) * 0.12))
        subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{grab_t:.2f}", "-i", out, "-frames:v", "1", thumb], check=True)
        print(f"THUMB: {thumb}")
    except Exception as e:
        print(f"[native_composer] thumbnail grab skipped: {e}")

    print(f"FINAL: {out}  ({len(cues)} SFX cues, BGM ducked: {os.path.basename(bgm)})")
    # Phase 6: emit a render metric to the observability hub (best-effort, never fatal).
    try:
        sys.path.insert(0, os.path.join(ROOT, "9_DASHBOARD"))   # observability hub home
        import obs_metrics
        obs_metrics.record("render", output=out, brand=brand, duration=round(dur, 1),
                           wpm=wpm0, caption_sync=("real" if _nasr >= _ntts else "estimated"),
                           sfx=len(cues), render_seconds=round(time.time() - _t0, 1))
    except Exception as _e:
        print(f"[obs] render metric skipped: {_e}")
    return out


def _srt_ts(sec):
    sec = max(0.0, float(sec))
    h = int(sec // 3600); m = int((sec % 3600) // 60)
    s = int(sec % 60); ms = int(round((sec - int(sec)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _write_srt(path, groups, segments):
    """One subtitle cue per scene, timed from that scene's display-word group."""
    lines, n = [], 0
    for i, seg in enumerate(segments):
        grp = groups[i] if i < len(groups) else []
        if not grp or not str(seg).strip():
            continue
        start, end = grp[0]["start"], grp[-1]["end"]
        n += 1
        lines += [str(n), f"{_srt_ts(start)} --> {_srt_ts(end)}", str(seg).strip(), ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def make_video_custom(project_dir, scenes_spec, *, lexicon=None, output=None, **kw):
    """FREEFORM (no template lock) — build a video from an explicit scene list.

    The Scene-Composer assembles scenes from the 12-component toolbox FREELY, driven
    by the content: any components, any order, any count (5–9 scenes). Templates are
    just optional starting points — this is the unrestricted path.

    scenes_spec: list of dicts, each:
      {"seg": "<câu thoại display-form>", "kicker": "...", "h1": "...", "h2": "...",
       "acc": "blue|green|orange", "comp": ("<kind>", {<data>}) or None}
    comp kinds: bignum repo compare terminal steps badges gittree cta stats quote tip feature.
    Keep a comp at scene 0 or >=2; cảnh 1 nên là text bắc cầu.
    """
    segments = [s.get("seg", "") for s in scenes_spec]
    scenes = []
    for s in scenes_spec:
        sc = {"kicker": s.get("kicker", ""), "h1": s.get("h1", ""),
              "h2": s.get("h2", ""), "acc": s.get("acc", "blue"), "hero": s.get("hero", False)}
        if s.get("comp"):
            sc["comp"] = s["comp"]
        scenes.append(sc)
    return make_video(project_dir, segments, scenes, lexicon=lexicon, output=output, **kw)


# ============================================================================
# TEMPLATE LIBRARY — separate STRUCTURE (template) from CONTENT (data)
# A template = scene STRUCTURE only (component type + accent role + kicker hint),
# NO content. The Scene-Composer fills it with per-topic data → make_video.
# More templates = more styles to rotate → news videos don't get repetitive.
# ============================================================================
TEMPLATE_DIR = os.path.join(ROOT, "7_ASSETS", "templates")
_ACCENTS = {"blue": BLUE, "green": GREEN, "orange": ORANGE}
_ACCENT_INV = {v: k for k, v in _ACCENTS.items()}


def list_templates():
    if not os.path.isdir(TEMPLATE_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(TEMPLATE_DIR) if f.endswith(".json"))


def load_template(name):
    with open(os.path.join(TEMPLATE_DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def save_template(name, template):
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    template = dict(template, name=name)
    with open(os.path.join(TEMPLATE_DIR, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    return name


def fill_template(template, content):
    """Merge a TEMPLATE (structure: per-scene component/accent/kicker_hint, NO data) with
    CONTENT (per-scene kicker/h1/h2/data) → the scenes list that make_video consumes."""
    tscenes, cscenes = template["scenes"], content["scenes"]
    if len(cscenes) != len(tscenes):
        raise ValueError(f"content has {len(cscenes)} scenes but template "
                         f"'{template.get('name')}' has {len(tscenes)}")
    scenes = []
    for ts, cs in zip(tscenes, cscenes):
        comp = (ts["component"], cs.get("data", {})) if ts.get("component") else None
        scenes.append({"kicker": cs.get("kicker") or ts.get("kicker_hint", ""),
                       "h1": cs["h1"], "h2": cs["h2"], "hero": cs.get("hero") or ts.get("hero", False),
                       "acc": ts.get("accent", "blue"), "comp": comp})  # accent ROLE; resolved by theme at render
    return content["segments"], scenes


def make_video_from_template(template_name, content, project_dir, *, output=None, **kw):
    """TEMPLATE + CONTENT → video. The high-level entry for the news factory."""
    tpl = load_template(template_name)
    segments, scenes = fill_template(tpl, content)
    kw.setdefault("theme", tpl.get("theme", "light"))  # light-mode only (brand)
    kw.setdefault("aspect", tpl.get("aspect", "9:16"))  # 9:16 default; 16:9 if template says so
    print(f"[template] '{template_name}' ({kw['theme']}, {kw['aspect']}) filled with {len(scenes)} scenes")
    return make_video(project_dir, segments, scenes, lexicon=content.get("lexicon"), output=output, **kw)


def extract_template(name, scenes, *, title="", description="", when_to_use="", aspect="9:16", theme="light"):
    """Reverse: strip content from a filled scenes list and SAVE its structure as a
    reusable template (component/accent/kicker_hint only). Grows the library from clones."""
    tscenes = [{"component": (sc.get("comp") or (None,))[0],
                "accent": (sc.get("acc") if sc.get("acc") in ("blue", "green", "orange")
                           else _ACCENT_INV.get(sc.get("acc"), "blue")),
                "kicker_hint": sc.get("kicker", "")} for sc in scenes]
    return save_template(name, {"title": title or name, "description": description,
                                "when_to_use": when_to_use, "aspect": aspect, "theme": theme, "scenes": tscenes})

