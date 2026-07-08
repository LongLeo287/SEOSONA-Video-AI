# V8 — "Ngành nào sẽ HOT" — Visual Element Inventory

**Source reel:** `08_Ngành_nào_ta_chatgpt_giapducthang_Claude_Noti_Gemini_AI_digi` · ~185s essay · 40 scenes · 9:16 talking-head
**Contact sheet:** `8_WORKSPACE/talking_head_study/elements/sheets/08_Ngành_nào_ta_chatgpt_giapducthang_Claude_Noti_Gemini_AI_digi.jpg`
**Scope:** every small visual element layered over the footage (icons / emoji / stickers / cards / text-effects / decoratives). The 3-zone layout (top eyebrow-pill zone, mid caption band, bottom checklist/reason cards) is documented elsewhere and NOT re-catalogued here.

**Reel logic in one line:** essay walks 4 setup pills → accumulating ☑ checklist of AI job types → a "NHƯNG…" pivot → two ranked picks marked ①②③ (Tư vấn Luật, Kế toán) each with a ⚖/📊-iconed reason card + "→" inference line → closing "GÓC NHÌN CÁ NHÂN / Lưu lại xem lại cuối năm" pill.

---

## 1. EMOJI GLYPHS (inside eyebrow pills & mini-cards)

These are the signature "micro-icons." All ride at the **left edge of a pill/card**, ~1 line-height, full-colour emoji rendering (not monochrome line icons), on a dark glass pill.

| # | Glyph | Desc | Concept | Pill it rides | Zone | Freq | SEOSONA remap |
|---|-------|------|---------|---------------|------|------|---------------|
| E1 | ⚙️ gear | white cog | "optimize / operate" | `⚙ Tối ưu vận hành` | top eyebrow (stacked pills) | once (scene ~2) | keep glyph; pill fill → soft blue-tint glass; highlight word coral |
| E2 | ✨ sparkles | pale 3-star sparkle | "simplify everything / magic" | `✨ Đơn giản hóa mọi thứ` | top eyebrow (stacked) | once (scene ~2) | keep glyph; amber-tint accent OK; keep light |
| E3 | ⚠️ warning triangle | amber triangle + `!` | "pay close attention / caution" | `⚠ Để ý kỹ` | top eyebrow | ~2 (persists over pivot) | keep glyph → amber role; pill amber-tint glass |
| E4 | ⚖️ balance scale | scales of justice | "law / regulation / compliance" | row card `⚖ Việt Nam siết chặt chẽ` (section ① Tư vấn Luật) | mid checklist card | persists across ① block (~3) | keep glyph → blue role (authority); on light glass |
| E5 | 🌐 globe | blue meridian globe | "foreign / overseas market / language" | pill `🌐 Ngoại ngữ tốt = thu nhập khá 💰` | mid card | ~2 | keep glyph → blue role |
| E6 | 💰 money-bag | `$` sack | "income / higher pay" | trailing on the 🌐 pill above | mid card | ~2 | keep glyph → green role (money) |
| E7 | 📺 / 🖥 TV-monitor | screen glyph | "self-learn on AI is doable" | pill `📺 Tự học trên AI là làm được` | top eyebrow | once | keep glyph → blue role |
| E8 | 📊 bar-chart | rising coloured bars | "accounting / services demand" | card `📊 Kế toán dịch vụ cho DN 1 người` (section ② Kế toán) | mid card | persists across ② block (~2) | keep glyph → green/blue role |

**Asset type:** native **emoji glyph** (font/Twemoji PNG). Reproduce by dropping the same Unicode emoji at pill-left; no custom art needed.

---

## 2. ICONS (drawn/semantic marks that are NOT emoji)

