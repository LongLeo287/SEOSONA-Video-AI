# SEOSONA — MASTER VIDEO SPEC
> The ONE canonical spec for every faceless SEOSONA video (9:16, OmniVoice CQA brand voice, light brand).
> This is a **thinking framework + strict rules + platform policy**, NOT a rigid mold. Content decides the structure — don't lock into 1 template / a fixed number of scenes.

---

## 0. CORE MINDSET
- **1 video = 1 message.** Viewers scroll at ~1.5s/scene — they must instantly get "what is it, what's in it for me".
- **Show, don't tell.** If you have real data (numbers, commands, comparisons, screenshots), BUILD it out, don't just say it.
- **REAL figures.** GitHub stars, %, price → fetch/cross-check. Fabricating = losing the channel.
- **Visual variety.** A video should have **≥ 3 different visual types** (e.g. bignum + terminal + compare), do NOT repeat one type.
- **Brand is invariant:** light mode, blue `#2A5BDA` + coral `#E2724D` + leaf `#16A34A`, logo + footer + SEOSONA CTA always present; voice/color/theme are locked by the engine — don't set them by hand.

---

## 1. FLEXIBLE ARC (don't lock the scene count — 5 to 9 scenes depending on content)
A good video goes through 4 **beats**, each beat can be 1–3 scenes depending on complexity:

1. **HOOK** (1 scene) — pain point / shocking number. Full at frame 0.
2. **VALUE** (1–4 scenes) — what it is + why it matters. Pick the right visual for each point: repo, compare, terminal, steps, bignum, stats… MORE content means more scenes, LESS means merge them.
3. **PROOF** (0–2 scenes) — credibility: GitHub stars, license badge, benchmark. Skip if there are no real numbers.
4. **CTA** (1 scene) — follow SEOSONA + try it now.

