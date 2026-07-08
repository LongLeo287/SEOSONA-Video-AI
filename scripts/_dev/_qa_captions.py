# -*- coding: utf-8 -*-
"""QA caption RULE #1 + timing alignment on diverse scripts (fast, no voice)."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import news_video_standards as nvs

CASES = {
 "numbers":      "Google chiếm 81% thị phần, Bing 11%, AI Search 8% trong năm nay.",
 "english-terms":"Dùng SEO và AI cùng ChatGPT để tối ưu content theo E-E-A-T.",
 "ratio-slash":  "Hỗ trợ 24/7 với hơn 1.000 khách hàng mỗi tháng.",
 "short":        "SEO thời AI đã khác.",
 "long-dense":   "Khi người dùng hỏi thẳng trợ lý AI thay vì lướt mười kết quả trên Google thì cách làm SEO buộc phải thay đổi hoàn toàn từ gốc.",
 "punctuation":  "Quan trọng nhất: nội dung phải đủ uy tín, đáng tin, và rõ ràng!",
 "acronym-heavy":"GEO, AEO và SEO là ba khái niệm khác nhau trong marketing.",
 "mixed":        "Hơn 60% truy vấn giờ có câu trả lời AI; bạn cần schema và backlink chất lượng.",
}

def simulate_perfect_asr(plan):
    """ASR that returns exactly the tts_words with monotonic synthetic timings."""
    out=[]; t=0.0
    for w in plan.tts_words:
        d=max(0.12, 0.06*len(w)); out.append({"word":w,"start":round(t,3),"end":round(t+d,3),"duration":round(d,3)}); t+=d+0.03
    return out, t

fails=0
for name, txt in CASES.items():
    plan = nvs.prepare_tts_script(txt)
    dw, tw, mp = plan.display_words, plan.tts_words, plan.tts_word_to_display_index
    # structural checks
    ok_map = len(mp)==len(tw) and all(0<=i<len(dw) for i in mp) and set(mp)==set(range(len(dw)))
    asr, dur = simulate_perfect_asr(plan)
    aligned = nvs.align_tts_boundaries_to_display_words(plan, asr, dur)
    words_out = [a["word"] for a in aligned]
    rule1 = (words_out == dw)                      # captions == DISPLAY words, not phonetic
    mono = all(aligned[i]["start"]<=aligned[i+1]["start"] for i in range(len(aligned)-1))
    nooverlap = all(aligned[i]["end"]<=aligned[i+1]["start"]+0.001 for i in range(len(aligned)-1))
    used_real = (len(aligned)==len(dw)) and rule1   # real-align path (not estimate fallback)
    expand = round(len(tw)/max(1,len(dw)),2)        # spoken words per display word
    status = "PASS" if (ok_map and rule1 and mono) else "FAIL"
    if status=="FAIL": fails+=1
    print(f"[{status}] {name:14} dw={len(dw):2} tw={len(tw):2} x{expand} | RULE#1={rule1} map={ok_map} mono={mono} noOv={nooverlap}")
    # show a sample of display vs spoken to eyeball RULE #1
    samp=[f"{dw[i]}→{plan.tts_words[mp.index(i)] if i in mp else '?'}" for i in range(len(dw)) if dw[i]!=(plan.tts_words[mp.index(i)] if i in mp else dw[i])][:4]
    if samp: print(f"        lexicon maps: {', '.join(samp)}")
print(f"\n=== {len(CASES)-fails}/{len(CASES)} PASS ===")