| # | Name | Desc | Concept | Style | Zone | Freq | Asset |
|---|------|------|---------|-------|------|------|-------|
| I1 | **● status dot** | small solid filled dot at pill-left | "live label / section tag on" | ~6px solid circle, **cyan-teal** fill, sits before ALL-CAPS eyebrow text | top eyebrow pill (leading) | **persists — on nearly every eyebrow pill**, ~15+ appearances (`● XU HƯỚNG SẮP TỚI`, `● BẢN CHẤT MÔ HÌNH`, `● HỎI AI`, `● AI ĐỀ XUẤT`, `● AI ĐỀ XUẤT`, `● ① TƯ VẤN LUẬT`, `● ② KẾ TOÁN`, `● GÓC NHÌN CÁ NHÂN`) | **CSS-drawn dot** → recolour to SEOSONA **blue** (or coral when "active"); this is the single most repeated element |
| I2 | **☑ check-circle** | filled round badge with white tick | "confirmed / add to list" | **coral/orange** solid disc, white checkmark, ~1 line tall, at card-left | mid checklist card (leading each row) | **accumulates** — 1→2→3 rows in AI-list block, reused in ① `Hoạt động đúng luật` context; ~7 appearances | **filled-icon** (SVG) → keep coral = "confirmed" role; the accumulating checklist is a signature move |
| I3 | **→ inference arrow** | thin rightward arrow inside reason text | "therefore / leads to" (cause→effect) | inline `→` glyph, same colour as card body text, mid-sentence OR leading | mid reason card (`DN 1 người bùng nổ → nhu cầu còn cao hơn`; `→ Việc kế toán nhiều hơn rất nhiều`) | ~4 (once per ranked pick's reason line) | **glyph / CSS** → keep; render as coral or blue accent arrow to signal reasoning |

---

## 3. STICKERS / GRAPHICS

| # | Name | Desc | Concept | Style | Zone | Freq | Asset |
|---|------|------|---------|-------|------|------|-------|
| G1 | **Circled number ① (full-screen)** | large white outline circle enclosing "1" | "Pick #1 / ranked item 1" | thin white ring, hollow, numeral centred, ~120px, floats mid-right over footage as a chapter stamp | mid-right, over face | once as full stamp (scene ~16) then miniaturised into pill | **CSS-drawn ring + numeral** (or `①` Unicode). Recolour ring → SEOSONA blue outline, keep hollow/light |
| G2 | **Circled number ② (full-screen)** | same, "2" | "Pick #2" | identical to G1 | mid-right | once as full stamp (scene ~27) | same as G1 |
| G3 | **Circled number ③ (implied/mini)** | circled numeral shrunk INTO the eyebrow pill | "which ranked pick this section belongs to" | small `①`/`②` glyph nested left-of-label inside eyebrow pill (`● ① TƯ VẤN LUẬT`, `● ② KẾ TOÁN`) | top eyebrow | persists across each ranked block (~5) | **glyph** `①②③`; the big-stamp → pill-badge demotion is a signature transition |

---

## 4. CARD / PANEL ELEMENTS

| # | Name | Desc | Style | Concept | Zone | Freq | Asset |
|---|------|------|-------|---------|--------|------|-------|
| P1 | **Eyebrow pill (section tag)** | rounded-full dark glass capsule, ALL-CAPS text, `●`-dot leading | frosted dark-grey glass, soft rounded, subtle hairline, small caps | names the current section/topic | top zone | **persists — the spine of the reel**, ~15 distinct labels | **card/panel** (CSS glass) → light-brand: frosted **white/pale** glass, thin blue hairline, dark text |
| P2 | **Stacked setup pills** | 2–3 eyebrow-style pills stacked vertically | same glass, each with its own emoji (⚙ ✨) + coral keyword | list of model traits at once | top zone | once cluster (scene ~2–3), repeats identically 2 scenes | same as P1; supports stacking |
| P3 | **Accumulating checklist card** | wide glass rows, each `☑` + label | rounded glass row, coral tick, bold label (coral fill), rows stack downward | building a list of AI job types (AI Automation → Personal Agency → AI Agent Builder → AI Content System Designer) | mid zone, upper | **accumulates** 1→4 rows across scenes ~5–12 | **card/panel** stack; keep coral tick + light glass |
| P4 | **Reason / inference card** | single wide glass pill holding a cause→effect line with `→` | rounded glass, body text + coral keyword + `→` | the "why this is HOT" logic under each pick | mid zone, below headline | ~1 per ranked pick (~4) | **card/panel**; light glass, coral keyword |
| P5 | **Bullet fact rows (⚖/📊 block)** | 2–3 short glass rows under a ranked pick | glass row, emoji-left, coral keyword-highlight (`chặt chẽ`, `1 quy chuẩn`, `đúng luật`) | supporting facts for the pick | mid zone | ~3 per pick block | **card/panel** rows; light remap |
| P6 | **"NHƯNG…" pivot pill** | tiny dark pill reading `NHƯNG…` | small dark glass, ellipsis, sits above a big coral headline | dramatic pivot / "but here's the twist" connector | mid-upper | ~2 (over the "2 NGÀNH sẽ cực kỳ HOT" beat) | **card/panel** mini-pill → coral-tint to signal turn |

---

## 5. TEXT-EFFECT ELEMENTS

| # | Name | Desc | Style | Concept | Zone | Freq | Asset |
|---|------|------|-------|---------|--------|------|-------|
| T1 | **Keyword highlight (caption band)** | one/two words per caption recoloured | **coral/orange** on otherwise **white** bold caption, black stroke/shadow | draw eye to the key noun/verb of each spoken line | mid caption band (bottom-third) | **persists — every caption line**, ~40 (one per scene) | **text-effect** (per-word colour) → keep: white caption + **coral** keyword |
| T2 | **Big kinetic headline** | large 1–2 line display type over face | bold, **blue + black** OR **coral + black** two-tone, tight leading, centred | punchy section statements (`Doanh nghiệp 1 người`, `Làm với thị trường nước ngoài`, `2 NGÀNH sẽ cực kỳ HOT`, `Rất nhiều đội cần`, `Việc lại NHẸ hơn`, `Lưu lại, xem lại cuối năm`) | mid, over subject | ~10 headline moments | **text-effect**; blue=topic, coral=emphasis, keep light |
| T3 | **Coral emphasis word in headline** | single word blown up/recoloured inside headline | coral fill vs blue/black siblings (`HOT?`, `cực kỳ HOT`, `NHẸ hơn`, `Designer`, `cuối năm`) | the payoff word | mid | ~8 | **text-effect** → coral role |
| T4 | **Ranked-pick title (blue)** | pick name in blue script beside/under circled number | bold **blue**, slightly scripted/rounded (`Tư vấn Luật`, `Kế toán`) | names the ranked item | mid-right by stamp | 2 | **text-effect** → blue role |

---

## 6. IMAGE / SCREENSHOT ELEMENTS

None. **No** app screenshots, product images, phone bezels, photo-cutouts, memes, or B-roll stills are composited in. 100% of overlays are typographic pills/cards + emoji/CSS icons over a single static talking-head shot (subject + LED-lit code-screen background). Asset pipeline needs **zero** real imagery for this reel style.

---

## 7. CURSOR / POINTER

None. No animated cursor, tap-ripple, or pointer-hand element present.

---

## 8. DECORATIVE ELEMENTS

| # | Name | Desc | Notes |
|---|------|------|-------|
| D1 | **Glass frosting / soft shadow on pills** | every pill/card has a faint frosted-dark backdrop + soft drop shadow for legibility over footage | This is the only "decorative" treatment. SEOSONA remap: swap dark-glass → **light frosted white glass + soft shadow** (NO neon glow), thin blue hairline. |
| D2 | **Caption black stroke/shadow** | white captions carry a subtle dark outline | legibility only; keep. |

*(No confetti, particles, underlines-swipe, brackets, or corner decoratives observed.)*

---

## SIGNATURE ELEMENTS (the 3–5 that define this reel's look)

1. **● dot + ALL-CAPS eyebrow pill** (I1 + P1) — the ever-present section tag; appears on ~15 scenes and structures the whole essay. **The #1 reusable primitive.**
2. **Accumulating ☑ coral check-circle checklist** (I2 + P3) — job-type list that grows row-by-row; the reel's core "building an argument" motion.
3. **Circled number ①②③ ranked-stamp → pill-badge** (G1/G2/G3) — big hollow-ring stamp over the face that then demotes into the eyebrow pill to tag the section.
4. **Emoji-led fact/reason cards with `→` inference arrow** (E4/E8 + I3 + P4/P5) — `⚖ / 📊` glyph + coral-highlighted facts + a "cause → effect" line = the "here's WHY it's HOT" unit, repeated per pick.
5. **Coral keyword-highlight on white captions** (T1) — every single caption line has exactly one coral hero-word; the reel's typographic heartbeat.

---

### Asset-production summary (what the factory must build)
- **CSS-drawn:** ● status dot (I1), circled-number ring ①②③ (G1–G3), all glass pills/cards (P1–P6), glass frosting/shadow (D1).
- **SVG filled-icon:** ☑ check-circle (I2).
- **Glyph (Unicode / font):** → arrow (I3), circled-number badges when inline (G3).
- **Emoji glyph (Twemoji PNG/font):** ⚙️ ✨ ⚠️ ⚖️ 🌐 💰 📺 📊 (E1–E8).
- **Text-effect (per-word colour + display type):** keyword highlight (T1), kinetic headlines (T2–T4).
- **Real imagery / screenshots / bezels / cutouts / cursors:** **NONE required.**

**Brand remap rule applied throughout:** dark-glass → light frosted white glass; neon/glow → soft shadow; colour roles → blue = topic/authority/law, coral = emphasis/confirmed/pivot, green = money/income, amber = caution. Keep light, never dark mode.
