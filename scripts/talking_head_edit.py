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
import brand_kit as bk         # single source of truth for brand palette

# ASS colours are &HBBGGRR (BGR). Brand accents (light-mode palette).
ACCENT = {"cyan": "&H00EED322", "violet": "&H00F65C8B", "gold": "&H004FD5FF",
          "green": "&H004AA316", "blue": "&H00DA5B2A", "coral": "&H004D72E2"}
WHITE = "&H00FFFFFF"
DIM = "&H009A9A9A"           # unsung karaoke colour (neutral grey, not a brand colour)
NAVY = bk.ass_color(bk.NAVY)  # caption pill / card bg — derived from brand_kit.NAVY (#16224A)
# Completion-STATE colours (a SEPARATE axis from a card's role border — the two-axes rule the
# reference reels insist on: border = domain role, ✓/fill = progress state; never conflate them).
OKC = bk.ass_color(bk.GREEN)     # done ✓ + progress-bar fill
WARNC = bk.ass_color(bk.AMBER)   # in-progress ▸
GREYC = bk.ass_color(bk.GREY)    # todo badge + progress-bar track


def _role_ass(role):
    """Map a semantic ROLE (brand_kit.ROLES: emphasis/success/danger/caution/info/baseline) to an
    ASS colour, else None — lets a card set its border by MEANING instead of a raw accent name."""
    try:
        hx = bk.ROLES.get(role) if role else None
        return bk.ass_color(hx) if hx else None
    except Exception:
        return None


DANGER = bk.ass_color(bk.CORAL)  # ✕ negation badge (danger role)
_CIRCLED = "①②③④⑤⑥⑦⑧⑨"


