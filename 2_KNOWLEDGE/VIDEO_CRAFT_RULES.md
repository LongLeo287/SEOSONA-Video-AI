# Video Craft Rules — pacing, scene-tags, motion (harvested knowledge)

Concrete craft knowledge mined from `feicaiclub/video-spec-builder` + `greensock/gsap-skills`
(both REFERENCE repos — the WHOLE wasn't adopted, but these specifics were). Use this when
writing the Gemini script prompt, planning scenes, or extending `native_composer` motion.
Brand-locked: light-mode, blue `#2A5BDA` / coral `#E2724D`, Be Vietnam Pro.

## 1. Scene tags (vocabulary for what each scene DOES)
`hook` (grab, ≤3s, must be scene-0/1) · `data` (number/stat/rank) · `concept` (define/explain) ·
`versus` (A vs B / before-after) · `demo` (steps/how) · `flow` (sequence) · `emotion` (story/value) ·
`structure` (hierarchy) · `cta` (follow/try) · `bridge` (transition, ≤15% of scenes) · `summary`.
→ Tag each scene; drives pacing + component choice.

## 2. Pacing archetypes (pick by platform/length)
| Archetype | sec/scene | scenes/min | whitespace | use |
|---|---|---|---|---|
| **hook** (Shorts/TikTok 30–60s) | 0.8–2.0 | 30–60 | <5% | news/hype |
| **tutorial** (YouTube) | 2.0–5.0 | 15–30 | 10–15% | how-to/explainer |
| **doc** (brand/long) | 3.0–8.0 | 8–15 | 20–30% | story/depth |
Hook must land in the first 3s; never open on a logo-only / >1s black fade.

## 3. Validation rules (cheap quality guards)
- **Visual variety:** same component used **≥4×** in one video → monotony warning (vary it).
- **Hook first:** a `hook`-tag scene within the first 3s.
- **bridge ≤15%** of scenes (don't dilute density).
- One idea per title/scene; numbers spoken phonetically (voice layer), displayed normally.
- (We already enforce display≠spoken via the nvs lexicon + script_schema.)

## 4. Tag → component (suggestion)
hook→bignum/poster · data→chart/stats/bignum · concept→compare/feature · versus→compare ·
demo/flow→steps/terminal · structure→steps · cta→cta · summary→badges/quote.

## 5. Motion / easing (GSAP, seek-safe only)
Our render seeks a PAUSED gsap timeline → only deterministic tweens (`tl.to/from/fromTo/set`,
stagger, ease, transform/opacity). NO ScrollTrigger / matchMedia / tl.call / CSS @keyframes.

**Easing menu (when to use):**
- entrances: `power2.out` / `power3.out` / `back.out(1.4–1.7)`
- exits: `power2.in` (snappy, don't linger)
- continuous (glow/blob breathe): `sine.inOut`
- impact (number lands): `expo.out` (≤1×/scene)
- AVOID: `elastic`, `bounce` (dated/playful — off-brand for news).
- ≤3 unique eases per scene (variety ≠ chaos).

**Brand CustomEase presets** (register once; cubic-bezier, not gimmicky):
`pop-brand .25,.46,.45,.94` · `glide-editorial .13,.27,.80,.98` · `whoosh .34,.1,.68,.55` · `settle .68,.55,.265,.55`.

**Stagger choreography** (instead of uniform): `from:"center"` = editorial (eye lands center→out) ·
`from:"edges"` = architectural (fill→center) · `from:"start"` = default. (`from:"random"` only for playful, NOT news.)

**Data-driven motion** (`gsap.utils`, pure/seek-safe): `mapRange` (value→scale/hue), `snap` (discrete steps),
`distribute({from:"center"})` (weight by position), `clamp`. Use only on data components (stats/compare), never captions.

## Status
**Knowledge CAPTURED** (this doc) — use it now in the Gemini script prompt + scene planning + any
motion work. **Code adoption = BACKLOG** (not yet wired): the CustomEase presets need the GSAP
CustomEase plugin (extra CDN + registerPlugin) and the center-stagger needs reordering the manual
reveal indices — both touch the working render engine, so they get done deliberately with a
frame-verify, not rushed. The source repos' bigger builds (69-component catalog, scene-breakdown
engine, pacing validator) are also BACKLOG — adopt incrementally only on real need (no-bloat).
