# SEOSONA Video — Product Roadmap (đường đi tới sản phẩm)

> Mục tiêu cuối: một **nhà máy video tiếng Việt tự động** đáng tin cậy — đưa input
> (GitHub URL / kịch bản / website / video dài) vào, ra video hoàn chỉnh đúng brand,
> tự chấm chất lượng và tự publish. Tài liệu này là bản đồ phase để đạt điều đó.

_Cập nhật: 2026-06-27 · trạng thái sau đợt hợp nhất engine + dọn dẹp toàn hệ thống._

---

## 0. Quyết định nền tảng: KHÔNG làm lại từ đầu

Làm lại từ đầu sẽ **vứt bỏ phần khó nhất đã chạy được** và phải đối mặt lại đúng
các vấn đề đó. Lý do giữ và đi tiếp:

- **Engine đã hợp nhất về MỘT đường sạch**: `video_engine.py → native_composer.py
  (+ scene_composer, make_video)`. `workflow_router` đã wire lại. **25/25 test pass**,
  `seosona:audit` + `video:audit:integration` đều **PASS**.
- **Các mảnh khó đã tích hợp & hoạt động**: VieNeu voice (local, miễn phí), ASR timing
  (caption RULE #1), HyperFrames render native, mix SFX + BGM ducking, fetch GitHub data,
  clipper (repurpose), scraper. Viết lại = làm lại nhiều tháng tích hợp.
- **Hạ tầng đầy đủ**: 10 agent, 7 skill, 10 JSON template, brand system, 23 SOP, knowledge base.
- **Đã dọn sạch, không nhiễm code cũ**: toàn bộ engine cũ đã gỡ khỏi cây dự án
  (lịch sử git giữ lại bản tracked), file mới không trộn code cũ.

→ **Việc còn lại là VERIFY + HARDEN + POLISH, không phải REBUILD.** Phần "chưa chắc" lớn
nhất chỉ là: *nó đã render ra video thật hoàn chỉnh chưa* — đó là Phase 1.

### Trạng thái hiện tại (snapshot)
| Mảng | Tình trạng |
|---|---|
| Kiến trúc / engine hợp nhất | ✅ Xong (1 đường, test + audit pass) |
| Tính năng create/scrape/repurpose/publish/quality-gate | ✅ Code đủ — ⚠️ **chưa chạy thật end-to-end** |
| Brand SEOSONA (logo/voice/footer/màu) | ✅ Đúng |
| Brand CQA | ⚠️ Logo/voice/footer đúng; **màu accent dùng chung của SEOSONA**; thiếu clip giọng cqa |
| Scene planner từ text bất kỳ | ⚠️ Bản nháp deterministic; path agent/LLM cho chất lượng cao chưa bật |
| Publish (YouTube/TikTok/FB/Drive) | ⚠️ Code có — **chưa có credentials, chưa test** |
| Dashboard / observability | ⚠️ Cơ bản |
| Môi trường | gh ✓ · vieneu ✓ · ffmpeg ✓ · hyperframes CLI (cần xác nhận) |

---

## Phase 1 — VERIFY: chứng minh nó render ra video thật ⛳ (LÀM TRƯỚC TIÊN)

**Đây là cổng quan trọng nhất.** Mọi thứ phía sau phụ thuộc việc xác nhận pipeline
thực sự ra một video xem được. Tới khi bạn *xem* 1 video thật, phần còn lại chỉ là lý thuyết.

**Việc cần làm:**
1. Xác nhận prereq: `gh auth status`, `node -e "require('hyperframes')"`, ffmpeg, VieNeu.
2. Chạy GitHub one-shot: `npm run make:video -- <github_url>` → kiểm `8_WORKSPACE/auto/<name>/`
   có `*.mp4` + `*.srt` + `Thumbnail/thumbnail.png`.
3. Chạy create-từ-text: `npm run video:news -- "<kịch bản tiếng Việt>"`.
4. **XEM video** và soi checklist chất lượng:
   - Giọng đúng (nam, miền Nam, VieNeu — không rớt sang edge fallback).
   - Caption = chữ HIỂN THỊ (SEO/AI/24/7), KHÔNG phải phiên âm (RULE #1).
   - Light mode, crossfade không có khung trắng.
   - Component hiện đúng (không có ô trống — bignum/repo/terminal/gittree...).
   - SFX/BGM cân bằng dưới giọng; logo + footer đúng brand.

**Exit:** có ít nhất 1 video bạn thật sự dám đăng. Ghi lại lỗi thực tế (nếu có) → Phase 2.

---

## Phase 2 — BRAND & QUALITY: chuẩn hoá đầu ra

**Việc cần làm:**
1. **CQA brand đầy đủ**: thêm bảng màu accent riêng cho cqa trong `native_composer`
   (hiện dùng chung palette SEOSONA); bỏ clip `chiquyet_sample_4s.wav` vào
   `7_ASSETS/voice/profiles/`; chạy `npm run video:course` xác nhận đúng brand CQA.
2. **Voice clone**: xác nhận `seosona_ref13.wav` thực sự clone (không chỉ preset);
   tinh chỉnh độ ổn định nếu cần.
3. **Scene planner chất lượng cao**: bật path Scene-Composer agent / LLM
   (`GEMINI_API_KEY`/`OPENAI_API_KEY`) cho heading + phân cảnh tự nhiên hơn,
   hoặc cải thiện heuristic deterministic. (Hiện là bản nháp trung thực.)
4. QA caption/timing trên 5–10 kịch bản đa dạng (số liệu, thuật ngữ tiếng Anh, dài/ngắn).

**Exit:** cả 2 brand + kịch bản VN bất kỳ đều ra video đúng brand, caption chuẩn.

---

## Phase 3 — RELIABILITY: chạy hàng loạt không sập

**Việc cần làm:**
1. **Queue end-to-end**: bỏ item thật vào `0_INPUT_INBOX/production_queue.yaml` →
   `npm run start:queue` → ra video cho từng item.
2. **Xử lý lỗi**: retry, phục hồi khi 1 bước fail, log trung thực; cleanup-on-failure
   (đã có) hoạt động đúng.
3. Đặt tên/đầu ra nhất quán; tránh trùng; idempotent khi chạy lại.

**Exit:** thả N item → ra N video; lỗi được log chứ không crash cả mẻ.

---

## Phase 4 — PUBLISH: phát hành tự động

**Việc cần làm:**
1. Điền credentials: `1_CONFIG/credentials/{youtube,tiktok,facebook,google_drive}.json`
   (copy từ `*.example.json`).
2. Test theo thứ tự an toàn: `SEOSONA_PUBLISH=google_drive` trước (private), rồi
   `youtube` (unlisted), rồi mở rộng.
3. SEO metadata (`seo_optimizer/youtube_seo`) gắn vào upload thật; kiểm tiêu đề/mô tả/tag.

**Exit:** 1 video tự publish lên ít nhất Drive + YouTube (unlisted) với metadata đúng.

---

## Phase 5 — CONTENT ENGINE: scale nội dung

**Việc cần làm:**
1. **News batch**: `python 4_BRAIN/make_video.py --news urls.txt` → feed tin hằng ngày,
   xoay template/theme để không nhàm.
2. **Mở rộng thư viện template**: dùng `native_composer.extract_template()` để biến các
   render đẹp thành template JSON tái dùng.
3. **Lịch tự động**: cron / scheduled agent cho sản xuất hằng ngày không cần người.

**Exit:** tự động sản xuất N video/ngày.

---

## Phase 6 — OBSERVABILITY & feedback loop: nhà máy tự cải thiện

**Việc cần làm:**
1. Dashboard (`9_DASHBOARD`) hiển thị metric thật (đang sản xuất / xong / hàng đợi).
2. Tinh chỉnh `quality_scorer` gate + vòng `analytics_feedback_agent` để chất lượng tăng dần.
3. Theo dõi chi phí/hiệu năng (thời gian render, tỉ lệ fallback giọng).

**Exit:** nhà máy tự giám sát + có vòng phản hồi chất lượng.

---

## Đường găng (critical path) & khuyến nghị thứ tự
1. **Phase 1 (VERIFY) — ngay bây giờ.** Không xác nhận render thật thì mọi phase sau là giả định.
2. Phase 2 (brand/quality) — khi đã có video thật để soi.
3. Phase 3 → 4 → 5 → 6 tuần tự; mỗi phase có exit criteria rõ ràng ở trên.

> Nguyên tắc xuyên suốt: **không trộn code cũ vào file mới** — engine cũ đã gỡ khỏi cây dự án.
> Mỗi thay đổi phải giữ `pytest` + `seosona:audit` + `video:audit:integration` ở trạng thái PASS.
