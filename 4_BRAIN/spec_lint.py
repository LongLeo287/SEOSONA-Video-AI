# -*- coding: utf-8 -*-
"""Pre-render edit-spec lint (ideas from feicaiclub/video-spec-builder, MIT).

Checkable discipline rules on a video's plan BEFORE rendering — catches retention/readability
problems cheaply (no render). Advisory by default (returns warnings), like content_moderation.
Two entry points: `lint_course(plan)` for the talking-head cut-plan, `lint_scenes(scenes)` for the
news/native_composer scene list. Wire as a gate before render; it never blocks unless strict.
"""
import re

MAX_HEADLINE_WORDS = 8        # text density on one screen
MAX_BULLET_WORDS = 6
MAX_NUMBERS_PER_SCREEN = 3
MIN_SEG_SECONDS = 1.5         # shorter = unreadable
MIN_TOTAL = 15
MAX_TOTAL = 95
HOOK_BY = 3.0                 # the hook must land in the first 3s

# Per-component REQUIRED-FIELD contract (from SKILL AUTO lint_plan.py). Each kind lists "any-of"
# groups; a group is satisfied if ANY of its fields is non-empty. A component missing a group would
# render BLANK — catch it before render, not on screen. (Field names verified against native_composer.)
_REQUIRED = {
    "bignum":    [("big", "value", "num")],
    "compare":   [("left",), ("right",)],
    "bars":      [("items",)], "checklist": [("items", "rows")], "stats": [("items", "tiles")],
    "steps":     [("items", "rows")], "icongrid": [("items",)], "chiprow": [("items",)],
    "feature":   [("items",)], "badges": [("items",)], "timeline": [("items",)],
    "hub":       [("nodes", "items", "left")],
    "photocard": [("img", "title")], "quote": [("text", "title")], "tip": [("text", "title")],
    "alert":     [("text", "items", "title")], "callout": [("text", "items")],
    "terminal":  [("lines", "items", "cmd")], "repo": [("name", "title")], "mockup": [("title", "img")],
    "stat_grid": [("stats", "items")], "ratio_dots": [("total",)], "layer_stack": [("layers",)],
    "ticker_feed": [("items",)], "org_diagram": [("nodes",)],
    # data-viz family (added to native_composer/component_picker but was missing here) — a chart with no
    # numbers renders EMPTY. component_picker._validate rejects these at assignment, but this is the
    # defense-in-depth floor for any other path (template / LLM-direct) that sets the comp.
    "linechart": [("points", "values")], "donut": [("segments",)], "ring": [("pct", "value", "ratio")],
    "pie": [("segments",)], "chat": [("messages", "items")], "codecard": [("lines", "items")],
    "tabs": [("tabs",), ("items",)], "gauge": [("value",)],
    "metric_rows": [("rows", "items")], "pill_stack": [("items",)],
    "people": [("items",)], "strike_list": [("items",)],
    "notification": [("title",)], "social": [("text",)], "phone": [("title", "screen")],
    # rich frames now LLM-assignable (component_picker._ALLOWED) — give them the same blank-risk floor so a
    # template / LLM-direct set with empty data is caught here too, not just at _validate.
    "comparison_grid": [("cols",), ("rows",)], "split_reveal": [("left",), ("right",)],
    "annotated_screenshot": [("concept",), ("marks",)], "concept_build": [("nodes",)],
    "filetree": [("items",)],
}
# A reason must NAME what's said + what the visual adds — these empty non-reasons are rejected.
_VAGUE = {"", "trang trí", "cho đẹp", "đẹp", "đẹp hơn", "visual interest", "decoration", "filler",
          "cho vui", "chèn cho có", "minh hoạ", "b-roll", "background", "nền"}


_EMPTY = (None, "", [], {}, ())


