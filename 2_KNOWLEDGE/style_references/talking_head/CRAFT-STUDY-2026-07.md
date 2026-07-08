# Talking-Head Craft Study — 9 reference reels (2026-07)

Craft analysis of **9 real Vietnamese/EN talking-head shorts** (`D:\SEOSONA AI\video talking heads`, all
9:16 1080×1920, 28–185 s) to enrich the **footage/talking-head engine** (`scripts/talking_head_edit.py`,
`scripts/course_video.py`; skill `.agents/skills/talking-head-video-editor`). Method: contact sheets
(`scripts/extract_scene_sheets.py` → `8_WORKSPACE/talking_head_study/`, mirrored in `./sheets/`) → 3
parallel analyst agents → this synthesis.

**Direction (same as the card-video study):** learn the CRAFT — 3-zone layout, karaoke keyword highlight,
progressive-reveal cards, semantic color roles, hook discipline — but keep the **SEOSONA LIGHT brand**. The
sources are dark/neon; drop the palette, keep the structure/motion/meaning. Dark→light mapping is in §6.

Videos studied: V1 "10 Bộ Preset" (editing) · V2 "DeepSeek V4 free" · V3 "API Key Free cho Hermes"
(tutorial) · V4 "Raw BĐS" · V5 "Selling Low Ticket" (EN) · V6 "Test hiệu quả AI" (agent tutorial) · V7
"Show kỹ năng edit" · V8 "Ngành nào HOT" (185 s essay) · V9 "Vận hành cty 1 mình bằng AI agent".

---

## 1. The universal shape — 3-zone vertical

Every reel resolves to the same vertical grammar (the strongest cross-cutting find):

```
┌─────────────────────────┐  TOP BAND  — section/eyebrow pill, header card, or floating
│  ● SECTION PILL / CARD   │             mockup/screenshot. Information lives HERE, above the face.
│                          │
│      [ SPEAKER ]         │  MIDDLE    — centered, medium close-up (chest-up), consistent
│   centered · mic low     │             headroom. A visible handheld/podcast mic low-center is a
│                          │             recurring "authenticity" signal — captions route to clear it.
│   ▁▁▁ karaoke caption ▁▁ │  BOTTOM    — one karaoke caption line, lower third / safe zone.
└─────────────────────────┘             NEVER over the mouth.
```

