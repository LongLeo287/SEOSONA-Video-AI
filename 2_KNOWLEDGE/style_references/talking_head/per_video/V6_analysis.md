# V6 Analysis — "Mình test hiệu quả AI agent"

**Source:** `06_Mình_test_xem_hiệu_quả_đến_đâu_rồi_share_cho_ae_thử.jpg`
**Duration:** ~105s · 54 keyframes · 9:16 (1080×1920)
**Why this reel:** the RICHEST card system in the study set — a true 3-zone with the speaker rendered as a **rounded inset card**, header cards with **semantic border colors** (gold / blue / green / red), a heavy screen-rec section that swaps the whole top zone, and a **next-episode teaser card** at the end. This is the single best reference for building the header-card + speaker-inset feature.

---

## 0. THE TWO LAYOUT MODES (the core finding)

This reel alternates between **three** presentation states. Tracking which is on-screen is the whole game.

| Mode | TOP zone | MIDDLE zone | When |
|------|----------|-------------|------|
| **A — Full speaker** | (none) | Speaker fills the WHOLE frame, edge-to-edge | Openers, transitions, emphasis beats (#1, #5, #31, #38, #44, #50-51) |
| **B — Card + inset** | Header card (ASS box, colored border) floating on a purple gradient | Speaker shrunk into a **rounded inset card**, centered, on the same gradient | Every "titled point" beat (#2-4, #6-8, #32-37, #39-43, #45-49, #52-54) |
| **C — Screen-rec split** | Full-width **screen recording** (light dashboard UI) occupying top ~45% | Speaker in bottom ~55%, straight crop (NOT a rounded inset), no gradient | The "how the org runs" demo (#10-29) |

The engine already has TOP-card / MIDDLE-speaker / BOTTOM-karaoke zones. **Mode B is the new thing to build**: speaker becomes a card-within-the-frame, and the background is no longer the footage — it's a brand gradient. Mode C is essentially existing B-roll `full` with the speaker pushed down.

---

## 1. FRAME-BY-FRAME TIMELINE (per beat)

Legend — TOP = header card (title / bullets / border color→role / reveal state) · MID = speaker treatment · BOT = caption chunk (keyword color).

### BEAT 1 — Hook: "một mình vận hành cả công ty" (#1–#5, 1.0–8.8s)
- **#1 (1.0s)** — TOP: none. MID: **Mode A**, full speaker. BOT: "**công** ty một mình tao mà" (kw `công` = GOLD).
- **#2 (2.9s)** — TOP: **GOLD** header card. Title "CÔNG TY MỘT MÌNH TAO" · subtitle "1 NGƯỜI VẬN HÀNH CẢ CÔNG TY". State: fully revealed. MID: **Mode B** — speaker snaps into rounded inset on purple gradient. BOT: "thử **nghiệm** trong thời gian gần" (kw GOLD).
- **#3 (4.9s)** — same GOLD card held. BOT: "cái kết **quả**. Công ty này".
- **#4 (6.8s)** — same GOLD card held. BOT: "để thay thế nhân **sự** bên".
- **#5 (8.8s)** — TOP: card OUT. MID: **Mode A**, full speaker (emphasis). BOT: "các nhân **sự** mình làm việc".

### BEAT 2 — Thesis: "AI không thay thế — AI bổ trợ" (#6–#8, 10.7–14.6s)
- **#6 (10.7s)** — TOP: **BLUE** header card. Title "AI KHÔNG THAY THẾ – AI BỔ TRỢ" · **3 check-bullets**: "Tăng năng suất / Tăng hiệu quả / Tiết kiệm thời gian". State: all 3 shown at once. MID: **Mode B** inset. BOT: "thế con **người** mà là giúp".
- **#7 (12.7s)** — same BLUE card. BOT: "tăng hiệu quả, tiết kiệm thời".
- **#8 (14.6s)** — same BLUE card. BOT: "việc. Ở đây cái công ty".

### BEAT 3 — Demo: how the org runs (#9–#29, 16.6–56.5s) — **Mode C**
- **#9 (16.6s)** — Mode A bridge, full speaker, "như ở phía trước mình chia".
- **#10–#12 (18.6–22.4s)** — **Mode C** begins. TOP: full-width **screen-rec** (light dashboard: org/roles board). Speaker bottom-half. Captions name roles with COLORED keywords: "**CEO** này, phòng" · "**marketing** này, rồi chuyên viên nghiên" (kw BLUE) · "cứu, chuyên viên hình, minh sẽ".
- **#13–#18 (24.4–34.1s)** — Mode C continues over different dashboards (kanban task board, ticket list, KPI cards, email/notification list). Keyword-accented captions: "giao những cái **task** hay là" · "**CEO** để nó sẽ tự động" · "và tạo những cái **ticket** công" · "việc giao **cho** trưởng phòng **marketing**" · "**giám đốc marketing** sẽ phân bổ" · "lại cái nhiệm **vụ** xuống dưới".
- **#19–#29 (36.1–56.5s)** — Mode C persists across more screens (agent runs, insight tables, content pipeline). Captions: "thì sẽ có một con **agent**" · "chuyển đi nghiên cứu thị trường" · "nghiên cứu **insight** khách hàng và" · "sản phẩm của công ty rồi" · "đưa ra chiến lược **marketing** và" · "lên chiến lược **content** bên cạnh" · "đấy thì nó sẽ có một" · "nó sẽ test lại và kiểm" · "thử lại những cái chiến lược" · "mà phòng **content** tạo ra để" · "vận hành một cái hệ thống".
- **#30 (57.6s)** — Mode A bridge, full speaker, pointing: "công ty mà **Agent** làm việc".

### BEAT 4 — Problem naming: "Loop Engineering → đốt token" (#31–#37, 59.5–71.2s)
- **#31 (59.5s)** — Mode A, full speaker. "**liên quan** một cái thuật ngữ".
- **#32 (61.5s)** — TOP: **BLUE/indigo** header card. Title "LOOP ENGINEERING" · subtitle "CÁC AGENT CHAT & PHỐI HỢP VỚI NHAU". **Header-only, no bullets.** MID: Mode B inset. BOT: "là **Loop Engineering** thì trong cái".
- **#33 (63.4s)** — same BLUE header. BOT: "vấn đề này thì nó **đốt**".
- **#34 (65.4s)** — TOP: card SWAPS to **GOLD** "ĐỐT NHIỀU TOKEN". **Bullet reveal state = 1 of 3** (only "Qua rất nhiều phiên chat" bright; other two dim/absent). MID: Mode B. BOT: "phiên chat mà **các Agent** làm".
- **#35 (67.3s)** — same GOLD card. **Bullet reveal = 2 of 3** ("+ Agent nói chuyện liên tục"). BOT: "thì cái **token** như hiện tại".
- **#36 (69.3s)** — same GOLD card. **Bullet reveal = 3 of 3** ("+ Tốn token đáng kể"). BOT: "**phiên** thì thật sự nó đốt".
- **#37 (71.2s)** — GOLD card held (all 3). BOT: "**token** khá là nhiều đấy như" (kw GREEN accent on "token").

### BEAT 5 — Solution: optimize cost (#38–#43, 73.2–82.9s)
- **#38 (73.2s)** — Mode A bridge, full speaker pointing up: "nên **cân** nhắc về các cái".
- **#39 (75.1s)** — TOP: **GREEN** header card. Title "TỐI ƯU CHI PHÍ" · **3 bullets** shown: "Cân nhắc kỹ model & API / Ưu tiên API miễn phí / Model chạy local nhẹ". MID: Mode B. BOT: "**model** API API mình cung cấp".
- **#40 (77.1s)** — same GREEN card. BOT: "**API free** và các cái model" (kw GREEN — matches card role).
- **#41 (79.0s)** — same GREEN card. BOT: "tại là mình dùng **đa phần**".
- **#42 (81.0s)** — same GREEN card. BOT: "và các **model** chạy **local** nhẹ".
- **#43 (82.9s)** — GREEN card held. BOT: "**để** làm sao mình tối ưu".

### BEAT 6 — Warning vs. recommendation (#44–#49, 84.9–94.6s)
- **#44 (84.9s)** — Mode A bridge, full speaker: "mà **chi** phí này mà anh".
- **#45 (86.8s)** — TOP: **RED/pink** header card. Title "API TRẢ PHÍ = KHÓ DUY TRÌ" · subtitle "CHI PHÍ TOKEN ĐỘI LÊN RẤT NHANH". MID: Mode B. BOT: "em có thể dùng **API trả**".
- **#46 (88.8s)** — same RED card. BOT: "**nó** không thể nào mà mà".
- **#47 (90.7s)** — TOP: card SWAPS to **GREEN** "ƯU TIÊN: MIỄN PHÍ" · subtitle "MODEL FREE · PROVIDER DÙNG THỬ · LOCAL". MID: Mode B. BOT: "duy trì được chi phí **công**".
- **#48 (92.7s)** — same GREEN card. BOT: "nào **cũng** sẽ là dùng các".
- **#49 (94.6s)** — GREEN card held. BOT: "cho dùng thử **free** để mình".

### BEAT 7 — Outro + TEASER (#50–#54, 96.6–104.4s)
- **#50 (96.6s)** — Mode A, full speaker: "tận **dụng** những cái **API** key".
- **#51 (98.5s)** — Mode A, full speaker: "**phí** vận hành công ty thì".
- **#52 (100.5s)** — TOP: **TEASER card**, **BLUE** border. Title "VIDEO SAU: KẾT QUẢ & CHI PHÍ" · subtitle "CÔNG TY NÀY LÀM ĐƯỢC GÌ · TỐN BAO NHIÊU". MID: Mode B inset. BOT: "**sẽ sâu** hơn cho anh em".
- **#53 (102.4s)** — same TEASER card. BOT: "**công ty** này làm được cũng".
- **#54 (104.4s)** — same TEASER card. BOT: "với những cái chi **phí** mà".

---

## 2. HEADER-CARD BORDER COLOR → ROLE MAP (verified from this reel)

Every header card in V6 carries a **semantic border color**. Confirmed occurrences:

| Border color | Role | Cards in V6 | Meaning |
|--------------|------|-------------|---------|
| **GOLD** `#D4A017`-ish (amber family → brand `#D97706`) | **CLAIM / cost-warning** | "CÔNG TY MỘT MÌNH TAO" (#2-4), "ĐỐT NHIỀU TOKEN" (#34-37) | The bold assertion or the pain-point being named. Highest visual weight. |
| **BLUE** (brand `#2A5BDA`) | **REASSURE / info / neutral thesis** | "AI KHÔNG THAY THẾ – AI BỔ TRỢ" (#6-8), "LOOP ENGINEERING" (#32-33), teaser "VIDEO SAU" (#52-54) | Calm framing, definitions, "next up". |
| **GREEN** (brand `#16A34A`) | **POSITIVE / solution / recommendation** | "TỐI ƯU CHI PHÍ" (#39-43), "ƯU TIÊN: MIỄN PHÍ" (#47-49) | The recommended action / the good outcome. |
| **RED / pink** (→ brand coral `#E2724D` in warn tint) | **WARN / negative / don't-do** | "API TRẢ PHÍ = KHÓ DUY TRÌ" (#45-46) | The trap, the failure mode. Directly precedes a GREEN recommendation card (RED→GREEN pairing = "problem → fix"). |

**Narrative color choreography** (this is the reusable pattern): GOLD claim → BLUE thesis → [Mode C demo] → BLUE term + GOLD problem → GREEN solution → RED warning → GREEN recommendation → BLUE teaser. Color = the argument's emotional beat, not decoration.

> **Palette translation note:** source card borders are neon-on-dark (gold glow, cyan-blue, neon-green, hot-pink). For SEOSONA LIGHT brand, translate to the flat brand hues (blue `#2A5BDA`, coral `#E2724D` for warn, green `#16A34A`, amber `#D97706` for gold/claim) and drop the glow. Keep the ROLE mapping; change the look.

---

## 3. BUILD-SPEC (engine-mappable)

### 3.1 Header-card schema (ASS box)

```yaml
header_card:
  title: str                     # "TỐI ƯU CHI PHÍ" — UPPERCASE, bold
  subtitle: str | null           # "MODEL FREE · PROVIDER DÙNG THỬ · LOCAL" — small caps, muted
  role: enum                     # claim | reassure | positive | warn
  bullets: [str]                 # 0..3; each with a leading glyph (check ✓ / dot •)
  reveal: enum                   # all_at_once | sequential
  icon: str | null               # small left glyph in title bar (gear / spark / check)
  prefix: str | null             # e.g. "VIDEO SAU:" for teaser variant
# role → border color (LIGHT brand):
#   claim    -> #D97706 (amber)   [bold assertion / named pain]
#   reassure -> #2A5BDA (blue)    [thesis / definition / next-up]
#   positive -> #16A34A (green)   [solution / recommendation]
#   warn     -> #E2724D (coral)   [trap / failure mode]
```

**Reveal timing** (from #34→#35→#36): sequential bullets appear ~1.9s apart, matching the caption cadence — each bullet lands as its caption line is spoken. Cards with `reveal: all_at_once` (#6, #39) show the full list on the card's entrance.

**Card lifecycle:** entrance ≈ card slides/fades in at beat start; held for 2–8s across multiple caption chunks; exits when the beat ends (often to a Mode-A full-speaker bridge before the next card). A card can **swap in place** to a new card of a different color without a Mode-A gap (#33 BLUE → #34 GOLD; #46 RED → #47 GREEN).

### 3.2 Speaker-inset 3-zone geometry (1080×1920, Mode B)

Approximate, measured off the sheet (inset is centered horizontally, upper-middle vertically; gradient fills all margins):

```
Frame: 1080 × 1920
Background: vertical purple→indigo gradient (brand LIGHT: swap to soft blue-tint
            gradient, e.g. #EEF3FF → #E3ECFF, or a light neutral #F5F7FB)

TOP zone (header card):
  x: 90        w: 900        (centered, 90px side margins)
  y: 70        h: ~150       (title bar ~56px + up to 3 bullet rows)
  corner radius: ~20px, 3px border in role color, subtle inner fill (dark→ light card)

MIDDLE zone (speaker INSET card):
  x: ~250      w: ~580       (centered; ~250px gradient margin each side)
  y: ~430      h: ~980       (portrait crop of speaker)
  corner radius: ~24px, thin light stroke / soft shadow
  → speaker is a 9:16-ish sub-card, NOT full-bleed

BOTTOM zone (karaoke caption):
  centered, y ≈ 1500–1650, dark pill behind text, one accent keyword per line
```

Mode C (screen-rec split) geometry:
```
TOP: screen-rec full width x:0 w:1080, y:0 h:~860 (light dashboard, letterboxed as needed)
MID/BOT: speaker straight crop x:0 w:1080, y:~860 h:~1060 (NOT inset, NOT gradient)
Caption pill sits over the speaker's lower third.
```

### 3.3 Teaser-card variant

Same schema as header-card with:
- `role: reassure` (BLUE border)
- `prefix: "VIDEO SAU:"` rendered inline before the title, same bar
- subtitle = the two things the next video answers, `·`-separated
- placed over a **Mode B** inset speaker at the very end (last ~4s)
- no bullets

### 3.4 Caption / keyword-accent spec (BOTTOM)

- Dark rounded pill, white body text, **exactly one accented keyword per chunk**.
- Keyword color usually GOLD, but **flips to match the active card's role** on solution beats (#40 "API free" = GREEN under the GREEN card). Rule: `keyword_color = card.role_color if card active else default_gold`.
- Chunk cadence ≈ 1.9–2.0s (matches keyframe interval), 4–6 words each.

---

## 4. WHAT THE ENGINE CAN vs. CANNOT DO

**CAN map directly:**
- Header card = existing ASS `header` box + `bullet` (sequential) — already have both. Add `role→border-color` field.
- `stat`/`term` boxes cover subtitles / definitions.
- Sequential bullet reveal exists.
- Karaoke keyword accent exists; adding "keyword color follows active card role" is a small rule.
- Mode C = existing B-roll `full` with speaker pushed to bottom band.

**GAPS to build:**
1. **Speaker-inset card (Mode B).** Engine currently renders speaker full-bleed or with cards *over* footage. Here the footage is replaced by a **brand gradient**, and the speaker is a **rounded sub-card**. Needs: gradient background layer + speaker crop-into-rounded-rect at the geometry above.
2. **Role→border-color header card.** Add the 4-role enum + LIGHT-brand color map to the header box.
3. **In-place card swap** (BLUE→GOLD, RED→GREEN) without a footage gap — sequencing feature.
4. **Teaser-card variant** with `VIDEO SAU:` prefix.
5. **Layout-mode state machine** (A/B/C) driving background + speaker treatment per beat.

**CANNOT / defer:**
- The exact neon glow on borders — intentionally NOT replicated (brand is LIGHT, flat). Translate role only.
- Real screen recordings (Mode C source footage) must be supplied as B-roll; engine can't fabricate the dashboard UI.
- Precise inset px are eyeballed from the contact sheet, not the master render — treat 3.2 numbers as a starting template to calibrate against a real 1080×1920 export.

---

## 5. TIMING SUMMARY

- Total ~105s, 54 sampled frames, ~1.9s interval.
- 6 distinct header cards + 1 teaser card across the reel.
- Mode A (full speaker) used for hook + every card-to-card bridge (~8 short beats).
- Mode B (card + inset) is the dominant "titled point" mode (~30s cumulative).
- Mode C (screen-rec split) is one long ~38s demo block (#10–#29).
- Color arc: GOLD → BLUE → [demo] → BLUE → GOLD → GREEN → RED → GREEN → BLUE(teaser).
