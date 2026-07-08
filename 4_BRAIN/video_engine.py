# -*- coding: utf-8 -*-
"""SEOSONA unified video engine — the single render brain (native_composer path).

Replaces the legacy `pipeline_manager.py` (HTML render-project engine). One entry,
`run_pipeline(...)`, handles every input mode and produces a finished SEOSONA video:

  - create   : a text/script OR a GitHub repo URL  → synthesized branded video
  - scrape   : a website URL  → scrape + SEO script → synthesized branded video
  - repurpose: a long MP4/SRT → transcript → hook analysis → vertical shorts
  - download : (handled by the router) YouTube/Drive → file → repurpose

Synthesis is rendered by `native_composer` (voice + RULE #1 captions + HyperFrames
native render + ducked-BGM/SFX mix). Repurpose reuses the proven clipper skill.
GitHub one-shots reuse `make_video.make` (real stars/desc, no hallucinated data).

The deterministic text→scenes planner is an honest DRAFT: it uses the real script
text for narration + captions and derives 2-tone headings from keywords. The
Scene-Composer agent (an LLM) produces richer scenes via `.agents/skills/scene-composer`;
this module guarantees a valid video with no human in the loop. No paid APIs required.
"""
import os
import re
import sys
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

import native_composer as nc  # noqa: E402
import make_video as mv       # noqa: E402  (GitHub one-shot path)
import brand_kit as bk        # noqa: E402  — single source of truth for brand CTA copy
import news_video_standards as nvs  # noqa: E402  (Vietnamese script quality gate)

WORKSPACE = os.path.join(ROOT, "8_WORKSPACE")


# ============================================================================ #
# Input detection (single source of truth — the router imports this).
# ============================================================================ #
def _is_github(value):
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    if "github.com/" in v:
        # a repo URL has owner/name after the host; bare github.com is not a repo
        tail = v.split("github.com/", 1)[1].strip("/")
        return len(tail.split("/")) >= 2
    # bare "owner/name" with no spaces/scheme and a single slash
    if re.fullmatch(r"[\w.-]+/[\w.-]+", value.strip()):
        return True
    return False


def detect_input_type(input_value):
    """Auto-detect the input and return (mode, processed_input)."""
    if not input_value:
        return "create", input_value

    if _is_github(input_value):
        return "create", input_value  # engine routes GitHub to the rich one-shot

    if isinstance(input_value, str) and (input_value.startswith("http://") or input_value.startswith("https://")):
        if "youtube.com" in input_value or "youtu.be" in input_value:
            return "download", input_value
        if "drive.google.com" in input_value:
            return "download", input_value
        return "scrape", input_value

    if isinstance(input_value, str) and os.path.isdir(input_value):
        return "repurpose", input_value

    if isinstance(input_value, str) and os.path.isfile(input_value):
        ext = os.path.splitext(input_value)[1].lower()
        if ext in (".srt", ".mp4", ".mkv", ".avi", ".mov", ".webm"):
            return "repurpose", input_value
        if ext in (".txt", ".md"):
            with open(input_value, "r", encoding="utf-8") as f:
                return "create", f.read()

    return "create", input_value


# ============================================================================ #
# Shared helpers
# ============================================================================ #
def _limit_words(text, max_words):
    words = (text or "").split()
    return " ".join(words[:max_words])