def _circled(n):
    """A circled digit ①..⑨ for a numbered section marker (falls back to '(n)')."""
    try:
        n = int(n)
        return _CIRCLED[n - 1] if 1 <= n <= 9 else f"({n})"
    except Exception:
        return f"({n})"


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
    # ASS H:MM:SS.cc — round to whole CENTISECONDS first, then decompose. `{s:05.2f}` on `sec % 60` rounds
    # 59.9996 up to "60.00" → an invalid "0:00:60.00" (seconds must be 00-59, must carry). divmod on the
    # total centiseconds can't overflow → always a valid timestamp. (Same class as native_composer._srt_ts.)
    cs_total = int(round(max(0.0, float(sec)) * 100))
    h, cs_total = divmod(cs_total, 360_000)
    m, cs_total = divmod(cs_total, 6_000)
    s, cs = divmod(cs_total, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _esc(s):
    return str(s).replace("{", "(").replace("}", ")").replace("\n", " ").strip()


def _chunks(words, n):
    return [words[i:i + n] for i in range(0, len(words), max(1, n))]


def build_ass(words, spec, W, H, chunk):
    cap_bottom = int(spec.get("caption_bottom", 380))
    cap_align = int(spec.get("caption_align", 2))     # 2=bottom-centre (default); 8=top, 5=mid-float
    chunk = int(spec.get("caption_chunk", chunk))     # a spec can force ≤2-word captions (Seedance craft)
    keywords = set(k.lower() for k in spec.get("keywords", []))
    if spec.get("auto_emphasis", True):               # SKILL-AUTO zoom_plan scoring → auto-highlight
        try:                                          # punchy words (numbers/brands/pivots) in captions
            import os as _os, sys as _sys
            _sys.path.insert(0, _os.path.join(ROOT, "4_BRAIN"))
            import beat_timing as _bt
            for _z in _bt.zoom_plan(words):
                trg = str(_z.get("trigger", "")).lower().strip(".,!?:;")
                if trg:
                    keywords.add(trg)
        except Exception:
            pass
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
        f"Style: Cap,Be Vietnam Pro,{cap_size},{WHITE},{DIM},{NAVY},{NAVY},-1,0,0,0,100,100,0,0,3,4,0,{cap_align},80,80,{cap_bottom},1",
        f"Style: Card,Be Vietnam Pro,{card_size},{WHITE},{WHITE},{NAVY},{NAVY},-1,0,0,0,100,100,0,0,3,3,2,7,0,0,0,1",
        # Bar: BorderStyle 1 + Outline/Shadow 0 → a plain \p1-drawn rectangle (progress bar), no box.
        f"Style: Bar,Be Vietnam Pro,20,{WHITE},{WHITE},{WHITE},{WHITE},0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        # Big: layered background typography — a LARGE faint keyword plate behind the captions/cards
        # (the Seedance "bold cinematic typography, keyword becomes a large design element, foreground/
        # background layers" craft). No box (BorderStyle 1), thin outline, centre-anchored (an5).
        f"Style: Big,Be Vietnam Pro,{int(H*0.11)},{acc1},{acc1},{NAVY},{NAVY},-1,0,0,0,100,100,2,0,1,3,0,5,0,0,0,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    events = []

    # --- karaoke captions ---
    if spec.get("smart_chunk"):                       # natural-break grouping (caption_segment port)
        try:
            import caption_segment
            groups = caption_segment.segment_words(words)
        except Exception:
            groups = _chunks(words, chunk)
    else:
        groups = _chunks(words, chunk)
    # Caption-readability QC (advisory) — same reading-speed check the news path runs, so an unreadable
    # cue is observable on the talking-head/course path too. Non-blocking; never affects the burn.
    try:
        import caption_segment as _cseg
        _warn = _cseg.readability_warnings(groups)
        if _warn:
            print(f"[caption-readability] ⚠ {len(_warn)} cue(s) hard to read (first 3):")
            for _w in _warn[:3]:
                print(f"    · {_w}")
        else:
            print(f"[caption-readability] ✓ all {len(groups)} cues within reading-speed standards.")
    except Exception as _e:
        print(f"[caption-readability] skipped ({_e})")
    for grp in groups:
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

    # --- layered BIG-KEYWORD typography plate (Seedance craft, opt-in `bigword`) -----------------
    # When the speaker hits an emphasis word, a LARGE faint keyword rises in the upper-third BEHIND the
    # captions/cards → the "keyword becomes a big design element, foreground/background layers, depth"
    # look from the reference edit spec. Dependency-free (pure ASS): the plate is on Layer 0 and is
    # PREPENDED (drawn first → sits behind everything), lives in the upper zone away from the bottom
    # caption, and is translucent so the speaker reads as being in front of it.
    #   NOTE: TRUE silhouette-occlusion (text masked by the speaker's outline) needs a per-frame person
    #   matte (mediapipe/rembg) — not available in this env; that is a documented upgrade, not faked here.
    if spec.get("bigword") and keywords:
        big_y = int(H * float(spec.get("bigword_y", 0.30)))
        hold = float(spec.get("bigword_hold", 0.30))
        alpha = spec.get("bigword_alpha", "&H70&")     # ~56% transparent → a background plate, not a title
        big_ev, last_end, shown = [], -1.0, 0
        cap_max = int(spec.get("bigword_max", 14))     # don't paper the whole video with plates
        for w in words:
            tok = str(w.get("word", "")).strip()
            key = tok.lower().strip(".,!?:;\"'")
            if len(key) < 2 or key not in keywords:
                continue
            s, e = float(w["start"]), float(w["end"])
            if s - last_end < 0.6 or shown >= cap_max:  # space them out; cap the count
                continue
            last_end = e
            shown += 1
            big = _esc(tok).upper()
            # subtle cinematic grow on entry (\t scale) — reads as the word "arriving" behind the speaker
            big_ev.append(
                f"Dialogue: 0,{_ts(s)},{_ts(e + hold)},Big,,0,0,0,,"
                f"{{\\an5\\pos({W//2},{big_y})\\alpha{alpha}\\b1"
                f"\\fscx104\\fscy104\\t(0,200,\\fscx112\\fscy112)\\fad(120,160)}}{big}")
        events = big_ev + events                        # prepend → the plate renders BEHIND captions/cards
        print(f"[edit] bigword: {shown} layered keyword plate(s) behind the speaker")

    # --- cards (header / bullet / term / stat) — templates cloned from the reference reels ---
    # Each Dialogue gets its own rounded pill box (Card style BorderStyle 3), so stacked rows read
    # as separate chips and \3c recolours a chip to an accent.  Layout = Group-B talking-head:
    #   header pill (tag + headline) on top, icon bullet-chips revealed one per beat below it.
    def ev(layer, ta, tb, txt):
        events.append(f"Dialogue: {layer},{_ts(ta)},{_ts(tb)},Card,,0,0,0,,{txt}")

    for c in spec.get("cards", []):
        t = float(c.get("t", 0)); dur = float(c.get("dur", 6)); end = t + dur
        # a card's colour can come from a semantic ROLE (border = meaning) or a raw accent name
        acc = _role_ass(c.get("role")) or ACCENT.get(c.get("accent", "cyan"), acc1)
        x = int(c.get("left", int(W * 0.55))); y = int(c.get("top", int(H * 0.12)))
        ctype = c.get("type", "term")
        rowH = int(card_size * 2.0)

        if ctype == "stat":
            big = _esc(c.get("title", "")); lab = _esc(c.get("sub", ""))
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\fs{int(card_size*1.9)}\\c{acc}\\b1}}{big}"
                          f"{{\\fs{card_size}\\c{WHITE}}}\\N{lab}")

        elif ctype == "header":
            # accent tag pill, then a bold white headline chip below it
            tag = _esc(c.get("tag", c.get("title", "")))
            head_txt = _esc(c.get("title", "") if c.get("tag") else c.get("sub", ""))
            if c.get("tag") is None and c.get("sub"):
                tag, head_txt = _esc(c.get("title", "")), _esc(c.get("sub", ""))
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\3c{acc}\\c{WHITE}\\b1\\fs{int(card_size*0.82)}}} {tag} ")
            if head_txt:
                ev(1, t + 0.12, end, f"{{\\pos({x},{y+int(card_size*1.5)})\\an7\\c{WHITE}\\b1"
                                     f"\\fs{int(card_size*1.45)}}}{head_txt}")

        elif ctype == "bullet":
            rows = c.get("rows") or ([c.get("sub")] if c.get("sub") else [])
            rows = [r for r in rows if r]
            y0 = y
            if c.get("title"):                       # accent tag pill heading
                ev(1, t, end, f"{{\\pos({x},{y})\\an7\\3c{acc}\\c{WHITE}\\b1\\fs{int(card_size*0.82)}}} {_esc(c['title'])} ")
                y0 = y + int(card_size * 1.6)
            step = max(0.25, (dur - 0.4) / max(1, len(rows)))
            row_times = None                         # SKILL-AUTO sync_list_items: reveal each row WHEN spoken
            try:
                import os as _os, sys as _sys
                _sys.path.insert(0, _os.path.join(ROOT, "4_BRAIN"))
                import beat_timing as _bt
                _lb = {"kind": "list", "start_sec": t, "end_sec": end,
                       "items": [(r.get("text", "") if isinstance(r, dict) else str(r)) for r in rows]}
                _bt.sync_list_items([_lb], words)
                row_times = [float(it.get("appear_sec")) for it in _lb["items"]]
            except Exception:
                row_times = None
            for i, r in enumerate(rows):             # each row = its own chip, revealed in sequence
                ry = y0 + i * rowH
                rt = round(row_times[i], 2) if row_times and i < len(row_times) else round(t + i * step, 2)
                icon = _esc(r.get("icon", "▸")) if isinstance(r, dict) else "▸"
                kw = _esc(r.get("kw", "")) if isinstance(r, dict) else ""
                text = _esc(r.get("text", "")) if isinstance(r, dict) else _esc(r)
                kwpart = f"{{\\c{acc}\\b1}}{kw} {{\\b0\\c{WHITE}}}" if kw else ""
                ev(1, rt, end, f"{{\\pos({x},{ry})\\an7\\fs{card_size}}}{{\\c{acc}}}{icon} {{\\c{WHITE}}}{kwpart}{text}")

        elif ctype == "checklist":
            # Progressive checklist with per-row STATE + optional progress bar (ref: V9 CEO-agent
            # checklist — the primary card-state reference). TWO INDEPENDENT AXES:
            #   • border colour = domain ROLE  (c["role"] → brand_kit.ROLES)
            #   • ✓ / green fill = completion STATE (per row)
            # A row flips todo/doing → done at its `done_at` (seconds from the card's t); the progress
            # bar fills in lockstep (fraction = done / total). Static `state` is also supported.
            role_c = _role_ass(c.get("role")) or acc
            rows = [r for r in (c.get("rows") or []) if r]
            y0 = y
            if c.get("title"):                        # role-bordered header pill
                ev(1, t, end, f"{{\\pos({x},{y})\\an7\\3c{role_c}\\c{WHITE}\\b1\\fs{int(card_size*0.82)}}} {_esc(c['title'])} ")
                y0 = y + int(card_size * 1.6)
            n = len(rows)
            animated = any(isinstance(r, dict) and r.get("done_at") is not None for r in rows)
            stagger = max(0.2, (dur - 0.5) / max(1, n))

            def crow(a, b, state, ry, badge, text):   # one checklist row in a given state
                # badge = step number that turns into ✓ when done; colour carries the STATE
                # (grey todo / amber doing / green done), independent of the card's role border.
                if state == "done":
                    mark, mcol, tcol = "✓", OKC, OKC
                elif state == "affirm":               # "do this" — green ✓, neutral text
                    mark, mcol, tcol = "✓", OKC, WHITE
                elif state == "negate":               # "not this" — coral ✕ (danger role)
                    mark, mcol, tcol = "✕", DANGER, WHITE
                elif state == "doing":
                    mark, mcol, tcol = badge, WARNC, WHITE
                else:
                    mark, mcol, tcol = badge, GREYC, WHITE
                ev(1, a, b, f"{{\\pos({x},{ry})\\an7\\fs{card_size}}}{{\\c{mcol}\\b1}}{mark} "
                            f"{{\\b0\\c{tcol}}}{text}")

            done_static, flips, prev_flip = 0, [], t
            for i, r in enumerate(rows):
                ry = y0 + i * rowH
                d = r if isinstance(r, dict) else {}
                text = _esc(d.get("text", "") if isinstance(r, dict) else r)
                badge = _esc(d.get("kw", "")) or str(i + 1)   # explicit label else the row number
                done_at = d.get("done_at")
                if done_at is not None:               # animated flip: doing until done_at, then done
                    da = round(t + float(done_at), 2)
                    # reveal as "doing" when the PREVIOUS step completed (a real state machine),
                    # not on an independent stagger — so a row is never revealed after its own flip.
                    crow(min(prev_flip, da), da, "doing", ry, badge, text)
                    crow(da, end, "done", ry, badge, text)
                    flips.append(da); prev_flip = da
                elif animated:                        # animated card, but this row has no flip time
                    crow(prev_flip, end, "todo", ry, badge, text)
                else:                                  # static card: even stagger reveal, fixed state
                    st = d.get("state", "todo")
                    crow(round(t + i * stagger, 2), end, st, ry, badge, text)
                    if st == "done":
                        done_static += 1

            if c.get("progress"):                     # progress bar under the rows
                barW = int(c.get("bar_width", W * 0.34)); barH = max(6, int(card_size * 0.42))
                by = y0 + n * rowH + int(card_size * 0.5)

                def rect(layer, a, b, w, col):
                    events.append(f"Dialogue: {layer},{_ts(a)},{_ts(b)},Bar,,0,0,0,,"
                                  f"{{\\pos({x},{by})\\an7\\1c{col}\\p1}}m 0 0 l {int(w)} 0 {int(w)} {barH} 0 {barH}")
                rect(1, t, end, barW, GREYC)           # track (grey, whole duration)
                if flips:                               # animated → step the fill at each done_at
                    order = sorted(flips)
                    for k, da in enumerate(order):
                        nb = order[k + 1] if k + 1 < len(order) else end
                        rect(2, da, nb, barW * (k + 1) / n, OKC)
                elif done_static:                       # static → fill = done / total
                    rect(2, t, end, barW * done_static / n, OKC)

        elif ctype == "steps":                       # numbered how-to (TIP/TRICK segments)
            rows = [r for r in (c.get("rows") or []) if r]
            y0 = y
            if c.get("title"):
                ev(1, t, end, f"{{\\pos({x},{y})\\an7\\3c{acc}\\c{WHITE}\\b1\\fs{int(card_size*0.82)}}} {_esc(c['title'])} ")
                y0 = y + int(card_size * 1.6)
            step = max(0.25, (dur - 0.4) / max(1, len(rows)))
            for i, r in enumerate(rows):
                ry = y0 + i * rowH
                rt = round(t + i * step, 2)
                text = _esc(r.get("text", "")) if isinstance(r, dict) else _esc(r)
                kw = _esc(r.get("kw", "")) if isinstance(r, dict) else ""
                kwpart = f"{{\\c{acc}\\b1}}{kw} {{\\b0\\c{WHITE}}}" if kw else ""
                ev(1, rt, end, f"{{\\pos({x},{ry})\\an7\\fs{card_size}\\c{acc}\\b1}}{i+1}. "
                               f"{{\\b0\\c{WHITE}}}{kwpart}{text}")

        elif ctype == "quote":                       # a memorable takeaway (ĐÚC KẾT segments)
            txt = _esc(c.get("title", "") or c.get("sub", ""))
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\fs{int(card_size*1.3)}\\c{acc}\\b1}}“"
                          f"{{\\c{WHITE}}}{txt}{{\\c{acc}}}”")

        elif ctype == "badge":                        # persistent corner STEP badge (ref V3 "BƯỚC N")
            # a small role-bordered pill that dwells for a whole step; a ✓ prefix marks it complete.
            lbl = _esc(c.get("label", c.get("title", "")))
            mk = "✓ " if c.get("done") else ""
            mcol = OKC if c.get("done") else WHITE
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\3c{acc}\\c{mcol}\\b1\\fs{int(card_size*0.9)}}} {mk}{lbl} ")
            if c.get("sub"):                          # breadcrumb sub-line under the badge
                ev(1, t, end, f"{{\\pos({x},{y+int(card_size*1.5)})\\an7\\c{WHITE}\\fs{int(card_size*0.68)}}}{_esc(c['sub'])}")

        elif ctype == "section":                      # eyebrow chapter pill (ref V8 "● ① TƯ VẤN LUẬT")
            lbl = _esc(c.get("label", c.get("title", "")))
            num = c.get("num")
            npart = f"{_circled(num)} " if num else ""
            if num and c.get("splash"):               # big centred number splash on entry, then it docks
                ev(2, t, min(end, t + 1.0),
                   f"{{\\an5\\pos({W//2},{int(H*0.42)})\\c{acc}\\b1\\fs{int(card_size*4.6)}}}{_circled(num)}")
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\3c{acc}\\c{WHITE}\\b1\\fs{int(card_size*0.8)}}} "
                          f"{{\\c{acc}}}●{{\\c{WHITE}}} {npart}{lbl} ")

        elif ctype == "reason":                       # reasoning line "cause → effect" (ref V8)
            # NB: fields are `cause`/`effect`, NOT left/right — `left` is the card's x-position.
            cause = _esc(c.get("cause", c.get("title", "")))
            effect = _esc(c.get("effect", c.get("sub", "")))
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\fs{card_size}\\c{WHITE}}}{cause} "
                          f"{{\\c{acc}\\b1}}→ {effect}")

        else:  # term — tag-style title + sub
            ttl = _esc(c.get("title", "")); sub = _esc(c.get("sub", ""))
            ev(1, t, end, f"{{\\pos({x},{y})\\an7\\fs{int(card_size*1.25)}\\c{acc}\\b1}}{ttl}"
                          f"{{\\fs{card_size}\\c{WHITE}\\b0}}" + (f"\\N{sub}" if sub else ""))

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


