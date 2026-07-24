# GROUP1 — Deep frame-by-frame craft study (reference shorts 1–14)

**Source folder:** `D:\SEOSONA AI\data\Video Template`
**Slice:** sorted-by-name index **1–14** (first 14 `.mp4` in `LC_ALL=C` sort order).
**Method:** per video I ran ffmpeg `scdet` hard-cut detection, built a 1-frame-per-second timestamp-stamped contact sheet (looked at every second), then extracted native-30fps dense montages around key moments (title reveal, list-row reveal, karaoke caption, glow-bloom transition, number count-up) and read the pixels. All specs are eyeballed from frames — treat timings as ±1–2 frames.

All 14 are **9:16 vertical, 30 fps**. 12 are 1080×1920, two are 720×1280 (v7, v11). Durations 37–139 s. All are Vietnamese-language faceless AI/tech "repo review / tool explainer" shorts. **They come from at least 6 different creator house-styles**, not one — that is the single most important framing fact for a rebuild: there is a shared *skeleton* but divergent *skins*.

### The 14 files (exact names, by index)
1. `3 kiểu lỗi trong hệ thống Agentic AI- Infinite loops, Hallucinated plans, Unsafe tools …Xem thêm.mp4` — 139.5s, 1080×1920
2. `AI Agent -hủy diệt- mới của ByteDance-  …DeerFlow… Xem thêm.mp4` — 37.3s, 1080×1920
3. `AI Berkshire là multi-agent framework, không phải tool đầu tư… .mp4` — 63.3s, 1080×1920
4. `AI code cứ mở session mới là quên sạch-  Engram… Xem thêm.mp4` — 51.5s, 1080×1920
5. `Agency Agents- Framework tối ưu hóa -Prompt Hệ thống-… Xem thêm.mp4` — 88.7s, 1080×1920
6. `Archify biến mô tả thành sơ đồ kiến trúc đẹp… Xem thêm.mp4` — 126.7s, 1080×1920
7. `Awesome LLM Apps- Kho template AI Agent & RAG… Xem thêm.mp4` — 116.7s, **720×1280**
8. `Bài 3- Skills trong Claude Code - Biến kinh nghiệm thành năng lực… .mp4` — 110.4s, 1080×1920
9. `Bạn muốn trò chuyện với AI theo cách riêng… SillyTavern… Xem thêm.mp4` — 103.8s, 1080×1920
10. `Bạn đã bao giờ tốn hàng giờ chỉ để căn chỉnh format code… Prettier… Xem thêm.mp4` — 108.1s, 1080×1920
11. `ChatbotX ra mắt như một lựa chọn mã nguồn mở thay thế ManyChat… Xem thêm.mp4` — 129.0s, **720×1280**
12. `Claude Code update tính năng Artifacts… Xem thêm.mp4` — 73.0s, 1080×1920
13. `Codebase Memory MCP giúp giảm token cost 99_… .mp4` — 52.2s, 1080×1920
14. `Codex không chỉ chạy với model của OpenAI… Ollama… Xem thêm.mp4` — 95.1s, 1080×1920

