# -*- coding: utf-8 -*-
"""SEOSONA Video — Course cut-planner (repurpose long course footage → tight lesson).

Knowledge/course videos are NOT generated like news; they REPURPOSE real footage. This plans
WHICH parts of a long course video to keep and IN WHAT ORDER.

The BRAIN is the user's proven prompt `9_PROMPTS/COURSE_SPLICE_PROMPT.md` — non-linear splicing
into a 5-act high-retention short (HOOK → NỖI ĐAU → TIP/TRICK → CASE STUDY → ĐÚC KẾT), 100% raw
text preserved (Ctrl+F audio match), captions corrected separately, SFX at splice points, one SRT
isolated per script. Three ways to produce the cut-plan:

  • LLM (auto)        — `plan_course(srt)`: sends the prompt+SRT to an LLM (Ollama/key), parses JSON.
  • Manual bridge     — `build_prompt(srt)` emits the filled prompt to run on ChatGPT/Gemini, then
                        `parse_matrix(text)` parses the pasted-back JSON/table → segments.
  • Deterministic     — fallback filler-trim (in-order) so the pipeline never blocks.

Output: {title, segments:[{part?, start, end, raw?, display?, value?}], n_cues, source}.
Kept separate from srt_analyzer (viral HOOKS for news) — different job.
"""
import os
import re
import sys
import json
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROMPT_PATH = os.path.join(ROOT, "9_PROMPTS", "COURSE_SPLICE_PROMPT.md")

# Spoken-filler cues to drop in the deterministic fallback (greetings/interjections).
_FILLER = ["xin chào", "chào mừng", "chào anh em", "ờ", "à ", "ừ", " ok ", "okê", "ô kê",
           "đúng không", "ha ", "nha ", "nhá", "đúng tám giờ", "mình bắt đầu", "rồi nha",
           "anh em nha", "cảm ơn anh em", "kết thúc video", "like share", "đăng ký kênh"]


def _ts_to_sec(s):
    s = s.strip().replace(",", ".")
    parts = s.split(":")
    if len(parts) == 3:
        h, m, rest = parts
    elif len(parts) == 2:
        h, m, rest = "0", parts[0], parts[1]
    else:
        return float(s)
    return int(h) * 3600 + int(m) * 60 + float(rest)


def parse_srt(path):
    """SRT → [{start,end,text}] (seconds)."""
    cues = []
    raw = open(path, encoding="utf-8", errors="replace").read()
    for chunk in re.split(r"\n\s*\n", raw):
        lines = [l for l in chunk.splitlines() if l.strip()]
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        try:
            # maxsplit=1: a stray 2nd "-->" in a malformed line won't ValueError the unpack. Per-cue guard:
            # one bad timestamp/cue must not abort the WHOLE SRT parse (→ course planning fails entirely).
            a, b = [x.strip() for x in tl.split("-->", 1)]
            text = " ".join(l for l in lines if "-->" not in l and not l.strip().isdigit()).strip()
            if text:
                cues.append({"start": _ts_to_sec(a), "end": _ts_to_sec(b), "text": text})
        except Exception:
            continue
    return cues


def _merge(cues, gap=1.6):
    """Merge adjacent (in-order) cues into segments — used only by the deterministic fallback."""
    segs = []
    for c in cues:
        if segs and c["start"] - segs[-1]["end"] <= gap:
            segs[-1]["end"] = c["end"]
        else:
            segs.append({"start": c["start"], "end": c["end"]})
    return segs


import unicodedata

# Talking-head CARD vocab (must match talking_head_edit.build_ass + course_video.topcards_from_plan).
CARD_TYPES = ("header", "bullet", "stat", "term", "quote", "steps")