def _present(d, group):
    # "present" = the key holds real data. Use an explicit emptiness check, NOT truthiness: a numeric 0
    # (bignum big=0 → "0 lỗi", gauge value=0 → 0%) is valid data that renders fine, so it must not be
    # mis-flagged BLANK-RISK. Empty string / list / dict still count as missing.
    return any(d.get(k) not in _EMPTY for k in group)


def _grown_kinds():
    """Self-grown frame_synth kinds (banked in the kho at RUNTIME). Kept OUT of the static _REQUIRED
    contracts on purpose: a grown frame has an arbitrary generated schema, so we can't list its fields
    here — it gets a generic floor instead (see _comp_blankrisk). Lazy + guarded like
    component_picker._allowed(), so spec_lint never hard-depends on the kho existing."""
    try:
        import frame_synth
        return set(frame_synth.kinds())
    except Exception:
        return set()


def _comp_blankrisk(kind, data):
    """List of missing required-field groups for a component (empty = fine)."""
    if not isinstance(data, dict):
        return []
    groups = _REQUIRED.get(kind)
    if groups is None:
        # A self-grown frame (frame_synth kho) is LLM-assignable but has no static field contract. Floor it
        # GENERICALLY: an assignment carrying NO real data at all would render blank. Scoped to grown kinds
        # so decorative code kinds (divider/spacer — not in _allowed(), legitimately data-less) aren't flagged.
        if kind in _grown_kinds() and not any(v not in _EMPTY for v in data.values()):
            return ["<any content>"]
        return []
    miss = []
    for group in groups:
        if not _present(data, group):
            miss.append("/".join(group))
    return miss


def _bad_reason(r):
    return str(r or "").strip().lower() in _VAGUE


# Ending discipline (SKILL AUTO non-negotiable): end on a LOOP or a hard CTA, never a soft trail-off.
_SOFT_CLOSERS = ("cảm ơn đã xem", "cảm ơn các bạn", "cảm ơn mọi người", "hẹn gặp lại", "hẹn gặp",
                 "tạm biệt", "thanks for watching", "chúc các bạn", "vậy là hết", "kết thúc rồi")
_CTA_CUES = ("theo dõi", "đăng ký", "subscribe", "bình luận", "comment", "lưu lại", "chia sẻ",
             "nhấn", "bấm", "để lại", "inbox", "nhắn tin", "truy cập", "ghé")


def _ending_warnings(end_text, has_loop):
    """SKILL-AUTO ending gate: the last line must be a LOOP-back or a hard CTA, not a soft closer."""
    w = []
    et = str(end_text or "").lower()
    if any(s in et for s in _SOFT_CLOSERS):
        w.append("SOFT-CLOSER: ending trails off (cảm ơn/hẹn gặp lại…) — close on a loop or a hard CTA")
    if not (has_loop or any(c in et for c in _CTA_CUES)):
        w.append("WEAK-CLOSE: ending has neither a CTA nor a hook loop-back")
    return w


READING_CPS = 10              # on-screen reading speed — VN reads slower than EN's 12 chars/sec
MAX_BEATS_PER_12S = 4         # density cap (SKILL-AUTO): more than this in a rolling 12s = frantic


def reading_dwell(text):
    """Ideal on-screen dwell for a text (SKILL-AUTO): reading time + a 1.5s settle, floored at 3.5s."""
    return round(max(3.5, len(str(text or "")) / READING_CPS + 1.5), 2)


def _density_warnings(items, label="element"):
    """Rolling-window density + back-to-back-same-kind (SKILL-AUTO) over timed items [{t,type}]."""
    w = []
    timed = sorted((e for e in items if isinstance(e, dict) and e.get("t") is not None),
                   key=lambda e: float(e.get("t", 0)))
    for k, e in enumerate(timed):
        t0 = float(e.get("t", 0))
        if sum(1 for x in timed if 0 <= float(x.get("t", 0)) - t0 < 12) > MAX_BEATS_PER_12S:
            w.append(f"density: >{MAX_BEATS_PER_12S} {label}s within 12s of {t0:.1f}s (frantic)")
            break
    for k in range(1, len(timed)):
        if (timed[k].get("type") == timed[k - 1].get("type")
                and abs(float(timed[k].get("t", 0)) - float(timed[k - 1].get("t", 0))) < 2.0):
            w.append(f"back-to-back same-kind '{timed[k].get('type')}' near {timed[k].get('t')}s")
            break
    return w


