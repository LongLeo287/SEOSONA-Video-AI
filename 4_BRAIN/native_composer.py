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
import brand_kit as bk   # single source of truth for brand palette + CTA copy
import effect_library as el   # 4th library layer: transition/exit recipes, rotated per-video

# ---------------------------------------------------------------- brand kit
# Sampled from the SEOSONA brand carousel (7_ASSETS/brand/SEOSONA/*.jpg):
# primary blue #2A5BDA, coral accent #E2724D, logo green #16A34A. Light mode only.
BLUE, GREEN, ORANGE = bk.BLUE, bk.GREEN, bk.ORANGE   # from brand_kit (single source)
BRAND = {
    "logo": "7_ASSETS/brand/logos/Seosona_Logo.png",
    "bgm": "7_ASSETS/audio/bgm/bgm_tech_ambient.mp3",
    "footer": ('<span class="dotg">●</span> <span class="b1">SEOSONA AI</span>'
               f'<span class="sep">·</span> <span class="b2">{bk.FOOTER_TAGLINE}</span>'),
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

# Emoji per kicker label → a small icon leads every kicker pill (more lively, scannable).
# NOTE: use single-codepoint emoji that render reliably in the font — AVOID variation-selector
# emoji (⚖️ ⚙️ 🛠️ ⚠️) which showed up blank in the render.
_KICKER_EMOJI = {
    "TIN NÓNG": "🔥", "SEOSONA AI": "✨", "GHI NHỚ": "📌", "CON SỐ": "📊", "QUY MÔ": "📈",
    "GÓC NHÌN": "💭", "SO SÁNH": "🆚", "CÁCH LÀM": "🔧", "ĐIỂM CHÍNH": "⭐", "BỐI CẢNH": "🌐",
    "CHI TIẾT": "🔍", "ĐÁNG CHÚ Ý": "👀", "THỰC TẾ": "✅", "TÁC ĐỘNG": "💥", "KHÁI NIỆM": "💡",
    "CÁCH HOẠT ĐỘNG": "🔧", "KẾT LUẬN": "🎯", "HOOK": "🔥", "TRÍCH DẪN": "💬", "NỖI ĐAU": "😣",
    "GIẢI PHÁP": "💡", "KẾT QUẢ": "🚀", "BÀI HỌC": "📌", "DANH SÁCH": "📋", "NỔI BẬT": "⭐",
    "VẤN ĐỀ": "🚨", "XU HƯỚNG": "📈", "RA MẮT": "🚀", "MỤC TIÊU": "🎯", "SETUP": "🔧",
}


def _kicker_label(text):
    """Prefix the kicker with a fitting emoji (icon-forward, more lively)."""
    e = _KICKER_EMOJI.get((text or "").strip().upper())
    return f"{e} {text}" if e else text


_VN_NORM = None       # VietnameseNormalizer singleton (lazy; 17K-entry dict, loaded once)
_VN_NUM_TOKEN = None  # compiled matcher for digit-bearing tokens


def _vn_normalize(text):
    """VN text→spoken normalization (dates/%/currency/units/phone) via VietNormalizer (MIT, dep-free).
    Applied ONLY to digit-bearing tokens: pure-text tokens (incl. brand acronyms like SEO / AI) are left
    UNTOUCHED so the PRONUNCIATION_LEXICON upstream stays the source of truth. Run on the whole string,
    VietNormalizer's built-in acronym dict overrides the lexicon (SEO→'ét ê o', its lowercase lexicon
    output 'seo'→'xơ') — a wrong brand pronunciation on virtually every video. Scoping it to \\S*\\d\\S*
    keeps every number/date/currency/percent normalization while never mangling a word. Returns the
    normalized string, or None if the lib is absent/errors → caller falls back to _say_number_vi."""
    global _VN_NORM, _VN_NUM_TOKEN
    try:
        if _VN_NORM is None:
            import vietnormalizer, re as _re
            _VN_NORM = vietnormalizer.VietnameseNormalizer()
            _VN_NUM_TOKEN = _re.compile(r"\S*\d\S*")
        return _VN_NUM_TOKEN.sub(lambda m: _VN_NORM.normalize(m.group(0)), text)
    except Exception:
        return None


def _say_number_vi(text):
    """Spoken-form numbers for TTS so it never misreads a thousands-comma as a decimal point:
    '119,765' → 'hơn 119 nghìn', '1,234,567' → 'hơn 1 triệu' (the DISPLAY keeps the exact digits;
    only the narration is rounded to a natural Vietnamese form). Small numbers (<1000) are left alone."""
    import re

    def _repl(m):
        raw = re.sub(r"[.,\s]", "", m.group(0))
        if not raw.isdigit():
            return m.group(0)
        n = int(raw)
        if n >= 1_000_000:
            return f"{n // 1_000_000} triệu"      # no 'hơn' here — segments already say 'hơn …' where apt
        if n >= 1000:
            return f"{n // 1000} nghìn"
        return str(n)

    # numbers written with thousands separators (1,234 / 1.234) OR a long 4+ digit run
    return re.sub(r"\d{1,3}(?:[.,]\d{3})+|\d{4,}", _repl, text)


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


def _avatar(name, img=None, acc="#2A5BDA"):
    """A circular avatar: the photo if `img` given, else up-to-2-letter initials on an accent circle
    (Video-Template craft — people/contributor/quote by-line). Reusable across people/quote/org."""
    if img:
        return f'<span class="av av-img"><img src="{_esc(img)}" alt=""/></span>'
    parts = [p for p in str(name or "").split() if p]
    ini = ("".join(p[0] for p in parts[:2]) or (str(name)[:2] if name else "•")).upper()
    return f'<span class="av av-ini" style="background:{acc}">{_esc(ini)}</span>'


_CODE_HL_RE = None
def _code_hl(s):
    """Minimal code/JSON syntax highlight for `codecard`. SINGLE-PASS tokenizer over the escaped text —
    scans once and appends colour spans, so it never re-scans (and corrupts) the markup it just inserted
    (an earlier chained-regex version mangled `class="cc-s"` because `class` is also a keyword). Never raises."""
    global _CODE_HL_RE
    if _CODE_HL_RE is None:
        import re as _re
        _CODE_HL_RE = _re.compile(
            r'(?P<s>&quot;[^&]*?&quot;)|'
            r'(?P<k>\b(?:const|let|var|function|def|return|import|from|export|class|async|await|new|'
            r'if|else|for|while|true|false|null|None|True|False)\b)|'
            r'(?P<n>\b\d+\.?\d*\b)')
    esc = _esc(s)
    out, i = [], 0
    for m in _CODE_HL_RE.finditer(esc):
        out.append(esc[i:m.start()])
        cls = {"s": "cc-s", "k": "cc-k", "n": "cc-n"}[m.lastgroup]
        out.append(f'<span class="{cls}">{m.group()}</span>')
        i = m.end()
    out.append(esc[i:])
    return "".join(out)
def _words(s):
    """Wrap each word of a headline in a .w span so TEXT-EFFECTS (effect_library) can animate words
    one-by-one (word-up / word-pop). Spaces between spans preserve wrapping; empty → ''."""
    return " ".join(f'<span class="w">{_esc(w)}</span>' for w in str(s or "").split())
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

_DUR_CACHE = {}
def _audio_dur(path):
    """Duration (seconds) of an audio file, cached per path. Returns 0.0 if unknown.
    Used to fade SFX out at their tail so cues don't hard-cut (pro-audio de-click)."""
    if path in _DUR_CACHE:
        return _DUR_CACHE[path]
    d = 0.0
    try:
        r = subprocess.run([_ffprobe_bin(), "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", path],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=30)   # a probe must be fast; a hang here would stall the render (other
                                         # ffprobe calls use the same 30s). TimeoutExpired → except → 0.0.
        d = round(float((r.stdout or "").strip()), 3)
    except Exception:
        d = 0.0
    _DUR_CACHE[path] = d
    return d


def _render_env():
    """Env for the HyperFrames render subprocess: point it at concrete ffmpeg/ffprobe."""
    env = dict(os.environ)
    env["HYPERFRAMES_FFMPEG_PATH"] = _ffmpeg_bin()
    env["HYPERFRAMES_FFPROBE_PATH"] = _ffprobe_bin()
    return env


def _scene_block(sc):
    """A scene may use a HyperFrames registry block via scene['block'] or comp=('block',{name}).
    SAFETY CHOKEPOINT: a barred/disabled block returns None here so it can NEVER overlay, regardless of
    how the field got set (writer suggestion — video_engine writes scene['block'] unconditionally —
    template, or auto-pick all funnel through here). Enforces block_picker's default-off + _KNOWN_BAD
    bar at the point of USE, not only at assignment, so the cycle-40 registry-demo safety can't be
    bypassed upstream. No-op unless a block is both enabled AND allow-listed → normal renders unchanged."""
    b = sc.get("block")
    name = (b if isinstance(b, str) else (b or {}).get("name")) if b else None
    if not name and sc.get("comp") and sc["comp"][0] == "block":
        name = (sc["comp"][1] or {}).get("name")
    if not name:
        return None
    # FORGED blocks (block_forge 9:16 kho) are pre-VETTED — rendered clean, light, no demo leak — so they
    # are always allowed (they carry the scene's REAL data, not the demo's). Raw registry blocks still
    # obey block_picker's default-off + _KNOWN_BAD bar.
    try:
        if name in __import__("block_forge").kinds():
            return name
    except Exception:
        pass
    try:
        _bp = __import__("block_picker")
        if not _bp.enabled() or name in getattr(_bp, "_KNOWN_BAD", ()):
            return None
    except Exception:
        pass
    return name


def _overlay_blocks(out, scenes, starts, total):
    """Block CUTAWAY: for each scene that carries a block, play it FULL-WIDTH over the content zone for a
    brief ~2s window (fade in/out) while the voice + karaoke continue underneath — a cinematic visual
    break, not a persistent corner overlay. Covers the upper content area only (karaoke/footer stay).
    NO-OP when no scene uses a block (normal news renders are byte-identical)."""
    H_CUT = 1480     # cover the content zone; leave the bottom (karaoke pill + footer) visible
    WIN = 2.0        # cutaway length (seconds)
    jobs = []
    for i, sc in enumerate(scenes):
        name = _scene_block(sc)
        if name:
            t0 = float(starts[i]) if i < len(starts) else 0.0
            t1 = float(starts[i + 1]) if i + 1 < len(starts) else float(total)
            jobs.append((name, t0, t1))
    if not jobs:
        return out
    import tempfile, shutil
    if os.path.join(ROOT, "4_BRAIN") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
    hf_blocks = __import__("hf_blocks")
    try:
        block_forge = __import__("block_forge")
    except Exception:
        block_forge = None
    inputs, filt, cur, idx = ["-i", out], [], "0:v", 1
    for n, (name, t0, t1) in enumerate(jobs):
        # a FORGED 9:16 block gets the SCENE's real data injected (title/sub/items); raw blocks render as-is.
        clip = None
        if block_forge and name in block_forge.kinds():
            si = next((k for k, s in enumerate(scenes) if _scene_block(s) == name), None)
            _sc = scenes[si] if si is not None else {}
            _cd = _sc.get("comp", (None, {}))[1] if _sc.get("comp") else {}
            data = {"title": _sc.get("h1", "") or "", "sub": _sc.get("h2", "") or "",
                    "acc": BLUE, "items": _cd.get("items", []) if isinstance(_cd, dict) else []}
            clip = block_forge.render_filled(name, data,
                                             os.path.join(tempfile.gettempdir(), f"forgeblk_{name}.mp4"))
        if not clip:
            clip = hf_blocks.render_block(name, os.path.join(tempfile.gettempdir(), f"hfblk_{name}.mp4"))
        if not clip:
            continue
        win = max(1.2, min(WIN, (t1 - t0) - 0.6))   # fit inside the scene, never the whole thing
        cs = t0 + 0.35                               # start just after the scene appears
        fo = max(0.2, win - 0.35)
        inputs += ["-i", clip]
        # take the block's first `win`s, cover the content zone, fade in+out, then time it to cs.
        filt.append(
            f"[{idx}:v]trim=0:{win:.2f},scale=1080:{H_CUT}:force_original_aspect_ratio=increase,"
            f"crop=1080:{H_CUT},format=yuva420p,fade=t=in:st=0:d=0.35:alpha=1,"
            f"fade=t=out:st={fo:.2f}:d=0.35:alpha=1,setpts=PTS-STARTPTS+{cs:.2f}/TB[bz{n}]")
        filt.append(f"[{cur}][bz{n}]overlay=0:0:enable='between(t,{cs:.2f},{cs+win:.2f})'[bo{n}]")
        cur, idx = f"bo{n}", idx + 1
    if idx == 1:
        return out
    tmp = out + ".blk.mp4"
    subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(filt), "-map", f"[{cur}]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", tmp], check=True)
    shutil.move(tmp, out)
    print(f"[native_composer] {idx-1} block cutaway(s)")


def _overlay_scroll(out, scenes, starts, total):
    """REAL screen-recording: for a MOCKUP scene whose data carries a captured scroll video (`scroll`),
    play the footage inside a browser-card region over the scene's window (fade in/out) — a live page
    scroll vs a static screenshot (user 2026-07-03 "cần video, cuộn chuột"). Same overlay pattern as
    _overlay_blocks; NO-OP when no mockup scene has a scroll clip."""
    import shutil
    CW, CH, CY = 940, 588, 610          # card w×h + top-y in the content zone (centered horizontally)
    CX = (1080 - CW) // 2
    jobs = []
    for i, sc in enumerate(scenes):
        comp = sc.get("comp")
        scroll = (comp[1] or {}).get("scroll") if (comp and comp[0] == "mockup") else None
        if scroll and os.path.exists(scroll):
            t0 = float(starts[i]) if i < len(starts) else 0.0
            t1 = float(starts[i + 1]) if i + 1 < len(starts) else float(total)
            jobs.append((scroll, t0, t1))
    if not jobs:
        return out
    inputs, filt, cur, idx = ["-i", out], [], "0:v", 1
    for n, (scroll, t0, t1) in enumerate(jobs):
        win = max(1.6, (t1 - t0) - 0.5); cs = t0 + 0.25; fo = max(0.3, win - 0.4)
        inputs += ["-stream_loop", "-1", "-i", scroll]     # loop the clip if the scene outlasts it
        filt.append(
            f"[{idx}:v]trim=0:{win:.2f},scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},"
            f"format=yuva420p,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st={fo:.2f}:d=0.35:alpha=1,"
            f"setpts=PTS-STARTPTS+{cs:.2f}/TB[sv{n}]")
        filt.append(f"[{cur}][sv{n}]overlay={CX}:{CY}:enable='between(t,{cs:.2f},{cs + win:.2f})'[so{n}]")
        cur, idx = f"so{n}", idx + 1
    if idx == 1:
        return out
    tmp = out + ".scr.mp4"
    subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(filt), "-map", f"[{cur}]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", tmp], check=True)
    shutil.move(tmp, out)
    print(f"[native_composer] scroll-video overlay on {len(jobs)} mockup scene(s)")
    print(f"[native_composer] overlaid {idx-1} block(s)")
    return out

# ---------------------------------------------------------------- SFX library
# Curated from the "Sound Effects Pack" by scripts/build_sfx_library.sh.
# Mixed per-component at scene timestamps so the video feels produced like the
# reference videos (whoosh on cut, impact on a number, keys under a terminal).
SFX_DIR = os.path.join(ROOT, "7_ASSETS", "audio", "sfx")
# transition pool AUTO-GLOBS the folder (2026-07-03) so ingesting more whoosh/swish variants from the
# Sound Effects Pack instantly widens cut-variety — no code edit needed. Sorted = deterministic rotation.
_TRANS = sorted(os.path.relpath(p, SFX_DIR).replace("\\", "/")
                for p in __import__("glob").glob(os.path.join(SFX_DIR, "transition", "*.mp3")))
SFX = {
    "transition": _TRANS or ["transition/swish_01.mp3", "transition/whoosh_01.mp3"],
    "impact_soft": "impact/impact_soft.mp3", "impact_deep": "impact/impact_deep.mp3",
    "impact_hit": "impact/impact_hit.mp3",
    "ui_positive": "ui/positive.mp3", "ui_click": "ui/click.mp3", "ui_success": "ui/success.mp3",
    "ui_pop": "ui/pop.mp3", "ui_notify": "ui/notify.mp3",
    "typing": "typing/keyboard.mp3",
    "riser_short": "riser/riser_short.mp3", "riser_long": "riser/riser_long.mp3",
    # urgency/deadline tension + snapshot reveal (harvested from Sound Effects Pack Clocks/Camera Shutter)
    "tick": "tick/tick.mp3", "countdown": "tick/countdown.mp3", "shutter": "shutter/shutter.mp3",
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
    # data-viz family added 2026-07 — a soft data-reveal impact like `chart` (were silent: no accent cue).
    "ring":      ("impact_soft", 0.42, 0.05),
    "donut":     ("impact_soft", 0.42, 0.05),
    "linechart": ("impact_soft", 0.42, 0.05),
    "divider":   ("impact_deep", 0.44, 0.05),   # a chapter/section break → give it weight (like a hook)
}                                                # timeline is covered by its per-row reveal pops

def _sfx(key_or_rel):
    rel = SFX.get(key_or_rel, key_or_rel)
    return os.path.join(SFX_DIR, rel)

# Semantic SFX (adopted from AI-auto-generate-video's keyword tiers, mapped to our library):
# when a scene's text carries an emphasis word, the structural per-component accent is
# OVERRIDDEN by a fitting sound — content-aware, but NO extra cue (keeps the mix uncluttered).
_SEMANTIC_SFX = [
    (("miễn phí", "thành công", "tốt nhất", "nhanh nhất", "đứng đầu", "vượt trội", "kỷ lục",
      "ấn tượng", "mạnh nhất", "hàng đầu", "dẫn đầu", "đột phá"), "ui_success", 0.44),
    (("cảnh báo", "nguy hiểm", "rủi ro", "vấn đề", "chú ý", "thách thức", "lưu ý", "sai lầm"), "impact_hit", 0.44),
    (("ra mắt", "mới nhất", "bùng nổ", "cách mạng", "nâng cấp", "sắp tới"), "riser_short", 0.34),
    # urgency/deadline → a clock-tick tension accent (Clocks pack)
    # NOTE: use "gấp rút"/"gấp lên" (urgency), NOT bare "gấp" — bare "gấp" also matches the MULTIPLIER
    # "gấp đôi"/"gấp 3 lần"/"gấp bội" (a POSITIVE growth stat), so a doubled-revenue scene wrongly got an
    # urgency countdown sting. "khẩn"/"nhanh lên" already cover the urgency sense.
    (("nhanh lên", "gấp rút", "gấp lên", "kịp", "hết hạn", "deadline", "đếm ngược", "chỉ còn", "sắp hết",
      "trước khi", "khẩn", "ngay bây giờ", "đừng bỏ lỡ"), "tick", 0.36),
    # capture/screenshot/reveal → a camera-shutter snapshot (Camera Shutter pack)
    (("ảnh chụp", "chụp màn hình", "screenshot", "ảnh chụp màn hình", "xem ngay hình",
      "nhìn vào đây", "kết quả thực tế", "bằng chứng"), "shutter", 0.4),
]

def _semantic_sfx(text):
    """Return (sfx_key, vol) if the text hits an emphasis keyword, else None."""
    t = str(text or "").lower()
    for kws, key, vol in _SEMANTIC_SFX:
        if any(k in t for k in kws):
            return key, vol
    return None

# ---------------------------------------------------------------- BGM (by mood)
# Drop royalty-free / licensed tracks here, one per mood. IMPORTANT: viral/chart
# songs are copyrighted — muxing them into the file risks mute/takedown (esp. Ads);
# prefer the platform's native sound library for those. BGM is ducked under the
# voice at mix time (sidechain), so narration always stays clear.
BGM_DIR = os.path.join(ROOT, "7_ASSETS", "audio", "bgm")
BGM = {"tech": "bgm_tech_ambient.mp3", "news": "bgm_news.mp3",
       "insight": "bgm_insight.mp3", "upbeat": "bgm_upbeat.mp3",
       "default": "bgm_tech_ambient.mp3"}

def _bgm(mood="tech", seed=None):
    """Pick a track for `mood`, ROTATING across the whole mood pool = the built-in track + any sourced
    `bgm_<mood>_*.mp3` (added by 2_SKILLS/bgm_sourcer) so videos of one mood no longer all reuse the same
    music. Deterministic per `seed` (e.g. output name) so a re-render keeps the same BGM; random otherwise."""
    import glob
    pool = []
    base = os.path.join(BGM_DIR, BGM.get(mood, BGM["default"]))
    if os.path.exists(base):
        pool.append(base)
    pool += sorted(glob.glob(os.path.join(BGM_DIR, f"bgm_{mood}_*.mp3")))
    pool = list(dict.fromkeys(pool))                    # dedupe (built-in tech file also matches the glob)
    if not pool:
        d = os.path.join(BGM_DIR, BGM["default"])
        return d if os.path.exists(d) else base
    if seed is not None:
        import hashlib
        # md5 → uniformly-distributed index (crc32's low bits cluster for structured names like video_N.mp4).
        h = int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16)
        return pool[h % len(pool)]                       # stable across runs (unlike hash())
    import random
    return random.choice(pool)


def _bgm_pool(mood):
    import glob
    pool = []
    base = os.path.join(BGM_DIR, BGM.get(mood, BGM["default"]))
    if os.path.exists(base):
        pool.append(base)
    pool += sorted(glob.glob(os.path.join(BGM_DIR, f"bgm_{mood}_*.mp3")))
    return list(dict.fromkeys(pool))


def _bgm_medley(mood, dur, seed, out):
    """BGM MEDLEY (user rule 2026-07-03): take ~60s of one track, CROSS-FADE into ~60s of the NEXT, chain
    until it covers the video, fade in at the very start + out at the very end. Beats looping one track on
    end. Returns the medley path, or None (→ caller falls back to single-track loop) if 1 track suffices."""
    import math, hashlib, subprocess
    pool = _bgm_pool(mood)
    SEG, XF = 60.0, 2.0
    need = max(1, int(math.ceil((dur - XF) / (SEG - XF))))   # segments (accounting for crossfade overlap)
    if need <= 1 or len(pool) < 2:
        return None
    h = int(hashlib.md5(str(seed).encode()).hexdigest(), 16)
    start = h % len(pool)
    picks = [pool[(start + i) % len(pool)] for i in range(need)]   # distinct, seed-rotated, wrap if few
    ff = _ffmpeg_bin()
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error"]
    for p in picks:
        cmd += ["-t", str(SEG), "-i", p]                          # first 60s of each track
    parts = ["[0:a]afade=t=in:d=1.5[x0]"]; prev = "x0"
    for i in range(1, len(picks)):
        parts.append(f"[{prev}][{i}:a]acrossfade=d={XF}:c1=tri:c2=tri[x{i}]"); prev = f"x{i}"
    parts.append(f"[{prev}]afade=t=out:d=2.5[bgm]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[bgm]", "-b:a", "160k", out]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if r.returncode == 0 and os.path.exists(out):
            print(f"[bgm] medley: {len(picks)} tracks × ~60s cross-faded → covers {dur:.0f}s")
            return out
    except Exception as _e:
        print(f"[bgm] medley failed ({_e}) — single-track loop")
    return None

# ---------------------------------------------------------------- Lucide SVG icons
_LUCIDE_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "icons")
_lucide_cache = {}
def _lucide(name, size=120, color="#2A5BDA", sw=2.0):
    """Inline a real Lucide SVG (professional line-icon, tintable via currentColor) at `size`px in
    `color` — reference videos use clean icon-tiles, not emoji (2026-07-03: wire the unused 110-icon lib).
    Returns '' if the name isn't in the library so callers fall back to their emoji."""
    if not name:
        return ""
    s = _lucide_cache.get(name)
    if s is None:
        p = os.path.join(_LUCIDE_DIR, f"{name}.svg")
        s = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        _lucide_cache[name] = s
    if not s:
        return ""
    import re as _re
    s = _re.sub(r'width="[0-9.]+"', f'width="{size}"', s, count=1)
    s = _re.sub(r'height="[0-9.]+"', f'height="{size}"', s, count=1)
    s = _re.sub(r'stroke-width="[0-9.]+"', f'stroke-width="{sw}"', s)
    return f'<span style="color:{color};line-height:0;display:inline-flex">{s}</span>'


# Emoji glyph → Lucide icon NAME (each verified present in 7_ASSETS/brand/icons). Lets the emoji-bearing
# tile components (feature / icongrid) render the professional line-icon instead of a raw emoji — the same
# craft upgrade the scene-hero got (reference videos = clean icon-tiles). Unmapped glyphs fall back to the
# emoji, so this never breaks a tile. (2026-07-03: finish "feature/steps tiles still use emoji not Lucide")
_EMOJI_LUCIDE = {
    "💻": "cpu", "🖥": "monitor", "🖥️": "monitor", "📱": "smartphone",
    "⚡": "zap", "🤖": "bot", "🧠": "brain", "🎁": "gift", "🆓": "gift",
    "🔒": "lock", "🔐": "lock", "🔧": "wrench", "🛠": "wrench", "🛠️": "wrench",
    "📊": "chart-column", "📈": "trending-up", "🚀": "rocket", "🎯": "target",
    "⚠": "triangle-alert", "⚠️": "triangle-alert", "✅": "circle-check", "☑": "circle-check", "☑️": "circle-check",
    "✔": "check", "✔️": "check", "✓": "check", "🌐": "globe", "📦": "package",
    "🔗": "link", "💡": "lightbulb", "⭐": "star", "⭐️": "star", "🌟": "star", "🔥": "flame",
    "🛡": "shield", "🛡️": "shield", "⏱": "timer", "⏱️": "timer", "⏲": "timer",
    "🕐": "clock", "🕒": "clock", "🔍": "search", "🔎": "search", "✨": "sparkles",
    "💬": "message-circle", "📡": "network", "🗄": "database", "🗄️": "database",
    "☁": "cloud", "☁️": "cloud",
    "📁": "folder", "📂": "folder-open", "🗂": "layers", "🗂️": "layers",
    "🔑": "key", "👥": "users", "👤": "user", "⚙": "settings", "⚙️": "settings",
    "⌨": "terminal", "⌨️": "terminal", "🔀": "workflow", "👁": "eye", "👁️": "eye",
    "🔌": "plug", "🔔": "bell", "📧": "mail", "✉": "mail", "✉️": "mail", "📦": "package",
}


