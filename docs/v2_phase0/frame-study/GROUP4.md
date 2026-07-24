# GROUP 4 — Frame-by-frame craft study

Deep craft extraction for the SEOSONA Video engine rebuild. Analysis only — no engine code touched.
Target brand we are rebuilding toward: **glow-on-LIGHT, self-drawn (HTML/CSS/SVG), brand-locked navy `#003BA6` + green `#00AA00`, Be Vietnam Pro.**

## Files analyzed (20 videos)

**Slice (a) — `D:\SEOSONA AI\data\Video Template`, sorted index 43–56 (14 files):**

| # | short id | file |
|---|----------|------|
| 43 | T43 | Orca biến một lập trình viên thành cả đội agent song song… |
| 44 | T44 | Seedance 2.5 - Ông Hoàng tạo Video thế hệ mới… |
| 45 | T45 | So sánh chi tiết OpenClaw và Hermes Agent… |
| 46 | T46 | SpaceX đang tiến hành mua lại Cursor… (Grok Build) |
| 47 | T47 | System Prompts Leaks… |
| 48 | T48 | ToolJet AI - Nền tảng mở cho app nội bộ… |
| 49 | T49 | Trả tiền API AI mỗi tháng làm gì - LocalAI… |
| 50 | T50 | Tôi mất 3 tiếng làm một bộ slide. NotebookLM… |
| 51 | T51 | Tạo Video Bằng AI Trong 1 Phút… (Pixelle-Video) |
| 52 | T52 | Voicebox - studio giọng nói AI chạy hoàn toàn trên máy bạn |
| 53 | T53 | [THƯ MỜI HỢP TÁC…] TÌM KIẾM 20 FOUNDING MEMBERS (SAA) |
| 54 | T54 | rag fusion.mp4 |
| 55 | T55 | Đây là 3 công cụ AI làm web-app cho những người không chuyên… |
| 56 | T56 | Đây là công cụ AI làm slide miễn phí… (Open Slide) |

**Slice (b) — `D:\SEOSONA AI\data\Video Course` (5 unique; P.4 exists twice, byte-identical, analyzed once):**

| short id | file |
|----------|------|
| C1 | GEO từ con số 0 (P.1) - SEO giờ không còn đủ nữa |
| C2 | GEO từ con số 0 (P.2) - SEO vs GEO - khác nhau như thế nào |
| C4 | GEO từ con số 0 (P.4) - AI trích dẫn nội dung theo cách nào |
| C5 | Làm SEO bao lâu mới thấy hiệu quả |
| C6 | Đừng bao giờ làm SEO nếu bạn vẫn còn giữ 3 tư duy này |

### Method + honest frame limits
- All 1080×1920 (9:16 @30fps) except **T50** 24fps, **T53** 1920×1080 (16:9) 23s, **C5/C6** 576×1024.
- **Beat maps** built from contact-sheet montages sampled **1 frame / 2 s** (5-col grid). Cell index → time: `t = (row·5 + col)·2 s`. **All beat timestamps are ±1–2 s** because of the 2-s sampling grid.
- **Motion / easing** verified with dense **10 fps strips** (cell = 0.1 s) on four representative reveals: T44 7.0–9.5 s, T54 44.0–46.5 s, C1 4.0–6.5 s, C4 28.0–30.5 s. Motion claims for *other* videos are inferred from the family they belong to, and flagged as such.
- **`scdet` hard-cut detection (thr 0.3):** almost all videos returned **0–3 cuts**. These are **not cut-driven montages** — they are single continuous compositions where *elements* animate in/out. Cut counts: T43=3, T46=1, T48=9, T52=3, T53=4, T56=1; every other video **0**.

---

## TWO REGISTERS (the headline finding)

The 20 files split cleanly into two production systems. Our engine should treat them as two distinct **modes**, not one.