def _norm_part(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("đ", "d")           # đ/Đ don't NFD-decompose → map manually so 'đau'/'đúc' match


def suggest_card(part, text="", has_value=False):
    """Cut-plan segment PART (+text) → a fitting talking-head CARD type from the REAL vocab. Mirrors the
    news `suggest_component`: this is what COUPLES the course cut-plan to the card library (typed), so a
    segment gets the RIGHT card (stat for a number, steps for a how-to, quote for the takeaway) instead
    of every segment defaulting to header+bullet. None of these kinds is invented — all render."""
    p = _norm_part(part)
    has_num = has_value or bool(re.search(r"\d", text or ""))
    if "hook" in p:
        return "header"
    if "noi dau" in p or "van de" in p or "pain" in p:
        return "term"
    if "tip" in p or "trick" in p or "meo" in p:
        return "steps"
    if "case" in p or "vi du" in p or "ket qua" in p or "study" in p:
        return "stat" if has_num else "bullet"
    if "duc ket" in p or "chot" in p or "tom" in p or "sum" in p:
        return "quote"
    return "bullet"


def _deterministic_plan(cues):
    kept = []
    for c in cues:
        low = " " + c["text"].lower() + " "
        words = len(c["text"].split())
        if words < 3:
            continue
        if any(f in low for f in _FILLER) and words < 10:
            continue
        kept.append(c)
    return _merge(kept)


# ---------------------------------------------------------------- prompt I/O

def _prompt_text():
    try:
        return open(PROMPT_PATH, encoding="utf-8").read()
    except Exception:
        return ""


def build_prompt(srt_path):
    """Return the canonical prompt with the SRT pasted in + JSON-mode instruction appended.
    Run this on ChatGPT/Gemini/any LLM, then feed the answer to parse_matrix()."""
    srt = open(srt_path, encoding="utf-8", errors="replace").read()
    base = _prompt_text()
    # Use sections A (rules+table) and B (JSON mode); drop our own doc header before "# SYSTEM".
    i = base.find("# SYSTEM INSTRUCTION")
    base = base[i:] if i >= 0 else base
    base = base.replace("[PASTE YOUR SRT FILE CONTENT HERE]", srt.strip())
    return base + ("\n\nIMPORTANT: also output the ENGINE JSON MODE ```json block (Section B schema) "
                   "so an editor can splice automatically.\n")


def parse_matrix(text):
    """Parse an LLM answer (the pasted-back result) → segments. Prefers the ```json block;
    falls back to the markdown table timecodes. Returns {title, segments} or None."""
    # 1) JSON block
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not m:
        m = re.search(r"(\{[^{}]*\"segments\"\s*:\s*\[.*?\]\s*\})", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            segs = []
            for s in data.get("segments", []):
                try:
                    st, en = float(s["start"]), float(s["end"])
                except Exception:
                    continue
                if en > st:
                    segs.append({"part": s.get("part", ""), "start": st, "end": en,
                                 "raw": s.get("raw", ""), "display": s.get("display", ""),
                                 "value": s.get("value", ""), "topcard": s.get("topcard"),
                                 "broll": s.get("broll")})
            if segs:
                return {"title": (data.get("title") or "Bài học SEO").strip(), "segments": segs}
        except Exception:
            pass
    # 2) Markdown-table fallback: pull `HH:MM:SS,mmm --> HH:MM:SS,mmm` or single timecodes
    rng = re.findall(r"(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{1,3})", text)
    if rng:
        segs = [{"start": _ts_to_sec(a), "end": _ts_to_sec(b)} for a, b in rng if _ts_to_sec(b) > _ts_to_sec(a)]
        if segs:
            return {"title": "Bài học SEO", "segments": segs}
    return None


# ---------------------------------------------------------------- LLM (auto)

def _llm_plan(cues, srt_path, title_hint):
    """Auto path: send the canonical prompt + SRT to an LLM, parse the JSON matrix. None if no LLM."""
    try:
        sw = import_module("scene_writer")
        if not sw._real_llm_available():
            return None
        llm = import_module("llm_engine")
    except Exception:
        return None
    try:
        prompt = build_prompt(srt_path)
        # Robust REAL-LLM cascade (Gemini keys rotated → Z.ai → OpenAI → Ollama → Claude), shape-checked
        # on 'segments', NO offline NLP router — the SAME reliability the news path uses. None → the
        # deterministic filler-trim fallback runs (never the social/thumbnail garbage generator).
        out = llm.generate_json_strict(prompt[:200], prompt, require_key="segments")
        plan = None
        if isinstance(out, dict) and out.get("segments"):
            plan = parse_matrix("```json\n" + json.dumps(out, ensure_ascii=False) + "\n```")
        if not plan:
            return None
        plan.update({"n_cues": len(cues), "source": "llm"})
        return plan
    except Exception:
        return None


# ---------------------------------------------------------------- public

def plan_course(srt_path, title_hint="", matrix_text=None, lint=True):
    """Return a usable cut-plan. If matrix_text (a pasted ChatGPT/Gemini answer) is given, use it;
    else try an LLM; else deterministic filler-trim. `lint=True` runs the shared `spec_lint.lint_course`
    gate (structure / duplicate part / hook / loop-back) — this is what CONNECTS the course path (D) to
    the same verification discipline as the news paths. Course narration = 100% real SRT transcript, so
    fabrication-traceability is N/A; the structure lint is the relevant gate here."""
    cues = parse_srt(srt_path)
    if not cues:
        return {"title": title_hint or "Bài học", "segments": [], "n_cues": 0, "source": "empty"}

    plan = None
    if matrix_text:
        p = parse_matrix(matrix_text)
        if p and p["segments"]:
            p.update({"n_cues": len(cues), "source": "matrix"})
            plan = p
    if plan is None:
        plan = _llm_plan(cues, srt_path, title_hint)
    if plan is None:
        plan = {"title": title_hint or "Bài học SEO", "segments": _deterministic_plan(cues),
                "n_cues": len(cues), "source": "deterministic"}

    # Typed writer↔library coupling: give each segment a suggested CARD type from its part (unless the
    # splice prompt already set one) so the render uses the full card library, not just header+bullet.
    for _s in plan.get("segments", []):
        if not _s.get("card_type"):
            _s["card_type"] = suggest_card(_s.get("part", ""), _s.get("display") or _s.get("raw", ""),
                                           has_value=bool(str(_s.get("value", "")).strip()))

    if lint:                                    # shared gate — surface structure/duplication warnings
        try:
            rep = import_module("spec_lint").lint_course(plan)
            plan["lint"] = rep
            if not rep.get("ok"):
                print(f"[course_planner] ⚠ lint_course ({len(rep.get('warnings', []))} warning):")
                for _w in rep.get("warnings", [])[:8]:
                    print("   ·", _w)
        except Exception as e:
            print(f"[course_planner] lint skipped: {e}")
    return plan


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Course cut-planner")
    ap.add_argument("srt")
    ap.add_argument("--emit-prompt", action="store_true", help="print the filled prompt for ChatGPT/Gemini")
    ap.add_argument("--from-matrix", help="parse a pasted-back LLM answer (file) → cut-plan")
    a = ap.parse_args()
    if a.emit_prompt:
        print(build_prompt(a.srt)); sys.exit(0)
    mt = open(a.from_matrix, encoding="utf-8").read() if a.from_matrix else None
    p = plan_course(a.srt, matrix_text=mt)
    total = sum(s["end"] - s["start"] for s in p["segments"])
    print(f"title: {p['title']}")
    print(f"source: {p['source']} | cues: {p['n_cues']} | segments: {len(p['segments'])} | kept {total:.0f}s")
    print(json.dumps(p["segments"][:6], ensure_ascii=False, indent=2))
