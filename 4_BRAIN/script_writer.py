# -*- coding: utf-8 -*-
"""SEOSONA — UNIFIED script-writing pipeline (the ONE path all video narration goes through).

Six stages, each with a clear input/output + a gate, so every pipeline (news, course, agent) writes to
the SAME rules and NOTHING skips verification:

    [1] FETCH   input → SourceData   (gate: must have a source_url OR raw_text; else UNSOURCED)
    [2] ANALYZE SourceData → KeyFacts (gate: every claim/number traces to the source text/fields)
    [3] REASON  KeyFacts → Angle      (angle_finder — pick a lens grounded in the facts)
    [4] PLAN    Angle → Outline        (gate: no two scenes share a focus; each maps to a fact)
    [5] WRITE   Outline+KeyFacts → Script (grounded prompt; MASTER_VIDEO_SPEC loaded at runtime)
    [6] VERIFY  Script → VerifyResult   (5 gates incl. FULL TRACEABILITY — reject → rewrite)

Rules live in `9_PROMPTS/MASTER_VIDEO_SPEC.md` (loaded here, NOT hardcoded) + the domain skills.
This module ADDS the pipeline; it delegates to existing modules (angle_finder, spec_lint,
news_video_standards, content_moderation, llm_engine) — no logic is duplicated.
See `6_SOP/SCRIPT_WRITING_PIPELINE.md`.
"""
import os
import re
import sys
from dataclasses import dataclass, field
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
SPEC_PATH = os.path.join(ROOT, "9_PROMPTS", "MASTER_VIDEO_SPEC.md")


# ── data structures ────────────────────────────────────────────────────────────────────────
@dataclass
class SourceData:
    facts: dict                       # structured real fields (GitHub metadata, RSS item, …)
    raw_text: str                     # the source prose to draw from (desc, article, SRT text)
    source_url: str = ""
    unsourced: bool = False           # topic with no attached source → tighten the numbers gate


@dataclass
class KeyFacts:
    claims: list = field(default_factory=list)     # short factual statements, each traceable
    numbers: list = field(default_factory=list)    # [{"value": int, "raw": "119,787", "context": str}]
    entities: list = field(default_factory=list)   # tool/company/person/lang/license names


@dataclass
class Outline:
    scenes: list = field(default_factory=list)     # [{"idx", "focus", "component"}]


@dataclass
class Script:
    scenes: list = field(default_factory=list)     # [{"idx", "text_vi", "h1", "h2"}]


@dataclass
class VerifyResult:
    ok: bool
    errors: list = field(default_factory=list)     # hard failures → reject + rewrite
    warnings: list = field(default_factory=list)   # soft flags → keep but note


# ── shared helpers ─────────────────────────────────────────────────────────────────────────
_SPEC_CACHE = None


def load_spec():
    """The canonical rulebook (MASTER_VIDEO_SPEC.md), loaded once. This is the SINGLE source of the
    writing rules — every path reads them from here instead of hardcoding its own copy."""
    global _SPEC_CACHE
    if _SPEC_CACHE is None:
        try:
            _SPEC_CACHE = open(SPEC_PATH, encoding="utf-8").read()
        except Exception:
            _SPEC_CACHE = ""
    return _SPEC_CACHE


def _norm(s):
    """Normalise for entity/number matching: lowercase, strip diacritics + non-alphanumerics."""
    import unicodedata
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


_MAG = {"nghìn": 1000, "ngàn": 1000, "k": 1000, "triệu": 1_000_000, "tr": 1_000_000,
        "tỷ": 1_000_000_000, "tỉ": 1_000_000_000}


def _extract_numbers(text):
    """Pull numbers from prose, honouring Vietnamese magnitude words so '5 triệu' → 5,000,000 and
    'hơn 119 nghìn' → 119,000. Returns [{"value": int, "raw": str, "pct": bool}]. A trailing '%' /
    'phần trăm' is captured and flagged `pct` — a percentage is a DATA claim (traced regardless of
    magnitude), unlike a bare small count ('3 cách'), so a fabricated '5%' is caught, not waved through."""
    out = []
    for m in re.finditer(r"(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s*(nghìn|ngàn|triệu|tỷ|tỉ|tr|k)?\s*(%|phần trăm)?", str(text or ""), re.I):
        num, mag, pct = m.group(1), (m.group(2) or "").lower(), (m.group(3) or "")
        base = re.sub(r"[.,\s]", "", num)
        if not base.isdigit():
            continue
        val = int(base)
        if mag in _MAG:
            val = int(val * _MAG[mag])
        out.append({"value": val, "raw": m.group(0).strip(), "pct": bool(pct)})
    return out


