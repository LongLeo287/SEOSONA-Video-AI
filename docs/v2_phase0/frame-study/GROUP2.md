# GROUP 2 — Deep Frame-by-Frame Craft Study (reference slice 15–28)

**Source folder:** `D:\SEOSONA AI\data\Video Template` (sorted by name; this doc covers sorted **index 15–28**, 14 files).
**Method:** `scdet` cut detection + 1 fps contact-sheet montages (timestamp burned into every frame) for the full arc of all 14 videos, then **12 fps burst montages** on representative moments to measure entrance easing, counting-number rates, caption cadence, and transition timing. All claims below come from **looking at frames**, not ffprobe metadata. Timestamps are in seconds from clip start, and are montage-frame accurate to ~±0.1 s (bursts) / ±0.5 s (1 fps sheets).

### Honesty caveats (what frames could NOT reveal)
- **Sub-frame easing curves** are estimated from position/scale/opacity across 12 fps bursts. I can distinguish "pop with overshoot" vs "pure ease-out fade," but exact cubic-bezier control points are inferred, not measured.
- **Audio / voiceover** was not analyzed; I infer karaoke word-timing from the caption's moving highlight, which is a reliable proxy but assumes highlight == spoken word.
- `scdet` at threshold 0.30 found **almost zero hard cuts** across the whole slice (only v19 @0.07/16.83 s and v27 @20.3/43.9/87.4 s). These videos are **continuous soft-crossfade motion-graphics**, so "cuts/sec" is near-zero for most — energy comes from *within-scene* animation, not cutting (a central finding).
- Two clips are 720×1280 (v21, v25); the rest 1080×1920. The lower-res two lose fine text in 1 fps thumbnails; I drilled those less.

### Filename legend (index → file → channel/brand watermark)
| # | Short name | Dur | Dim | Channel watermark | Theme |
|---|---|---|---|---|---|
| v15 | Cognee (self-host memory) | 69 s | 1080×1920 | **LẠCH CÁCH AI** | Dark, chaptered |
| v16 | Comment "AI" / 3 free tools | 54 s | 1080×1920 | **@abhishek.devini** (EN) | **LIGHT** |
| v17 | DESIGN.md (Google Stitch) | 63 s | 1080×1920 | **Công nghệ 24h** | Dark cinematic |
| v18 | DeepClaude | 69 s | 1080×1920 | **kzpn.ai** | Dark, blue orb |
| v19 | Lightpanda (OSS phần 53) | 31 s | 1080×1920 | **@HocAImoingay** | Purple, screenshot tour |
| v20 | Fable 5 returns | 75 s | 1080×1920 | **@centrix.digital** | Dark tech-news (red) |
| v21 | GStack | 139 s | 720×1280 | **Nguyễn Thành Rainmaker** | Dark starfield |
| v22 | Gamma in ChatGPT | 65 s | 1080×1920 | **@sockseo** | Dark space |
| v23 | Google AI Studio → Android | 46 s | 1080×1920 | **@sockseo** | Dark space |
| v24 | Interactions API (Gemini) | 104 s | 1080×1920 | **@sockseo** | Dark space + green |
| v25 | Gemini-SQL2 | 99 s | 720×1280 | **@sockseo** | Dark green |
| v26 | Hindsight (HuggingFace) | 65 s | 1080×1920 | (teal) | Dark + b-roll hybrid |
| v27 | HyperAgent Founding 500 | 94 s | 1080×1920 | **@sockseo** | Dark + interview b-roll |
| v28 | Học Git qua game | 72 s | 1080×1920 | **KNS / Eric Tran AI** | **LIGHT** |

**Six distinct template families in one slice** — the two LIGHT ones (v16, v28) plus the screenshot-tour (v19) are the most directly transferable to our glow-on-light engine; the rest teach structure, pacing, and the near-universal caption system.

---

## Universal spine (present in ~all 14 — read this first)

Every video, regardless of channel, is built on the same skeleton:

1. **Persistent top zone** — a small channel logo/wordmark (top-left) and often a *section-header label* (a short title that names the current beat, e.g. "REVEAL", "Classifier gate", "toàn bộ workflow AI", "Con số nổi bật", "TRỰC QUAN HÓA GIT").
2. **Center focal graphic** — exactly ONE hero object per beat: a card, chat mockup, node diagram, big stat number, gauge, bar chart, code block, brand-tile grid, or product screenshot. It *animates continuously* while on screen (builds, counts, drifts).
3. **Bottom caption band** — 1–2 lines, bottom-anchored, that swap **phrase-by-phrase (~1–1.3 s each)** and highlight **exactly one keyword in the channel accent color**, and in most channels the highlight **steps word-by-word (karaoke) synced to the VO** (~0.3–0.5 s per step). This is *the* engagement engine and is the single most copied element in the whole slice.
4. **Soft crossfades between beats** (~0.3–0.4 s), not hard cuts. The whole old group fades/dims out as the new one fades/rises in.
5. **1–2 accent colors max**, disciplined: dark channels use white text + one or two neons (cyan/magenta, or green, or orange, or red); light channels use near-black text + one or two brand accents.

The perceived pace is *fast* even though hard cuts are near-zero, because captions re-highlight every ~0.4 s and the focal graphic is always mid-build.

---

## Per-video breakdown

### v15 — Cognee (LẠCH CÁCH AI) · dark, chaptered · 69 s
**Format:** the "chaptered explainer" — ~10 beats, each with its **own background color mood** + section label + focal graphic, joined by crossfades.

**Beat map** (1 fps sheet):
- **0–2 s HOOK.** Deep-blue radial-glow bg. Big white left-aligned question "Agent của bạn có nhớ mãi không?" (~3 lines, bold). Tiny pill "LẠCH CÁCH AI" top-center. Hold ~2 s.
- **3–9 s** bg → purple/magenta. Lavender **rounded card** centered ("thử một thứ khiến mình phải" + body), soft glow, with **bokeh light-flare particles** drifting behind (6–8 s). Caption keyword magenta.
- **10–15 s** dark bg; **comment/chat mockup** top-left (red avatar dot "@founder_ai — Memory = mất dữ liệu", stacked reply rows). Problem beat.
- **16–24 s "REVEAL"** — small "REVEAL" pill label above a serif-bold heading "Tự host, mã nguồn mở!" + body paragraph. Breathing purple radial glow.
- **25–32 s** — the ONLY photo beat: a **dimmed real stock photo** (person/room) as bg with two floating compare cards over it: red ✕ "Trước đây: đánh đổi" vs green ✓ "Với Cognee: cả hai".
- **33–42 s** bg → dark green glow; header "Cơ hội cho bạn!"; a **green-check bullet-list card** (3 items).
- **43–49 s** — **giant ghost countdown numerals** "3", "2", "1" (huge, gold/tan, very low opacity, behind text) as numbered steps.
- **50–55 s** navy bg; header "Cộng đồng lớn mạnh"; **huge cyan stat "12.4k"** + tiny "+1.8k tuần này".
- **56–60 s** — **concentric radar/sonar rings** bg; "Agent nhớ mãi, dữ liệu an toàn." summary.
- **61–68 s** — purple gradient → maroon glow; bottom CTA bar "Cognee - Bộ nhớ mãi mãi" + "^^" arrows pointing to pinned comment. End card.

**Motion (12 fps burst 15.0–18.9 s):** section change is a **crossfade ~0.3–0.4 s**; during it a **scrolling ghost-text marquee band** ("Open-Source & Open Coding Models in 2…" sliding diagonally) briefly bridges old→new as connective tissue. Two-line centered caption, keyword steps **yellow** word-by-word ~0.3–0.5 s (mất→kiểm→soát→Minh→cứ→nghĩ→phải). Background radial glow **breathes/drifts** position slowly.
**Typography:** big bold display heading (serif-leaning) ~top; body paragraph small; caption medium. Big:small ratio roughly **4–5:1** (heading vs caption).
**Reusable:** (a) chaptered structure with per-beat bg mood + section label; (b) giant ghost countdown numerals behind a step list; (c) scrolling ghost-text band as a crossfade bridge; (d) huge single stat number in one bright accent; (e) two floating ✕/✓ compare cards over a dimmed photo.

### v16 — Comment "AI" / 3 free tools (@abhishek.devini) · **LIGHT** · 54 s  ★ most transferable
**Background:** near-white with very large, extremely desaturated **pastel bokeh blobs** (faint rainbow) that drift — "airy tech" energy with **no dark**. This is the closest reference to our glow-on-light target.