def _tile_icon(glyph, color="#2A5BDA", size=48):
    """Inner HTML for an icon-tile slot: a tinted Lucide SVG when the glyph maps to one, else the raw
    emoji (escaped). Upgrades feature/icongrid tiles to line-icons (reference craft) without touching data."""
    svg = _lucide(_EMOJI_LUCIDE.get((glyph or "").strip(), ""), size=size, color=color, sw=2.2)
    return svg or _esc(glyph or "")


_LOTTIE_DIR = os.path.join(ROOT, "7_ASSETS", "brand", "lottie")


def _lottie_json(name, maxbytes=380000):
    """Resolve a lottie name/CONCEPT → its animation JSON string, CONTENT-MATCHED via element_maker's
    concept→animation aliases (so a 'thành công' scene gets the success anim — real relevance, not random).
    None if missing / oversized / the player lib is absent."""
    try:
        p = str(name or "").lower().strip()
        try:
            sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "element_maker"))
            import element_maker as _em
            p = _em.LOTTIE_ALIASES.get(p, p)
        except Exception:
            pass
        fp = os.path.join(_LOTTIE_DIR, p if p.endswith(".json") else p + ".json")
        if not os.path.exists(fp) or os.path.getsize(fp) > maxbytes:
            return None
        if not os.path.exists(os.path.join(_LOTTIE_DIR, "lottie.min.js")):
            return None
        return open(fp, encoding="utf-8").read()
    except Exception:
        return None


# ---------------------------------------------------------------- progressive reveal
# Multi-item components reveal item-by-item (build-on) as the scene plays, each with a
# pop SFX — instead of showing everything at once.
def _reveal_count(comp):
    if not comp: return 0
    kind, d = comp
    if kind in ("steps", "feature", "badges", "chart", "checklist", "icongrid", "chiprow",
                "alert", "filetree", "bars", "timeline"):
        return len(d.get("items", []))
    if kind == "terminal": return len(d.get("lines", []))
    if kind == "stats": return len(d.get("items", [])[:3])
    if kind == "mockup": return len(d.get("tiles", [])) if d.get("tiles") else 0
    if kind == "hub": return len(d.get("nodes", []))
    if kind == "concept_build": return len(d.get("nodes", [])) + len(d.get("frames", []))
    if kind == "comparison_grid": return len(d.get("rows", []))
    if kind == "split_reveal": return 2
    if kind == "annotated_screenshot": return len(d.get("marks", []))
    if kind == "stat_grid": return len(d.get("stats", d.get("items", []))[:6])
    if kind == "ratio_dots": return 1
    if kind == "layer_stack": return len(d.get("layers", []))
    if kind == "ticker_feed": return len(d.get("items", [])[:6])
    if kind == "org_diagram": return len(d.get("nodes", [])) + 1
    if kind == "pie": return len(d.get("segments", []))
    if kind == "chat": return len(d.get("messages", d.get("items", [])))
    if kind == "codecard": return len(d.get("lines", d.get("items", [])))
    if kind == "tabs": return len(d.get("items", []))
    if kind == "gauge": return 1
    if kind == "metric_rows": return len(d.get("rows", d.get("items", [])))
    if kind == "pill_stack": return len(d.get("items", []))
    if kind == "people": return len(d.get("items", []))
    if kind == "strike_list": return len(d.get("items", []))
    if kind in ("notification", "social"): return 1
    if kind == "phone": return len(d.get("screen", d.get("items", [])))
    if kind == "compare":
        return len(d.get("left", (None, []))[1]) + len(d.get("right", (None, []))[1])
    # generated frames (frame_synth) reveal per data.items (the template's {{#items}} loop)
    try:
        import frame_synth as _fsyn
        if kind in _fsyn.kinds():
            return len(d.get("items", []))
    except Exception:
        pass
    return 0

def _reveal_plan(st, en, n):
    """Return (start, interval, times[]) spreading n item-reveals across the scene span."""
    if n < 2: return None
    start = st + 0.45
    span = max(0.6, (en - st) - 0.8)
    interval = min(0.55, max(0.22, span / n))
    return start, interval, [round(start + j * interval, 3) for j in range(n)]


def _spring_ease_path(stiffness=140.0, mass=1.0, damping=13.0, steps=46):
    """Port of Remotion's damped-spring solver → a GSAP CustomEase path (physics motion GSAP eases lack).
    Under-damped (ζ<1) overshoots then settles with a subtle secondary micro-bounce = 'alive' hero motion.
    Deterministic + seek-safe (it's just an ease curve). Returns an SVG-ish CustomEase path 'M0,0 L…L1,1'."""
    import math
    zeta = damping / (2 * math.sqrt(stiffness * mass))
    w0 = math.sqrt(stiffness / mass)
    def _v(t):
        if zeta < 1:
            wd = w0 * math.sqrt(1 - zeta * zeta)
            return 1 - math.exp(-zeta * w0 * t) * (math.cos(wd * t) + (zeta * w0 / wd) * math.sin(wd * t))
        return 1 - math.exp(-w0 * t) * (1 + w0 * t)
    T = -math.log(0.006) / (zeta * w0)                 # settle time (envelope decayed)
    pts = [(i / steps, _v(T * i / steps)) for i in range(steps + 1)]
    pts[-1] = (1.0, 1.0)
    return "M0,0 " + " ".join(f"L{x:.4f},{y:.4f}" for x, y in pts[1:])


def _comp_item_texts(comp):
    """Ordered per-item label strings for a list-like component, so its item reveals can sync to WHEN
    each is spoken. Returns [] for non-list components (they keep the even spread)."""
    if not comp:
        return []
    kind = comp[0]
    d = comp[1] if len(comp) > 1 else {}
    if not isinstance(d, dict):
        return []
    def _s(x):
        if isinstance(x, (list, tuple)):
            return " ".join(str(v) for v in x)
        if isinstance(x, dict):
            return str(x.get("text") or x.get("title") or x.get("label") or x.get("name") or x.get("value") or "")
        return str(x)
    if kind in ("checklist", "steps", "icongrid", "chiprow", "feature", "badges", "bars", "alert", "filetree"):
        return [_s(it) for it in d.get("items", [])]
    if kind == "hub":
        return [str(n) for n in d.get("nodes", [])]
    if kind == "stat_grid":
        return [_s(s) for s in (d.get("stats") or d.get("items") or [])]
    if kind == "layer_stack":
        return [_s(l) for l in d.get("layers", [])]
    if kind == "ticker_feed":
        return [_s(it) for it in d.get("items", [])]
    if kind == "org_diagram":
        return [_s(n) for n in d.get("nodes", [])]
    return []


def _item_reveal_times(comp, grp, rstart, rint, n):
    """Reveal time per item, SYNCED to when its keyword is spoken in the scene's word list `grp`
    (HyperFrames voice-first principle — content builds as the narration NAMES it, not on a blind
    timer). Monotonic, ≥0.2s apart (readable); any unmatched item falls back to the even rstart+k*rint.
    'nội dung/icon bám sát voice hơn'."""
    even = [round(rstart + k * rint, 3) for k in range(n)]
    texts = _comp_item_texts(comp)
    if not grp or n < 2 or len(texts) != n:
        return even
    try:
        import beat_timing as _bt
        # guard the WHOLE body: malformed word-timing (an explicit null "start", odd keyword text) must not
        # crash — this runs in the main render tween loop (line ~2601), so a raise here would kill the whole
        # video. Fall back to the already-computed even reveal times.
        win_s = float(grp[0].get("start", rstart))
        win_e = float(grp[-1].get("end", rstart + n * rint))
        last = rstart - 0.2
        out = []
        for k in range(n):
            found = _bt._find_appear(grp, _bt._keywords(texts[k]), win_s, win_e, last + 0.2)
            t = even[k] if found is None else round(max(found - 0.06, last + 0.2), 3)
            t = min(max(t, rstart), max(rstart, win_e - 0.15))     # stay in the scene window
            out.append(t)
            last = t
        return out
    except Exception:
        return even

def _sfx_cues(groups, scenes, TOTAL, seed=""):
    """Build (time, file, volume) SFX cues from scene timing + component kinds.
    - transition swish/whoosh at every scene change (variant rotated per-video via effect_library)
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
            key = SFX["transition"][el.sfx_variant(i - 1, len(SFX["transition"]), seed)]
            add(st - 0.15, key, 0.42)               # whoosh/swish on the cut (per-video rotation)
        comp = sc.get("comp")
        kind = comp[0] if comp else None
        reveal = st + (0.0 if i == 0 else 0.24)     # .comp tween lands at st+0.24
        en = grp[-1]["end"]
        n = _reveal_count(comp)
        plan = _reveal_plan(st, en, n)
        if plan:                                    # per-item SFX rides the SAME speech-synced times as the
            _st = _item_reveal_times(comp, grp, plan[0], plan[1], n)   # visual reveal → SFX lands as spoken
            plan = (plan[0], plan[1], _st)
        _fxsfx = (sc.get("fx") or {}).get("sfx")    # writer's explicit SFX override (else auto-by-kind)
        if i == len(scenes) - 1:                     # SKILL-AUTO closer-suppression: the last (CTA) beat gets
            pass                                      # NO audio sting — the brain wants closure; visual pop stays
        elif _fxsfx:
            add(reveal - 0.05, _fxsfx, 0.44)
        elif kind == "terminal":
            # DEMONSTRATE the install (user 2026-07-03): panel opens → keystroke per command line as it
            # types in → success "ding" on the ✓ line. Falls back to a single keyboard bed if no reveal plan.
            _tlines = (comp[1] or {}).get("lines", []) if comp else []
            if plan and plan[2]:
                add(st - 0.08, "impact_soft", 0.34)          # bảng terminal mở ra
                for j, t in enumerate(plan[2]):
                    row = _tlines[j] if j < len(_tlines) else None
                    is_ok = isinstance(row, (list, tuple)) and len(row) >= 1 and row[0] != "$"
                    add(t, "ui_success" if is_ok else "typing", 0.44 if is_ok else 0.26)
            else:
                add(reveal, "typing", 0.22)
        elif plan:                                  # build-on list: a soft pop per item
            for t in plan[2]:
                add(t, "ui_pop", 0.34)
        elif kind in _COMP_SFX:
            key, vol, lead = _COMP_SFX[kind]
            sem = _semantic_sfx(f"{sc.get('kicker','')} {sc.get('h1','')} {sc.get('h2','')}")
            if sem:                                 # content-aware accent overrides the default
                key, vol = sem
            add(reveal - lead, key, vol)
    return cues


def _snap_cues_to_beats(cues, audio_file, total, looped=True, window=0.22):
    """SFX 'hợp lý hơn' (music-to-video idea, adapted for voice-first content): nudge ONLY the transition
    whoosh cues onto the nearest BGM onset so the cut hits WITH the music — scene timing (voice) is untouched,
    the whoosh just lands on the beat within ±`window`. Best-effort: any failure returns cues unchanged.
    librosa (already in env). `looped` tiles a single track's onsets across the whole video."""
    try:
        if not audio_file or not os.path.exists(audio_file):
            return cues
        import bisect
        import librosa
        y, sr = librosa.load(audio_file, sr=22050, mono=True)
        ons = [float(o) for o in librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=True)]
        if not ons:
            return cues
        if looped:                                   # single track is stream-looped → tile its onsets
            L = float(librosa.get_duration(y=y, sr=sr)) or (total + 1)
            grid, k = [], 0
            while k * L < total + 1 and len(grid) < 4000:
                grid += [o + k * L for o in ons if o + k * L <= total]
                k += 1
            ons = grid
        ons = sorted(o for o in ons if 0.2 <= o <= total)
        if not ons:
            return cues
        out, moved = [], 0
        for (t, path, vol) in cues:
            p = str(path)
            if "transition" in p or "whoosh" in p or "swish" in p:
                i = bisect.bisect_left(ons, t)
                cand = [ons[j] for j in (i - 1, i) if 0 <= j < len(ons)]
                if cand:
                    near = min(cand, key=lambda o: abs(o - t))
                    if abs(near - t) <= window:
                        t = round(max(0.0, near - 0.02), 3); moved += 1
            out.append((t, path, vol))
        if moved:
            print(f"[beat-sfx] snapped {moved} transition cue(s) to the BGM beat (±{window}s)")
        return out
    except Exception:
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


def _prograil(i, total, acc, hero=False):
    """A persistent story-style PROGRESS RAIL (segments) at the top of each scene showing i/total —
    a numbered-series structure device (from the Shorts-Studio reference). Filled up to the current
    scene; muted after. Skipped for a 1-scene video."""
    if not total or total < 2:
        return ""
    fill = "#ffffff" if hero else acc
    empt = "rgba(255,255,255,.30)" if hero else "rgba(15,23,42,.13)"
    segs = "".join(f'<div class="pr-seg" style="background:{fill if k <= i else empt}"></div>'
                   for k in range(total))
    return f'<div class="prograil">{segs}</div>'


