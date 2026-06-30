---
name: video-seo-metadata
description: >
  Use this skill when the user wants to "write the YouTube title/description/tags",
  "SEO metadata for this video", "what should I title/tag this", "caption for TikTok/Shorts",
  or after a video is rendered and needs platform-ready publishing text.
  Produces a keyword-targeted title + description + tags + hashtags for a video — FREE/LOCAL
  (no paid SEO API). Do NOT use for: writing the video SCRIPT (use the Gemini script path in
  make_video / content-strategy domain skill), or finding trending topics (use video-discovery).
metadata:
  author: SEOSONA
  version: "1.0"
  license: internal
  provenance: adapted from every-app/open-seo's keyword-research workflow PATTERN — its API
    tools (DataForSEO) were REJECTED as paid; only the free/local workflow shape was kept.
---

# Video SEO Metadata — publish-ready text (free/local)

Turns a video's topic into the text platforms rank/recommend on. No paid keyword API: it uses
the topic's own real terms + SEOSONA's copy craft. (open-seo's DataForSEO tools were skipped —
paid; this keeps only the free workflow.)

## Reference files
| File | For |
|------|-----|
| `9_PROMPTS/MASTER_VIDEO_SPEC.md` | the SEO + title-formula section, brand tone |
| `2_KNOWLEDGE/domain_skills/copywriting/SKILL.md` | hook/headline craft |
| `2_KNOWLEDGE/domain_skills/content-strategy/SKILL.md` | searchable-content + keyword intent |
| `8_WORKSPACE/<name>/caption.txt` | make_video already writes a VN hook + topic hashtags — extend it |

## Inputs
- Topic source: GitHub repo data / news headline / SEO topic (Vietnamese audience).
- Platform: YouTube (long) · Shorts/TikTok/Reels (short). Default: both.
- Target keywords: derive from the topic's REAL terms (repo name, language, domain, the 2–3
  obvious search phrases a VN viewer would type). No invented stats.

## Output (JSON-ish; Vietnamese, brand voice)
```
title       : ≤60 chars, keyword near the front + a benefit/curiosity hook (not clickbait-fake)
description : 120–200 words — 1-line hook, what+why, key points, CTA "Theo dõi SEOSONA", links
tags        : 8–12 lowercase keywords (repo/lang/domain/category + 2–3 search phrases)
hashtags    : 5–8 (#SEOSONA #congnghe #AI + topic-specific)
thumb_text  : 2–4 word on-thumbnail phrase
```

## Keyword intent (classify the search pull — pick ONE per video)
- **Informational** ("how to / what is / cách / là gì") → explainer, top-of-funnel.
- **Navigational** (brand/product name) → awareness, discovery.
- **Commercial** ("vs / alternative / so sánh / thay thế") → comparison, positioning.
- **Transactional** ("free / download / tải / dùng thử") → lead-gen.
SEOSONA tech videos usually mix **informational + commercial**; the title plants the intent keyword.

## Keyword derivation (free/local — no API)
1. **Seed** from the topic's REAL terms: repo name, language, domain, category. Ask "what would a
   VN viewer TYPE to find this?" (e.g. repo+lang → "ten-repo Python", tool+usecase, problem+solution).
2. **Expand**: variations (free/open-source), long-tail (+audience), comparison ("X alternative"), guide intent ("… hướng dẫn").
3. **Map intent** (above) → keep 1–2 that fit the video.
4. **Dedup/priority**: keep specific 2–4-word + clear-intent; drop brand-only / too-broad / off-domain.
5. **Front-load** the keyword in the first 1–2 words of the title.

## Formulas (exact)
- **Title** ≤60 (Shorts ≤50): `[1–2 word keyword] + [benefit/curiosity]`. Keyword first; one idea; no ALL-CAPS; no fake numbers.
- **Description** 120–200w, 4 short ¶: hook line · what+why (with REAL numbers: stars/lang/license) · key points · CTA "Theo dõi SEOSONA" + link. No AI-filler ("delve/explore"), no unverified stats.
- **Tags** 8–12 lowercase: 1–2 category + 3–5 topic + 2–3 niche/comparison.
- **Hashtags** 5–8: always `#SEOSONA #congnghe #AI` + topic-specific.

## Rules (brand + SEO)
- Vietnamese (system files English; this is CONTENT → Vietnamese). English tech terms kept as-is
  in display (GitHub, AI) — pronunciation is the voice layer's job, not here.
- Front-load the keyword; one idea per title; no ALL-CAPS, no fake numbers.
- Reuse the topic's real data (stars, language) — never invent metrics.

## Execution Contract (non-negotiable)
- Keywords come from the topic's REAL terms only — forbidden to fabricate volumes/metrics
  (we have no keyword API; do not pretend to).
- **Fail-closed:** if the topic is too thin to derive keywords, ask for the topic/keywords —
  don't emit generic filler.