def _extract_srt_from_media(media_path, srt_out_path):
    """Transcribe a media file to SRT via the switchable ASR router (PhoWhisper
    primary, faster-whisper/openai backups). Returns True/False (caller logs)."""
    try:
        _asr = import_module("2_SKILLS.srt_maker.asr_router")
        _srt = import_module("2_SKILLS.srt_maker")
        words = _asr.transcribe_words(media_path, language="vi")
        if not words:
            return False
        segments = _srt.group_words_to_segments(words)

        def _ts(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec - int(sec)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        lines = []
        for i, seg in enumerate(segments, 1):
            lines += [str(i), f"{_ts(seg['start'])} --> {_ts(seg['end'])}", (seg.get("text") or "").strip(), ""]
        if len(lines) <= 1:
            return False
        with open(srt_out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True
    except Exception as e:
        print(f"[SRT Extract] failed for {media_path}: {e}")
        return False


# ============================================================================ #
# Text → scenes planner (deterministic backbone + optional LLM enrichment)
# ============================================================================ #
_STOP = set("là và của có không được một những các với cho khi này đó đã sẽ rất "
            "thì mà ở từ ra vào nên cũng để theo trên về "
            # common connectors/prepositions that were missing → a label/heading could start on or reduce to
            # a bare stopword ("Trong khi đó …" → junk label "TRONG"). Unambiguous only (skip hay/cần/chỉ/
            # lên/xuống which have common CONTENT senses).
            "trong đang quá đều còn đến dưới sau trước vì do bởi như cùng tại "
            "the a an of to in is for".split())
_ACCENTS = ("blue", "green", "orange")
_H2_BANK = ["là gì?", "vì sao hot?", "điểm chính", "đáng chú ý", "cần biết",
            "nổi bật", "thực tế", "tóm lại"]
# Kicker label per detected scene ROLE (was always "SEOSONA" → monotonous).
_KICKER_BY_ROLE = {"hero": "TIN NÓNG", "cta": "SEOSONA AI", "tip": "GHI NHỚ",
                   "stats": "CON SỐ", "bignum": "QUY MÔ", "quote": "GÓC NHÌN",
                   "compare": "SO SÁNH", "steps": "CÁCH LÀM", "feature": "ĐIỂM CHÍNH",
                   "alert": "LƯU Ý", "chiprow": "TƯƠNG THÍCH", "photocard": "MẸO"}   # + photo-tip card
_KICKER_BANK = ["BỐI CẢNH", "CHI TIẾT", "ĐÁNG CHÚ Ý", "THỰC TẾ", "TÁC ĐỘNG"]
# Sentences carrying these cues become a "GHI NHỚ" tip callout.
_MEM_CUES = ("ghi nhớ", "lưu ý", "mẹo", "đừng quên", "nhớ rằng", "chú ý", "quan trọng nhất")
# Enumeration cues → a step-by-step scene.
_STEP_CUES = ("đầu tiên", "tiếp theo", "sau đó", "cuối cùng", "bước ", "thứ nhất", "thứ hai")


def _label(seg, n=3):
    """Short UPPERCASE label = the sentence's LEADING content phrase, words in READING ORDER. Vietnamese
    is multi-syllable, so a contiguous phrase keeps compounds intact ('nghiên cứu', 'công cụ'); the old
    top-FREQUENCY single-syllable pick broke them AND jumbled order ('nghiên cứu từ khóa' → junk 'BƯỚC CỨU
    KHÓA'). Mirrors _heading's proven approach (which already uses _phrase for its titles)."""
    words = re.findall(r"[\wÀ-ỹ]+", seg or "")
    while words and words[0].lower() in _STOP:        # start on a content word (skip leading connectors)
        words = words[1:]
    parts = _phrase(words, 0, n, 34).split()
    while parts and parts[-1].lower() in _STOP:       # don't end on a trailing connector
        parts.pop()
    return " ".join(parts).upper() if parts else "SEOSONA"


# pure measurement units — a bignum label made ONLY of these ("PHẦN TRĂM") describes no subject, so we
# then look at the words BEFORE the number instead ("tỷ lệ chuyển đổi 80 phần trăm" → "TỶ LỆ CHUYỂN ĐỔI").
_UNIT_ONLY = {"phần", "trăm", "đồng", "usd", "vnd", "đô", "%"}


def _salient_num(nums):
    """The 'hero' number for a bignum = the most headline-worthy, not just the first one found. A
    percentage wins (it's the result); else the number with the most digits (a headline stat beats an
    incidental '3 tháng'); else the first. Fixes 'trong 3 tháng doanh thu tăng 47%' → 47%, not 3."""
    if not nums:
        return None
    pct = [n for n in nums if n.strip().endswith("%")]
    if pct:
        return pct[0]
    # A bare 4-digit YEAR (1990-2099) is temporal CONTEXT, not a headline stat — but it has more digits
    # than a real 2-3 digit count, so "most digits" would wrongly crown it ("năm 2026, 12 công cụ" → 2026
    # instead of 12). Deprioritize year-looking numbers; keep one only if it's the sole number present.
    def _is_year(n):
        d = re.sub(r"\D", "", n)
        return len(d) == 4 and 1990 <= int(d) <= 2099 and "%" not in n
    pool = [n for n in nums if not _is_year(n)] or nums
    # most digits wins (headline stat > incidental small count); ties → the earliest number.
    best = max(range(len(pool)), key=lambda i: (len(re.sub(r"\D", "", pool[i])), -i))
    return pool[best]


def _bignum_label(seg, num, maxlen=28):
    """A bignum caption should name WHAT the number measures = the noun phrase right after it
    ('trong 3 tháng doanh thu tăng 47%' → 'DOANH THU'), which reads far better than top-frequency
    keywords ('MÃI 2026 BIẾN'). Captions are TIGHT — capped at ≤2 words / maxlen chars. Tries the
    phrase after the number, then before; falls back to _label."""
    s = seg or ""
    m = re.search(r"(?<![\d.,])" + re.escape(str(num).rstrip("%")) + r"(?![\d.,])", s)
    if not m:
        return _label(seg)

    # function words that read as junk at the END of a 2-word caption (may not all be in _STOP)
    _trail = _STOP | {"bị", "sau", "và", "các", "những", "đã", "sẽ", "đang", "rất", "cho",
                      "với", "khi", "mà", "áp", "của", "trong", "một", "để", "là"}

    # counter/measure words that PRECEDE the real subject of a count — "10 lần hiệu suất" means the number
    # measures HIỆU SUẤT (×10), not LẦN; "3 cái máy" measures MÁY. Skip them like leading stopwords so the
    # label names the subject, not the counter unit (fixes "10 lần hiệu suất" → "HIỆU SUẤT", not "LẦN HIỆU").
    _unit_lead = {"lần", "cái", "chiếc"}

    def _clean(words):
        ph = []
        for w in words:
            if not ph and w.lower() in _STOP | _unit_lead:   # skip leading stopwords + counter units
                continue
            ph.append(w)
            if len(" ".join(ph)) >= maxlen or len(ph) >= 2:   # bignum captions are tight (≤2 words)
                break
        while ph and ph[-1].lower() in _trail:         # trim trailing function words
            ph.pop()
        return ph

    # phrase AFTER the number (the unit/subject of a COUNT: "22 website cờ bạc")
    after = _clean(re.findall(r"[\wÀ-ỹ]+", re.split(r"[.,;:!?…()]", s[m.end():], 1)[0]))
    # phrase BEFORE the number (the subject of a RESULT/%: "doanh thu tăng 47%") — drop a trailing
    # connective verb ("đạt/tăng/giảm…") then keep the nearest 2 content words, in reading order.
    _verb = {"đạt", "tăng", "giảm", "còn", "chỉ", "đến", "khoảng", "hơn", "gần", "tới", "là", "có", "với"}
    bw = re.findall(r"[\wÀ-ỹ]+", re.split(r"[.,;:!?…()]", s[:m.start()])[-1])
    while bw and bw[-1].lower() in _verb:
        bw.pop()
    before = _clean(bw[-2:])

    def _ok(ph):
        return ph and any(w.lower() not in _UNIT_ONLY for w in ph)

    # a % states a RESULT about a subject that PRECEDES it; a bare count PRECEDES its noun (which follows).
    order = [before, after] if "%" in str(num) else [after, before]
    for ph in order:
        if _ok(ph):
            return " ".join(ph).upper()[:maxlen + 8]
    return _label(seg)


def _cp_pick(seg, h1, i, total, prev_kind=None):
    """Extended scene→component vocabulary (component_picker). Returns (kind,data) or None. Uses pick_wide
    → reaches MORE of the 48-frame kho deterministically (steps/feature/phone/web/notification/social/
    terminal/divider/timeline) so the whole library is drawn on even with no LLM."""
    try:
        return import_module("component_picker").pick_wide(seg, h1, i, total, _label, prev_kind)
    except Exception:
        return None


def _split_sentences(text):
    text = re.sub(r"\s+", " ", (text or "").strip())
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip(" .") for p in parts if p.strip(" .")]


def _keywords(text, n=2):
    """Top content words by frequency (drops stopwords/short tokens). Honest draft —
    headings are derived from the real text, never invented."""
    toks = re.findall(r"[\wÀ-ỹ]+", (text or "").lower())
    freq = {}
    for t in toks:
        if len(t) < 3 or t in _STOP:
            continue
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq, key=lambda k: (-freq[k], k))[:n]
    return [w.capitalize() for w in top]