def _num_match(v, kv):
    """A spoken number `v` matches a known fact `kv` only within the SAME order of magnitude (so 900
    never matches 119,787) but with a rounding tolerance (so 119,000 ≈ 119,787)."""
    import math
    if v == kv:
        return True
    if v <= 0 or kv <= 0:
        return False
    if abs(math.log10(v) - math.log10(kv)) > 0.35:     # different magnitude → not the same fact
        return False
    return abs(v - kv) <= max(999, kv * 0.05)


def _pct_match(v, kv):
    """A spoken PERCENTAGE traces to a source percentage only within a TIGHT tolerance — '30%' and '50%'
    are DIFFERENT facts. _num_match must NOT be used for percentages: its max(999, …) floor is meaningless
    for 0–100 values, so it would wave a fabricated '50%' onto a real '30%' (magnitude ratio < 2.24, abs
    diff < 999). Allow ~2 points / 3% for honest rounding of a source figure ('78%' spoken as '80%')."""
    if v == kv:
        return True
    if v <= 0 or kv <= 0:
        return False
    return abs(v - kv) <= max(2, kv * 0.03)


# ── [1] FETCH ──────────────────────────────────────────────────────────────────────────────
def fetch(input_value, context=""):
    """input (GitHub url / topic text / dict of facts) → SourceData. `context` lets a bare topic
    carry attached source prose (an article, notes) so it is NOT flagged UNSOURCED."""
    if isinstance(input_value, dict):                       # already-fetched facts (e.g. gh metadata)
        raw = context or input_value.get("desc", "")
        return SourceData(facts=input_value, raw_text=raw,
                          source_url=input_value.get("url", ""), unsourced=not (raw or input_value))
    val = str(input_value or "").strip()
    if re.match(r"https?://github\.com/|^[\w.-]+/[\w.-]+$", val):
        try:
            gh = import_module("scene_composer").fetch_github(val)
            if gh and not gh.get("error"):
                return SourceData(facts=gh, raw_text=gh.get("desc", ""),
                                  source_url=gh.get("url", val), unsourced=False)
        except Exception:
            pass
    # a plain topic → RESEARCH the web (Google News RSS, free) for real facts to ground on, UNLESS the
    # caller already attached source prose via `context`. Off with SEOSONA_RESEARCH=0.
    if not context and os.environ.get("SEOSONA_RESEARCH", "1") != "0":
        try:
            res = import_module("researcher").research(val, max_items=6, fetch_bodies=2)
            if res.get("raw_text"):
                return SourceData(facts={"topic": val, "sources": res["sources"]},
                                  raw_text=res["raw_text"],
                                  source_url=(res["sources"][0] if res["sources"] else ""),
                                  unsourced=False)        # grounded on real gathered news
        except Exception as e:
            print(f"[script_writer] research skipped ({e})")
    # a plain topic / attached article text (no research)
    return SourceData(facts={}, raw_text=(context or val), source_url="",
                      unsourced=not context)             # topic with no source → tighten gates


# ── [2] ANALYZE ────────────────────────────────────────────────────────────────────────────
def analyze(src):
    """SourceData → KeyFacts. Every number/entity/claim is pulled from the REAL source fields +
    raw_text only — nothing invented. This is what the WRITE stage is allowed to draw from."""
    kf = KeyFacts()
    f = src.facts or {}
    # numbers: from structured fields (stars) + any in the raw text
    if f.get("stars"):
        kf.numbers.append({"value": int(f["stars"]), "raw": f.get("stars_h", str(f["stars"])),
                           "context": "GitHub stars"})
    for n in _extract_numbers(src.raw_text):
        n["context"] = "source text"
        kf.numbers.append(n)
    # entities: repo/tool name, language, license, topics + capitalised words in the raw text
    for key in ("name", "lang", "license"):
        if f.get(key):
            kf.entities.append(str(f[key]))
    kf.entities += [str(t) for t in (f.get("topics") or [])]
    kf.entities += re.findall(r"\b[A-Z][A-Za-z0-9.+-]{1,}\b", src.raw_text or "")
    kf.entities = list(dict.fromkeys(kf.entities))          # de-dup, keep order
    # claims: the source description sentences (the only prose we may paraphrase)
    if src.raw_text:
        kf.claims = [s.strip() for s in re.split(r"[.!?\n]", src.raw_text) if len(s.strip()) > 8]
    return kf


