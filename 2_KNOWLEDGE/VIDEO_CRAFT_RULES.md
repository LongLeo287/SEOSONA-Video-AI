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

## 8. CapCut ecosystem — harvested craft (6 repos vetted; patterns learned, NOT vendored)
Repos examined (clones in `2_KNOWLEDGE/external_toolkits/`): renezander030/capcut-cli (MIT), GuanYixuan/pyJianYingDraft
+ pyCapCut (Apache-2.0), sun-guannan/VectCutAPI (2k★), Hommy-master/capcut-mate (1.3k★), opencut-app/opencut
(60k★), mrbuslov/capcut-ai-editor (MCP). **Hard finding: there is NO free + headless way to render CapCut's
effect library** — every render path needs the CapCut/JianYing GUI (manual or fragile RPA, Windows-only) or a
PAID cloud (VectCutAPI → `open.capcutapi.top`, license-gated). So we do NOT route renders through CapCut; we
harvest the *knowledge* and apply it natively in our free/headless engine.

**ADOPTED (built):**
- **SFX de-click (afade)** — every SFX cue now gets `afade=t=in:st=0:d=0.03` (kills the hard-attack click) + a
  tail `afade=t=out` (no abrupt cut-off), durations via cached ffprobe. `native_composer._audio_dur` + the mix
  loop. Technique from capcut-cli's render filtergraph; free, headless, frame-verified (ffmpeg rc=0).
- **TEXT-EFFECT layer** — `effect_library.TEXT_EFFECTS`: **5 headline treatments** (rise · word-up · clip-wipe ·
  word-pop · drop) rotated on a DIFFERENT seed phase than transitions, so transition×text-effect form fresh
  COMBINATIONS every scene (multiplicative variety). Word recipes animate per-word `.head .w` spans (native_composer
  `_words()` wraps each word; `.head .w{display:inline-block}`). The headline is now OWNED by the text-effect layer;
  transitions animate only the kicker + component. **Frame-verified**: word-up + word-pop headlines fully settle,
  head-top spread across scenes stays ~34px (no jump), layout intact.
- **SFX + MOTION formalized into the library** — `effect_library.motion_ambient()` (glow-breathe + ghost +
  brand-blob drift; 3 blob PROFILES rotate per-video) + `effect_library.sfx_variant()` (transition-swish sequence
  rotates per-video; SFX files stay in native_composer, no dup). native_composer calls both instead of inline code.
- **New brand components (from capcut-cli patterns, re-skinned)** — `lower-third` (source/handle attribution card,
  accent bar) + `callout` (punchy accent pill = caption-pop). Frame-verified. The other capcut patterns map to
  existing: gold-title→hero, end-card & subscribe-cta→`cta` (btn param), hook-question→hero headline (no dup).
- **EFFECT LIBRARY (4th library layer)** — `4_BRAIN/effect_library.py`: a stored, extensible catalog of
  **6 transition** + **5 text-effect** + **2 overlay** + **5 exit** + **3 motion-profiles** + **8 sfx-categories**,
  with SELECTORS that **rotate per-video**
  (seeded by topic/output via a position-weighted hash) so DIFFERENT videos get DIFFERENT effect sequences —
  variety at scale, not repetition — while consecutive scenes within a video never reuse a recipe. Wired into
  `native_composer` (entrance + exit pull from the library, `_vseed`); the old inline `_entrance_tweens`/`_EXITS`
  were removed (no dup). Shows in `grow_library status` as the EFFECT layer. Grow it like the other libraries:
  add a recipe → it joins the rotation. Seek-safe GSAP only; **NO horizontal drift** (brand: content never
  slides sideways — recipes move on y/scale/opacity/clip-path only); NOT ffmpeg `xfade` (our render is ONE
  continuous seek-render, not concatenated clips). **Frame-verified** across 2 renders (different seeds →
  different sequences; all recipes resolve to rest pose, text fully visible, no black frames, render exit 0).