# ── Coverage / timing / safe-zone rules (SKILL AUTO knowledge/non_negotiables + editing_rules) ──
COVERAGE_MIN = 0.70          # #1 non-negotiable: a visual must be on screen ≥70% of runtime
HOOK_VISUAL_BY = 0.5         # the first visual must land in the very first frame (thumbnail moment)
BEAT_CEIL = 5.0              # past 5s a single static visual goes boring (retention death)
BEAT_WARN = 4.0             # warn approaching the ceiling
ICON_MAX_Y = 80             # overlays below 80% height collide with the platform's UI chrome
LIST_ITEM_DWELL = 1.5       # each list item must stay ≥1.5s (muted-viewer readability)

# Overlays on their OWN layer leave the speaker visible → allowed to overlap; never counted as gaps
# and exempt from the duration ceiling (they accumulate). Mirrors SKILL AUTO close_gaps.PARTIAL_KINDS.
PARTIAL_KINDS = {"icon_tile", "icon", "chip", "badge", "marker", "emoji", "lottie", "count_up",
                 "word_pop", "hook_title", "subscribe", "bar_overlay", "ratio_dots", "headline_card"}


def coverage_ratio(beats, total):
    """Fraction of `total` runtime with a full-frame visual on screen (partial overlays don't count
    as coverage — the speaker is still the frame). beats = [{start,end,kind}] or [{t,dur,type}]."""
    if not total or total <= 0:
        return 1.0
    covered = 0.0
    for b in beats or []:
        if not isinstance(b, dict):
            continue
        kind = b.get("kind") or b.get("type")
        if kind in PARTIAL_KINDS:
            continue
        st = b.get("start_sec", b.get("start", b.get("t")))
        en = b.get("end_sec", b.get("end"))
        if en is None and b.get("dur") is not None and st is not None:
            en = float(st) + float(b["dur"])
        if st is None or en is None:
            continue
        covered += max(0.0, float(en) - float(st))
    return min(1.0, covered / float(total))


def coverage_warnings(beats, total):
    """SKILL-AUTO retention gate: ≥70% visual coverage + a visual on the very first frame."""
    w = []
    if total and total > 0:
        cov = coverage_ratio(beats, total)
        if cov < COVERAGE_MIN:
            w.append(f"COVERAGE: visuals cover {cov*100:.0f}% of runtime < {COVERAGE_MIN*100:.0f}% "
                     f"(talking head on a bare frame too long — add b-roll/cards)")
    firsts = [float(b.get("start_sec", b.get("start", b.get("t", 9)))) for b in (beats or [])
              if isinstance(b, dict)]
    if firsts and min(firsts) > HOOK_VISUAL_BY:
        w.append(f"HOOK-LATE: first visual at {min(firsts):.1f}s > {HOOK_VISUAL_BY}s "
                 f"(the opening frame — the thumbnail moment — has no visual)")
    return w


def _duration_warnings(beats):
    """Beat-duration ceiling (SKILL-AUTO): a full-frame visual >5s reads as a boring static slide."""
    w = []
    for i, b in enumerate(beats or []):
        if not isinstance(b, dict):
            continue
        kind = b.get("kind") or b.get("type")
        if kind in PARTIAL_KINDS:
            continue
        st = b.get("start_sec", b.get("start", b.get("t")))
        en = b.get("end_sec", b.get("end"))
        if en is None and b.get("dur") is not None and st is not None:
            en = float(st) + float(b["dur"])
        if st is None or en is None:
            continue
        dur = float(en) - float(st)
        if dur > BEAT_CEIL:
            w.append(f"TOO-LONG: beat {i} '{kind}' {dur:.1f}s > {BEAT_CEIL}s (static slide — cut or split)")
    return w