**Palette caveat up front:** every one of these is a **DARK** video (near-black or deep-tinted background, neon/glow accents). Our engine is **glow-on-LIGHT** (navy #003BA6 + green #00AA00, Be Vietnam Pro). So we port the *techniques, structure, motion, and semantic-color logic*, and invert the value scheme. The good news: almost every technique below is value-agnostic (a glow-bloom, a staggered list reveal, a count-up, a karaoke recolor all work on white just as well as on black).

---

## PART A — Recurring cross-video patterns (the reusable skeleton)

These appear in a majority of the 14 and are the highest-confidence findings.

### A1. The universal scene template: `kicker → 2-line headline → content block → bottom caption`
Seen cleanly in v2, v4, v5, v7, v8, v14; partially in almost all. Each "scene" is built from up to 4 stacked bands:
- **Kicker** — a tiny UPPERCASE, letter-spaced label above the headline, often with a leading dot or step-icon (`· GIỚI THIỆU`, `· ZERO DEPS`, `KIẾN TRÚC`, `AGENT-AGNOSTIC`, `REVEAL`). v4 24s `· ZERO DEPS`; v3 34s `REVEAL` badge; v14 every scene has a kicker + step icon.
- **Headline** — usually **two lines, the second line in the section accent colour**. v2 0-8s "Giao việc khó." (white) / "Rồi đi ngủ." (green); v4 18s "Một bộ não" / "cho mọi agent" (orange); v4 45s "Cho AI" / "một bộ não." (orange); v14 91s "Biến một URL" / "thành video." (green).
- **Content block** — one of a small vocabulary: chip-grid, numbered list, big number, comparison table, node diagram, code/terminal block, framed screenshot, data-viz (donut/bar/progress). See A5.
- **Bottom caption** — a running spoken-word caption band, phrase-swapped or karaoke (see A3).

**Rebuild takeaway:** model a scene as a slot machine of `{kicker?, headline{line1, line2, accentLine}, content{type,data}, caption}`. This one struct covers ~80% of what these videos do.

### A2. Semantic colour roles, one accent per section (NOT per video)
Colour carries *meaning* and switches per chapter:
- **Red = error / warning / danger / "the problem".** v1: "INFINITE LOOP" chapter is red (18-22s), the whole video's error types get red blooms; v8: the "Sai Lầm Phổ Biến" (common mistakes) section switches to RED (74-92s) while the rest is green.
- **Green = good / success / the featured topic / "solution".** v1 "UNSAFE TOOLS→fix" ends green; v8 whole "Skills" topic is green; v2/v5/v10/v14 green as brand.
- **Yellow/gold = highlight / the active karaoke word / "caution-ish middle state".** v1 "HALLUCINATED PLANNING" = gold (41-68s); karaoke active word = gold in v13.
- **Orange/coral = brand energy / stats** (v4 Engram, v7, v12 Claude).
Each video otherwise commits to **ONE dominant accent** (v6 red, v8 green, v9 purple, v10 green, v7 red) with a matching radial glow.

**Rebuild takeaway:** give the engine a `roleColor()` map — `error→red, success/topic→green(#00AA00), highlight→gold, brand→navy(#003BA6)` — and let the *script's* semantic tags drive per-section accent, exactly like these do. This is already close to the SEOSONA `ROLES` idea in memory; these videos prove the discipline works.

### A3. Bottom captions are ALWAYS present, in one of two modes
Every video has a persistent spoken-caption band in the lower third.
- **Mode 1 — phrase swap** (v4, v5, v7): the current spoken phrase shows in full, then hard-swaps to the next. Measured in v4 (30fps zoom @0s): phrase "AI code của bạn cứ" holds frames 0-26, blanks at f28, next phrase "mở phiên mới là quên" at f29 → **~0.9–1.0 s per phrase, ~1-frame gap, near-hard swap**. In denser-narration scenes (v4 @31.3s) the same swap runs **~0.6 s/phrase**, i.e. cadence tracks the voice.
- **Mode 2 — karaoke recolor** (v3, v9, v10, v13): the full phrase shows at once and **one word recolors to the accent** as it is spoken. Measured in v13 (20fps zoom @3s): white serif-italic phrase, active word turns **gold** and walks left→right, **~3–5 frames (~0.15–0.25 s) per word**, no scale/bounce — pure colour swap. There is often a **dim full-sentence context line** beneath the bright active phrase (two-tier caption).

**Rebuild takeaway:** we already have karaoke (ASS). Add the two-tier "dim context line under bright active phrase" and the phrase-swap mode. Keyword-recolor-to-accent is the single most consistent motion in the whole set.

### A4. Transitions are colour glow-blooms + cross-fades, NOT hard cuts
`scdet gt(scene,0.3)` found **0 hard cuts in 10 of 14 videos** — because the background stays constant (usually black) and scenes cross-fade. Measured the v1 chapter break (30fps zoom @99.3s): old card fades out (~3 frames) → **a full-screen radial glow flood in the section's accent colour ramps up over ~5–6 frames (f27–33), peaks saturated, then decays over ~10 frames** while the new card's content fades in underneath. **Total ~0.7–1.0 s.** Same red-bloom flashes visible in v1 @14s/41s/54s/87s/100s and v7 @~20s. Within a scene, elements cross-fade; between chapters, a coloured bloom.

**Rebuild takeaway:** implement a `chapterGlowBloom(accent)` transition = radial-gradient overlay, opacity 0→~0.7→0 over ~25 frames, under a content cross-fade. On our *light* bg this becomes a soft accent-tinted bloom wash (navy or green) rather than a black-to-red flash — still reads as a "beat".

### A5. The content-block vocabulary (what actually fills the middle)
Across all 14, the middle "content" is drawn from a small, buildable set:
1. **Chip / tag grid** — rounded pills with icon+label, popping in staggered. v2 15-30s, v4 18s/39s, v5 hook, v7 31-47s.
2. **Numbered list card** — rows `① title / subtitle`, staggered reveal, sometimes the active row highlighted. v4 30-38s, v8 mistakes, v13 25-29s, v3 42-47s.
3. **Big number** — huge accent numeral, often counting up. v1 counters, v2 57.5k→72.6k, v4 "0"/"8+", v7 "115K★", v9 "299k", v10 "239→430", v13 "95→99", v11 "5→8".
4. **Comparison table** — header row + rows, accent header. v5 roster, v7 61-72s, v10 10-15s, v11 ports.
5. **Node / flow diagram** — nodes + connectors, vertical or radial, glow edges. v2 agents, v10 35-42s architecture, v13 17-24s, v14 70-81s, v12 3-9s.
6. **Code / terminal block** — mono font, syntax highlight, lines appear one by one; used as the CTA-install and as "proof". v2 32-36s, v4 45-49s, v8 20-39s (SKILL.md YAML), v13 30-35s, v14 throughout.
7. **Framed real screenshot / screen-recording** — a light-mode product shot inset in a rounded dark frame with a tiny persistent header label. v4 12-17s, v5 21-34s (long), v6 many, v11 many, **v12 13-68s is ~55 s of framed screen-recording**.
8. **Data-viz** — donut/ring with center %, progress bar, bar chart, timeline. v10 is the richest (donut @51-57s "35", progress bar @78-84s "92%", stat grid @16-24s), v9 HUD/timeline, v3 podium bars @48-53s.
9. **Big-word background typography** — a huge low-opacity word bleeding behind content ("BEAUTIFUL", "VIBE CODE" in v6; "MANY" in v11; brand wordmark reveals in v6/v11/v12).

### A6. Strong close: brand/CTA outro is mandatory
Every video ends on a deliberate CTA, ~5–12 s:
- **Follow-card** with avatar + handle + a coloured Follow/Subscribe button: v4 "AIDev Repo · Theo dõi" (red), v7 "FOLLOW NGAY" (red), v9/v10 red subscribe buttons, v3 "XEM NGAY →" gold, v13 "TAP HERE →" gold.
- **Install/terminal CTA**: v2 `git clone`, v4 `brew install`, v14 `escbase.xyz` pill.
- **Brand wordmark**: v12 "Claude Code", v2 "DeerFlow".
- Several end on a **waveform** graphic (v3 54-59s, v13 46-50s) synced to the outro voice.

### A7. Composition: full-bleed on background, content vertically centered, big safe margins
Content lives in the **middle ~60%** of the frame; the top ~15% and bottom ~20% are mostly empty (platform UI safe zones) except the caption band. Cards are **NOT full-bleed** — they're centered rounded rectangles ~80-90% width with generous surrounding negative space. Headlines are often **left-aligned and top-anchored** (v6, v7, v9, v10 anchor the section title top-left) while the content card sits centered below. Text and cards **rarely bleed off-edge** — the exceptions are deliberate big-word backgrounds (A5.9) and full-bleed photo/screenshot scenes.

### A8. Backgrounds: near-black + single-accent radial glow + faint texture
Dominant treatment = flat near-black or deep-tinted gradient, with a **soft radial glow in the accent colour** behind the focal card, plus **very faint texture** (tiny particle dots v2/v4, orbital rings v10, subtle grid). Two creators (v9 AIDAILY.ONE) add **GPU-rendered 3D spectacle backgrounds** (matrix data-rain, particle funnels, wireframe servers, HUD dashboards) as full-bleed "wow" interludes — the hardest thing here to reproduce in pure HTML/CSS/SVG.

---

## PART B — Per-video breakdown

### v1 — "3 kiểu lỗi trong hệ thống Agentic AI" (139.5s) — the color-coded chapter explainer
- **Structure:** 0-8s intro title card (red tint) → 9-17s **SYSTEM DESIGN** chapter (cyan) diagram card → 18-40s **INFINITE LOOP** (red, big radial glow @18-22s) → 41-68s **HALLUCINATED PLANNING** (gold) → 69-86s **UNSAFE TOOLS** (green, list builds @72-80s) → 87-100s red bloom section → 101-123s **TÓM LẠI** (summary) → 124-138s **THIẾT KẾ HỆ THỐNG** (solution, cyan), ends with a particle burst @133s. Three error types = three colour chapters, bookended by intro+summary+solution.
- **Scene hold:** ~8–15 s per chapter; content lines build inside each.
- **Motion:** neon-outline cards fade in; bullet lines accumulate one-by-one inside a card; **chapter breaks = accent-colour radial glow-bloom flood** (measured f27–33 red ramp @99.3s, ~0.8s). Entrances are fades, ease-out, no overshoot.
- **Transitions:** colour glow-bloom (red @14/41/54/87/100s). No hard cuts.
- **Typography:** section title in caps in the accent colour above the card; card body = small sans bullets. ~2 sizes.
- **Composition:** single centered neon-outline rounded card, mid-frame; heavy black negative space; radial glow behind.
- **Colour/light:** black bg, ONE accent per chapter (cyan/red/gold/green), strong radial bloom, neon 1px card borders.
- **Subjects:** thin-stroke neon "cards", a mini node diagram, bullet lists.
- **Pacing:** slow, explainer-paced (~0.1 cut/s equivalent); energy pulses at each colour-bloom.
- **Buildable:** color-coded chapter system; neon-outline card on glow; radial-bloom chapter transition; progressive bullet accumulation.

### v2 — "DeerFlow / ByteDance" (37.3s) — editorial kinetic-typography
- **Structure:** 0-8s HOOK big serif "Giao việc khó." (white) + "Rồi đi ngủ." (green) two-color headline, subtext + "· · · ĐANG CHẠY" status → 9-14s **brand reveal** "DeerFlow" serif logotype (Deer white / Flow green), kicker "BYTEDANCE · OPEN SOURCE", italic tagline, "#1 GITHUB TRENDING" → 15-23s node diagram (3 agent nodes + 2×2 feature chip grid) → 24-31s 2×3 app-type icon grid (Báo cáo/Slide/Trang web/Hình ảnh/Video/Nghiên cứu) → 32-36s **stat** big number 57.5k→72.6k ⭐ + terminal CTA `git clone / cd / make setup` + repo URL.
- **Scene hold:** ~6–9 s.
- **Motion:** serif second line fades in after first (~0.5s later); chips pop staggered; number counts up; terminal lines type/appear in sequence.
- **Transitions:** cross-fade, dark-green constant bg.
- **Typography:** **three-font system** — serif display headline (elegant), sans for chips/labels, mono for terminal. Two-colour headline split by meaning. Kicker above every headline. This is the most typographically sophisticated of the 14.
- **Composition:** centered, generous; a faint chevron motif + particle dots on a green-black gradient.
- **Colour/light:** near-black with green radial glow; green accent throughout.
- **Subjects:** serif logotype, node diagram, app-icon grid, big number, terminal.
- **Buildable (high value):** serif+sans+mono three-font hierarchy; two-colour semantic headline; kicker system; app-icon grid; counting stat; terminal-as-CTA.

### v3 — "AI Berkshire" (63.3s) — "Lạch Cạch AI" style, karaoke + full-bleed gradients
- **Structure:** 0-2s HOOK blue gradient "Thử đoán xem ai vừa open-source một 'Chief of Staff'" → 3-9s pink/lavender **notification card** "AI Berkshire lên GitHub Trending!" → 10-15s big number "12.4k GitHub stars" → **16-20s real talking-head b-roll** (creator in hoodie, "· REC" indicator, "KHÔNG PHẢI TOOL TỰ ĐỘNG!") → 21-27s **before/after** "Trước: hỗn loạn / Sau: cấu trúc" (teal bokeh) → 28-33s GitHub repo card "AI-Berkshire/framework" with coloured pills → 34-41s reveal "Nó là Decision Machine!" (orange-brown, REVEAL kicker) → 42-47s "3 lợi ích cho solo founder" benefit cards (green) → 48-53s **podium/bar chart** (2-1-3, gold) → 54-59s CTA "Fork ngay, chạy thử!" with **audio waveform** → 60-61s outro "Follow Lạch Cạch AI…" + "XEM NGAY →" gold button.
- **Persistent:** bottom **karaoke captions** (gold active word) run the whole video.
- **Motion:** per-word karaoke recolor; before/after slides; podium bars grow; waveform reacts.
- **Transitions:** full-bleed gradient scene changes (each section a different gradient), cross-fade.
- **Typography:** bold sans headlines + karaoke serif-ish caption; keyword-in-caption highlighted gold.
- **Composition:** **full-bleed gradient scenes** (not cards) — content floats directly on gradient. Real b-roll is full-bleed.
- **Colour:** sectional gradients — blue → pink → teal → orange → green → dark. Less disciplined single-accent than the review channels; more "each beat its own mood".
- **Subjects:** notification card, big number, **real reaction clip**, before/after, repo card, podium chart, waveform.
- **Buildable:** karaoke keyword highlight; before/after split; podium bar chart; notification-card mockup; waveform outro. (Real b-roll insert = a footage-engine thing.)

### v4 — "Engram" (51.5s) — "AIDev Repo", the most template-like ★ reference build target
- **Structure:** 0-5s HOOK giant "ENGRAM" (heavy condensed, specular glow-sweep), kicker "AIDEV REPO · REPO REVIEW", "1 bộ não" (orange), chip row (4.7K/MIT/Single-Go-binary), green "8+ AI agent" pill, `$ brew install` line → 6-11s intro "Engram" + stat chips (4.7K stars/Feb 2026/v1.17.0) + feature pills → 12-17s **framed screenshots** (star-history chart, GitHub file list, terminal) → 18-23s "Một bộ não / cho mọi agent" (orange L2) + chips (Claude Code/Cursor/Copilot/Gemini) + "8+" big number → 24-29s big **"0"** "· ZERO DEPS" + comparison table → 30-38s "Ba lớp cốt lõi" **numbered list** (3 rows stagger in) → 39-44s "Đủ đồ chơi cho dev pro" 2×3 chip grid → 45-49s CTA "Cho AI / một bộ não." + `brew install` terminal + repo URL → 49-50s **follow-card** "AIDev Repo · Theo dõi" (red button).
- **Scene hold:** ~5–6 s, very regular.
- **Motion (measured):** ENGRAM wordmark persistent with a **specular light-sweep** left→right across letters over ~12 frames (~0.4 s, f26–38 @0s); captions **phrase-swap ~0.9s** (title scene) to **~0.6s** (dense scene); numbered rows **stagger fade+slide-up ~0.2s apart, ease-out no overshoot** (f24–36 @31.3s).
- **Transitions:** cross-fade on a constant navy-teal gradient.
- **Typography:** heavy condensed display headline, 2nd line orange; kicker caps label; sans chips; mono terminal. ~3 sizes, big:small ratio roughly 4–5:1.
- **Composition:** headline top-left-ish, content centered; navy-teal radial glow; particle dots.
- **Colour:** navy/teal bg + **orange accent** + occasional green pill for "good" facts (8+ agents).
- **Subjects:** big wordmark, chip rows, big numbers (0, 8+), numbered list, comparison table, framed screenshots, terminal, follow-card.
- **Buildable (highest value):** this IS the template. `kicker + 2-line accent headline + {chips|bignum|list|screenshot} + caption + follow-outro`. Specular wordmark sweep. Staggered list reveal.

### v5 — "Agency Agents" (88.7s) — green, screenshot-heavy
- **Structure:** 0-8s HOOK "Một trợ lý" (white) / "đội ngũ chuyên gia" (green), robot icon with **role-chip swarm** popping in (Backend/Security/Product/…) → 9-20s big "140+"/"130+" persona + list card building → **21-34s long real light-mode screenshots** (GitHub repo, README, "What is This?", Quick Start, code, roster **table**) ~14s → 35-47s "Bốn tiêu chí cốt lõi" 2×2 chip grid + green "production-ready" badge → 48-62s "Division rộng hơn code" two-column list building, gold underline sweep → 63-76s "Agency Agents App" **product-UI mockup** (roles + progress bars + download buttons) → 77-88s "Không chỉ là prompt" closing statement card.
- **Scene hold:** 8–14 s; screenshot section dwells long.
- **Motion:** icon+chip swarm entrance; big-number; row-by-row list; gold underline wipe.
- **Typography:** white/green 2-line headline; sans throughout; keyword green in captions.
- **Composition:** centered cards; full-screen for the screenshots.
- **Colour:** near-black + green accent + radial green glow.
- **Buildable:** icon-with-chip-swarm hook; two-column division list with underline-wipe; app-UI mockup with progress bars; long framed-screenshot handling.

### v6 — "Archify" (126.7s) — red, dense screenshot review + big-word bg
- **Structure:** 0-9s HOOK "CHAT RA SƠ ĐỒ ĐẸP" (top-left) + product window → then rapid sectioned feature tour: "Nhiều Loại Sơ Đồ" (10-17), "Hỗ Trợ Nhiều Lệnh" (18-25, screenshots w/ red callouts), "Xuất File Xịn" (26-31, numbered "1" badges), "Đổi Sáng Tối" (32-38), "Vẽ Theo Mẫu"/"Năm Kiểu Chính" (39-53), "Workflow Rõ Nhất" (54-59, **big-word "BEAUTIFUL" bg**), "Sequence/Data Flow" (60-72, **"VIBE CODE" scrolling bg**), "Lifecycle/Bản 2.5" (73-85), "Xuất Nét Tới 4×" (86-95), "SVG Theo Người Đọc" (96-104), "Cài Đặt Nhanh" (105-112), "Điểm Chốt" summary (113-119) → 120-126s outro "YOU ARE BEAUTIFUL" big-word + "Xem thêm" CTA.
- **Scene hold:** short, ~6–8s, many sections (dense).
- **Motion:** red highlight callouts appear on screenshots; big-word backgrounds scroll/drift behind content.
- **Typography:** section header anchored **top-left small**; huge low-opacity **background word**; red keyword highlights.
- **Colour:** black + **red accent**.
- **Buildable:** **big-word background typography** (huge low-opacity word bleeding behind, drifting); red callout-highlight on screenshots; top-left persistent section header.

### v7 — "Awesome LLM Apps" (116.7s, 720p) — "Nguyễn Thành Rainmaker", navy+red review skeleton
- **Structure:** 0-9s HOOK "Awesome LLM Apps" (red, top-left) + kicker "· TỔNG HỢP GITHUB" + numbered cards 01/02/03 → 10-19s "Sức hút cộng đồng" + big **"115K ★"** → 20-30s red glow bloom + card "Không chỉ tổng hợp link…" with persistent index "1" top-right → 31-47s "Bao phủ toàn bộ hệ sinh thái" chip grid (AI Agents/MCP/Voice/RAG…) → 48-60s template example cards grid → 61-72s **comparison table** (model/cost/platform) → 73-84s value card → 85-96s **3-step card** (numbered steps + code) → 97-116s outro "Theo dõi để không bỏ lỡ AI thực chiến" + red "FOLLOW NGAY" + collab card.
- **Persistent:** creator name top on every frame; index counter top-right during a section.
- **Motion:** numbered cards build; red glow blooms at section breaks; big stat.
- **Typography:** red 2-line headline; kicker; numbered cards.
- **Colour:** navy-black + **red accent** + red blooms.
- **Buildable:** numbered feature cards (01/02/03); persistent section index counter; big red stat; comparison table; 3-step install card; strong follow-CTA.

### v8 — "Skills trong Claude Code" (110.4s) — green topic + red mistakes section
- **Structure:** 0-7s HOOK "Bạn đang copy-paste cùng một prompt mỗi ngày?" (copy-paste green) → 8-19s "Slash Command vs Skill" **side-by-side comparison cards** (Skill card green-highlighted) → 20-39s "Cấu trúc một Skill" **code block** (SKILL.md YAML, green syntax, grows line-by-line) + bullet list → 40-58s "Hai loại Skill" two cards (Personal / Project, green) with paths → 55-73s "Skill có thể chứa nhiều file" file-tree/code blocks → **74-92s "Sai Lầm Phổ Biến" (RED)** numbered mistakes (01 quá rộng / 02 description quá ngắn / 03 quá nhiều instructions) → 93-99s green "copy-paste → tạo Skill" → 100-109s outro "Biến kinh nghiệm → Năng lực tái sử dụng".
- **Motion:** code lines appear sequentially; comparison rows build; mistake list staggers.
- **Colour:** green topic accent, **switches to RED for the mistakes chapter** — cleanest example of A2.
- **Buildable:** side-by-side comparison cards (one highlighted); syntax-highlighted code block growing line-by-line; semantic red "mistakes" section; two-type cards.

### v9 — "SillyTavern" (103.8s) — "AIDAILY.ONE", purple + 3D spectacle
- **Structure:** 0-17s HOOK small card + karaoke caps captions (purple) → **18-27s 3D "data-rain" matrix background** + "299 NGHÌN SAO" → 28-37s API-provider list card → **38-45s 3D particle funnel** + "HƠN 1287 COMMIT" → 46-53s paragraph card → 54-61s **timeline** (2023→TavernAI→SillyTavern dots) → **62-68s 3D wireframe server** → 69-84s feature list + **3D HUD dashboard** (glowing bar charts + gauges) → 85-91s "Làm chủ trí tuệ nhân tạo" → 92-103s outro red-heart + subscribe buttons.
- **Motion:** karaoke caps captions (green/cyan word); rendered 3D motion backgrounds drift/rotate.
- **Colour:** purple/violet + cyan 3D glow.
- **Subjects:** **GPU-rendered 3D spectacle** (data-rain, particle funnel, wireframe server, HUD) — the least reproducible in HTML/CSS/SVG.
- **Buildable (partial):** timeline dots; HUD-style gauge/bar cluster (can approximate with SVG); ALL-CAPS karaoke captions; red-heart subscribe outro. **Not easily buildable:** the true 3D interludes.

### v10 — "Prettier" (108.1s) — "AIDAILY.ONE", green + the richest data-viz ★ data-viz target
- **Structure:** 0-9s HOOK small "Prettier" card + karaoke caps captions → 10-15s comparison table → 16-24s **2×2 stat grid** (GitHub numbers) → 25-34s supported-languages **list w/ icons** → 35-42s **node/architecture diagram** (central node, radiating glow edges) → 43-50s pipeline step list → **51-57s donut/ring chart** (yellow-green ring, center "35", animated fill) → 58-71s terminal + CI/CD step cards → 72-77s file-tree → **78-84s progress bar "92%"** (fills 88→92) → 85-91s activity stat cards → **92-98s big counting number 239→430** → 99-107s outro red-heart "Cảm ơn bạn" + subscribe.
- **Motion (measured):** count-up 0→430 over **~1.5–1.6 s, ease-out deceleration** (+104,+64,+71,+55,+42,+25,+25,+17,+12,+6,+5,+2) with subtle **sparkle particles** around the numeral; donut ring sweeps to fill; progress bar animates to 92%.
- **Colour:** green + gold/orange numbers; subtle orbital-ring bg motif.
- **Buildable (highest value for our data-viz family):** animated **donut with center %**; **progress bar fill**; **ease-out count-up with sparkle**; stat grid; node diagram; timeline — this maps 1:1 to our existing ring/donut/bars/linechart components.

### v11 — "ChatbotX" (129.0s, 720p) — red review, screenshots + gauge + crowd photo
- **Structure:** 0-6s HOOK "MANYCHAT BỊ THÁCH THỨC" over product shot → feature tour: "Chat Marketing AI" (7-22, colourful tile board), "15+ Nút Luồng" (23-30, screenshots+red callouts), "AI Tự Phản Hồi"/"Inbox Có Người" (31-47), "CRM Và Broadcast" (48-67, **red radial gauge 5→8**), "Tin Nhắn Phong Phú"/"Kích Hoạt Tự Động" (68-83), "API/CLI/MCP"/"Stack Rất Dày" (84-102), "Dự Án Chia Lớp"/"Stack Mặc Định" (103-119, comparison table of ports over **crowd-silhouette photo**), big-word "ChatbotX" reveal (112-119) → 120-128s "Mở Nhưng Có Giới Hạn" AGPLv3 outro.
- **Colour:** black + red; a photographic crowd-silhouette background appears late.
- **Buildable:** red radial gauge/counter; screenshot red-callouts; comparison table; big-word brand reveal; photo-bg scene.

### v12 — "Claude Code Artifacts" (73.0s) — designed bookends + long framed screen-recording
- **Structure:** 0-2s HOOK "CẢ PHIÊN LÀM VIỆC" + kicker "CLAUDE CODE · ARTIFACTS" + "</> → TRANG WEB SỐNG ĐỘNG" card → 3-9s **designed diagram** (nodes Mã nguồn/Kết nối/Hội thoại → Artifacts + mini bar chart, orange/teal) → 10-12s "VIDEO DEMO NGUYÊN BẢN" play-button card → **13-68s ~55s framed screen-recording** (real Claude Code / Artifacts usage, rounded inset container, dark surround, persistent tiny header "VIDEO TRONG BÀI VIẾT" + creator credit, occasional overlay text "Code that's worth showing") → 62-72s outro "Artifacts, now available" → "Claude Code" wordmark (orange logo).
- **Colour:** dark + **orange/coral** (Claude brand).
- **Buildable:** designed intro + **framed screen-recording as b-roll** (rounded inset, small margin, persistent header label) + brand-wordmark outro. Good pattern for "we have a real demo clip" cases.

### v13 — "Codebase Memory MCP" (52.2s) — "Lạch Cạch AI", stock-photo b-roll + reaction + countdown
- **Structure:** 0-2s HOOK "Token giảm 99%? Thật sao?" (orange gradient) → 3-12s **stock-photo b-roll** (mountain, house) with headline overlay + before/after "Trước: gửi code lên cloud / Sau: local knowledge graph" + karaoke caption → 13-16s **article screenshot + animated number 95→99** overlay → 17-24s **node diagram** (Codebase→Memory MCP→Knowledge Graph, blue) → 25-29s "Lợi ích cho solo builder" numbered list with **sequential gold-outline highlight** → 30-35s **terminal** `npm install @codebasememory/mcp` boot log → **36-39s real reaction talking-head** with **pink marker-strike "MIND BLOWN!"** → 40-45s "Cũ vs Mới" reveal + **countdown 3→2→1** big numbers → 46-50s "Cài đặt ngay hôm nay!" + **waveform** → "TAP HERE →" gold button (purple outro).
- **Motion (measured):** karaoke gold word-walk ~0.2s/word; count-up on the screenshot; countdown big numbers.
- **Colour:** warm→blue→purple sectional gradients.
- **Buildable:** stock-photo b-roll with headline overlay; before/after; animated number over a screenshot; **marker-strike highlight text** (pink/accent wipe behind bold word); countdown 3-2-1; waveform CTA; tap-here button.

### v14 — "Codex + Ollama" (95.1s) — "@escbase", green step-tutorial (a literal template output)
- **Structure:** every scene is a numbered **step** with a kicker + step-icon: 0-10s HOOK tweet-screenshot card "Advanced Configuration" → 11-19s **"Cài Ollama"** (Ollama brand card, "Server đã sẵn sàng localhost:11434") → 20-29s **"Tải model"** terminal `ollama pull qwen3-coder:30b` + "19 GB · CODER 30B" card with **progress/RAM bar** → 30-46s **"Nối model vào Codex"** terminal + connector-icon row (green edges) → 47-55s **"Đổi model"** `ollama ls` inventory + dropdown card → 56-69s **"Cho Codex App ghi nhớ"** config.toml code block building line-by-line → 70-81s **"Provider online"** node diagram (base_url/API key/model → custom provider) + checkmark chips → 82-90s **"Test tool trước"** icon grid (web search/browser/computer) + test card → 91-94s **outro** "Template Tạo Video Viral / Biến một URL thành video. · escbase.xyz" (green pill).
- **Colour:** consistent **green** accent throughout; near-black bg with faint particles.
- **Note:** the outro literally advertises a **"turn a URL into a video" template** (escbase.xyz) — i.e. these shorts are *outputs of an automated video-template product*, which is precisely our north-star. The whole video is what a good template pass looks like.
- **Buildable:** numbered step-tutorial spine (kicker+step-icon, monotone accent); terminal blocks; brand cards; progress bars; node diagrams with checkmark chips; icon grids.

---

## PART C — Motion & timing constants (measured from 30fps zooms)

| Behaviour | Measured value | Source |
|---|---|---|
| Caption phrase-swap (calm) | ~0.9–1.0 s/phrase, ~1-frame gap, near-hard swap | v4 @0s zoom |
| Caption phrase-swap (dense narration) | ~0.6 s/phrase, tracks voice | v4 @31.3s zoom |
| Karaoke per-word recolor | ~3–5 frames (0.15–0.25 s)/word, colour-only, no scale | v13 @3s zoom |
| Karaoke caption structure | bright active phrase + dim full-sentence context line beneath | v13 |
| List-row stagger reveal | ~5–7 frames (~0.2 s) apart, fade + slight slide-up, ease-out, NO overshoot | v4 @31.3s zoom |
| Wordmark specular sweep | ~12 frames (~0.4 s) left→right highlight gradient across letters | v4 @0s zoom |
| Chapter glow-bloom transition | old fades ~3f → accent radial flood ramps ~5–6f, peaks, decays ~10f; total ~0.7–1.0 s | v1 @99.3s zoom |
| Number count-up | ~1.5–1.6 s, ease-out deceleration, + sparkle particles | v10 @91.8s zoom |
| Typical scene hold | ~5–6 s (review/template channels), 8–14 s (explainers) | all sheets |
| Motion blur / flying objects | essentially none — entrances are fades/slides/scales, not fast physical flight | all |

**Easing:** everything reads as **ease-out** (settle, no bounce) — I saw **no overshoot/spring** and no motion blur in any of the 14. These videos get energy from **colour blooms, count-ups, staggered reveals, karaoke, and big type**, not from物 kinetic flying. That is an important correction to any "make it bouncy" instinct: the reference craft is *calm motion + loud colour/typography*.

---

## PART D — Techniques to build, ranked by impact

Ranked by (frequency across the 14 × fit to our glow-on-light / self-drawn / brand-locked engine).

**Tier 1 — build first (appear in almost all; directly buildable in HTML/CSS/SVG on light bg):**
1. **The scene template struct** `{kicker, headline(line1 / line2 in accent), content, caption}` — the backbone of v2/v4/v5/v7/v8/v14. One component, huge coverage.
2. **Two-tier bottom captions**: phrase-swap mode (~0.7s, ease-out fade) AND karaoke keyword-recolor mode (active word → accent, ~0.2s/word) with a dim context line under the bright phrase. On light bg: active word → navy or green, rest dark-grey.
3. **Semantic per-section accent** driven by script tags: `error→red, success/topic→#00AA00, highlight→gold, brand→#003BA6`. Switch accent per chapter (v1, v8).
4. **Ease-out count-up** for stats (~1.5s, decelerating, optional sparkle) — v2/v10/v13. Maps to our data-viz.
5. **Staggered list-row reveal** (fade + 8–12px slide-up, ~0.2s stagger, ease-out) with numbered `①②③` badges and optional active-row highlight — v4/v8/v13.
6. **Kicker labels** (uppercase, letter-spaced, dot/step-icon lead) above every headline.
7. **Follow/CTA outro card** (avatar + handle + accent button) and/or **terminal-install CTA** (`brew/npm/git` block) — every video ends on one.

**Tier 2 — build next (frequent, moderate effort):**
8. **Chapter glow-bloom transition** — radial accent-tinted wash opacity 0→~0.7→0 over ~25f under a content cross-fade. On light bg = soft navy/green bloom.
9. **Data-viz components animated in**: donut/ring with center % (sweep-fill), progress bar (fill-to-value), stat grid, node/flow diagram with glowing/coloured connector edges, horizontal timeline of dots, podium/ranked bars — v3/v9/v10/v12/v14. (We already have most; add the *entrance animation* + center-label.)
10. **Chip / tag grids** popping in staggered (icon + label pills) — v2/v4/v5/v7.
11. **Comparison layouts**: side-by-side cards (one highlighted) and header+rows table — v7/v8/v10/v11.
12. **Framed screenshot / screen-recording as b-roll**: rounded inset container, small dark margin, persistent tiny header label, optional overlay text — v4/v5/v12.
13. **Three-font hierarchy**: display headline / sans body-chips / mono terminal. (We're locked to Be Vietnam Pro — approximate with weight+size+tracking; add a mono for code blocks.)
14. **Specular light-sweep** across the hero wordmark (~0.4s highlight-gradient traversal) — v4.

**Tier 3 — selective / harder:**
15. **Big-word background typography** (huge low-opacity word bleeding/drifting behind content) — v6/v11. Easy CSS, use sparingly; on light bg use a pale navy tint.
16. **Marker-strike / highlighter text** (accent bar wipes in behind a bold keyword) — v13 "MIND BLOWN!", v3. We have a marker-wipe concept already (cinematic reel memory); port it.
17. **Countdown 3→2→1** big-number beat — v13.
18. **Notification-card / repo-card mockups** (chat bubble, GitHub repo card with coloured pills) — v3.
19. **Radial gauge counter** (number in a glowing ring, counts) — v11.
20. **Not recommended to chase:** the v9 GPU-rendered 3D spectacle interludes (data-rain, particle funnel, wireframe server). High cost, off-brand for a clean light system; the SVG HUD/timeline approximations (Tier 2) capture 80% of the intent.

---

## PART E — Honesty: what frames could and couldn't tell me

- **Confident (read directly):** all structure/beat maps, scene holds, colour roles, composition, typography hierarchy, content-block vocabulary, transition mechanism, and the specific measured motion timings in Part C (those came from true 30fps/20fps dense montages, not the 1fps sheets).
- **Estimated, not exact:** easing curves (I inferred ease-out from the shape of count-up deltas and the absence of overshoot; I did not curve-fit). Exact per-word karaoke timing varies with speech and I sampled one phrase. Scene-boundary timestamps from the 1fps sheets are ±1 s.
- **Could not determine from frames:** audio/BGM specifics (I did not analyze the audio track; waveforms are *visual* elements in v3/v13, and beat-synced cutting can't be confirmed without the audio — cuts *look* voice-paced, not music-beat-paced). Exact fonts (I can name categories — heavy condensed sans, elegant serif, mono — but not the specific typeface). Whether the "real b-roll" clips (v3/v13/v9) are the creators themselves or stock. The precise opacity/blur values of glows.
- **Cross-checks worth doing later if we want to be exact:** pull the actual keyframe PNGs at the transition boundaries at full res to measure glow radius/opacity, and analyze one audio track to settle the beat-sync question.

---

### One-line synthesis
The reference set is **calm motion + loud colour + disciplined structure**: a repeated `kicker → 2-line accent headline → one content block → running caption` scene, chaptered by semantic-colour glow-blooms, proven by big count-up stats and framed screenshots, closed by a hard CTA. Rebuild that skeleton on our light navy/green brand with ease-out entrances, karaoke keyword-recolor, and animated data-viz, and we match their engagement mechanics without copying their dark neon skin.