def _phrase(words, start, k, maxlen):
    """A short readable PHRASE (words in order) — Vietnamese words are multi-syllable,
    so a leading phrase reads far better than top-frequency single syllables."""
    out = []
    for w in words[start:start + k]:
        if (" ".join(out + [w])) and len(" ".join(out + [w])) > maxlen:
            break
        out.append(w)
    return " ".join(out)


def _heading(seg, idx, total):
    if idx == total - 1:
        return bk.CTA_FOLLOW, "xem thêm mỗi ngày"
    words = re.findall(r"[\wÀ-ỹ]+", seg)
    while words and words[0].lower() in _STOP:        # skip ALL leading connectors (a single skip left
        words = words[1:]                             # 'Trong khi đó …' → h1 starting on the stopword 'Khi')
    h1_span = _phrase(words, 0, 3, 16).split()        # words H1 CONSUMES → H2 starts AFTER this span (below)
    n1 = len(h1_span)
    d1 = list(h1_span)
    while d1 and d1[-1].lower() in _STOP:             # don't END h1 on a connector ('Nghiên cứu từ' → 'Nghiên cứu')
        d1.pop()
    h1 = " ".join(d1) or "SEOSONA"
    rest = words[n1:]                                 # H2 continues after H1's consumed span (no dup/loss)
    while rest and rest[0].lower() in _STOP:           # H2 also starts on a content word
        rest = rest[1:]
    d2 = _phrase(rest, 0, 3, 18).split()
    while d2 and d2[-1].lower() in _STOP:
        d2.pop()
    h2 = " ".join(d2)
    if not h2:
        kws = _keywords(seg, 1)
        h2 = kws[0] if kws else _H2_BANK[idx % len(_H2_BANK)]
    # Capitalise the first letter only (preserve Vietnamese diacritics mid-phrase).
    return h1[:1].upper() + h1[1:], h2


def _scene_count(n_sent):
    # PACING (2026-07): more, SHORTER scenes = a punchy reel, not a slideshow. Was max 7 (~12s/scene at
    # 60-90s → too slow). Now ~1 scene per sentence (cap 13) so each scene ≈ one spoken sentence (~4-6s
    # of voice = well-paced, still voice-synced so never TOO fast). See spec_lint.lint_pacing (the gate).
    return max(6, min(13, round(n_sent * 0.85)))


# Trailing connective words that make a HEADING read cut mid-clause ("TobyFlow không tự"). Trimmed off.
_HEAD_DANGLING = {"và", "của", "không", "tự", "mà", "rồi", "để", "cho", "với", "là", "các", "những", "trên",
                  "trong", "khi", "nếu", "hay", "hoặc", "bằng", "qua", "từ", "được", "bị", "sẽ", "đã", "này",
                  "đó", "thì", "ở", "ra", "vào", "nên", "cũng", "theo", "về", "một"}


# components that DISPLAY a figure — the heading must not repeat the number (de-dup, see plan_scenes).
_NUMERIC_COMP = {"bignum", "stats", "gauge", "ring", "donut", "pie", "bars", "linechart", "metric_rows"}


def _trim_dangling(text):
    """Never let a heading end on a dangling connective (the 'TobyFlow không tự' bug). Pops trailing
    connective words until the last word carries meaning; keeps ≥1 word (returns original if it'd empty)."""
    ws = str(text or "").split()
    while len(ws) > 1 and ws[-1].lower().strip(".,;:!?") in _HEAD_DANGLING:
        ws.pop()
    return " ".join(ws) if ws else str(text or "")


def _llm_plan(script_text):
    """High-quality copywriting-aware scene plan, delegated to the dedicated `scene_writer`
    module (kept separate so this file stays lean). Returns scene dicts or None — when None,
    the deterministic planner below takes over. Runs on free local Ollama or a cloud key."""
    try:
        return import_module("scene_writer").write_scenes(script_text)
    except Exception as e:
        print(f"[video_engine] LLM plan unavailable ({e}); using deterministic planner.")
        return None


def _hint_comp(kind, seg, h1):
    """Build a render-safe component from the writer's TEXT-ONLY suggestion (tip/quote/alert/callout/
    feature). Data-heavy kinds (compare/stats/bars/steps/checklist/icongrid/bignum) need real data →
    return None so the deterministic/LLM pickers build them from the (already-aligned) text."""
    s = seg.rstrip(".")
    if kind in ("tip", "callout"):
        return ("tip", {"title": (h1 or "GHI NHỚ").upper(), "text": s})
    if kind == "quote":
        return ("quote", {"text": s, "by": ""})
    if kind == "alert":
        return ("alert", {"role": "caution", "title": (h1 or "LƯU Ý").upper(), "text": s})
    if kind == "feature":
        return ("feature", {"items": [["✨", (h1 or "SEOSONA"), s[:60]]]})
    return None