def _safezone_warnings(elements):
    """Icon/overlay safe-zone (SKILL-AUTO non-negotiable): keep overlays above 80% height so they
    don't collide with the platform's caption/like/share UI."""
    w = []
    for i, e in enumerate(elements or []):
        if not isinstance(e, dict):
            continue
        y = e.get("y")
        if y is None:
            continue
        try:
            yv = float(y)
        except Exception:
            continue
        yv = yv * 100 if yv <= 1.0 else yv            # accept 0-1 or 0-100
        if yv > ICON_MAX_Y:
            w.append(f"SAFE-ZONE: element {i} at y={yv:.0f}% > {ICON_MAX_Y}% (collides with platform UI)")
    return w


def lint_broll(beats, total_dur=None):
    """Lint a talking-head b-roll/beat plan [{start_sec,end_sec,kind,...}] for the coverage + timing
    rules SKILL AUTO treats as non-negotiable. Advisory (warnings), consistent with the rest."""
    w = []
    w += coverage_warnings(beats, total_dur)
    w += _duration_warnings(beats)
    # sub-1.5s micro-gaps between full-frame beats read as flicker (close_gaps fixes; lint flags)
    full = sorted((b for b in (beats or []) if isinstance(b, dict)
                   and (b.get("kind") or b.get("type")) not in PARTIAL_KINDS),
                  key=lambda b: float(b.get("start_sec", b.get("start", 0))))
    for k in range(1, len(full)):
        prev_en = full[k - 1].get("end_sec", full[k - 1].get("end"))
        cur_st = full[k].get("start_sec", full[k].get("start"))
        if prev_en is not None and cur_st is not None:
            gap = float(cur_st) - float(prev_en)
            if 0 < gap < 1.5:
                w.append(f"FLICKER: {gap:.2f}s gap before beat {k} (run close_gaps — bridge or breathe)")
    return {"ok": not w, "warnings": w}


# ── PACING / DENSITY gate (2026-07, after a real video read as a slow slideshow — 5 scenes/62s) ──
PACE_AVG_MAX = 8.0        # a scene held longer than this on average = slideshow, not a reel
PACE_SCENE_MAX = 13.0     # any single scene static longer than this = dead hold (retention death)
PACE_PER_MIN_MIN = 6.0    # a punchy short changes visual ≥6×/min


def lint_pacing(durations, total=None):
    """Measure SCENE PACING from per-scene durations (seconds). Flags a slow/sparse video BEFORE it ships
    so the factory never repeats the 5-scenes/62s slideshow. Returns a list of warning strings + is used by
    quality_scorer for a pacing score. `durations` = [scene_seconds, ...]."""
    w = []
    ds = [float(x) for x in (durations or []) if x and float(x) > 0]
    if not ds:
        return w
    n = len(ds)
    tot = float(total) if total else sum(ds)
    avg = tot / n
    per_min = n / (tot / 60.0) if tot else 0
    if avg > PACE_AVG_MAX:
        w.append(f"PACING-SLOW: {avg:.1f}s/scene avg (>{PACE_AVG_MAX:.0f}s) over {n} scenes — too few scenes; "
                 f"split into more/shorter scenes or add sub-beats (target ≤{PACE_AVG_MAX:.0f}s)")
    if per_min < PACE_PER_MIN_MIN:
        w.append(f"LOW-PACE: {per_min:.1f} scenes/min (<{PACE_PER_MIN_MIN:.0f}) — reads as a slideshow")
    dead = [i + 1 for i, d in enumerate(ds) if d > PACE_SCENE_MAX]
    if dead:
        w.append(f"DEAD-HOLD: scene(s) {dead} static >{PACE_SCENE_MAX:.0f}s — needs sub-beats (pop text/ý) mid-scene")
    return w


