# -*- coding: utf-8 -*-
"""Topic → video (autonomous) — the front of the factory's OODA loop.

Closes the gap the router never had: it takes a SCRIPT, not a topic. This picks/accepts a demand-driven
TOPIC, runs the full grounded script pipeline (script_writer.generate_script: fetch→analyze→reason→plan→
write→verify — real facts, no fabrication), then hands the written narration to the normal render route.

    python scripts/topic_to_video.py --discover "SEO"          # pick a real demand topic, make a video
    python scripts/topic_to_video.py --topic "SEO audit checklist"   # explicit topic
    python scripts/topic_to_video.py --discover "SEO" --dry     # just show discovered topics, don't render

Demand comes from researcher.demand_topics (keyless Google Trends VN + YouTube autocomplete). The script
MUST come from a real LLM (topic→video can't be faked) — if none is up, it aborts instead of guessing.
"""
import os
import re
import sys
import json
import datetime
import argparse
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))


def _build_vn_fold():
    groups = {"a": "àáảãạăằắẳẵặâầấẩẫậ", "e": "èéẻẽẹêềếểễệ", "i": "ìíỉĩị",
              "o": "òóỏõọôồốổỗộơờớởỡợ", "u": "ùúủũụưừứửữự", "y": "ỳýỷỹỵ", "d": "đ"}
    m = {}
    for base, chars in groups.items():
        for c in chars:
            m[ord(c)] = base
    return m


_VN_FOLD = _build_vn_fold()


def _slug(s, n=40):
    # fold Vietnamese diacritics to ASCII first so "cách tối ưu" → "cach-toi-uu", not "c-ch-t-i-u".
    s = (s or "").lower().translate(_VN_FOLD)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:n].strip("-") or "topic")


# Produced-topic history so a DAILY batch doesn't remake the same stable top topics every run. This is a
# dedup log (distinct from factory_ledger's performance stats). Kept in the learning area, time-windowed.
_HISTORY = os.path.join(ROOT, "3_MEMORY", "learning", "produced_topics.json")


def _load_history():
    try:
        return json.load(open(_HISTORY, encoding="utf-8"))
    except Exception:
        return []


def _recent_slugs(days):
    if days <= 0:
        return set()
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    return {h.get("slug") for h in _load_history() if h.get("ts", "") >= cutoff}