def plan_scenes(script_text):
    """script text → (segments, scenes) ready for native_composer.make_video.

    `scenes` items: {kicker, h1, h2, acc, hero, comp:(kind,data)|None}.
    """
    sentences = _split_sentences(script_text)
    if not sentences:
        sentences = [_limit_words(script_text, 40) or "SEOSONA Video"]

    plan = _llm_plan(script_text)
    # ANTI-COMPRESSION (2026-07, "thiếu nội dung"): a RICH input (many facts/sentences) must NOT be squashed
    # into a few crammed scenes — that drops content + reads slow. If the LLM plan compressed a many-sentence
    # script well below one-scene-per-sentence, discard it and use the deterministic split that KEEPS the
    # facts (≈1 scene/sentence via _scene_count). Short inputs keep the LLM plan (it's better there).
    if plan and len(sentences) >= 8 and len(plan) < len(sentences) * 0.7:
        print(f"[plan_scenes] LLM compressed {len(sentences)} facts → {len(plan)} scenes; keeping content "
              f"with deterministic {_scene_count(len(sentences))}-scene split (anti-compression)")
        plan = None
    _whints = None                       # writer's per-scene component/block SUGGESTION (if any)
    if plan:
        groups = [[s["seg"]] for s in plan]
        forced_heads = [(s.get("h1", ""), s.get("h2", "")) for s in plan]
        _whints = [(s.get("comp_hint"), s.get("block"), s.get("fx")) for s in plan]
    else:
        n = _scene_count(len(sentences))
        # distribute sentences EVENLY (2026-07 DEAD-HOLD fix): the old `per = len//n` dumped ALL the remainder
        # into the LAST scene (12 sent / 10 scenes → last scene got 3 sentences → >13s CTA hold). Spread the
        # remainder so every scene ≈ equal length (esp. the CTA stays short) — no dead-hold.
        groups, forced_heads = [], None
        idx, rem_scenes, rem_sent = 0, n, len(sentences)
        for _ in range(n):
            take = max(1, round(rem_sent / rem_scenes))
            take = min(take, rem_sent - (rem_scenes - 1))   # leave ≥1 sentence for each remaining scene
            grp = sentences[idx:idx + max(1, take)] or [sentences[-1]]
            groups.append(grp)
            idx += len(grp); rem_sent -= len(grp); rem_scenes -= 1
        groups = [g for g in groups if g]

    total = len(groups)
    # STRUCTURAL VARIETY (2026-07, user "xài 1 template cho nhiều video"): the 23-template kho was only used
    # by the github path — news/topic/scrape videos (LLM OR deterministic) all shared one shape. ROTATE a
    # template (seeded by content → different topics get different arcs) and use its component SEQUENCE as the
    # writer-hints for EVERY scene, so each video follows a distinct structure. Keeps the LLM/heading CONTENT;
    # only borrows the component arc. A scene fills its beat via _hint_comp when content allows, else the
    # content-cue components + richness floor still win — honest + varied. (SEOSONA_TEMPLATE_ROTATE=0 to opt out.)
    if os.environ.get("SEOSONA_TEMPLATE_ROTATE", "1") == "1":
        try:
            _tmpls = sorted(t for t in nc.list_templates() if not t.startswith("_auto_"))  # skip repo-specific auto-gen
            if _tmpls and groups:
                _tseed = sum(ord(c) for c in (" ".join(groups[0])[:40] if groups[0] else "s"))
                _tname = _tmpls[_tseed % len(_tmpls)]
                _tcomps = [s.get("component") for s in nc.load_template(_tname).get("scenes", [])]
                _tcomps = [c for c in _tcomps if c]              # drop hook/None slots → real component beats
                if _tcomps:
                    # merge: keep any LLM per-scene block/fx hint, override the component hint with the template's
                    _prev = _whints or [(None, None, None)] * total
                    _whints = [(_tcomps[k % len(_tcomps)],
                                _prev[k][1] if k < len(_prev) else None,
                                _prev[k][2] if k < len(_prev) else None) for k in range(total)]
                    print(f"[plan_scenes] structure ← template '{_tname}' ({len(_tcomps)} beats) — variety")
        except Exception as _te:
            print(f"[plan_scenes] template rotation skipped ({_te})")
    segments, scenes = [], []
    used_stats = used_bignum = False
    _prev_kind = None   # last scene's component kind (component_picker uses it to avoid repeats)
    # STRUCTURED component enrichment — one LLM pass assigns hub/bars/compare/checklist/… to the
    # scenes that fit (auto-on when a real LLM is up; else {} and the deterministic picker runs).
    _llm_comps = {}
    try:
        _cpm = import_module("component_picker")
        _llm_in = [{"seg": " ".join(g).strip(),
                    "h1": (forced_heads[k][0] if forced_heads else "")} for k, g in enumerate(groups)]
        _llm_comps = _cpm.enrich_llm(_llm_in)
    except Exception as _e:
        print(f"[video_engine] LLM component enrich skipped ({_e})")
    _block_budget = [int(os.environ.get("SEOSONA_BLOCK_BUDGET", "4"))]  # enriching blocks per video (SEOSONA_USE_BLOCKS=1)
    _grow_budget = [int(os.environ.get("SEOSONA_GROW_BUDGET", "3"))]    # kho self-grow: new frames synthesised per video (richer kho faster)
    for i, grp in enumerate(groups):
        seg = " ".join(grp).strip()
        if not seg.endswith((".", "!", "?")):
            seg += "."
        if forced_heads:
            h1, h2 = forced_heads[i]
            if not h1:
                h1, h2 = _heading(seg, i, total)
        else:
            h1, h2 = _heading(seg, i, total)
        h1, h2 = _trim_dangling(h1), _trim_dangling(h2)   # no heading cut mid-clause ("… không tự")
        acc = _ACCENTS[i % len(_ACCENTS)]
        comp = None
        hero = False
        role = None
        low = seg.lower()
        nums = re.findall(r"\d[\d.,]*%?", seg)
        nwords = len(re.findall(r"[\wÀ-ỹ]+", seg))

        if i == 0:
            hero = True            # full-bleed accent intro (breaks the centered-card sameness)
            role = "hero"
            if nums:               # a number in the hook → big-number hero
                _bn = _salient_num(nums)
                comp = ("bignum", {"big": _bn, "label": _bignum_label(seg, _bn)})
        elif i == total - 1:
            # rotate the CTA VARIANT per-video (craft-study §7) so endings vary: subscribe /
            # comment-bait / follow. Deterministic from the hook text → same video, same CTA.
            _cv = ["subscribe", "comment", "follow"][sum(ord(c) for c in (segments[0] if segments else "s")) % 3]
            comp = ("cta", {"line": bk.CTA_TAGLINE, "btn": bk.CTA_BUTTON, "variant": _cv, "keyword": "AI"})
            role = "cta"
        # STRUCTURED LLM component (highest priority for a middle scene) — hub/bars/compare/…
        elif i in _llm_comps:
            comp = _llm_comps[i]; role = comp[0]
        # Extended vocabulary next (craft-study §7): component_picker turns caution/danger,
        # false-number and explicit-list beats into alert/bignum-strike/chiprow components so
        # the new library resources actually appear. Falls through to the classics below.
        elif (_picked := _cp_pick(seg, h1, i, total, _prev_kind)):
            comp = _picked; role = _picked[0]
        # Richer component detection from the real text (was: only stats/quote). Every
        # branch builds render-safe data shapes — never an empty component.
        elif any(c in low for c in _MEM_CUES):
            comp = ("tip", {"title": "GHI NHỚ", "text": seg.rstrip(".")})
            role = "tip"
        elif len(nums) >= 2 and not used_stats:
            used_stats = True
            # label each stat with the phrase near ITS number (was empty "" → 3 context-less big numbers).
            comp = ("stats", {"items": [(n, _bignum_label(seg, n)) for n in nums[:3]]})
            role = "stats"
        elif len(nums) == 1 and not used_bignum:
            used_bignum = True                          # this branch fires only when len(nums)==1
            comp = ("bignum", {"big": nums[0], "label": _bignum_label(seg, nums[0])})
            role = "bignum"
        elif nwords <= 12:
            comp = ("quote", {"text": seg.rstrip("."), "by": ""})
            role = "quote"
        # else: text-only scene — fill it with the WRITER'S suggested component if one fits.
        _wh_comp, _wh_block, _wh_fx = (_whints[i] if _whints and i < len(_whints) else (None, None, None))
        if comp is None and _wh_comp:
            _hc = _hint_comp(_wh_comp, seg, h1)
            if _hc:
                comp = _hc; role = _hc[0]
        # SELF-SUFFICIENT RICHNESS FLOOR — a bare MIDDLE scene still gets a real, non-fabricated
        # visual from the kho (rotated for variety, no repeats). This is the factory doing its OWN
        # enrichment: no external LLM needed, so videos stay rich even when the LLM cascade is down.
        # Only honest data (scene text / concept keyword) → never invents numbers. photocard here also
        # turns ON the image kho (native_composer auto-sources a real 9:16 photo per concept).
        if comp is None and 0 < i < total - 1:
            try:
                _cp = import_module("component_picker")
                # KHO SELF-GROW (budgeted): nothing built-in fit → HyperFrames auto-synthesises a NEW
                # frame from this scene's content + BANKS it (reused free forever). Best-effort + local-first
                # (fast; skips silently if no LLM). Budget caps it per video so the kho grows gradually.
                if _grow_budget[0] > 0:
                    _g = _cp.auto_grow(seg, h1, i)
                    if _g:
                        comp = _g; role = _g[0]; _grow_budget[0] -= 1
                        print(f"[plan_scenes] kho GREW new frame '{_g[0]}' for scene {i} (banked → reusable)")
                if comp is None:            # grow declined → deterministic richness floor (no LLM)
                    _concept = " ".join(_keywords(seg, 2)) or h1
                    _fc = _cp.fill(seg, h1, i, _prev_kind, _label, _concept)
                    if _fc:
                        comp = _fc; role = _fc[0]
            except Exception as _e:
                print(f"[video_engine] richness-floor skipped ({_e})")

        # DE-DUP (2026-07): a NUMERIC component (bignum/stats/gauge…) already shows the figure + unit, so the
        # HEADING must NOT repeat it (the "Hiện 7900 người dùng" heading OVER a "7,900 người dùng" bignum).
        # Drop the number from the emphasis line → the figure appears exactly ONCE.
        if comp and comp[0] in _NUMERIC_COMP:
            if re.search(r"\d", h2 or ""):
                h2 = ""
            h1 = _trim_dangling(re.sub(r"\b\d[\d.,]*%?\b", "", str(h1 or "")).strip(" ·-")) or h1

        kicker = _KICKER_BY_ROLE.get(role) or _KICKER_BANK[i % len(_KICKER_BANK)]
        segments.append(seg)
        scene = {"kicker": kicker, "h1": h1, "h2": h2, "acc": acc, "hero": hero, "comp": comp}
        if _wh_fx:                       # writer's explicit SFX/transition override (else auto-by-kind)
            scene["fx"] = _wh_fx
        # ENRICH with a HyperFrames block: the writer's block suggestion wins; else content-match pick.
        # Conservative + capped + opt-in (SEOSONA_USE_BLOCKS=1); 14 components stay the default.
        if _wh_block:
            scene["block"] = _wh_block
        elif _block_budget[0] > 0:
            try:
                blk = import_module("block_picker").pick_block(seg)
            except Exception:
                blk = None
            if blk:
                scene["block"] = blk
                _block_budget[0] -= 1
        scenes.append(scene)
        _prev_kind = comp[0] if comp else None

    # VISUAL-COVERAGE GOVERNOR — a demo must be VISUAL, not talking text. The richness floor above already
    # fills bare middle scenes; this GUARANTEES the ≥60% floor explicitly (and logs it, so a thin video is
    # never silent) by force-filling any straggler middle scene. Self-contained — no LLM.
    _vis = sum(1 for s in scenes if s.get("comp"))
    _floor = int(len(scenes) * 0.6 + 0.999)
    if _vis < _floor:
        try:
            _cp = import_module("component_picker")
            _pk = None
            for k, (sg, s) in enumerate(zip(segments, scenes)):
                if 0 < k < len(scenes) - 1 and not s.get("comp") and _vis < _floor:
                    _fc = _cp.fill(sg, s.get("h1", ""), k, _pk, _label,
                                   " ".join(_keywords(sg, 2)) or s.get("h1", ""))
                    if _fc:
                        s["comp"] = _fc; _vis += 1
                _pk = (s.get("comp") or (None,))[0]
        except Exception as _e:
            print(f"[plan_scenes] coverage governor skipped ({_e})")
    print(f"[plan_scenes] visual coverage {_vis}/{len(scenes)} "
          f"({100 * _vis // max(len(scenes), 1)}%) — floor {_floor}")
    return segments, scenes