def pacing_score(durations, total=None):
    """0-100 pacing score for the quality gate: 100 = well-paced, drops as avg scene length / dead-holds grow."""
    ds = [float(x) for x in (durations or []) if x and float(x) > 0]
    if not ds:
        return 100
    avg = (float(total) if total else sum(ds)) / len(ds)
    s = 100
    if avg > PACE_AVG_MAX:
        s -= min(45, (avg - PACE_AVG_MAX) * 9)          # −9/sec over the 8s target
    s -= 12 * sum(1 for d in ds if d > PACE_SCENE_MAX)  # each dead-hold scene
    return max(0, round(s))


# TRUNCATION guard (2026-07, after a callout shipped "TobyFlow không tự" — cut mid-clause). On-screen
# text (callout/heading/quote) ending on a dangling connective reads as broken.
_DANGLING = {"và", "của", "không", "tự", "mà", "rồi", "để", "theo", "cho", "với", "là", "các", "những",
             "trên", "trong", "khi", "nếu", "hay", "hoặc", "bằng", "qua", "từ", "được", "bị", "sẽ", "đã"}


def truncation_warnings(texts):
    """Flag on-screen text that ends on a DANGLING word (a mid-clause truncation). `texts` = [(label, str)]."""
    w = []
    for label, t in texts or []:
        s = str(t or "").strip().rstrip(".…!?,;:")
        if not s:
            continue
        last = s.split()[-1].lower() if s.split() else ""
        if last in _DANGLING:
            w.append(f"TRUNCATED: {label} ends on dangling '{last}' → \"{s[-40:]}\" (cut mid-clause, reads broken)")
    return w


def _collision_warnings(items):
    """Rule CỨNG #4 (loha-video-maker): two overlays must not stack — same on-screen slot AND overlapping
    time reads as cards đè nhau. Conservative (same rounded x,y) to avoid false positives."""
    w = []
    timed = [e for e in (items or []) if isinstance(e, dict) and e.get("t") is not None
             and (e.get("x") is not None or e.get("left") is not None)]
    def _xy(e):                                                    # normalise to ~1080×1920 px space
        x = float(e.get("x", e.get("left", 0))); y = float(e.get("y", e.get("top", 0)))
        return (x * 1080 if x <= 1 else x, y * 1920 if y <= 1 else y)
    THRESH = 170                                                   # closer than this in BOTH axes = same slot
    for i in range(len(timed)):
        for j in range(i + 1, len(timed)):
            a, b = timed[i], timed[j]
            ta0 = float(a.get("t", 0)); ta1 = ta0 + float(a.get("dur", 3) or 3)
            tb0 = float(b.get("t", 0)); tb1 = tb0 + float(b.get("dur", 3) or 3)
            (xa, ya), (xb, yb) = _xy(a), _xy(b)
            if ta0 < tb1 and tb0 < ta1 and abs(xa - xb) < THRESH and abs(ya - yb) < THRESH:
                w.append(f"OVERLAP: overlays {i}/{j} collide in the same spot at ~{max(ta0,tb0):.1f}s "
                         f"(cards đè nhau — move one or offset its time)")
                return w                                            # one is enough signal
    return w


def variety_warnings(scenes):
    """Rule CỨNG #5 (loha-video-maker): a demo/explainer must show ≥2 DISTINCT visuals — one component
    (or none) repeated across a whole video reads as flat. Advisory."""
    w = []
    kinds = []
    for sc in scenes or []:
        comp = sc.get("comp") if isinstance(sc, dict) else None
        if isinstance(comp, (list, tuple)) and comp:
            kinds.append(comp[0])
        elif isinstance(comp, dict):
            kinds.append(comp.get("type") or comp.get("kind"))
    distinct = set(k for k in kinds if k)
    if len(scenes or []) >= 4 and len(distinct) < 2:
        w.append(f"LOW-VARIETY: {len(scenes)} scenes but {len(distinct)} distinct visual(s) "
                 f"(≥2-3 different components make a demo watchable)")
    return w