# ── [3] REASON ─────────────────────────────────────────────────────────────────────────────
def reason(kf, topic):
    """KeyFacts + topic → chosen Angle (via the existing angle_finder; grounded in the facts).
    Returns a dict {lens, headline, hook, why} or None (caller proceeds without an explicit angle)."""
    try:
        res = import_module("angle_finder").find_angles(topic)
        if res and res.get("angles"):
            return res["angles"][res.get("recommended", 0)]
    except Exception:
        pass
    return None


# ── [6] VERIFY — the 5 gates, incl. FULL TRACEABILITY ─────────────────────────────────────────
# Vietnamese words that take an initial capital at a sentence start and would otherwise masquerade as
# invented proper nouns. Combined with the sentence-initial skip below, this kills the entity noise.
_VN_CAP_STOP = {_norm(w) for w in (
    "Bạn", "Năm", "Hay", "Xu", "Web", "Khi", "Nếu", "Các", "Một", "Này", "Đó", "Từ", "Với", "Cho",
    "Là", "Có", "Và", "Của", "Theo", "Trong", "Ngoài", "Hơn", "Người", "Việc", "Điều", "Cách",
    "Không", "Được", "Sẽ", "Đã", "Những", "Rất", "Nhiều", "Chúng", "Tôi", "Hãy", "Vì", "Nên", "Mà",
    "Tại", "Sao", "Làm", "Thế", "Nào", "Đây", "Vậy", "Nhưng", "Bây", "Giờ", "Ngay", "Hiện", "Nay")}


def _spoken_entities(txt):
    """Proper-noun-ish tokens in narration worth tracing for fabrication: ALL-CAPS acronyms anywhere
    (SEO, GEO, API), PLUS Capitalised words that are NOT sentence-initial — so a Vietnamese sentence
    opener like 'Bạn'/'Năm' is never mistaken for an invented brand. High precision, low noise."""
    ents = list(re.findall(r"\b[A-Z]{2,}[0-9]*\b", txt))              # acronyms, any position
    for m in re.finditer(r"[A-Z][A-Za-z0-9.+-]{2,}", txt):
        prev = txt[:m.start()].rstrip()
        if prev and prev[-1] not in ".!?:…\n":                        # keep only mid-sentence Caps
            ents.append(m.group().rstrip(".+-"))                      # drop trailing punctuation
    return list(dict.fromkeys(e for e in ents if e))


def _traceability(script, kf, unsourced=False):
    """Gate 2 (FULL): every NUMBER + ENTITY spoken in the script must trace to KeyFacts. Numbers match
    by value with a ±rounding tolerance (so 'hơn 119 nghìn' ≈ 119,787). Entities match normalised.
    Returns (errors, warnings). A thin/UNSOURCED source → any un-traceable number is a hard error."""
    errors, warnings = [], []
    # split by kind: a spoken percentage may ONLY trace to a source PERCENTAGE (tight tolerance), a plain
    # number to a source number — else a fabricated '50%' matched a raw count of 50, or a nearby pct, and slipped.
    kf_nums = [n["value"] for n in kf.numbers if not n.get("pct")]
    kf_pcts = [n["value"] for n in kf.numbers if n.get("pct")]
    kf_ents = {_norm(e) for e in kf.entities if _norm(e)}
    # a small allow-list of brand/common tokens that are always legitimate, never "invented data"
    allow_ent = {_norm(x) for x in ("SEOSONA", "GitHub", "AI", "Google", "YouTube", "TikTok")}
    for sc in script.scenes:
        txt = sc.get("text_vi", "")
        for n in _extract_numbers(txt):
            v = n["value"]
            if v < 100 and not n.get("pct"):                # small counts (steps, "3 cách") aren't "data"
                continue                                    # …but a percentage always is → keep checking
            traced = (any(_pct_match(v, kv) for kv in kf_pcts) if n.get("pct")
                      else any(_num_match(v, kv) for kv in kf_nums))
            if not traced:
                errors.append(f"scene {sc.get('idx')}: số '{n['raw']}' KHÔNG có trong nguồn (nghi bịa)")
        for ent in _spoken_entities(txt):
            ne = _norm(ent)
            if (ne and ne not in kf_ents and ne not in allow_ent
                    and ne not in _VN_CAP_STOP and len(ne) > 3):
                warnings.append(f"scene {sc.get('idx')}: tên riêng '{ent}' không có trong nguồn")
    if unsourced:                                           # no source → promote entity warnings to errors
        errors += [w.replace("không có trong nguồn", "không nguồn (topic tự do → cấm)")
                   for w in warnings if "tên riêng" in w]
        warnings = [w for w in warnings if "tên riêng" not in w]
    return errors, warnings