- Speaker is **centered** in all 9 (not the rule-of-thirds off-center you'd use in 16:9). Medium close-up.
- **Overlays never cover the face/mouth.** Top band and bottom band do the work; the mid stays clean.
- Simpler reels are **2-zone** (speaker + floating caption, no top band); premium reels (V3/V6/V9) run the
  full **3-zone** with a persistent top card band. → 3-zone is the default premium template; 2-zone the light one.

Engine status: `course_video.py` **already implements 3-zone** (top cards / speaker / bottom karaoke). The
plain `talking_head_edit.py` is 2-zone (footage + cards + caption). ✓ Core layout exists.

---

## 2. Captions — karaoke keyword highlight (universal)

All 9 highlight the **important word**, not just render a static line:

- **Per-word active-word karaoke:** current spoken word flips to an accent color; rest of line white
  (V8 orange live-word; V9 green/yellow; V2/V3 green+yellow). This is the retention device.
- **Keyword (semantic) highlight beyond karaoke (V6/V8):** the *SEO/topic keyword* is colored even when
  not the live word — highlight marks MEANING, not only timing. → caption color should be driven by a
  **keyword list + role**, layered on top of karaoke timing.
- **Legibility plate:** over busy/neon backgrounds, text sits on a **semi-transparent dark pill** (V2/V3/V6/V9).
  Over clean shots, floating text with stroke/shadow (V1/V4/V5).
- **Chunk size scales with energy:** fast EN promo (V5) = 1–2 words/frame; VN talk (V4/V6/V8) = 3–7 words.
- **Placement:** true **bottom safe zone** with pill (V2/V3/V6/V9) OR **floating mid ~30–40 % up** over the
  chest, above the mic (V1/V4/V5/V7). Offer both.

Engine status: ASS karaoke `\k` + keyword-accent already in the skill (`keywords` must match transcript). ✓
Karaoke + keyword-accent exist. **GAP:** semantic keyword highlight independent of the live word; a
switchable "bottom-pill" vs "floating-mid" placement.

---

## 3. Cards — progressive-disclosure is the primary graphic (not b-roll)

The biggest lesson: **variety comes from the overlay/card layer, not from cutting away.** V8 and V9 (the two
longest, 185 s / 95 s) have **almost no b-roll** — a static talking head stays engaging purely through cards
that **reveal and update**:

- **Persist-and-grow list/panel cards.** The same neon-bordered card stays up ~4–6 s and **reveals rows
  one at a time** as narration advances (V2 bullets fade in; V6 header + 2–3 bullets; V9 org panels build
  role-by-role). Cheaper and more coherent than a new full-screen graphic per beat.
- **State changes on the card:** checkmarks flip done, a **progress bar animates** through steps
  (V9 CEO-agent checklist 1→2→3→4 with ✓ + progress). → cards need a *state* (todo/doing/done), not just text.
- **Semantic border color = role** (V6 is the clearest): **gold = claim/topic · blue = reassurance ·
  green = positive/optimize · red/magenta = warning · cyan = structure/system.** Border color carries meaning.
- **Section / eyebrow pill + circled number** (V8: `● XU HƯỚNG` … `① TƯ VẤN LUẬT / ② KẾ TOÁN`) — a persistent
  "where am I" chapter marker for long essays, auto-generatable from script section headings.
- **Step-badge** for tutorials (V3: `BƯỚC 1..4` top-left, held for the whole step) — orients the viewer
  through a how-to. Strongly worth templating.
- **Next-episode teaser card** (V3/V6: "PHẦN 2 SẮP RA", "VIDEO SAU: KẾT QUẢ & CHI PHÍ") — a close-out variant.
- **Negation / checklist motif** (V5): icon tiles with **red ✕ ("not this")** vs **green ✓ ("do this")** —
  powerful for "avoid X, do Y" scripts.
- **Reasoning line** (V8): a small secondary line with an arrow, e.g. `DN 1 người bùng nổ → nhu cầu cao hơn`,
  above the main caption on point-making beats.

Engine status: `course_video` cards = `header / bullet(sequential reveal) / stat / term`, accents cyan/violet/
gold/green. ✓ header + sequential-reveal bullets + accents exist. **GAPs to build (priority order):**
1. **card state** (todo/doing/done ✓ + progress bar) on bullet/checklist rows — the #1 device.
2. **semantic border-color by role** (map to light brand, §6) instead of free accent choice.
3. **step-badge** template (`BƯỚC N` persistent top-left).
4. **section/eyebrow pill + circled number** chapter marker for long videos.
5. **negation tile** (✓/✕ on icon rows) + **next-episode teaser** card + **reasoning arrow line**.

---

## 4. Showing an artifact (tool / screenshot / deliverable)

- **PiP card over the face** (top band): artifact floats top, speaker stays visible below (V2 pricing table,
  V1 phone mockup). The "glance at the proof, keep the human" move.
- **Presenter-on-top / screen-rec-below split** for demos (V3, V6): head shrinks to a top strip, the app UI
  fills the lower ~55 %. The tutorial pattern — screen-rec is ~half the runtime for how-tos.
- Screenshots are almost always a **framed rounded "device mockup"** on a branded card, rarely raw full-bleed.
- **"Show the noun" loop:** each named tool/deliverable triggers a cutaway (motion-graphic icon *or* screen-rec),
  then back to head. Head → proof → head is the backbone for demo/tutorial content.
- **Deliverable-as-object** (V7): the offer is a physical object near the hand — mini "Raw 1/2/3" thumbnails +
  a folder icon "20+ Raw Footage" composited into the open palm. Concrete, persuasive.

Engine status: b-roll spec `full` | `pip` exists in `course_video`. ✓ both modes exist. **GAP:** the
"framed device-mockup" wrapper for screenshots; auto-cutaway on named tools (couples to script keywords).

---

## 5. Hooks — no cold open (first 1–3 s)

Not one reel opens on "face + hi". The first 1–3 s always carries a **promise, a number, a proof, or a prop**:

- **Proof artifact:** V7 opens on a client DM screenshot ("what's your price for one video"); V2 on the
  DeepSeek logo + "đang **free**".
- **Bold claim/curiosity title:** V8 "Ngành nào sẽ **HOT**?"; V9 neon "MỘT MÌNH · TỰ ĐỘNG · 24/7"; V6
  "CÔNG TY MỘT MÌNH TAO".
- **Stat hook:** V5 opens on "$30,000" (cyan, underlined).
- **Prop-in-hand:** V4 holds up a phone showing the footage.
- The **payoff is shown immediately**, not teased — finished result / logo / "gần như 0 đồng" in frame 0.

This matches the faceless engine's **hook-at-frame-0** rule ([[master-video-spec]]). → talking-head briefs
must specify a hook element (stat / prop / claim card / proof screenshot) rendered in the first card + caption.

---

## 6. Dark → LIGHT translation (keep craft, keep brand)

The references are dark/neon; SEOSONA is **light-only** ([[brand-colors-light-only]], [[design-system-and-craft]]).
Translate the *meaning*, not the look:

| Reference (dark/neon) | SEOSONA light equivalent |
|---|---|
| Neon glow border on dark glass card | **Light glass card** (white/mist fill, soft shadow `0 8px 40px rgba(15,23,42,.10)`), **colored 2px border + tint** by role |
| Semantic accent = gold/cyan/green/red | **Role→brand hue** ([[brand-colors-light-only]] ROLES): topic=blue `#2A5BDA` · emphasis=coral `#E2724D` · confirmed/positive=green `#16A34A` · warning=amber `#D97706` · info/structure=slate `#3A4A6B` |
| Live-word karaoke = orange on white | Live word = **coral `#E2724D`**; keyword = **blue**; done/positive = **green**; base = ink `#0F172A` |
| Dark caption pill for contrast | Light caption: ink text on **white/mist pill** (or the brand navy karaoke pill `#16224A` already used) |
| Purple/green ambient room wash | Real footage as-is; overlays stay light — do NOT darken the footage to fake neon |

The two-accent semantic logic maps 1:1 to the ROLE system already built for the card engine
([[template-craft-study]] `brand_kit.ROLES`) — reuse it so caption highlight + card border + icon tint all
come from ONE role map. That is the through-line between the two studies.

---

## 7. Reusable rule list (drop-in for the editor skill)

1. **3-zone**: top card band · centered medium-CU speaker + mic · bottom karaoke. Never cover the mouth.
2. **Karaoke keyword highlight** every caption: live word in coral, SEO keyword in blue, done/positive in
   green, over a light pill on busy footage. 2–7 words/chunk (fewer = more energy).
3. **Cards persist and grow** — reveal rows one at a time, flip ✓ states, animate a progress bar. Prefer this
   over cutting to a new graphic.
4. **Border color = role** (blue topic / coral emphasis / green positive / amber warning / slate structure).
5. **Step-badge** for tutorials; **section pill + circled number** for long essays; **next-episode teaser**
   to close.
6. **Show the noun**: cutaway (framed device-mockup or screen-rec split) on each named tool/deliverable.
7. **Hook at frame 0**: stat / prop / claim card / proof screenshot — show the payoff immediately.
8. **Deliverable-as-object** near the hand for offer/CTA beats.
9. **A strong overlay system beats needing b-roll** — the two longest reels used almost none.
10. **One brand accent set, applied by meaning** to caption + card + icon — never decorative-random.

## 8. Build backlog (engine GAPs) — ALL BUILT + VERIFIED 2026-07-01

Every §8 item is now implemented in `scripts/talking_head_edit.py` on the LIGHT brand and frame-verified
(real render on a reference reel). Deep per-video specs: `per_video/V1..V9_analysis.md`.

1. ✅ **Card row STATE** — new `checklist` card: per-row `todo/doing/done` (numbered badge → green ✓) with an
   animated **progress bar** (`\p1` `Bar` style) that steps in lockstep with the ✓ via per-row `done_at`
   (state machine; ref V9). Static `state` snapshot also supported.
2. ✅ **Role border-color** for ALL cards — `_role_ass(role)` maps `brand_kit.ROLES`; `acc = _role_ass(role)
   or accent`. Border = MEANING (danger/success/…); kept as a SEPARATE axis from the ✓/fill state.
3. ✅ **Step-badge** — `badge` card: persistent corner pill (`label`+`sub`, `done:true`→✓); ref V3 "BƯỚC N".
4. ✅ **Section pill + circled ①②** — `section` card: `● label` + `num`→①..⑨, `splash:true`=centre splash→dock.
5. ✅ **Framed device-mockup** (`broll full` + `"frame":true` → blue border) + **presenter/screen-rec split**
   (`broll mode:"split"`, `split_ratio`) + **speaker-inset Mode-B** (`broll mode:"inset"`: footage→brand
   gradient + rounded speaker inset).
6. ✅ **Negation tile** (`checklist` row `state:"negate"` coral ✕ / `"affirm"` green ✓) + **reasoning line**
   (`reason` card `cause → effect`) + teaser = a `badge`/`section` "VIDEO SAU" variant.
7. ✅ **Caption placement** — `caption_align` (2 bottom / 8 top / 5 mid-float) + `caption_bottom` offset.

All new card types + b-roll modes documented in the talking-head SKILL.md (so the pipeline/agents can emit them).
Next (optional polish, not blocking): auto-emit these from `course_planner`/the splice matrix; rounded-corner
alpha mask on the inset; the AR tile-grab / 3D-morph motions noted as pre-render-only in the per_video files.

Related: [[talking-head-engine]] · [[template-craft-study]] · [[brand-colors-light-only]] ·
[[design-system-and-craft]] · [[master-video-spec]] · [[sfx-library-system]]
