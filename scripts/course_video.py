# -*- coding: utf-8 -*-
"""SEOSONA Video — COURSE / knowledge video pipeline (repurpose real footage).

Different from news (which is generated): a course video REPURPOSES an existing lecture.
Flow (the user's spec):
  1. analyse the video → get its SRT (transcribe)            [talking_head_transcribe / ASR]
  2. from the SRT → build the content cut-plan               [course_planner]
  3. cut + splice the footage into one coherent lesson       [ffmpeg cut + concat, keeps aspect]
  4. finish it talking-head style (real voice + captions)    [talking_head_edit on real footage]

  python scripts/course_video.py --video lecture.mp4 [--srt lecture.srt] --out lesson.mp4
  python scripts/course_video.py --srt "D:\\SRT\\....srt" --plan-only   # just show the cut-plan

Free/local. Source footage is required for cut/splice; --srt + --plan-only works on an SRT alone.
"""
import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "4_BRAIN"))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _ffmpeg():
    try:
        import native_composer
        return native_composer._ffmpeg_bin()
    except Exception:
        return "ffmpeg"


def _words(media):
    """Extract audio (16k mono wav) then run the ASR router → word list (proven path)."""
    import importlib, tempfile
    wav = str(Path(tempfile.gettempdir()) / (Path(media).stem + "_course.wav"))
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", media,
                    "-ac", "1", "-ar", "16000", wav], capture_output=True)
    asr = importlib.import_module("2_SKILLS.srt_maker.asr_router")
    return asr.transcribe_words(wav, language="vi") or []


def transcribe(video, out_srt):
    """Step 1: video → SRT via the project ASR (PhoWhisper)."""
    words = _words(video)
    if not words:
        return None
    # write a simple SRT
    def ts(s):
        # round to whole ms FIRST, then decompose — `{sec:06.3f}` rounds 59.9996 up to "60.000", emitting
        # an invalid "00:00:60,000" (seconds must be 00-59, must carry). divmod on total ms can't overflow.
        ms_total = int(round(max(0.0, float(s)) * 1000))
        h, ms_total = divmod(ms_total, 3_600_000)
        m, ms_total = divmod(ms_total, 60_000)
        sec, ms = divmod(ms_total, 1000)
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
    lines = []
    for i, w in enumerate(words, 1):
        lines.append(f"{i}\n{ts(w['start'])} --> {ts(w['end'])}\n{w['word']}\n")
    Path(out_srt).write_text("\n".join(lines), encoding="utf-8")
    return out_srt


# 16:9 (or any) → 9:16 1080x1920: speaker full-width centered, blurred fill top/bottom
# (leaves an upper band for cards + a lower band for captions — the Group-B course layout).
_VF_916 = ("split=2[bg][fg];"
           "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2[bgb];"
           "[fg]scale=1080:-2[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1")


def splice(video, segments, out_path, max_height=0, aspect="keep"):
    """Step 3: cut each (start,end) from the source and concat → one video.
    aspect='9:16' → vertical 1080x1920 (blurred-pad); else keep aspect, max_height downscales."""
    work = Path(out_path).parent / "_course_segs"
    work.mkdir(parents=True, exist_ok=True)
    if aspect == "9:16":
        vf = ["-vf", _VF_916]
    elif max_height:
        vf = ["-vf", f"scale=-2:{max_height}"]
    else:
        vf = []
    parts = []
    for i, s in enumerate(segments):
        p = work / f"seg_{i:03d}.mp4"
        r = subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                            "-ss", f"{s['start']:.2f}", "-to", f"{s['end']:.2f}", "-i", video,
                            *vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                            "-c:a", "aac", "-avoid_negative_ts", "make_zero", str(p)],
                           capture_output=True)
        if r.returncode == 0 and p.exists():
            parts.append(p)
        else:
            # A silently dropped segment desyncs EVERY caption after it (the plan still counts it) and
            # leaves a hole in the lesson. A failed cut means bad timestamps / a corrupt source region —
            # surface it and abort, don't ship an incomplete/desynced course video.
            print(f"[course] splice: segment {i} [{s['start']:.2f}-{s['end']:.2f}] failed to cut — "
                  f"aborting (a dropped segment would desync captions).")
            return None, []
    if not parts:
        return None, []
    durs = [_duration(p) for p in parts]
    lst = work / "concat.txt"
    # absolute paths — concat resolves entries relative to the list file otherwise
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    r = subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
                        "-safe", "0", "-i", str(lst), "-c", "copy", str(out_path)], capture_output=True)
    return (out_path, durs) if (r.returncode == 0 and Path(out_path).exists()) else (None, [])