**Register A — "Template" (dark motion-graphics).** 13 of 14 template files. Dark navy/near-black bg, ONE saturated accent per video, product-screenshot cards, big-number stats, **per-word karaoke captions**, glow/bloom. Faceless. This is a slick after-effects-style deck.

**Register B — "Course / Doodle" (whiteboard explainer).** All 5 course files + **T53 is a light hybrid**. Dark grid-paper frame + **white crumpled-paper center panel**, **hand-drawn marker doodles** (stick figures, speech bubbles, comic starbursts), a **real presenter photo-cutout PIP** pinned to a corner, a **comic-lettered thesis title** pinned to the opposite corner, **phrase-append all-caps caption bar**. Personality-led.

**For OUR light brand, Register B is the bigger unlock** (we have nothing like it), and **T54 + T53** are the two files closest to our exact target (light bg, single accent, black text) — study those hardest.

---

# PART 1 — TEMPLATE SET (T43–T56)

## Shared template DNA (present in most)
- **Persistent top-left "chapter heading" zone**: a bold 2–3 word section title that swaps per beat while the graphic below changes (T43, T46, T47, T48, T52). Small letter-spaced **eyebrow micro-label** above it (T47, T49).
- **Persistent brand furniture**: tiny logo top-center or top-left + `@handle` watermark top-right (T44 "trạm ai", T46 "@escbase", T45/T47 branded header strip).
- **Bottom-center kinetic caption**, **per-word karaoke** highlight (current word switches to white-bold or accent, rest dimmed) — verified T44 & T54. One short phrase per breath.
- **Single-accent discipline** on near-black; accent used for the highlighted word, key numbers, glow, borders.
- **Card idiom**: product screenshot inside a rounded card with a soft accent border-glow; or a spec/metadata card of chips.
- **CTA outro**: "Xem thêm" / follow-card / URL pill, often with a glow.

### T43 — Orca ADE · dark navy+black, RED accent · 110 s · 3 cuts
- **Beats** (`T43_grid`): 0–8 s ORCA ADE wordmark + orca/shark graphic intro; then chaptered walkthrough — "ORCA LÀ GÌ" (~10 s), "Chạy Song Song" (~24 s), "Điện Thoại Điều Khiển" (~34 s), "Terminal Không Đứt" (~44 s), "Sửa UI Trực Tiếp" (~56 s), "GitHub Vào Thẳng" (~66 s), "SSH Worktree" (~72 s), "Review Ngay Trong App" (~84 s), "Thêm Agent Rộng"/"Công Cụ Kèm Theo" (~92 s), "Cài Đặt Nhanh" (~100 s), "Mã Nguồn Mở MIT" (~106 s), "Xem thêm" CTA end.
- **Composition**: full-bleed dark bg; top-left heading + subtitle; centered product screenshot/UI card with red glow; GitHub star/comment chips.
- **Reusable**: chapter-heading zone that persists while content swaps; red toggle-switch UI chips; screenshot-in-glow-card.

### T44 — Seedance 2.5 · dark navy, MINT/cyan accent · 42 s
- **Beats** (`T44_grid`): 0–3 s "Seedance 2.5 / BƯỚC TIẾN MỚI" wordmark + fanned translucent purple preview-cards; ~4–12 s **big stat "30 GIÂY"** (mint) + **card-multiplication** (1 card → 3) for "nhất quán đa cảnh"; ~14 s→end **bordered 16:9 video-card showcase** of AI b-roll (clockwork, fire-horse, ships, moon) with **source attribution line** "Nguồn: Gorden Sun @… - X" + "PHÁT NGUYÊN BẢN - CÓ ÂM THANH".
- **Motion (verified `T44_motion` 7–9.5 s)**: a **vertical mint scan-line sweeps left→right across the 3 cards** (~1.5 s); cards gently **float/parallax**; spheres glow; caption is **per-word karaoke** (white-bold advancing), resolving into a rounded **pill caption chip**.
- **Reusable (high)**: big accent stat number + small label to its right; **card-multiplication** to show "consistency/multi-scene"; **scan-line sweep** as an energy accent; bordered content-card with attribution line for embedding external media.