def _ff(v, dflt=0.0):
    """Safe float for render-path scalar data (LLM/template coords, fractions, counts). A present-but-non-
    numeric value ("N/A", a stray string, None) defaults instead of crashing the render — the same
    discipline gauge/donut/pie already apply to their float() coercions (batch-resilience, hot path)."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return dflt


def _ii(v, dflt=0):
    """Safe int (tolerates '3.0'/3.0) for render-path counts; defaults rather than crashing on bad input."""
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return dflt


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
        # craft-study §1: strike=True → red diagonal over an UNVERIFIED/false number (vids 17,20);
        # delta → a signed +/−/× chip (role-coloured); sub → a small note under the label.
        strike = " bn-strike" if d.get("strike") else ""
        delta = ""
        if d.get("delta"):
            drole = {"success": pal["green"], "danger": pal["orange"], "emphasis": pal["blue"]}.get(
                d.get("delta_role", "success"), pal["green"])
            delta = f'<div class="bn-delta" style="color:{drole};background:{drole}1a">{_esc(d["delta"])}</div>'
        sub = f'<div class="bn-sub">{_esc(d["sub"])}</div>' if d.get("sub") else ""
        return (f'<div class="c-bignum"><div class="bgglow" style="background:radial-gradient(circle,{acc}29 0%,transparent 68%)"></div>'
                f'<div class="big{strike}" style="color:{acc}">{inner}</div>{delta}'
                f'<div class="biglabel">{_esc(d["label"])}</div>{sub}</div>')
    if kind == "photocard":
        # LEARNED from the Shorts-Studio render (2026-07): a real photo in a rounded ACCENT-bordered
        # FRAME, then a structured text block (big step NUMBER → title → description) — cleaner + more
        # premium than a full-bleed photo with text overlaid. Photo comes from image_sourcer; `acc` can
        # be harmonised to the photo's dominant colour (`_acc`, set by the render loop). Karaoke is separate.
        pacc = d.get("_acc") or acc                   # frame + number harmonise to the photo; scene stays brand
        img = (f'<div class="pc-frame" style="border-color:{pacc}"><img src="{_esc(d["img"])}" alt=""/></div>'
               if d.get("img") else "")
        num = _esc(d.get("num", ""))
        tot = f'<span class="pc-tot">/ {_esc(d.get("total"))}</span>' if d.get("total") not in (None, "") else ""
        counter = (f'<div class="pc-count"><span class="pc-num" style="color:{pacc}">{num}</span>{tot}</div>'
                   if str(num) != "" else "")
        title = f'<div class="pc-title">{_esc(d.get("title",""))}</div>' if d.get("title") else ""
        desc = f'<div class="pc-desc">{_esc(d.get("desc",""))}</div>' if d.get("desc") else ""
        return f'<div class="c-photocard">{img}{counter}{title}{desc}</div>'
    if kind == "repo":
        if d.get("img"):                            # REAL screenshot framed as a browser window
            return (f'<div class="c-mockup"><div class="mkbar"><span class="mkdot r"></span>'
                    f'<span class="mkdot y"></span><span class="mkdot g"></span>'
                    f'<span class="mkaddr">{_esc(d.get("url","github.com"))}</span></div>'
                    f'<div class="mkbody"><div class="mkshot"><img src="{_esc(d["img"])}" alt=""/></div></div>'
                    f'<div class="mkcap"><b>{_esc(d["owner"])}/{_esc(d["name"])}</b>'
                    f'<span class="mkstars" style="background:{acc}">★ {_esc(d["stars"])}</span></div></div>')
        tags = "".join(f'<span class="tag">{_esc(t)}</span>' for t in d.get("tags", []))
        return (f'<div class="c-repo"><div class="repo-top"><div class="gh">◉</div>'
                f'<div class="repo-name"><b>{_esc(d["owner"])}</b> / {_esc(d["name"])}</div>'
                f'<div class="stars" style="background:{acc}">★ {_esc(d["stars"])}</div></div>'
                f'<div class="repo-desc">{_esc(d["desc"])}</div><div class="tags">{tags}</div>'
                f'<div class="repo-btn" style="background:{acc}">{_esc(d.get("btn","Xem ngay"))}</div></div>')
    if kind == "compare":
        # Bad side = danger role (coral); winner side = emphasis role (brand blue) so CQA
        # renders #4A60E9 and SEOSONA #2A5BDA. Craft-study §1/§4: add a centre VS badge + a
        # brand-tinted winner-glow. `mode:"beforeafter"` → arrow variant (no ✕/✓).
        lt, li = d["left"]; rt, ri = d["right"]
        win = pal["blue"]
        if d.get("mode") == "beforeafter":
            vs = '<div class="cmp-vs arrow">→</div>'
            lrows = "".join(f'<div class="crow x ritem">{_esc(x)}</div>' for x in li)
            rrows = "".join(f'<div class="crow v ritem" style="color:{win}">{_esc(x)}</div>' for x in ri)
        else:
            vs = '<div class="cmp-vs">VS</div>'
            lrows = "".join(f'<div class="crow x ritem">✕ {_esc(x)}</div>' for x in li)
            rrows = "".join(f'<div class="crow v ritem" style="color:{win}">✓ {_esc(x)}</div>' for x in ri)
        return (f'<div class="c-compare"><div class="col bad"><div class="ctitle bad">{_esc(lt)}</div>{lrows}</div>'
                f'{vs}<div class="col hi" style="border-color:{win};box-shadow:0 24px 60px {win}26">'
                f'<div class="ctitle" style="color:{win}">{_esc(rt)}</div>{rrows}</div></div>')
    if kind == "hub":
        # hub-and-spoke node-diagram (craft-study §4 signature): a centre node + satellites on
        # a ring, dashed connectors, and an optional progress line with a travelling dot. The
        # satellites carry .ritem so they pulse-in one-by-one (the "orbit light-up" motion).
        import math as _m
        S, R = 720, 270; C = S / 2
        center = d.get("center", "HUB"); nodes = d.get("nodes", [])[:8]
        n = max(1, len(nodes)); lines = ""; sats = ""
        for i, nd in enumerate(nodes):
            a = -_m.pi / 2 + i * (2 * _m.pi / n)
            x = C + _m.cos(a) * R; y = C + _m.sin(a) * R
            lines += (f'<line x1="{C}" y1="{C}" x2="{x:.0f}" y2="{y:.0f}" stroke="{acc}" '
                      f'stroke-width="3" stroke-dasharray="5 9" opacity="0.45"/>')
            sats += (f'<div class="hub-sat ritem" style="left:{x:.0f}px;top:{y:.0f}px;'
                     f'border-color:{acc};color:{acc}">{_esc(nd)}</div>')
        prog = (f'<div class="hub-prog"><span class="hub-fill" style="background:{acc}"></span>'
                f'<span class="hub-dot" style="background:{acc};color:{acc}"></span></div>') if d.get("line") else ""
        return (f'<div class="c-hub"><div class="hub-ring" style="width:{S}px;height:{S}px">'
                f'<svg class="hub-svg" viewBox="0 0 {S} {S}">{lines}</svg>'
                f'<div class="hub-center" style="background:{acc}">{_esc(center)}</div>{sats}</div>{prog}</div>')
    if kind == "concept_build":
        # free-form EXPLAINER canvas (SKILL AUTO ConceptBuild): labeled nodes (box/chip/tile/note) at
        # x,y (0–1) + dashed connectors + a `frame` container ("X lives inside Y"). Each node/frame is
        # .ritem so the diagram BUILDS one element at a time in sync with the voice — not a static slide.
        S = 760
        nodes = d.get("nodes", [])[:9]
        _px = lambda v: max(0.0, min(1.0, _ff(v, 0.5))) * S
        lines = ""
        for e in d.get("edges", []):
            if isinstance(e, (list, tuple)) and len(e) >= 2 and e[0] < len(nodes) and e[1] < len(nodes):
                a, b = nodes[e[0]], nodes[e[1]]
                lines += (f'<line x1="{_px(a.get("x",.5)):.0f}" y1="{_px(a.get("y",.5)):.0f}" '
                          f'x2="{_px(b.get("x",.5)):.0f}" y2="{_px(b.get("y",.5)):.0f}" stroke="{acc}" '
                          f'stroke-width="3" stroke-dasharray="4 8" opacity="0.4" marker-end="url(#cbar)"/>')
        frames = ""
        for fr in d.get("frames", []):
            frames += (f'<div class="cb-frame ritem" style="left:{_px(fr.get("x",.1)):.0f}px;'
                       f'top:{_px(fr.get("y",.1)):.0f}px;width:{_px(fr.get("w",.4)):.0f}px;'
                       f'height:{_px(fr.get("h",.3)):.0f}px;border-color:{acc}">'
                       f'<span class="cb-flabel" style="color:{acc}">{_esc(fr.get("label",""))}</span></div>')
        nhtml = ""
        for nd in nodes:
            shp = nd.get("shape", "box")
            col = role_color(nd.get("role")) if nd.get("role") else acc
            nhtml += (f'<div class="cb-node cb-{shp} ritem" style="left:{_px(nd.get("x",.5)):.0f}px;'
                      f'top:{_px(nd.get("y",.5)):.0f}px;--nc:{col}">{_esc(nd.get("label",""))}</div>')
        return (f'<div class="c-cb" style="width:{S}px;height:{S}px">'
                f'<svg class="cb-svg" viewBox="0 0 {S} {S}"><defs><marker id="cbar" markerWidth="8" '
                f'markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{acc}"/>'
                f'</marker></defs>{lines}</svg>{frames}{nhtml}</div>')
    if kind == "comparison_grid":
        # feature matrix (SKILL AUTO): N columns × M feature rows, a WINNER column highlighted. Each
        # row .ritem so it fills in as the speaker reads it. ✓/✕ cells carry meaning (green/coral).
        cols = d.get("cols", [])[:4]
        cn = [((c.get("name"), c.get("winner")) if isinstance(c, dict) else (str(c), False)) for c in cols]
        head = ('<div class="cg-row cg-head"><div class="cg-cell cg-feat"></div>' + "".join(
            f'<div class="cg-cell cg-col{" win" if w else ""}" style="--wc:{acc}">{_esc(n)}</div>' for n, w in cn) + "</div>")
        body = ""
        for r in d.get("rows", []):
            if isinstance(r, dict):
                feat, cells = r.get("feature", ""), r.get("cells", [])
            elif isinstance(r, (list, tuple)) and r:
                feat, cells = r[0], list(r[1:])
            else:
                continue
            cs = ""
            for k, cell in enumerate(cells[:len(cn)]):
                v = str(cell).strip().lower()
                cls = "cg-yes" if v in ("✓", "yes", "có", "true", "1") else ("cg-no" if v in ("✕", "x", "no", "không", "false", "0") else "")
                mark = "✓" if cls == "cg-yes" else ("✕" if cls == "cg-no" else _esc(str(cell).strip()))
                win = cn[k][1] if k < len(cn) else False
                cs += f'<div class="cg-cell {cls}{" win" if win else ""}" style="--wc:{acc}">{mark}</div>'
            body += f'<div class="cg-row ritem"><div class="cg-cell cg-feat">{_esc(feat)}</div>{cs}</div>'
        return f'<div class="c-cg">{head}{body}</div>'
    if kind == "split_reveal":
        # before/after: two framed images + a glowing divider. Images auto-sourced by concept at render
        # time (like photocard) into left._img/right._img; falls back to a labelled placeholder panel.
        def _side(s, cls):
            s = s if isinstance(s, dict) else {"label": str(s)}
            img = s.get("_img") or s.get("img")
            inner = (f'<img src="{_esc(img)}" alt=""/>' if img
                     else f'<div class="sr-ph" style="color:{acc}">{_esc(s.get("concept") or "…")}</div>')
            tag = f'<div class="sr-tag" style="background:{acc}">{_esc(s.get("label", ""))}</div>' if s.get("label") else ""
            return f'<div class="sr-side {cls} ritem">{inner}{tag}</div>'
        return (f'<div class="c-sr">{_side(d.get("left", {}), "sr-l")}'
                f'<div class="sr-div" style="background:{acc}"></div>{_side(d.get("right", {}), "sr-r")}</div>')
    if kind == "annotated_screenshot":
        # a screenshot with corner-bracket highlight boxes + dimmed surround (SKILL AUTO). marks .ritem.
        img = d.get("_img") or d.get("img")
        marks = ""
        for m in d.get("marks", [])[:4]:
            marks += (f'<div class="as-mark ritem" style="left:{_ff(m.get("x",.1))*100:.1f}%;'
                      f'top:{_ff(m.get("y",.1))*100:.1f}%;width:{_ff(m.get("w",.3))*100:.1f}%;'
                      f'height:{_ff(m.get("h",.15))*100:.1f}%;border-color:{acc}">'
                      + (f'<span class="as-lab" style="background:{acc}">{_esc(m.get("label"))}</span>' if m.get("label") else "")
                      + "</div>")
        media = (f'<img src="{_esc(img)}" alt=""/>' if img else f'<div class="as-ph">screenshot</div>')
        return f'<div class="c-as">{media}<div class="as-dim"></div>{marks}</div>'
    if kind == "stat_grid":
        # grid of mini-stat cells (SKILL AUTO StatGrid): value + label + optional delta. Each cell
        # .ritem so it pops as the speaker names it. cols auto-pick by count (2 or 3 wide).
        stats = d.get("stats") or d.get("items") or []
        stats = stats[:6]
        cols = 3 if len(stats) > 4 else 2
        cells = ""
        for s in stats:
            s = s if isinstance(s, dict) else {"value": str(s)}
            delta = s.get("delta")
            up = not str(delta).strip().startswith("-")
            dhtml = (f'<span class="sg-delta" style="color:{"#16A34A" if up else "#E2724D"}">{_esc(delta)}</span>'
                     if delta not in (None, "") else "")
            cells += (f'<div class="sg-cell ritem"><div class="sg-val" style="color:{acc}">{_esc(s.get("value",""))}</div>'
                      f'<div class="sg-lab">{_esc(s.get("label",""))}</div>{dhtml}</div>')
        return f'<div class="c-sg" style="grid-template-columns:repeat({cols},1fr)">{cells}</div>'
    if kind == "ratio_dots":
        # X-of-Y proportion (SKILL AUTO RatioDots): a grid of Y dots, X of them filled/accent to read a
        # ratio at a glance. whole unit is one .ritem (single reveal — the flip is the moment).
        import math as _m
        total = max(1, min(60, _ii(d.get("total", 10), 10)))
        marked = max(0, min(total, _ii(d.get("marked", 0), 0)))
        cols = int(_m.ceil(_m.sqrt(total)))
        dots = ""
        for i in range(total):
            on = i < marked
            dots += (f'<span class="rd-dot" style="background:{acc if on else "#E2E8F0"};'
                     f'{"box-shadow:0 0 12px "+acc if on else ""}"></span>')
        cap = f'<div class="rd-cap" style="color:{acc}">{_esc(d.get("caption",""))}</div>' if d.get("caption") else ""
        big = f'<div class="rd-big" style="color:{acc}">{marked}/{total}</div>' if d.get("show_number", True) else ""
        return (f'<div class="c-rd ritem">{big}<div class="rd-grid" style="grid-template-columns:repeat({cols},1fr)">'
                f'{dots}</div>{cap}</div>')
    if kind == "layer_stack":
        # stacked slabs foundation→top (SKILL AUTO LayerStack): "X sits on Y sits on Z". Each layer
        # .ritem so the stack BUILDS. Optional glyph + sub-line; one layer can be accented.
        title = d.get("title", "")
        layers = d.get("layers", [])[:6]
        rows = ""
        for ly in layers:
            ly = ly if isinstance(ly, dict) else {"label": str(ly)}
            hot = ly.get("accent")
            bc = acc if hot else "#E2E8F0"
            glyph = f'<span class="ls-glyph">{_esc(ly.get("glyph",""))}</span>' if ly.get("glyph") else ""
            sub = f'<span class="ls-sub">{_esc(ly.get("sub",""))}</span>' if ly.get("sub") else ""
            rows += (f'<div class="ls-layer ritem" style="border-color:{bc};'
                     f'{"background:color-mix(in srgb,"+acc+" 8%,#fff)" if hot else ""}">'
                     f'{glyph}<span class="ls-lab">{_esc(ly.get("label",""))}</span>{sub}</div>')
        thd = f'<div class="ls-title" style="color:{acc}">{_esc(title)}</div>' if title else ""
        return f'<div class="c-ls">{thd}{rows}</div>'
    if kind == "ticker_feed":
        # live activity feed (SKILL AUTO TickerFeed): rows enter top; each = glyph + label + body +
        # time. Each row .ritem so the feed accumulates in sync with the voice.
        items = d.get("items", [])[:6]
        rows = ""
        for it in items:
            it = it if isinstance(it, dict) else {"text": str(it)}
            glyph = f'<span class="tf-glyph" style="color:{acc}">{_esc(it.get("glyph","▪"))}</span>'
            lab = f'<span class="tf-lab" style="color:{acc}">{_esc(it.get("label",""))}</span>' if it.get("label") else ""
            tm = f'<span class="tf-time">{_esc(it.get("time",""))}</span>' if it.get("time") else ""
            rows += (f'<div class="tf-row ritem" style="border-left-color:{acc}">{glyph}'
                     f'<span class="tf-body">{lab}{_esc(it.get("text",""))}</span>{tm}</div>')
        return f'<div class="c-tf">{rows}</div>'
    if kind == "org_diagram":
        # parent node + a grid of children with connector lines (SKILL AUTO OrgDiagram). A child can be
        # `kept` (accent) or `dim` (faded + ✕). Parent first, then children each .ritem.
        parent = d.get("parent", "")
        nodes = d.get("nodes", [])[:12]
        n = max(1, len(nodes))
        cols = 4 if n > 6 else (3 if n > 4 else n)
        kids = ""
        for nd in nodes:
            nd = nd if isinstance(nd, dict) else {"label": str(nd)}
            kept, dim = nd.get("kept"), nd.get("dim")
            bc = acc if kept else "#E2E8F0"
            x = '<span class="od-x">✕</span>' if dim else ""
            kids += (f'<div class="od-node ritem{" od-dim" if dim else ""}" style="border-color:{bc};'
                     f'{"background:color-mix(in srgb,"+acc+" 8%,#fff)" if kept else ""}">'
                     f'{_esc(nd.get("label",""))}{x}</div>')
        phtml = f'<div class="od-parent ritem" style="background:{acc}">{_esc(parent)}</div>' if parent else ""
        return (f'<div class="c-od">{phtml}<div class="od-stem" style="background:{acc}"></div>'
                f'<div class="od-grid" style="grid-template-columns:repeat({cols},1fr)">{kids}</div></div>')
    if kind == "terminal":
        rows = ""
        for row in d.get("lines", []):
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                k2, txt = row[0], row[1]
            else:                                        # a bare string → treat as a command line ("$ …")
                k2, txt = "$", str(row)
            if k2 == "$": rows += f'<div class="tline ritem"><span class="prompt">$</span> {_esc(txt)}</div>'
            else: rows += f'<div class="tline ok ritem" style="color:{acc}">✓ {_esc(txt)}</div>'
        rows += f'<div class="tline tcur"><span class="prompt">$</span> <span class="tcaret" style="background:{acc}"></span></div>'
        return (f'<div class="c-term"><div class="term-bar"><span class="dot r"></span><span class="dot y"></span>'
                f'<span class="dot g"></span><span class="term-title">{_esc(d.get("title","seosona@ai: ~"))}</span></div>'
                f'<div class="term-body">{rows}</div></div>')
    if kind == "steps":
        rows = "".join(f'<div class="step ritem"><span class="snum" style="background:{acc}">{i+1}</span>'
                       f'<div><b>{_esc(t)}</b><span>{_esc(s)}</span></div></div>' for i,(t,s) in enumerate(d["items"]))
        return f'<div class="c-steps">{rows}</div>'
    if kind == "checklist":
        # status list (craft-study §1, video-23 roadmap): each row a state badge.
        #   done→success ✓ · doing→caution ◐ · locked→baseline 🔒 · plain "" → ✓.
        STAT = {"done": ("✓", pal["green"]), "doing": ("◐", "#D97706"),
                "locked": ("🔒", "#94A3B8"), "": ("✓", pal["green"])}
        rows = ""
        for it in d["items"]:
            if isinstance(it, (list, tuple)):
                txt = it[0]; stt = it[1] if len(it) > 1 else "done"
            else:
                txt, stt = it, "done"
            mk, col = STAT.get(stt, STAT["done"])
            dim = " chk-dim" if stt == "locked" else ""
            rows += (f'<div class="chk ritem{dim}"><span class="chk-b" style="color:{col};border-color:{col}">{mk}</span>'
                     f'<span class="chk-t">{_esc(txt)}</span></div>')
        return f'<div class="c-checklist">{rows}</div>'
    if kind == "icongrid":
        # 2-col category grid (craft-study §1, videos 02/44): each tile a tinted-icon + label.
        # Colour is CATEGORICAL (wayfinding, not good/bad) — a fixed cycle unless a tile gives its own.
        CATS = [pal["blue"], pal["green"], "#D97706", pal["orange"], "#7C3AED", "#0EA5E9"]
        cells = ""
        for i, it in enumerate(d["items"]):
            emoji = it[0] if len(it) >= 1 else "•"
            lab = it[1] if len(it) >= 2 else ""
            col = it[2] if len(it) >= 3 and it[2] else CATS[i % len(CATS)]
            cells += (f'<div class="ig-cell ritem"><span class="ig-ic" style="background:{col}1a;color:{col}">{_tile_icon(emoji, col, 42)}</span>'
                      f'<span class="ig-lab">{_esc(lab)}</span></div>')
        return f'<div class="c-icongrid">{cells}</div>'
    if kind == "alert":
        # danger / caution callout (craft-study §1, videos 20/36): role-coloured bordered card.
        # danger → dashed coral border + ⚠ ; caution → solid amber border + ◑ ("verify/reality-check").
        r = d.get("role", "caution")
        col = pal["orange"] if r == "danger" else "#D97706"
        bg, bd = ("var(--badbg)", pal["orange"]) if r == "danger" else ("var(--warnbg)", "#D97706")
        style = "dashed" if r == "danger" else "solid"
        icon = "⚠️" if r == "danger" else "🔎"
        if d.get("items"):
            body = "".join(f'<div class="al-row ritem" style="--m:{col}">{_esc(x)}</div>' for x in d["items"])
        else:
            body = f'<div class="al-text">{_esc(d.get("text",""))}</div>' if d.get("text") else ""
        title = (f'<div class="al-title" style="color:{col}"><span class="al-ic">{icon}</span>'
                 f'{_esc(d.get("title",""))}</div>') if d.get("title") else ""
        return f'<div class="c-alert" style="background:{bg};border:3px {style} {bd}">{title}{body}</div>'
    if kind == "filetree":
        # repo file-tree card (craft-study §1) — a window-chrome card whose rows reveal one-by-one.
        # items: (icon, name[, meta]) tuples. Header = the folder/repo name.
        hdr = f'<div class="ft-path">{_esc(d["title"])}</div>' if d.get("title") else ""
        rows = ""
        for it in d["items"]:
            ic = it[0] if len(it) >= 2 else "📄"
            nm = it[1] if len(it) >= 2 else it[0]
            meta = f'<span class="ft-meta">{_esc(it[2])}</span>' if len(it) >= 3 and it[2] else ""
            rows += (f'<div class="ft-row ritem"><span class="ft-ic">{_esc(ic)}</span>'
                     f'<span class="ft-nm">{_esc(nm)}</span>{meta}</div>')
        return (f'<div class="c-filetree"><div class="ft-bar"><span class="dot r"></span>'
                f'<span class="dot y"></span><span class="dot g"></span>{hdr}</div>'
                f'<div class="ft-body">{rows}</div></div>')
    if kind == "bars":
        # horizontal score/compare bars (craft-study §1, videos 35/07/20). items: (label, pct[, color[, value]]).
        # single-series → accent; multi → categorical cycle (or per-entity colour when given).
        CATS = [pal["blue"], pal["green"], "#D97706", pal["orange"]]
        single = len(d["items"]) == 1
        rows = ""
        for i, it in enumerate(d["items"]):
            lab = it[0]; pct = max(0, min(100, it[1]))
            col = it[2] if len(it) >= 3 and it[2] else (acc if single else CATS[i % len(CATS)])
            val = it[3] if len(it) >= 4 else f"{it[1]}%"
            rows += (f'<div class="bar-row ritem"><div class="bar-top"><span class="bar-lab">{_esc(lab)}</span>'
                     f'<span class="bar-val" style="color:{col}">{_esc(str(val))}</span></div>'
                     f'<div class="bar-tr"><span class="bar-fl" style="width:{pct}%;background:{col}"></span></div></div>')
        return f'<div class="c-bars">{rows}</div>'
    if kind == "chiprow":
        # compat/tool chip row (craft-study §1) — pills reveal one-by-one (var: outline or solid).
        solid = d.get("solid")
        st = (f'background:{acc};color:#fff;border-color:{acc}' if solid else f'border-color:{acc};color:{acc}')
        chips = "".join(f'<span class="crx ritem" style="{st}">{_esc(x)}</span>' for x in d["items"])
        return f'<div class="c-chiprow">{chips}</div>'
    if kind == "badges":
        return '<div class="c-badges">' + "".join(
            f'<span class="badge ritem" style="border-color:{acc};color:{acc}">{_esc(x)}</span>' for x in d["items"]) + '</div>'
    if kind == "stats":
        # up to 3 number cards side by side. data: {"items":[(num,label), ...]}
        cells = "".join(f'<div class="stat ritem"><div class="stnum" style="color:{acc}">{_esc(n)}</div>'
                        f'<div class="stlab">{_esc(l)}</div></div>' for n, l in d["items"][:3])
        return f'<div class="c-stats">{cells}</div>'
    if kind == "ring":
        # circular progress gauge — the data-viz family we lacked (only horizontal bars before).
        # SVG stroke-dashoffset (single numeric property → seek-safe; static-final + reveal, like bars).
        # data: {"pct": 0-100, "label": "...", "center": "<override, e.g. 9/10>"}
        import math as _m
        pct = max(0.0, min(100.0, float(d.get("pct", 0) or 0)))
        circ = 2 * _m.pi * 52
        off = round(circ * (1 - pct / 100.0), 1)
        center = _esc(d.get("center") or f"{int(round(pct))}%")
        lab = f'<div class="ring-lab">{_esc(d["label"])}</div>' if d.get("label") else ""
        return (f'<div class="c-ring ritem"><svg class="ring-svg" viewBox="0 0 120 120">'
                f'<circle cx="60" cy="60" r="52" fill="none" stroke="#E6EAF2" stroke-width="11"/>'
                f'<circle cx="60" cy="60" r="52" fill="none" stroke="{acc}" stroke-width="11" stroke-linecap="round" '
                f'stroke-dasharray="{round(circ, 1)}" stroke-dashoffset="{off}" transform="rotate(-90 60 60)"/></svg>'
                f'<div class="ring-num" style="color:{acc}">{center}</div>{lab}</div>')
    if kind == "linechart":
        # trend line over time (traffic/ranking/revenue by month) — the data-viz family's TIME-SERIES member
        # (ring = one ratio, bars = compare categories, this = a trend/growth arc). Static-final SVG polyline
        # + whole-unit .ritem reveal → seek-safe, same low risk as ring. viewBox units == container px (1:1)
        # so dots stay circular and x-labels align by %. data: {"points":[(label,value),...]} OR
        # {"values":[...],"labels":[...]}, optional "label" caption.
        pts = d.get("points")
        if pts:
            _pp = []                              # guard like donut/pie: drop a malformed point (non-numeric
            for p in pts[:8]:                     # value) rather than crash the render; keep label↔value aligned
                try:
                    _pp.append((str(p[0]), float(p[1])))
                except (TypeError, ValueError, IndexError):
                    pass
            labels = [a for a, _b in _pp]
            vals = [b for _a, b in _pp]
        else:
            vals = []
            for v in (d.get("values") or [])[:8]:
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
            labels = [str(x) for x in (d.get("labels") or [])][:8]
        if len(vals) >= 2:
            W, H = 840.0, 360.0
            padL, padR, padT, padB = 24, 24, 26, 54
            vmin, vmax = min(vals), max(vals)
            rng = (vmax - vmin) or 1.0
            n = len(vals)
            xs = [padL + (W - padL - padR) * i / (n - 1) for i in range(n)]
            ys = [padT + (H - padT - padB) * (1 - (v - vmin) / rng) for v in vals]
            line_pts = " ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in zip(xs, ys))
            base_y = round(H - padB, 1)
            area_pts = f"{round(xs[0], 1)},{base_y} {line_pts} {round(xs[-1], 1)},{base_y}"
            dots = "".join(f'<circle cx="{round(x, 1)}" cy="{round(y, 1)}" r="8" fill="{acc}"/>' for x, y in zip(xs, ys))
            dots += (f'<circle cx="{round(xs[-1], 1)}" cy="{round(ys[-1], 1)}" r="14" fill="none" '
                     f'stroke="{acc}" stroke-width="4"/>')          # emphasise the latest point
            xlabs = "".join(f'<div class="lc-x" style="left:{round(x / W * 100, 2)}%">{_esc(l)}</div>'
                            for x, l in zip(xs, labels) if l)
            cap = f'<div class="lc-lab">{_esc(d["label"])}</div>' if d.get("label") else ""
            return (f'<div class="c-linechart ritem"><div class="lc-plot">'
                    f'<svg class="lc-svg" viewBox="0 0 840 360" preserveAspectRatio="none">'
                    f'<line x1="{padL}" y1="{base_y}" x2="{round(W - padR, 1)}" y2="{base_y}" stroke="#E6EAF2" stroke-width="2"/>'
                    f'<polygon points="{area_pts}" fill="{acc}" opacity="0.09"/>'
                    f'<polyline class="lc-line" points="{line_pts}" fill="none" stroke="{acc}" stroke-width="5" '
                    f'stroke-linejoin="round" stroke-linecap="round"/>{dots}'
                    f'<circle class="lc-flow" r="9" cx="0" cy="0" fill="#fff" stroke="{acc}" stroke-width="4" opacity="0"/></svg>'
                    f'<div class="lc-xlabels">{xlabs}</div></div>{cap}</div>')
    if kind == "donut":
        # part-to-whole breakdown (device split, market share, budget allocation) — the data-viz family's
        # composition member (ring = ONE ratio, this = MANY parts of a whole). Each segment is a full circle
        # with stroke-dasharray "seg gap" + dashoffset to its start → static-final, seek-safe like ring.
        # data: {"segments":[(label,value),...≤6], "center":"<hole text>", "label":"<caption>"}.
        import math as _m
        parsed = []
        for s in (d.get("segments") or [])[:6]:
            if isinstance(s, (list, tuple)) and len(s) >= 2:
                try:
                    parsed.append((str(s[0]).strip(), max(0.0, float(s[1]))))
                except Exception:
                    pass
        total = sum(v for _, v in parsed)
        if parsed and total > 0:
            circ = 2 * _m.pi * 52
            # FIXED categorical palette (blue→coral→green→amber→purple→slate) — independent of the scene
            # accent so segments never collide (a coral-accent scene must not paint two parts the same coral).
            _PAL = ["#2A5BDA", "#E2724D", "#16A34A", "#EAB308", "#8B5CF6", "#6B7AA8"]
            arcs, legend, cum = "", "", 0.0
            for idx, (lab, val) in enumerate(parsed):
                seg_len = circ * (val / total)
                col = _PAL[idx % len(_PAL)]
                arcs += (f'<circle cx="60" cy="60" r="52" fill="none" stroke="{col}" stroke-width="15" '
                         f'stroke-dasharray="{round(seg_len, 2)} {round(circ - seg_len, 2)}" '
                         f'stroke-dashoffset="{round(-cum, 2)}" transform="rotate(-90 60 60)"/>')
                legend += (f'<div class="dn-li"><span class="dn-sw" style="background:{col}"></span>'
                           f'<span class="dn-lb">{_esc(lab)}</span>'
                           f'<span class="dn-pc">{round(val / total * 100)}%</span></div>')
                cum += seg_len
            cen = f'<div class="dn-cen">{_esc(d["center"])}</div>' if d.get("center") else ""
            cap = f'<div class="dn-cap">{_esc(d["label"])}</div>' if d.get("label") else ""
            return (f'<div class="c-donut ritem"><div class="dn-chart">'
                    f'<svg class="dn-svg" viewBox="0 0 120 120">'
                    f'<circle cx="60" cy="60" r="52" fill="none" stroke="#E6EAF2" stroke-width="15"/>'
                    f'{arcs}</svg>{cen}</div><div class="dn-legend">{legend}</div>{cap}</div>')
    if kind == "pie":
        # SOLID pie (Remotion makePie arc math) — part-to-whole as FILLED wedges (vs donut's ring). Each
        # wedge = an arc-to-centre path, its own .ritem so slices build one-by-one. data: {segments:[(label,
        # value),..≤6], label?:"caption"}. Fixed categorical palette (never the scene accent → no collisions).
        import math as _m
        parsed = []
        for s in (d.get("segments") or [])[:6]:
            if isinstance(s, (list, tuple)) and len(s) >= 2:
                try:
                    parsed.append((str(s[0]).strip(), max(0.0, float(s[1]))))
                except Exception:
                    pass
        total = sum(v for _, v in parsed)
        if parsed and total > 0:
            _PAL = ["#2A5BDA", "#E2724D", "#16A34A", "#EAB308", "#8B5CF6", "#6B7AA8"]
            cx = cy = 60.0; r = 54.0; a0 = -_m.pi / 2
            wedges, legend = "", ""
            for idx, (lab, val) in enumerate(parsed):
                a1 = a0 + (val / total) * 2 * _m.pi
                x0, y0 = cx + r * _m.cos(a0), cy + r * _m.sin(a0)
                x1, y1 = cx + r * _m.cos(a1), cy + r * _m.sin(a1)
                large = 1 if (a1 - a0) > _m.pi else 0
                col = _PAL[idx % len(_PAL)]
                dpath = (f"M{cx:.1f},{cy:.1f} L{x0:.2f},{y0:.2f} "
                         f"A{r:.1f},{r:.1f} 0 {large} 1 {x1:.2f},{y1:.2f} Z")
                wedges += f'<path class="pie-seg ritem" d="{dpath}" fill="{col}" stroke="#fff" stroke-width="1.5"/>'
                legend += (f'<div class="dn-li"><span class="dn-sw" style="background:{col}"></span>'
                           f'<span class="dn-lb">{_esc(lab)}</span>'
                           f'<span class="dn-pc">{round(val / total * 100)}%</span></div>')
                a0 = a1
            cap = f'<div class="dn-cap">{_esc(d["label"])}</div>' if d.get("label") else ""
            return (f'<div class="c-donut c-pie ritem"><div class="dn-chart">'
                    f'<svg class="dn-svg" viewBox="0 0 120 120">{wedges}</svg></div>'
                    f'<div class="dn-legend">{legend}</div>{cap}</div>')
    if kind == "chat":
        # messaging conversation UI (Video-Template craft — ubiquitous in AI content: "you ask → AI answers").
        # Alternating bubbles: user right (accent), assistant left (grey). Each .ritem → the chat BUILDS
        # turn-by-turn in sync with the voice. data: {messages:[{from:"user"|"ai", text:".."}], ..≤6}.
        msgs = d.get("messages") or d.get("items") or []
        rows = ""
        for m in msgs[:6]:
            m = m if isinstance(m, dict) else {"text": str(m)}
            who = str(m.get("from", m.get("who", "ai"))).lower()
            side = "user" if who in ("user", "me", "bạn", "you", "u") else "ai"
            style = f' style="background:{acc}"' if side == "user" else ""
            rows += (f'<div class="ch-row ch-{side} ritem">'
                     f'<div class="ch-bubble"{style}>{_esc(m.get("text", ""))}</div></div>')
        return f'<div class="c-chat">{rows}</div>'
    if kind == "codecard":
        # code / config editor card (Video-Template craft) — filename tab + syntax-lit lines. DISTINCT from
        # `terminal` ($ commands): this shows SOURCE/JSON. Light editor theme (brand = light). Lines .ritem.
        fn = d.get("file") or d.get("title") or "code"
        lines = d.get("lines") or d.get("items") or []
        body = "".join(f'<div class="cc-ln ritem">{_code_hl(str(ln)) or "&nbsp;"}</div>' for ln in lines[:12])
        return (f'<div class="c-codecard"><div class="cc-bar">'
                f'<span class="cc-dot"></span><span class="cc-dot"></span><span class="cc-dot"></span>'
                f'<span class="cc-file">{_esc(fn)}</span></div>'
                f'<div class="cc-body">{body}</div></div>')
    if kind == "tabs":
        # segmented tabs over a list (Video-Template craft: "Cơ bản / Nâng cao" level tabs). One tab ACTIVE
        # (accent), the rest muted; the active tab's items build below. data: {tabs:[..≤4], active:idx,
        # items:[["nội dung","done|doing|locked"?],..≤6]}. Items .ritem → reveal one-by-one with the voice.
        tabs = d.get("tabs", [])[:4]
        active = max(0, min(int(d.get("active", 0) or 0), max(0, len(tabs) - 1)))
        thtml = ""
        for i, t in enumerate(tabs):
            on = i == active
            thtml += (f'<div class="tb-tab{" tb-on" if on else ""}"'
                      + (f' style="background:{acc}"' if on else "") + f'>{_esc(t)}</div>')
        rows = ""
        _ST = {"done": ("✓", "#16A34A"), "doing": ("◐", None), "locked": ("🔒", "#94A3B8")}
        for it in (d.get("items") or [])[:6]:
            it = it if isinstance(it, (list, tuple)) else [str(it)]
            lab = it[0] if it else ""
            st = str(it[1]).lower() if len(it) > 1 else ""
            glyph, col = _ST.get(st, ("", None))
            badge = (f'<span class="tb-badge" style="color:{col or acc}">{glyph}</span>' if glyph else "")
            rows += f'<div class="tb-item ritem">{badge}<span>{_esc(lab)}</span></div>'
        return f'<div class="c-tabs"><div class="tb-bar">{thtml}</div><div class="tb-list">{rows}</div></div>'
    if kind == "gauge":
        # radial gauge / speedometer (Video-Template craft — benchmark/speed score, distinct from `ring`'s
        # simple % circle). 240° arc: grey track + accent fill to value/max + big centre value. data:
        # {value:80,max?:100,unit?:"%",label:"..",display?:"6x"}. Static-final SVG → seek-safe, whole .ritem.
        import math as _m
        try:
            val = float(d.get("value", 0)); mx = float(d.get("max", 100)) or 100.0
        except Exception:
            val, mx = 0.0, 100.0
        frac = max(0.0, min(1.0, val / mx))
        cx = cy = 60.0; r = 50.0
        def _pt(deg):
            a = _m.radians(deg); return (cx + r * _m.sin(a), cy - r * _m.cos(a))
        x0, y0 = _pt(-120); x1, y1 = _pt(120); xf, yf = _pt(-120 + 240 * frac)
        track = f'M{x0:.2f},{y0:.2f} A{r},{r} 0 1 1 {x1:.2f},{y1:.2f}'
        fill = f'M{x0:.2f},{y0:.2f} A{r},{r} 0 {1 if 240 * frac > 180 else 0} 1 {xf:.2f},{yf:.2f}'
        disp = d.get("display") or (str(int(val) if val == int(val) else val) + str(d.get("unit", "")))
        lab = f'<div class="ga-lab">{_esc(d.get("label", ""))}</div>' if d.get("label") else ""
        return (f'<div class="c-gauge ritem"><div class="ga-dial"><svg class="ga-svg" viewBox="0 0 120 120">'
                f'<path d="{track}" fill="none" stroke="#E6EAF2" stroke-width="12" stroke-linecap="round"/>'
                f'<path d="{fill}" fill="none" stroke="{acc}" stroke-width="12" stroke-linecap="round"/></svg>'
                f'<div class="ga-val" style="color:{acc}">{_esc(disp)}</div></div>{lab}</div>')
    if kind == "metric_rows":
        # stacked metric rows (Video-Template craft: "⭐ Stars 4.7K / Forks 1.3K") — icon/dot + label + value,
        # vertical. Distinct from stat_grid (grid of hero numbers). Each row .ritem. data: {rows:[{label,value,
        # icon?},..≤6]} (also accepts [["Stars","4.7K"],..]).
        rows = ""
        for it in (d.get("rows") or d.get("items") or [])[:6]:
            if isinstance(it, dict):
                lab, valx, icon = it.get("label", ""), it.get("value", ""), it.get("icon", "")
            elif isinstance(it, (list, tuple)):
                lab = it[0] if it else ""; valx = it[1] if len(it) > 1 else ""; icon = it[2] if len(it) > 2 else ""
            else:
                lab, valx, icon = str(it), "", ""
            ic = (f'<span class="mr-ic">{_esc(icon)}</span>' if icon
                  else f'<span class="mr-dot" style="background:{acc}"></span>')
            rows += (f'<div class="mr-row ritem">{ic}<span class="mr-lab">{_esc(lab)}</span>'
                     f'<span class="mr-val" style="color:{acc}">{_esc(valx)}</span></div>')
        return f'<div class="c-mrows">{rows}</div>'
    if kind == "pill_stack":
        # vertical option pills (Video-Template craft: "chọn hướng / các gói") — icon + label per pill, one can
        # be `active` (accent). Distinct from chiprow (inline wrap). Each pill .ritem. data: {items:[{label,
        # icon?,active?},..≤5]}.
        rows = ""
        for it in (d.get("items") or [])[:5]:
            it = it if isinstance(it, dict) else {"label": str(it)}
            on = it.get("active")
            style = f' style="background:{acc};color:#fff;border-color:{acc}"' if on else ""
            ic = f'<span class="ps-ic">{_esc(it.get("icon", ""))}</span>' if it.get("icon") else ""
            rows += f'<div class="ps-pill ritem"{style}>{ic}<span>{_esc(it.get("label", ""))}</span></div>'
        return f'<div class="c-pills">{rows}</div>'
    if kind == "people":
        # people/contributor row (Video-Template craft: avatar circle + name + role — team/founder/community).
        # Avatar = photo if given else initials on an accent circle. Each .ritem. data: {items:[{name,role?,
        # img?},..≤5]}.
        rows = ""
        for it in (d.get("items") or [])[:5]:
            it = it if isinstance(it, dict) else {"name": str(it)}
            rows += (f'<div class="pp-row ritem">{_avatar(it.get("name", ""), it.get("img"), acc)}'
                     f'<div class="pp-txt"><div class="pp-name">{_esc(it.get("name", ""))}</div>'
                     + (f'<div class="pp-role">{_esc(it.get("role"))}</div>' if it.get("role") else "")
                     + "</div></div>")
        return f'<div class="c-people">{rows}</div>'
    if kind == "strike_list":
        # "cross out the OLD way" list (Video-Template craft, e.g. Open Slide): each old item gets a strike
        # line drawn through it, then a positive conclusion chip. Strong before→after retention device. Each
        # item .ritem; the strike line animates in the render loop. data: {items:["..",..≤5], conclusion?:".."}.
        rows = ""
        for it in (d.get("items") or [])[:5]:
            rows += (f'<div class="sk-item ritem"><span class="sk-txt">{_esc(str(it))}</span>'
                     f'<span class="sk-line" style="background:{acc}"></span></div>')
        concl = (f'<div class="sk-concl" style="background:{acc}">{_esc(d["conclusion"])}</div>'
                 if d.get("conclusion") else "")
        return f'<div class="c-strike">{rows}{concl}</div>'
    if kind == "notification":
        # MOCKUP: a phone/OS notification card (the honest native replacement for the registry's
        # macos/liquid-glass notification demos — light-brand, filled with the SCENE's real message).
        # data: {app?, title, text, time?}. One .ritem (the whole card slides in).
        app = _esc(d.get("app", "SEOSONA")); tm = _esc(d.get("time", "bây giờ"))
        return (f'<div class="c-notif ritem"><div class="nf-head">'
                f'{_avatar(d.get("app", "S"), d.get("icon"), acc)}'
                f'<span class="nf-app">{app}</span><span class="nf-time">{tm}</span></div>'
                f'<div class="nf-title">{_esc(d.get("title", ""))}</div>'
                f'<div class="nf-text">{_esc(d.get("text", ""))}</div></div>')
    if kind == "social":
        # MOCKUP: a social-post card (native replacement for the x-post/instagram/reddit demos — no fake
        # follower counts; shows the SCENE's own quote/claim). data: {name, handle?, text, likes?, comments?}.
        vf = '<span class="so-vf" style="background:' + acc + '">✓</span>' if d.get("verified", True) else ""
        eng = ""
        if d.get("likes") or d.get("comments"):
            eng = (f'<div class="so-eng"><span>♥ {_esc(d.get("likes", ""))}</span>'
                   f'<span>\U0001f4ac {_esc(d.get("comments", ""))}</span></div>')
        return (f'<div class="c-social ritem"><div class="so-head">'
                f'{_avatar(d.get("name", ""), d.get("img"), acc)}<div class="so-id">'
                f'<div class="so-name">{_esc(d.get("name", ""))}{vf}</div>'
                f'<div class="so-handle">{_esc(d.get("handle", ""))}</div></div></div>'
                f'<div class="so-text">{_esc(d.get("text", ""))}</div>{eng}</div>')
    if kind == "phone":
        # MOCKUP: a REALISTIC iPhone — titanium bezel, dynamic island, status bar (time + signal/wifi/
        # battery), app bar, home indicator (native replacement for app-showcase/ios demos, real content).
        # data: {title, screen:[lines] | items:[..], time?}.
        lines = [x for x in (d.get("screen") or d.get("items") or []) if str(x).strip()][:5]
        body = "".join(f'<div class="ph-line ritem">{_esc(str(l))}</div>' for l in lines)
        _sig = ('<svg class="ph-i" viewBox="0 0 18 12"><rect x="0" y="8" width="3" height="4" rx="1"/>'
                '<rect x="5" y="5" width="3" height="7" rx="1"/><rect x="10" y="2" width="3" height="10" rx="1"/>'
                '<rect x="15" y="0" width="3" height="12" rx="1"/></svg>')
        _wifi = ('<svg class="ph-i" viewBox="0 0 16 12"><path d="M8 11.2 6 8.8a3 3 0 0 1 4 0z"/>'
                 '<path d="M3.3 6.1a7 7 0 0 1 9.4 0" fill="none" stroke="currentColor" stroke-width="1.7"/>'
                 '<path d="M1 3.6a10.5 10.5 0 0 1 14 0" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>')
        _batt = ('<svg class="ph-i" viewBox="0 0 26 12"><rect x="0.7" y="0.7" width="21" height="10.6" rx="2.6" '
                 'fill="none" stroke="currentColor" stroke-width="1.2"/><rect x="2.4" y="2.4" width="15" height="7.2" rx="1.3"/>'
                 '<rect x="23" y="4" width="2" height="4" rx="1"/></svg>')
        return (f'<div class="c-phone"><div class="ph-frame"><div class="ph-island"></div>'
                f'<div class="ph-status"><span class="ph-time">{_esc(d.get("time", "9:41"))}</span>'
                f'<span class="ph-sys">{_sig}{_wifi}{_batt}</span></div>'
                f'<div class="ph-scr"><div class="ph-appbar" style="color:{acc}">'
                f'<span class="ph-dot" style="background:{acc}"></span>{_esc(d.get("title", ""))}</div>'
                f'{body}</div><div class="ph-home"></div></div></div>')
    if kind == "timeline":
        # dated milestones on a spine (roadmap / history / "how X evolved" videos). Pure normal-flow +
        # per-row .ritem reveal — no SVG, lowest render risk. data: {"items":[(date,title[,sub]), ...]}
        rows = ""
        for it in d["items"][:5]:
            date = it[0] if len(it) >= 1 else ""
            title = it[1] if len(it) >= 2 else ""
            sub = it[2] if len(it) >= 3 else ""
            rows += (f'<div class="tl-row ritem"><div class="tl-dot" style="background:{acc}"></div>'
                     f'<div class="tl-body"><div class="tl-date" style="color:{acc}">{_esc(date)}</div>'
                     f'<div class="tl-title">{_esc(title)}</div>'
                     + (f'<div class="tl-sub">{_esc(sub)}</div>' if sub else "") + "</div></div>")
        return f'<div class="c-timeline"><div class="tl-spine" style="background:{acc}"></div>{rows}</div>'
    if kind == "divider":
        # section / chapter divider (oversized index number + label) — a scene archetype we lacked, for
        # multi-part videos ("Phần 1", "Bước 2"). Pure normal-flow. data: {"num":"01","title":"...","sub":"..."}
        sub = f'<div class="dv-sub">{_esc(d["sub"])}</div>' if d.get("sub") else ""
        return (f'<div class="c-divider ritem"><div class="dv-num" style="color:{acc}">{_esc(d.get("num", ""))}</div>'
                f'<div class="dv-title">{_esc(d.get("title", ""))}</div>{sub}</div>')
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
    if kind == "lower-third":
        # broadcast-style attribution label (source / handle / speaker). Re-skinned from capcut-cli's
        # `lower-third` template → brand card w/ accent bar. data: {"title":.., "sub":..}
        sub = f'<div class="l3sub">{_esc(d["sub"])}</div>' if d.get("sub") else ""
        return (f'<div class="c-lower3" style="border-left:8px solid {acc}">'
                f'<div class="l3title">{_esc(d.get("title",""))}</div>{sub}</div>')
    if kind == "callout":
        # punchy highlighted one-liner (re-skinned from capcut-cli `caption-pop`) — solid accent pill,
        # white bold text. For a single high-impact line. data: {"text":..}
        return f'<div class="c-callout" style="background:{acc}"><span>{_esc(d.get("text",""))}</span></div>'
    if kind == "feature":
        # emoji/icon + title (+sub) grid — more visual than steps. data: {"items":[(emoji,title,sub),...]}
        rows = "".join(f'<div class="feat ritem"><span class="femoji">{_tile_icon(e, acc, 54)}</span>'
                       f'<div><b>{_esc(t)}</b>{("<span>"+_esc(s)+"</span>") if s else ""}</div></div>'
                       for e, t, s in d["items"])
        return f'<div class="c-feature">{rows}</div>'
    if kind == "chart":
        # horizontal bar chart (data viz). data: {"title":.., "items":[(label, pct0-100, disp), ...]}
        # disp optional (text shown on the bar); each bar can have its own color via 4th elem.
        cols = [acc, pal["green"], pal["orange"], pal["blue"]]
        rows = ""
        for i, it in enumerate(d["items"]):
            try:
                _raw = float(it[1])               # guard like donut/pie: a non-numeric bar value must not
            except (TypeError, ValueError, IndexError):
                continue                          # crash the whole render — skip the malformed bar instead
            lab, pct = it[0], max(3, min(100, _raw))
            disp = it[2] if len(it) > 2 else f"{int(_raw)}%"
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
        if d.get("img"):                            # REAL screenshot inside the browser chrome
            body = f'<div class="mkshot"><img src="{_esc(d["img"])}" alt=""/></div>'
        elif d.get("tiles"):
            body = '<div class="mktiles">' + "".join(
                f'<div class="mktile ritem"><div class="mktnum" style="color:{acc}">{_esc(n)}</div>'
                f'<div class="mktlab">{_esc(l)}</div></div>' for n, l in d["tiles"][:4]) + '</div>'
        else:
            body = '<div class="mklines">' + "".join(f'<div class="mkline">{_esc(x)}</div>' for x in d.get("lines", [])) + '</div>'
        _lock = ('<svg class="mklock" viewBox="0 0 14 16"><path d="M3 7V5a4 4 0 0 1 8 0v2" fill="none" '
                 'stroke="currentColor" stroke-width="1.6"/><rect x="1.5" y="7" width="11" height="8" rx="2"/></svg>')
        return (f'<div class="c-mockup"><div class="mkbar"><span class="mkdot r"></span>'
                f'<span class="mkdot y"></span><span class="mkdot g"></span>'
                f'<span class="mknav">&#8249;&#8250;&#10227;</span>'
                f'<span class="mkaddr">{_lock}<span class="mkurl">{_esc(url)}</span></span>'
                f'<span class="mkmenu">&#8942;</span></div><div class="mkbody">{body}</div></div>')
    if kind == "cta":
        # named CTA variants (craft-study §7): subscribe (default) / url / star / comment / follow.
        var = d.get("variant", "subscribe")
        logo = '<img class="cta-logo" src="assets/logo.png"/>'
        line = f'<div class="cta-line">{_esc(d.get("line", bk.CTA_DEFAULT_LINE))}</div>'
        if var == "url":
            btn = f'<div class="cta-btn" style="background:{acc}">→ {_esc(d.get("url","seosona.com"))}</div>'
        elif var == "star":
            btn = f'<div class="cta-btn" style="background:{pal["green"]}">★ {_esc(d.get("btn","Star repo ngay"))}</div>'
        elif var == "comment":
            btn = (f'<div class="cta-comment"><span class="cc-txt">{_esc(d.get("keyword","AI"))}</span>'
                   f'<span class="cc-send" style="background:{acc}">➤</span></div>')
        elif var == "follow":
            btn = (f'<div class="cta-follow"><span class="cf-name">{_esc(d.get("name","SEOSONA"))}</span>'
                   f'<span class="cf-btn" style="background:{acc}">+ Theo dõi</span></div>')
        else:
            btn = f'<div class="cta-btn" style="background:{acc}">{_esc(d.get("btn","👉 Theo dõi ngay"))}</div>'
        return f'<div class="c-cta">{logo}{line}{btn}</div>'
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
    # GENERATED FRAME fallback — the kho self-grows: any kind not hard-coded above may be a
    # frame_synth-registered template. Render it from its stored light-brand HTML (seek-safe, .ritem motion).
    try:
        import frame_synth as _fsyn
        _g = _fsyn.render_generated(kind, d, acc)
        if _g:
            return _g
    except Exception:
        pass
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
              "coral": "#E2724D", "badbg": "#FFF7F4", "badbd": "#F4D6CC", "hibg": "#EEF3FC",
              # semantic ROLE tokens (craft-study §3): text/line hue + light card tint per role.
              # danger reuses coral/badbg/badbd above. Components: var(--c_ok)/--okbg, etc.
              "c_emph": "#2A5BDA", "c_ok": "#16A34A", "c_warn": "#D97706", "c_bad": "#E2724D",
              "c_info": "#3A4A6B", "c_base": "#94A3B8",
              "okbg": "#F0FAF3", "okbd": "#CDEBD6", "warnbg": "#FFF9EC", "warnbd": "#F5E4C0",
              "infobg": "#EEF3FC", "infobd": "#D9E3F5"},
    # CQA (Chi Quyết Academy) — fun, creator-focused, indigo. Still 100% light mode.
    "cqa": {"bg": "radial-gradient(125% 80% at 50% 0%,#E9EDFF 0%,#F4F7FF 45%,#FFFFFF 100%)",
              "ink": "#1A1D2B", "ink2": "#3A3F55", "muted": "#6B7088", "card": "#ffffff",
              "cardb": "#E4E8F7", "tagbg": "#EEF1FE", "tagtx": "#3A3F55", "dots": "#C9D2F2",
              "footerbg": "#ffffff", "footertx": "#3A3F55", "kara": "#1A1D2B", "karatx": "#FFFFFF",
              "ghbg": "#1A1D2B", "ghtx": "#ffffff", "fb": "#4A60E9", "dotc": "#10B981",
              "coral": "#FB7185", "badbg": "#FFF5F6", "badbd": "#FBD5DB", "hibg": "#EEF1FE",
              # semantic ROLE tokens (craft-study §3) — CQA hues.
              "c_emph": "#4A60E9", "c_ok": "#10B981", "c_warn": "#D97706", "c_bad": "#FB7185",
              "c_info": "#3A3F55", "c_base": "#94A3B8",
              "okbg": "#ECFDF5", "okbd": "#C7EFDD", "warnbg": "#FFF9EC", "warnbd": "#F5E4C0",
              "infobg": "#EEF1FE", "infobd": "#DAE0FB"},
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


# Semantic ROLE (meaning) → the brand-aware theme token (craft-study §3, brand_kit.ROLES).
_ROLE_KEY = {"emphasis": "c_emph", "success": "c_ok", "danger": "c_bad",
             "caution": "c_warn", "info": "c_info", "baseline": "c_base"}


def role_color(role, brand="seosona"):
    """Semantic role ('danger'/'success'/'caution'/…) → brand hex (light-mode, brand-aware).
    Use this instead of hard-coding a hue so a component's MEANING drives its colour."""
    t = _theme(brand)
    key = _ROLE_KEY.get(role)
    if key and key in t:
        return t[key]
    return bk.ROLES.get(role, role)


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