**Beat map:**
- **0–7 s HOOK.** Small terminal/toast card top-left. Headline **builds word-by-word** in near-black: "Claude" → "Claude Code is" → "…quietly **burning** your **tokens**." (keywords **burning/tokens** in coral/red). Below it a **live token counter decrements**: 178,253 → … → 92,803.
- **7–9 s** "Three free tools", counter settles 92,803; then "**stop it.**" adds on a 2nd line.
- **8–11 s** three tool cards stack in (Graphify, claude-mem, codegraph) as small pill-cards; ghost outline numeral "**01**" fades in.
- **10–21 s Tool 1 Graphify** — wordmark with partial-word accent ("GRAPH" + teal "**IFY**"); a **/graphify terminal card**; a **node-graph builds** (nodes pop, edges draw); "META GRAPHIFY" data panel "-30,002 tokens"; big stats "**-27%**" (gray) → "**-70%**" (green) "fewer tokens".
- **22–33 s Tool 2 claude-mem** — ghost "02"; coral accent; toast notifications stack; "memory, not amnesia." (amnesia coral); "blank slate?".
- **34–47 s Tool 3 codegraph** — ghost "03"; blue accent; "Same idea."; blue node graph; big "**100%**" / "ON YOUR MACHINE"; "STILL CUTS TOKENS **61%**", "**48%**". Summary triad "A **map**, a **memory**, and a **vault**." with keywords **green/coral/blue** matched to three labeled cards MAP/MEMORY/VAULT + a rotated "**100% FREE**" sticker badge.
- **48–53 s CTA** — "Want all three links?"; a **fake IG comment bar** with red send button; the letters "**A**"→"**AI**" typed in red into the box; LIKE/FOLLOW row; end card "@abhishek.devini · MAP • MEMORY • VAULT".

**Motion (12 fps burst 6.4–10.3 s — measured):**
- **Counting number:** continuous decrement, **~3,000–3,500/s**, *decelerating* into the final value, **locks at 92,803 @7.56 s** (ease-out on the count). Tabular figures with thousands commas, "TOKENS THIS SESSION" caption beneath.
- **Word-build headline:** each new word appears as a **light-gray ghost then darkens to full black over ~2 frames (~0.15 s)** — a fade-in-place with a hair of scale, **no bouncy overshoot**. Cadence **~0.3–0.4 s/word**.
- **Section change:** the entire group (headline + number) **fades out together ~0.3 s** → next group fades in. Soft, never a cut.
- **Cards:** slide-in from an edge + fade, **staggered ~0.2 s** apart (Graphify @8.56, claude-mem slides from right @8.90, codegraph up @9.31).
- **Ghost numeral:** slow **fade-in of a light outline** "01", low opacity, ~0.5 s.

**Typography:** heavy near-black sans, tight leading; keyword recolor is the only decoration; big stats (−70%, 100%) are the largest type, **ratio ~6:1** over caption. Full-bleed on the airy bg, contained cards for UI mockups.
**Reusable:** (1) **live counting number** as a hook (down for "waste", up for "growth"); (2) word-build headline with coral problem-keywords; (3) ghost outline section numerals 01/02/03; (4) partial-word accent wordmarks; (5) semantic stat color (gray=bad → green=good); (6) color-coded summary triad matched to 3 cards; (7) rotated "100% FREE" hand-drawn sticker; (8) the type-the-keyword IG comment-bar CTA.

### v17 — DESIGN.md (Công nghệ 24h) · dark cinematic · 63 s
**Background:** near-black with a **top spotlight cone** + **giant ghost outline section numerals** ("01…07") faint in the bg, one per beat. Accent duo **cyan + magenta**.

**Beat map:** 0–5 s DESIGN.md gradient wordmark (".md" lighter weight) + subhead; 6–13 s a **left-aligned chat bubble** stating the problem; 14–20 s huge **cyan→magenta gradient stat "67.8K"** GitHub stars "#236 toàn cầu"; 21–29 s a **dark code-editor card** "Cấu trúc 1 file DESIGN.md" with syntax-colored lines; 30–35 s a **brand-tile grid** (Stripe/Vercel/Linear/Figma… rounded icon tiles pop in one-by-one) "70 thương hiệu"; 36–43 s "Workflow 30 giây" step cards appear sequentially; 44–52 s a **VS bar** "Tooling phức tạp" (magenta) **VS** "Drop-in · 30s" (cyan); 53–56 s an **analogy line building** "DESIGN.md is to design what README.md is to docs." with cyan/magenta keyword coloring + attribution; 57–62 s end card wordmark + **follow card** (avatar "Quốc Lâm IT" + red "Following" button).
**Signature caption:** the current keyword phrase is drawn inside a **thin boxed/underlined rounded rectangle** (e.g. "danh headless browser" boxed) — a boxed-keyword variant of the karaoke highlight.
**Reusable:** giant ghost section numerals as chapter markers; cyan+magenta two-accent discipline; brand-tile grid popping in; VS comparison bar; analogy statement built line-by-line; boxed-keyword caption.

