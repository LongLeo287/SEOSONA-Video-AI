# -*- coding: utf-8 -*-
"""Talking-head step 2 — edit footage into a finished video.

    python scripts/talking_head_edit.py --spec cards.json --video <mp4> \
        --words words_fixed.json --out final.mp4 --caption-chunk 6

Burns karaoke captions + cards (term/bullet/stat) onto the REAL footage (keeps the
footage's own resolution → supports BOTH 9:16 and 16:9), then mixes the original voice
with ducked BGM + SFX and loudness-normalises. Uses the real voice from the footage
(no AI TTS). See `.agents/skills/talking-head-video-editor/SKILL.md`.

Captions/cards are rendered as an ASS subtitle (native karaoke `\\k` + positioning),
burned by ffmpeg `ass=` — robust and dependency-light (no alpha render).
"""
import os, sys, json, argparse, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, os.path.join(ROOT, "4_BRAIN")):
    if p not in sys.path:
        sys.path.insert(0, p)
import native_composer as nc  # _ffmpeg_bin/_ffprobe_bin/_bgm/_sfx + SFX library

# ASS colours are &HBBGGRR (BGR). Brand accents (light-mode palette).
ACCENT = {"cyan": "&H00EED322", "violet": "&H00F65C8B", "gold": "&H004FD5FF",
          "green": "&H004AA316", "blue": "&H00DA5B2A", "coral": "&H004D72E2"}
WHITE = "&H00FFFFFF"
DIM = "&H009A9A9A"      # unsung karaoke colour
NAVY = "&H004A2216"     # caption pill / card bg (BGR of #16224A-ish)


def _probe(video):
    pb = nc._ffprobe_bin()
    def q(stream, key):
        r = subprocess.run([pb, "-v", "error", "-select_streams", stream, "-show_entries",
                            f"stream={key}", "-of", "default=nw=1:nk=1", video],
                           capture_output=True, text=True)
        return r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
    w = int(q("v:0", "width") or 1080)
    h = int(q("v:0", "height") or 1920)
    dr = subprocess.run([pb, "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=nw=1:nk=1", video], capture_output=True, text=True)
    dur = float(dr.stdout.strip() or 0) or 60.0
    return w, h, dur