# ============================================================================ #
# Mode handlers
# ============================================================================ #
def _create_github(target, project_dir, output, theme):
    """Rich GitHub one-shot (real metadata, auto template + theme)."""
    out = mv.make(target, theme=(theme or "light"), output=output, project_dir=project_dir)
    score_output(out, "seosona")
    maybe_publish(out, project_dir, os.path.basename(project_dir), str(target), "seosona")
    return out


def _vietnamese_gate(script_text):
    """RULE: SEOSONA scripts are Vietnamese — block raw English prose. Strict by
    default (SEOSONA_STRICT_VIETNAMESE_NEWS=1); set to 0 to warn instead of raise."""
    try:
        validation = nvs.validate_vietnamese_news_script(script_text)
    except Exception as e:
        print(f"[video_engine] VN gate skipped ({e}).")
        return
    if getattr(validation, "is_valid", True):
        return
    terms = ", ".join(getattr(validation, "disallowed_terms", [])[:12])
    msg = f"Vietnamese script gate failed — disallowed English prose: {terms}"
    if os.getenv("SEOSONA_STRICT_VIETNAMESE_NEWS", "1") == "1":
        raise RuntimeError(msg)
    print(f"[video_engine] QUALITY WARNING: {msg}")


def _make_thumbnail(project_dir, scenes, segments, brand, aspect_ratio="9:16"):
    try:
        tm = import_module("2_SKILLS.thumbnail_maker.thumbnail_maker")
        thumb_dir = os.path.join(project_dir, "Thumbnail")
        os.makedirs(thumb_dir, exist_ok=True)
        h1 = scenes[0].get("h1", "") if scenes else ""
        h2 = scenes[0].get("h2", "") if scenes else ""
        title = (f"{h1} {h2}").strip() or "SEOSONA"
        # The scene already gives us the exact headline; NLP only adds the highlight
        # keyword + subtext. This designer PNG is the canonical Thumbnail/thumbnail.png
        # (native_composer's frame grab is saved separately as thumbnail_frame.png).
        tm.make_thumbnail(
            content=(segments[0] if segments else title),
            output_path=os.path.join(thumb_dir, "thumbnail.png"),
            aspect_ratio=aspect_ratio, brand=brand,
            top_label="SEOSONA" if brand == "seosona" else brand.upper(),
            main_title=title,
        )
    except Exception as e:
        print(f"[video_engine] thumbnail skipped: {e}")