### v18 — DeepClaude (kzpn.ai) · dark, central blue "orb" · 69 s
**Background:** a soft **blue radial orb** glowing at center, dark vignette corners; the orb gently **breathes**. Everything centered and minimal. Accent cyan.
**Beat map:** 0–13 s hook heading "Claude Code… nhưng hóa đơn API?" persists; a small dark "Chi phí token" card → "DeepClaude" card fades in center. 14–19 s "DeepClaude là gì?" + provider pills (DeepSeek/OpenRouter/Fireworks). 20–35 s a **dark env-config card** "ANTHROPIC_BASE_URL = token → backend…" + repo URL. 36–41 s **big cyan stat "×17"** (17× cheaper). 42–56 s "Workflow gọn nhẹ" (Bash/git/subagent pills) + a **checklist card** (checkbox items tick in). 57–68 s summary "Cân bằng năng suất & ví tiền" + github URL card + "mở tả video" CTA.
**Motion:** minimal, calm, premium; small dark cards **fade in at center** (no slide), the orb breathing supplies the only ambient motion; cyan keyword caption.
**Reusable:** central breathing radial glow as the entire "set"; extreme minimalism (one small card at a time, centered); checklist card with sequential ticks; single big multiplier stat "×17".

### v19 — Lightpanda (@HocAImoingay) · purple gradient · **screenshot tour** · 31 s
**Background:** violet/purple diagonal-gradient with a moving light band. This is the **screenshot-tour archetype**: real GitHub-repo / product-website **screenshots panned & zoomed (Ken Burns)** under a persistent title.
**Beat map:** 0–2 s repo file-list screenshot + a **cyan rounded intro card** "DỰ ÁN MÃ NGUỒN MỞ BẠN NÊN BIẾT ĐẾN"; 3–30 s rapid ~1 s/shot tour of README/website screenshots (features, exec-time, memory, comparison cards, "The first browser for machines, not humans"), title "Lightpanda" pinned top the whole time.
**Signature caption:** white text with the active keyword phrase inside a **cyan rounded-rectangle box** each beat ("nó là một", "danh headless browser", "hơn gấp 10 lần", "puppeteer"…). One of only two clips with a real hard cut (@0.07 & 16.83 s).
**Reusable:** cheapest-to-produce faceless format — pan/zoom real screenshots + pinned title + boxed-keyword caption. Good fallback when we lack bespoke graphics. (Ken Burns already exists in our engine.)

