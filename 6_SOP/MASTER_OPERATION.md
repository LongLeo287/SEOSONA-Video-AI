# TÀI LIỆU VẬN HÀNH CHUẨN (MASTER OPERATION)
*Nơi lưu trữ trình tự vận hành của SEOSONA Video Micro-OS.*

Hệ thống hoạt động theo **Trình tự Tuyến tính (Linear Pipeline)** đi từ Lõi (`1_CORE`) ra Không gian làm việc (`4_WORKSPACE`).

## THỨ TỰ VẬN HÀNH TỔNG QUÁT (END-TO-END)

Dù sếp chọn Workflow nào (Video Tin tức, Video Academy, hay Short), trình tự máy móc chạy luôn tuân thủ 5 bước bất di bất dịch sau:

### BƯỚC 1: SCRIPTING (Não Bộ lên Kịch bản)
- **Công cụ:** Gọi LLM Agent (Gemini/Claude) từ `1_CORE/agents/`.
- **Đầu vào:** Lấy kiến thức/SRT từ `2_KNOWLEDGE` hoặc `5_ASSETS/srt_raw`.
- **Đầu ra:** File kịch bản JSON (Phân rõ Cảnh 1, Cảnh 2, Lời đọc, Hình ảnh).
- **Quy tắc:** Mỗi câu không quá 20 từ, dùng phong cách "sếp Chí Quyết".

### BƯỚC 2: TỔNG HỢP GIỌNG NÓI (TTS)
- **Công cụ:** 
  - Video SEOSONA: Dùng Text-to-Speech (TTS) tiêu chuẩn (Giọng AI phổ thông).
  - Video CQ Academy: Kích hoạt `1_CORE/skills/tts_f5.js` (Voice Clone giọng sếp).
- **Đầu ra:** File âm thanh `4_WORKSPACE/output/voiceover.wav`.

### BƯỚC 2.5: VOICE-TO-SRT (Nhận diện Phụ đề) [MỚI]
- **Công cụ:** Kích hoạt mô hình `faster-whisper`.
- **Hành động:** Nghe lại file `voiceover.wav` vừa tạo và xuất ra file `4_WORKSPACE/output/subtitles.srt`. Đảm bảo khớp từng mili-giây phục vụ cho hiệu ứng Kinetic Typography.

### BƯỚC 3: ASSET GATHERING (Săn lùng Hình ảnh)
- **Công cụ:** Kích hoạt Playwright ẩn danh.
- **Đầu vào:** Kịch bản JSON ở Bước 1 (Chỗ nào yêu cầu chụp ảnh Ahrefs/Google).
- **Đầu ra:** Các file ảnh lưu vào `4_WORKSPACE/output/scene_1.png` v.v..
- **Bỏ qua:** Nếu đang chạy Luồng làm video Short (Không cần ảnh).

### BƯỚC 4: THUMBNAIL & METADATA (Bao bì sản phẩm)
- **Công cụ:** Chạy `1_CORE/workflows/workflow4_thumbnail_gen.js`.
- **Hành động:** 
  1. Trộn Logo từ `5_ASSETS/logos` với Text.
  2. Xuất ra 2 ảnh JPG nét căng (16:9 và 9:16).
  3. LLM sinh ra file `metadata.json` chứa Tiêu đề, Tags, Hashtags chuẩn SEO.

### BƯỚC 5: VIDEO COMPILATION (Lắp ráp & Xuất xưởng)
- **Công cụ:** Chạy `1_CORE/skills/render_html.js` (Dùng thư viện html-video & FFmpeg).
- **Đầu vào:** Lấy Audio (Bước 2) + Hình ảnh (Bước 3). Nếu là video Short thì lấy Audio ghép với Chữ chuyển động (Kinetic Typography).
- **Đầu ra:** File MP4 cuối cùng nằm tại `4_WORKSPACE/output/FINAL_VIDEO.mp4`.

---

**CƠ CHẾ KÍCH HOẠT:** 
Khi hoàn thiện, sếp chỉ cần gõ 1 dòng lệnh duy nhất trên Terminal:
`npm run video:short --source="12_cau_hoi.srt"`
Hệ thống sẽ tự động chạy ngầm toàn bộ 5 bước trên.
