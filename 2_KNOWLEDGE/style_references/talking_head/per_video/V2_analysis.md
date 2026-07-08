# V2 Analysis — "Ae tranh thủ bào ngay có hết event nhé" (DeepSeek V4 free)

- **Source video:** `Ae tranh thủ bào ngay có hết event nhé.mp4`
- **Sheet:** `8_WORKSPACE/talking_head_study/dense/sheets/02_Ae_tranh_thủ_bào_ngay_có_hết_event_nhé.jpg`
- **Duration:** ~52.1s · **Scenes:** 28 · **Aspect:** 9:16 (source is a talking-head short)
- **Genre:** AI-tool announcement / "grab it while it's free" hype + how-to teaser
- **Palette note:** SOURCE is DARK + NEON CYAN HUD. SEOSONA brand is LIGHT. Translate the *mechanics* (corner-bracket panels, reveal states, spec table, teaser banner), not the neon palette — remap glow-cyan → brand blue/green roles on a light card.

> NOTE ON SOURCE ACCURACY: the sheet is the authoritative artifact (28 labeled keyframes with timestamps + captions). The decimated `_tmp/f_*.jpg` frames are a separate ~1fps sample of a DIFFERENT cut and do NOT align to the sheet — ignore them. All findings below are read directly from the sheet cells (cropped + 3× upscaled for card text).

---

## 1. TOP-ZONE CARD INVENTORY (the buildable payload)

The video uses **five distinct overlay archetypes**, all sharing one visual DNA (rounded panel, thin cyan stroke, **HUD corner-brackets** at all 4 corners, soft outer glow, dark semi-transparent fill):

| # | Archetype | Frames | Title text | Body | Notes |
|---|-----------|--------|-----------|------|-------|
| A | **Logo / brand intro card** | #1–#4 (0.9–6.5s) | `deepseek` / `V4 FLASH` | whale glyph | Big centered SQUARE card, blue fill, corner brackets. Scales UP (zoom-in) across #1→#4. |
| B | **Spec-sheet table card** (device-mockup) | #5–#10 (8.4–17.7s) | window titlebar `DeepSeek V4 Flash - Event` + `FREE` gold pill | 2-col table Item\|Details, 6 rows | macOS window chrome (3 traffic-light dots). Table body REVEALS row-by-row (#5 partial → #7–#9 full). |
| C | **HUD banner — title + subtitle** (section-pill / stat) | #11–#12 `GIỚI HẠN`; #13–#15 `MẸO LÁCH`; #24–#28 `KHỎE·KHÔN·NHANH` | bold title + small caps subtitle | dot-bullet before title | One template reused 3× with different copy. |
| D | **HUD checklist card** (card-state / bullet reveal) | #16–#22 (28.8–40.0s) | `TÍCH HỢP MỌI NƠI` + header icon | 3 icon-tile bullet rows | Rows reveal sequentially: #16 = 2 rows, #17–#22 = 3 rows. Each row = icon-tile + label. |
| — | (bottom) **Karaoke caption pill** | all frames | — | black pill, white text, dual-color keyword accent | present ~every scene. |

### Card copy (verbatim, from upscaled crops)