→ **BRAND STANDARD (video-maker_SKILL): 45–60s, 8–12 sentences, 8–11 scenes.** Minimal quick-news 6–7 sentences (~30–40s). **A video < 40s is TOO SHORT (violates RULE #8 ≥45s).**

**Beat rule:** **WRITE FULL SENTENCES** (one complete thought ~12–18 words, NO stub sentences of 3–4 words) → the voice is long enough, the video is 45–60s. Each scene ~4–6s. Full hook at frame 0 (hero).

---

## 2. COMPONENT LIBRARY (14 types — choose freely, don't repeat one type)
Currently in the `native_composer` engine (all render-safe, pure HTML/CSS):
`bignum` (big number) · `repo` (GitHub card) · `compare` (coral-left old / blue-right new) · `terminal` (real command) · `steps` (3–4 numbered steps) · `badges` (labels) · `gittree` (git log graph) · `cta` · `stats` (3 number cards) · `quote` (large pull-quote) · `tip` (💡 takeaway box) · `feature` (emoji + title + sub) · **`chart`** (bar chart — data viz) · **`mockup`** (browser/dashboard window — simulated screenshot).

**🎨 HERO scene** (anti-monotony): any scene with `"hero": true` → **bold full-bleed accent-color background, white text** (instead of light background + card). Use it for the HOOK so every video opens with a striking color block.

**🔁 ROTATE ACCENT (anti-duplication):** the engine automatically **rotates the palette by topic** (`accent_shift` auto-derived from the output name) → **2 videos from the SAME template still differ in color** (video A coral-dominant, video B blue-dominant…). Deterministic, not random (safe for HF). Pass `accent_shift=0/1/2` to force it. → The same template no longer produces identical videos.

Choose by **the nature of the point**, not by template:
- A single number/price/scale → `bignum` · many numbers (benchmark) → `stats`
- Introduce a repo/tool → `repo` · "old vs new" → `compare` · install/run → `terminal`
- List steps → `steps` · highlights with icons → `feature` · credibility/traits → `badges`
- A quote/argument (a viewpoint) → `quote` · the core thing to remember → `tip` · git/commit → `gittree`

*Place a component at scene 0 or ≥ 2; keep scene 1 as "bridging" text. Need a type that does NOT yet exist (browser/window, a real screenshot `shot`, tagcloud, timeline) → note it down to add to the engine in a render-safe way (HTML/CSS, NOT inline-SVG / absolute / image embedded in the scene), don't force data into the wrong type.*

### TEMPLATE philosophy (important) — NOT hard-locked
A template is **only a reference sample**, NOT a rigid mold. Content decides the frame.
- Frames/scenes with the **same style** → group into 1 template (a template richer in frames).
- A **very different style** → split into a NEW template (don't merge carelessly).
- **The more distinct templates → the more diverse the videos.** There are currently 9: `repo-showcase`, `tool-walkthrough`, `ai-news-flash`, `resource-list`, `insight-explainer`, `tutorial-gittree`, `benchmark-news` (stats+feature), `opinion-insight` (quote+tip+feature), **`seo-explainer`** (SEO/Marketing).

### SEO/Marketing topics (SEOSONA's CORE domain)
SEOSONA is an SEO/Marketing brand — the engine fits this topic even better than AI/dev. Use the `seo-explainer` template
or freeform with **non-dev** components: `bignum` (traffic/%, ranking) · `compare` (old SEO vs
SEO in the AI era — matches the original brand slide) · `steps` (SEO process) · `feature` (ranking factors, tips) · `tip`
(the core thing) · `stats` (3 metrics) · `quote` (a viewpoint). **Avoid** `repo`/`terminal`/`gittree` (code-specific).
SEO topics: Google update, AI Overview/GEO/AEO, E-E-A-T, keywords, content, backlink, local SEO, traffic.

**2 ways to create a video (choose by need):**
1. **By template** (fast): `make_video_from_template(name, content, dir)` — fill in an existing template.
2. **FREEFORM (no template lock):** `make_video_custom(dir, scenes_spec)` — assemble scenes yourself from the 14 components based on content: which component, what order, how many scenes is all decided by content. `scenes_spec` = list of `{"seg","kicker","h1","h2","acc","comp":(kind,data)}`. → Use when the content doesn't match any template / you want a custom mix.

*A component that does NOT yet exist (multi-card dashboard, UI mockup/screenshot, image, animated chart, custom effect) → add it to the engine in a render-safe way then use it in freeform. Don't force content into the wrong component.*

### Audio (SFX + Voice + BGM)
- **SFX (17 cues):** transition (6 rotating types) · impact (soft/deep/hit) · ui (positive/click/success/pop/notify) · typing · riser. The engine attaches them per component — each type has its own sound, no repeated beep.
- **Mix:** Voice is dominant (always clear). **BGM auto-ducks under the voice** (sidechain) — loud at intro/outro/silences, quiet while speaking. The end of the chain has loudnorm -14 LUFS + a brickwall limiter (TP < 0, no clipping).
- **BGM by mood:** `music="tech|news|insight"` (drop royalty-free files into `7_ASSETS/audio/bgm`, map in `BGM`). ⚠️ Viral/chart music **is copyrighted** → don't mux it into the file (risk of being muted/removed, especially for Ads); use the platform's sound library for hot music.

---

## 3. HOW TO WRITE (better content)
**HOOK** = a pain-point question OR a shocking number, full at frame 0. Plant a question in the viewer's mind.
- ✅ "Trả tiền API AI mỗi tháng có làm bạn mệt mỏi?" · "Chạy mọi model AI mà KHÔNG cần GPU."
- ❌ "Hôm nay mình giới thiệu…", greetings, putting the number at the end.

**BODY** — each sentence is **1 point, ≤ 16 displayed words**, active spoken language, with proper names + real numbers.
- `compare`: left = the old way (3 ugly dashes), right = the product (3 winning points — always blue).
- `terminal`: real command + 1 `ok` result line.
- `steps`: 3–4 short, parallel items.

**2-TONE HEADING** — `h1` navy = the subject, `h2` accent = the punchline; ≤ 4 words/line.

**CTA** (fixed style): "Go to [name] to try it now. Follow SEOSONA for more tips." → `Theo dõi SEOSONA / xem thêm mỗi ngày`.

**RETENTION SCIENCE (Shorts)** — from `claude-youtube` (MIT, 2026-07-02):
- **Value prop in the first ~5s**, hook decision is sub-second → land the promise/question immediately (frame 0).
- **Pattern-interrupt every 2–3s** for Shorts (a visual/verbal change: new scene, number reveal, component, SFX) — this is why we never let a scene stall.
- **Energy = gradual slowdown**: open at the HIGHEST energy (HERO hook), then ease — don't build up slowly.
- Benchmark to beat: **~70%+ retention at 30s**. If the first 10–15s is weak the whole video dies → over-invest in the hook.

---

## 3b. CONTENT CRAFT — grounded in `2_KNOWLEDGE/domain_skills/`
The script is the product. These distill the ingested SEO/copywriting/design skills; read the
full `SKILL.md` for depth (`seo-audit`, `copywriting`, `ogilvy`, `stop-slop`, `content-strategy`,
`marketing-psychology`).

- **Pick a NAMED hook type** (`copywriting/references/short-form-structures.md`): **Curiosity** (hidden
  cause/method) · **Value** (concrete promise / warning) · **Story** (transformation / mistake) ·
  **Controversial** (bold, defensible). Write 2 for A/B, each a different type.
- **Pull ONE persuasion lever for the HOOK + ONE for the CTA** (`marketing-psychology`): Curiosity Gap /
  Zeigarnik open-loop / Loss-Aversion for the hook; Peak-End / Reciprocity / Scarcity for the CTA — each
  must ride on a REAL fact (never fabricate the number/proof/urgency it leans on).
- **Headline carries 80% of the value** (Ogilvy). The hook must promise ONE concrete benefit or
  spark ONE curiosity gap — specific, not vague. Test: would a stranger stop scrolling?
- **One idea, one CTA, one action verb.** Don't stack asks. Lead with the benefit, not the feature.
- **Earn every claim.** Real, cited numbers only — no superlatives ("tốt nhất", "số 1"), no
  fabricated social proof. (Enforced by `content_moderation`.)
- **Kill AI-slop** (`stop-slop`): ban clichés — "trong thời đại số", "không thể phủ nhận",
  "hãy cùng khám phá", "đóng vai trò quan trọng", "delve into", "game-changer". Write like a
  sharp human. (Flagged by `content_moderation`.)
- **SEO angle** (`seo-audit` / `content-strategy`): target ONE clear search intent / keyword per
  video; answer the question a viewer would type. For GEO/AEO, structure so an AI can quote you.
- **Design honesty** (`web-design-guidelines`, `make-interfaces-feel-better` + `DESIGN.md`):
  one focal point per scene, real hierarchy, brand colors — never decorate for its own sake.
- **Frame-0 = thumbnail packaging** (`claude-youtube` CTR science): the hook overlay is **≤5 words**
  (3 ideal), **1 focal point + 30–40% negative space**, one strong emotion; do NOT duplicate the exact
  hook text between the on-screen frame-0 and the post caption/title. A viewer decides in < 1 second.

---

## 4. 🔴 HARD RULES (violation = REDO)
1. **TEXT ≠ PHONETICS (RULE #1):** on-screen text = the correctly-spelled display form (`AI`, `GitHub`, `24/7`, `159K`); the pronunciation is kept SEPARATELY in the `lexicon`. Do NOT write "ây ai" on screen.
2. **FULL HOOK AT FRAME 0:** scene 0 shows the full hook right at second 0 (= the thumbnail). The engine renders scene 0 static.
3. **REAL FIGURES:** fetch from GitHub / the primary source. Don't fabricate stars, %, price.
4. **≥ 3 DIFFERENT VISUALS/VIDEO:** don't repeat one component. Avoid an "all text" video.
5. **KARAOKE & TEXT in the SAFE ZONE:** not flush against the bottom/edge (see §6 per-platform safe zone).
6. **CORRECT COMPARE colors:** coral left (old/bad) / blue right (new/winner). Don't flip them.
7. **SEOSONA CTA** on the last scene, always present.
8. **VERIFY before delivery** (don't fabricate): extract frames (`ffmpeg -i v -ss T -frames:v 1`, use output-seek or `select`), check: no black/empty frames, loudness ~ -14 LUFS, **True Peak < 0** (no clipping), all components present, correct duration.
9. **FILENAME = POST CAPTION:** `<Vietnamese hook WITH DIACRITICS> #SEOSONA #xuhuong #<topic> (9x16).mp4`. Avoid the forbidden characters `< > : " / \ | ? *`.
10. **VARIED SFX:** whoosh on scene change, impact for numbers, keystrokes for terminal, UI for badge/CTA (the engine handles it per component — don't turn it off).

---

## 5. SEO (TikTok / Shorts / Reels)
- **Retention:** hook < 2s; change scene every 3–4s; no "stalling".
- **Keywords in on-screen text** (OCR + visible to the reader): tool name + topic (AI, open source, free) in the heading/kicker.
- **Caption/Title:** `<Name> — <one-sentence benefit with a keyword>`. Description: 1–2 value sentences + GitHub link + "Follow SEOSONA…".
- **Hashtags 5–8:** broad + niche. Default `#AI #AITools #congnghe #mannguonmo #SEOSONA` + niche (`#ClaudeAI #AIAgent #RAG #LLM #vibecoding #opensource`).
- **A/B hook:** write 2 hooks/topic, each from one of the **4 named hook types** (choose by goal):
  **Curiosity** (hidden cause/method) · **Value** (concrete promise / warning) · **Story** (transformation / mistake) ·
  **Controversial** (bold defensible claim). Phrasing templates + Story-Arc/POV structures in
  `2_KNOWLEDGE/domain_skills/copywriting/references/short-form-structures.md`. Post the strong one, keep the other for a repeat.
- **Persuasion lever:** pick ONE lever for the HOOK and ONE for the CTA (Curiosity Gap · Zeigarnik open-loop ·
  Loss-Aversion · Social Proof · Scarcity · Peak-End · Reciprocity — see `[[marketing-psychology]]`). It must ride
  on a REAL fact from KeyFacts — never fabricate the number/proof/scarcity it leverages.

---

## 6. 📋 PLATFORM POLICY (MUST grasp — to avoid reduced reach / removal / ban)

### Common to all 3 platforms
- **Original / transformed content:** Do NOT repost someone else's video verbatim. We re-create it in our brand → fine. Don't use copyrighted footage/screenshots beyond fair use; displaying public GitHub data is OK.
- **Copyrighted music:** use music from our own library (`7_ASSETS/audio/bgm`) or royalty-free/licensed music. Commercial (hit) music → gets muted/removed, especially when running Ads.
- **AI disclosure:** the voice is AI TTS. Not impersonating a real person → low risk; but if the platform requires an "AI-generated/altered" label for realistic synthetic content, then TURN that label ON (TikTok AI-label, YouTube "altered content", Meta AI label).
- **No other-platform watermarks** (TikTok/CapCut logo on a video posted elsewhere → reduced reach). Export clean.
- **Honest claims:** "free", "159K stars", "6x faster" MUST be true (matches rule #3). No false clickbait.
- **Content safety:** our tech/AI topics are inherently low-risk (no violence/adult/medical/political). Avoid: instructions for bypassing security/jailbreaking, financial/investment claims guaranteeing profit.

### TikTok
- 9:16 1080×1920; best duration 15–60s (supports up to 10 minutes).
- **Safe zone:** leave **right ~120px** (like/share buttons), **bottom ~150px** (caption + @handle), **top ~100px**. → our karaoke/footer is already in the safe middle-bottom; keep important text in the central frame.
- Music: business accounts MUST use the **Commercial Music Library**; hot music is blocked for commercial purposes.
- Branded/Ads: add the "Paid partnership"/Spark Ads label when it's an advertisement.
- External links only in the bio (organic doesn't allow links in the caption).
- Banned: misinformation (medical/election), "follow for follow" spam, banned hashtags.

### YouTube Shorts
- 9:16; **≤ 3 minutes** to count as a Short (we are always < 40s → fine).
- **Safe zone:** leave the **bottom** (title + @handle + buttons), the **right** (like/dislike/share). Don't put important text/CTA at the bottom.
- **Originality:** "reused/non-transformed repetitive" content can NOT be monetized → we must build it ourselves, add value (which we're doing right).
- Music: YouTube Audio Library or licensed; watch out for Content ID claims.
- Declare "altered/synthetic content" if it's realistic-fake. Metadata/thumbnail must not mislead.

### Facebook (Reels / Post / Ads)
- **Reels:** 9:16, up to ~90s. **Post video:** flexible. Follow Community Standards.
- **Ads (Meta Advertising Policies — the strictest):**
  - No false/exaggerated claims, no unrealistic "before/after", no targeting "personal attributes" ("you are in debt…"), no excessive clickbait/emoji.
  - The landing page must work and match the ad content.
  - Some industries need permits/restrictions (finance, health…). Tech/AI is usually OK.
  - Music/footage must be licensed (Meta Sound Collection to be safe).
  - Social/political ads must declare AI.
- Branded content: use the "Paid partnership" label. Reels music: licensed library; business accounts have hot-music restrictions.

### Quick safe-zone table (px on the 1080×1920 frame)
| Platform | Top | Right | Bottom |
|---|---|---|---|
| TikTok | ~100 | ~120 | ~150 |
| YT Shorts | ~80 | ~110 | ~160 |
| FB Reels | ~90 | ~110 | ~150 |
→ **Keep important text in the common safe frame: top 110 / right 120 / bottom 160.** (The engine keeps the footer/karaoke in the middle-bottom area; check when you change the layout.)

---

## 7. FILL-IN PROMPT (per video — fill it in then hand to the Scene-Composer)
```
TOPIC:         <repo URL / news / concept>
PLANNED BEATS: HOOK + <n value scenes> + <proof?> + CTA   (5–9 scenes, by content)
TEMPLATE:      <repo-showcase | tool-walkthrough | ai-news-flash | resource-list | insight-explainer | tutorial-gittree | or custom scenes>
REAL DATA:     fetch_github(<repo>)  →  stars/license/language
FILENAME:      <hook WITH DIACRITICS> #SEOSONA #xuhuong #<topic> (9x16)

HOOK (×2 for A/B):  1) ...   2) ...
SCRIPT (1 sentence/scene ≤16 words, display form):
  0 [h1 / h2] ...
  ... (all the scenes you chose)
VISUAL per scene:  <bignum | repo | compare | terminal | steps | badges | gittree>  (≥3 different types)
DATA:  repo/★/badges = slots (auto) · terminal/compare/steps = write yourself (real commands/points)
LEXICON: { "<hard word>":"<pronunciation>" }   # e.g. Docker→"đốc cơ", npm→"en pi em"

POST:  caption = filename · hashtags 5–8 · platform: <TikTok/Shorts/Reels> → check safe-zone + music license + AI label if needed
```
→ Render: `make_video_from_template(...)` or `python 4_BRAIN/make_video.py <github-url>`.

---

## 8. STANDARD SAMPLE EXAMPLES (rendered and passing)
`9_PROMPTS/video_scripts/`: `local-ai-engine.md` (repo-showcase) · `file-to-markdown.md` (tool-walkthrough) · `leaked-system-prompts.md` (ai-news-flash 6 scenes) · +3 more. Open them to see a complete, standard-compliant script.
