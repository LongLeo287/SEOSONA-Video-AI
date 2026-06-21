# 🎬 SEOSONA Video Factory (v2.0 Autonomous Edition)

Chào mừng đến với **SEOSONA Video Factory**, hệ thống sản xuất video truyền thông mạng xã hội tự động hóa 100% dựa trên trí tuệ nhân tạo (AI). 
Đây là lõi trung tâm giúp SEOSONA thống trị các nền tảng YouTube Shorts, TikTok, Facebook Reels thông qua tốc độ, số lượng, và chất lượng hình ảnh vượt trội.

---

## 🚀 Tính Năng Cốt Lõi (Core Features)

Hệ thống vừa trải qua đợt Audit và Nâng cấp toàn diện (Giai đoạn v2.0), hiện tại sở hữu các năng lực tự hành (Autonomous) cực kỳ mạnh mẽ:

1. **Hệ sinh thái 19 Dynamic Templates**: 
   - Lõi `template_core.js` xử lý linh hoạt mọi độ dài kịch bản, tự động co giãn Subtitles, bọc Timeline Animation theo điệu nhảy GSAP. Không bao giờ còn hiện tượng lệch tiếng, đứt Sub hay mất hình.
2. **Gen-AI B-Roll Generator (Đạo Diễn Hình Ảnh)**: 
   - Tích hợp cổng kết nối `Luma Dream Machine` / `Runway Gen-3`.
   - Dùng cờ `--generate-broll` để hệ thống tự động vẽ các đoạn phim siêu thực dựa trên kịch bản thay vì dùng ảnh Stock (Có cơ chế Fallback tự động tải video Pexels nếu API lỗi mạng).
3. **Smart Cleanup Manager**: 
   - Module `clean_temp_data.py` tích hợp sâu vào ống xả hệ thống (`pipeline_manager.py`), tự động dọn rác (audio nháp, frame nháp) ngay khi render xong, chống tràn ổ cứng (Storage Overflow).
4. **Offline NLP Fallback**: 
   - Sử dụng thuật toán IF-IDF cục bộ (`llm_engine.py`) để tự trích xuất tiêu đề (Hook, Main Title, CTA) nếu các API GenAI (OpenAI/Gemini) bị lỗi. Đảm bảo dây chuyền sản xuất video không bao giờ chết.

---

## 🤖 3 Siêu Đặc Vụ Tự Hành (Autonomous Agents)

### 1. Trend-Jacking Agent ⚡
- **Vị trí**: `1_AGENTS/trend_jacking_agent/trend_tracker.py`
- **Năng lực**: Quét RSS tự động từ *SearchEngineLand*. Khi phát hiện bài viết có độ Hot cao (Trend), nó sẽ tự động đánh thức hệ thống và chạy thẳng `workflow_video_news.py`. Kênh của bạn sẽ luôn là người đưa tin đầu tiên về các biến động của Google!

### 2. Thumbnail A/B Tester Agent 👁️
- **Vị trí**: `1_AGENTS/thumbnail_tester_agent/ab_tester.py`
- **Năng lực**: Sửa đổi cơ chế sinh ảnh. Thay vì 1 ảnh mù mờ, hệ thống sinh ra **3 biến thể** (Auto, Split, Center layout). Sau đó, mang ảnh đi hỏi OpenAI Vision (GPT-4o) chấm điểm tỷ lệ click (CTR), và chỉ chọn ảnh tốt nhất để gắn vào video.

### 3. Analytics Feedback & Social Auto-Pilot Agent 🧠🚀
- **Vị trí**: `1_AGENTS/analytics_feedback_agent/` và `1_AGENTS/publisher_agent/social_autopilot.py`
- **Năng lực**: 
  - **Học từ quá khứ (Feedback)**: Đọc điểm rơi Retention Rate của khán giả (VD: Giây 30) và phản hồi lại hệ thống để Pipeline tự động chèn thêm SFX Pop/Whoosh vào giây thứ 30 ở video tiếp theo nhằm giữ chân người xem.
  - **Tự động xuất bản (Autopilot)**: Gắn cờ `--autopilot`, hệ thống tự viết mô tả chuẩn SEO có gắn Link và tự động hẹn lịch (Schedule) trên YouTube v3, TikTok API vào đúng khung giờ vàng.

---

## ⚙️ Hướng Dẫn Sử Dụng Nhanh (Quick Start)

Mở Terminal và điều hướng vào thư mục dự án:

**1. Tạo một Video News Cơ bản (Fallback Stock):**
```bash
python scripts/workflow_video_news.py "Đường dẫn bài viết hoặc nội dung văn bản"
```

**2. Tạo Video với Trí Tuệ Nhân Tạo Vẽ Hình (Gen-AI B-Roll):**
```bash
python scripts/workflow_video_news.py "Kịch bản của bạn" --generate-broll
```

**3. Tạo Video và Tự Động Ném Thẳng Lên Mạng Xã Hội (Auto-Pilot):**
```bash
python scripts/workflow_video_news.py "Kịch bản của bạn" --autopilot
```

---

## 📂 Cấu Trúc Hệ Thống (Directory Structure)

- `1_AGENTS/`: Nơi chứa bộ não của các Siêu Đặc Vụ (Trend-Jacking, Thumbnail Tester, Publisher).
- `2_SKILLS/`: Các module chức năng đơn lẻ (Lấy B-Roll, Quản lý ổ đĩa, Kịch bản...).
- `4_BRAIN/`: Lõi ghép nối (Pipeline Manager, Workflow Router, LLM Engine).
- `7_ASSETS/`: Quản lý kho hình ảnh, nhạc, hiệu ứng (BGM, SFX, 19 Dynamic HTML Templates).
- `8_WORKSPACE/`: Nhà máy làm việc tạm thời. (Hệ thống tự động xóa rác tại đây nhờ module Cleanup).
- `scripts/`: Nơi chứa các lệnh Trigger đầu vào của bạn (`workflow_*.py`).

---

*Hệ thống được phát triển và tối ưu độc quyền cho đội ngũ SEOSONA. Đã Audit thành công vào Tháng 06/2026. Mọi thao tác push mã nguồn đã được thông qua giao thức kiểm định bảo mật.*
