# Domain Skills — SEO · Marketing · Content · Design/UX

Curated, community-vetted domain knowledge for SEOSONA Video so its scripts, headings, CTAs,
and on-screen design are grounded in real expertise — not guesswork. Each folder is a
self-contained `SKILL.md` (deep domain knowledge, Claude-Code-compatible).

## Source & license
Ingested 2026-06-29 from **boraoztunc/skills** (github.com/boraoztunc/skills, Apache-2.0;
the `ogilvy` skill is MIT, sourced from David Ogilvy's books). Kept close to upstream so they
stay diffable. Found via a community search after the repo-inventory proved thin on domain
knowledge (it is tool/agent-heavy, not marketing/design-knowledge-heavy).

## What's here (19 skills)
**SEO**
- `seo-audit/` — technical + on-page SEO audit methodology (411 lines)
- `programmatic-seo/` — building pages at scale to target keywords
- `schema-markup/` — structured data for rich results / AI citation
- `geo-aeo/` — Generative/Answer-Engine Optimization: get CITED by ChatGPT/Gemini/AI-Overviews (2026
  discipline). answer-first, RAG-chunk-ready, llms.txt, entity trust. (from amplifying-ai/awesome-GEO, CC0, 2026-07-02.)

**Content & copywriting**
- `copywriting/` — conversion copywriting framework (homepage/landing/pricing/CTA)
- `content-strategy/` — content planning, topic clusters, intent
- `copy-editing/` — editing for clarity/voice (447 lines)
- `ogilvy/` — David Ogilvy's advertising principles ("copy that sells")
- `stop-slop/` — anti-AI-slop: how to write copy that doesn't read like a machine

**Marketing / conversion**
- `page-cro/` — conversion-rate optimization for a page
- `competitor-alternatives/` — competitive positioning / "alternatives" content
- `marketing-psychology/` — named persuasion levers (cognitive biases + mental models) for a 45–60s
  short: pick ONE HOOK lever + ONE CTA lever, each riding a REAL fact. (from `coreyhaines31/marketingskills`,
  MIT, 2026-07-02.) Paired with `copywriting/references/short-form-structures.md` (4 named hook types + Story-Arc/POV).

**Design / UX**
- `web-design-guidelines/` · `make-interfaces-feel-better/` · `frontend-design/` (boraoztunc)
- `design-system/` · `brand/` · `ui-styling/` · `banner-design/` (from nextlevelbuilder/ui-ux-pro-max-skill, MIT)
  — visual systems, brand identity, styling, and social/thumbnail banner craft.

(Animation/motion skills from upstream — gsap/anime/lottie — were NOT ingested: SEOSONA already
has the HyperFrames craft library at `2_KNOWLEDGE/hyperframes/craft/`.)

## How SEOSONA Video uses this
These inform the **content + brand** of every video. When writing a script or planning scenes:
- pull a HOOK / CTA from `copywriting` + `ogilvy`; sanity-check it against `stop-slop`;
- choose SEO topics/angles with `seo-audit` + `content-strategy` + `programmatic-seo`;
- keep on-screen design honest with the design/UX skills + the brand contract
  (`7_ASSETS/brand/SEOSONA/DESIGN.md`).
The pre-render `content_moderation` gate + the `MASTER_VIDEO_SPEC` playbook remain the rules;
these skills are the craft behind them.

## Further reading (reference only — NOT vendored)
These are curated link-collections with **no license file**, so per `6_SOP/REPO_VETTING_SOP.md`
(step 2) they are referenced, not copied into the repo:
- SEO resources — https://github.com/awesomelistsio/awesome-seo · https://github.com/teles/awesome-seo
- UI/UX resources — https://github.com/kevindeasis/awesome-ui
- Digital marketing — https://github.com/paulbradish/awesome-digital-marketing
- Agent-skills catalog (1000+, incl. Corey Haines marketing stack) — https://github.com/VoltAgent/awesome-agent-skills
  (MIT, but a pointer-list with no SKILL.md to vendor → mine it by hand when a specific skill is needed)

Related: [[master-video-spec]] · [[design-system-and-craft]] · `9_PROMPTS/MASTER_VIDEO_SPEC.md`