### v20 — Fable 5 returns (@centrix.digital) · dark tech-news (red) · 75 s
**Format:** **tech-news standard** — top **news-ticker header**: a red "● TIN NÓNG" (breaking) badge + a scrolling ticker "TIN AI: FABLE 5 TRỞ LẠI · CLASSIFIER · QUOTA". Warm dark **red/maroon radial** theme.
**Beat map:** 0–4 s **F5 app-icon** bounces in + hook "Đã quay lại. NHƯNG KHÓ VUI." (red); 4–12 s "Tin tốt trước" **timeline** "Jun 12 Tạm dừng → Jul 1 Khôi phục" + status pills; 13–27 s "Classifier gate" **diagram card** (Anthropic classifier flow, benign/bypass-blocked colored rows, "false positive" highlighted); 28–39 s "Giới hạn cũng đau" **radial gauge/ring "50% weekly limit"** (orange/red arc meter) + "included → usage credits" + "Đến Jul 7"; 40–47 s "Cảm giác bị lệch" "Model mạnh" card + classifier-vs-allowance pills.
**Motion (12 fps burst 0.0–3.9 s — measured):** the **F5 icon pops in with overshoot** (~0.15 s: @0.41 s it's large & bright, @0.50 s settles smaller) plus a **sparkle glint** and a **persistent diagonal gold shine-sweep** across the icon. Heading rises+fades in below. Red keyword caption steps word-by-word. Section change = **crossfade ~0.3 s** (@3.66 s the whole F5 group dims out).
**Reusable:** the whole **news chrome** (breaking badge + scrolling ticker header) — matches our `news_video_standards.py`; icon **pop-overshoot + shine-sweep glint**; **radial gauge/ring meter** for a limit/percentage; timeline strip; classifier/flow diagram card.

### v21 — GStack (Nguyễn Thành Rainmaker) · dark starfield · 139 s (longest)
**Background:** dark blue-black **starfield** (tiny star dots) + a diagonal accent-line motif + a **giant faint ghost "1"** watermark on the right. Accent cyan + red.
**Beat map (0–47 s of 139):** 0–12 s title + **VS table** "TRƯỚC ĐÂY vs BÂY GIỜ" (roles CEO/Designer/QA/Release Manager rows appear); 13–26 s **big red stat "110K"** GitHub stars + info-card grid building; 27–42 s **huge red stat "810×"** productivity multiplier with a pulsing "</>" code-bracket icon; 43+ s "Quy Trình Sprint" **process nodes** (Think/Plan/Build/Ship colored dots on a vertical flow).
**Reusable:** starfield + ghost-numeral bg for "big claim" energy; big red hero stat numbers; "</>" code-bracket motif; role-comparison VS table; colored process-node flow.

### v22 / v23 — Gamma & Google-AI-Studio (@sockseo) · dark space · 65 s / 46 s
**Template (sockseo core):** deep blue-black **space/particle** bg; real product **screenshots composited into rounded device frames, floating & Ken-Burns'd**; **flow-chip diagrams** connecting steps (e.g. "Apps → Gamma → Connect", "web prototype → native Android") with small pill tags; **green** primary accent; big **red money stat** near the end ("$4.2M ARR"). Kinetic keyword captions.
**v22 beats:** GAMMA hero screenshot → ChatGPT UI screenshots + "Apps→Gamma→Connect" flow chips → deck-preview toasts → numbered prompt-example card (01/02/03) → "$4.2M" ARR stat.
**v23 beats:** "Prompt ra Android app" + Google-AI-Studio logo/badges → "web prototype → native Android" flow → prompt-input card + Kotlin/Compose output chips → **Android Emulator device card + ADB slider** → Google Play internal-test card + export chips (ZIP/GitHub/Android Studio) → developer-review timeline.
**Reusable:** screenshots-in-floating-frames over particles; **flow-chip step diagrams** with pill tags + a traveling progress dot; green accent + red money-stat payoff; device-frame mockups (emulator, phone).

### v24 — Interactions API for Gemini (@sockseo) · dark space + green · 104 s  ★ best diagram animation
Same sockseo template; the **richest progressive diagram** in the slice.
**Beat map:** 0–5 s "Interactions API" screenshot + gradient wordmark build; 6–17 s giant section keyword "**interaction**" with a small dark flow-card below (prompt→text, then state/steps/history pills); 18–37 s "toàn bộ workflow AI" — a **radial node diagram builds**: central "API endpoint" green pill, then a horizontal green backbone + 6 colored satellite nodes (A/chat/image/…/ "</>"), then "một đường chính" with a **dot traveling** the line; 38–47 s+ "Agent layer / không chỉ gọi model" — a horizontal 3-node flow (search→memory→send) on a glowing gradient line with a **white progress dot** traversing.
**Motion (12 fps burst 18.0–21.9 s — measured):**
- Header pill **blooms in**: @18.16 a blurry glow blob → @18.25 a **colored particle burst** → @18.33–18.41 resolves to the sharp green rounded pill (**glow-bloom + particle → focus-resolve, ~0.25 s**, slight overshoot then settle @18.50). It then has a subtle **idle float/bob**.
- Node diagram: @20.83 nodes appear as **out-of-focus colored blobs** → @20.91 a **central sparkle burst** → @21.00–21.16 nodes **sharpen and edges connect** → @21.25–21.33 fully resolved. **~0.4–0.5 s "blurry glow → sharp + wire-up"** entrance (real focus-pull / bloom, with motion-blur/glow during the transition).
- Caption: **karaoke** — a single word turns **orange** as spoken, stepping through "Nó đi từ text generation" ~0.15–0.3 s/word, rest white.
**Reusable:** (1) **glow-bloom + particle-sparkle + focus-resolve** entrance for any node/diagram (our version: CSS blur→sharp + opacity + a brief particle overlay); (2) **radial hub-and-spoke node graph** that builds node-by-node then draws edges; (3) a **dot traveling a path** to show flow/progress; (4) giant section-keyword typography with a small explainer card under it; (5) idle float on header chips.

### v25 — Gemini-SQL2 (@sockseo) · dark green · 99 s (720×1280)
Same sockseo template, **green-dominant** (Gemini brand).
**Beat map:** 0–7 s title + **orbital diagram** (DB cylinder icon + orbit ring + "80%" badge + "PROOT" label) "Vượt 80%…"; 8–16 s **chat mockup** "Doanh thu theo khu vực quý này?" + flow chips (NL→Gemini-SQL2→SQL) + SQL code output + "Gemini 3.1 Pro" badge; 17–28 s "Con số nổi bật" **line-chart card** + big **"~80.0 s"** execution-accuracy stat counting + stat pills (95 databases / Dirty / 37+); 29–40 s "Khoảng cách khá rõ" **horizontal bar chart** (Gemini-SQL 77.14% / Gemini-SQL2 80.04% / Human 92.96%) with a **"+2.90" delta callout badge** (green up-arrow), bars grow; 41–47 s "Chi tiết dễ bị bỏ qua" a "Many → SELECT" self-consistency node diagram (gold accent).
**Reusable:** orbital/orbit-ring diagram; **horizontal bar-chart comparison with a delta-callout badge**; big counting time/accuracy stat; small stat-pill triad; chat + code-output mockup for "ask in NL → get SQL".

### v26 — Hindsight (HuggingFace) · dark + b-roll hybrid · 65 s
**Format:** hybrid — mixes **real stock B-roll** (a street scene w/ motorbike) and **talking-head clips** with text overlays. Teal/green accent, dark.
**Beat map:** 0–2 s **glowing green hook text** "AI của bạn có bao giờ học từ sai lầm?" (bloom glow on the type); 3–9 s moody spotlight bg "bao giờ thấy AI của mình" + a ticker bar @6 s; 10–18 s **street B-roll** with pinned title "Sau: Hindsight tự ghi nhớ" + captions; 19–24 s big teal stat **"79% → 80%"** "Thời gian debug giảm" (ticks up); 25–28 s a **talking-head clip** + comment-card "Nó lưu lỗi thành kiến thức?!"; 29–36 s "LỖI → Memory" section title; 37–42 s a **giant cyan quote-mark ❞ testimonial** block "— Minh, indie founder"; 43–47 s "3 lợi ích cho indie dev" numbered benefit card.
**Reusable:** glow/bloom on hook text; big **quote-mark testimonial card**; stat that ticks up ("time saved"); tasteful B-roll + pinned-title + caption when we have footage.

### v27 — HyperAgent Founding 500 (@sockseo) · dark + interview b-roll · 94 s
**Format:** the most **footage-driven** clip — essentially an **interview/podcast clip** (a man in glasses talking) + **cinematic B-roll** (hands, nature, tree, screen-recs) with **word-by-word kinetic captions** and a few graphic inserts. Closer to talking-head than pure motion-gfx.
**Beat map:** 0–8 s **orbital "$10M The Founding 500"** logo/stat (orange glow ring); 9–17 s talking head + big **"$10,000,000"** overlay + captions; 18–27 s B-roll (tree/hands) + big **serif cinematic text** "The leaders of this era" over footage, word captions; 28–41 s talking head + captions w/ orange keyword; 42–47 s Hyperagent product screenshots + captions.
**Reusable:** big orange money stat with orbital ring; **cinematic serif overlay text on B-roll**; word-by-word caption over talking footage (this is our talking-head engine's lane); orange keyword highlight.

### v28 — Học Git qua game (KNS / Eric Tran AI) · **LIGHT** · 72 s  ★ most transferable structure
**Format:** clean **light screencast-explainer**. Persistent **top header** (section label "TRỰC QUAN HÓA GIT" + title "LearnGitBranching · git commit tree") + big **white content card** center + **bottom gray caption pill** + a credit bar ("FB: KNS… YT: Eric Tran AI"). White/light bg with faint tint.
**Beat map:** 0–6 s git **commit-tree diagram draws on** in the card (main/feature branches, colored commit dots pop, "HEAD" label); 7–16 s a **repo info card** (28.5k stars, JavaScript, MIT, green "Ủng hộ dự án" button); 17–24 s "Cập nhật thời gian thực" terminal card ($ git status) + live-updating tree; 25–35 s "Chế độ Sandbox" console card (git commit/reset commands + tree); 32–39 s "Lộ trình học tập" **lesson table** (Cơ bản/Tự do/Nâng cao columns; HOÀN THÀNH/ĐANG HỌC/ĐANG KHÓA status pills); 40–47 s "Git Golf" **scoreboard card** (CỦA BẠN/MỤC TIÊU/KỶ LỤC with counting numbers).
**Motion (12 fps burst 0.0–3.9 s — measured):**
- Diagram **stroke-reveal**: @0.08–0.25 s the branch curves **draw on** (SVG-stroke style), then commit **nodes pop in one at a time ~0.3–0.5 s** each; "HEAD" yellow label appears @3.58 s.
- **Caption pill** enters @0.25–0.33 s as a **fade + slight scale (~0.15 s)**; header title fades in @0.58–0.66 s; subtitle fades in @0.75–0.91 s.
- Caption pill: gray rounded bar, centered text, **keyword highlighted green**, phrase swaps ~1–1.3 s, keyword **steps word-by-word (karaoke)** within each phrase.
**Reusable (highest priority for us):** the entire **LIGHT layout system** — persistent header + white content card + **bottom gray caption pill with green karaoke keyword** + credit bar; **SVG stroke-reveal diagrams** with node-pop; lesson/status **table card** with colored status pills; **scoreboard card** with counting numbers. This is almost exactly our target aesthetic.

---

## Recurring patterns across the 14 (ranked by frequency)

1. **Bottom keyword-karaoke caption** — 14/14. One keyword recolored to the channel accent, usually stepping word-by-word with the VO (~0.4 s/step); phrase swaps ~1–1.3 s. Boxed-keyword variant in v17/v19. *This is the backbone of engagement.*
2. **Soft crossfades, ~no hard cuts** — 12/14 (scdet ≈ 0). Energy comes from within-scene building, not cutting.
3. **One animated focal graphic per beat** — 14/14 (card / diagram / stat / mockup / screenshot), always mid-build while on screen.
4. **Big single stat number, often counting** — 13/14 (12.4k, 178k→92.8k, 67.8K, ×17, 110K, 810×, $4.2M, ~80.0s, 79%→80%, $10M, −70%…). Counting/rolling is a top hook.
5. **Section-header label + section index** — 11/14 (ghost numerals 01–07 in v16/v17/v21; text labels elsewhere).
6. **1–2 accent color discipline** — 14/14. Dark: white + neon(s); light: near-black + brand accent.
7. **Entrance easing = ease-out fade/slide for text; pop-with-slight-overshoot for icons/nodes** — measured in v16/v20/v24/v28. Heavy bouncy overshoot is *absent*; the "energetic" feel on dark channels comes from **glow-bloom + particle-sparkle + focus-resolve** (sockseo), not from spring physics.
8. **Progressive diagram building** — 8/14 (node graphs v16/v24, flow-chips v22/v23, bar/line charts v25, gauge v20, git-tree v28, orbital v25/v27). Node-by-node then edge-draw.
9. **UI/terminal/chat mockups as "proof"** — 10/14 (light or dark terminal cards, IG comment bars, chat bubbles, env-config cards).
10. **Ghost/watermark giant elements behind content** — 6/14 (countdown numerals, section indices, brand "1").
11. **Native-platform CTA** — v16 (type "AI" in IG comment bar), v17/v20/v22 (follow card with red Following button), v15 ("^^" to pinned comment).
12. **Background is a mood, not a texture** — radial glow/orb (v15/v18/v20), bokeh (v16), starfield (v21/v22/v24), spotlight (v17/v26), gradient (v19); each **breathes/drifts** slowly. Almost never a static flat fill.

---

## Consolidated "techniques to build" — ranked for our engine
(glow-on-light · self-drawn HTML/CSS/SVG · navy **#003BA6** + green **#00AA00** · Be Vietnam Pro)

**Tier 1 — build first (universal + directly on-brand):**
1. **Keyword-karaoke caption band.** Bottom-anchored, 1–2 lines, phrase swaps ~1.2 s, and **step one keyword to green #00AA00 on its beat** (~0.4 s/step, rest navy on light). Add a boxed-keyword variant (thin green rounded outline) per v17/v19. Cite: v28@0.3–3.9, v24@20–22, v15@15–18, v16 headline.
2. **LIGHT layout system (v28 model).** Persistent top header (section label + title) + centered **white content card** (soft shadow, ~24 px radius) + bottom caption pill + tiny credit line. This *is* our target frame. Cite: v28 whole, v16 whole.
3. **Big counting stat number.** Tabular Be-Vietnam-Pro figures, ease-out deceleration, **lock on final** (~1.5–4 s). Down for waste, **up for growth**; color the "good" outcome green, neutral/bad in gray-navy. Cite: v16@3–7.56 (measured ~3.2k/s), v25 "~80.0s", v26 "79→80%".
4. **Semantic stat color pair.** Bad/neutral in muted gray-navy → good result in **green #00AA00** (v16 −27%→−70%). One-line rule already fits our two-color brand.

**Tier 2 — build next (the "motion energy" toolkit, re-skinned to light):**
5. **Glow-bloom + focus-resolve entrance** for cards/diagrams: element enters **blurred + low-opacity + faint colored glow → sharpens to crisp over ~0.35 s** with a brief particle-sparkle overlay at the moment of resolve. Re-skin sockseo's neon bloom as a **soft green/navy glow on white**. Cite: v24@18.1–18.5 & 20.8–21.3 (measured).
6. **Progressive node/flow diagram** (SVG): draw nodes then **draw edges** (stroke-dashoffset), optional **dot traveling the path** for flow/progress. Central hub-and-spoke (v24) and horizontal flow-chip (v22/v23) variants. Cite: v24, v22, v23.
7. **SVG stroke-reveal diagrams + node-pop** (v28 git-tree): branch curves draw on, commit dots pop ~0.4 s apart. Perfect for our self-drawn SVG pipeline. Cite: v28@0.08–3.6.
8. **Radial gauge / ring meter** for a percentage or limit (v20 "50% weekly"). Green arc on light, animated sweep. Cite: v20@28–39.
9. **Horizontal bar-chart comparison + delta-callout badge** ("+2.90" green up-arrow). Cite: v25@29–40. (Overlaps our existing bars component — add the delta badge.)
10. **Icon/logo pop-in with slight overshoot + a one-pass diagonal shine-sweep glint.** ~0.15 s pop, then a light streak crosses once. Cite: v20@0.33–0.5 (measured).

**Tier 3 — structure & CTA patterns:**
11. **Chaptered structure with per-beat background mood + section label**, joined by ~0.3 s crossfades; optional **scrolling ghost-text band** as a crossfade bridge. Cite: v15 whole & @15.7–16.1.
12. **Ghost outline section numerals 01/02/03** behind each chapter (low-opacity stroked numerals) + **giant ghost countdown numerals** for step lists. Cite: v16, v17, v15@43–49.
13. **Color-coded summary triad matched to 3 cards** (map/memory/vault → green/coral/blue). For us: 3 navy cards, keywords in navy/green + one neutral. Cite: v16@42–47.
14. **VS comparison** (two stacked bars/tables, problem vs solution, distinct colors). Cite: v17@44–52, v21@0–12.
15. **Breathing background** — a slow-drifting radial glow / soft bokeh on white (never a static flat fill). Our light version: faint navy+green radial blooms drifting at ~1% motion. Cite: v16, v18, v15.
16. **Native-platform CTA** — a "type the keyword" comment-bar (v16) or a follow-card with the platform's button; "^^" arrow to pinned comment. Cite: v16@48–53, v17@57–62, v20, v15@66.
17. **Screenshot-tour fallback** — pan/zoom real screenshots under a pinned title + boxed-keyword caption when bespoke graphics aren't worth it. Cite: v19 whole. (Ken Burns already in engine.)

**Explicitly NOT to copy:** dark backgrounds (v15/v17/v18/v20/v21/v22/v24/v25/v26/v27 are all dark — our brand forbids it; port their *structure*, not their palette); neon cyan/magenta/orange accents (replace with navy+green); other creators' watermarks/wordmarks; heavy spring/bounce overshoot (the references deliberately use restrained ease-out — match that restraint).

---

### One-line takeaway
The engagement isn't from fast cutting (there almost is none) — it's from **a keyword-karaoke caption re-highlighting every ~0.4 s over one continuously-building focal graphic per beat, on a slowly-breathing background, joined by 0.3 s crossfades.** Our two most valuable references are the **light** ones — **v28** (header + white card + green karaoke caption pill + SVG stroke-reveal) and **v16** (airy bokeh + live counting number + word-build headline + ghost numerals) — which already look like where our glow-on-light, navy+green, Be-Vietnam-Pro engine should land.