def _replace_figure(txt, n):
    """Swap ONE fabricated figure for a grounded, magnitude-free generic that carries no invented data:
    a percentage → 'một phần', any other number → 'rất nhiều'. Neither asserts a specific quantity, so
    nothing untrue ships. Replaces only the first occurrence of that exact figure."""
    repl = "một phần" if n.get("pct") else "rất nhiều"
    return txt.replace(n["raw"], repl, 1)


def _strip_fabricated(script, kf, unsourced=False):
    """LAST-RESORT SANITISE (makes the traceability gate ENFORCING, not advisory): when the rewrite loop
    has run out and a NUMBER in the narration still traces to nothing in KeyFacts, replace that specific
    figure with a grounded generic so NO invented number reaches the render. Real (traceable) numbers are
    left untouched. Mutates script.scenes in place; returns how many figures were stripped."""
    # same pct-aware split as _traceability, so the strip removes EXACTLY what the gate flags (no drift).
    kf_nums = [n["value"] for n in kf.numbers if not n.get("pct")]
    kf_pcts = [n["value"] for n in kf.numbers if n.get("pct")]
    stripped = 0
    for sc in script.scenes:
        txt = sc.get("text_vi", "")
        if not txt:
            continue
        bad = [n for n in _extract_numbers(txt)
               if (n["value"] >= 100 or n.get("pct"))
               and not (any(_pct_match(n["value"], kv) for kv in kf_pcts) if n.get("pct")
                        else any(_num_match(n["value"], kv) for kv in kf_nums))]
        if not bad:
            continue
        for n in bad:
            txt = _replace_figure(txt, n)
            stripped += 1
        sc["text_vi"] = re.sub(r"\s{2,}", " ", txt).strip()
    return stripped


def verify(script, kf, unsourced=False, trace=True):
    """Run ALL gates on a written Script. Any hard error → ok=False → caller rewrites. Applied by
    EVERY pipeline (news + course), so no path ships un-verified copy. `trace=False` (or empty
    KeyFacts) skips the traceability gate — used by the render-chokepoint floor, where no source is
    available to compare against and running it would false-flag every number."""
    errors, warnings = [], []
    full_text = " ".join(sc.get("text_vi", "") for sc in script.scenes)
    # Gate 1 — English leak (Vietnamese narration only)
    try:
        val = import_module("news_video_standards").validate_vietnamese_news_script(full_text)
        if not getattr(val, "is_valid", True):
            errors.append("lọt tiếng Anh: " + ", ".join(getattr(val, "disallowed_terms", [])[:8]))
    except Exception:
        pass
    # Gate 2 — FULL traceability (no fabricated numbers/entities); skipped when there are no facts to
    # compare against (trace=False or empty KeyFacts) so we never flag numbers with nothing to check.
    if trace and (kf.numbers or kf.entities):
        e2, w2 = _traceability(script, kf, unsourced)
        errors += e2
        warnings += w2
    # Gate 3 — fabricated social-proof / unsafe (content_moderation)
    try:
        verdict = import_module("content_moderation").moderate(full_text, record=False)
        for fl in verdict.get("flags", []):
            (errors if fl.get("severity") == "block" else warnings).append(
                f"{fl.get('kind')}: {fl.get('detail')}")
    except Exception:
        pass
    # Gate 4 — structure / duplicate scene / busy heading (spec_lint)
    try:
        sl = import_module("spec_lint").lint_scenes(
            [{"h1": s.get("h1", ""), "h2": s.get("h2", ""), "segs": [s.get("text_vi", "")]}
             for s in script.scenes])
        warnings += sl.get("warnings", [])
    except Exception:
        pass
    # Gate 5 — repeated sentences (the "trùng cảnh" the owner flagged)
    seen = {}
    for sc in script.scenes:
        key = _norm(sc.get("text_vi", ""))[:40]
        if key and key in seen:
            errors.append(f"scene {sc.get('idx')}: lặp câu với scene {seen[key]}")
        seen[key] = sc.get("idx")
    return VerifyResult(ok=not errors, errors=errors, warnings=warnings)