### T45 — OpenClaw vs Hermes · dark, blue/pink · 118 s · text-dense
- **Beats** (`T45_grid`): 0–6 s split "OpenClaw vs Hermes" **two-column color-coded comparison card** (purple L / pink R); article/doc cards with header image + body; **animated line-chart draw-on** (growth curve, ~rows 8–9, repeated frames = progressive reveal); **two-column check/cross lists**; dense multi-column text tables. Persistent branded header strip top.
- **Reusable**: two-column comparison card with per-column color; **line-chart draw-on on a card** (maps to our dataviz linechart, static-final reveal); check/cross feature lists.

### T46 — SpaceX/Cursor/Grok Build · dark **starfield+amber bokeh**, amber/cyan · 88 s · 1 cut
- **Beats** (`T46_grid`): chapters "Quyền mua" (slider toggle *chưa chốt deal → đang mua*), "Con số phía sau" (**big-number comparison 60B vs 10B**, amber), "Mảnh ghép nguy hiểm" ("1M H100 eq." / "Colossus" chips, VS card), "Người dùng hỏi gì?" (**icon-chip triplet** Composer/giá/ổn định), "Grok Build" (**VS battle card** with app-icon tiles: Grok Build vs Claude Code vs Codex). End: **escbase.xyz CTA card** (green glow pill button "Biến một URL thành video").
- **Colour/light**: warm nebula/starfield ambient = "tech energy" source, not flat black.
- **Reusable**: big-number comparison (large primary + smaller secondary); icon-chip triplet row; **VS battle card** with logo tiles; slider/toggle state graphic; ambient particle bg.

### T47 — System Prompts Leaks · dark, **GREEN accent** · 93 s  ★ closest template to our green
- **Beats** (`T47_grid`): chapters "ĐIỀU GÌ ĐÚNG SAU CÂU TRẢ LỜI?", "CHỈ DẪN HỆ THỐNG" (green checklist chips), "MỘT KHO – NHIỀU HỆ SINH THÁI" (**hub-and-spoke orbit diagram**: central `system_prompts_leaks` node + app-icon satellites OpenAI/Anthropic/Gemini on a ring, green connector lines), real GitHub README screenshot, "DỮ LIỆU ĐẾN TỪ ĐÂU?" (green check-dot checklist + amber "CẦN KIỂM CHỨNG" caveat chip), "BA GÓC NHÌN" (**3-branch mind-map** node graph), "ĐỌC CÓ PHÊ PHÁN" (green checklist).
- **Reusable (high, on-brand green)**: **hub-and-spoke orbit diagram** for "ecosystem"; **green check-dot checklist** with progressive reveal; **mind-map / node-branch** for perspectives; **amber caveat chip** as the single contrast to green.

### T48 — ToolJet · dark, RED accent · 114 s · 9 cuts (most cutty template)
- **Beats** (`T48_grid`): same chaptered walkthrough family as T43. "80+ Nguồn Dữ Liệu" shows a **number count-up 79→80** (red). Recurring **3D isometric red-cube product motif**. Some chapters use **full-bleed dimmed b-roll** behind the heading ("Triển Khai Linh Hoạt / Build internal apps 10x faster"). "LTS Khuyên Dùng" = **torn-paper receipt card** with checklist. "ToolJet / Xem thêm" CTA end.
- **Reusable**: number count-up for stats; recurring 3D product-icon motif; full-bleed dimmed b-roll as a chapter divider; torn-paper receipt card.

