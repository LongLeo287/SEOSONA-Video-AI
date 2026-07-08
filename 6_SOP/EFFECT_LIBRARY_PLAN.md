# Effect Library — build plan (tiếp tục mai 2026-07-01)

**Mục tiêu (user):** Build FULL một **thư viện effect lưu trữ** cho SEOSONA Video — text-effect, effect,
SFX, transition — **tái dùng across nhiều video để phong phú, KHÔNG nhàm/lặp**. **Tuyệt đối không phụ
thuộc CapCut** (lấy *kiến thức* effect, dựng *native*). Tất cả: free · headless · seek-safe GSAP ·
brand-fit (light-only, blue #2A5BDA / coral #E2724D) · no-bloat · frame-verify từng cái.

## Kiến trúc: effect = LỚP THỨ 4 của hệ library sẵn có (KHÔNG dựng song song)
Hệ hiện tại: `scripts/grow_library.py` nuôi 3 lib **template · component · block**, mỗi lib có
**selector** (`template_picker`, `block_picker`) + catalog (`gen_catalog`). Pipeline nạp→học→tạo:
`2_KNOWLEDGE/hyperframes/LIBRARY_PIPELINE.md`.
→ Thêm **EFFECT library** theo đúng pattern đó:
- **Kho:** một registry effect (đề xuất `7_ASSETS/effects/` + `effects_registry.json` hoặc module
  `4_BRAIN/effect_library.py`) chứa từng effect dạng preset có tham số.
- **Selector:** `effect_picker` — chọn + **xoay effect theo video/scene** (deterministic theo topic+index,
  như `_rot`/`_EXITS`/`accent_shift` đang làm) để 2 video khác nhau → bộ effect khác nhau ⇒ phong phú.
- **Catalog:** đưa vào `gen_catalog` + `grow_library status` (đếm effect, list selector rules).
- **Wire:** `native_composer` gọi effect_picker thay vì hardcode (entrance/exit/text/sfx kéo từ thư viện).

## ĐÃ XONG (đừng làm lại)
- **SFX de-click (afade)** — `native_composer._audio_dur` + vòng mix. ✅ frame-verified (ffmpeg rc=0).
- **SFX sidechain-duck** — BGM né dưới mỗi SFX hit (SFX sum → key → `sidechaincompress` lần 2, ratio 4
  nhẹ hơn voice-duck 8). `native_composer` mix. ✅ filtergraph-verified (rc=0).
- **EFFECT LIBRARY (lớp thứ 4)** — `4_BRAIN/effect_library.py`: **6 transition** (slide-up · rise-fade ·
  zoom-wipe+headline-clip-wipe · drop-dissolve · dissolve · wipe-up) + **5 exit** (fade · slide-left · lift ·
  shrink · sink), **selector xoay theo video** (seed hash → video khác → chuỗi khác). Wired vào native_composer
  (entrance+exit, `_vseed`), gỡ `_entrance_tweens`/`_EXITS` cũ (no dup), hiện trong `grow_library status`.
  ✅ frame-verified 2 render (seed khác → chuỗi khác; recipe mới wipe-up/rise-fade resolve đủ; exit 0).
  ⚠️ KHÔNG trượt ngang (brand): recipe chỉ y/scale/opacity/clip, không x. KHÔNG ffmpeg xfade.
- Đã có sẵn (rich): reveal-item direction rotation `_E`, glow-breathe + blob-drift + ghost-word depth,
  bignum pop/count-up, chart clip-wipe, semantic-SFX + swish/whoosh mỗi cut.

## ĐÃ XONG thêm (đợt 2)
- **TEXT-EFFECT registry** — `effect_library.TEXT_EFFECTS` 5 recipe (rise·word-up·clip-wipe·word-pop·drop),
  word recipe animate `.head .w` span (native_composer `_words()`), xoay khác phase transition → combo.
  ✅ frame-verified (word-up/word-pop hiện đủ, head-top spread 34px).
- **EFFECT overlay registry** — `effect_library.EFFECTS` 2 recipe (light-leak coral · accent-bloom), áp
  SPARSE (~nửa scene, xoay), sau content z0, subtle brand-fit. ✅ frame-verified (light-leak subtle, không che chữ).
- **Vertical safe-zone + căn dọc** — SAFE_* consts + `--sz-*` vars, `.scene` top-anchor (title hết nhảy
  224px→34px), fix bug scale. ✅ (VIDEO_CRAFT_RULES §9).

## ĐÃ XONG thêm (đợt 3)
- **SFX + MOTION formalized** → `effect_library`: `motion_ambient()` (glow-breathe + ghost + blob-drift, 3
  blob-PROFILE xoay/video) + `sfx_variant()` (swish-sequence xoay/video). native_composer gọi thay inline.
  status hiện motion-profiles(3) + sfx-categories(8). ✅ verified (render exit 0, blob/swish khác nhau/video).
- **Template re-skin (capcut-cli 6)** — honest no-dup: **2 component MỚI** `lower-third` (nhãn nguồn/handle) +
  `callout` (caption-pop pill punchy), brand-fit, wired + CSS. ✅ frame-verified. 4 pattern còn lại đã có sẵn:
  gold-title→hero · end-card & subscribe-cta→`cta` (btn param, đã verify "Đăng ký ngay") · hook-question→hero headline.

## ĐÃ XONG thêm (đợt 4 — backlog)
- **Auto-select lower-third** — `make_video` tự đặt lower-third credit nguồn (data THẬT: name • sao • ngôn ngữ)
  lên 1 scene text thừa của repo-video (gated `SEOSONA_NO_CREDIT=1`). callout để sẵn trong toolbox (vocab doc).
- **Talking-head analyzer** — `scripts/talking_head_analyze.py` (`npm run talkinghead:analyze`): detect silence
  (>1s gap) + duplicate-take (difflib similarity, cut earlier/keep retake) từ words.json. Self-tested. Free, no LLM.

## ĐÃ XONG thêm (đợt 5 — smart selection + talking-head)
- **#1 Content-aware SMART selection** — `effect_library.entrance(kind=…)`: transition CHỌN THEO nội dung
  (data→wipe-up/zoom · list→slide/rise · text→dissolve · hook→zoom), vẫn xoay trong subset hợp-nội-dung
  → smart + vẫn phong phú. native_composer truyền comp_kind. ✅ verified (pool đúng theo kind).
- **#1 Flywheel hook** — effect-profile (chuỗi transition) ghi vào obs_metrics (`effects="wipe-up+dissolve+…"`)
  để quan sát + học sau. (Học chất-lượng-per-combo cần tích eval — nối với #4.)
- **#4 Talking-head analyzer wired** — `talking_head_edit --analyze` báo cáo silence + duplicate-take trước khi
  dựng (advisory; region-removal + re-time thật để dành — rủi ro cao trong assembly ffmpeg).
- **#4 Eval** — `eval_judge.judge()` có sẵn điểm `visual_variety`/`brand_fit`; chạy thử: Gemini 429 + Ollama
  (OLLAMA_MODELS chưa set) → rơi về agent-review tier. Agent-review honest: visual_variety cao (nhiều combo),
  brand_fit tốt (đã soi nhiều frame). Eval TỰ-ĐỘNG cần set OLLAMA_MODELS hoặc Gemini quota (blocker môi trường).

## BACKLOG còn lại
1. **Eval tự-động** — set OLLAMA_MODELS (7_ASSETS/models/ollama) để judge chạy local → tích điểm per-video
   → learn_flywheel học combo/template nào điểm cao (đóng vòng chất-lượng).
2. **Talking-head auto-cut THẬT** — xoá region silence/dup + re-time words/cards/sfx (bước lớn, cẩn thận).
3. Talking-head **translate đa-ngữ** (cần LLM). Thêm recipe/component khi cần.

## Nguyên tắc bất di
Native · free · headless · seek-safe GSAP (KHÔNG @keyframes, KHÔNG random) · brand light-only ·
KHÔNG ffmpeg `xfade` (render ta là 1 seek-render liền mạch, không ghép clip) · no-bloat · frame-verify
mỗi effect bằng render thật + trích frame. Nguồn kiến thức: `2_KNOWLEDGE/VIDEO_CRAFT_RULES.md` §8 +
catalog CapCut đã đào (INGESTION_LOG 2026-06-30).