def _ts(sec):
    sec = max(0.0, float(sec)); h = int(sec // 3600); m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def _esc(s):
    return str(s).replace("{", "(").replace("}", ")").replace("\n", " ").strip()


def _chunks(words, n):
    return [words[i:i + n] for i in range(0, len(words), max(1, n))]


def build_ass(words, spec, W, H, chunk):
    cap_bottom = int(spec.get("caption_bottom", 380))
    keywords = set(k.lower() for k in spec.get("keywords", []))
    acc1 = ACCENT.get((spec.get("accent") or "cyan"), ACCENT["cyan"])
    cap_size = int(H * 0.030)        # ~58px on a 1920-tall frame
    card_size = int(H * 0.026)

    head = [
        "[Script Info]", "ScriptType: v4.00+", "WrapStyle: 2",
        f"PlayResX: {W}", f"PlayResY: {H}", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # Karaoke caption: Primary=white(sung), Secondary=dim(unsung), pill bg via BorderStyle 3
        f"Style: Cap,Be Vietnam Pro,{cap_size},{WHITE},{DIM},{NAVY},{NAVY},-1,0,0,0,100,100,0,0,3,4,0,2,80,80,{cap_bottom},1",
        f"Style: Card,Be Vietnam Pro,{card_size},{WHITE},{WHITE},{NAVY},{NAVY},-1,0,0,0,100,100,0,0,3,3,2,7,0,0,0,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    events = []

    # --- karaoke captions ---
    for grp in _chunks(words, chunk):
        grp = [w for w in grp if str(w.get("word", "")).strip()]
        if not grp:
            continue
        start, end = float(grp[0]["start"]), float(grp[-1]["end"])
        parts = []
        for w in grp:
            kcs = max(1, int(round((float(w["end"]) - float(w["start"])) * 100)))
            tok = _esc(w["word"])
            col = acc1 if tok.lower().strip(".,!?:") in keywords else ""
            seg = (f"{{\\c{col}}}" if col else "") + f"{{\\k{kcs}}}{tok} "
            parts.append(seg)
        events.append(f"Dialogue: 0,{_ts(start)},{_ts(end + 0.4)},Cap,,0,0,0,,{''.join(parts).strip()}")

    # --- cards (term / bullet / stat) ---
    for c in spec.get("cards", []):
        t = float(c.get("t", 0)); dur = float(c.get("dur", 6)); end = t + dur
        acc = ACCENT.get(c.get("accent", "cyan"), acc1)
        x = int(c.get("left", int(W * 0.55))); y = int(c.get("top", int(H * 0.12)))
        ctype = c.get("type", "term")
        if ctype == "stat":
            big = _esc(c.get("title", "")); lab = _esc(c.get("sub", ""))
            txt = f"{{\\pos({x},{y})\\an7\\fs{int(card_size*1.9)}\\c{acc}\\b1}}{big}{{\\fs{card_size}\\c{WHITE}}}\\N{lab}"
        elif ctype == "bullet":
            rows = c.get("rows") or ([c.get("sub")] if c.get("sub") else [])
            body = "\\N".join(f"{{\\c{acc}}}• {{\\c{WHITE}}}{_esc(r)}" for r in rows if r)
            ttl = f"{{\\c{acc}\\b1}}{_esc(c.get('title',''))}{{\\b0\\c{WHITE}}}\\N" if c.get("title") else ""
            txt = f"{{\\pos({x},{y})\\an7\\fs{card_size}}}{ttl}{body}"
        else:  # term
            ttl = _esc(c.get("title", "")); sub = _esc(c.get("sub", ""))
            txt = (f"{{\\pos({x},{y})\\an7\\fs{int(card_size*1.25)}\\c{acc}\\b1}}{ttl}"
                   f"{{\\fs{card_size}\\c{WHITE}\\b0}}" + (f"\\N{sub}" if sub else ""))
        events.append(f"Dialogue: 1,{_ts(t)},{_ts(end)},Card,,0,0,0,,{txt}")

    return "\n".join(head + events) + "\n"


def build_audio_filter(spec, n_sfx, music_path):
    """[0:a]=voice, [1:a]=bgm(looped), [2..]=sfx. BGM sidechain-ducks under the voice."""
    mvol = float(spec.get("music_vol", 0.10))
    filt = ["[0:a]aresample=48000,asplit=2[vmain][vkey]",
            f"[1:a]volume={mvol}[bg0]",
            "[bg0][vkey]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[bgduck]"]
    mixn = ["[vmain]", "[bgduck]"]
    for i, ev in enumerate(spec.get("sfx_events", [])):
        db = ev.get("db", -14)
        filt.append(f"[{i+2}:a]volume={db}dB,adelay={int(float(ev.get('t',0))*1000)}|{int(float(ev.get('t',0))*1000)}[s{i}]")
        mixn.append(f"[s{i}]")
    fc = ";".join(filt) + ";" + "".join(mixn) + \
        f"amix=inputs={len(mixn)}:normalize=0:duration=first[mx];" \
        f"[mx]alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[ao]"
    return fc


def _resolve_sfx(f):
    """Resolve an sfx path: absolute/existing → as-is; else map by keyword to the SFX lib."""
    if f and os.path.isabs(f) and os.path.exists(f):
        return f
    cand = os.path.join(ROOT, f) if f else ""
    if cand and os.path.exists(cand):
        return cand
    base = os.path.basename(str(f)).lower()
    table = {"whoosh": "transition", "swish": "transition", "pop": "ui_pop", "ding": "ui_notify",
             "success": "ui_success", "notify": "ui_notify", "coin": "ui_positive",
             "click": "ui_click", "swipe": "transition"}
    for key, sfxkey in table.items():
        if key in base:
            rel = nc.SFX.get(sfxkey, sfxkey)
            if isinstance(rel, list):       # e.g. "transition" → list of variants
                rel = rel[0]
            p = os.path.join(nc.SFX_DIR, rel)
            return p if os.path.exists(p) else None
    return None


def main():
    ap = argparse.ArgumentParser(description="Footage + words + cards → finished talking-head video")
    ap.add_argument("--spec", required=True, help="cards.json")
    ap.add_argument("--video", required=True, help="footage .mp4")
    ap.add_argument("--words", required=True, help="words_fixed.json (word-level transcript)")
    ap.add_argument("--out", required=True, help="output .mp4")
    ap.add_argument("--caption-chunk", type=int, default=6, dest="chunk")
    ap.add_argument("--composition", default="hf-demo")  # accepted for SKILL compatibility; unused
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    words = json.load(open(a.words, encoding="utf-8"))
    video = a.video if os.path.isabs(a.video) else os.path.abspath(a.video)
    out = a.out if os.path.isabs(a.out) else os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    W, H, dur = _probe(video)
    print(f"[edit] footage {W}x{H} {dur:.1f}s | {len(words)} words | {len(spec.get('cards',[]))} cards")

    ass_path = os.path.splitext(out)[0] + ".ass"
    open(ass_path, "w", encoding="utf-8").write(build_ass(words, spec, W, H, a.chunk))
    print(f"[edit] ASS captions/cards → {ass_path}")

    # resolve sfx + bgm
    sfx_events = []
    for ev in spec.get("sfx_events", []):
        p = _resolve_sfx(ev.get("file"))
        if p:
            sfx_events.append({**ev, "_path": p})
        else:
            print(f"[edit] skip sfx (not found): {ev.get('file')}")
    spec["sfx_events"] = sfx_events
    bgm = nc._bgm(spec.get("music", "tech"))

    inputs = ["-i", video, "-stream_loop", "-1", "-i", bgm]
    for ev in sfx_events:
        inputs += ["-i", ev["_path"]]

    # ass path must be escaped for the ffmpeg filter on Windows (drive colon + backslashes)
    ass_f = ass_path.replace("\\", "/").replace(":", "\\:")
    vf = f"ass='{ass_f}'"
    af = build_audio_filter(spec, len(sfx_events), bgm)

    cmd = [nc._ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", *inputs,
           "-filter_complex", f"[0:v]{vf}[vo];{af}",
           "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-preset", "medium",
           "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", out]
    print("[edit] rendering (ffmpeg burn + mix)…")
    subprocess.run(cmd, check=True)
    print(f"[edit] DONE: {out}")


if __name__ == "__main__":
    main()