def _record_produced(topic):
    hist = _load_history()
    hist.append({"slug": _slug(topic), "topic": topic, "ts": datetime.datetime.now().isoformat()})
    try:
        os.makedirs(os.path.dirname(_HISTORY), exist_ok=True)
        json.dump(hist[-500:], open(_HISTORY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[topic] history not saved ({e})")


def pick_topics(seed, n=1, fresh_days=14, days=30, hot=False):
    """Return the top `n` distinct on-domain demand topics for `seed`, SKIPPING ones produced in the last
    `fresh_days` (so a daily batch rotates through fresh topics instead of repeating the stable top). Falls
    back to recently-made ones only if there aren't enough fresh; [seed] if discovery is dry.

    hot=True → RECENCY-FIRST: lead with what broke in the last `days` (HackerNews/GitHub/arXiv engagement,
    the last30days-skill harvest) then top up with trends/long-tail — a "make videos from this week's hot
    tech news" batch. hot=False → the balanced demand_topics order (trends → recency → long-tail)."""
    rs = import_module("researcher")
    if hot:
        cands = rs.recency_topics(seed=seed, days=days, n=max(n * 2, 12))
        cands += [c for c in rs.demand_topics(seed=seed, recency=False)     # top up with trends + long-tail
                  if c["topic"].lower() not in {x["topic"].lower() for x in cands}]
    else:
        cands = rs.demand_topics(seed=seed, days=days)
    if not cands:
        print(f"[topic] discovery dry — using the seed as the topic: {seed!r}")
        return [seed]
    print(f"[topic] {len(cands)} demand candidate(s) for {seed!r}:")
    for c in cands[:8]:
        print(f"    • [{c['source']:>10}] {c['topic']}  ({c['signal']})")
    seen, deduped = set(), []
    for c in cands:                                       # dedupe within this run, preserve rank
        k = c["topic"].lower().strip()
        if k not in seen:
            seen.add(k); deduped.append(c["topic"])
    recent = _recent_slugs(fresh_days)
    fresh = [t for t in deduped if _slug(t) not in recent]
    if len(fresh) >= n:
        return fresh[:n]
    fill = [t for t in deduped if t not in fresh]          # not enough new → top up with recent ones
    if fill and fresh_days > 0:
        print(f"[topic] only {len(fresh)} fresh topic(s) (< {n}); topping up with recently-made ones.")
    return (fresh + fill)[:n]


# A guaranteed-safe fallback CTA (used only as a last resort when a stubborn off-platform CTA survives
# every rewrite — the CTA scene's only job is to say "follow SEOSONA", so replacing it is always correct).
_CLEAN_CTA = "Theo dõi SEOSONA để xem thêm nhiều nội dung hữu ích mỗi ngày."


def topic_to_script(topic, n_scenes=7):
    """Full grounded pipeline → narration text (joined scene lines). '' if no real LLM (caller aborts)."""
    sw = import_module("script_writer")
    script, vr, kf = sw.generate_script(topic, topic=topic, n_scenes=n_scenes)
    if not script or not getattr(script, "scenes", None):
        return "", vr
    # Final deterministic safety net: the rewrite loop is the primary mechanism, but if an off-platform
    # CTA (bare external domain in the CTA scene / after a visit-verb) SURVIVED every rewrite, it must NOT
    # ship — the single CTA must be "follow SEOSONA". This makes off-platform-CTA enforcement HARD on this
    # path, the same way script_writer._strip_fabricated makes the NUMBER gate hard. (Shared detector.)
    try:
        cm = import_module("content_moderation")
        scenes = script.scenes
        last_i = len(scenes) - 1
        fixed = 0
        for i, sc in enumerate(scenes):
            t = sc.get("text_vi") or ""
            if cm.off_platform_domain(t, is_cta_scene=(i == last_i)):
                if i == last_i:                          # CTA scene → replace with the canonical clean CTA
                    sc["text_vi"] = _CLEAN_CTA
                else:                                    # mid-scene → drop the sentence carrying the domain
                    keep = [seg for seg in re.split(r"(?<=[.!?])\s+", t)
                            if not cm.off_platform_domain(seg, is_cta_scene=False)]
                    sc["text_vi"] = " ".join(keep).strip() or _CLEAN_CTA
                fixed += 1
        if fixed:
            print(f"[topic] ⚠ neutralized {fixed} off-platform CTA that survived rewrites → clean SEOSONA CTA")
            vr = sw.verify(script, kf, unsourced=getattr(vr, "unsourced", False))
    except Exception as e:
        print(f"[topic] CTA safety-net skipped: {e}")
    text = " ".join((s.get("text_vi") or "").strip() for s in script.scenes if s.get("text_vi"))
    return text.strip(), vr


def make_one(topic, aspect="9:16", n_scenes=7, dry=False):
    """One topic → one video. Returns True on success, False if the writer had no LLM (skip, don't fake)."""
    print(f"[topic] → {topic!r}")
    text, vr = topic_to_script(topic, n_scenes=n_scenes)
    if not text:
        print("[topic] ✗ no script (real LLM unavailable) — skipping this topic, not fabricating.")
        return False
    print(f"[topic] script written ({len(text.split())} words, "
          f"verify {'✓' if vr.ok else '⚠ ' + ';'.join(vr.errors[:3])}).")
    if dry:
        print("\n--- SCRIPT ---\n" + text + "\n")
        return True
    import_module("workflow_router").route(text, brand="seosona", aspect_ratio=aspect,
                                           project_name=_slug(topic))
    _record_produced(topic)                               # remember it so a daily batch won't remake it
    return True


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--topic", help="explicit topic to make a video about")
    g.add_argument("--discover", metavar="SEED", help="pick a demand topic for this seed (e.g. 'SEO')")
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--scenes", type=int, default=7)
    ap.add_argument("--count", type=int, default=1, help="batch: make N videos from the top N demand topics")
    ap.add_argument("--fresh-days", type=int, default=14, dest="fresh_days",
                    help="skip topics produced within this many days (0 = allow repeats)")
    ap.add_argument("--days", type=int, default=30, help="recency window for hot/fresh tech-news discovery")
    ap.add_argument("--hot", action="store_true",
                    help="recency-FIRST: make videos from the last --days of hot tech news (HN/GitHub/arXiv)")
    ap.add_argument("--dry", action="store_true", help="only discover/write; don't render")
    a = ap.parse_args()

    topics = ([a.topic] if a.topic else
              pick_topics(a.discover, n=max(1, a.count), fresh_days=a.fresh_days, days=a.days, hot=a.hot))
    if a.topic and a.count > 1:
        print("[topic] --count is ignored with an explicit --topic (one topic → one video).")
    print(f"[topic] batch of {len(topics)}: {topics}")

    made = 0
    for idx, t in enumerate(topics, 1):
        print(f"\n===== [{idx}/{len(topics)}] =====")
        if make_one(t, aspect=a.aspect, n_scenes=a.scenes, dry=a.dry):
            made += 1
    print(f"\n[topic] batch done — {made}/{len(topics)} produced.")
    if made == 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