# --- 9:16 vertical-video SAFE ZONE (single source of truth; base = 1080x1920) ---------------
# Short-form platforms (TikTok / Reels / Shorts) overlay their OWN caption + right-side button
# column over the bottom ~26% and top status bar, so SEOSONA content lives in a defined band and
# is TOP-ANCHORED (the title sits on the SAME line every scene → it never "jumps" between cuts,
# which center-anchoring caused: the head bounced ~224px as component height changed). Content is
# intentionally a touch above the true frame-centre — correct for short-form (the bottom is UI).
SAFE_SIDE = 100            # left/right margin
# 2026-07-02: raised the content band — start higher (fills the empty top) AND end higher (bigger gap
# above the karaoke box at bottom:300 ≈ y1530), so tall components (steps/chart/mockup) no longer
# overflow DOWN into the caption/tag. Band 440→1440 = 1000px workable height.
SAFE_TITLE_TOP = 300       # TOP-zone height (below logo/progress); content is centered in the MID band
SAFE_CONTENT_BOTTOM = 1440 # content must stay above this (karaoke box top ≈1530 → ~90px clearance)
SAFE_BOTTOM_PAD = 1920 - SAFE_CONTENT_BOTTOM   # = 480

def _css(brand="seosona", W=1080, H=1920):
    t = _theme(brand)
    faces = "".join(f"@font-face{{font-family:BVP;src:url('assets/{f}');font-weight:{w}}}" for f,w,_ in FONTS)
    vars_ = ";".join(f"--{k}:{v}" for k, v in t.items())
    # Safe-zone as CSS vars (scaled for non-portrait), so .scene padding has ONE source and the
    # old "stale replace string" bug (scale silently no-op) can't recur.
    vs, hs = H / 1920.0, W / 1080.0
    sz = (f"--sz-top:{int(SAFE_TITLE_TOP*vs)}px;--sz-side:{int(SAFE_SIDE*hs)}px;"
          f"--sz-bot:{int(SAFE_BOTTOM_PAD*vs)}px")
    css = faces + "\n*{margin:0;padding:0;box-sizing:border-box;font-family:BVP,Arial,sans-serif}\n" + \
        "#root{" + vars_ + ";" + sz + ";width:1080px;height:1920px;position:relative;overflow:hidden;background:var(--bg);color:var(--ink)}\n" + """
.dots{position:absolute;inset:0;background-image:radial-gradient(var(--dots) 1.4px,transparent 1.4px);background-size:42px 42px;opacity:.30}
.brandlogo{position:absolute;top:58px;left:64px;width:190px;z-index:60}
.prograil{position:absolute;top:26px;left:var(--sz-side);right:var(--sz-side);height:7px;display:flex;gap:8px;z-index:55}
.prograil .pr-seg{flex:1;border-radius:99px}
/* 3-ZONE SAFE LAYOUT (user 2026-07-03: "safe zone ở từng cụm top/mid/bottom + căn dọc"): TOP zone =
   logo+progress (absolute, y0–~200); MID zone = the content cluster, VERTICALLY CENTERED between the
   top pad and the karaoke; BOTTOM zone = karaoke+footer (absolute). justify-content:center balances the
   cluster instead of dumping it at the top. */
.scene{position:absolute;left:0;top:0;width:1080px;height:1920px;padding:var(--sz-top) var(--sz-side) var(--sz-bot);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}
/* Ambient background depth (house-style.md "Background is not empty"): a breathing
   accent glow + an oversized faint ghost word behind the content. z-index keeps them
   under the text. */
.scbg{position:absolute;inset:0;z-index:0;overflow:hidden;pointer-events:none}
.scglow{position:absolute;left:50%;top:34%;width:1000px;height:1000px;transform:translate(-50%,-50%);border-radius:50%}
.scghost{position:absolute;left:50%;top:58%;transform:translateX(-50%);font-weight:900;font-size:300px;line-height:1;white-space:nowrap;letter-spacing:-6px;text-transform:uppercase}
/* content emoji = a PROMINENT hero icon in the TOP zone (above the centered content, no overlap) — the
   scene shows WHAT the voice says, clearly, not a faint monotone ghost. (user 2026-07-03) */
.scghost-ic{top:19%;letter-spacing:0;text-transform:none;font-size:150px;opacity:.95;filter:drop-shadow(0 10px 22px rgba(20,40,90,.14))}
.scrail{position:absolute;left:48px;top:31%;width:8px;height:38%;border-radius:999px;opacity:.9;z-index:1;box-shadow:0 6px 18px rgba(20,40,90,.10)}   /* persistent left brand rail */
.scnum{position:absolute;right:54px;top:20%;font-weight:900;font-size:210px;line-height:1;color:#0F172A0A;z-index:0;letter-spacing:-6px}   /* ghost chapter numeral 0N */
.scconf span{position:absolute;color:#0F172A09;font-weight:800;font-family:monospace;z-index:0;transform:translate(-50%,-50%);pointer-events:none}   /* code-glyph confetti bg filler */
/* Soft "liquid" depth blobs (brand colours, light-mode). Animated via GSAP (not CSS
   @keyframes) so every captured frame is deterministic. Low opacity = subtle premium depth. */
.scblob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.13;z-index:0;pointer-events:none;will-change:transform}
/* Decorative EFFECT overlays (effect_library), behind content, brand-fit + subtle. Applied sparsely. */
.scfx{position:absolute;inset:0;z-index:0;pointer-events:none;will-change:transform,opacity}
/* Lottie ACCENT (director-picked, content-matched) — framed as a clean WHITE STICKER card in the upper-
   right safe zone (below the progress rail, above the ghost numeral) so a full-colour lottie reads as a
   deliberate motion badge on the light brand, not a stray graphic. Seek-safe (GSAP goToAndStop). */
.sclottie{position:absolute;left:50%;top:8.5%;transform:translateX(-50%);width:230px;height:190px;z-index:2;display:flex;align-items:center;justify-content:center;pointer-events:none;filter:drop-shadow(0 12px 26px rgba(20,40,90,.12))}
.sclottie svg{max-width:100%!important;max-height:100%!important;width:auto!important;height:auto!important}
.scfx.leak{background:radial-gradient(90% 60% at 88% 8%,rgba(226,114,77,.20) 0%,transparent 55%);mix-blend-mode:multiply}
.scfx.bloom{background:radial-gradient(circle at 50% 42%,rgba(42,91,218,.16) 0%,transparent 60%)}
.scene>.kicker,.scene>.head,.scene>.comp{position:relative;z-index:1}
.kicker{font-weight:800;font-size:30px;letter-spacing:3px;padding:14px 30px;border-radius:999px;text-transform:uppercase}
.head{margin-top:38px;text-align:center;line-height:1.08}
.subnote{max-width:840px;margin:14px auto 0;font-weight:500;font-size:32px;color:var(--muted);line-height:1.42;text-align:center}
.head .w{display:inline-block}
.head .l1{display:block;font-weight:900;font-size:80px;letter-spacing:-1px}
.head .l2{display:inline-block;position:relative;font-weight:900;font-size:80px;letter-spacing:-1px}
/* title-hook variant (craft-study §7): mono-filename headline */
.head.hk-mono .l1,.head.hk-mono .l2{font-family:'Consolas','Courier New',monospace;letter-spacing:-3px;font-size:72px}
.l2u{position:absolute;left:2px;right:2px;bottom:-14px;height:8px;border-radius:4px;transform:scaleX(0);transform-origin:left center}
.comp{margin-top:64px;width:100%;display:flex;justify-content:center}
.c-bignum{text-align:center;position:relative}.c-bignum .big{font-weight:900;font-size:225px;line-height:1;letter-spacing:-4px;position:relative;z-index:1}
.c-bignum .bgglow{position:absolute;left:50%;top:44%;width:780px;height:780px;transform:translate(-50%,-50%);border-radius:50%;z-index:0;pointer-events:none}
.c-bignum .biglabel{margin-top:18px;font-weight:800;font-size:34px;letter-spacing:2px;color:var(--muted);position:relative;z-index:1}
/* bignum extras (craft-study §1): red strike = false/unverified number · delta chip · sub note */
.c-bignum .big.bn-strike::after{content:"";position:absolute;left:-5%;top:48%;width:110%;height:12px;
  background:var(--c_bad);transform:rotate(-11deg);border-radius:8px;box-shadow:0 6px 18px rgba(226,114,77,.4);z-index:2}
.c-bignum .bn-delta{display:inline-block;margin-top:22px;padding:10px 26px;border-radius:999px;
  font-weight:900;font-size:44px;letter-spacing:-1px;position:relative;z-index:1}
.c-bignum .bn-sub{margin-top:14px;font-weight:600;font-size:28px;color:var(--muted);position:relative;z-index:1}
.scene.hero .head .l1{color:#0F172A}
.scene.hero .c-bignum .big{color:#2A5BDA!important}
.scene.hero .c-bignum .biglabel{color:#475569}
/* Heights tuned so image + number + title + desc together fit ABOVE the karaoke zone (~740px content
   band). The 4/3 image (675px) + 150px number overflowed into the captions/footer — verified 2026-07-03. */
.c-photocard{width:860px;display:flex;flex-direction:column;align-items:flex-start;text-align:left}
.pc-frame{width:100%;height:420px;border-radius:28px;overflow:hidden;border:3px solid;box-shadow:0 22px 54px rgba(20,40,90,.18);background:var(--card)}
.pc-frame img{width:100%;height:100%;object-fit:cover;display:block}
.c-photocard .pc-count{margin-top:20px;display:flex;align-items:baseline;gap:14px;font-weight:900;line-height:.85}
.c-photocard .pc-num{font-size:100px;letter-spacing:-3px}
.c-photocard .pc-tot{font-size:38px;font-weight:800;color:var(--muted)}
.c-photocard .pc-title{margin-top:6px;font-weight:800;font-size:52px;color:var(--ink);line-height:1.05}
.c-photocard .pc-desc{margin-top:12px;font-weight:500;font-size:30px;color:var(--muted);line-height:1.35}
.c-repo{width:864px;background:var(--card);border:1px solid var(--cardb);border-radius:34px;padding:48px;box-shadow:0 30px 70px rgba(20,40,90,.10)}
.repo-top{display:flex;align-items:center;gap:20px}
.gh{width:64px;height:64px;border-radius:16px;background:var(--ghbg);color:var(--ghtx);font-size:38px;display:flex;align-items:center;justify-content:center}
.repo-name{font-size:38px;font-weight:600;flex:1;color:var(--ink)}.repo-name b{font-weight:800}
.stars{color:#fff;font-weight:800;font-size:30px;padding:12px 22px;border-radius:999px}
.repo-desc{margin-top:30px;font-size:34px;font-weight:500;color:var(--ink2);line-height:1.4}
.tags{margin-top:30px;display:flex;flex-wrap:wrap;gap:16px}
.tag{background:var(--tagbg);color:var(--tagtx);font-weight:700;font-size:27px;padding:12px 24px;border-radius:14px}
.repo-btn{margin-top:38px;color:#fff;font-weight:800;font-size:34px;text-align:center;padding:24px;border-radius:18px}
.c-compare{display:flex;gap:30px;width:864px;position:relative;align-items:stretch}
.col{flex:1;background:var(--card);border:1px solid var(--cardb);border-radius:28px;padding:40px 34px}
.col.bad{background:var(--badbg);border:2px solid var(--badbd)}
.col.hi{border-width:3px;background:var(--hibg);box-shadow:0 24px 60px rgba(42,91,218,.14)}
/* centre VS badge (craft-study §1) — sits over the gap between the two cards */
.cmp-vs{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:6;
  width:92px;height:92px;border-radius:50%;background:var(--card);border:3px solid var(--c_emph);
  color:var(--c_emph);font-weight:900;font-size:38px;display:flex;align-items:center;justify-content:center;
  box-shadow:0 12px 30px rgba(0,0,0,.14)}
.cmp-vs.arrow{font-size:54px;line-height:1}
.ctitle{font-weight:900;font-size:40px;margin-bottom:24px;color:var(--ink)}.ctitle.bad{color:var(--coral)}
.crow{font-weight:600;font-size:32px;margin:18px 0;line-height:1.3;color:var(--ink2)}.crow.x{color:var(--coral)}
/* terminal = LIGHT theme (SEOSONA is light-only; converted from the old dark #0B1220) — matches codecard */
.c-term{width:864px;background:#fff;border:1px solid #E6EAF2;border-radius:22px;overflow:hidden;box-shadow:0 14px 40px rgba(15,23,42,.14)}
.term-bar{background:#F4F6FA;padding:20px 26px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #E6EAF2}
.dot{width:16px;height:16px;border-radius:50%}.dot.r{background:#E2724D}.dot.y{background:#EAB308}.dot.g{background:#16A34A}
.term-title{color:#64748B;font-weight:700;font-size:26px;margin-left:14px;font-family:'JetBrains Mono',ui-monospace,monospace}
.term-body{padding:36px 38px;font-family:'JetBrains Mono',ui-monospace,monospace}
.tline{color:#334155;font-size:32px;margin:16px 0;font-weight:500;white-space:pre-wrap;word-break:break-word;font-family:'JetBrains Mono',ui-monospace,monospace}.prompt{color:#2A5BDA;font-weight:800}.tline.ok{color:#16A34A;font-weight:800}
.tcur{display:flex;align-items:center;gap:14px;margin-top:8px}.tcaret{display:inline-block;width:18px;height:34px;border-radius:2px;vertical-align:middle}
.c-steps{width:864px;display:flex;flex-direction:column;gap:26px}
.step{display:flex;align-items:center;gap:26px;background:var(--card);border:1px solid var(--cardb);border-radius:22px;padding:30px 36px;box-shadow:0 14px 34px rgba(20,40,90,.07)}
.snum{flex:none;width:64px;height:64px;border-radius:16px;color:#fff!important;font-weight:900;font-size:36px;display:flex;align-items:center;justify-content:center;text-shadow:0 1px 3px rgba(0,0,0,.30);box-shadow:0 6px 16px rgba(20,40,90,.18)}
/* checklist w/ tri-state badge (craft-study §1): done ✓ / doing ◐ / locked 🔒 */
.c-checklist{width:864px;display:flex;flex-direction:column;gap:22px}
.chk{display:flex;align-items:center;gap:26px;background:var(--card);border:2px solid var(--cardb);border-radius:22px;padding:26px 34px;box-shadow:0 14px 34px rgba(20,40,90,.06)}
.chk-b{flex:none;width:64px;height:64px;border-radius:16px;border:2.5px solid;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:900;background:var(--card)}
.chk-t{font-weight:700;font-size:36px;color:var(--ink2);line-height:1.25}
.chk-dim{opacity:.5}
/* hub-and-spoke node diagram + travelling-dot progress line (craft-study §4) */
.c-hub{display:flex;flex-direction:column;align-items:center}
.c-cb{position:relative;margin:0 auto}
.cb-svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.cb-flow{position:absolute;left:0;top:0;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;box-shadow:0 0 12px 2px currentColor;z-index:5;pointer-events:none}
.cb-node{position:absolute;transform:translate(-50%,-50%);font-weight:800;font-size:28px;padding:16px 26px;border-radius:16px;background:#fff;border:2.5px solid var(--nc);color:var(--ink,#0F172A);box-shadow:0 8px 24px rgba(15,23,42,.12);white-space:nowrap;max-width:280px;text-align:center;line-height:1.2}
.cb-chip{border-radius:999px;font-size:26px;padding:12px 26px}
.cb-tile{width:132px;height:132px;display:flex;align-items:center;justify-content:center;border-radius:26px;padding:10px;white-space:normal}
.cb-note{background:#FFF8E7;border-color:#EAC36A;font-weight:600}
.cb-frame{position:absolute;border:2px dashed;border-radius:22px;background:rgba(42,91,218,.03)}
.cb-flabel{position:absolute;top:-15px;left:22px;background:#fff;padding:0 12px;font-weight:800;font-size:22px}
.c-cg{width:920px;display:flex;flex-direction:column;gap:9px}
.cg-row{display:flex;gap:9px}
.cg-cell{flex:1;padding:22px 14px;background:#fff;border-radius:14px;box-shadow:0 4px 16px rgba(15,23,42,.08);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:30px;text-align:center;min-height:34px}
.cg-feat{flex:1.6;justify-content:flex-start;font-weight:800;color:var(--ink,#0F172A)}
.cg-head .cg-col{font-weight:900;font-size:28px;background:#EEF3FB}
.cg-cell.win{border:2.5px solid var(--wc);background:color-mix(in srgb,var(--wc) 9%,#fff)}
.cg-yes{color:#16A34A;font-size:38px} .cg-no{color:#E2724D;font-size:38px}
.c-sr{display:flex;align-items:stretch;gap:0;width:960px;height:640px;border-radius:26px;overflow:hidden;box-shadow:0 14px 44px rgba(15,23,42,.16)}
.sr-side{position:relative;flex:1;overflow:hidden;background:#EEF3FB}
.sr-side img{width:100%;height:100%;object-fit:cover}
.sr-ph{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:34px}
.sr-tag{position:absolute;top:20px;left:20px;color:#fff;font-weight:800;font-size:26px;padding:8px 20px;border-radius:999px}
.sr-r .sr-tag{left:auto;right:20px}
.sr-div{width:6px;z-index:3;box-shadow:0 0 22px 3px var(--nc,#2A5BDA)}
.c-as{position:relative;width:940px;border-radius:22px;overflow:hidden;box-shadow:0 12px 40px rgba(15,23,42,.16)}
.c-as img{width:100%;display:block}
.as-ph{width:100%;height:560px;background:#EEF3FB;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:34px;color:#94A3B8}
.as-dim{position:absolute;inset:0;background:rgba(15,23,42,.34)}
.as-mark{position:absolute;border:4px solid;border-radius:12px;box-shadow:0 0 0 4000px rgba(15,23,42,.0);z-index:2}
.as-lab{position:absolute;top:-40px;left:0;color:#fff;font-weight:800;font-size:24px;padding:5px 16px;border-radius:999px;white-space:nowrap}
.c-sg{display:grid;gap:16px;width:900px}
.sg-cell{background:#fff;border-radius:20px;padding:30px 22px;box-shadow:0 8px 26px rgba(15,23,42,.10);display:flex;flex-direction:column;align-items:center;gap:6px;position:relative}
.sg-val{font-weight:900;font-size:60px;line-height:1;font-variant-numeric:tabular-nums}
.sg-lab{font-weight:700;font-size:26px;color:#475569;text-align:center;text-transform:uppercase;letter-spacing:.4px}
.sg-delta{font-weight:800;font-size:26px}
.c-rd{display:flex;flex-direction:column;align-items:center;gap:22px;width:760px}
.rd-big{font-weight:900;font-size:72px;line-height:1;font-variant-numeric:tabular-nums}
.rd-grid{display:grid;gap:18px}
.rd-dot{width:46px;height:46px;border-radius:50%;display:block}
.rd-cap{font-weight:800;font-size:30px;text-transform:uppercase;letter-spacing:1px}
.c-ls{display:flex;flex-direction:column-reverse;gap:12px;width:780px}
.ls-title{font-weight:900;font-size:32px;text-transform:uppercase;letter-spacing:.6px;margin-top:14px;text-align:center;order:99}
.ls-layer{background:#fff;border:2.5px solid;border-radius:18px;padding:24px 30px;box-shadow:0 6px 20px rgba(15,23,42,.09);display:flex;align-items:center;gap:18px;font-weight:800;font-size:34px}
.ls-glyph{font-size:40px}
.ls-lab{color:var(--ink,#0F172A)}
.ls-sub{margin-left:auto;font-weight:600;font-size:26px;color:#64748B}
.c-tf{display:flex;flex-direction:column;gap:12px;width:860px}
.tf-row{background:#fff;border-left:6px solid;border-radius:14px;padding:20px 26px;box-shadow:0 5px 18px rgba(15,23,42,.08);display:flex;align-items:center;gap:16px;font-size:30px;font-weight:600}
.tf-glyph{font-size:34px}
.tf-lab{font-weight:900;margin-right:10px;text-transform:uppercase;letter-spacing:.4px}
.tf-body{color:var(--ink,#0F172A)}
.tf-time{margin-left:auto;font-weight:700;font-size:24px;color:#94A3B8;font-variant-numeric:tabular-nums}
.c-od{display:flex;flex-direction:column;align-items:center;width:900px}
.od-parent{color:#fff;font-weight:900;font-size:40px;padding:22px 46px;border-radius:18px;box-shadow:0 10px 30px rgba(15,23,42,.16)}
.od-stem{width:4px;height:40px}
.od-grid{display:grid;gap:16px;width:100%}
.od-node{position:relative;background:#fff;border:2.5px solid;border-radius:16px;padding:24px 16px;text-align:center;font-weight:800;font-size:30px;box-shadow:0 6px 18px rgba(15,23,42,.09);color:var(--ink,#0F172A)}
.od-dim{opacity:.45}
.od-x{position:absolute;top:8px;right:12px;color:#E2724D;font-size:28px;font-weight:900}
.hub-ring{position:relative}
.hub-svg{position:absolute;inset:0;width:100%;height:100%;z-index:0}
.hub-center{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);min-width:150px;height:150px;
  border-radius:50%;color:#fff;font-weight:900;font-size:36px;display:flex;align-items:center;justify-content:center;
  padding:0 26px;text-align:center;box-shadow:0 16px 44px rgba(0,0,0,.18);z-index:3}
.hub-sat{position:absolute;transform:translate(-50%,-50%);background:var(--card);border:2.5px solid;border-radius:18px;
  padding:16px 26px;font-weight:800;font-size:29px;white-space:nowrap;box-shadow:0 10px 26px rgba(20,40,90,.10);z-index:2}
.hub-prog{position:relative;width:820px;height:10px;border-radius:6px;background:var(--cardb);margin-top:44px;overflow:visible}
.hub-fill{position:absolute;left:0;top:0;height:100%;width:60%;border-radius:6px;opacity:.85;animation:hubfill 2.6s ease-in-out infinite alternate}
.hub-dot{position:absolute;top:50%;left:60%;width:28px;height:28px;border-radius:50%;transform:translate(-50%,-50%);
  box-shadow:0 0 20px currentColor;animation:hubdot 2.6s ease-in-out infinite alternate}
@keyframes hubdot{from{left:4%}to{left:96%}}
@keyframes hubfill{from{width:4%}to{width:96%}}
/* icon/pill CATEGORY grid (craft-study §1) — 2-col, per-tile wayfinding colour */
.c-icongrid{display:grid;grid-template-columns:1fr 1fr;gap:24px;width:864px}
.ig-cell{display:flex;align-items:center;gap:22px;background:var(--card);border:2px solid var(--cardb);border-radius:22px;padding:26px 30px;box-shadow:0 12px 30px rgba(20,40,90,.06)}
.ig-ic{flex:none;width:76px;height:76px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:40px}
.ig-lab{font-weight:800;font-size:31px;color:var(--ink);line-height:1.2}
/* alert / danger-or-caution callout (craft-study §1) */
.c-alert{width:820px;border-radius:26px;padding:36px 42px;box-shadow:0 16px 40px rgba(20,40,90,.08)}
.al-title{font-weight:900;font-size:42px;margin-bottom:20px;display:flex;align-items:center;gap:16px;line-height:1.15}
.al-ic{font-size:44px}
.al-text{font-weight:600;font-size:34px;color:var(--ink2);line-height:1.4}
.al-row{font-weight:700;font-size:33px;color:var(--ink2);margin:16px 0;padding-left:42px;position:relative;line-height:1.3}
.al-row::before{content:"•";position:absolute;left:10px;font-size:38px;line-height:1;color:var(--m)}
/* repo file-tree card (craft-study §1) — window chrome + rows reveal one-by-one */
.c-filetree{width:820px;background:var(--card);border:1px solid var(--cardb);border-radius:24px;overflow:hidden;box-shadow:0 18px 44px rgba(20,40,90,.10)}
.ft-bar{display:flex;align-items:center;gap:12px;padding:22px 30px;background:var(--tagbg);border-bottom:1px solid var(--cardb)}
.ft-path{margin-left:14px;font-weight:800;font-size:28px;color:var(--ink2)}
.ft-body{padding:20px 14px}
.ft-row{display:flex;align-items:center;gap:20px;padding:18px 24px;border-radius:14px;font-weight:700;font-size:32px;color:var(--ink2)}
.ft-row:nth-child(even){background:var(--tagbg)}
.ft-ic{font-size:34px}.ft-nm{flex:1}.ft-meta{font-weight:600;font-size:26px;color:var(--muted)}
/* score / compare bars (craft-study §1) */
.c-bars{width:840px;display:flex;flex-direction:column;gap:34px}
.bar-top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:14px}
.bar-lab{font-weight:800;font-size:34px;color:var(--ink)}
.bar-val{font-weight:900;font-size:42px;letter-spacing:-1px}
.bar-tr{height:26px;border-radius:14px;background:var(--cardb);overflow:hidden}
.bar-fl{display:block;height:100%;border-radius:14px}
/* compat/tool chip row (craft-study §1) */
.c-chiprow{display:flex;flex-wrap:wrap;gap:20px;justify-content:center;width:900px}
.crx{border:2.5px solid;background:var(--card);font-weight:800;font-size:32px;padding:18px 34px;border-radius:999px;box-shadow:0 8px 22px rgba(20,40,90,.07)}
/* director SUPPORTING CHIPS row under the hero (density study 2026-07) */
.dchips{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;align-items:center;margin-top:36px;width:864px}
.dchip{border:2.5px solid;background:var(--card);font-weight:800;font-size:27px;padding:12px 26px;border-radius:999px;box-shadow:0 6px 16px rgba(20,40,90,.06)}
.step b{display:block;font-size:36px;font-weight:800;color:var(--ink)}.step span{display:block;font-size:28px;color:var(--muted);font-weight:500;margin-top:4px}
.c-badges{display:flex;flex-wrap:wrap;gap:24px;justify-content:center;width:864px}
.badge{border:3px solid;font-weight:800;font-size:36px;padding:22px 38px;border-radius:18px;background:var(--card)}
.c-stats{display:flex;gap:26px;width:864px;justify-content:center}
/* min-width:0 lets the flex cards share the 864px equally instead of each refusing to
   shrink below its (unbreakable) big-number min-content width — that auto-min was what
   pushed 3 wide-number cards past the 864px box and clipped the 3rd card at the frame
   edge in portrait. The fit('.c-stats .stnum',38) pass then shrinks each number to its
   now-correct card width, so all 3 cards stay centered within the safe margins. */
.stat{flex:1;min-width:0;background:var(--card);border:1px solid var(--cardb);border-radius:26px;padding:44px 20px;text-align:center;box-shadow:0 18px 44px rgba(20,40,90,.08)}
.stnum{font-weight:900;font-size:96px;line-height:1;letter-spacing:-2px}
.stlab{margin-top:16px;font-weight:700;font-size:28px;color:var(--muted);line-height:1.25}
.c-ring{position:relative;width:380px;height:380px;margin:0 auto;display:flex;align-items:center;justify-content:center}
.ring-svg{position:absolute;inset:0;width:380px;height:380px}
.ring-num{font-weight:900;font-size:104px;line-height:1;letter-spacing:-3px;font-variant-numeric:tabular-nums}
.ring-lab{position:absolute;bottom:-4px;left:0;right:0;text-align:center;font-weight:700;font-size:28px;color:var(--muted)}
.c-donut{display:flex;flex-direction:column;align-items:center;gap:34px}
.dn-chart{position:relative;width:340px;height:340px}
.dn-svg{position:absolute;inset:0;width:340px;height:340px}
.dn-cen{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:52px;color:var(--ink);letter-spacing:-1px}
.dn-legend{display:flex;flex-direction:column;gap:18px;width:560px}
.dn-li{display:flex;align-items:center;gap:18px}
.c-chat{display:flex;flex-direction:column;gap:18px;width:840px}
.ch-row{display:flex}
.ch-user{justify-content:flex-end}
.ch-ai{justify-content:flex-start}
.ch-bubble{max-width:78%;padding:24px 30px;border-radius:28px;font-size:33px;font-weight:600;line-height:1.35;box-shadow:0 6px 20px rgba(15,23,42,.09)}
.ch-user .ch-bubble{color:#fff;border-bottom-right-radius:9px}
.ch-ai .ch-bubble{background:#EEF2F8;color:var(--ink,#0F172A);border-bottom-left-radius:9px}
.c-codecard{width:880px;border-radius:20px;overflow:hidden;background:#fff;box-shadow:0 14px 40px rgba(15,23,42,.14);border:1px solid #E6EAF2}
.cc-bar{display:flex;align-items:center;gap:10px;padding:16px 22px;background:#F4F6FA;border-bottom:1px solid #E6EAF2}
.cc-dot{width:14px;height:14px;border-radius:50%;background:#D3D9E4}
.cc-dot:nth-child(1){background:#E2724D}.cc-dot:nth-child(2){background:#EAB308}.cc-dot:nth-child(3){background:#16A34A}
.cc-file{margin-left:14px;font-weight:700;font-size:26px;color:#64748B;font-family:'JetBrains Mono',ui-monospace,monospace}
.cc-body{padding:26px 30px;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:30px;line-height:1.7;color:#334155}
.cc-ln{white-space:pre-wrap;word-break:break-word}
.cc-s{color:#16A34A}.cc-n{color:#E2724D}.cc-k{color:#2A5BDA;font-weight:700}
.c-tabs{width:840px;display:flex;flex-direction:column;gap:26px}
.tb-bar{display:flex;gap:12px;background:#EEF2F8;padding:10px;border-radius:18px}
.tb-tab{flex:1;text-align:center;padding:18px 10px;border-radius:12px;font-weight:800;font-size:30px;color:#64748B}
.tb-tab.tb-on{color:#fff;box-shadow:0 6px 18px rgba(15,23,42,.14)}
.tb-list{display:flex;flex-direction:column;gap:14px}
.tb-item{display:flex;align-items:center;gap:18px;background:#fff;border-radius:16px;padding:24px 30px;font-weight:700;font-size:32px;color:var(--ink,#0F172A);box-shadow:0 6px 18px rgba(15,23,42,.08)}
.tb-badge{font-size:34px;font-weight:900}
.c-gauge{display:flex;flex-direction:column;align-items:center;gap:20px;width:560px}
.ga-dial{position:relative;width:440px;height:440px}
.ga-svg{position:absolute;inset:0;width:440px;height:440px}
.ga-val{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:96px;line-height:1;letter-spacing:-2px;font-variant-numeric:tabular-nums}
.ga-lab{font-weight:800;font-size:34px;color:#475569;text-transform:uppercase;letter-spacing:.6px;text-align:center}
.c-mrows{display:flex;flex-direction:column;gap:16px;width:760px}
.mr-row{display:flex;align-items:center;gap:22px;background:#fff;border-radius:18px;padding:26px 34px;box-shadow:0 6px 18px rgba(15,23,42,.08)}
.mr-ic{font-size:44px}.mr-dot{width:22px;height:22px;border-radius:6px;flex:none}
.mr-lab{font-weight:700;font-size:34px;color:var(--ink,#0F172A)}
.mr-val{margin-left:auto;font-weight:900;font-size:48px;font-variant-numeric:tabular-nums}
.c-pills{display:flex;flex-direction:column;gap:18px;width:720px}
.ps-pill{display:flex;align-items:center;gap:20px;justify-content:center;background:#fff;border:2.5px solid #E2E8F0;border-radius:999px;padding:28px 40px;font-weight:800;font-size:36px;color:var(--ink,#0F172A);box-shadow:0 8px 22px rgba(15,23,42,.08)}
.ps-ic{font-size:40px}
.av{flex:none;width:88px;height:88px;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center}
.av-img img{width:100%;height:100%;object-fit:cover}
.av-ini{color:#fff;font-weight:900;font-size:38px;letter-spacing:-1px}
.c-people{display:flex;flex-direction:column;gap:18px;width:760px}
.pp-row{display:flex;align-items:center;gap:24px;background:#fff;border-radius:20px;padding:22px 30px;box-shadow:0 6px 18px rgba(15,23,42,.08)}
.pp-name{font-weight:800;font-size:36px;color:var(--ink,#0F172A);line-height:1.15}
.pp-role{font-weight:600;font-size:28px;color:#64748B}
.c-strike{display:flex;flex-direction:column;gap:20px;width:760px;align-items:flex-start}
.sk-item{position:relative;background:#fff;border-radius:16px;padding:24px 32px;font-weight:700;font-size:36px;color:#94A3B8;box-shadow:0 6px 18px rgba(15,23,42,.07);align-self:stretch}
.sk-line{position:absolute;left:28px;top:50%;height:5px;border-radius:3px;transform:scaleX(0);transform-origin:left center;width:calc(100% - 56px)}
.sk-concl{align-self:center;margin-top:10px;color:#fff;font-weight:900;font-size:38px;padding:24px 44px;border-radius:999px;box-shadow:0 10px 26px rgba(15,23,42,.16)}
.c-notif{width:824px;background:#fff;border:1px solid #E6EAF2;border-radius:34px;padding:44px 48px;box-shadow:0 26px 64px rgba(20,40,90,.12)}
.nf-head{display:flex;align-items:center;gap:18px;margin-bottom:22px}
.nf-app{font-weight:800;font-size:32px;color:var(--muted);letter-spacing:.2px}
.nf-time{margin-left:auto;font-weight:600;font-size:28px;color:#94A3B8}
.nf-title{font-weight:900;font-size:44px;color:var(--ink);line-height:1.15;margin-bottom:14px}
.nf-text{font-weight:500;font-size:34px;color:#334155;line-height:1.35}
.c-social{width:824px;background:#fff;border:1px solid #E6EAF2;border-radius:30px;padding:44px 48px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.so-head{display:flex;align-items:center;gap:20px;margin-bottom:26px}
.so-id{display:flex;flex-direction:column;gap:4px}
.so-name{display:flex;align-items:center;gap:12px;font-weight:900;font-size:38px;color:var(--ink)}
.so-vf{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;color:#fff;font-size:22px;font-weight:900}
.so-handle{font-weight:600;font-size:30px;color:#94A3B8}
.so-text{font-weight:600;font-size:40px;color:var(--ink);line-height:1.32}
.so-eng{display:flex;gap:40px;margin-top:30px;font-weight:700;font-size:30px;color:var(--muted)}
.c-phone{display:flex;justify-content:center;width:100%}
.ph-frame{position:relative;width:496px;background:#0B0F1A;border:3px solid #232a3a;border-radius:74px;padding:16px;box-shadow:0 40px 90px rgba(20,40,90,.28),inset 0 0 0 4px #0B0F1A}
.ph-island{position:absolute;top:34px;left:50%;transform:translateX(-50%);width:128px;height:36px;background:#000;border-radius:20px;z-index:3}
.ph-status{position:absolute;top:30px;left:44px;right:44px;display:flex;align-items:center;justify-content:space-between;z-index:2;color:#0F172A}
.ph-time{font-weight:800;font-size:28px;letter-spacing:.5px}
.ph-sys{display:flex;align-items:center;gap:9px}
.ph-i{height:22px;width:auto;fill:#0F172A;color:#0F172A}
.ph-scr{background:#fff;border-radius:60px;padding:104px 40px 46px;display:flex;flex-direction:column;gap:18px;min-height:760px}
.ph-appbar{display:flex;align-items:center;gap:16px;font-weight:900;font-size:42px;line-height:1.1;margin-bottom:12px}
.ph-dot{width:26px;height:26px;border-radius:9px;flex:none}
.ph-line{background:#F4F6FA;border:1px solid #EAEEF5;border-radius:18px;padding:26px 28px;font-weight:700;font-size:32px;color:#334155}
.ph-home{position:absolute;bottom:26px;left:50%;transform:translateX(-50%);width:150px;height:8px;background:#0F172A;border-radius:5px;z-index:3}
.dn-sw{width:28px;height:28px;border-radius:8px;flex:none}
.dn-lb{font-weight:700;font-size:34px;color:var(--ink)}
.dn-pc{font-weight:800;font-size:34px;color:var(--muted);margin-left:auto}
.dn-cap{text-align:center;font-weight:600;font-size:30px;color:var(--muted);margin-top:4px}
.c-linechart{width:840px;margin:0 auto}
.lc-plot{position:relative;width:100%}
.lc-svg{width:100%;height:360px;display:block;overflow:visible}
.lc-xlabels{position:relative;height:40px;margin-top:2px}
.lc-x{position:absolute;transform:translateX(-50%);font-weight:800;font-size:30px;color:var(--muted);white-space:nowrap}
.lc-lab{text-align:center;font-weight:600;font-size:30px;color:var(--muted);margin-top:16px}
.c-timeline{position:relative;width:840px;display:flex;flex-direction:column;gap:34px;padding-left:8px}
.tl-spine{position:absolute;left:28px;top:14px;bottom:14px;width:4px;border-radius:2px;opacity:.28}
.tl-row{position:relative;display:flex;padding-left:70px;align-items:flex-start}
.tl-dot{position:absolute;left:19px;top:6px;width:22px;height:22px;border-radius:50%;box-shadow:0 0 0 7px #fff}
.tl-date{font-weight:800;font-size:30px;line-height:1}
.tl-title{font-weight:700;font-size:36px;color:var(--ink);margin-top:4px;line-height:1.15}
.tl-sub{font-weight:500;font-size:27px;color:var(--muted);margin-top:4px;line-height:1.2}
.c-divider{text-align:center;display:flex;flex-direction:column;align-items:center;gap:6px}
.dv-num{font-weight:900;font-size:200px;line-height:.88;letter-spacing:-8px;font-variant-numeric:tabular-nums}
.dv-title{font-weight:800;font-size:58px;color:var(--ink);line-height:1.05}
.dv-sub{font-weight:500;font-size:30px;color:var(--muted)}
.c-quote{width:864px;background:var(--card);border:1px solid var(--cardb);border-radius:30px;padding:54px 56px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.qmark{font-weight:900;font-size:140px;line-height:0.6;height:70px}
.qtext{font-weight:800;font-size:52px;line-height:1.3;color:var(--ink)}
.qby{margin-top:28px;font-weight:700;font-size:32px;color:var(--muted)}
.c-tip{width:864px;display:flex;gap:28px;align-items:flex-start;background:var(--card);border:2px solid;border-radius:26px;padding:42px 48px;box-shadow:0 18px 44px rgba(20,40,90,.08)}
.tipicon{font-size:60px;line-height:1;flex:none}
.tiptitle{font-weight:800;font-size:32px;letter-spacing:1px;margin-bottom:12px}
.tiptext{font-weight:600;font-size:40px;line-height:1.35;color:var(--ink2)}
.c-lower3{align-self:center;max-width:864px;background:var(--card);border:1px solid var(--cardb);border-radius:16px;padding:30px 46px;box-shadow:0 16px 40px rgba(20,40,90,.12)}
.c-lower3 .l3title{font-weight:900;font-size:52px;color:var(--ink);line-height:1.1}
.c-lower3 .l3sub{font-weight:600;font-size:32px;color:var(--muted);margin-top:8px}
.c-callout{max-width:864px;border-radius:22px;padding:36px 52px;box-shadow:0 20px 48px rgba(20,40,90,.16)}
.c-callout span{color:#fff;font-weight:900;font-size:56px;line-height:1.12;text-align:center;display:block}
.c-feature{width:864px;display:flex;flex-direction:column;gap:26px}
.feat{display:flex;align-items:center;gap:28px;background:var(--card);border:1px solid var(--cardb);border-radius:22px;padding:30px 38px;box-shadow:0 14px 34px rgba(20,40,90,.07)}
.femoji{font-size:60px;line-height:1;flex:none}
.feat b{display:block;font-size:38px;font-weight:800;color:var(--ink)}.feat span{display:block;font-size:28px;color:var(--muted);font-weight:500;margin-top:4px}
.c-chart{width:864px;background:var(--card);border:1px solid var(--cardb);border-radius:30px;padding:48px 52px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.chtitle{font-weight:900;font-size:40px;color:var(--ink);margin-bottom:36px}
.chrow{margin:26px 0}
.chlab{font-weight:700;font-size:32px;color:var(--ink2);margin-bottom:12px}
.chtrack{height:62px;background:var(--tagbg);border-radius:14px;overflow:hidden}
.chfill{height:100%;border-radius:14px;display:flex;align-items:center;justify-content:flex-end;min-width:90px}
.chval{color:#fff;font-weight:800;font-size:30px;padding-right:22px}
.c-mockup{width:920px;background:var(--card);border:1px solid var(--cardb);border-radius:26px;overflow:hidden;box-shadow:0 30px 70px rgba(20,40,90,.16)}
.mkbar{background:var(--tagbg);padding:20px 28px;display:flex;align-items:center;gap:13px;border-bottom:1px solid var(--cardb)}
.mkdot{width:20px;height:20px;border-radius:50%}.mkdot.r{background:#FF5F57}.mkdot.y{background:#FEBC2E}.mkdot.g{background:#28C840}
.mknav{margin-left:14px;color:#94A3B8;font-size:32px;letter-spacing:8px;font-weight:700}
.mkaddr{margin-left:8px;display:flex;align-items:center;justify-content:center;gap:12px;background:var(--card);border:1px solid var(--cardb);border-radius:999px;padding:12px 30px;font-size:27px;color:var(--muted);font-weight:600;flex:1}
.mklock{height:24px;width:auto;fill:#16A34A;color:#16A34A;flex:none}
.mkurl{color:#475569}
.mkmenu{color:#94A3B8;font-size:34px;font-weight:800;margin-left:6px}
.mkbody{padding:44px 40px}
/* real screenshot fills the window body edge-to-edge (no padding) */
.c-mockup:has(.mkshot) .mkbody{padding:0}
.mkshot{width:100%;line-height:0;overflow:hidden}.mkshot img{width:100%;height:auto;display:block;will-change:transform;transform-origin:center top}
.mkcap{display:flex;align-items:center;justify-content:space-between;padding:26px 38px;border-top:1px solid var(--cardb)}
.mkcap b{font-size:34px;font-weight:800;color:var(--ink)}
.mkstars{color:#fff;font-weight:800;font-size:28px;padding:10px 24px;border-radius:999px}
.mktiles{display:flex;flex-wrap:wrap;gap:24px}
.mktile{flex:1 1 40%;background:var(--hibg);border-radius:20px;padding:34px 28px;text-align:center}
.mktnum{font-weight:900;font-size:72px;line-height:1}.mktlab{margin-top:12px;font-weight:700;font-size:28px;color:var(--muted)}
.mklines .mkline{font-size:34px;font-weight:600;color:var(--ink2);padding:18px 0;border-bottom:1px solid var(--cardb)}
.mklines .mkline:last-child{border-bottom:none}
.c-cta{display:flex;flex-direction:column;align-items:center;gap:34px}
.cta-logo{width:560px}.cta-line{font-weight:800;font-size:48px;color:var(--ink);text-align:center}
.cta-btn{color:#fff;font-weight:800;font-size:42px;padding:28px 56px;border-radius:999px}
/* CTA variants (craft-study §7): comment-bait box + follow lower-third */
.cta-comment{display:flex;align-items:center;gap:16px;background:var(--card);border:2px solid var(--cardb);border-radius:999px;padding:18px 22px 18px 44px;box-shadow:0 12px 30px rgba(20,40,90,.08);min-width:420px}
.cc-txt{flex:1;font-weight:900;font-size:46px;color:var(--ink)}
.cc-send{flex:none;width:66px;height:66px;border-radius:50%;color:#fff;font-size:32px;display:flex;align-items:center;justify-content:center}
.cta-follow{display:flex;align-items:center;gap:26px;background:var(--card);border:1px solid var(--cardb);border-radius:22px;padding:22px 30px;box-shadow:0 14px 34px rgba(20,40,90,.08)}
.cf-name{font-weight:900;font-size:44px;color:var(--ink)}
.cf-btn{color:#fff;font-weight:800;font-size:34px;padding:16px 38px;border-radius:999px}
.c-gitlog{width:864px;background:var(--card);border:1px solid var(--cardb);border-radius:28px;padding:46px 56px;box-shadow:0 24px 60px rgba(20,40,90,.10)}
.gltitle{font-family:monospace;font-size:32px;font-weight:700;color:var(--muted);margin-bottom:36px}
.glprompt{color:var(--fb);font-weight:800}
.glrows{border-left:5px solid var(--cardb);margin-left:21px;display:flex;flex-direction:column;gap:34px}
.glrow{display:flex;align-items:center;gap:22px;margin-left:-22px}
.gldot{width:38px;height:38px;border-radius:50%;flex:none;box-shadow:0 0 0 7px var(--card)}
.glid{font-family:monospace;font-size:42px;font-weight:900;color:var(--ink)}
/* --- Design-craft upgrades (mined from ant-design + open-design, re-skinned brand, light,
   SEEK-SAFE: static CSS only, no @keyframes; convergent picks from 2 design digs) --- */
.big,.bn-num,.stnum,.chval,.mktnum{font-variant-numeric:tabular-nums}              /* no digit jitter on count-up */
.qtext,.head .l1,.ctitle,.chtitle,.tiptext{text-wrap:balance}                      /* no orphan/awkward wraps */
.c-repo,.stat,.c-quote,.c-tip,.c-chart,.feat,.step,.c-gitlog,.c-mockup,.col{       /* layered premium depth (ant-design pattern), brand-tinted ambient */
  box-shadow:0 0 0 1px rgba(15,23,42,.05),0 2px 6px -2px rgba(15,23,42,.08),0 18px 44px -10px rgba(42,91,218,.13)}
.stars,.mkstars{box-shadow:0 2px 8px rgba(15,23,42,.12)}                           /* star pill floats (ant Badge) */
.gltag{font-size:28px;font-weight:800;padding:8px 20px;border-radius:999px}
.glhead{margin-left:auto;background:var(--coral);color:#fff;font-weight:800;font-size:24px;letter-spacing:1px;padding:8px 16px;border-radius:9px}
.footer{position:absolute;left:50%;transform:translateX(-50%);bottom:230px;background:var(--card);border:1px solid var(--cardb);border-radius:999px;
 padding:20px 40px;font-weight:700;font-size:30px;color:var(--ink2);box-shadow:0 12px 34px rgba(20,40,90,.10);white-space:nowrap}
.footer .dotg{color:var(--dotc);margin-right:12px}.footer .b1{color:var(--fb);font-weight:800}.footer .b2{color:var(--dotc);font-weight:700}.footer .sep{color:var(--cardb);margin:0 14px}
.kara{position:absolute;left:50%;transform:translateX(-50%);bottom:300px;background:var(--kara);border-radius:20px;padding:20px 38px;max-width:864px;box-shadow:0 18px 40px rgba(8,15,35,.40)}
.kara span{display:inline-block;color:var(--karatx);font-weight:700;font-size:36px;letter-spacing:-.5px;margin:0 7px}
"""
    # Parameterize for aspect. CSS is authored for portrait 1080x1920; for other
    # resolutions scale the canvas + vertical spacing/anchors proportionally (vs) and
    # horizontal padding (hs) so content fits without overflow. Portrait = no-op.
    css = css.replace("width:1080px;height:1920px", f"width:{W}px;height:{H}px")  # #root + .scene
    # .scene padding is now driven by the scaled --sz-* safe-zone vars (built above), so there is
    # no separate padding replace here (that string went stale before and silently no-op'd).
    css = css.replace("bottom:230px", f"bottom:{int(230*vs)}px")  # .footer
    css = css.replace("bottom:300px", f"bottom:{int(300*vs)}px")  # .kara
    if vs < 0.95:  # landscape / non-portrait: shrink the whole scene content to fit height
        css += f"\n.scene>.kicker,.scene>.head,.scene>.comp{{transform:scale({vs:.3f});transform-origin:center top}}"
    return css