### T49 — LocalAI · dark, AMBER accent · 52 s  ★ cleanest typography
- **Beats** (`T49_grid`): 0–2 s "LOCALAI" huge white wordmark + "0 GPU" big amber + "47K ⭐" badge + `$ docker run localai/localai` terminal chip; **metadata/spec card** (47K stars · Mar 2023 · v4.4.3 + feature tags LLM/Ảnh/Voice); **GitHub star line-chart draw-on** on a white card; **two-line headings with accent highlight on the key line** ("Không cần / **card đồ hoạ**"); **hero big-number "0đ"** (huge orange) + pricing comparison bars; **numbered list with circular badges** (1·2·3 "Ba thế mạnh vượt trội"); **progressive hardware tag-cloud** (NVIDIA/AMD/Intel/Apple Silicon/Vulkan…); "Server AI riêng / **trong một dòng.**" + terminal chip; **follow-card CTA** (@aidev.repo "Theo dõi") + hashtag outro.
- **Typography**: biggest hierarchy jump in the set — wordmark/number ~140 px vs body ~34 px (~4:1). Letter-spaced eyebrow micro-labels above headings.
- **Reusable (high)**: two-line heading with accent-highlighted second line; **hero big-number stat** as the scene's subject; numbered list with circular badges; metadata/spec chip card; terminal command chip (`$` monospace); progressive tag-cloud; letter-spaced eyebrow label; follow-card CTA.

### T50 — NotebookLM prompts · dark, purple/cyan · 64 s · 24 fps
- **Beats** (`T50_grid`): opener "NotebookLM làm slide / NHANH GỌN VÀ ĐẸP HƠN" + **before/after value pills** "LÀM THỦ CÔNG **3 TIẾNG** → NotebookLM **3 PHÚT**" (arrow between, purple→cyan). Then 7 numbered **prompt sections** ("P1 PROMPT 01"… badge top-left, "Chuyên gia thiết kế / SLIDE CHUYÊN NGHIỆP" title, prompt card with "MỤC TIÊU" label). A **persistent slide-cards mockup graphic** (fanned white cards) anchors the bottom of every scene. End "COMMENT 'AI'" cyan CTA.
- **Reusable**: before/after value-pill comparison with arrow; numbered chapter badges (P1…P7); a **persistent motif graphic** that anchors every scene; labelled prompt card; comment-keyword engagement CTA.

### T51 — Pixelle-Video · dark, **per-chapter background COLOR SHIFT** · 63 s
- **Beats** (`T51_grid`): 0–10 s blue-purple bg "1 DÒNG CHỮ / TRIỆU VIEW" + browser screenshots + a **cartoon fox mascot**; ~24 s **big green "3 PHÚT"** + green checklist (Viết kịch bản / Tạo hình ảnh & clip / Lồng tiếng); ~34–42 s "NGƯỜI ẢO ↔ MOTION TRANSFER" **two-column icon comparison** w/ vertical divider (purple bg); ~52–62 s **bg turns GREEN** "MIỄN PHÍ" + green checklist; ~62 s→end **bg deep blue-purple radial glow** "KỶ NGUYÊN MỚI" outro.
- **Reusable (high, structural)**: **whole-frame background hue shift per chapter** (blue→green→purple) to demarcate sections and signal emotional beats; big centered chapter title + accent subtitle; green checklist reveal; two-column icon comparison with divider.

### T52 — Voicebox · dark, RED accent · 151 s (longest) · 3 cuts
- **Beats** (`T52_grid`): same product-walkthrough family as T43/T48; ~17 chapters. Signature addition: a **big lowercase repo-wordmark horizontal text-wipe** ("voicebox" / "jamepepine/voicebox") sweeps across the frame as the **chapter-transition device** between sections. Red spec cards, screenshots, checklists. "Xem thêm" end. (Frames small at this length — detail limited, pattern clear.)
- **Reusable**: big-wordmark horizontal text-wipe as a section transition.