def _nums(s):
    return len(re.findall(r"\d[\d.,]*", str(s)))


def _words(s):
    return len(str(s).split())


def lint_course(plan):
    """Lint a course cut-plan {title, segments:[{part,start,end,display,topcard}]}."""
    w = []
    segs = plan.get("segments", []) if isinstance(plan, dict) else (plan or [])
    if not segs:
        return {"ok": False, "warnings": ["empty plan — no segments"]}

    total = sum((s.get("end", 0) - s.get("start", 0)) for s in segs)
    if total < MIN_TOTAL:
        w.append(f"total {total:.0f}s < {MIN_TOTAL}s (too short)")
    if total > MAX_TOTAL:
        w.append(f"total {total:.0f}s > {MAX_TOTAL}s (too long for a short)")

    parts = [s.get("part", "") for s in segs]
    if "HOOK" not in parts and (segs[0].get("part", "") or "").upper() != "HOOK":
        w.append("no HOOK segment — a strong hook should open the video (land in first 3s)")

    # loop-back (reels-af, Apache-2.0): the ending should echo a >=4-char keyword from the hook
    # → rewatch-loop closure. Advisory.
    hook_kw = {t for t in re.findall(r"\w+", (segs[0].get("display") or "").lower()) if len(t) >= 4}
    end_kw = {t for t in re.findall(r"\w+", (segs[-1].get("display") or "").lower()) if len(t) >= 4}
    if hook_kw and end_kw and not (hook_kw & end_kw):
        w.append("no loop-back: the ending doesn't echo any hook keyword (weak rewatch closure)")
    w += _ending_warnings(segs[-1].get("display") or segs[-1].get("raw"), bool(hook_kw & end_kw))
    # coverage/timing over any b-roll beats attached to the plan (SKILL-AUTO non-negotiables)
    beats = plan.get("beats") or plan.get("broll") if isinstance(plan, dict) else None
    if beats:
        w += lint_broll(beats, total).get("warnings", [])

    _CARD_OK = ("header", "bullet", "stat", "term", "quote", "steps")
    for i, s in enumerate(segs):
        ct = s.get("card_type")
        if ct and ct not in _CARD_OK:                  # typed card coupling — reject an invented type
            w.append(f"seg {i} card_type '{ct}' không hợp lệ (chỉ {'/'.join(_CARD_OK)})")
        dur = s.get("end", 0) - s.get("start", 0)
        if dur < MIN_SEG_SECONDS:
            w.append(f"seg {i} ({s.get('part','')}) only {dur:.1f}s < {MIN_SEG_SECONDS}s")
        if not (s.get("display") or s.get("raw")):
            w.append(f"seg {i} has no display/caption text")
        tc = s.get("topcard") or {}
        if tc.get("headline") and _words(tc["headline"]) > MAX_HEADLINE_WORDS:
            w.append(f"seg {i} headline {_words(tc['headline'])} words > {MAX_HEADLINE_WORDS}")
        if tc.get("headline") and _nums(tc["headline"]) > MAX_NUMBERS_PER_SCREEN:
            w.append(f"seg {i} headline has >{MAX_NUMBERS_PER_SCREEN} numbers")
        for b in (tc.get("bullets") or []):
            txt = b.get("text", "") if isinstance(b, dict) else str(b)
            if _words(txt) > MAX_BULLET_WORDS:
                w.append(f"seg {i} bullet '{txt[:24]}…' {_words(txt)} words > {MAX_BULLET_WORDS}")
    return {"ok": not w, "warnings": w, "total_s": round(total, 1)}