# ── prompt building (ONE set of rules, from MASTER_VIDEO_SPEC.md — not hardcoded) ─────────────
def _spec_excerpt(max_chars=3800):
    """Pull the rule-bearing sections of MASTER_VIDEO_SPEC (HARD RULES + HOW TO WRITE) for the prompt,
    so the writer follows the ONE canonical rulebook. Falls back to a compact built-in if unreadable."""
    spec = load_spec()
    if not spec:
        return ("HARD RULES: tiếng Việt thuần; KHÔNG lọt câu tiếng Anh; mỗi cảnh 1 ý; "
                "KHÔNG lặp câu/từ mở đầu; CHỈ dùng dữ kiện được cấp, KHÔNG bịa số/tên.")
    keep, take = [], False
    for line in spec.splitlines():
        low = line.lower()
        if line.startswith("## "):
            take = any(k in low for k in ("hard rule", "how to write", "content craft", "core mindset"))
        if take:
            keep.append(line)
    out = "\n".join(keep) or spec
    return out[:max_chars]


def _fewshot(n=2):
    """A couple of hand-authored sample scripts (9_PROMPTS/video_scripts/*.md) as style examples —
    so the LLM matches SEOSONA's proven voice instead of generic AI prose. Best-effort, cached."""
    d = os.path.join(ROOT, "9_PROMPTS", "video_scripts")
    if not os.path.isdir(d):
        return ""
    picks = sorted(f for f in os.listdir(d) if f.endswith(".md"))[:n]
    ex = []
    for f in picks:
        try:
            body = open(os.path.join(d, f), encoding="utf-8").read()
            lines = [re.sub(r"^\d+\.\s*\*\*\[.*?\]\*\*\s*", "", ln).strip()
                     for ln in body.splitlines() if re.match(r"^\d+\.\s*\*\*\[", ln)]
            if lines:
                ex.append("Ví dụ văn phong SEOSONA:\n" + "\n".join("- " + l for l in lines[:6]))
        except Exception:
            continue
    return "\n\n".join(ex)


def _system_prompt():
    """The SINGLE writer system prompt — role + the canonical rules loaded from MASTER_VIDEO_SPEC."""
    return (
        "Bạn là biên kịch video ngắn tiếng Việt cho SEOSONA (kênh SEO/Marketing, khán giả VN B2B). "
        "Viết lời đọc THUẦN VIỆT, tự nhiên, súc tích. Tuân THẬT SÁT bộ luật dưới đây.\n\n"
        "=== LUẬT (MASTER_VIDEO_SPEC) ===\n" + _spec_excerpt() + "\n\n"
        "=== GROUNDING (bắt buộc) ===\n"
        "- CHỈ dùng dữ kiện trong phần KeyFacts được cấp. TUYỆT ĐỐI KHÔNG bịa số liệu, tên riêng, tính năng, "
        "hay TUYÊN BỐ SAI SỰ THẬT để giật tít (vd KHÔNG nói 'công cụ ĐO tốc độ làm CHẬM website' — sai bản chất). "
        "Câu hook phải ĐÚNG sự thật, gây tò mò bằng góc nhìn thật, không bằng thông tin sai.\n"
        "- Câu nào không dựa được vào KeyFacts thì viết chung chung, KHÔNG nêu số/tên cụ thể.\n"
        "- MỖI SỐ LIỆU chỉ dùng MỘT LẦN, đúng ngữ cảnh gốc của nó. KHÔNG gán lại một con số cho hai tuyên bố "
        "khác nhau/mâu thuẫn (vd KHÔNG nói '93% ngân sách lãng phí' rồi lại '93% người dùng thành công'). "
        "Nếu chỉ có một số liệu, dùng nó ĐÚNG một chỗ; các câu khác viết chung chung, không lặp số đó.\n"
        "- AN TOÀN THƯƠNG HIỆU: video này LÀ của SEOSONA. TUYỆT ĐỐI KHÔNG quảng bá/giới thiệu/kêu gọi tải-truy "
        "cập thương hiệu, công ty hay website KHÁC (vd 'tải file miễn phí từ X', 'truy cập Y'), dù nguồn "
        "nghiên cứu có nhắc tới. Tên bên ngoài chỉ được nêu như DỮ KIỆN trung tính, không khen/mời gọi. Chỉ "
        "có MỘT CTA duy nhất là theo dõi SEOSONA — KHÔNG dẫn người xem rời kênh sang nguồn khác.\n"
        "- KHÔNG chèn nguyên câu tiếng Anh; dịch sang tiếng Việt. Mỗi cảnh mở đầu bằng cấu trúc KHÁC nhau.")