def score_output(output, brand="seosona"):
    """Quality gate on a finished video (best-effort, non-fatal). Runs on EVERY
    create entrypoint so direct make_video / news batches are scored too."""
    try:
        qs = import_module("quality_scorer")
        report = qs.score_video(output, brand=brand)
        verdict = "PASS" if report.get("pass") else "FAIL"
        print(f"[quality] {report.get('score', '?')}/100 ({verdict})")
        try:                                   # Phase 6: feed the observability hub (9_DASHBOARD)
            _root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            sys.path.insert(0, os.path.join(_root, "9_DASHBOARD"))
            import_module("obs_metrics").record("quality", output=output,
                                                score=report.get("score"), verdict=verdict)
        except Exception:
            pass
        return report
    except Exception as e:
        print(f"[quality] scoring skipped: {e}")
        return None


def maybe_publish(output, project_dir, project_name, script_text="", brand="seosona"):
    """STEP 8 (optional) — publish if SEOSONA_PUBLISH is set (e.g. "google_drive,youtube").
    Credential-gated per destination; never breaks the render."""
    targets = os.environ.get("SEOSONA_PUBLISH", "").strip()
    if not targets:
        return None
    # EVALUATOR GATE (maker-checker): an independent skeptic must approve the real MP4 before
    # it can publish. A REJECT blocks publishing (the output stays for human review). Override
    # with SEOSONA_SKIP_EVAL=1 only for debugging.
    if os.environ.get("SEOSONA_SKIP_EVAL", "0") != "1":
        try:
            verdict = import_module("evaluator").evaluate(output, brand=brand)
            if not verdict.get("ok"):
                print(f"[publish] BLOCKED by evaluator — {'; '.join(verdict.get('reasons', []))}")
                return {"_blocked": "evaluator-reject", "reasons": verdict.get("reasons", [])}
        except Exception as ee:
            print(f"[publish] evaluator gate skipped (non-fatal): {ee}")
    try:
        ag = os.path.join(ROOT, "1_AGENTS")
        if ag not in sys.path:
            sys.path.insert(0, ag)
        from publisher_agent import publish as _publish
        thumb = os.path.join(project_dir, "Thumbnail", "thumbnail.png")
        product = {"video": output, "title": project_name}
        if os.path.exists(thumb):
            product["thumbnail"] = thumb
        try:
            from seo_optimizer.youtube_seo import generate_youtube_metadata
            kw = [w for w in project_name.replace("_", " ").replace("-", " ").split()
                  if len(w) > 2][:5] or [project_name]
            hook = (script_text or project_name).strip().split(".")[0][:120]
            seo = generate_youtube_metadata(hook, kw, {}, video_duration=60)
            product.update({"title": seo["title"], "description": seo["description"], "tags": seo["tags"]})
            print(f"[publish] SEO metadata: {seo['title']}")
        except Exception as se:
            print(f"[publish] SEO enrich skipped: {se}")
        # CC-BY: append the BGM attribution (native_composer wrote `<output>.credits.txt` when a sourced
        # track was used) to the published description, so the licence obligation actually reaches the platform.
        try:
            _cf = output + ".credits.txt"
            if os.path.exists(_cf):
                _credit = open(_cf, encoding="utf-8").read().strip()
                if _credit:
                    product["description"] = (product.get("description", "").rstrip() + "\n\n" + _credit).strip()
                    print("[publish] BGM credit appended to description")
        except Exception as _ce:
            print(f"[publish] credit append skipped: {_ce}")
        dests = [d.strip() for d in targets.split(",") if d.strip()]
        print(f"[publish] → {', '.join(dests)}")
        return _publish(product, destinations=dests,
                        save_report_to=os.path.join(project_dir, "publish_report.json"))
    except Exception as e:
        print(f"[publish] step failed (non-fatal): {e}")
        return None


