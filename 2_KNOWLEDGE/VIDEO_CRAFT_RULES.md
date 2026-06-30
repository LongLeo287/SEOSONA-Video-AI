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

## 6. Static-CSS craft (from nicobailon/visual-explainer, MIT — SEEK-SAFE picks only)
Static CSS = always seek-safe (no animation timing). Adoptable:
- **Depth tiers** for component cards (light-mode shadows): `elevated` (0 2px 8px) for primary,
  `hero` (0 4px 20px + faint brand tint) for the focal stat, flat for reference. Improves hierarchy
  with zero new components.
- **Overflow guard:** add `min-width:0` to grid/flex children (stops content-overflow on narrow
  layouts) — a cheap base-reset win.
- **Scene-tag label:** small uppercase mono label + colored dot (`::before`) to badge a scene's tag
  (hook/data/...) using the scene-tag colors.
⚠️ **REJECTED (agent mislabelled it "seek-safe"):** the `--i` staggered fade via **CSS @keyframes +
animation-delay**. CSS @keyframes run in WALL-CLOCK, NOT synced to our paused-GSAP seek → would
flicker/desync per captured frame. Our stagger MUST stay GSAP tweens. (Same reason we use gsap, not
CSS @keyframes, for the blobs.) Mermaid zoom / slide-engine = backlog (interactive, not for render).

## 7. Hooks & narrative structure (from calesthio/OpenMontage, AGPL — patterns learned, not vendored)
Used by `_gemini_outline` (Stage 1) to vary the arc per topic instead of one fixed template.

**Hook patterns (scene 1 — pick the one the facts support):**
- **Số liệu bất ngờ** — "[con số phản trực giác]. Vì sao?"
- **Lật ngộ nhận** — "Bạn nghĩ [X]. Thực ra [Y]."
- **Tính mới** — "[Thứ này] vừa thay đổi [lĩnh vực]."
- **Câu hỏi tò mò** — "Vì sao [điều ai cũng gặp] lại xảy ra?"
- **So sánh tương phản** — "[A] mất [nhiều]. [B] chỉ [ít]."
- **Góc nhìn ít ai nói** — "Điều về [chủ đề] mà không ai giải thích."
- NEVER: "trong video này…", chào mở màn dài, logo-only >1s.

**Narrative structures (pick by topic, don't always use the same):**
giới-thiệu-dự-án · vấn-đề→giải-pháp · kể-bằng-số-liệu (stat-heavy) · so-sánh A/B · tiến-trình/timeline.
→ Mỗi video chọn 1 cho hợp → tránh cảm giác công thức (đúng than phiền "video giống nhau").

**Climax/điểm-nhấn:** mark 1 hero scene (giữa-cuối) → giữ lâu hơn + 1 hiệu ứng nhấn (chưa wire vào render — BACKLOG: `hero_moment` flag trong native_composer).

**From OpenMontage = REFERENCE/BACKLOG (not built — over-build for a solo 1-pipeline factory):** declarative pipeline-manifests + stage-director skills + tool-registry/selector + checkpoint-resume + executable-playbook YAML + 5-aspect scene grammar + CHAI prompt-oversight. Clone at `2_KNOWLEDGE/external_toolkits/OpenMontage` for reference if we ever scale to multiple video pipelines.

## Status
**Knowledge CAPTURED** (this doc) — use it now in the Gemini script prompt + scene planning + any
motion work. **Code adoption = BACKLOG** (not yet wired): the CustomEase presets need the GSAP
CustomEase plugin (extra CDN + registerPlugin) and the center-stagger needs reordering the manual
reveal indices — both touch the working render engine, so they get done deliberately with a
frame-verify, not rushed. The source repos' bigger builds (69-component catalog, scene-breakdown
engine, pacing validator) are also BACKLOG — adopt incrementally only on real need (no-bloat).
