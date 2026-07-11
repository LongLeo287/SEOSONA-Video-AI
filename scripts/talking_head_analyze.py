# -*- coding: utf-8 -*-
"""Talking-head footage analyzer — find dead air + duplicate takes from a word-level transcript.

Reads a `words.json` ([{"word","start","end"}, …] from talking_head_transcribe) and reports:
  • SILENCES  — gaps > threshold between words (dead air to trim)
  • DUPLICATE TAKES — a phrase spoken twice within a short window (a flubbed take + its retake);
    the EARLIER span is the likely one to cut, the later is usually the good take.

Portable heuristic (algorithm harvested from mrbuslov/capcut-ai-editor + capcut-cli, re-built native,
free, no LLM). Output is advisory — for review or to feed an auto-cut list into talking_head_edit.

  python scripts/talking_head_analyze.py selfshot/words.json
  python scripts/talking_head_analyze.py selfshot/words.json --silence 1.0 --json selfshot/analysis.json
"""
import argparse
import difflib
import json
import re
import sys


def detect_silences(words, threshold_s=1.0):
    """Gaps >= threshold_s between consecutive words → dead air to trim."""
    out = []
    for i in range(len(words) - 1):
        gap = float(words[i + 1]["start"]) - float(words[i]["end"])
        if gap >= threshold_s:
            out.append({"start": round(float(words[i]["end"]), 2),
                        "end": round(float(words[i + 1]["start"]), 2),
                        "duration": round(gap, 2),
                        "after": words[i]["word"], "before": words[i + 1]["word"]})
    return out


def _norm(w):
    return re.sub(r"[^\w]", "", str(w).lower(), flags=re.UNICODE)


def detect_duplicate_takes(words, win=6, min_run=4, sim=0.8, look_s=20.0):
    """Flag a run of ~`win` words that repeats (similarity >= `sim`) within `look_s` seconds — a
    likely flubbed take + retake. Returns spans; cut take1 (earlier), keep take2 (later)."""
    toks = [_norm(w["word"]) for w in words]
    n = len(words)
    dups, used, i = [], set(), 0
    while i < n - min_run:
        if i in used:
            i += 1
            continue
        a = toks[i:i + win]
        hit = None
        for j in range(i + min_run, n - min_run + 1):
            if float(words[j]["start"]) - float(words[i]["start"]) > look_s:
                break
            r = difflib.SequenceMatcher(None, a, toks[j:j + win]).ratio()
            if r >= sim:
                hit = (j, r)
                break
        if hit:
            j, r = hit
            end_i = min(i + win - 1, n - 1)
            end_j = min(j + win - 1, n - 1)
            dups.append({"take1": [round(float(words[i]["start"]), 2), round(float(words[end_i]["end"]), 2)],
                         "take2": [round(float(words[j]["start"]), 2), round(float(words[end_j]["end"]), 2)],
                         "similarity": round(r, 2),
                         "text": " ".join(w["word"] for w in words[i:end_i + 1])})
            used.update(range(i, i + win))
            i += win
        else:
            i += 1
    return dups


# Pure disfluency tokens to drop (WHOLE-WORD normalized match — never substring, per the VN
# substring-collision rule). Conservative on purpose: excludes ambiguous real words (VN "ạ"/"hả"/
# "kiểu", EN "like"/"you know") that a filler-cut could wrongly remove.
FILLER_WORDS = {
    "um", "umm", "ummm", "uh", "uhh", "uhm", "uhmm", "er", "err", "erm", "ah", "ahh",
    "hmm", "hmmm", "mm", "mmm", "eh",
    # Vietnamese disfluencies
    "ừ", "ừm", "ưm", "ừmm", "à", "ờ", "ờm", "ể", "hử", "ậ", "ừa",
}


def detect_fillers(words):
    """Standalone filler/disfluency words to remove (umm/uh/ừ/à/ờ…). WHOLE-WORD normalized match."""
    out = []
    for i, w in enumerate(words):
        if _norm(w.get("word", "")) in FILLER_WORDS:
            out.append({"start": round(float(w["start"]), 2), "end": round(float(w["end"]), 2),
                        "word": w.get("word", ""), "index": i})
    return out


def analyze(words, silence_s=1.0):
    sil = detect_silences(words, silence_s)
    dup = detect_duplicate_takes(words)
    fil = detect_fillers(words)
    return {"n_words": len(words),
            "silences": sil, "duplicate_takes": dup, "fillers": fil,
            "dead_air_total_s": round(sum(s["duration"] for s in sil), 2),
            "filler_total_s": round(sum(f["end"] - f["start"] for f in fil), 2),
            "cut_suggestions": [d["take1"] for d in dup]}


def main():
    ap = argparse.ArgumentParser(description="Talking-head footage analyzer (silence + duplicate takes)")
    ap.add_argument("words", help="path to words.json (from talking_head_transcribe)")
    ap.add_argument("--silence", type=float, default=1.0, help="silence threshold seconds (default 1.0)")
    ap.add_argument("--json", help="also write the full analysis to this JSON path")
    a = ap.parse_args()
    words = json.load(open(a.words, encoding="utf-8"))
    r = analyze(words, a.silence)
    print(f"[analyze] {r['n_words']} words | {len(r['silences'])} silences "
          f"({r['dead_air_total_s']}s dead air) | {len(r['duplicate_takes'])} duplicate take(s) "
          f"| {len(r['fillers'])} filler(s) ({r['filler_total_s']}s)")
    for s in r["silences"]:
        print(f"  · silence {s['duration']}s @ {s['start']}–{s['end']}  ('{s['after']}' … '{s['before']}')")
    for f in r["fillers"]:
        print(f"  · filler '{f['word']}' @ {f['start']}–{f['end']}")
    for d in r["duplicate_takes"]:
        print(f"  · dup take (sim {d['similarity']}): cut {d['take1']} keep {d['take2']}  — \"{d['text']}\"")
    if a.json:
        json.dump(r, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[analyze] wrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