def _duration(path):
    import native_composer as nc
    r = subprocess.run([nc._ffprobe_bin(), "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


# brand terms to accent-highlight in captions
_KEYWORDS = ["SEO", "Google", "SEMrush", "Ahrefs", "Search", "Console", "Screaming", "Frog",
             "ChatGPT", "AI", "content", "website", "SEOSONA", "top", "traffic", "backlink"]


# talking-head Rule 4: SFX must be VARIED — rotate transition sounds at splice points
_SPLICE_SFX = ["whoosh", "swipe", "pop", "swish"]


def captions_from_plan(segments, seg_durs, asr_words=None):
    """Word-level karaoke captions from each segment's corrected `display` text, SYNCED to the
    REAL voice. If `asr_words` (the spliced video's actual ASR word timings, same timeline) is given,
    each display word is anchored to the real speech timing at its proportional position — so the
    karaoke follows the actual rhythm + pauses instead of a uniform guess. Falls back to even spacing
    only when ASR timings are unavailable. Also returns VARIED transition SFX at each splice point."""
    words, sfx = [], []
    t = 0.0
    for i, s in enumerate(segments):
        dur = seg_durs[i] if i < len(seg_durs) and seg_durs[i] > 0 else (s["end"] - s["start"])
        if i > 0:                                   # varied transition SFX at each splice point
            sfx.append({"t": round(t, 2), "file": _SPLICE_SFX[(i - 1) % len(_SPLICE_SFX)], "db": -12})
        disp = (s.get("display") or s.get("raw") or "").split()
        if disp:
            seg_asr = [w for w in (asr_words or [])
                       if t - 0.05 <= float(w.get("start", -1)) < t + dur + 0.05]
            n, m = len(disp), len(seg_asr)
            if m:                                   # SYNC to real voice timing (proportional anchor)
                for j, dw in enumerate(disp):
                    si = min(m - 1, int(j * m / n))
                    ei = max(si, min(m - 1, int((j + 1) * m / n - 1e-9)))
                    words.append({"word": dw, "start": round(float(seg_asr[si]["start"]), 2),
                                  "end": round(float(seg_asr[ei]["end"]), 2)})
            else:                                   # fallback: even spacing (no ASR timings)
                step = dur / n
                for j, dw in enumerate(disp):
                    words.append({"word": dw, "start": round(t + j * step, 2),
                                  "end": round(t + (j + 1) * step, 2)})
        t += dur
    return words, sfx


# caption styles (talking-head SKILL §2) → (caption-chunk, accent)
_STYLES = {"clean_tutorial": (7, "blue"), "authority_news": (6, "blue"),
           "karaoke_neon": (6, "coral"), "tiktok_bold": (4, "coral")}

# 5-act part → on-screen Vietnamese tag (top-band content header)
_PART_TAG = {"HOOK": "MỞ ĐẦU", "NỖI ĐAU": "VẤN ĐỀ", "TIP/TRICK": "MẸO ÁP DỤNG",
             "CASE STUDY": "VÍ DỤ THỰC TẾ", "ĐÚC KẾT": "CHỐT LẠI"}
_CARD_ACCENTS = ["cyan", "violet", "gold", "green"]


def _headline(display, n=6):
    """A short top-band headline from the (already corrected) caption text."""
    w = display.replace("…", "").split()
    h = " ".join(w[:n])
    return h + ("…" if len(w) > n else "")


def _first_num(text):
    """First number-ish token (with optional %) — lets a 'stat' card feature a number that lives in
    the caption/display when the splice prompt didn't fill the optional `value` field."""
    m = re.search(r"\d[\d.,]*\s*%?", str(text or ""))
    return m.group(0).strip() if m else ""


def topcards_from_plan(segments, seg_durs, out_h=1920):
    """3-zone talking-head (cloned from the reference reels): TOP band = a header pill (part tag +
    headline) + icon bullet-chips revealed in sequence; MIDDLE = speaker; BOTTOM = karaoke.
    Uses each segment's `topcard` {tag, headline, bullets:[{icon,kw,text}]} when present (authored
    by the splice prompt); else derives a header from the part + caption."""
    cards = []
    t = 0.0
    left = int(1080 * 0.055)
    top = int(out_h * 0.05)                           # header pill band (~96px)
    bul_top = int(out_h * 0.135)                      # bullet chips below the header
    for i, s in enumerate(segments):
        dur = seg_durs[i] if i < len(seg_durs) and seg_durs[i] > 0 else (s["end"] - s["start"])
        acc = _CARD_ACCENTS[i % len(_CARD_ACCENTS)]
        tc = s.get("topcard") or {}
        tag = tc.get("tag") or _PART_TAG.get(s.get("part", ""), "KIẾN THỨC SEO")
        headline = tc.get("headline") or _headline(s.get("display") or s.get("raw") or "")
        cards.append({"type": "header", "tag": tag, "title": headline, "accent": acc,
                      "left": left, "top": top, "t": round(t + 0.15, 2),
                      "dur": round(max(2.0, dur - 0.3), 2)})
        # SECONDARY card — typed by the segment's suggested card_type (course_planner.suggest_card) so
        # the full card library is used: a number → stat, a how-to → steps, else the icon bullet-chips.
        # b-roll fills the content zone → skip the secondary card to avoid clutter.
        bullets = tc.get("bullets")
        ctype = s.get("card_type")
        if not s.get("broll"):
            base = {"accent": acc, "left": left, "top": bul_top,
                    "t": round(t + 0.6, 2), "dur": round(max(2.0, dur - 0.6), 2)}
            # stat number: prefer the explicit `value`, else pull the first number from the caption so a
            # "stat" segment isn't silently downgraded to header-only when the prompt omitted `value`.
            statnum = str(s.get("value", "")).strip() or _first_num(s.get("display") or s.get("raw") or "")
            if ctype == "stat" and statnum:
                cards.append({"type": "stat", "title": statnum, "sub": headline, **base})
            elif ctype == "steps" and bullets:
                cards.append({"type": "steps", "rows": bullets, **base})
            elif ctype == "quote":                    # ĐÚC KẾT takeaway → a quote card (was header-only)
                cards.append({"type": "quote",
                              "title": _headline(s.get("display") or s.get("raw") or headline, 12), **base})
            elif ctype == "term" and not bullets:     # NỖI ĐAU term → a term card (was header-only)
                cards.append({"type": "term", "title": tag,
                              "sub": _headline(s.get("display") or s.get("raw") or "", 9), **base})
            elif bullets:                             # icon bullet-chips (sequential) — term-with-bullets too
                cards.append({"type": "bullet", "rows": bullets, **base})
        t += dur
    return cards


def _resolve_block(name):
    """Render a HyperFrames registry block (e.g. 'code-snippet-dark-modern', 'data-chart') to a clip
    via the hf_blocks bridge → returns the clip path for use as b-roll. None on failure. Barred blocks
    (gallery-chrome demos like cinematic-zoom — see block_picker._KNOWN_BAD) are skipped so a plan that
    names one never leaks showcase chrome ('Cinematic Zoom / Prompt / SCENE A') into the video."""
    try:
        import tempfile
        from importlib import import_module
        try:
            if name in import_module("block_picker")._KNOWN_BAD:
                print(f"[course] block '{name}' barred (gallery-chrome/render-fail) — skipped")
                return None
        except Exception:
            pass
        hb = import_module("hf_blocks")
        out = os.path.join(tempfile.gettempdir(), f"hfblock_{name}.mp4")
        return hb.render_block(name, out)
    except Exception as e:
        print(f"[course] block '{name}' render failed: {e}")
        return None


def broll_from_plan(segments, seg_durs, out_h=1920):
    """Per-segment b-roll overlaid in the content zone, timed to the segment. Source is either a
    `src` (screenshot/screen-rec) OR a `block` (a HyperFrames registry block rendered on the fly —
    code-snippet-*, data-chart, liquid-glass-*, …; gallery-chrome demos are barred in _resolve_block).
    full = covers the speaker band; pip = corner."""
    items = []
    t = 0.0
    for i, s in enumerate(segments):
        dur = seg_durs[i] if i < len(seg_durs) and seg_durs[i] > 0 else (s["end"] - s["start"])
        b = s.get("broll")
        src = b.get("src") if b else None
        if b and not src and b.get("block"):
            src = _resolve_block(b["block"])             # render a registry block → clip
        if b and src:
            mode = b.get("mode", "full")
            it = {"src": src, "mode": mode,
                  "t": round(t + 0.4, 2), "dur": round(max(2.0, dur - 0.8), 2)}
            if mode == "full":
                it["top"] = int(out_h * 0.30)        # over the speaker band
            items.append(it)
        t += dur
    return items


def _safe_filename(title, hashtags):
    """talking-head Rule 7: filename = Vietnamese hook (diacritics) + hashtags, no forbidden chars."""
    import re
    base = f"{title} {hashtags}".strip()
    base = re.sub(r'[<>:"/\\|?*]', "", base)        # Windows-forbidden
    return re.sub(r"\s+", " ", base)[:150].strip()


def _caption_bottom(height):
    """Lower-third safe zone: SKILL says 380 for 9:16 (1920 tall) → scale to this height."""
    return max(60, round(height * 380 / 1920))


def finalize(out_path, spliced, plan, spec_d, style, brand, hashtags):
    """talking-head/operator rules: emit thumbnail + production_manifest + rule-7 filename + verify."""
    import shutil
    outp = Path(out_path)
    proj = outp.parent
    # rule-7 filename (copy alongside the working out)
    nice = _safe_filename(plan["title"], hashtags) + ".mp4"
    nice_path = proj / nice
    try:
        shutil.copy(out_path, nice_path)
    except Exception:
        nice_path = outp

    # thumbnail → <project>/Thumbnail/
    thumb_dir = proj / "Thumbnail"; thumb_dir.mkdir(exist_ok=True)
    thumb = thumb_dir / (outp.stem + "_thumb.png")
    try:
        from importlib import import_module
        tm = import_module("2_SKILLS.thumbnail_maker.thumbnail_maker")
        # a real frame as the portrait background
        frame = proj / "_thumb_frame.png"
        subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-ss", "2",
                        "-i", spliced, "-frames:v", "1", str(frame)], capture_output=True)
        tm.make_thumbnail(
            content=(plan["segments"][0].get("display", "")[:60] if plan["segments"] else plan["title"]),
            output_path=str(thumb), aspect_ratio="9:16", brand=brand,
            top_label="KIẾN THỨC SEO", main_title=plan["title"], cta="THEO DÕI SEOSONA",
            portrait_path=str(frame) if frame.exists() else None)
    except Exception as e:
        print(f"[course]   thumbnail skipped: {e}"); thumb = None

    # verify (YAVG brightness + duration)
    dur = _duration(out_path)
    yavg = _yavg(out_path)
    ok = dur >= 30 and (yavg is None or yavg > 12)
    print(f"[course]   verify: {dur:.0f}s | YAVG={yavg} | {'PASS' if ok else 'CHECK'}")

    # production manifest
    manifest = {"engine": "course-repurpose (talking-head)", "title": plan["title"],
                "brand": brand, "caption_style": style, "voice": "real (from footage)",
                "bgm": spec_d.get("music"), "sfx": [e.get("file") for e in spec_d.get("sfx_events", [])],
                "segments": len(plan["segments"]), "duration_s": round(dur, 1),
                "cut_plan_source": plan.get("source"), "output": str(nice_path),
                "thumbnail": str(thumb) if thumb else None, "verify_ok": ok}
    (proj / "production_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[course]   finalized → {nice_path.name} | thumbnail + manifest written")
    return str(nice_path)


