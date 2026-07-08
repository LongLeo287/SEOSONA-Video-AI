# V9 — "Vận hành cty 1 mình bằng AI agent" — Frame-by-Frame Card-State Analysis

> **THE primary reference for the CARD-STATE feature** (checklist ✓ / progress bar / row-by-row panel reveal / role-coded borders).
> Source video: `09_Vận_hành_cty_1_mình_tao_sẽ_thế_nào_.jpg` · ~95s · 52 scenes (~1.8s cadence)
> Frames read: `8_WORKSPACE/talking_head_study/dense/_tmp/f_0000.jpg … f_0051.jpg` (scene #N = `f_{N-1}`)
> Engine target: footage 9:16 (1080×1920), 3-zone (TOP card band / MIDDLE speaker / BOTTOM karaoke). All positions below are on the 1080×1920 canvas.

---

## 0. THE BIG PICTURE — what this reel does that our engine cannot yet

This reel is built almost entirely on **persistent, stateful TOP cards that UPDATE in place** rather than cut away. Six distinct card *archetypes* appear:

| # | Archetype | Example | Border ROLE-color | State behavior |
|---|-----------|---------|-------------------|----------------|
| A | **Title / hero banner** | "VẬN HÀNH BẰNG AI AGENT", "24/7" | gold | static (entrance only) |
| B | **Section-header teaser** | "GIAO MỤC TIÊU CHO CEO", "SẼ CẬP NHẬT HÀNH TRÌNH" | green / purple | static, bullet-dot + example subtitle |
| C | **Row-reveal list panel** | "CÁC PHÒNG BAN", "ĐỘI NGŨ DEV", "VÒNG LẶP…", "CHI PHÍ VẬN HÀNH" | cyan / amber / green / purple | rows appear one-by-one; an **active-row highlight** slides down synced to narration keyword |
| D | **Numbered CHECKLIST w/ ✓ state** | "CEO AGENT tự điều phối…" | purple (title accent) | each step flips todo→done (green ✓ + green fill); persists |
| E | **PROGRESS BAR** | attached under the CEO checklist | green fill | fills 0→100% across the 4 checklist steps |
| F | **B-roll pip / full** | isometric office-sim screenshot | — | rounded window in TOP zone (pip) or full |

The **CEO AGENT checklist (D) + progress bar (E)** is the crown jewel and the exact feature we are about to build.

---

## 1. FRAME-BY-FRAME TIMELINE (per beat)

Format per row: **TOP** (card: title / rows / reveal-state / active-row / bar%) · **MIDDLE** (speaker) · **BOTTOM** (caption chunk / accent word).

### Beat 1 — Cold open + title (scenes 1–6, 0.0–10.0s)
| # | Ts | TOP | MIDDLE | BOTTOM (accent) |
|---|----|-----|--------|-----------------|
| 1 | 0.9 | none | speaker, hands clasped | "vận hành **công** ty một mình" (accent = amber "công") |
| 2 | 2.7 | **Title banner** "VẬN HÀNH BẰNG AI AGENT" / sub "MỘT MÌNH · TỰ ĐỘNG · 24/7" (gold) **+ b-roll PIP** (isometric office-sim, rounded window) | speaker below pip | "ở trên online sử dụng **hệ**" |
| 3 | 4.5 | same title banner + b-roll pip | speaker | "nhau thì hiện ra mỗi **test**" |
| 4 | 6.4 | same title banner (b-roll gone) | speaker | "thời mà **nó** đã mang lại" |
| 5 | 8.2 | none | speaker | "ngoài **sức** tưởng tượng của mình" |
| 6 | 10.0 | none | speaker | "nó giống như một **công** ty" |

### Beat 2 — "BAN LÃNH ĐẠO AI" leadership panel — ROW REVEAL (scenes 7–8, 11.8–13.6s)
| # | Ts | TOP (list panel C, **purple** border) | BOTTOM |
|---|----|-----|--------|
| 7 | 11.8 | Title "★ BAN LÃNH ĐẠO AI". **1 row** visible: `⚑ CEO — định hướng & ra quyết định` (active, boxed highlight) | "thật từ **mô** hình cho đến" |
| 8 | 13.6 | **3 rows**: `CEO — định hướng & ra quyết định` (active) · `Founder` · `CTO · CFO` | "quy mô có **CEO** này, có" |

→ **Row-by-row reveal proven:** #7 = 1 row, #8 = 3 rows. Active row = top, rounded outline.

### Beat 3 — "CÁC PHÒNG BAN" departments — REVEAL + active-row SLIDE (scenes 9–13, 15.5–22.8s)
Border = **cyan/teal** (role: departments).
| # | Ts | Rows present | Active row (highlight box) | BOTTOM (accent) |
|---|----|--------------|---------------------------|-----------------|
| 9 | 15.5 | 2: `Quản lý` · `Content Creator` | Quản lý | "Founder này, có **CTO**, CFO, rồi" |
| 10 | 17.3 | **5** (all): Quản lý · Content Creator · **Marketing** · Sale · Chăm sóc khách hàng | Content Creator | "có quản lý này, **content** creator" |
| 11 | 19.1 | 5 (all) | **Marketing** (highlight slid to row 3) | "này, **marketing** này, phòng ban sale" |
| 12 | 20.9 | 5 (all) | **Sale** (highlight slid to row 4) | "này, marketing này, phòng ban **sale**" |
| 13 | 22.8 | 5 (all) | (fades / releases) | "chung đủ tất **cả** mọi" |

→ **Active-row highlight slides DOWN row-by-row, one row per narration keyword.** Rows persist; only the highlight moves. Accent word in caption == the row being highlighted.

### Beat 4 — "ĐỘI NGŨ DEV" dev team — HEADER-FIRST entrance (scenes 14–18, 24.6–31.5s)
Border = **amber/gold** (role: engineering).
| # | Ts | State | Active | BOTTOM |
|---|----|-------|--------|--------|
| 14 | 24.6 | **Header only** — empty box with a light SWEEP/shimmer across it, 0 rows | — | "thứ luôn. Ví dụ về **bên**" |
| 15 | 26.4 | **3 rows** all in: `Orchestrator — giao việc, tạo ticket` · `Dev · Senior · Junior` · `Tester — kiểm thử` | **Tester** (row 3) | "Dev đi thì có **Tester** này," |
| 16 | 28.2 | 3 rows | (mid) | "có người giao việc, ví **dụ**" |
| 17 | 30.0 | 3 rows | **Orchestrator** (row 1, highlight moved back up) | "**Orchestrator** giao việc này, và có" |
| 18 | 31.5 | 3 rows | Dev · Senior/Junior | "Dev này và Senior, **Junior** có" |

→ **Header-first entrance:** title card materializes with a sweep, THEN rows populate. Active-row highlight can move both down AND back up to re-reference a row.

### Beat 5 — "GIAO MỤC TIÊU CHO CEO" section header (scenes 19–23, 33.7–42.8s)
Archetype B — **green** border, bullet-dot + title + example subtitle.
| # | Ts | TOP | BOTTOM |
|---|----|-----|--------|
| 19 | 33.7 | none | "luôn, có Tester luôn, **các** con" |
| 20 | 35.5 | **Header banner** "● GIAO MỤC TIÊU CHO CEO" / sub "VD: THÁNG NÀY RA APP / PHẦN MỀM" (green) | "với nhau khi mình **giao** việc" |
| 21 | 37.3 | same header | "cho con **CEO** ví dụ giao" |
| 22 | 39.1 | same header | "để nó những con app **này**" |
| 23 | 41.0 | (transition into checklist) | "thì cái con **CEO** đấy nó" |

### Beat 6 — ★★ CEO AGENT CHECKLIST + PROGRESS BAR (scenes 24–31, 42.8–55.5s) — THE FEATURE
Archetype D+E. Title "CEO AGENT tự điều phối…" (purple accent on "AGENT"). Numbered step badges on the LEFT; green ✓ chip on the RIGHT when done; done row gets a **green-tinted fill**; a **progress bar** sits under the last row.

| # | Ts | Rows | Step states (badge→✓) | Bar fill | BOTTOM (accent) |
|---|----|------|----------------------|----------|-----------------|
| 24 | 42.8 | **3 rows**: 1 Phân tích mục tiêu · 2 Tạo ticket & nhiệm vụ · 3 Giao agent chuyên trách | **1 = DONE ✓** (green fill) · 2 todo · 3 todo (dim) | (no bar yet) | "sẽ tự động **phân** tích cái" |
| 25 | 44.6 | **4 rows** (row 4 `Agent nhận & thực hiện` revealed) | 1 ✓ · 2·3·4 todo | **bar appears ~15–20%** | "tự **phân** tích ra và sau" |
| 26 | 46.4 | 4 | **1 ✓ · 2 ✓** · 3·4 todo | **~40%** | "những cái **ticket** cái nhiệm vụ" |
| 27 | 48.2 | 4 | 1 ✓ · 2 ✓ · 3·4 todo | ~50% | "và nó sẽ giao **cho** những" |
| 28 | 50.0 | 4 | **1 ✓ · 2 ✓ · 3 ✓** · 4 todo | **~65–70%** | "con **agent** mà chuyên trách cái" |
| 29 | 51.9 | 4 | 1·2·3 ✓ · 4 todo | ~80% | "thì các **agent** nó nó" |
| 30 | 53.7 | 4 | **1 ✓ · 2 ✓ · 3 ✓ · 4 ✓ (ALL DONE)** | **100% (full green)** | "sẽ nhận **ticket** công việc đấy," |
| 31 | 55.5 | (checklist releases) | — | — | "và sau đấy nó thực **hiện**" |

→ **State machine, one step per ~2s beat:** reveal step (todo) → flip to done (✓ + green fill) → advance bar. Bar and checkmarks are **synchronized**: bar% ≈ (done_count / total) with easing. Steps 1–4 map exactly to: **1 Phân tích → 2 Tạo ticket → 3 Giao agent → 4 Thực hiện**.

### Beat 7 — "VÒNG LẶP TỰ KIỂM THỬ" self-test loop panel (scenes 32–38, 57.3–68.2s)
Archetype C — **cyan** border. Rows: `Tester test lại App & Code` · `Log lại lỗi & bug` · `Dev tự động fix lỗi`.
| # | Ts | Active row | BOTTOM (accent) |
|---|----|-----------|-----------------|
| 32 | 57.3 | (enter) | "làm việc Và hệ thống **báo**" |
| 33 | 59.2 | **Tester test lại App & Code** (row 1) | "thì nó có **Tester** Nó sẽ" |
| 34 | 61.0 | Tester (row 1) | "test lại cái app hay **là**" |
| 35 | 62.8 | Log (row 2) | "cái code Mã con **Dev** này" |
| 36 | 64.6 | **Log lại lỗi & bug** (row 2) | "nó sẽ **log** lại những cái" |
| 37 | 66.4 | Dev tự động fix (row 3) | "lỗi này Hay là những **cái**" |
| 38 | 68.2 | (release) | "fix lỗi Tức là toàn **bộ**" |

### Beat 8 — ★ "24/7" GOLD HERO BADGE (scenes 39–41, 70.1–73.7s)
Archetype A — **big gold "24/7"** centered in a gold-bordered dark panel; sub "TỰ CHẠY · ĐỘC LẬP · KHÔNG CAN THIỆP".
| # | Ts | TOP | BOTTOM |
|---|----|-----|--------|
| 39 | 70.1 | **24/7 badge enters** | "**24/7** Chạy độc lập với nhau" |
| 40 | 71.9 | 24/7 badge (full) | "Và mình **không** cần can thiệp" |
| 41 | 73.7 | 24/7 badge | "đang ở quy trình **test** thôi" |

### Beat 9 — "CHI PHÍ VẬN HÀNH" cost panel (scenes 42–47, 75.5–86.4s)
Archetype C — **green** border (role: cost/money). Rows: `API trả phí · tốn token` · `Vài provider miễn phí` · `Model chạy local`.
| # | Ts | Active row | BOTTOM (accent) |
|---|----|-----------|-----------------|
| 42 | 75.5 | (enter) | "Chỉ phí thì **thật** ra nó" |
| 43 | 77.3 | API trả phí (row 1) | "trả phí Thì **token** nó tốn" |
| 44 | 79.2 | (mid) | "khá nhiều nhé **Nhưng** hiện tại" |
| 45 | 81.0 | Vài provider miễn phí (row 2) | "thì mình có một vài **provider**" |
| 46 | 82.8 | Model chạy local (row 3) | "model **local** Thế nên hơn tại" |
| 47 | 84.6 | (release) | "gần như là free thì **Trong**" |

### Beat 10 — "SẼ CẬP NHẬT HÀNH TRÌNH" closing teaser (scenes 48–52, 86.4–93.7s)
Archetype B — header banner, **purple** border; sub "TIẾN ĐỘ · KHẢ NĂNG · CHI PHÍ".
| # | Ts | TOP | BOTTOM |
|---|----|-----|--------|
| 48 | 86.4 | header enters | "thời gian tới mình sẽ **cập**" |
| 49 | 88.3 | "✦ SẼ CẬP NHẬT HÀNH TRÌNH" / sub "TIẾN ĐỘ · KHẢ NĂNG · CHI PHÍ" | "công ty này của mình **Từ**" |
| 50 | 90.1 | same | "tiến độ công việc này, **khởi**" |
| 51 | 91.9 | same | "gì Và cái phí **vận** hành" |
| 52 | 93.7 | none (close on speaker) | "mỗi người có thể **tham** khảo" |

---

## 2. COLOR → ROLE MAP (borders & accents)

Source reel is dark/neon; **translate meaning, keep our LIGHT brand palette**:

| Reel neon | Semantic ROLE in reel | → SEOSONA LIGHT role color |
|-----------|----------------------|----------------------------|
| purple border | leadership / meta / "journey" | **blue #2A5BDA** (primary/authority) |
| cyan/teal border | operational departments / process loop | **blue #2A5BDA** tint or a secondary cool |
| amber/gold border | engineering / dev team | **amber #D97706** |
| green border | goals + cost/money + **done ✓** | **green #16A34A** (success/done); coral #E2724D reserved for cost warning if we want to split |
| gold "24/7" hero numerals | achievement / hero stat | **amber #D97706** on light chip (hero) |
| green ✓ chip + green row fill | step DONE state | **green #16A34A** |
| numbered dark badge | step TODO state | neutral gray-blue chip |
| caption accent word | keyword the card is "on" | brand blue / coral alternating (matches active row) |

**Rule:** border-color encodes the card's *domain role*; the ✓/green-fill encodes *completion state*. Keep those two axes independent in our schema.

---

## 3. BUILD-SPEC (engine-mappable)

### 3.1 Zone layout (1080×1920)
- **TOP card band:** y = 40 → ~620 (≈30% height). Card left margin x=60, width=960 (rounded-rect, 24px radius).
- **MIDDLE speaker:** the footage; cards float above, footage often shown in a rounded inset window (x≈150–930) when a card is present — pip-like framing.
- **BOTTOM karaoke:** y ≈ 1640 → 1820, centered dark pill, active word colored.

### 3.2 Card schema (proposed)

```yaml
card:
  id: string
  archetype: title | teaser_header | list_panel | checklist | hero_badge
  role: leadership | departments | dev | goals | cost | loop | achievement   # → border color
  title: string
  subtitle: string|null            # small caps under title (teaser/title/badge)
  bullet_dot: bool                 # leading ● for teaser_header
  # --- geometry (1080x1920) ---
  x: 60
  width: 960
  y_top: 40
  corner_radius: 24
  # --- entrance ---
  entrance: header_first | slide_down | fade | pop     # header_first = title+sweep, then rows
  sweep_on_title: bool

  rows:                            # list_panel + checklist
    - text: string
      icon: string|null            # ⚑ ✎ ⚙ etc. leading glyph
      badge: null | int            # checklist step number
      state: todo | doing | done   # checklist only; done → ✓ chip + green fill
      reveal_at: seconds           # when this row first appears
      active_from: seconds         # when highlight lands on it
      active_to: seconds

  progress_bar:                    # checklist only, optional
    enabled: bool
    y: <under last row>
    height: 10
    fill_pct: derived             # = done_count/total, eased; OR explicit keyframes
    color: green #16A34A
    track_color: light gray

  hero:                            # hero_badge only
    big_text: "24/7"
    big_color: amber #D97706
```

### 3.3 Row-reveal timing (from measured beats)
- **List panel (C):** rows reveal ~1 per 1.0–1.8s OR all-at-once then highlight slides. Two sub-modes seen:
  - *staggered reveal* (BAN LÃNH ĐẠO: #7 1row → #8 3rows)
  - *reveal-all + active-slide* (CÁC PHÒNG BAN: all 5 by #10, highlight walks rows 1→4 over #10–#12).
  - **Recommend:** support both via per-row `reveal_at`; `active_from/active_to` drives the moving highlight.
- **Active-row highlight:** a rounded outline box (2px, role color) + subtle fill; moves to the row whose keyword the narration is currently on. Sync to the SAME word the karaoke accents. Can move up OR down (re-reference).

### 3.4 Checklist state machine (the CEO card)
- 4 steps, `["Phân tích mục tiêu","Tạo ticket & nhiệm vụ","Giao agent chuyên trách","Agent nhận & thực hiện"]`.
- Cadence ≈ one step-completion per ~2s beat.
- Per step transition: **row present as `todo` (numbered dark badge)** → on its beat flip to **`done`** = swap badge for green ✓ chip (right side) + apply green-tint row fill. Prior done rows STAY done (cumulative, persistent).
- **Progress bar** appears when row 4 is revealed (#25) and fills: `fill_pct = done_count / 4`, eased between beats. Measured: ~20% (1 done) → 40% (2) → 70% (3) → 100% (4). Bar and checkmarks advance TOGETHER.
- Title stays fixed ("CEO AGENT tự điều phối…"). Whole card persists ~13s (#24–#30) then releases.

### 3.5 Entrance recipes observed
- **Title/hero (A):** slide-down + fade, gold accent, ~0.4s. B-roll pip may co-appear beneath in TOP zone.
- **Teaser header (B):** slide-down, bullet-dot + subtitle typed/faded.
- **List panel (C) header-first:** empty title box materializes with a **light SWEEP** across it, then rows pop in staggered (see DEV #14→#15).
- **Checklist (D):** rows pop in; ✓ chips "stamp" on with a small scale-pop; bar wipes L→R.
- **24/7 hero (E):** number scales up / glows.

### 3.6 Caption / karaoke placement (BOTTOM)
- Chunk of 4–6 words, centered dark rounded pill, y≈1640–1820.
- **Exactly one accent word per chunk**, colored (brand blue or coral). The accent word == the concept the active card row is currently on (tight card↔caption sync). e.g. "**ticket**" accent while step 2 flips done; "**Orchestrator**" accent while that row highlights.
- White for non-accent words; heavy weight; thin dark stroke/pill for legibility over footage.

---

## 4. WHAT THE ENGINE CANNOT DO (gaps to close)

1. **Per-row STATE (todo/doing/done) + ✓ stamp** — current `bullet` cards reveal sequentially but have no per-row completion state or green-tint fill on a done row. **NEW: `state` field + ✓ chip render.**
2. **PROGRESS BAR primitive** — no progress-bar element exists. **NEW: `progress_bar` with derived or keyframed fill, L→R wipe, green.**
3. **Numbered STEP BADGE** — no left-side numbered pill that swaps to a ✓. **NEW: badge render (int → ✓).**
4. **Moving ACTIVE-ROW highlight synced to narration keyword** — cards reveal but don't keep a highlight box that *walks* rows in sync with the accented caption word. **NEW: `active_from/active_to` per row driving a moving outline box.**
5. **Role-coded BORDER color** — need a `role → border color` table so each panel's border encodes domain (blue/amber/green), independent of the done-state green. **NEW: role enum.**
6. **HERO badge archetype** (big centered number like "24/7") — distinct from list/stat cards. **NEW archetype.**
7. **Header-first entrance with SWEEP** — title box appears alone + shimmer, then rows populate. **NEW entrance mode.**
8. **Card PERSIST + UPDATE across many beats (~13s)** without cutting away — our cards tend to be per-beat; the checklist must live and mutate over 8 scenes. **NEW: long-lived card w/ scheduled row/state/bar keyframes.**
9. **Card + rounded footage-inset framing** — when a card is up, the speaker footage is shown in a rounded window rather than full-bleed. Nice-to-have.

Feasible with ASS today (approximation): stacked `\an7` boxes, per-line `\t` fades for reveal, a filled rectangle grown via keyframed `\clip` for the bar, ✓ glyph swap by toggling two overlapping dialogue lines at the flip time. Full easing/glow may need a compositor pass. **Confirm ASS `\clip` keyframing is acceptable for the bar; else render bar as a short image sequence.**

---

## 5. ONE-LINE TAKEAWAYS
- This reel is the reference for **stateful, persistent, updating cards** — not cut-away flash cards.
- Two independent axes: **border = domain role**, **✓/green-fill = completion state**. Keep them separate in schema.
- The CEO checklist is a **4-step state machine, one flip per ~2s beat, bar and ✓ in lockstep**, steps = Phân tích → Tạo ticket → Giao agent → Thực hiện.
- List panels use either **staggered row reveal** or **reveal-all + a highlight that walks the rows** synced to the accented caption word.
- Keep it LIGHT: purple/cyan/amber/green neon → blue #2A5BDA / amber #D97706 / green #16A34A on light chips.