def _scrape_capture(url, project_dir, max_shots=3):
    """Capture source-page screenshots (B-roll → project_dir/broll/) + a text 'mockup'
    card built from real page headings. Best-effort: needs Playwright; returns the
    mockup data dict or None. (HyperFrames scenes can't composite raw images, so the
    screenshots are saved as assets and the on-screen card is the text mockup.)"""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print(f"[scrape] screenshots skipped (Playwright unavailable): {e}")
        return None
    broll = os.path.join(project_dir, "broll")
    os.makedirs(broll, exist_ok=True)
    domain = url.split("//")[-1].split("/")[0]
    lines = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            for i in range(max_shots):
                page.screenshot(path=os.path.join(broll, f"shot_{i}.png"))
                page.evaluate("window.scrollBy(0, 800)")
                page.wait_for_timeout(400)
            try:
                heads = page.eval_on_selector_all(
                    "h1,h2,h3", "els => els.slice(0,4).map(e=>e.innerText.trim()).filter(Boolean)")
                lines = [h[:60] for h in heads][:4]
            except Exception:
                pass
            browser.close()
        print(f"[scrape] captured {max_shots} screenshots → {broll}")
    except Exception as e:
        print(f"[scrape] screenshot capture failed: {e}")
        return None
    return {"url": domain, "lines": lines or [domain]}


def _create_from_text(script_text, project_dir, output, theme, brand="seosona", mockup=None, source_url=None):
    _vietnamese_gate(script_text)
    # CONTENT MODERATION (pre-render gate): enforce "real data only, brand-safe". A BLOCK
    # stops the render; FLAGs warn (unless SEOSONA_MODERATION=strict). Override: =off.
    if os.environ.get("SEOSONA_MODERATION", "warn").lower() != "off":
        verdict = import_module("content_moderation").moderate(script_text)
        if not verdict["ok"]:
            raise RuntimeError(
                "Content moderation "
                + ("BLOCKED" if verdict["severity"] == "block" else "flagged (strict)")
                + ": " + "; ".join(f"{f['kind']}:{f['detail']}" for f in verdict["flags"])
                + ". Fix the script (real cited data, brand-safe) or set SEOSONA_MODERATION=warn/off.")
    segments, scenes = plan_scenes(script_text)
    # input-link → cào ảnh: give photo/mockup scenes the SOURCE PAGE's own images (else photocard
    # falls back to per-concept Pexels at render time). Best-effort, never blocks the render.
    if source_url:
        try:
            sys.path.insert(0, os.path.join(ROOT, "2_SKILLS", "image_sourcer"))
            _n = import_module("image_sourcer").assign_from_url(scenes, source_url)
            if _n:
                print(f"[video_engine] scraped {_n} image(s) from source → scenes")
        except Exception as _e:
            print(f"[video_engine] source-image scrape skipped ({_e})")
    # UNIFIED verify gate (same one make_video + course use): the freeform scenes must stay grounded
    # in the source script — flag any number/name that isn't in it, and any repeated line.
    try:
        _sw = import_module("script_writer")
        _kf = _sw.analyze(_sw.fetch(script_text, context=script_text))
        _vr = _sw.verify(_sw.Script(scenes=[{"idx": i, "text_vi": s, "h1": "", "h2": ""}
                                            for i, s in enumerate(segments)]), _kf, unsourced=False)
        _bad = [e for e in _vr.errors if ("nghi bịa" in e or "lặp câu" in e)]
        if _bad:
            print("[video_engine] ⚠ VERIFY: " + " | ".join(_bad[:5]))
    except Exception:
        pass
    if mockup and len(scenes) >= 3:
        # show the source page as a text mockup card on an early middle scene
        scenes[1]["comp"] = ("mockup", mockup)
    print(f"[video_engine] create: {len(scenes)} scenes from {len(segments)} segments")
    out = nc.make_video(project_dir, segments, scenes, output=output,
                        theme=(theme or "light"), brand=brand)
    _make_thumbnail(project_dir, scenes, segments, brand)
    score_output(out, brand)
    maybe_publish(out, project_dir, os.path.basename(project_dir), script_text, brand)
    return out