def _resolve_broll(src):
    """Resolve a b-roll path: absolute/existing → as-is; else relative to repo root or cwd."""
    if not src:
        return None
    if os.path.isabs(src) and os.path.exists(src):
        return src
    for cand in (src, os.path.join(ROOT, src)):
        if os.path.exists(cand):
            return cand
    return None


def main():
    ap = argparse.ArgumentParser(description="Footage + words + cards → finished talking-head video")
    ap.add_argument("--spec", required=True, help="cards.json")
    ap.add_argument("--video", required=True, help="footage .mp4")
    ap.add_argument("--words", required=True, help="words_fixed.json (word-level transcript)")
    ap.add_argument("--out", required=True, help="output .mp4")
    ap.add_argument("--caption-chunk", type=int, default=6, dest="chunk")
    ap.add_argument("--composition", default="hf-demo")  # accepted for SKILL compatibility; unused
    ap.add_argument("--analyze", action="store_true",
                    help="report dead-air + duplicate takes (talking_head_analyze) before editing")
    ap.add_argument("--silence", type=float, default=1.0, help="silence threshold for --analyze")
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    words = json.load(open(a.words, encoding="utf-8"))
    try:                                              # SKILL-AUTO: deterministic brand-term correction
        sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
        import transcript_fix as _tfix
        for _w in words:
            if isinstance(_w, dict) and _w.get("word"):
                _w["word"] = _tfix.fix_brands(_w["word"])
    except Exception:
        pass
    video = a.video if os.path.isabs(a.video) else os.path.abspath(a.video)
    out = a.out if os.path.isabs(a.out) else os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    W, H, dur = _probe(video)
    print(f"[edit] footage {W}x{H} {dur:.1f}s | {len(words)} words | {len(spec.get('cards',[]))} cards")

    # Optional pre-edit analysis: surface dead-air + duplicate takes so the operator can trim them.
    # (Advisory report — actual region-removal + re-timing is a separate step, not done here.)
    if a.analyze:
        try:
            import talking_head_analyze as _thz
            rep = _thz.analyze(words, a.silence)
            print(f"[edit] ANALYZE: {len(rep['silences'])} silence(s) = {rep['dead_air_total_s']}s dead air "
                  f"· {len(rep['duplicate_takes'])} duplicate take(s):")
            for s in rep["silences"]:
                print(f"    · dead air {s['duration']}s @ {s['start']}–{s['end']}")
            for d in rep["duplicate_takes"]:
                print(f"    · dup take (sim {d['similarity']}) → consider cutting {d['take1']}, keep {d['take2']}")
        except Exception as _e:
            print(f"[edit] analyze skipped: {_e}")

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

    # SKILL-AUTO close_gaps: bridge sub-1.5s flicker micro-gaps + fix overlaps between b-roll beats BEFORE
    # the render reads their timing (lint_broll below only FLAGS these — this is the pass that FIXES them,
    # completing the 3-pass port alongside zoom_plan/sync_list_items). In-place, deterministic, best-effort.
    try:
        _brl0 = spec.get("broll")
        if _brl0 and len(_brl0) > 1:
            sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
            import beat_timing as _bt0
            _bt0.close_gaps(_brl0)
    except Exception as _e:
        print(f"[edit] b-roll close_gaps skipped ({_e})")
    # b-roll / layout composites overlaid in the content zone, timed to a beat — the reference-reel
    # patterns. Modes: full (fill), pip (framed corner), split (presenter-top / screen-rec-below),
    # inset (Mode-B: footage → brand gradient + speaker as a rounded-border inset card).
    broll = []
    for b in spec.get("broll", []):
        if b.get("mode") == "inset":                 # Mode-B reuses the base footage → no input file
            broll.append({**b, "_inset": True, "_path": None})
            continue
        p = _resolve_broll(b.get("src"))
        if p:
            broll.append({**b, "_path": p})
        else:
            print(f"[edit] skip b-roll (not found): {b.get('src')}")
    broll_base = 2 + len(sfx_events)                  # input index of the first external b-roll
    media = [b for b in broll if not b.get("_inset")]
    for j, b in enumerate(media):
        b["_idx"] = broll_base + j                    # only external media consumes an -i input
        if os.path.splitext(b["_path"])[1].lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            inputs += ["-loop", "1", "-i", b["_path"]]
        else:
            inputs += ["-i", b["_path"]]

    # rich visual ELEMENTS (icon-tiles, emojis, badges, sparkles, arrows…) rendered on-brand to a
    # TRANSPARENT png by element_maker and composited over the footage at each beat — the dense
    # element layer of the reference reels. spec: elements:[{type,..params.., t, dur, x, y, w?}].
    elements = []
    el_specs = list(spec.get("elements", []))
    # AUTO-PLACE elements from the narration (default when none were hand-authored) — the loop that
    # gives a plain talking-head the dense element layer with no authoring. Opt out: auto_elements:false.
    if spec.get("auto_elements", not el_specs):
        try:
            sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "element_maker"))
            import element_picker as _ep
            auto = _ep.pick_elements(words, W, H)
            el_specs += auto
            print(f"[edit] auto-placed {len(auto)} element(s) from narration")
        except Exception as _e:
            print(f"[edit] auto-elements skipped ({_e})")
    if el_specs:
        try:                                          # SPEECH-ANCHOR (SKILL-AUTO): time by spoken phrase
            sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "element_maker"))
            import element_picker as _ep2
            _na = sum(1 for e in el_specs if isinstance(e, dict) and (e.get("speech_anchor") or e.get("anchor")))
            if _na:
                _ep2.snap_to_speech(el_specs, words)
                print(f"[edit] speech-anchored {_na} element(s) to the transcript")
        except Exception as _e:
            print(f"[edit] speech-anchor skipped ({_e})")
        try:                                          # SPEC-LINT (SKILL-AUTO): catch blank/too-brief elements
            sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
            import spec_lint as _spec_lint
            _elw = _spec_lint.lint_elements(el_specs).get("warnings", [])
            _elb = [x for x in _elw if x.startswith("BLANK-RISK")]
            if _elb:
                print(f"[edit] ⚠ spec-lint {len(_elb)} element issue(s): " + " | ".join(_elb[:4]))
            _brl = spec.get("broll") or []            # b-roll track → ceiling + flicker (advisory; coverage/
            if _brl:                                   # hook don't apply to a talking head where broll is intermittent)
                _bw = [x for x in _spec_lint.lint_broll(_brl, None).get("warnings", [])
                       if x.startswith(("TOO-LONG", "FLICKER"))]
                if _bw:
                    print(f"[edit] ⚠ b-roll timing {len(_bw)} issue(s): " + " | ".join(_bw[:4]))
        except Exception:
            pass
        try:
            sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "element_maker"))
            import element_maker as _em
            eldir = os.path.join(os.path.dirname(out), "_elements")
            os.makedirs(eldir, exist_ok=True)
            skip = ("t", "dur", "x", "y", "w", "anim")
            rich = bool(spec.get("rich_motion"))      # global: all elements as animated clips
            el_base = broll_base + len(media)
            # PER-ELEMENT: lottie + count_up are inherently animated → ALWAYS clips; the rest are a
            # static PNG (cheap ffmpeg entrance motion) unless rich_motion asks for clips everywhere.
            for i, e in enumerate(el_specs):
                etype = e.get("type")
                body = {k: v for k, v in e.items() if k not in skip}
                use_clip = rich or etype in ("lottie", "count_up")
                if use_clip:
                    mov = os.path.join(eldir, f"el_{i:02d}.mov")
                    is_lottie = etype == "lottie"
                    if is_lottie:
                        clip = _em.render_lottie_clip(e.get("src") or e.get("icon"), mov,
                                                      w=int(e.get("w", 300)), h=int(e.get("h", 300)),
                                                      dur=float(e.get("dur", 3.4)))
                    else:
                        clip = _em.render_element_clip(body, mov, anim=e.get("anim", "pop"),
                                                       dur=float(e.get("dur", 3.4)))
                    if clip and os.path.exists(mov):
                        elements.append({**e, "_path": mov, "_eidx": el_base + len(elements),
                                         "_clip": True, "_lottie": is_lottie})
                        inputs += ["-itsoffset", f"{float(e.get('t', 0)):.2f}", "-i", mov]
                else:
                    png = os.path.join(eldir, f"el_{i:02d}.png")
                    if _em.render_element(body, png):
                        elements.append({**e, "_path": png, "_eidx": el_base + len(elements)})
                        inputs += ["-loop", "1", "-i", png]
            print(f"[edit] {len(elements)} element(s) rendered → overlay")
        except Exception as _ee:
            print(f"[edit] elements skipped ({_ee})")

    # video chain: footage → b-roll/layout overlays → ass (cards/captions render ON TOP)
    ass_f = ass_path.replace("\\", "/").replace(":", "\\:")
    vparts = []
    n_inset = sum(1 for b in broll if b.get("_inset"))
    if n_inset:                                       # pre-split the base so inset can reuse the speaker
        vparts.append(f"[0:v]split={n_inset+1}[vbase]" + "".join(f"[insrc{k}]" for k in range(n_inset)))
        cur = "vbase"
    else:
        cur = "0:v"
    ik = 0
    for i, b in enumerate(broll):
        t0 = float(b.get("t", 0)); t1 = t0 + float(b.get("dur", 5))
        en = f"enable='between(t,{t0:.2f},{t1:.2f})'"
        mode = b.get("mode", "full")
        if b.get("_inset"):                          # Mode-B: brand-gradient bg + speaker inset card
            insW = int(b.get("width", W * 0.66)); insH = int(b.get("height", H * 0.46))
            grad = b.get("bg", "0xEEF3FF")           # light brand tint (footage is REPLACED here)
            ix = int(b.get("left", (W - insW) // 2)); iy = int(b.get("top", int(H * 0.30)))
            vparts.append(f"color=c={grad}:s={W}x{H}:d={dur:.2f}[grad{i}]")
            # ROUNDED-corner alpha mask on the speaker inset (geq rounded-rect: alpha 0 in the 4
            # corner-outside regions) — a premium touch vs a hard rectangle. R scaled to the inset.
            _R = max(24, int(min(insW, insH) * 0.07))
            _geq = (f"format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*(1-gt("
                    f"lt(X,{_R})*lt(Y,{_R})*gt(hypot(X-{_R},Y-{_R}),{_R})"
                    f"+gt(X,W-{_R})*lt(Y,{_R})*gt(hypot(X-(W-{_R}),Y-{_R}),{_R})"
                    f"+lt(X,{_R})*gt(Y,H-{_R})*gt(hypot(X-{_R},Y-(H-{_R})),{_R})"
                    f"+gt(X,W-{_R})*gt(Y,H-{_R})*gt(hypot(X-(W-{_R}),Y-(H-{_R})),{_R}),0))'")
            vparts.append(f"[insrc{ik}]scale={insW}:{insH}:force_original_aspect_ratio=increase,"
                          f"crop={insW}:{insH},{_geq}[ins{i}]"); ik += 1
            vparts.append(f"[{cur}][grad{i}]overlay=0:0:{en}[gb{i}]")
            vparts.append(f"[gb{i}][ins{i}]overlay={ix}:{iy}:{en}[bo{i}]")
        elif mode == "split":                        # presenter stays top; screen-rec fills below
            ratio = float(b.get("split_ratio", 0.36)); sy = int(H * ratio); sh = H - sy
            vparts.append(f"[{b['_idx']}:v]scale={W}:{sh}:force_original_aspect_ratio=increase,"
                          f"crop={W}:{sh}[bz{i}]")
            vparts.append(f"[{cur}][bz{i}]overlay=0:{sy}:{en}[bo{i}]")
        elif mode == "pip":                          # framed corner picture-in-picture
            bw = int(b.get("width", W * 0.42))
            vparts.append(f"[{b['_idx']}:v]scale={bw}:-1,pad=iw+10:ih+10:5:5:color=0x2A5BDA[bz{i}]")
            x = int(b.get("left", W - bw - 50)); y = int(b.get("top", H * 0.10))
            vparts.append(f"[{cur}][bz{i}]overlay={x}:{y}:{en}[bo{i}]")
        else:                                        # full — fill the content zone (+ optional frame)
            bw = int(b.get("width", W * 0.92))
            if b.get("frame"):                       # framed device-mockup wrapper (blue border)
                vparts.append(f"[{b['_idx']}:v]scale={bw}:-1,pad=iw+12:ih+12:6:6:color=0x2A5BDA[bz{i}]")
            else:
                vparts.append(f"[{b['_idx']}:v]scale={bw}:-1[bz{i}]")
            x = int(b.get("left", (W - bw) // 2)); y = int(b.get("top", H * 0.16))
            vparts.append(f"[{cur}][bz{i}]overlay={x}:{y}:{en}[bo{i}]")
        cur = f"bo{i}"
    # element overlays (transparent PNGs): MOTION entrance (rise/drop/slide + fade), hold, fade out —
    # over footage, under captions. The entrance gives each element a "pop" energy like the reels.
    for i, e in enumerate(elements):
        t0 = float(e.get("t", 0)); t1 = t0 + float(e.get("dur", 3))
        x = int(e.get("x", 60)); y = int(e.get("y", int(H * 0.12)))
        if e.get("_clip"):                         # animated .mov — motion is BAKED in; just fade out
            # lottie clips are rendered at exact w×h (no motion headroom); element clips carry a CLIP_INSET
            ox, oy = (x, y) if e.get("_lottie") else (x - _em.CLIP_INSET, y - _em.CLIP_INSET)
            vparts.append(f"[{e['_eidx']}:v]format=rgba,"
                          f"fade=t=out:st={max(t0, t1-0.2):.2f}:d=0.18:alpha=1[el{i}]")
            vparts.append(f"[{cur}][el{i}]overlay={ox}:{oy}:"
                          f"enable='between(t,{t0:.2f},{t1:.2f})'[elo{i}]")
            cur = f"elo{i}"
            continue
        sc = f"scale={int(e['w'])}:-1," if e.get("w") else "scale=iw/2:-1,"   # 2× render → half = intended
        vparts.append(f"[{e['_eidx']}:v]{sc}format=yuva420p,"
                      f"fade=t=in:st={t0:.2f}:d=0.18:alpha=1,"
                      f"fade=t=out:st={max(t0, t1-0.15):.2f}:d=0.15:alpha=1[el{i}]")
        # entrance offset that decays to 0 over ~0.34s (slide toward the rest position)
        anim = e.get("anim", "rise"); E = 0.34
        p = f"max(0\\,1-(t-{t0:.2f})/{E})"      # 1 → 0 across the entrance window
        ox, oy = str(x), str(y)
        if anim in ("rise", "pop"):     oy = f"{y}+56*{p}"
        elif anim == "drop":            oy = f"{y}-56*{p}"
        elif anim == "slide-left":      ox = f"{x}+110*{p}"
        elif anim == "slide-right":     ox = f"{x}-110*{p}"
        vparts.append(f"[{cur}][el{i}]overlay=x='{ox}':y='{oy}':"
                      f"enable='between(t,{t0:.2f},{t1:.2f})'[elo{i}]")
        cur = f"elo{i}"
    vparts.append(f"[{cur}]ass='{ass_f}'[vo]")
    vf_complex = ";".join(vparts)
    af = build_audio_filter(spec, len(sfx_events), bgm)

    # HARD duration cap — the mix has INFINITE inputs (BGM `-stream_loop -1`, PNG b-roll `-loop 1`)
    # feeding `-filter_complex`. ffmpeg's `-shortest` is unreliable across a filtergraph fed by an
    # endless input (here `sidechaincompress` keeps the looped BGM as its MAIN stream, so `[ao]` never
    # EOFs), and the encode can run FOREVER — observed: a course mix hung 4 h, two orphan ffmpeg holding
    # ~1.7 GB each. `-t <footage duration>` bounds the OUTPUT regardless, guaranteeing termination.
    try:
        _dur = float(subprocess.run(
            [nc._ffprobe_bin(), "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", video], capture_output=True, text=True).stdout.strip())
    except Exception:
        _dur = 0.0
    cmd = [nc._ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error", *inputs,
           "-filter_complex", f"{vf_complex};{af}",
           "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264",
           "-preset", os.environ.get("SEOSONA_X264_PRESET", "veryfast"),
           "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"]
    if _dur > 0:
        cmd += ["-t", f"{_dur:.3f}"]        # the real guard against the infinite-input hang
    cmd += ["-shortest", out]
    print("[edit] rendering (ffmpeg burn + mix)…")
    # Backstop: even with -t, never let a wedged ffmpeg run unbounded (10× realtime + 5 min headroom).
    _timeout = max(600, _dur * 10) if _dur > 0 else 1800
    subprocess.run(cmd, check=True, timeout=_timeout)
    print(f"[edit] DONE: {out}")


if __name__ == "__main__":
    main()