# ---------------------------------------------------------------- main API
_DIMS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}


_FILE_RE = re.compile(r"\b[\w-]+\.(md|py|js|ts|jsx|tsx|json|ya?ml|sh|toml|txt|html|css|env|go|rs|sql)\b", re.I)


def _hook_style(text):
    """Title-hook VARIANT class (craft-study §7): a filename headline (DESIGN.md, config.yaml)
    renders in monospace — the mono-filename hook. Default = bold sans. Cheap, content-driven."""
    return " hk-mono" if text and _FILE_RE.search(text) else ""


def make_video(project_dir, segments, scenes, *, lexicon=None, output=None,
               target_lufs=-14, voice="Trọng Hữu", theme="light", music="tech",
               accent_shift=None, brand="seosona", aspect="9:16", redo=None):
    _t0 = time.time()   # render wall-clock for the observability hub (Phase 6)
    # Anchor EVERY derived path (proj/assets/voice.mp3/_raw.mp4/FINAL) to an ABSOLUTE base up front. A
    # relative project_dir + a non-root CWD silently broke artifact reuse — this is the root of the
    # `_raw.mp4` stale-render bug (previously patched per-path with abspath on _raw_p/out only); the
    # voice.mp3/assets reuse checks had the SAME latent exposure. One abspath here fixes the whole class.
    project_dir = os.path.abspath(project_dir)
    # RENDER-CHOKEPOINT VERIFY — every path (news B, freeform C, course D, and the Claude agent path A,
    # which has NO code-level verify of its own) funnels through make_video, so this is the one place
    # that guarantees no script reaches the renderer un-checked. Source-independent floor (English leak,
    # repeated scene, moderation, structure) always runs. Default = warn loudly but still render so the
    # factory never dead-stops; SEOSONA_VERIFY_STRICT=1 turns hard errors into an abort.
    try:
        import script_writer as _swv
        _vr = _swv.enforce_before_render([s if isinstance(s, str) else "" for s in (segments or [])])
        if _vr.errors:
            print("[native_composer] ⚠ VERIFY (render gate) errors:")
            for _e in _vr.errors[:8]:
                print("   -", _e)
            if os.environ.get("SEOSONA_VERIFY_STRICT") == "1":
                raise RuntimeError("verify hard errors (SEOSONA_VERIFY_STRICT=1): "
                                   + "; ".join(_vr.errors[:5]))
        for _w in (_vr.warnings or [])[:5]:
            print("   · [verify]", _w)
    except RuntimeError:
        raise
    except Exception as _e:
        print(f"[native_composer] render-gate verify skipped: {_e}")
    # SPEC-LINT (SKILL-AUTO): scenes now carry their MERGED component → catch a BLANK-RISK component
    # (missing required data → renders empty) here, at the one chokepoint, before we spend a render on it.
    try:
        import spec_lint as _spec_lint
        _sl = _spec_lint.lint_scenes(scenes,
                                     require_reason=os.environ.get("SEOSONA_REQUIRE_REASON") == "1")
        _blank = [x for x in _sl.get("warnings", []) if x.startswith("BLANK-RISK")]
        if _blank:
            print(f"[native_composer] ⚠ spec-lint {len(_blank)} blank-risk component(s):")
            for _x in _blank[:8]:
                print("   -", _x)
    except Exception:
        pass
    # DIRECTOR stage (5-role pipeline … → ĐẠO DIỄN → nhà máy): scenes now carry their MERGED component +
    # kicker, so author the demonstrative motion + action-SFX per scene into the spec HERE — covers both
    # the make() path AND rerender. Best-effort; the factory still renders if it's skipped.
    try:
        import director as _director
        _shots = _director.direct(scenes, [s if isinstance(s, str) else "" for s in (segments or [])])
        print(_director.format_shot_list(_shots))
    except Exception as _de:
        print(f"[native_composer] director skipped ({_de})")
    # accent_shift rotates the whole colour scheme so two videos from the SAME
    # template don't look identical. None -> auto-derive a stable shift from the topic.
    if accent_shift is None:
        accent_shift = _auto_shift(output)
    # Per-video seed for the effect library: rotates transitions/exits so DIFFERENT videos get
    # DIFFERENT effect sequences (variety at scale). Topic-derived → stable for one video.
    _vseed = (os.path.basename(output) if output else "") or (scenes[0].get("h1", "") if scenes else "x")
    profile = _load_profile(brand)        # logo + voice come from system_config.yaml
    vcfg = profile.get("voice", {}) or {}
    _pal = ACCENT_PALETTE.get(brand, ACCENT_PALETTE["seosona"])
    os.makedirs(project_dir, exist_ok=True)
    # Block enrichment for ALL paths (news template + freeform): give scenes that don't already carry a
    # block a fitting registry block by content (data-chart, mockup, transition…) so videos are visually
    # rich, not bare. Gated (SEOSONA_USE_BLOCKS, default on) + capped (SEOSONA_BLOCK_BUDGET).
    try:
        import block_picker as _bp
        if _bp.enabled():
            _bud = int(os.environ.get("SEOSONA_BLOCK_BUDGET", "4"))
            # CONTENT MATCH ONLY — assign a block when it genuinely fits the scene's words. There is NO
            # decorative fallback: the registry's transition demos (cinematic-zoom/light-leak/glitch) are
            # gallery cards that render fixed showcase chrome (block_picker._KNOWN_BAD bars them), so forcing
            # one onto a generic scene "for visual richness" leaked demo text into real videos. Visual
            # richness comes from the data-driven components + element layer + effects, not fake cutaways.
            for _i, _sc in enumerate(scenes):
                if _bud <= 0:
                    break
                if _scene_block(_sc):
                    continue
                _blk = _bp.pick_block(segments[_i] if _i < len(segments) else "")
                if _blk:
                    _sc["block"] = _blk; _bud -= 1
    except Exception as _e:
        print(f"[native_composer] block enrich skipped: {_e}")
    proj = os.path.join(project_dir, "proj"); assets = os.path.join(proj, "assets")
    os.makedirs(assets, exist_ok=True)
    # PARTIAL RE-RENDER (KeepVoice family) — reuse cached expensive artifacts when only part is wrong:
    #   redo=None/"all" → full render.  "visual"=keep voice, re-render video.  "voice"=keep video (_raw),
    #   re-do the voice + remux.  "mix"=keep voice+video, redo SFX/BGM/loudness.  "thumb"=keep all, re-grab
    #   the thumbnail.  Additive: with redo=None the code path below is byte-identical to before.
    _redo = set(x.strip().lower() for x in str(redo or "").replace(";", ",").split(",") if x.strip())
    _partial = bool(_redo) and "all" not in _redo
    def _skip(stage): return _partial and stage not in _redo   # reuse this stage's cached artifact?
    # FAST-PATH — redo="thumb" ONLY: voice+video+mix are all reused, so the poster is the only thing to
    # redo. Skip the ENTIRE pipeline (the ~60s ASR + caption build + HTML) and just re-grab the frame from
    # the existing final video. Without this, a thumbnail re-grab needlessly transcribes the whole voice —
    # defeating the KeepVoice family's whole point (redo the broken stage CHEAPLY). Falls through to the
    # full path if the final video is missing or the grab fails.
    if _redo == {"thumb"}:
        _fout = os.path.abspath(output or os.path.join(project_dir, "FINAL.mp4"))
        if os.path.exists(_fout):
            try:
                _tdir = os.path.join(os.path.dirname(_fout) or ".", "Thumbnail")
                os.makedirs(_tdir, exist_ok=True)
                _thumb = os.path.join(_tdir, "thumbnail_frame.png")
                _picked = None
                try:
                    _fs_dir = os.path.join(ROOT, "2_SKILLS", "thumbnail_maker")
                    if _fs_dir not in sys.path:
                        sys.path.insert(0, _fs_dir)
                    import frame_scorer as _fscore
                    _picked = _fscore.best_frame(_fout, _thumb)
                except Exception as _fe:
                    print(f"[redo] frame scorer skipped: {_fe}")
                if not _picked:
                    subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
                                    "-ss", "2.0", "-i", _fout, "-frames:v", "1", _thumb], check=True)
                print("[redo] thumb-only fast-path — reused voice+video+mix, re-grabbed poster only.")
                print(f"THUMB: {_thumb}{'' if _picked else ' (fixed-grab fallback)'}")
                return _fout
            except Exception as _e:
                print(f"[redo] thumb fast-path failed ({_e}) — falling through to full path.")
    _raw_p = os.path.abspath(os.path.join(project_dir, "_raw.mp4"))
    _reuse_voice = _skip("voice") and os.path.exists(os.path.join(assets, "voice.mp3"))
    _reuse_raw = _skip("visual") and os.path.exists(_raw_p)    # reuse the rendered video unless redoing it
    if _partial:
        print(f"[redo] partial re-render {sorted(_redo)} → reuse voice={_reuse_voice} video={_reuse_raw}")
    # Persist the exact content+params so a later partial re-render (scripts/rerender.py) reuses the
    # SAME segments/scenes → the kept voice/video always matches. Best-effort (never blocks a render).
    try:
        json.dump({"segments": segments, "scenes": scenes,
                   "params": {"output": output, "brand": brand, "aspect": aspect, "theme": theme,
                              "music": music, "target_lufs": target_lufs, "voice": voice,
                              "lexicon": lexicon, "accent_shift": accent_shift}},
                  open(os.path.join(proj, "content.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, default=str)
    except Exception as _e:
        print(f"[redo] content.json not saved ({_e})")
    # assets (BGM no longer goes into the HF render — it is ducked under the voice
    # at mix time in step 6 so narration always stays clear)
    for f, _, _ in FONTS:
        src = os.path.join(ROOT, "7_ASSETS/brand/fonts", "BeVietnamPro-" + dict((x[0], x[2]) for x in FONTS)[f] + ".ttf")
        if os.path.exists(src): shutil.copy(src, os.path.join(assets, f))
    logo_src = os.path.join(ROOT, "7_ASSETS/brand/logos", profile.get("logo", "Seosona_Logo.png"))
    if not os.path.exists(logo_src):
        logo_src = os.path.join(ROOT, BRAND["logo"])
    shutil.copy(logo_src, os.path.join(assets, "logo.png"))
    # Copy any real screenshot (captured by make_video's `shot` step) into the render assets
    # and rewrite the component to the relative path. Graceful: skips if the file is gone.
    for _si, sc in enumerate(scenes):
        comp = sc.get("comp")
        if not (comp and isinstance(comp[1], dict)):
            continue
        d = comp[1]
        # photocard: AUTO-SOURCE a real illustrative photo (image_sourcer) when none was supplied —
        # so a photo-tip scene gets a relevant 9:16 photo with no human. (Craft learned from Shorts Studio.)
        if comp[0] == "photocard" and not d.get("img"):
            try:
                sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "image_sourcer"))
                import image_sourcer as _isrc
                _p = _isrc.source_for_concept(d.get("concept") or sc.get("h1") or d.get("title") or "")
                if _p:
                    d["img"] = os.path.abspath(_p)
            except Exception as _e:
                print(f"[photocard] image source skipped ({_e})")
        # per-scene COLOUR HARMONY: tint the photocard frame + number to the photo's dominant colour
        if comp[0] == "photocard" and d.get("img") and not d.get("_acc"):
            try:
                sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "image_sourcer"))
                import image_sourcer as _isrc
                _ip = d["img"] if os.path.isabs(d["img"]) else os.path.join(assets, os.path.basename(d["img"]))
                if os.path.exists(_ip):
                    d["_acc"] = _isrc.dominant_color(_ip)
            except Exception:
                pass
        if comp[0] in ("mockup", "repo", "photocard"):
            img = d.get("img")
            if img and os.path.isabs(img) and os.path.exists(img):
                _ext = os.path.splitext(img)[1] or ".png"
                rel = f"assets/shot_{_si}{_ext}"   # unique per scene so multiple shots don't collide
                shutil.copy(img, os.path.join(assets, f"shot_{_si}{_ext}"))
                d["img"] = rel
        # split_reveal / annotated_screenshot: AUTO-SOURCE + copy their photo(s) to assets (relative src)
        if comp[0] in ("split_reveal", "annotated_screenshot"):
            try:
                sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "image_sourcer"))
                import image_sourcer as _isrc

                def _cpimg(concept, tag):
                    _p = _isrc.source_for_concept(concept) if concept else None
                    if not _p or not os.path.exists(os.path.abspath(_p)):
                        return None
                    _ex = os.path.splitext(_p)[1] or ".jpg"
                    shutil.copy(os.path.abspath(_p), os.path.join(assets, f"shot_{_si}_{tag}{_ex}"))
                    return f"assets/shot_{_si}_{tag}{_ex}"
                if comp[0] == "split_reveal":
                    for _side, _tag in (("left", "l"), ("right", "r")):
                        _sd = d.get(_side)
                        if isinstance(_sd, dict) and not _sd.get("_img"):
                            _r = _cpimg(_sd.get("concept") or sc.get("h1"), _tag)
                            if _r:
                                _sd["_img"] = _r
                elif not d.get("_img"):
                    _r = _cpimg(d.get("concept") or sc.get("h1"), "as")
                    if _r:
                        d["_img"] = _r
            except Exception as _e:
                print(f"[{comp[0]}] image source skipped ({_e})")

    # 1) voice (pronunciation form) via VieNeu male
    lex = dict(nvs.PRONUNCIATION_LEXICON); lex.update(lexicon or {})
    import re
    def pron(s):
        # 1) brand/English lexicon FIRST (SEO→"séo", MIT→"em ai ti") so acronyms aren't mangled by the
        #    normalizer's Latin-transliteration below.
        for k in sorted(lex, key=len, reverse=True):
            s = re.sub(r'(?<![A-Za-z0-9])'+re.escape(k)+r'(?![A-Za-z0-9])', lex[k], s)
        # 2) VN text-normalization: dates/%/currency/units/phone → spoken words (VietNormalizer, MIT,
        #    dependency-free — adopted 2026-07-02). Best-effort: falls back to the number-only
        #    _say_number_vi if the lib is absent/errors, so the render never depends on it.
        v = _vn_normalize(s)
        return v if v else _say_number_vi(s)
    display_full = " ".join(segments)
    voice_path = os.path.join(assets, "voice.mp3")
    # Route through voice_router (single source of truth): it enforces the single
    # approved brand voice + honest edge fallback. `voice` is advisory — the router
    # coerces any preset to APPROVED_VOICE.
    vr = __import__("2_SKILLS.voice_cloner.voice_router", fromlist=["x"])
    ref = vcfg.get("reference_audio")
    ref = os.path.join(ROOT, ref) if ref else None
    ref = ref if (ref and os.path.exists(ref)) else None   # clone auto-activates when a real clip exists
    if _reuse_voice:
        print("[redo] reuse cached voice.mp3 (skip TTS)")
    else:
        # NOTE (2026-07-03): the earlier "add a period between scenes for pauses" hack made the clone
        # HALLUCINATE a filler ("ấy") at each fabricated sentence boundary (user heard it at 00:00/00:16/
        # 00:31…). Reverted to a plain join — pacing/breathing comes from the relaxed silence-trim +
        # atempo floor, NOT from inserting punctuation the model then fills with a filler.
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
    # Energetic-news band: 178–210 wpm. A cloned voice often drags (~150 wpm) with dead air — that reads
    # as SLOW. So speed any sub-178 take UP toward 178 (snappy), and trim only real tongue-twisters (>210)
    # DOWN. atempo preserves pitch. Overridable: SEOSONA_TARGET_WPM (the floor we speed up to).
    # Prefer a NATURAL take over hitting an exact wpm: only correct genuine outliers, and cap the
    # stretch tighter (1.15) so atempo artifacts stay inaudible. 168 floor + 210 ceil = a wide
    # natural band (a 171-wpm take is left ALONE, not sped to 178 → less robotic). (2026-07-02)
    # 2026-07-03 (user: "video nhanh, khó xem") — lowered the floor 168→150 so a natural CQA
    # lecture pace (~150) is LEFT ALONE instead of sped up; only real tongue-twisters trimmed.
    MAX_WPM = 205.0
    MIN_WPM = float(os.environ.get("SEOSONA_TARGET_WPM", "150"))
    MIN_ATEMPO, MAX_ATEMPO = 0.90, 1.12
    nwords = len(nvs.tokenize_words(display_full))
    wpm0 = round(nwords / dur * 60, 1) if dur else 0.0
    rate = None
    if dur > 0 and nwords > 0 and wpm0 > MAX_WPM:            # genuine tongue-twister → ease down
        rate = max(MIN_ATEMPO, round(dur / (nwords / MAX_WPM * 60.0), 3))
    elif dur > 0 and nwords > 0 and wpm0 < MIN_WPM:          # draggy/slow → speed up toward the band. nwords>0
        rate = min(MAX_ATEMPO, round(dur / (nwords / MIN_WPM * 60.0), 3))   # guards /0: empty narration = nothing to pace
    if rate and abs(rate - 1.0) > 0.02 and not _reuse_voice:
        sped = os.path.join(assets, "voice_p.mp3")
        subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", "-i", voice_path,
                        "-filter:a", f"atempo={rate}", sped], check=True)
        shutil.move(sped, voice_path)
        dur = AudioFileClip(voice_path).duration
        print(f"[pace] {nwords}w {wpm0}→{round(nwords/dur*60,1) if dur else 0} wpm | atempo {rate} | → {dur:.1f}s")
    else:
        print(f"[pace] {nwords}w {wpm0} wpm | {dur:.1f}s"
              + (" — reuse, no re-pace" if _reuse_voice else " — within comfort band, no change"))
    # KEEP-VIDEO / redo-voice: the new take must FIT the kept video's duration or audio drifts. Stretch
    # the fresh voice to _raw's length (single atempo covers 0.5–2×; beyond that, fall back to full render).
    if _reuse_raw and not _reuse_voice:
        _rawdur = _audio_dur(_raw_p)
        if _rawdur > 0 and dur > 0 and abs(dur - _rawdur) > 0.1:
            _r2 = round(dur / _rawdur, 3)
            if 0.5 <= _r2 <= 2.0:
                _fit = os.path.join(assets, "voice_fit.mp3")
                subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", "-i", voice_path,
                                "-filter:a", f"atempo={_r2}", _fit], check=True)
                shutil.move(_fit, voice_path); dur = AudioFileClip(voice_path).duration
                print(f"[redo] fit new voice to kept video: atempo {_r2} → {dur:.1f}s")
            else:
                print(f"[redo] ⚠ new voice {dur:.1f}s vs video {_rawdur:.1f}s ngoài tầm atempo — nên redo=all")
    asr = __import__("2_SKILLS.srt_maker.asr_router", fromlist=["x"])
    words = asr.transcribe_words(voice_path, language="vi")
    for w in words: w["duration"] = w["end"] - w["start"]
    plan = nvs.prepare_tts_script(display_full)
    dwords = nvs.align_tts_boundaries_to_display_words(plan, words, dur)
    # TAIL-ANCHOR (2026-07, "voice lệch cuối"): on the low-ASR path the aligner SPREADS cues proportionally,
    # so timing error ACCUMULATES toward the end → the last scene/captions drift off the voice. Pin the whole
    # caption timeline to the real voice end (linear rescale) so the tail lands on the voice, not past it.
    if dwords:
        _t0 = float(dwords[0].get("start", 0.0) or 0.0)
        _tN = float(dwords[-1].get("end", dur) or dur)
        _cur = _tN - _t0
        _tgt = (dur - 0.15) - _t0          # last word should end ~0.15s before the voice does
        if _cur > 0.1 and _tgt > 0.1 and abs(_tN - dur) > 0.4:   # only when the tail is meaningfully off
            _k = _tgt / _cur
            for _w in dwords:
                _w["start"] = _t0 + (float(_w.get("start", _t0) or _t0) - _t0) * _k
                _w["end"] = _t0 + (float(_w.get("end", _t0) or _t0) - _t0) * _k
            print(f"[caption-sync] tail-anchored: last cue {_tN:.1f}s → voice end {dur:.1f}s (drift corrected)")
    # Caption-sync QC: the aligner needs ≥1 ASR boundary per spoken word, else it falls
    # back to EVENLY-ESTIMATED timing (captions still show display words — RULE #1 — but
    # drift from the voice). Surface which path was taken so sync quality is observable.
    _ntts, _nasr = len(plan.tts_words), len(words)
    _ratio = round(_nasr / _ntts, 2) if _ntts else 0.0
    if _nasr < 0.6 * _ntts:
        print(f"[caption-sync] ⚠ low ASR ({_nasr}/{_ntts}, ratio {_ratio}) — spreading over the real "
              f"speech envelope (take likely low-quality).")
    elif _nasr < _ntts:
        print(f"[caption-sync] ✓ proportional anchor to real ASR timing (ASR {_nasr} < spoken {_ntts}, "
              f"ratio {_ratio}) — robust to dropped words.")
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
    # PACING GATE (2026-07): measure per-scene durations + flag a slow/slideshow video so the factory
    # catches it BEFORE shipping (the 5-scenes/62s lesson). Advisory print; also feeds the quality score.
    try:
        _durs = [(starts[i+1] if i+1 < len(starts) else float(TOTAL)) - starts[i] for i in range(len(starts))]
        _pw = __import__("spec_lint").lint_pacing(_durs, float(TOTAL))
        _pac_data = {"durations": _durs, "total": float(TOTAL)}
        globals()["_LAST_PACING"] = _pac_data
        # ALSO persist a per-project sidecar: the QA scorer (production_manifest→factory_brain) runs in the
        # PARENT process while renders run in queue_processor SUBPROCESSES — so the parent's _LAST_PACING
        # global is None and the pacing dimension was silently skipped (full credit). The sidecar survives
        # the process boundary so slow slideshows are actually pacing-scored at the gate.
        try:
            with open(os.path.join(project_dir, "_pacing.json"), "w", encoding="utf-8") as _pf:
                json.dump(_pac_data, _pf)
        except Exception:
            pass
        if _pw:
            print("[pacing] " + " | ".join(_pw))
        else:
            print(f"[pacing] ✓ {len(starts)} scenes / {TOTAL:.0f}s = {len(starts)/(TOTAL/60):.1f} scenes/min "
                  f"(avg {TOTAL/max(1,len(starts)):.1f}s/scene)")
        # TRUNCATION guard: catch on-screen text cut mid-clause (the 'TobyFlow không tự' callout bug).
        _tex = []
        for _si, _sc in enumerate(scenes):
            for _f in ("h2",):
                if _sc.get(_f):
                    _tex.append((f"scene{_si+1}.{_f}", _sc[_f]))
            _cp = _sc.get("comp")
            if isinstance(_cp, (list, tuple)) and len(_cp) == 2 and isinstance(_cp[1], dict):
                for _k in ("text", "title"):
                    if _cp[1].get(_k):
                        _tex.append((f"scene{_si+1}.{_cp[0]}", _cp[1][_k]))
        _tw = __import__("spec_lint").truncation_warnings(_tex)
        if _tw:
            print("[truncation] ⚠ " + " | ".join(_tw[:5]))
    except Exception as _pe:
        print(f"[pacing] skipped ({_pe})")
    appear = lambda i: 0.0 if i == 0 else max(0.0, starts[i] - 0.25)
    scene_html, tweens, _fx_profile, lottie_inits = [], [], [], []
    for i, sc in enumerate(scenes):
        ap = appear(i)
        nxt = appear(i+1) if i+1 < len(scenes) else None
        # TIGHT scene↔voice sync: scene i shows exactly for ITS segment's voice, disappearing right as
        # the next scene's voice begins. Do NOT force scenes to overstay (min-dur / long hold) — that
        # desyncs display from narration ("cảnh A còn hiện khi voice đã sang B", user 2026-07-03).
        # Breathing room comes from VOICE PAUSES between scenes (paced join + relaxed silence-trim),
        # which push each scene's start later WITHOUT overlapping the previous scene's voice.
        gone = (nxt + 0.45) if nxt is not None else TOTAL
        d = max(1.0, gone - ap)
        acc = _resolve_acc(_rotate_acc(sc.get("acc", "blue"), accent_shift), brand); cid = f"sc{i}"
        # Render the component defensively: a single malformed component (bad data shape from the LLM/
        # picker) must NOT crash the whole render and discard the expensive voice+render work — it degrades
        # to no-component (the scene still shows its kicker+heading). "đừng để đứt gãy."
        comp_kind = sc["comp"][0] if sc.get("comp") else None
        try:
            comp = _component(sc["comp"][0], sc["comp"][1], acc, _pal) if sc.get("comp") else ""
        except Exception as _ce:
            print(f"[native_composer] scene {i} component '{comp_kind}' failed ({_ce}) — rendering without it.")
            comp, comp_kind = "", None
        # HERO scene = full-bleed accent background + white text (breaks the "always
        # light + centered card" sameness). kicker/heading use white; component picks
        # white via .scene.hero CSS overrides.
        hero = bool(sc.get("hero"))
        scls = "scene clip hero" if hero else "scene clip"
        # HERO = LIGHT accent-tinted panel (brand is light-only) — a subtle tint distinguishes it from
        # body scenes WITHOUT going dark/coloured. Text stays dark; accent lives in kicker + line-2. (2026-07-02)
        sstyle = f' style="background:linear-gradient(157deg,{acc}14 0%,#F8FAFC 72%)"' if hero else ""
        kstyle = f"color:{acc};background:{acc}1f"
        l2style = f"color:{acc}"
        # Ambient depth layer: breathing glow + oversized faint ghost word (the kicker).
        if hero:
            glowbg, ghostcol = "radial-gradient(circle,#ffffff2b 0%,transparent 70%)", "#ffffff14"
        else:
            glowbg, ghostcol = f"radial-gradient(circle,{acc}1f 0%,transparent 70%)", "#0F172A0A"
        # Brand-colour depth blobs (light-mode safe): scene accent + brand coral; white on hero.
        _coral = _theme(brand).get("coral", "#E2724D")
        if hero:
            b1c, b2c, bop = "#ffffff", "#ffffff", "opacity:.09"
        else:
            b1c, b2c, bop = acc, _coral, "opacity:.08"
        # Symmetric placement (same inset + size both sides) so the soft glow never pulls the eye
        # left/right — the content reads dead-centre. One high-left, one low-right for gentle depth.
        blobs = (f'<div class="scblob" id="{cid}_bl1" style="width:540px;height:540px;left:-140px;top:14%;background:{b1c};{bop}"></div>'
                 f'<div class="scblob" id="{cid}_bl2" style="width:540px;height:540px;right:-140px;top:56%;background:{b2c};{bop}"></div>')
        # Ghost layer: a content-matched ILLUSTRATIVE EMOJI (director sets sc["icon"]) so the scene shows
        # WHAT the voice says (fills empty space) — falls back to the faint kicker word. (user 2026-07-03)
        _dsvg = _lucide(sc.get("svg", ""), size=138, color=(acc if not hero else "#ffffff"), sw=1.7) if sc.get("svg") else ""
        _dic = sc.get("icon")
        if sc.get("lottie"):                        # the LOTTIE is the illustrative anchor (top-centre) —
            ghost_html = f'<div class="scghost" style="color:{ghostcol}">{_esc(sc.get("kicker", ""))}</div>'  # keep only the faint word-ghost (58%) for depth; no duplicate top icon
        elif _dsvg:                                 # professional Lucide line-icon (preferred over emoji)
            ghost_html = f'<div class="scghost scghost-ic scghost-svg">{_dsvg}</div>'
        elif _dic:
            ghost_html = f'<div class="scghost scghost-ic">{_dic}</div>'
        else:
            ghost_html = f'<div class="scghost" style="color:{ghostcol}">{_esc(sc.get("kicker", ""))}</div>'
        # Persistent LEFT ACCENT RAIL (density study 2026-07 — "chrome = free density"): a vertical brand
        # bar anchoring the mid-zone on body scenes (skip hero — it has its own tinted panel).
        rail = ("" if hero else
                f'<div class="scrail" style="background:linear-gradient(180deg,{acc},{_coral})"></div>')
        # GHOST NUMERAL (density study 2026-07): a giant faded scene number "0N" (reference "01/06"
        # chapter markers) — free depth + fills the upper-right negative space on body scenes.
        scnum = "" if hero else f'<div class="scnum">{i + 1:02d}</div>'
        # CODE-GLYPH CONFETTI (density study 2026-07 §space-filling): faint scattered code marks in the
        # peripheral negative space → cheap "tech" texture (reference bg filler). Positions rotate by scene.
        _GLY = [(7, 13, 52, "{"), (89, 17, 46, "}"), (11, 84, 48, "</>"), (91, 76, 56, "("),
                (5, 47, 42, ";"), (94, 45, 48, "="), (15, 30, 38, "[ ]"), (85, 90, 44, ")")]
        _off = i % len(_GLY)
        conf = ("" if hero else '<div class="scconf">' + "".join(
            f'<span style="left:{lx}%;top:{ty}%;font-size:{sz}px">{_esc(g)}</span>'
            for (lx, ty, sz, g) in (_GLY[_off:] + _GLY[:_off])) + '</div>')
        scbg = (f'<div class="scbg">{blobs}<div class="scglow" style="background:{glowbg}"></div>'
                f'{conf}{rail}{scnum}{ghost_html}</div>')
        # Decorative EFFECT overlay from the library — the DIRECTOR's chosen accent (sc.fx.effect) wins,
        # else sparse per-video auto. This is the seek-safe animation-accent layer the director holds.
        _fxforce = (sc.get("fx") or {}).get("effect")
        _fxhtml, _fxtw, _ = el.overlay(cid, ap, d, i, _vseed, force=_fxforce) if (i or _fxforce) else (None, [], None)
        # LOTTIE ACCENT (the director sets sc["lottie"] = a content-matched animation). Rendered INSIDE the
        # composition + driven by a GSAP tween → seek-safe (GSAP fires onUpdate under .seek, as the count-up
        # numbers already rely on). Real relevance: the anim matches the scene meaning, not random decoration.
        _lot_html = ""
        _lj = _lottie_json(sc.get("lottie", "")) if sc.get("lottie") else None
        if _lj:
            _lid = f"{cid}_lot"
            _lot_html = f'<div class="sclottie" id="{_lid}"></div>'
            lottie_inits.append(
                f'window.__lot["{_lid}"]=lottie.loadAnimation({{container:document.getElementById("{_lid}"),'
                f'renderer:"svg",loop:false,autoplay:false,animationData:{_lj}}});')
            _ls = ap + 0.2
            tweens.append(f'tl.fromTo("#{_lid}",{{scale:0.6,opacity:0}},{{scale:1,opacity:1,duration:0.5,ease:"back.out(1.7)"}},{_ls:.2f});')
            tweens.append(
                f'tl.to({{p:0}},{{p:1,duration:{max(0.6, d-0.6):.2f},ease:"none",onUpdate:function(){{'
                f'var a=window.__lot["{_lid}"];if(a&&a.totalFrames)a.goToAndStop(this.targets()[0].p*(a.totalFrames-1),true);}}}},{_ls:.2f});')
        scene_html.append(
            f'<div class="{scls}" id="{cid}"{sstyle} data-start="{ap:.2f}" data-duration="{d:.2f}" data-track-index="{2+(i%2)*3}">'
            f'{scbg}{_fxhtml or ""}{_lot_html}{_prograil(i, len(scenes), acc, hero)}'
            f'<div class="kicker" style="{kstyle}">{_esc(_kicker_label(sc.get("kicker", "")))}</div>'
            f'<h1 class="head{_hook_style(sc.get("h1","")+" "+sc.get("h2",""))}"><span class="l1">{_words(sc.get("h1",""))}</span><span class="l2" style="{l2style}">{_words(sc.get("h2",""))}<i class="l2u" style="background:{"#fff" if hero else acc}"></i></span></h1>'
            + (f'<div class="subnote">{_esc(sc["subnote"])}</div>' if sc.get("subnote") else "")
            + f'<div class="comp">{comp}</div>'
            # SUPPORTING CHIPS (density study 2026-07): a 2-3 chip cluster under the hero so a single-
            # component scene reads DENSE (never one bare component). Director sets sc["chips"].
            + ((f'<div class="dchips">' + "".join(
                f'<span class="dchip ritem" style="border-color:{acc};color:{acc}">{_esc(c)}</span>'
                for c in sc["chips"][:3]) + '</div>') if sc.get("chips") else "")
            + '</div>')
        if i == 0:
            tweens.append(f'tl.set("#{cid}",{{opacity:1}},0);')
            tweens.append(f'tl.set("#{cid} .kicker",{{y:0}},0);tl.set("#{cid} .head",{{y:0}},0);tl.set("#{cid} .comp",{{y:0,scale:1}},0);')
        else:
            tweens.append(f'tl.fromTo("#{cid}",{{opacity:0}},{{opacity:1,duration:0.32,ease:"power1.out"}},{ap:.2f});')
            # TWO independent rotating dimensions from the effect library, seeded per-video so
            # different videos get different sequences + fresh combinations (no "same every time"):
            #   • TRANSITION animates the kicker + component
            #   • TEXT-EFFECT animates the headline (rise / word-up / clip-wipe / word-pop / drop)
            _etw, _tname = el.entrance(cid, ap, i, _vseed, kind=comp_kind,
                                       force=(sc.get("fx") or {}).get("transition"))
            tweens.extend(_etw)
            _htw, _ = el.text_effect(cid, ap, i, _vseed)
            tweens.extend(_htw)
            _fx_profile.append(_tname)   # flywheel: record the transition used (per scene)
            tweens.extend(_fxtw)   # decorative overlay tween (empty when this scene has no overlay)
        # Marker underline draws under the accent heading word (craft/references/css-patterns.md
        # "highlight/sketch" modes, re-skinned): a hand-drawn accent rule that sweeps in.
        ut = 0.50 if i == 0 else ap + 0.60
        tweens.append(f'tl.fromTo("#{cid} .l2u",{{scaleX:0}},{{scaleX:1,duration:0.50,ease:"power2.out"}},{ut:.2f});')
        # EMPHASIS zoom-punch (SKILL AUTO): the accent heading word pulses 1→1.06→1 as its underline
        # draws — a subtle beat on the key word (numbers already punch in the bignum component).
        tweens.append(f'tl.fromTo("#{cid} .l2",{{scale:1.0}},{{scale:1.055,duration:0.16,ease:"power2.out",transformOrigin:"left center"}},{ut-0.04:.2f});')
        tweens.append(f'tl.to("#{cid} .l2",{{scale:1.0,duration:0.42,ease:"power2.out"}},{ut+0.12:.2f});')
        # Ambient MOTION (glow breathe + ghost + brand-blob drift) from the effect library — the
        # blob-drift profile rotates per-video so the background feels different across videos.
        tweens.extend(el.motion_ambient(cid, ap, d, _vseed))
        # SUB-BEAT (2026-07 pacing): a LONG scene (>7s) with its reveals done early goes static → retention
        # dies. Add a mid-scene re-emphasis beat (~62% through): pulse the heading accent line + nudge the
        # component, so every long scene has a 2nd visual event. Seek-safe (pure GSAP), no voice change.
        if d > 7.0 and not hero:
            _mb = ap + d * 0.62
            tweens.append(f'tl.fromTo("#{cid} .l2u",{{scaleX:1}},{{scaleX:1.06,duration:0.22,ease:"power2.out",transformOrigin:"left center"}},{_mb:.2f});')
            tweens.append(f'tl.to("#{cid} .l2u",{{scaleX:1,duration:0.5,ease:"power2.inOut"}},{_mb+0.24:.2f});')
            tweens.append(f'tl.fromTo("#{cid} .comp",{{y:0}},{{y:-8,duration:0.28,ease:"sine.inOut"}},{_mb:.2f});')
            tweens.append(f'tl.to("#{cid} .comp",{{y:0,duration:0.5,ease:"sine.inOut"}},{_mb+0.3:.2f});')
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
                else:                  # non-numeric bignum → entrance land with REAL spring physics
                    pt = ap + 0.55                       # springLand overshoots then settles (Remotion spring);
                    # falls back to a normal ease if CustomEase failed to load (guarded registration).
                    tweens.append(f'tl.fromTo("#{cid} .c-bignum .big",{{scale:0.72,opacity:0}},{{scale:1.0,opacity:1,duration:0.68,ease:"springLand"}},{pt:.2f});')
        # BUILD-ON: reveal multi-item content one-by-one as the scene plays (synced with
        # the per-item pop SFX in _sfx_cues), instead of showing the whole card at once.
        grp_i = groups[i] if i < len(groups) else []
        rplan = _reveal_plan(grp_i[0]["start"], grp_i[-1]["end"], _reveal_count(sc.get("comp"))) if grp_i else None
        if rplan:
            rstart, rint, _ = rplan
            # VOICE-SYNCED item reveals: each .ritem builds WHEN the narration names it (falls back to the
            # even rstart+k*rint when a keyword isn't found). The per-item pop SFX in _sfx_cues uses the SAME
            # `_item_reveal_times`, so visual + SFX stay locked. Entrance DIRECTION/EASE still varies per item.
            _rtimes = _item_reveal_times(sc.get("comp"), grp_i, rstart, rint, _reveal_count(sc.get("comp")))
            _Tjs = "[" + ",".join(f"{t:.2f}" for t in _rtimes) + "]"
            tweens.append(
                ';(function(){var _it=document.querySelectorAll("#%s .ritem");var _T=%s;'
                'var _E=[{x:-44,ease:"expo.out",duration:0.50},{y:26,ease:"power3.out",duration:0.46},'
                '{x:44,ease:"expo.out",duration:0.50},{scale:0.90,ease:"back.out(1.4)",duration:0.55}];'
                '_it.forEach(function(el,k){var e=Object.assign({opacity:0},_E[k%%_E.length]);'
                'tl.from(el,e,(_T[k]!=null?_T[k]:%.2f+k*%.3f));});})();' % (cid, _Tjs, rstart, rint))
            # ACTIVE-ROW (density study 2026-07): a highlight travels the list — light each item as it
            # reveals (accent ring), dim it when the next appears → reads as "active state synced to voice".
            if comp_kind in ("steps", "feature", "badges", "checklist", "icongrid", "hub"):
                tweens.append(
                    ';(function(){var _it=document.querySelectorAll("#%s .ritem");var _T=%s;'
                    '_it.forEach(function(el,k){var t=(_T[k]!=null?_T[k]:%.2f+k*%.3f);'
                    'tl.to(el,{boxShadow:"0 0 0 3px %s66,0 16px 36px rgba(20,40,90,.15)",duration:0.22},t+0.05);'
                    'if(k<_it.length-1)tl.to(el,{boxShadow:"0 12px 28px rgba(20,40,90,.07)",duration:0.30},(_T[k+1]!=null?_T[k+1]:%.2f+(k+1)*%.3f));});})();'
                    % (cid, _Tjs, rstart, rint, acc, rstart, rint))
            # Chart bars GROW left→right via a clip-path wipe (craft/data-in-motion.md: a
            # number needs visual weight; a bar that fills reads as data, not static text).
            # clip-path wipe (not scaleX) so the value label never distorts.
            if comp_kind == "chart":
                tweens.append(
                    ';(function(){var _b=document.querySelectorAll("#%s .chfill");'
                    '_b.forEach(function(el,k){tl.fromTo(el,{clipPath:"inset(0 100%% 0 0)"},'
                    '{clipPath:"inset(0 0%% 0 0)",duration:0.62,ease:"power2.out"},%.2f+k*%.3f+0.05);});})();'
                    % (cid, rstart, rint))
            # DATA-FLOW (HyperFrames motion / GSAP MotionPath idea): a token travels each concept_build edge
            # A→B after the nodes build → the diagram reads as data MOVING through the process, not a static
            # slide. Straight edges = a seek-safe x/y tween (MotionPathPlugin loaded for future curved paths).
            if comp_kind == "concept_build":
                tweens.append(
                    ';(function(){var S=document.querySelector("#' + cid + ' .cb-svg");'
                    'var C=document.querySelector("#' + cid + ' .c-cb");if(!S||!C)return;'
                    'S.querySelectorAll("line").forEach(function(l,k){'
                    'var x1=+l.getAttribute("x1"),y1=+l.getAttribute("y1"),x2=+l.getAttribute("x2"),y2=+l.getAttribute("y2");'
                    'var d=document.createElement("div");d.className="cb-flow";d.style.background="' + acc + '";C.appendChild(d);'
                    'var t0=' + f'{rstart:.2f}' + '+(k+1)*' + f'{max(rint,0.5):.3f}' + ';'
                    'tl.set(d,{opacity:0,x:x1,y:y1},0);'
                    'tl.to(d,{opacity:1,duration:0.18},t0);'
                    'tl.to(d,{x:x2,y:y2,duration:0.9,ease:"power1.inOut"},t0);'
                    'tl.to(d,{opacity:0,duration:0.22},t0+0.72);});})();')
            # LINECHART data-flow (GSAP MotionPath): a glowing dot rides the trend line start→end, so the
            # growth reads as MOVEMENT. Seek-safe (timeline-driven); guarded (no-op if plugin absent).
            if comp_kind == "linechart":
                tweens.append(
                    ';(function(){if(!window.MotionPathPlugin)return;'
                    'var c=document.querySelector("#' + cid + ' .lc-flow"),p=document.querySelector("#' + cid + ' .lc-line");'
                    'if(!c||!p)return;var t0=' + f'{rstart + 0.4:.2f}' + ';'
                    'tl.set(c,{opacity:0},0);tl.to(c,{opacity:1,duration:0.2},t0);'
                    'tl.to(c,{motionPath:{path:p,alignOrigin:[0.5,0.5]},duration:1.5,ease:"power1.inOut"},t0);'
                    'tl.to(c,{opacity:0,duration:0.3},t0+1.5);})();')
            # STRIKE-LIST: the strike line DRAWS across each "old way" item shortly after it reveals (scaleX
            # 0→1) — the animated cross-out that makes the before→after land. Seek-safe.
            if comp_kind == "strike_list":
                tweens.append(
                    ';(function(){var ls=document.querySelectorAll("#' + cid + ' .sk-line");'
                    'ls.forEach(function(l,k){tl.to(l,{scaleX:1,duration:0.4,ease:"power2.inOut"},'
                    + f'{rstart:.2f}' + '+k*' + f'{max(rint, 0.45):.3f}' + '+0.28);});})();')
        # KEN BURNS on a real screenshot (user 2026-07-03: "cần video, cuộn chuột" — a static shot reads
        # as dead; a slow zoom+pan makes it feel like live footage/scrolling). Seek-safe GSAP tween over
        # the scene span; clipped by .c-mockup overflow:hidden. Only when a REAL image is present.
        if comp_kind == "mockup" and sc.get("comp") and (sc["comp"][1] or {}).get("img"):
            _kb_end = nxt if nxt is not None else TOTAL
            _kb_dur = max(1.4, _kb_end - ap - 0.2)
            tweens.append('tl.fromTo("#%s .mkshot img",{scale:1.0,yPercent:0},'
                          '{scale:1.14,yPercent:-12,duration:%.2f,ease:"none"},%.2f);'
                          % (cid, _kb_dur, ap))
        if nxt is not None:
            # Old scene fully GONE by the moment the next mounts (data-start=nxt) → the
            # two are NEVER on screen together (no double-text/ghosting at all). The new
            # then fades in from the light branded bg; the ~1 transition frame is bg+dots,
            # never black. EXIT STYLE rotates per scene (from the effect library, seeded per-video)
            # so cuts aren't all the same crossfade — but always non-overlapping.
            ex, _ = el.exit_delta(i, _vseed)
            tweens.append(f'tl.to("#{cid}",{{opacity:0{ex},duration:0.34,ease:"power2.in"}},{nxt-0.34:.2f});')

    # karaoke chunks (~4 words), alternating tracks
    chunks = []
    for si, grp in enumerate(groups):
        acc = _resolve_acc(_rotate_acc(scenes[si].get("acc", "blue") if si < len(scenes) else "blue", accent_shift), brand)
        for j in range(0, len(grp), 4):
            sub = grp[j:j+4]
            if sub: chunks.append({"start": sub[0]["start"], "end": sub[-1]["end"], "acc": acc, "words": sub})
    # Caption-readability QC (advisory) — flag cues that break reading-speed standards (too fast/long/brief)
    # so an unreadable subtitle is observable, same non-blocking spirit as the caption-sync QC above.
    try:
        import caption_segment as _cseg
        _warn = _cseg.readability_warnings([c["words"] for c in chunks])
        if _warn:
            print(f"[caption-readability] ⚠ {len(_warn)} cue(s) hard to read (first 3):")
            for _w in _warn[:3]:
                print(f"    · {_w}")
        else:
            print(f"[caption-readability] ✓ all {len(chunks)} cues within reading-speed standards.")
    except Exception as _e:
        print(f"[caption-readability] skipped ({_e})")
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
            ws = w["start"]; _a = ch["acc"]
            tweens.append(f'tl.set("#k{ci}_{wi}",{{color:"{_a}",fontWeight:800}},{ws:.2f});')
            # ASR keyword pop (HyperFrames animation skill) — the word being SPOKEN gently pops + glows,
            # drawing the eye to it in real time. Seek-safe (GSAP), reflow-safe (span is inline-block, so
            # transform:scale doesn't move neighbours). Attack then settle back to rest.
            tweens.append(f'tl.fromTo("#k{ci}_{wi}",{{scale:1,textShadow:"0 0 0px {_a}00"}},'
                          f'{{scale:1.12,textShadow:"0 0 15px {_a}",duration:0.13,ease:"power2.out"}},{ws:.2f});')
            tweens.append(f'tl.to("#k{ci}_{wi}",{{scale:1,textShadow:"0 0 0px {_a}00",duration:0.34,ease:"power2.in"}},{ws+0.14:.2f});')
            tweens.append(f'tl.set("#k{ci}_{wi}",{{color:"#E5E7EB",fontWeight:700}},{w["end"]:.2f});')

    # fitText: shrink any oversized number/headline to fit its container BEFORE the timeline
    # is built (runs once at load → identical on every captured frame, so it's deterministic).
    # Stops the long-number / long-word overflow that made big stats spill past the card.
    # fitH: after the text shrink, scale DOWN (via CSS `zoom`, not transform — transform is owned by the
    # GSAP reveal tweens) any component whose bottom crosses the safe-content line, so a tall component
    # (checklist/steps at max items, photocard) can't overflow into the karaoke/footer. Portrait only
    # (SAFE_CONTENT_BOTTOM is a 1920-tall constant); landscape already scales content via `vs`.
    _fith = (f"function fitH(sel,maxB){{var e=document.querySelectorAll(sel);"
             "for(var i=0;i<e.length;i++){var el=e[i],r=el.getBoundingClientRect();"
             "if(r.height>4&&r.bottom>maxB){var av=maxB-r.top;if(av>120){"
             "el.style.zoom=(av/r.height).toFixed(3);}}}}"
             f"fitH('.comp',{SAFE_CONTENT_BOTTOM});") if _DIMS.get(aspect, (1080, 1920))[1] == 1920 else ""
    fit_js = ("(function(){function fit(sel,minPx){var e=document.querySelectorAll(sel);"
              "for(var i=0;i<e.length;i++){var el=e[i],p=el.parentElement||el,"
              "av=(p.clientWidth||0)*0.96;if(!av)continue;"
              "var s=parseFloat(getComputedStyle(el).fontSize)||60,g=0;"
              "while(el.scrollWidth>av&&s>minPx&&g++<90){s-=2;el.style.fontSize=s+'px';}}}"
              "fit('.c-bignum .big',96);fit('.c-stats .stnum',38);fit('.c-mockup .mk-num',30);"
              "fit('.head .l1',46);fit('.head .l2',46);" + _fith + "})();")
    js = "window.__timelines=window.__timelines||{};" + fit_js + "const tl=gsap.timeline({paused:true});" + "".join(tweens) + 'window.__timelines["main"]=tl;'
    VW, VH = _DIMS.get(aspect, (1080, 1920))
    res = "portrait" if VH >= VW else "landscape"
    # Lottie: inline the player ONCE (only if any scene uses a lottie accent) + the per-scene inits. The
    # drive tweens (in `js`) call goToAndStop under GSAP .seek → seek-safe, like the count-up numbers.
    _lottie_player = ""
    _lottie_init = ""
    if lottie_inits:
        try:
            _lottie_player = f'<script>{open(os.path.join(_LOTTIE_DIR, "lottie.min.js"), encoding="utf-8").read()}</script>'
            _lottie_init = f'<script>window.__lot={{}};{"".join(lottie_inits)}</script>'
        except Exception:
            _lottie_player = _lottie_init = ""
    doc = (f'<!doctype html><html lang="vi" data-resolution="{res}"><head><meta charset="UTF-8"/>'
           f'{_lottie_player}'
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
           # SplitText = free GSAP plugin (3.13+) → per-character kinetic typography (effect_library char-cascade).
           # Best-effort: if it fails to load, the char-cascade recipe falls back to a whole-headline rise.
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/SplitText.min.js"></script>'
           # MotionPathPlugin = free since GSAP 3.13 → flow a token ALONG a path (data-flow motion on
           # concept_build edges). Guarded: if it fails to load, the flow tween no-ops (never breaks render).
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/MotionPathPlugin.min.js"></script>'
           # CustomEase = free since GSAP 3.13. We register `springLand` = a REAL damped-spring curve
           # (ported from Remotion's spring solver) → hero moments land with physics, not just an ease.
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>'
           f'<script>try{{gsap.registerPlugin(SplitText);}}catch(e){{}}'
           f'try{{gsap.registerPlugin(MotionPathPlugin);}}catch(e){{}}'
           # spring PRESETS (Remotion spring math → GSAP CustomEase) — tune ζ per feel: soft≈critical (gentle
           # settle), land=default, snappy=fast, bouncy=playful (use sparingly on a clean brand).
           f'try{{gsap.registerPlugin(CustomEase);'
           f'CustomEase.create("springLand","{_spring_ease_path(140,1,13)}");'
           f'CustomEase.create("springSoft","{_spring_ease_path(110,1,20)}");'
           f'CustomEase.create("springSnappy","{_spring_ease_path(220,1,20)}");'
           f'CustomEase.create("springBouncy","{_spring_ease_path(130,1,9)}");}}catch(e){{}}</script>'
           # __nz = compact seeded 1D value-noise (Remotion @remotion/noise idea) → ORGANIC drift for
           # background blobs (meander, not a straight sine slide). Deterministic → seek-safe.
           f'<script>window.__nz=function(s,x){{function h(n){{n=(n<<13)^n;'
           f'return 1-((n*(n*n*15731+789221)+1376312589)&2147483647)/1073741824;}}'
           f'var i=Math.floor(x),f=x-i,u=f*f*(3-2*f);return h(i+s)*(1-u)+h(i+1+s)*u;}};</script>'
           f'<style>{_css(brand, VW, VH)}</style></head><body>'
           f'<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.2f}" data-width="{VW}" data-height="{VH}">'
           f'<div class="dots"></div>'
           f'<audio id="voice" class="clip" data-start="0" data-duration="{TOTAL:.2f}" data-track-index="0" src="assets/voice.mp3" data-volume="1"></audio>'
           f'<img class="brandlogo" src="assets/logo.png"/>'
           f'{"".join(scene_html)}'
           f'<div class="footer">{FOOTERS.get(brand, BRAND["footer"])}</div>'
           f'{"".join(kara_html)}{_lottie_init}<script>{js}</script></div></body></html>')
    json.dump({"$schema":"https://hyperframes.heygen.com/schema/hyperframes.json","paths":{"blocks":"compositions","components":"compositions/components","assets":"assets"}}, open(os.path.join(proj,"hyperframes.json"),"w"))
    json.dump({"id":"seosona-video","name":"SEOSONA Video"}, open(os.path.join(proj,"meta.json"),"w"))
    open(os.path.join(proj,"index.html"),"w",encoding="utf-8").write(doc)

    # 5) lint + render native — SKIPPED when the video is reused (redo=voice/mix/thumb): the HTML above
    # is still built (cheap) but the expensive HyperFrames render is not re-run.
    # ABSOLUTE — the HF render runs with cwd=proj, so a relative --output would nest the file inside
    # proj/ and the SFX step below (different cwd) would not find it, silently failing. Keep it absolute.
    raw = _raw_p
    if _reuse_raw:
        print("[redo] reuse cached _raw.mp4 (skip HyperFrames render)")
    else:
        cli = _hf_cli()
        renv = _render_env()   # point the node renderer at concrete ffmpeg/ffprobe binaries
        subprocess.run(["node", cli, "lint"], cwd=proj, env=renv)
        # HyperFrames 0.7.24 render knobs — configurable, default = current behaviour (standard, no GPU).
        #   SEOSONA_RENDER_QUALITY = draft (fast proofs) | standard (default) | high (near-lossless delivery)
        #   SEOSONA_RENDER_GPU=1   → hardware (NVENC) encode; OFF by default (respect GPU budget / avoid
        #                            contention with voice training — the user gates GPU use explicitly)
        #   SEOSONA_RENDER_WORKERS = N | auto (default auto; each worker ≈ a Chrome proc ~256MB)
        _rcmd = ["node", cli, "render", "--format", "mp4"]
        _q = os.environ.get("SEOSONA_RENDER_QUALITY", "").strip().lower()
        if _q in ("draft", "standard", "high"):
            _rcmd += ["--quality", _q]
        _wk = os.environ.get("SEOSONA_RENDER_WORKERS", "").strip()
        if _wk:
            _rcmd += ["--workers", _wk]
        if os.environ.get("SEOSONA_RENDER_GPU") == "1":
            _rcmd += ["--gpu"]
        _rcmd += ["--output", raw]
        subprocess.run(_rcmd, cwd=proj, check=True, env=renv)

    # 6) MIX = voice (from raw) + BGM ducked under voice (sidechain) + component SFX,
    #    then loudnorm + brickwall limiter. Inputs: [0]=raw(voice video), [1]=bgm
    #    (looped), [2..]=SFX. BGM sidechain-ducks to the voice so narration is always
    #    clear; SFX sit between. The final alimiter GUARANTEES no clipping.
    out = os.path.abspath(output or os.path.join(project_dir, "FINAL.mp4"))
    _reuse_final = _skip("mix") and _reuse_raw and _reuse_voice and os.path.exists(out)
    cues = _sfx_cues(groups, scenes, TOTAL, seed=_vseed)
    _bseed = os.path.basename(out)
    bgm = _bgm(music, seed=_bseed)                        # rotate the mood pool, stable per output file
    # BGM MEDLEY (user rule): for videos long enough for >1 segment, cross-fade 60s-of-each across several
    # tracks instead of looping ONE. Falls back to the single looped track when a medley isn't warranted.
    _medley = _bgm_medley(music, TOTAL, _bseed, os.path.join(assets, "bgm_medley.mp3"))
    # BEAT-AWARE SFX: nudge transition whooshes onto the actual BGM's beat (voice/scene timing untouched).
    # Opt-out via SEOSONA_BEAT_SFX=0. Analyses whichever track actually plays (medley spans the video;
    # a single track is stream-looped so its onsets tile).
    if os.environ.get("SEOSONA_BEAT_SFX", "1") == "1":
        cues = _snap_cues_to_beats(cues, _medley or bgm, TOTAL, looped=not _medley)
    if _medley:
        inputs = ["-i", raw, "-i", _medley]              # medley already spans the video — no stream_loop
    else:
        inputs = ["-i", raw, "-stream_loop", "-1", "-i", bgm]
    # VOICE SOURCE: normally the freshly-rendered _raw's own audio ([0:a]). When the VIDEO is reused
    # (redo=voice → keep video, new voice), _raw's baked audio is stale → take the voice from the fresh
    # voice.mp3 appended as the last input; the video still maps from _raw (0:v). Index is known upfront
    # (raw=0, bgm=1, sfx=2..len+1, voice=len+2).
    _vidx = f"{len(cues) + 2}:a" if _reuse_raw else "0:a"
    # Voice is the HERO of the mix: boost it and keep BGM well under it so narration is
    # never buried. BGM ducks further under the (boosted) voice via sidechain.
    filt = [f"[{_vidx}]asplit=2[v0][vkey]",
            "[v0]volume=1.3[vmain]",
            "[1:a]volume=0.18[bg0]",
            "[bg0][vkey]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[bgduck]"]
    # SFX get a short fade-in (kills the hard-attack "click" at sample start) + a tail
    # fade-out (no abrupt cut-off) — the standard pro-audio de-click. Technique harvested
    # from capcut-cli's render filtergraph (afade); applied natively (free, headless).
    FIN, FOUT = 0.03, 0.08
    mixn_sfx, sfxkeys = [], []
    for i, (t, path, vol) in enumerate(cues):
        inputs += ["-i", path]
        ms = int(t * 1000)
        fade = f",afade=t=in:st=0:d={FIN}"
        d = _audio_dur(path)
        if d > FIN + FOUT + 0.02:                       # only if the clip is long enough
            fade += f",afade=t=out:st={round(d - FOUT, 3)}:d={FOUT}"
        # split each cue: one copy into the final mix, one into the BGM-duck sidechain key
        filt.append(f"[{i+2}]volume={vol}{fade},adelay={ms}|{ms},asplit=2[s{i}][s{i}k]")
        mixn_sfx.append(f"[s{i}]"); sfxkeys.append(f"[s{i}k]")
    # BGM ducks under the SFX too (like CapCut) — a light SECOND sidechain: sum the SFX into a
    # key and dip the (already voice-ducked) BGM under each hit so SFX punch through cleanly.
    # Lighter than the voice duck (ratio 4 vs 8) so it's a gentle dip, not a pump.
    bgfinal = "[bgduck]"
    if sfxkeys:
        filt.append("".join(sfxkeys) + f"amix=inputs={len(sfxkeys)}:normalize=0[sfxkey]")
        filt.append("[bgduck][sfxkey]sidechaincompress=threshold=0.05:ratio=4:attack=8:release=180[bgduck2]")
        bgfinal = "[bgduck2]"
    # Fade the MUSIC out over the last ~1.8s so it never cuts abruptly at the amix end — critical for the
    # medley (which otherwise plays at full level right up to the cut, since its own fade sits at the medley
    # end, past the video). Only the BGM chain is faded; the voice (hero) and SFX are untouched, so the
    # closing narration still lands clean over a gently-tailing bed. (st clamped ≥0 for very short videos.)
    _bgfo = max(0.1, dur - 1.8)
    filt.append(f"{bgfinal}afade=t=out:st={_bgfo:.2f}:d=1.8[bgend]")
    bgfinal = "[bgend]"
    if _reuse_raw:                       # append the fresh voice as the last input (see _vidx above)
        inputs += ["-i", os.path.join(assets, "voice.mp3")]
    mixn = ["[vmain]", bgfinal] + mixn_sfx
    # alimiter first catches big transients, then loudnorm LAST sets loudness AND
    # hard-limits TRUE peak to its TP target (dBTP) — guarantees TP < 0 on every channel.
    # loudnorm resamples to a high internal rate; aresample back to 48k so the output is
    # a STANDARD 48 kHz stream. A 96 kHz AAC plays fine in ffmpeg but is SILENT in many
    # players/platforms (web, mobile, social) — that reads as "no voice".
    fc = ";".join(filt) + ";" + "".join(mixn) + \
        f"amix=inputs={len(mixn)}:normalize=0:duration=first[mix];" \
        f"[mix]alimiter=limit=0.95:level=disabled,loudnorm=I={target_lufs}:TP=-1.5:LRA=11,aresample=48000[ao]"
    if _reuse_final:
        print("[redo] reuse FINAL.mp4 (skip mix + overlay)")
    else:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)   # ensure --out to a new dir exists (ffmpeg won't mkdir)
        subprocess.run([_ffmpeg_bin(),"-y","-hide_banner","-loglevel","error",*inputs,"-filter_complex",fc,
                        "-map","0:v","-map","[ao]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000",out], check=True)

    # 6b) BLOCK OVERLAY (gated, additive) — scenes may carry a HyperFrames registry block
    #     (comp=("block",{name}) or scene["block"]); render it + overlay onto the final video at the
    #     scene's time window. Pure no-op when no scene uses a block, so normal news renders are unchanged.
    if not _reuse_final:
        try:
            _overlay_blocks(out, scenes, starts, TOTAL)
        except Exception as e:
            print(f"[native_composer] block overlay skipped: {e}")
        try:
            _overlay_scroll(out, scenes, starts, TOTAL)     # real page-scroll footage on the mockup scene
        except Exception as e:
            print(f"[native_composer] scroll overlay skipped: {e}")

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

    # 8) THUMBNAIL FRAME — grab a representative frame (scene-0 hook is full at frame 0;
    # take a moment in so motion has settled) → <project_dir>/Thumbnail/thumbnail_frame.png.
    # This is a raw-frame FALLBACK; the branded designer PNG (video_engine._make_thumbnail)
    # owns the canonical thumbnail.png. Kept under a separate name so they no longer collide.
    try:
        thumb_dir = os.path.join(os.path.dirname(out) or ".", "Thumbnail")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb = os.path.join(thumb_dir, "thumbnail_frame.png")
        # Pick the SHARPEST, best-exposed, most-informative frame (Katna-style scorer) instead of a blind
        # grab that can land on a blurry crossfade. Falls back to the fixed 12%-in grab if scoring fails.
        picked = None
        try:
            _fs_dir = os.path.join(ROOT, "2_SKILLS", "thumbnail_maker")
            if _fs_dir not in sys.path:
                sys.path.insert(0, _fs_dir)
            import frame_scorer as _fscore
            picked = _fscore.best_frame(out, thumb)
        except Exception as _fe:
            print(f"[native_composer] frame scorer skipped: {_fe}")
        if not picked:
            grab_t = min(2.0, max(0.5, (TOTAL or 4) * 0.12))
            subprocess.run([_ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
                            "-ss", f"{grab_t:.2f}", "-i", out, "-frames:v", "1", thumb], check=True)
        print(f"THUMB: {thumb}{'' if picked else ' (fixed-grab fallback)'}")
    except Exception as e:
        print(f"[native_composer] thumbnail grab skipped: {e}")

    print(f"FINAL: {out}  ({len(cues)} SFX cues, BGM ducked: {os.path.basename(bgm)})")
    # CC-BY attribution: if the chosen BGM is a sourced track (in bgm_sourcer's ATTRIBUTION.json), write a
    # credit line beside the output so the publisher can put it in the description — honouring the licence.
    try:
        _att = json.load(open(os.path.join(BGM_DIR, "ATTRIBUTION.json"), encoding="utf-8"))
        _hit = next((a for a in _att if a.get("file") == os.path.basename(bgm)), None)
        if _hit:
            _credit = (f'Music: "{_hit.get("title","")}" by {_hit.get("creator","")} '
                       f'({_hit.get("license","")}) — {_hit.get("source","")}')
            with open(out + ".credits.txt", "w", encoding="utf-8") as _cf:
                _cf.write(_credit + "\n")
            print(f"[native_composer] BGM credit → {os.path.basename(out)}.credits.txt")
    except Exception:
        pass                                             # built-in tracks need no attribution; never blocks
    # Phase 6: emit a render metric to the observability hub (best-effort, never fatal).
    try:
        sys.path.insert(0, os.path.join(ROOT, "9_DASHBOARD"))   # observability hub home
        import obs_metrics
        obs_metrics.record("render", output=out, brand=brand, duration=round(dur, 1),
                           wpm=wpm0, caption_sync=("real" if _nasr >= _ntts else "estimated"),
                           sfx=len(cues), render_seconds=round(time.time() - _t0, 1),
                           effects="+".join(_fx_profile))   # flywheel: transition profile used
    except Exception as _e:
        print(f"[obs] render metric skipped: {_e}")

    # AUTO-FIX — close the "gặp lỗi tự fix" loop: evaluate the finished render and, if a STAGE failed,
    # auto-redo only that stage ONCE (silent audio → voice · blank/black frames → visual · too-short →
    # full). Bounded (the 'autofix' tag blocks re-entry); opt out with SEOSONA_AUTOFIX=0.
    if os.environ.get("SEOSONA_AUTOFIX", "1") != "0" and "autofix" not in _redo:
        try:
            import evaluator as _evm
            _ev = _evm.evaluate(out, record=False) or {}
            if not _ev.get("ok"):
                _rs = " ".join(_ev.get("reasons", [])).lower()
                _stage = ("voice" if ("silent" in _rs or "audio" in _rs) else
                          "visual" if ("blank" in _rs or "black" in _rs) else
                          "all" if "short" in _rs or "duration" in _rs else None)
                if _stage:
                    print(f"[autofix] lỗi render {_ev.get('reasons')} → tự sửa redo={_stage}")
                    return make_video(project_dir, segments, scenes, lexicon=lexicon, output=output,
                                      target_lufs=target_lufs, voice=voice, theme=theme, music=music,
                                      accent_shift=accent_shift, brand=brand, aspect=aspect,
                                      redo=f"{_stage},autofix")
                print(f"[autofix] phát hiện lỗi nhưng không map được stage: {_ev.get('reasons')}")
        except Exception as _e:
            print(f"[autofix] skipped ({_e})")
    return out