### T53 — SAA Community · **LIGHT cream `#F5EFE6`**, ORANGE `#E8620E`, 16:9 · 23 s · 4 cuts  ★ light register
- **Beats** (`T53_grid`): "AI Automation tutorials" label + **hand-drawn pin/nail scatter doodle** on cream; "sự đang **phát**" (black + orange keyword highlight); SAA dark UI screenshot on cream; **post-composer mockup** (input "Vừa build|" + orange "+ Đăng bài" button + "+5 XP" chip); **level-badge progression** "Level 4: AI Engineer → Level 5: AI Mastermind"; "không phải trường học / **là sân chơi** cho dân automation" (orange keyword); end URL "community.shineaicompany.com".
- **Reusable (high, on-brand register)**: **cream light bg + black heading + single-accent keyword highlight** — this is our exact glow-on-light discipline, just orange instead of navy/green; post-composer UI mockup + XP chip (gamification); level-badge progression; **a hand-drawn doodle element living on a light bg** (bridge to the doodle register).

### T54 — RAG-Fusion · **LIGHT cream `#F2EFE9`**, RED-ORANGE `#E8452A` · 114 s  ★★ closest to our target
- **Beats** (`T54_grid`): a **step-by-step algorithm diagram** that assembles over the whole runtime. Chapters top-center: "MỘT CÂU · MỘT GÓC" → "RAG-Fusion" → "BA CÂU · BA GÓC" → "MỖI CÂU · MỘT BẢNG" → "LẬT SANG CÂU HAI/BA" → "CỘNG ĐỒNG · NHẤT LÊN HẠNG 1" → "GỘP · RECIPROCAL RANK FUSION" → "XÓA · GỘP · TRẢ LỜI" → "BẮT RAG TỰ NÓI LẠI MÌNH". Visual language: **nodes** (filled circles, **red = active / gray = inactive**), **connector lines**, **document skeleton-cards** (rounded rect + horizontal placeholder text-lines) with **rank badges**, and **fusion/merge bars** combining ranked lists into one.
- **Motion (verified `T54_motion` 44–46.5 s)**: active node has a **continuous soft glow-pulse (breathing)**; a **connector line grows/extends** from source toward target (eased, ~0.5 s); a **document card outline appears then its skeleton text-lines populate top-down** row by row; caption is **per-word karaoke** (advancing **red** highlight, rest black). Cream bg, single red accent, black serif-ish body.
- **Reusable (highest priority for us)**: the **entire light-bg diagram vocabulary** — accent/gray node states, growing connector lines, document skeleton-cards with rank badges, fusion/merge bars, and **progressive assembly synced to per-word captions**. This is almost exactly our intended engine, minus color.

### T55 — 3 web-app tools · dark, per-tool accent · 85 s
- **Beats** (`T55_grid`): 0–4 s **big number hero "3" (yellow) CÔNG CỤ**; Tool 1 "⚡ Bolt.new" (yellow, dark bg) heading + **browser-screenshot card** + check-bullet list; Tool 2 "💗 Lovable.dev" (pink accent, **bg tints purple**) same layout; Tool 3 "🌱 Replit" (green accent) same; **"Tóm lại" recap = three color-coded tool tiles** side by side; end "Bạn không cần biết lập trình để bắt đầu" + "Bắt đầu ngay ✨" pill CTA.
- **Reusable**: per-item accent color + emoji-logo (color-coded sections); browser-screenshot card with URL bar; per-item check-bullet list; **color-coded recap tile row**; big-number opener; emoji pill CTA.

### T56 — Open Slide · dark **purple→magenta GRADIENT bg** (shifts), cyan accent · 89 s · 1 cut
- **Beats** (`T56_grid`): opener question "Bạn mất bao nhiêu giờ để làm một bộ slide?" + pain checklist (Cần layout / Chọn màu / Thêm animation / Sửa từng dòng); "Open Slide [Open Source green badge]" + tech chips (Claude Code/Cursor/Codex) + real screenshots + **green `$ harness engineering` terminal**; "Mỗi slide = **trang web mini**" (cyan keyword) + **purple icon-tile row** (Layout/Animation/Biểu đồ/Hình ảnh) + **chat-bubble AI-conversation mockup**; "Không cần designer" + big blue **✓**; "Tải về" checklist + "Hoàn toàn miễn phí"; **strikethrough "old way" list** (~Chỉnh từng textbox~ / ~Kéo từng icon~) replaced by "Chỉ cần mô tả ý tưởng" pill; end "Open Slide / Tương lai của presentation" glow outro.
- **Reusable**: **gradient bg that shifts hue across scenes** (richer than flat); **strikethrough old-way → highlighted new-way pill**; **chat-bubble conversation mockup**; icon-tile row; big single ✓; green monospace terminal callout.