def _yavg(path):
    """Average luma of a mid frame (talking-head verify: YAVG > 12)."""
    r = subprocess.run([_ffmpeg(), "-hide_banner", "-ss", "5", "-i", path, "-vf",
                        "signalstats,metadata=print", "-frames:v", "1", "-f", "null", "-"],
                       capture_output=True, text=True)
    import re
    m = re.search(r"(?:signalstats\.)?YAVG[:=]([\d.]+)", r.stderr)
    return round(float(m.group(1)), 1) if m else None


def embedded_captions(spliced, plan, words, out_path, brand, matte_fps=15):
    """B — upgrade captions to the `embedded-captions` skill (rail + person-matting → captions
    behind the subject). dna='anchor' (rail-first, words must read — right for explainer/course).
    Injects our CORRECTED `words` as transcript.json so prepare's transcribe reuses them (keeps the
    display-spelling fixes). Matting is CPU-slow (~2fps) → source is re-timed to matte_fps first."""
    skill = ROOT / ".agents" / "skills" / "embedded-captions"
    proj = Path(out_path).with_suffix("")
    proj = proj.parent / (proj.name + "_embedded")
    proj.mkdir(parents=True, exist_ok=True)
    src = proj / "source.mp4"
    # lower fps to cut matte time (matte extracts at native rate)
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", spliced,
                    "-r", str(matte_fps), "-c:v", "libx264", "-c:a", "aac", str(src)], capture_output=True)

    # env: point the embedded-captions scripts at our npm-installed hyperframes (shim at
    # packages/cli/dist/cli.js) + repo node_modules for puppeteer.
    env = dict(os.environ, HYPERFRAMES_ROOT=str(ROOT))

    # prepare (matte ∥ transcribe ∥ envelope → safe-zones)
    print(f"[course]   embedded: prepare (matting @ {matte_fps}fps — slow) …")
    r = subprocess.run(["bash", str(skill / "scripts" / "prepare.sh"), str(proj)],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print("[course]   prepare failed:", r.stderr[-400:]); return False

    # AFTER prepare: whisperx overwrote transcript.json with raw ASR. Overwrite it with our
    # CORRECTED words — make-theme requires `lines` to match transcript VERBATIM in order, so
    # both the transcript and the rail lines come from the same corrected tokens.
    toks = [w["word"] for w in words]
    tj = {"text": " ".join(toks),
          "words": [{"text": w["word"], "start": w["start"], "end": w["end"]} for w in words]}
    (proj / "transcript.json").write_text(json.dumps(tj, ensure_ascii=False), encoding="utf-8")
    # anchor = clean lower-third rail (the explainer/course default); heroless = no embed climax.
    # width/height/fps from safe-zones so the render keeps 9:16 (make-theme defaults to 16:9 otherwise).
    lines = [toks[i:i + 4] for i in range(0, len(toks), 4)]
    theme = {"dna": "anchor", "lines": lines}
    try:
        sz = json.loads((proj / "safe-zones.json").read_text(encoding="utf-8"))
        theme.update({"width": sz.get("width", 1080), "height": sz.get("height", 1920),
                      "fps": sz.get("fps", matte_fps)})
    except Exception:
        theme.update({"width": 1080, "height": 1920, "fps": matte_fps})
    (proj / "theme.json").write_text(json.dumps(theme, ensure_ascii=False), encoding="utf-8")

    print("[course]   embedded: render-theme …")
    r = subprocess.run(["bash", str(skill / "scripts" / "render-theme.sh"), str(proj)],
                       capture_output=True, text=True, env=env)
    final = proj / "final_fx.mp4"
    if not final.exists():
        final = proj / "final.mp4"
    if final.exists():
        import shutil
        shutil.copy(final, out_path)
        print(f"[course]   embedded DONE → {final}")
        return True
    print("[course]   render-theme failed:", r.stderr[-400:]); return False


def main():
    ap = argparse.ArgumentParser(description="SEOSONA course-video repurpose pipeline")
    ap.add_argument("--video", help="source lecture footage (.mp4)")
    ap.add_argument("--srt", help="existing SRT (else transcribe the video)")
    ap.add_argument("--out", default=str(ROOT / "8_WORKSPACE" / "clones" / "course_lesson.mp4"))
    ap.add_argument("--plan-only", action="store_true", help="print the cut-plan, don't cut")
    ap.add_argument("--emit-prompt", action="store_true",
                    help="write the filled COURSE_SPLICE prompt (run it on ChatGPT/Gemini)")
    ap.add_argument("--from-matrix", help="parse a pasted-back ChatGPT/Gemini answer (file) → cut-plan")
    ap.add_argument("--max-height", type=int, default=0, help="downscale output to this height (e.g. 1080)")
    ap.add_argument("--aspect", default="9:16", choices=["9:16", "keep"],
                    help="output aspect — course/knowledge videos are 9:16 (default)")
    ap.add_argument("--style", default="clean_tutorial", choices=list(_STYLES),
                    help="caption style (talking-head SKILL §2)")
    ap.add_argument("--captions", default="talkinghead", choices=["talkinghead", "embedded"],
                    help="caption engine: talkinghead (ASS karaoke) or embedded (rail+matting)")
    ap.add_argument("--brand", default="seosona")
    ap.add_argument("--hashtags", default="#SEO #SEOSONA #kienthucSEO")
    a = ap.parse_args()
    import course_planner

    # 1) SRT
    srt = a.srt
    if not srt:
        if not a.video:
            print("need --video or --srt"); sys.exit(1)
        srt = str(Path(a.out).with_suffix(".source.srt"))
        print("[course] step 1: transcribe →", srt)
        if not transcribe(a.video, srt):
            print("[course] transcription failed"); sys.exit(1)

    # 1b) manual bridge — emit the prompt to run on ChatGPT/Gemini
    if a.emit_prompt:
        pf = str(Path(srt).with_suffix(".splice_prompt.txt"))
        Path(pf).write_text(course_planner.build_prompt(srt), encoding="utf-8")
        print(f"[course] prompt → {pf}\n  Run it on ChatGPT/Gemini, save the answer, then:")
        print(f"  python scripts/course_video.py --video <mp4> --srt \"{srt}\" --from-matrix <answer.txt> --out <out.mp4>")
        return

    # 2) cut-plan (matrix from ChatGPT/Gemini > LLM auto > deterministic)
    print("[course] step 2: cut-plan from SRT")
    mt = open(a.from_matrix, encoding="utf-8", errors="replace").read() if a.from_matrix else None
    plan = course_planner.plan_course(srt, matrix_text=mt)
    total = sum(s["end"] - s["start"] for s in plan["segments"])
    print(f"[course]   title='{plan['title']}' | {len(plan['segments'])} segments | {total:.0f}s | source={plan['source']}")
    try:                                              # advisory pre-render lint (spec_lint)
        import spec_lint
        spec_lint.report(spec_lint.lint_course(plan), "course-lint")
    except Exception:
        pass
    if a.plan_only or not a.video:
        print(json.dumps(plan["segments"][:8], ensure_ascii=False, indent=2))
        if not a.video:
            print("[course] (no --video → stopped after planning; provide footage to cut/splice)")
        return

    # 3) splice
    print("[course] step 3: cut + splice footage")
    spliced = str(Path(a.out).with_name("_spliced.mp4"))
    spliced, seg_durs = splice(a.video, plan["segments"], spliced, max_height=a.max_height, aspect=a.aspect)
    if not spliced:
        print("[course] splice failed"); sys.exit(1)
    out_h = 1920 if a.aspect == "9:16" else (a.max_height or 1080)

    # 4) captions finish — embedded (rail+matting) OR talkinghead (ASS karaoke)
    has_display = any(s.get("display") for s in plan["segments"])
    if has_display:
        # SYNC: re-transcribe the spliced audio for REAL word timings, then anchor the corrected
        # `display` captions to them (karaoke matches the actual voice — not an even guess).
        print("[course]   aligning captions to real voice (ASR word timings)…")
        asr_words = _words(spliced)
        words, sfx = captions_from_plan(plan["segments"], seg_durs, asr_words)
    else:
        words, sfx = _words(spliced), []

    if a.captions == "embedded":
        print("[course] step 4: embedded-captions (rail + matting)")
        ok = embedded_captions(spliced, plan, words, a.out, a.brand)
        if not ok:
            print("[course] embedded-captions failed"); sys.exit(1)
    else:
        print(f"[course] step 4: talking-head captions + SFX (style={a.style})")
        h = _duration  # noqa
        chunk, accent = _STYLES[a.style]
        # 3-zone layout (top content cards) when vertical + we have a structured plan
        vertical = has_display and a.aspect == "9:16"
        cards = topcards_from_plan(plan["segments"], seg_durs, out_h) if vertical else []
        broll = broll_from_plan(plan["segments"], seg_durs, out_h) if vertical else []
        spec_d = {"title": plan["title"], "cards": cards, "broll": broll, "keywords": _KEYWORDS,
                  "accent": accent, "music": "insight", "music_vol": 0.08, "sfx_events": sfx,
                  "caption_bottom": _caption_bottom(out_h), "smart_chunk": True}
        if has_display:
            print(f"[course]   captions {len(words)}w | {len(cards)} top-cards | {len(broll)} b-roll | {len(sfx)} varied SFX | lower-third {spec_d['caption_bottom']}")
        words_json = str(Path(a.out).with_suffix(".words.json"))
        Path(words_json).write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
        spec = str(Path(a.out).with_suffix(".spec.json"))
        Path(spec).write_text(json.dumps(spec_d, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "talking_head_edit.py"),
                            "--spec", spec, "--video", spliced, "--words", words_json,
                            "--out", a.out, "--caption-chunk", str(chunk)], cwd=str(ROOT))
        if r.returncode != 0:
            print("[course] talking_head_edit failed"); sys.exit(1)
        # finalize only applies to the ASS path (embedded has its own deliverable)
        spec_d["style"] = a.style
        tag = a.hashtags + (" (9x16)" if a.aspect == "9:16" else "")
        finalize(a.out, spliced, plan, spec_d, a.style, a.brand, tag)
    print(f"[course] DONE → {a.out}")


if __name__ == "__main__":
    main()