def _srt_ts(sec):
    # round to whole milliseconds FIRST, then decompose — computing ms separately let a fractional part
    # that rounds up (e.g. 5.9996 → 999.6 → 1000) emit "00:00:05,1000" (invalid: ms must be 000-999, must
    # carry to the next second). divmod on the total ms can't overflow → always a valid SRT timestamp.
    ms_total = int(round(max(0.0, float(sec)) * 1000))
    h, ms_total = divmod(ms_total, 3_600_000)
    m, ms_total = divmod(ms_total, 60_000)
    s, ms = divmod(ms_total, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _write_srt(path, groups, segments):
    """One subtitle cue per scene, timed from that scene's display-word group. Each cue's text is wrapped
    at NATURAL break points to ≤42 chars/line (Netflix/BBC standard) so the uploaded caption isn't one
    over-long line — the same readability standard `caption_segment.readability_warnings` checks."""
    try:
        import caption_segment as _cs
        _wrap = lambda t: "\n".join(_cs.segment_text(t)) or t
    except Exception:
        _wrap = lambda t: t
    lines, n = [], 0
    for i, seg in enumerate(segments):
        grp = groups[i] if i < len(groups) else []
        if not grp or not str(seg).strip():
            continue
        start, end = grp[0]["start"], grp[-1]["end"]
        n += 1
        lines += [str(n), f"{_srt_ts(start)} --> {_srt_ts(end)}", _wrap(str(seg).strip()), ""]
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
    comp kinds: bignum repo compare terminal steps badges gittree cta stats quote tip feature
                lower-third callout.
       lower-third {"title":.., "sub":..}  — source/handle attribution card (accent bar).
       callout     {"text":..}            — punchy accent pill for one high-impact line.
    Keep a comp at scene 0 or >=2; cảnh 1 nên là text bắc cầu.
    """
    segments = [s.get("seg", "") for s in scenes_spec]
    scenes = []
    for s in scenes_spec:
        sc = {"kicker": s.get("kicker", ""), "h1": s.get("h1", ""),
              "h2": s.get("h2", ""), "acc": s.get("acc", "blue"), "hero": s.get("hero", False)}
        if s.get("comp"):
            sc["comp"] = s["comp"]
        for _k in ("lottie", "fx", "block"):     # carry director/writer resource hints if given
            if s.get(_k):
                sc[_k] = s[_k]
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
        kind = cs.get("comp_override") or ts.get("component")   # content may override (e.g. inject a 2nd shot)
        comp = (kind, cs.get("data", {})) if kind else None
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

