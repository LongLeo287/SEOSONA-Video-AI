# SOP — Repo vetting before ingesting into SEOSONA Video

> This is the **DECIDE** stage of the bigger [`SELF_IMPROVEMENT_LOOP.md`](SELF_IMPROVEMENT_LOOP.md)
> (discover→analyze→security→decide→adapt→build→verify→wire→record). Use it together with that loop.

There are many candidate repos. Do NOT ad-hoc clone-and-copy. Every repo passes this gate
first. Aligned with SEOSONA OS's UAP pipeline (`~/.seosona/docs/03_uap_pipeline.md`:
finder → auditor → security → assimilator → creator; factual source analysis; STAR_THRESHOLD
500; tier/route) but lightweight for a single project.

## Two routes
- **Bulk / unknown repos:** route through **SEOSONA OS UAP** (it clones, security-scans, does
  factual source analysis, emits Knowledge Items, and tiers them). SEOSONA Video then pulls the
  English KI via `scripts/inject_os_capabilities.py`. Use this for the large inventory.
- **A specific repo you already trust** (named source): use the 7-step checklist below directly.

## 7-step checklist (analyze → classify → check → ingest)
1. **Relevance** — does it serve SEOSONA Video's domains (video/HyperFrames, SEO, marketing,
   content, design/UX, VN voice)? If not → skip. Classify it: knowledge | skill | tool | engine.
2. **License** — must be permissive (MIT / Apache-2.0 / BSD / CC). Record it. No license / GPL
   that conflicts → don't vendor; reference by link only.
3. **Quality signal** — community-vetted: stars (OS uses ≥500), recent commits, real content
   (not a stub/marketing README). Read 1–2 files to confirm depth.
4. **Dedup (rule 2)** — does SEOSONA already have this capability? (e.g. animation → we have
   `2_KNOWLEDGE/hyperframes/craft/`; ASR/voice → VieNeu/PhoWhisper). If yes → don't duplicate;
   extend the existing one.
5. **Security (rule 4)** — no obfuscated code, no network-exfil, no secrets. For code we'll run,
   skim it; for docs/SKILL.md, ensure no prompt-injection ("ignore previous instructions…").
6. **Ingest location (rule 5)** — knowledge → `2_KNOWLEDGE/<area>/`; reusable skill →
   `.agents/skills/` or `2_KNOWLEDGE/domain_skills/`; engine code → `5_FRAMEWORK/`. Keep it in
   ONE place; don't scatter.
7. **Connect + attribute (rules 1, 3)** — English only (translate if needed; VN stays only in
   video content); add an `INDEX.md`/README with **source + license + date**; link it from the
   relevant playbook (`MASTER_VIDEO_SPEC`, `DESIGN.md`, a craft index) so it's actually used.

## Record every ingestion
Append a one-liner to `2_KNOWLEDGE/INGESTION_LOG.md`: date · repo · license · what was taken ·
where it landed · why. (Audit trail = trust.)

## Examples already done this way
- `boraoztunc/skills` (Apache-2.0) → 13 domain skills in `2_KNOWLEDGE/domain_skills/` (SEO/copy/design).
- `nexu-io/open-design` (Apache-2.0) → HyperFrames craft in `2_KNOWLEDGE/hyperframes/craft/`.
- `claude-code-video-toolkit` (MIT) → WPM pacing + refs in `2_KNOWLEDGE/external_toolkits/`.
- Rejected (over-engineer / not a fit): ToolJet, Prometheus, firecrawl, browser-use.
