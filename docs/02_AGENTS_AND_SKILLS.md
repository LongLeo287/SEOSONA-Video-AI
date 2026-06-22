# Danh sách Agents và Kỹ năng Python

Tài liệu này liệt kê bộ não nhận thức (Agents) và tay chân thực thi (Skills) của SEOSONA Video.

## 🤖 Lớp Nhận Thức: 17 AI Agents (`1_AGENTS/`)
Đây là những Persona chịu trách nhiệm tư duy, lên kế hoạch và viết kịch bản trước khi mã code can thiệp.

- **`analytics_feedback_agent`**: Thu thập và phân tích các chỉ số giữ chân người xem (retention metrics).
- **`carousel_writer_agent`**: Chuyên gia sáng tạo nội dung định dạng trượt (carousel) cho LinkedIn/Instagram.
- **`editor_agent`**: Tổng biên tập, người soát lỗi và sắp xếp lại cấu trúc mạch truyện.
- **`hermes_agent`**: Kiến trúc sư trưởng, điều phối việc gọi các công cụ kỹ thuật và chuyển giao data.
- **`personas`**: Định dạng gốc (Base definitions) chứa đặc điểm tính cách, giọng điệu cho toàn bộ agents.
- **`publisher_agent`**: Đặc vụ nắm API để ấn nút Publish lên các nền tảng MXH.
- **`quality_reviewer`**: Người kiểm định chất lượng cuối cùng (tìm khung hình đen, lỗi âm thanh).
- **`repurposer_agent`**: Cắt nhỏ video/podcast dài thành nhiều luồng nội dung (shorts, reels).
- **`researcher_agent`**: Máy ủi dữ liệu, chuyên cào nát các trang web để tổng hợp sự thật (facts).
- **`scraper_agent`**: Cánh tay phải của researcher, thực thi các lệnh bóc tách HTML/JSON.
- **`seo_optimizer`**: Tối ưu từ khóa cho Youtube/TikTok (Title, Tags, Meta Description).
- **`seo_writer_agent`**: Viết kịch bản video sao cho từ khóa khớp với hành vi tìm kiếm.
- **`social_media_agent`**: Thợ săn view, chuyên giật tít và viết caption tạo hiệu ứng chim mồi.
- **`thumbnail_tester_agent`**: Phân tích ảnh bìa bằng thị giác máy tính và tiến hành A/B Testing.
- **`trend_jacking_agent`**: Kẻ đu trend, rình rập Twitter/Tiktok để chớp thời cơ làm video bám xu hướng.
- **`writer_agent`**: Thợ viết kịch bản đa năng cho các dự án thông thường.
- **(Và nhân vật cốt lõi thứ 17 luôn chạy ngầm)**: Hệ thống Operator.

---

## 🛠️ Lớp Thực Thi: 24 Python Skills (`2_SKILLS/`)
Đây là các đoạn mã Python nguyên thủy (Native) để xử lý trực tiếp tín hiệu Audio/Video/Text.

1. **`audio_cleaner`**: Xóa tiếng ồn nền, lọc xì và chuẩn hóa âm lượng (Normalize).
2. **`audio_mixer`**: Trộn nhiều track âm thanh lại với nhau (Giọng đọc + BGM + SFX).
3. **`b_roll_fetcher`**: Tìm và tải các đoạn video minh họa (b-roll) không bản quyền.
4. **`carousel_maker`**: Biến file Text thành các chuỗi hình ảnh Carousel.
5. **`hf_blueprints`**: Các bản vẽ cảnh quay (scene blueprints) cho HyperFrames.
6. **`llm_processor`**: Cầu nối gọi API của ChatGPT / Claude.
7. **`metadata_extractor`**: Trích xuất siêu dữ liệu (EXIF, codec) từ các file phương tiện.
8. **`movierecaptool_landing`**: Sinh mã nguồn HTML cho trang Landing Page của mảng review phim.
9. **`os_decodo-openclaw-skill`**: Kỹ năng liên kết với Decodo.
10. **`os_gdrive-manager`**: Tự động lưu trữ và đồng bộ hóa thành phẩm lên Google Drive.
11. **`os_humanizer`**: Bơm các khoảng nghỉ, tiếng thở để làm giọng AI trở nên tự nhiên.
12. **`os_openclaw-skill-infographic`**: Tự động vẽ bản đồ Infographic bằng mã code.
13. **`repo_analyzer`**: Đọc và phân tích cây thư mục của một Github Repository.
14. **`script_writer`**: Công cụ ép chuẩn format kịch bản (JSON/XML).
15. **`sfx_mixer`**: Căn giờ và chèn đè các tiếng "whoosh", "pop", "ding" chuyển cảnh.
16. **`srt_maker`**: Ép file âm thanh vào Whisper để lấy độ trễ (timestamp) đến từng chữ một.
17. **`srt_parser`**: Đọc, sửa đổi và dịch các file phụ đề định dạng .srt/.vtt.
18. **`thumbnail_maker`**: Cắt ghép hình ảnh tự động qua thư viện Pillow/OpenCV để tạo Thumbnail.
19. **`tts_generator`**: Module phát sinh Giọng nói AI nói chung.
20. **`video_clipper`**: Cắt trích đoạn video theo mili-giây.
21. **`visual_fetcher`**: Tải ảnh hàng loạt từ các link URL thu thập được.
22. **`voice_cloner`**: Lõi gọi Engine F5-TTS và OmniVoice để nhân bản giọng 0-shot.
23. **`yt_downloader`**: Sử dụng yt-dlp để bòn rút video từ Youtube.
24. **Module bổ trợ chạy ngầm**: Các file `.py` tiện ích khác trong `2_SKILLS`.