# ── component/block suggestion (writer ↔ library coupling) ────────────────────────────────────
# Valid kinds ONLY (must match native_composer._component + component_picker) — never invent a kind.
_COMP_KINDS = ("bignum", "stats", "compare", "bars", "steps", "checklist", "icongrid", "alert",
               "chiprow", "hub", "quote", "tip", "feature", "callout", "cta")


def suggest_component(focus, text=""):
    """Scene FOCUS (+ optional text) → a fitting component KIND + block, from the REAL vocab only.
    This is the writer's VISUAL INTENT: the narration is written to fit it (so the component pickers
    reliably detect it) and the render prefers it — keeping the writer and the component/block
    libraries in lock-step instead of the picker guessing from text alone."""
    f = _norm(focus)                     # NOTE: _norm strips spaces too → match space-free tokens
    has_num = bool(_extract_numbers(text)) if text else False
    if "cta" in f:
        kind = "cta"
    elif "hook" in f:
        kind = "bignum" if has_num else "callout"
    elif "sosanh" in f or "khacbiet" in f:
        kind = "compare"
    elif "cachdung" in f or "cachlam" in f or "buoc" in f:
        kind = "steps"
    elif "bangchung" in f:
        kind = "stats"
    elif "loiich" in f:
        kind = "checklist"
    elif "ruiro" in f or "luuy" in f or "phanbien" in f:
        kind = "alert"
    elif "xuhuong" in f:
        kind = "bars"
    elif "vidu" in f or "vithuc" in f:
        kind = "quote"
    elif "giatri" in f or "tinhnang" in f:
        kind = "icongrid"
    elif "boicanh" in f:
        kind = "feature"
    else:
        kind = "tip"
    block = "data-chart" if kind in ("bignum", "stats", "bars", "compare") else None
    return kind, block


# Real effect vocab (must match native SFX keys + effect_library.TRANSITIONS) — never invent.
_SFX_KEYS = ("impact_deep", "impact_soft", "impact_hit", "ui_success", "ui_pop", "ui_click",
             "ui_positive", "ui_notify", "riser_short")
_TRANSITIONS = ("slide-up", "rise-fade", "zoom", "drop", "dissolve", "wipe-up")


def suggest_fx(focus, kind):
    """OPTIONAL explicit effect for a scene → {sfx?, transition?} from the REAL vocab, or None. Only
    the strong beats where an explicit FX beats the auto component-default: a build-up riser + punchy
    zoom on the HOOK, a zoom close on the CTA, an impact on an alert. None → auto-by-component (the
    SFX/entrance still follow the component kind), so this is a sparse OVERRIDE, not a replacement."""
    f = _norm(focus)
    if "hook" in f:
        return {"sfx": "riser_short", "transition": "zoom"}   # build-up + punchy open
    if "cta" in f:
        return {"transition": "zoom"}                         # punchy close
    if "ruiro" in f or "luuy" in f or "phanbien" in f:
        return {"sfx": "impact_hit"}                          # make the alert land
    return None                                              # else → auto (component-driven)


# how each component wants its narration written (fed into the prompt so text ↔ visual align)
_COMP_WRITE_HINT = {
    "compare": "viết dạng đối lập: 'thay vì X thì Y' hoặc 'trước … nay …'",
    "steps": "liệt kê các bước theo thứ tự",
    "stats": "nêu 2-3 con số cụ thể (có nguồn)",
    "bignum": "nhấn 1 con số lớn nhất",
    "checklist": "liệt kê các mục việc/lợi ích",
    "icongrid": "liệt kê 3-6 tính năng ngắn",
    "alert": "cảnh báo/lưu ý rõ ràng",
    "bars": "so sánh mức độ giữa vài mục",
    "quote": "1 câu ngắn đáng nhớ",
    "feature": "nêu 1 điểm nổi bật + mô tả ngắn",
    "callout": "1 câu khẳng định mạnh mở đầu",
    "tip": "1 mẹo/ghi nhớ súc tích",
    "cta": "kêu gọi theo dõi SEOSONA",
}


