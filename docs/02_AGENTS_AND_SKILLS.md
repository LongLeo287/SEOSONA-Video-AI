# Danh sách Agents và Kỹ năng Python

Tài liệu này liệt kê bộ não nhận thức (Agents) và tay chân thực thi (Skills) của SEOSONA Video. Nhấn vào các thẻ để xem chi tiết.

## 🤖 Lớp Nhận Thức: 17 AI Agents (`1_AGENTS/`)
Đây là những Persona chịu trách nhiệm tư duy, lên kế hoạch và viết kịch bản trước khi mã code can thiệp.

<details>
<summary><b>1. Nhóm Quản trị & Điều phối (3 Agents)</b></summary>
<br>

- 👑 **`hermes_agent`**: Kiến trúc sư trưởng, điều phối việc gọi các công cụ kỹ thuật và chuyển giao data.
- ⚙️ **`seosona-video-operator`**: Hệ thống Operator chạy ngầm (Nhân vật cốt lõi thứ 17).
- 🎭 **`personas`**: Định dạng gốc (Base definitions) chứa đặc điểm tính cách, giọng điệu cho toàn bộ agents.

</details>

<details>
<summary><b>2. Nhóm Nghiên cứu & Dữ liệu (2 Agents)</b></summary>
<br>

- 🔍 **`researcher_agent`**: Máy ủi dữ liệu, chuyên cào nát các trang web để tổng hợp sự thật (facts).
- ⛏️ **`scraper_agent`**: Cánh tay phải của researcher, thực thi các lệnh bóc tách HTML/JSON.

</details>

<details>
<summary><b>3. Nhóm Sáng tạo Nội dung & Kịch bản (4 Agents)</b></summary>
<br>

- ✍️ **`writer_agent`**: Thợ viết kịch bản đa năng cho các dự án thông thường.
- 🎯 **`seo_writer_agent`**: Viết kịch bản video sao cho từ khóa khớp với hành vi tìm kiếm.
- 🎠 **`carousel_writer_agent`**: Chuyên gia sáng tạo nội dung định dạng trượt (carousel) cho LinkedIn/Instagram.
- ✂️ **`repurposer_agent`**: Cắt nhỏ video/podcast dài thành nhiều luồng nội dung (shorts, reels).

</details>

<details>
<summary><b>4. Nhóm Tối ưu hóa & MXH (4 Agents)</b></summary>
<br>

- 📈 **`seo_optimizer`**: Tối ưu từ khóa cho Youtube/TikTok (Title, Tags, Meta Description).
- 🔥 **`trend_jacking_agent`**: Kẻ đu trend, rình rập Twitter/Tiktok để chớp thời cơ làm video bám xu hướng.
- 💬 **`social_media_agent`**: Thợ săn view, chuyên giật tít và viết caption tạo hiệu ứng chim mồi.
- 🖼️ **`thumbnail_tester_agent`**: Phân tích ảnh bìa bằng thị giác máy tính và tiến hành A/B Testing.

</details>

<details>
<summary><b>5. Nhóm Kiểm duyệt & Đăng tải (4 Agents)</b></summary>
<br>

- 🛡️ **`quality_reviewer`**: Người kiểm định chất lượng cuối cùng (tìm khung hình đen, lỗi âm thanh).
- 📝 **`editor_agent`**: Tổng biên tập, người soát lỗi và sắp xếp lại cấu trúc mạch truyện.
- 📊 **`analytics_feedback_agent`**: Thu thập và phân tích các chỉ số giữ chân người xem (retention metrics).
- 🚀 **`publisher_agent`**: Đặc vụ nắm API để ấn nút Publish lên các nền tảng MXH.

</details>

---

## 🛠️ Lớp Thực Thi: 24 Python Skills (`2_SKILLS/`)
Các đoạn mã Python nguyên thủy (Native) để xử lý trực tiếp tín hiệu Audio/Video/Text.

<details>
<summary><b>🔊 Nhóm Kỹ năng Âm thanh & Giọng nói (7 Skills)</b></summary>
<br>

- 🎙️ **`tts_generator`**: Module phát sinh Giọng nói AI nói chung.
- 🗣️ **`voice_cloner`**: Lõi gọi Engine F5-TTS và OmniVoice để nhân bản giọng 0-shot.
- 🧹 **`audio_cleaner`**: Xóa tiếng ồn nền, lọc xì và chuẩn hóa âm lượng (Normalize).
- 🎛️ **`audio_mixer`**: Trộn nhiều track âm thanh lại với nhau (Giọng đọc + BGM + SFX).
- 🔊 **`sfx_mixer`**: Căn giờ và chèn đè các tiếng "whoosh", "pop", "ding" chuyển cảnh.
- 🫁 **`os_humanizer`**: Bơm các khoảng nghỉ, tiếng thở để làm giọng AI trở nên tự nhiên.
- 📝 **`srt_maker`**: Ép file âm thanh vào Whisper để lấy độ trễ (timestamp) đến từng chữ một.

</details>

<details>
<summary><b>🎞️ Nhóm Kỹ năng Hình ảnh & Video (6 Skills)</b></summary>
<br>

- 🖼️ **`thumbnail_maker`**: Cắt ghép hình ảnh tự động qua thư viện Pillow/OpenCV để tạo Thumbnail.
- ✂️ **`video_clipper`**: Cắt trích đoạn video theo mili-giây.
- 📸 **`visual_fetcher`**: Tải ảnh hàng loạt từ các link URL thu thập được.
- 🎞️ **`b_roll_fetcher`**: Tìm và tải các đoạn video minh họa (b-roll) không bản quyền.
- 🎠 **`carousel_maker`**: Biến file Text thành các chuỗi hình ảnh Carousel.
- 🎨 **`hf_blueprints`**: Các bản vẽ cảnh quay (scene blueprints) cho HyperFrames.

</details>

<details>
<summary><b>⚙️ Nhóm Kỹ năng Dữ liệu & Hệ thống (11 Skills)</b></summary>
<br>

- 🧠 **`llm_processor`**: Cầu nối gọi API của ChatGPT / Claude.
- 📂 **`repo_analyzer`**: Đọc và phân tích cây thư mục của một Github Repository.
- 📄 **`script_writer`**: Công cụ ép chuẩn format kịch bản (JSON/XML).
- 🏷️ **`metadata_extractor`**: Trích xuất siêu dữ liệu (EXIF, codec) từ các file phương tiện.
- 🌐 **`movierecaptool_landing`**: Sinh mã nguồn HTML cho trang Landing Page của mảng review phim.
- ⬇️ **`yt_downloader`**: Sử dụng yt-dlp để bòn rút video từ Youtube.
- ☁️ **`os_gdrive-manager`**: Tự động lưu trữ và đồng bộ hóa thành phẩm lên Google Drive.
- 🔗 **`os_decodo-openclaw-skill`**: Kỹ năng liên kết với Decodo.
- 📊 **`os_openclaw-skill-infographic`**: Tự động vẽ bản đồ Infographic bằng mã code.
- 📑 **`srt_parser`**: Đọc, sửa đổi và dịch các file phụ đề định dạng .srt/.vtt.
- ⚙️ **(Các Module bổ trợ)**: Chạy ngầm trong thư mục gốc `2_SKILLS`.

</details>