---

# PART 2 — COURSE / DOODLE SET (C1–C6)  ★ the register we don't have

## Shared doodle DNA (all five)
- **Frame layout**: outer **dark grid/graph-paper** background (near-black with faint grid) → inner **white crumpled-paper center panel** (the "whiteboard") where all doodles play → **bottom caption band** on the dark area.
- **Presenter photo-cutout PIP** pinned to a top corner, persistent (top-right in C1; top-left in C2/C4/C5; top-right in C6). Real person, navy polo — the channel's face.
- **Comic-lettered thesis title** pinned to the opposite top corner, persistent for the whole video: hand-drawn outlined lettering, **red + black**, e.g. C1 "SEO CHỈ LÀ / ĐIỀU KIỆN / CẦN", C2 "SEO vs GEO", C4 "AI TRÍCH DẪN / NỘI DUNG / NHƯ THẾ NÀO?", C5 "SEO KHÔNG PHẢI / TÍNH MỘT ĐÊM", C6 "**03** KIỂU NGƯỜI / KHÔNG NÊN LÀM SEO" (number-led).
- **Doodle vocabulary on the white panel**: stick figures (with expressive faces + prop metaphors), **speech / thought bubbles**, arrows, **comic starburst "POW" callouts** for stats & keywords (C1 "40% TRUY VẤN", "GIẢM 34%", "HƠN 65% GEN Z"), **hashtag chips** (#XẾP HẠNG), **comic-X cross-outs** on obsolete items (C2 từ khóa·backlink crossed), **yellow-highlighter marker** underlines/fills on key words, and **real brand logos** (Google, ChatGPT, Gemini, Perplexity) dropped straight into the sketch.
- **Bottom caption band**: **all-caps, bold, phrase-append** (whole phrase appears, next phrase appends/replaces — NOT per-word karaoke). Color varies per video (C1 yellow/white, C2 white with red emphasis lines, C4/C5 lime-green, C6 white+red). Emphasis words switch to red.

## Motion mechanics (verified dense strips)
- **Elements POP in on beat** (`C1_motion` 4–6.5 s): a doodle/logo/text appears in ~1–2 frames (0.1–0.2 s), synced to the narration beat — **not** SVG stroke-by-stroke drawing. Speech bubbles pre-exist empty and text fills them. Occasional **quick color-streak wipe** across text as it lands (C1 "TRƯỚC ĐÂY"). Brand logos (Google) snap in fully-formed.
  - **Big implication for us**: the hand-drawn look needs **static pre-drawn SVG doodle assets that pop/cut in on the beat** — cheap to build, no real draw-on engine required.
- **"Boiling line" animation** (`C4_motion` 28–30.5 s): the comic title + stick figures have a subtle **per-frame outline wiggle/redraw**, giving the "alive hand-sketch" feel. A **star/sparkle orbits** around callout bubbles. **Character mascots** (a robot with laptop + thought-cloud) pop in with a pulsing glow brain.
- **Accumulating "notepad"** (`C5_grid`): hand-lettered notes append line-by-line inside the white panel like real handwriting building up (C5 "SEO = TÁN TỈNH GOOGLE = CÔ GÁI / KHÔNG THỂ MỘT SỚM MỘT CHIỀU").

## Metaphor drawing (the soul of the register)
- C5: **SEO = courting Google = a girl** (stick figure with wedding rings; "không thể một sớm một chiều") + **milestone timeline** (3 tháng đầu / tháng thứ 6 / tháng thứ 9, red highlights).
- C1: SEO **funnel** doodle; celebration figures; "ask ChatGPT instead of Google" figure-and-logo scene.
- C6: perseverance figure lifting weights ("KIÊN TRÌ"); defeated slouch ("THUA CUỘC"); **real photo inserts** (a phone on a desk = "ỨNG DỤNG AI"; two women at a whiteboard = "con người") dropped into the doodle frame — the doodle register is a **hybrid** that also composites real photos/footage.

## Per-video notes
- **C1** (68 s): thesis "SEO chỉ là điều kiện cần"; funnel, logos, GEN-Z stats. Caption yellow/white.
- **C2** (75 s): "SEO vs GEO" two-figure comparison; #XẾP HẠNG chips; crossed từ khóa·backlink; E-E-A-T with heart; yellow-highlighter on "LÀM SEO TỬ TẾ".
- **C4** (60 s): "AI trích dẫn thế nào"; colored concept blobs (green=tên tác giả, yellow=authority, pink=trang khác đề cập), "E-E-A-T +2" hand-lettered, "SEO 2026 → viết cho Google crawl + AI trích dẫn" checklist. Caption lime.
- **C5** (64 s, 576×1024): courtship metaphor + milestone timeline + easy-vs-hard-keyword starburst comparison + accumulating notepad.
- **C6** (60 s, 576×1024): number-led listicle "03 kiểu người"; emotion figures; real-photo inserts; "TOP TỪ KHÓA vs TOP TÂM TRÍ".

---

# PART 3 — RANKED REUSABLE TECHNIQUES (buildable in HTML/CSS/SVG, brand-locked)

Ranked by value to our glow-on-light, navy+green, Be Vietnam Pro engine.

1. **Light-bg step-by-step DIAGRAM vocabulary** (from T54, T47). Nodes with **active(accent)/inactive(gray) states**, **connector lines that grow (eased ~0.5 s)**, **document skeleton-cards** (rounded rect + placeholder text-lines) with **rank badges**, **fusion/merge bars**, **hub-and-spoke orbit** + **mind-map branches**. Assemble progressively, synced to captions. *Navy nodes, green = active/positive, gray = inactive.* This is our single biggest adopt.
2. **DOODLE / whiteboard mode** (C1–C6) — a whole new register for us. White paper panel on a subtle frame, **static pre-drawn SVG doodle assets that pop in on the beat** (no real stroke engine needed), speech bubbles, **comic starburst stat-badges**, **comic-X cross-outs**, highlighter underline, optional **"boiling-line" wiggle** and **orbiting sparkle**. Metaphor drawings (funnel, timeline, courtship). Presenter PIP + comic thesis title pinned to opposite corners. *Redraw in navy/green line-art, green highlighter instead of yellow.*
3. **Per-word karaoke captions** (T44, T54) for the motion-graphics mode: current word → accent/bold, rest dimmed, advancing in VO sync — vs **phrase-append all-caps band** for the doodle mode. Two distinct caption engines by mode.
4. **Hero big-number stat scene** (T49 "0đ", T44 "30 GIÂY", T55 "3", T46 "60B vs 10B", T48 count-up 79→80). Giant accent numeral + small label; count-up animation; two-number comparison. ~4:1 big:small ratio.
5. **Persistent chapter-heading zone + eyebrow micro-label** (T43/T46/T47/T48/T52/T49). A 2–3-word section title that swaps while the graphic changes, with a letter-spaced small-caps eyebrow above it. Gives long videos structure without hard cuts.
6. **Checklist / feature-list cards** with progressive check-dot reveal (T47 green, T51, T55, T56) + **strikethrough old-way → highlighted new-way pill** (T56). *Green checks are on-brand.*
7. **Comparison idioms**: two-column color-coded card (T45), VS battle card with logo tiles (T46), before/after value-pills with arrow (T50 "3 TIẾNG → 3 PHÚT"), color-coded recap tile row (T55).
8. **Per-chapter background treatment**: whole-frame **hue shift per section** (T51) or **shifting gradient** (T56). For light brand: subtle warm/cool cream shifts or a faint navy→green wash to mark beats.
9. **Card idioms for embedded media**: browser-screenshot card with URL bar (T55), bordered content-card + **source-attribution line** (T44), screenshot-in-glow-card (T43/T48). We must keep attribution lines (we already do `.credits.txt`).
10. **Icon-chip / tag systems**: icon-tile row (T56/T51), icon-chip triplet (T46), progressive tag-cloud (T49), numbered circular-badge list (T49), metadata/spec chip card (T49). *Use our 95 Lucide icons + navy chips.*
11. **Transition & energy accents**: **scan-line sweep** across cards (T44), **big-wordmark horizontal text-wipe** as a section break (T52), color-streak wipe on text landing (C1). Sparingly, as glow-energy.
12. **CTA outros**: follow-card with handle+button (T49), "Comment 'X'" engagement (T50), glowing pill + URL (T46/T55/T56), "Xem thêm" (T43/T48/T52).
13. **Terminal command chip** (`$ …` monospace) (T49, T56) for dev-tool topics; **3D isometric product-icon motif** (T48) as a recurring anchor.

---

# PART 4 — RECURRING PATTERNS & Template-vs-Course contrast

| Dimension | **Template (Register A)** | **Course / Doodle (Register B)** |
|---|---|---|
| Background | Dark navy/near-black; some starfield/gradient | Dark grid-paper frame + **white paper center panel** |
| Light | Dark-mode, glow/bloom, single accent | Bright white panel, marker colors, comic red |
| Accent | ONE saturated accent per video (red/mint/amber/green/cyan/pink) | Red comic title + yellow highlighter + multicolor logos |
| Subjects | Product screenshots, UI cards, big numbers, diagrams | Hand-drawn stick figures, speech bubbles, metaphors, real logos/photos |
| Face | Faceless | **Presenter photo-cutout PIP** always present |
| Title | Swapping top-left chapter heading | **Fixed comic thesis title** pinned one corner |
| Captions | **Per-word karaoke** (accent/bold advancing) | **Phrase-append all-caps band** (red emphasis lines) |
| Motion | Sweeps, floats, growing lines, count-ups, glow-pulse | **Pop-in on beat** + **boiling-line wiggle** + orbiting sparkle |
| Cuts | Mostly 0 hard cuts (continuous element animation) | 0 hard cuts (continuous doodle build) |
| Structure | Chaptered walkthrough / stat / comparison | Narrative argument built as a running sketch |
| Our fit | We already do most of this (dark→relight to navy+green) | **New capability** — highest learning value |

**Cross-cutting truths for the rebuild:**
- **Neither register cuts.** Both are single continuous timelines where *elements* enter/move/exit on the VO beat. Our engine should think in **element-level ENTER/HOLD/EXIT keyframes synced to caption beats**, not scene cuts.
- **One accent, hard discipline.** Every template video is monochromatic-accent on a neutral field. For us that means navy `#003BA6` as the structural ink and green `#00AA00` as the single "active/positive/highlight" accent, gray for inactive — mirrors T54's red/gray node system and T47's green.
- **Captions are the spine.** Every video is caption-anchored bottom-center; motion is choreographed to the caption beat. Two caption engines (karaoke vs phrase-append) selectable by mode.
- **Two files are our north star for LIGHT**: **T54** (`rag fusion.mp4`) for the premium diagram vocabulary and **T53** (SAA) for the cream + single-accent-keyword-highlight discipline. **C1–C6** are the north star for the doodle mode we lack.
- **The doodle look is cheap to fake**: static pre-drawn SVG assets popping in on beat + optional 2–3-frame "boil" — no real hand-draw animation engine required.

_All beat timestamps ±1–2 s (2-s montage grid); motion/easing claims verified only for T44, T54, C1, C4 at 10 fps and generalized within each register._