- **SFX sidechain-duck** — BGM dips under each SFX hit via a light SECOND `sidechaincompress` (SFX summed into a
  key; ratio 4 vs the voice-duck's 8) so SFX punch through without a pump. `native_composer` mix. Filtergraph-verified.

**BACKLOG (worth it, deferred — no-bloat):**
- **EFFECT overlays** — subtle light-leak sweep / film-grain / brand-glow bloom / flash accent (brand-tinted,
  very low opacity, rotated — NOT every cut). Add as an EFFECTS registry in `effect_library.py` + CSS overlay in
  native_composer (needs an overlay div + picker; sparse — only impact scenes).
- **SFX / MOTION library layers** — formalize the semantic-SFX pool + the ambient motions (glow-breathe,
  blob-drift, ghost-drift) and emphasis motions (bignum-pop, chart-wipe) into `effect_library.py` registries
  with rotating selectors (they already work inline; this makes them stored + rotatable like transitions).
- **More recipes** — extra transitions/text-effects as needed; each is just a new registry entry.
- **Re-skinned text templates** — capcut-cli ships 6 short-video patterns (gold-title, end-card, subscribe-cta,
  hook-question, lower-third, caption-pop). Re-color to brand (blue #2A5BDA / coral, Be Vietnam Pro, soften
  shadows for light-mode) → add as components / craft presets.
- **Talking-head reliability** — silence auto-detect (>1s gaps in word timings) + duplicate-take detect
  (Levenshtein on word runs) + multi-language subtitle translate. Algorithms portable from capcut-ai-editor /
  capcut-cli; our caption/karaoke chunking is already SMARTER (Vietnamese-grammar breaks) so caption gen = SKIP-DUP.

**SKIPPED:** ~85% of CapCut's effect catalog (anime / neon / retro / cute / dark) breaks the light-mode
professional brand. CapCut's strength is breadth (choice); ours is curation (taste).

## 9. Vertical safe-zone & alignment (9:16)
Single source of truth = the `SAFE_*` constants in `native_composer` (base 1080×1920, scaled by `vs/hs`
for other aspects via the `--sz-*` CSS vars):
- **`SAFE_SIDE=100`** · **`SAFE_TITLE_TOP=560`** (title anchor line) · **`SAFE_CONTENT_BOTTOM=1500`** (content
  must stay above the caption band; kara caption top ≈ 1544, footer ≈ 1690).
- **Content is TOP-ANCHORED** (`.scene{justify-content:flex-start}`): the kicker/title sits on the SAME line
  every scene → it never "jumps" between cuts. (Bug fixed 2026-07-01: center-anchoring made the head bounce
  ~224px scene-to-scene because the centred block's height varied; measured head-top range went 224px→46px.)
- Content sits a touch ABOVE the true frame-centre ON PURPOSE — short-form platforms (TikTok/Reels/Shorts)
  overlay their own caption + right-side button column over the bottom ~26%, so the usable stage is the upper-
  centre. Don't "fix" it to dead-centre.
- Components flow directly below the title and must not cross `SAFE_CONTENT_BOTTOM` (verified: tallest test
  scene bottom = 1394 < 1544). If a very tall component is added, cap its item count, don't lower the title.
- **Never** re-introduce a hard-coded `.scene` padding string that must be kept in sync with a `.replace()` —
  that stale-string bug silently no-op'd the non-portrait scale. Everything routes through the `--sz-*` vars.
- Verify layout with the Playwright measure pass (seek-free bounding-box read) whenever `.scene`/safe-zone
  changes: head-top spread across scenes should stay small (<~60px) and no content should cross 1500.

## 10. SKILL AUTO adoption — components + timing + non-negotiables (2026-07-03, WIRED)

Learned from `SKILL AUTO` (Remotion edit skill); ported native/free/light-brand. See
`2_KNOWLEDGE/hyperframes/craft/SKILL-AUTO-ADOPTION-2026-07.md` for the full plan.

**New scene components** (in `native_composer._component` + `component_picker` menu/validator + `spec_lint._REQUIRED`):
`concept_build` (VO-synced explainer canvas) · `comparison_grid` · `split_reveal` · `annotated_screenshot` ·
`stat_grid` (multi-stat grid) · `ratio_dots` (X/Y proportion dots) · `layer_stack` (stacked slabs) ·
`ticker_feed` (activity feed) · `org_diagram` (parent + kept/dim children). All `.ritem` seek-safe, render-verified.

**Timing passes** (`4_BRAIN/beat_timing.py`, VN-adapted): `close_gaps` (bridge sub-1.5s flicker gaps) ·
`sync_list_items` (reveal each row WHEN spoken — wired into talking-head bullets) · `zoom_plan` (score punchy
words → emphasis; wired to auto-highlight captions). ASR brand fix = `4_BRAIN/transcript_fix.py`.

**Non-negotiable lint rules** (`spec_lint.py`, advisory): coverage ≥70% · hook-visual@0.0s · beat ceiling ≤5s ·
icon safe-zone Y≤80% · flicker gap. Live: safe-zone→`lint_elements`, ceiling+flicker→talking-head b-roll track,
hook/ending/density/reason/blank-risk→`lint_scenes`/`lint_course`. Coverage is a guard that only fires on a
bare-frame timeline — our full-frame engines inherently pass it.

## Status
**Knowledge CAPTURED** (this doc) — use it now in the Gemini script prompt + scene planning + any
motion work. **Code adoption = BACKLOG** (not yet wired): the CustomEase presets need the GSAP
CustomEase plugin (extra CDN + registerPlugin) and the center-stagger needs reordering the manual
reveal indices — both touch the working render engine, so they get done deliberately with a
frame-verify, not rushed. The source repos' bigger builds (69-component catalog, scene-breakdown
engine, pacing validator) are also BACKLOG — adopt incrementally only on real need (no-bloat).

## 11. HyperFrames engine capability map (v0.7.24, mined 2026-07-03)

Our render engine (`node_modules/hyperframes`, driven by `native_composer` → `node cli render`). What we tap vs what's available — so we don't re-mine and know what's on tap.

**We USE:** `lint` (pre-render) + `render --format mp4`; our own HTML + GSAP seek-safe timeline + scene components + karaoke; light-brand; voice.mp3 audio.

**Render knobs NOW wired (env, default = current behaviour):** `SEOSONA_RENDER_QUALITY` = draft|standard|high · `SEOSONA_RENDER_GPU=1` (NVENC, off by default) · `SEOSONA_RENDER_WORKERS` = N|auto. Also real (unused): `--resolution portrait-4k` (supersample), `--crf`, `--video-bitrate`, `--fps`.

**Available but NOT adopted (with why):**
- `beats` — detects music beats → `beats/<audio>.json`. Music-sync visual cuts. NOT adopted: our reveals are SPEECH-synced (informational content), and we pick BGM at mix-time AFTER the visual render → beat-sync would need a pipeline restructure + competes with speech-sync. Reference for future rhythm-driven content.
- `validate` — runtime headless check (JS errors, missing assets, **contrast**). We run `lint` (static) only. Could add as a pre-render gate (+~10s Chrome pass) to catch light-on-light contrast; deferred (our renders verify clean).
- `snapshot` (PNG at timestamps) / `inspect` (layout overflow) / `benchmark` — we grab frames via ffmpeg already; native tools = convenience, not needed.
- composition **variables** + `--batch rows.json` — per-viewer personalized video at scale. Not our model (SEO content, not 1-per-viewer). The big engine feature we don't need.
- `data-color-grading` — per-instance video/image grade. Marginal (we have dominant-color harmony); useful only if multi-brand.
- nested compositions + relative timing (`data-start="intro + 0.5"`) — modular scene reuse. Our single-timeline index.html works; refactor not worth the risk.
- `tts` (Kokoro-82M, EN) / `transcribe` / `remove-background` / `cloud`/`lambda`/`cloudrun` — we use OmniVoice (VN) + our ASR; cloud = paid. SKIP.

**Catalog/registry:** confirmed our [[registry-blocks-are-demos]] learning — the 100+ catalog blocks are hardcoded gallery DEMOS (baked text/chrome), technique-reference not drop-in. Only `code-typing`/`code-diff` are parametric enough to re-skin IF we do code-heavy content (deferred).

## 12. Footage transitions & draw-on reveal (2026-07-08, WIRED — BSD-3 clean-room from salaheddinek/video-editing-py-script)

Two native techniques for the FOOTAGE path (not the HTML→mp4 path, which already has GSAP entrances). Clean-room, no vendored code, no new dependency (PIL+numpy+ffmpeg+playwright, all present).

**Footage transitions — `4_BRAIN/footage_transition.py`.** Physical clip-to-clip transitions (`make_transition`, `splice`, `montage`) that warp the tail frames of clip A + head frames of clip B into a **rotation** or **zoom** push, filling rotate/zoom-exposed edges by MIRRORING the frame (`mirror_pad`, np.pad reflect) instead of black bars. **BRAND RULE (non-negotiable):** content never slides sideways → only `zoom` + `rotate` kinds exist (no translation). Use as an occasional accent, not every cut.
- **Where it plugs in:** the talking-head b-roll path only. Author a b-roll entry with `"montage": [src1, src2, …]` → talking_head_edit resolves the sources, builds ONE dynamic montage clip (zoom/rotate joins, kinds alternate) via `footage_transition.montage`, and uses it as a single `full`-mode b-roll source. No filter-graph surgery — the montage is one clip that flows through the existing overlay. Optional `"trans_frames"` (default 15) per join.
- `mirror_pad` is reusable for Ken Burns / avatar_motion edge cases (fill exposed borders by reflection).
- The HTML/native_composer path is a single hyperframes pass (no clip concat) — footage transitions do NOT apply there.

**Draw-on icon reveal — `4_BRAIN/svg_draw_on.py`** = the free native stand-in for the PAID GSAP DrawSVGPlugin. Progressive stroke reveal via CSS `stroke-dashoffset` + the browser's exact `getTotalLength()`. Because native_composer renders through hyperframes which SEEKS the timeline per frame, a wall-clock CSS/GSAP animation is NOT captured — so the reveal is BAKED to a transparent qtrle `.mov` the same way `element_maker.render_element_clip` does (a paused animation stepped by a deterministic `window.__seek(ms)`, playwright screenshot per frame). Seek-safe by construction; composites over footage like any element clip.
- **Where it plugs in:** the element layer. New element type `draw_icon` in `element_maker` (a lone Lucide icon that draws itself on, stroke = brand role colour, padded with CLIP_INSET so the standard `x-CLIP_INSET` overlay math holds). `element_picker` emits ONE `draw_icon` as a premium opener (the first icon concept; `draw_first=True` default) — the rest stay `icon_tile`. Lucide stroke icons are the ideal input.

**Subject-aware overlay placement — `2_SKILLS/element_maker/subject_zones.py` (2026-07-08, WIRED).** Clean-room of the IDEA behind bachdyon/video-automator-skills `overlay-subject-placement` (PolyForm Noncommercial → technique only). Where that skill calls a PAID vision-LLM per frame, this locates the subject offline with zero new deps: the speaker is WHERE THE MOTION IS, so per-pixel **temporal variance** across a few sampled frames (ffmpeg+numpy) bounds the subject region. `detect_subject_box(video,W,H)` → (x,y,w,h) or None; `safe_zones(W,H,box,tile_w)` ranks candidate slots by row (TOP first) then horizontal distance from the subject (side gutters beat centre) — reel convention, never the caption band; `clamp_to_safe(...)` enforces the hard safe-area (1080×1920 → top100/left100/right100/bottom200). Wired into talking_head_edit: computes the box from the footage, feeds subject-aware `zones` to `element_picker.pick_elements`, and clamps EVERY element (hand + auto). Degrades to the fixed top-band when the subject can't be located (static footage / no ffmpeg) — no regression. Opt out `subject_aware:false`.