# ── [4] PLAN ───────────────────────────────────────────────────────────────────────────────
def plan(angle, kf, n_scenes=10):
    """Angle + KeyFacts → an Outline of n distinct scene focuses (hook → … → CTA). Deterministic
    skeleton grounded in the available facts (the WRITE stage fills the prose). No two focuses repeat.
    Each scene also carries a suggested component KIND + block (writer ↔ library coupling)."""
    focuses = ["HOOK — mở bằng con số/khẳng định mạnh nhất"]
    pool = [c[:60] for c in kf.claims[:n_scenes]] or ["bối cảnh", "giá trị cốt lõi"]
    # 10 distinct archetypes → no body-focus repeats until n_scenes > 12 (was 6 → repeated from n=9).
    body = ["BỐI CẢNH", "GIÁ TRỊ CHÍNH", "SO SÁNH / KHÁC BIỆT", "CÁCH DÙNG", "BẰNG CHỨNG",
            "LỢI ÍCH", "RỦI RO / LƯU Ý", "XU HƯỚNG", "VÍ DỤ THỰC TẾ", "PHẢN BIỆN"]
    for i in range(n_scenes - 2):
        focuses.append(body[i % len(body)] + (f" ({pool[i % len(pool)]})" if i < len(pool) else ""))
    focuses.append("CTA — theo dõi SEOSONA")
    # belt-and-suspenders: guarantee no two focuses are identical even if archetypes wrap
    seen, uniq = set(), []
    for f in focuses:
        base = f.split(" (")[0]
        uniq.append(f if base not in seen else f"{f} · góc {len(uniq)}")
        seen.add(base)
    out = []
    for i, f in enumerate(uniq[:n_scenes]):
        kind, block = suggest_component(f)
        out.append({"idx": i, "focus": f, "component": kind, "block": block, "fx": suggest_fx(f, kind)})
    return Outline(scenes=out)


# ── [5] WRITE ──────────────────────────────────────────────────────────────────────────────
def write(outline, kf, n_scenes=None, feedback=""):
    """Outline + KeyFacts → a Script (Vietnamese narration), via the unified prompt on the shared LLM
    chain (Gemini→Ollama). `feedback` (verify errors from a prior attempt) is injected so a rewrite
    actually CORRECTS instead of repeating. Returns a Script, or None if no LLM is reachable (caller
    uses its deterministic fallback). The output is NOT trusted until verify() passes."""
    n = n_scenes or len(outline.scenes)
    facts_txt = ("Số liệu THẬT: " + "; ".join(f"{x['raw']} ({x.get('context','')})" for x in kf.numbers[:8]) +
                 "\nTên riêng THẬT: " + ", ".join(kf.entities[:12]) +
                 "\nÝ nguồn: " + " | ".join(kf.claims[:6]))
    def _scene_line(s):
        k = s.get("component") or "tip"
        return (f"  Cảnh {s['idx']+1}: {s['focus']}  [hình ảnh: {k}"
                + (f" — {_COMP_WRITE_HINT[k]}" if k in _COMP_WRITE_HINT else "") + "]")
    userp = (f"{facts_txt}\n\nDàn ý {n} cảnh (bám sát, mỗi cảnh đúng trọng tâm của nó):\n" +
             "\n".join(_scene_line(s) for s in outline.scenes) +
             "\n\nMỗi cảnh VIẾT lời đọc HỢP với dạng hình ảnh đã ghi (để hình và lời khớp nhau)." +
             (("\n\n" + _fewshot()) if _fewshot() else "") +
             f"\n\nTrả JSON: {{\"scenes\":[{{\"text_vi\":\"lời đọc ~28-40 từ\",\"h1\":\"dòng tiêu đề (≤22)\","
             f"\"h2\":\"từ nhấn (≤22)\"}}]}} đúng {n} phần tử, cảnh cuối là CTA theo dõi SEOSONA.")
    if feedback:                                        # rewrite → tell the LLM exactly what to fix
        userp += (f"\n\n⚠ BẢN TRƯỚC BỊ LỖI, SỬA CHO ĐÚNG (đừng lặp lại lỗi này, đừng trùng câu, "
                  f"đủ {n} cảnh): {feedback}")
    try:
        # REAL-LLM cascade only (Gemini→OpenAI→Ollama→Claude), shape-validated, NO offline NLP router —
        # so a bad tier retries the next instead of dropping to formulaic templates ("mất tự nhiên").
        out = import_module("llm_engine").generate_scenes_json(_system_prompt(), userp)
        rows = out.get("scenes") if isinstance(out, dict) else None
        if isinstance(rows, list) and rows:
            if len(rows) < n:               # LLM under-delivered → make the drop VISIBLE (was silent)
                print(f"[script_writer] ⚠ LLM trả {len(rows)}/{n} cảnh — thiếu {n - len(rows)}")
            osc = outline.scenes            # carry the per-scene component/block suggestion downstream
            return Script(scenes=[{"idx": i, "text_vi": r.get("text_vi", ""),
                                   "h1": r.get("h1", ""), "h2": r.get("h2", ""),
                                   "comp_hint": (osc[i].get("component") if i < len(osc) else None),
                                   "block": (osc[i].get("block") if i < len(osc) else None),
                                   "fx": (osc[i].get("fx") if i < len(osc) else None)}
                                  for i, r in enumerate(rows[:n])])
    except RuntimeError:
        raise                               # SEOSONA_REQUIRE_LLM abort — propagate, don't silently drop
    except Exception as e:
        print(f"[script_writer] write LLM unavailable ({e})")
    return None