def _scrape_to_text(url):
    scraper = import_module("1_AGENTS.scraper_agent.scraper")
    scraped = scraper.scrape_article(url)
    if scraped and scraped.get("content"):
        print(f"[scrape] '{scraped.get('title')}' ({scraped.get('word_count')} words)")
        try:
            writer = import_module("1_AGENTS.seo_writer_agent.writer").SeoWriterAgent()
            script_json = writer.generate_script(scraped)
            text = (script_json or {}).get("narrator_text", "")
            if not text and isinstance(script_json, dict) and "scenes" in script_json:
                text = " ".join(s.get("narrator_text", "") for s in script_json["scenes"])
            if text:
                return text
        except Exception as e:
            print(f"[scrape] SEO writer failed ({e}); using trimmed article body.")
        return _limit_words(scraped["content"], 200)
    print("[scrape] scraping failed/empty.")
    return None


def _repurpose(media_path, project_dir, brand, project_name):
    srt_dir = os.path.join(project_dir, "SRT")
    thumb_dir = os.path.join(project_dir, "Thumbnail")
    os.makedirs(srt_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    real_srt = os.path.join(srt_dir, f"{project_name}_source.srt")
    is_srt = str(media_path).lower().endswith(".srt")
    if is_srt:
        real_srt = media_path
    elif not _extract_srt_from_media(media_path, real_srt):
        print("[REPURPOSE] WARNING: transcript extraction failed — hooks may be unreliable.")

    analyzer = import_module("1_AGENTS.repurposer_agent.srt_analyzer")
    clipper = import_module("2_SKILLS.video_clipper.clipper")
    tm = import_module("2_SKILLS.thumbnail_maker.thumbnail_maker")

    hooks = analyzer.analyze_srt_for_hooks(real_srt) or []
    outputs = []
    for hook in hooks:
        hid = hook.get("id", "?")
        out_name = os.path.join(project_dir, f"{project_name}_Part{hid}.mp4")
        if not is_srt:
            try:                                   # one bad hook (timestamp/corrupt region) must not abort
                clipper.cut_and_format_short(media_path, hook["start"], hook["end"], out_name)
                outputs.append(out_name)
            except Exception as e:                 # the whole batch → skip this short, keep the rest
                print(f"[REPURPOSE] clip failed for part {hid}: {e} — skipping.")
                continue
        thumb_out = os.path.join(thumb_dir, f"{project_name}_Part{hid}_Thumbnail.png")
        try:
            tm.make_thumbnail(
                content=hook.get("hook_text", "") or "VIDEO SHORTS",
                output_path=thumb_out, aspect_ratio="9:16", brand=brand,
                top_label="BẢN TIN",
            )
        except Exception as e:
            print(f"[REPURPOSE] thumbnail failed for part {hid}: {e}")
    print(f"[REPURPOSE] {len(outputs)} shorts → {project_dir}")
    return {"project_dir": project_dir, "outputs": outputs}


# ============================================================================ #
# Public entry — signature-compatible with the legacy pipeline_manager.
# ============================================================================ #
def run_pipeline(script_text, brand="seosona", mode="create", aspect_ratio="9:16", project_name=None):
    if not project_name:
        from datetime import datetime
        project_name = f"{brand.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if mode == "carousel":
        raise RuntimeError(
            "Carousel and image workflows are not video workflows. "
            "Use scripts/workflow_social_post.py or `npm run post:image`."
        )

    project_dir = os.path.join(WORKSPACE, project_name)
    os.makedirs(project_dir, exist_ok=True)
    output = os.path.join(project_dir, "FINAL.mp4")
    theme = "light"  # brand law: light mode only

    print(f"[video_engine] mode={mode} brand={brand} ratio={aspect_ratio} → {project_name}")

    try:
        if mode == "repurpose":
            return _repurpose(script_text, project_dir, brand, project_name)

        if mode == "scrape":
            text = _scrape_to_text(script_text)
            if not text:
                raise RuntimeError(f"Scrape produced no usable script from: {script_text}")
            mockup = _scrape_capture(script_text, project_dir)  # screenshots + source card
            return _create_from_text(text, project_dir, output, theme, brand, mockup=mockup, source_url=script_text)

        # create (text or GitHub)
        if _is_github(script_text):
            return _create_github(script_text, project_dir, output, theme)
        return _create_from_text(script_text, project_dir, output, theme, brand)
    except Exception:
        _cleanup_incomplete(project_dir)
        raise


def _cleanup_incomplete(project_dir):
    """Delete the project dir if the render failed before any real output exists
    (no .mp4/.srt/.png that isn't an intermediate). Mirrors the old engine."""
    if not os.path.isdir(project_dir):
        return
    for root_d, _dirs, files in os.walk(project_dir):
        for fn in files:
            low = fn.lower()
            if low.endswith((".mp4", ".srt", ".png")) and "_raw" not in low \
               and "scene_" not in low and "voice." not in low:
                return  # a real product file exists — keep it
    try:
        import shutil
        shutil.rmtree(project_dir)
        print(f"[video_engine] cleaned up incomplete project: {project_dir}")
    except Exception as e:
        print(f"[video_engine] cleanup failed for {project_dir}: {e}")


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "SEOSONA Video Factory tự động sản xuất video tiếng Việt bằng AI."
    brand = sys.argv[2] if len(sys.argv) > 2 else "seosona"
    ratio = sys.argv[3] if len(sys.argv) > 3 else "9:16"
    name = sys.argv[4] if len(sys.argv) > 4 else None
    mode, processed = detect_input_type(inp)
    print(run_pipeline(processed, brand=brand, mode=mode, aspect_ratio=ratio, project_name=name))