**B — Spec table (#5–#10):**
```
[● ● ●]  DeepSeek V4 Flash - Event                 [FREE]
Item              | Details
Event Model       | DeepSeek V4 Flash
Event Price       | Free (Input $0 / Output $0)
Free Tier Limits  | 10 RPM / 100K TPM per user
Other Models      | 20%–80% off during event
Sign-up Bonus     | $1 free API credit per new account
Event End         | Regular pricing resumes (to be announced)
```

**C — HUD banners (title + subtitle):**
```
GIỚI HẠN BẢN FREE
10 REQUEST/PHÚT · 100K TOKEN/PHÚT        (#11–#12)

MẸO LÁCH GIỚI HẠN
TẠO NHIỀU TÀI KHOẢN · XOAY KEY           (#13–#15)

KHỎE · KHÔN · NHANH
ĐANG FREE · LINK Ở COMMENT               (#24–#28, closing CTA teaser)
```

**D — Checklist card (#16–#22), header + 3 rows:**
```
[icon] TÍCH HỢP MỌI NƠI
  [</>]  Code prototype / MVP
  [▭]    Chatbot & Website
  [人]   Hermes qua 9Router
```

---

## 2. FRAME-BY-FRAME TIMELINE

Format per beat — **TOP** (card) · **MID** (speaker) · **BOT** (caption). Speaker is a young man in a brown/olive shirt, medium close-up, holding a fuzzy dynamic **mic** at chest/chin height in his right hand; other hand gestures. Background = dim room, door, monitors (neon rim). MID is essentially constant (medium-CU, centered, slightly right) — the STORY is told by the TOP card + BOT caption, not by shot changes.

| # | Ts | TOP (card / reveal state) | BOT caption (accent word→role) |
|---|----|---------------------------|-------------------------------|
| 1 | 0.9 | Logo card A, small, appearing | "DeepSeek V4 đang **được free**, anh" — `DeepSeek V4`=green, `được free`=yellow |
| 2 | 2.8 | Logo card A, larger (zoom) | "tích hợp vào sản phẩm **của**" — `của`=green |
| 3 | 4.7 | Logo card A, full size | "**DeepSeek** đang cho free bản V4" — `DeepSeek`=green |
| 4 | 6.5 | Logo card A holds | "Flash, còn **DeepSeek** V4 này được" — `DeepSeek`=green |
| 5 | 8.4 | Spec table B enters (top rows visible) | "nâng **reasoning** suy luận của nó" — `reasoning`=yellow |
| 6 | 10.2 | Spec table B, more rows + FREE pill | "và ở khả năng **cốt** truyện" — `cốt`=yellow |
| 7 | 12.1 | Spec table B fully revealed | "rất tốt. Tốc độ **phản hồi**" — `phản hồi`=yellow |
| 8 | 14.0 | Spec table B holds | "token trên giây rất là nhanh," |
| 9 | 15.8 | Spec table B holds | "với model 284 tỷ **tham số**" — `tham số`=yellow |
| 10 | 17.7 | Spec table B exiting | "cực kỳ ok. **Tuy** nhiên thì" — `Tuy`=green |
| 11 | 19.5 | Banner C `GIỚI HẠN BẢN FREE` enters | "10 **request** 1 phút Và 100k" — `request`=yellow |
| 12 | 21.4 | Banner C holds | "token 1 phút Nhưng ngược lại" |
| 13 | 23.3 | Banner C swap → `MẸO LÁCH GIỚI HẠN` | "có cách để mà **lách được**" — `lách được`=yellow |
| 14 | 25.1 | Banner C `MẸO LÁCH` holds | "**tài khoản** để có thể sử" — `tài khoản`=yellow |
| 15 | 27.0 | Banner C `MẸO LÁCH` holds | "dụng **Xoay** cái tài khoản đấy" — `Xoay`=green |
| 16 | 28.8 | Checklist D enters — **2 of 3 rows** (Code prototype/MVP, Chatbot & Website) | "cái **API** key này vào sản" — `API`=yellow |
| 17 | 30.7 | Checklist D — **3 rows** (Hermes qua 9Router added) | "phẩm của mình Vào code **để**" — `để`=yellow |
| 18 | 32.6 | Checklist D holds (3 rows) | "ra một cái MVP hoàn Toàn" |
| 19 | 34.4 | Checklist D holds | "có thể dùng được **Và độc**" — `Và độc`=yellow |
| 20 | 36.3 | Checklist D holds | "Hợp vào website của mình **Bên**" — `Bên`=yellow |
| 21 | 38.1 | Checklist D holds | "**9Router** anh em có kết Hợp" — `9Router`=green |
| 22 | 40.0 | Checklist D holds (last full-3 beat) | "Cái **API** key sao vào con **Hermes**" — `API`,`Hermes`=yellow/green |
| 23 | 41.9 | (card out / transition) | "**Để** làm sao vận hành con" — `Để`=yellow |
| 24 | 43.7 | Banner C swap → `KHỎE·KHÔN·NHANH` + sub `ĐANG FREE · LINK Ở COMMENT` | "**Hermes** Đấy hoàn toàn **free nhé**" — `Hermes`=green,`free nhé`=yellow |
| 25 | 45.6 | Banner C `KHỎE·KHÔN·NHANH` holds | "thông minh Con **này** thì vừa" — `này`=green |
| 26 | 47.4 | holds | "khỏe này **Vừa** khôn này **Vừa**" — `Vừa`=green |
| 27 | 49.3 | holds | "**free** nữa Nên anh em phải" — `free`=green |
| 28 | 51.2 | holds → outro | "để dưới comment nhé **Anh** em" — `Anh`=green |

**Story arc (card-driven):** brand reveal (A) → proof/spec (B) → constraint (C:GIỚI HẠN) → workaround (C:MẸO LÁCH) → application checklist (D:TÍCH HỢP) → CTA teaser (C:KHỎE·KHÔN·NHANH + "link ở comment"). Each ~2s caption beat; each card holds 2–7 beats.

---

## 3. BUILD-SPEC (engine-mappable)

### 3.1 Shared visual DNA → one base card style ("HUD panel")
- Rounded-rect panel, radius ≈ 24–32px.
- Fill: dark-translucent in source → **remap to light**: white/near-white fill at ~92% opacity with a subtle brand-tinted inner glow.
- Border: 2px thin stroke. **Corner brackets** (L-shaped marks) at all 4 corners — a distinctive, cheap-to-draw motif. In source they glow cyan → map cyan role to **brand BLUE #2A5BDA** for neutral/info panels.
- Header row: small leading ICON (or dot bullet) + BOLD title (uppercase for banners).

### 3.2 Card schemas (add/extend engine card types)

**`header` (already exists — extend to "banner"):** title + optional subtitle line + optional dot-bullet + corner-bracket frame + optional trailing pill.
```yaml
type: header            # banner variant
title: "GIỚI HẠN BẢN FREE"
subtitle: "10 REQUEST/PHÚT · 100K TOKEN/PHÚT"   # small-caps, muted
bullet_dot: true        # dot before title
frame: hud_brackets     # NEW cosmetic flag
role: warn|info|good    # border color role (see 3.4)
```

**`bullet` (already exists — add per-row icon + reveal state):**
```yaml
type: bullet
header:
  icon: pin
  title: "TÍCH HỢP MỌI NƠI"
rows:
  - {icon: code,     text: "Code prototype / MVP"}
  - {icon: chat,     text: "Chatbot & Website"}
  - {icon: person,   text: "Hermes qua 9Router"}
reveal: sequential      # rows appear one at a time, ~1 per beat
frame: hud_brackets
role: info
```

**`spec_table` (NEW — device/window mockup):**
```yaml
type: spec_table
chrome: macos           # 3 traffic-light dots
titlebar: "DeepSeek V4 Flash - Event"
badge: {text: "FREE", role: good}     # gold pill in source → brand GREEN/AMBER
columns: ["Item", "Details"]
rows:
  - ["Event Model", "DeepSeek V4 Flash"]
  - ["Event Price", "**Free** (Input $0 / Output $0)"]
  - ["Free Tier Limits", "10 RPM / 100K TPM per user"]
  - ["Other Models", "20%–80% off during event"]
  - ["Sign-up Bonus", "$1 free API credit per new account"]
  - ["Event End", "Regular pricing resumes (TBA)"]
reveal: rows_sequential
```

**`logo_card` (NEW — brand intro):** big centered square, brand-fill, logo glyph + product name + variant line, corner brackets, **scale-in** entrance.

### 3.3 Reveal STATES (the core "wow" mechanic)
- Rows / table-rows are **todo → done** by *appearance*, one per caption beat (~1–2s apart).
- Engine mapping: this is exactly the existing `bullet` "rows revealed sequentially" — extend it to (a) the spec-table body rows, and (b) tie reveal cadence to caption word timing (reveal row N when caption reaches the beat that introduces it: e.g. row "Hermes qua 9Router" appears at #17 as the VO says the checklist item).
- **No literal ✓/✕ checkmarks in THIS video** — reveal *is* the "done" signal (row simply materializes). Negation/✕ tiles are NOT demonstrated here (a gap this video does not fill; see V-others).

### 3.4 Colors → brand ROLES (light remap)
| Source (dark/neon) | Meaning | SEOSONA light role |
|---|---|---|
| Cyan glow border/brackets | neutral info panel | **Blue #2A5BDA** stroke, faint blue glow |
| Gold/amber `FREE` pill | positive / free offer | **Green #16A34A** pill (good) — or **Amber #D97706** if "limited-time" framing wins |
| Caption green word | entity / brand / key noun | **Green #16A34A** |
| Caption yellow word | emphasis / number / value | **Amber #D97706** |
| Red `GIỚI HẠN` framing (implied constraint) | warning / limit | **Amber #D97706** or coral **#E2724D** |

Rule: **border-color = card role.** info→blue, good/free→green, limit/warn→amber/coral. Same panel geometry, role drives the accent.

### 3.5 Positions (px, 1080×1920 canvas)
Cards sit in the TOP band; captions in the lower-middle. Estimated from sheet (card occupies top ~18–30% of cell for banners, ~30–40% for table/checklist):
- **Banner C (title+sub):** card box ≈ x:160–920 (w≈760, centered), y:150–330 (h≈180). Title ~52px bold, subtitle ~26px caps.
- **Checklist D:** card box ≈ x:150–840, y:150–560 (h≈410 for 3 rows). Header ~44px; rows ~40px with 56px icon tiles at left (x≈180), text at x≈260. Row pitch ≈ 105px.
- **Spec table B:** card box ≈ x:120–960, y:70–760. Titlebar h≈70; 6 rows pitch ≈ 95px; col split at ~x:430.
- **Logo card A:** centered square ≈ 520×520 at x:280–800, y:120–640; scale-in from ~0.4→1.0.
- **Caption pill:** centered, y ≈ 1120–1230 (lower-third-but-raised, sits over chest, NOT screen bottom). Pill auto-widths to text, ~64px tall, radius ~16px, pad ~28px. Text ~48px bold.

### 3.6 Timing / entrance rules
- Caption beats ≈ 1.5–2.0s each (28 beats / 52s).
- Card lifespans: banner 2–4 beats; spec table ~5 beats; checklist ~7 beats; logo ~4 beats.
- **Entrances:** logo = scale-in (zoom); banners = fade/slide-down + bracket-draw; checklist & table = container fades in then **rows reveal sequentially** synced to VO.
- Card SWAP between sections (B→C→C→D→C) — hard cut or quick cross, one card family on screen at a time.

---

## 4. ENGINE GAP FLAGS (what current engine CANNOT do yet)

Current engine has: `header`, `bullet`(seq reveal), `stat`, `term`; b-roll `full`/`pip`; karaoke caption w/ keyword accent. Against this video:

1. **`spec_table` card = MISSING.** No window-chrome / 2-column table / titlebar+badge card type. Highest-value new build (archetype B). Needs: macOS chrome cosmetic, 2-col grid, per-row reveal, corner badge pill.
2. **`logo_card` intro = MISSING.** No branded square logo card with scale-in. Cheap, high-impact opener.
3. **HUD corner-bracket frame = MISSING cosmetic.** A `frame: hud_brackets` flag on any card would unlock the whole look in one primitive.
4. **Per-row ICON TILES in bullets = likely MISSING.** Current `bullet` reveals rows but this video puts a distinct icon tile per row (`</>`, chat, person). Add optional `rows[].icon`.
5. **Header ICON + dot-bullet + trailing PILL on `header`/banner = extend.** Banner variant needs subtitle line + leading dot + optional trailing badge pill.
6. **Section-pill / "middot title" style (`KHỎE·KHÔN·NHANH`) = cosmetic add** — uppercase words joined by `·`, small-caps subtitle CTA line ("ĐANG FREE · LINK Ở COMMENT"). Maps to a `header` banner but the middot-triplet + CTA-sub is a recognizable teaser template.
7. **Reveal-synced-to-VO timing = partial.** Engine reveals rows sequentially but this video ties each row's appearance to the caption beat that names it. Need a hook: `reveal_at: <caption_word|beat>` per row.
8. **Dual-accent caption (two colors in ONE caption line) = verify.** Source colors both a green entity word AND a yellow value word in the same line (#1, #22, #24). Confirm engine keyword-accent supports >1 accent color per caption.

**NOT demonstrated here (don't infer from this video):** literal ✓/✕ checkmark toggles, numeric progress bar, circled step-numbers, negation/comparison tiles, device screen-recording mockup. This reel proves *reveal-as-done*, *spec-table*, *HUD banner+brackets*, *section teaser*, *dual-accent caption* — not the check/progress family.

---

## 5. TOP 3 TO BUILD FIRST (ROI order)
1. **`frame: hud_brackets` cosmetic** — one primitive, unlocks A/C/D looks instantly.
2. **`spec_table` card** — the single most differentiated, reusable "proof" asset (pricing/limits/specs); reused across every tool-announcement video.
3. **`bullet` row-icons + reveal-synced-to-VO** — turns the existing bullet into the checklist archetype D with minimal new code.