# ── orchestrator ─────────────────────────────────────────────────────────────────────────────
def generate_script(input_value, topic=None, n_scenes=10, context="", max_rewrites=2):
    """Run the full 6-stage pipeline. Returns (Script|None, VerifyResult, KeyFacts). None script →
    the caller falls back to its deterministic writer (which then ALSO goes through verify())."""
    src = fetch(input_value, context=context)
    kf = analyze(src)
    ang = reason(kf, topic or src.raw_text[:80] or "SEOSONA")
    outline = plan(ang, kf, n_scenes)
    feedback = ""
    last = VerifyResult(ok=False, errors=["no LLM"])
    for _ in range(max_rewrites + 1):
        script = write(outline, kf, n_scenes, feedback=feedback)
        if not script:
            return None, VerifyResult(ok=False, errors=["LLM unavailable"]), kf
        last = verify(script, kf, unsourced=src.unsourced)
        if len(script.scenes) < n_scenes:               # content-drop guard → force a rewrite
            last.errors.append(f"rớt cảnh: chỉ {len(script.scenes)}/{n_scenes} cảnh")
            last.ok = False
        if last.ok:
            return script, last, kf
        feedback = "; ".join(last.errors[:5])           # feed errors back → rewrite (loop)
    # Rewrite loop exhausted — the LLM kept re-inserting a flagged figure. Do NOT ship it: STRIP any
    # still-fabricated number to a grounded generic, then re-verify. This is what makes the traceability
    # gate ENFORCING rather than advisory — no invented number reaches the render (the invariant this gate
    # exists to hold). Genuine researched numbers match KeyFacts and are left intact.
    n_stripped = _strip_fabricated(script, kf, unsourced=src.unsourced)
    if n_stripped:
        print(f"[script_writer] ⚠ gỡ {n_stripped} số bịa (không sửa được sau {max_rewrites} lần rewrite) "
              f"→ thay bằng cách nói chung, KHÔNG để số bịa lọt ra render")
        last = verify(script, kf, unsourced=src.unsourced)
    return script, last, kf


# ── render-chokepoint gate (so NO path — incl. the Claude agent path — skips verification) ─────
def enforce_before_render(scene_texts, kf=None, unsourced=False):
    """The ONE gate every render funnels through (native_composer.make_video calls it). The agent
    path (Claude writes via the scene-composer skill) has no code-level verify of its own; this makes
    verification UNAVOIDABLE at render time. Runs the source-independent gates always (English leak,
    repeated scene, moderation, structure); runs FULL traceability only when KeyFacts are supplied.
    Never raises — returns a VerifyResult the caller can act on."""
    scenes = []
    for i, t in enumerate(scene_texts or []):
        txt = t if isinstance(t, str) else (t.get("text_vi") or t.get("text") or "")
        scenes.append({"idx": i, "text_vi": txt})
    try:
        return verify(Script(scenes=scenes), kf or KeyFacts(),
                      unsourced=unsourced, trace=kf is not None)
    except Exception as e:
        return VerifyResult(ok=True, errors=[], warnings=[f"verify skipped: {e}"])


if __name__ == "__main__":
    # smoke test — trace a fabricated number
    kf = KeyFacts(numbers=[{"value": 119787, "raw": "119,787", "context": "stars"}],
                  entities=["agency-agents", "Shell", "MIT"])
    good = Script(scenes=[{"idx": 0, "text_vi": "Dự án đã đạt hơn 119 nghìn sao.", "h1": "a", "h2": "b"}])
    bad = Script(scenes=[{"idx": 0, "text_vi": "Dự án có 5 triệu người dùng và 900 nghìn sao.", "h1": "a", "h2": "b"}])
    print("good:", verify(good, kf).ok, "| errors:", verify(good, kf).errors)
    print("bad :", verify(bad, kf).ok, "| errors:", verify(bad, kf).errors)