def lint_scenes(scenes, require_reason=False):
    """Lint a news/native_composer scene list [{heading|h1/h2, comp, reason?}]. `require_reason` turns
    on the SKILL-AUTO 'every visual must justify itself' gate (dormant until planners emit `reason`).
    BLANK-RISK warnings flag a component that would render empty (missing required data)."""
    w = []
    if not scenes:
        return {"ok": False, "warnings": ["empty scene list"]}
    for i, sc in enumerate(scenes):
        head = sc.get("heading") or " ".join(str(sc.get(k, "")) for k in ("h1", "h2"))
        if _words(head) > MAX_HEADLINE_WORDS + 2:
            w.append(f"scene {i} heading {_words(head)} words (busy)")
        if _nums(head) > MAX_NUMBERS_PER_SCREEN:
            w.append(f"scene {i} heading >{MAX_NUMBERS_PER_SCREEN} numbers")
        comp = sc.get("comp")                          # per-kind required-field contract (blank-risk)
        if comp:
            if isinstance(comp, (list, tuple)):
                kind, data = comp[0], (comp[1] if len(comp) > 1 else {})
            elif isinstance(comp, dict):
                kind, data = comp.get("type") or comp.get("kind"), comp
            else:
                kind, data = None, {}
            for miss in _comp_blankrisk(kind, data):
                w.append(f"BLANK-RISK: scene {i} comp '{kind}' missing {miss} → renders empty")
        if require_reason and _bad_reason(sc.get("reason")):
            w.append(f"NO-REASON: scene {i} — every visual must name what's said + what it adds")
    w += variety_warnings(scenes)
    return {"ok": not w, "warnings": w}


def lint_elements(elements, require_reason=False):
    """Lint a talking-head `elements:[...]` overlay plan (icon_tile/chip/lottie/count_up/emoji/…).
    Catches blank-risk elements + too-brief dwell; `require_reason` gates the justify-itself rule."""
    w = []
    for i, e in enumerate(elements or []):
        if not isinstance(e, dict):
            continue
        t = e.get("type", "icon_tile")
        blank = ((t == "icon_tile" and not (e.get("icon") or e.get("label")))
                 or (t == "lottie" and not (e.get("src") or e.get("icon")))
                 or (t == "count_up" and e.get("value") in (None, ""))
                 or (t == "emoji" and not (e.get("char") or e.get("name")))
                 or (t in ("chip", "badge", "marker") and not (e.get("label") or e.get("kind"))))
        if blank:
            w.append(f"BLANK-RISK: element {i} '{t}' missing its content field → renders empty")
        try:
            if float(e.get("dur", 3)) < 1.0:
                w.append(f"element {i} '{t}' dwell {e.get('dur')}s < 1.0s (too brief to read)")
        except Exception:
            pass
        lab = e.get("label") or e.get("text") or ""
        if lab and float(e.get("dur", 3) or 3) + 0.2 < reading_dwell(lab):
            w.append(f"element {i} '{t}' dwell {e.get('dur')}s < reading-time {reading_dwell(lab)}s for '{str(lab)[:20]}'")
        if require_reason and _bad_reason(e.get("reason")):
            w.append(f"NO-REASON: element {i} ({t})")
    w += _density_warnings(elements or [], "element")
    w += _safezone_warnings(elements)
    w += _collision_warnings(elements)
    return {"ok": not w, "warnings": w}


def report(result, label="spec-lint"):
    if result.get("ok"):
        print(f"[{label}] ✅ clean")
    else:
        print(f"[{label}] ⚠ {len(result['warnings'])} issue(s):")
        for x in result["warnings"]:
            print(f"   - {x}")
    return result


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        data = json.load(open(sys.argv[1], encoding="utf-8"))
        plan = data if isinstance(data, dict) and "segments" in data else {"segments": data}
        report(lint_course(plan))
    else:
        print("usage: python 4_BRAIN/spec_lint.py <plan.json>")
