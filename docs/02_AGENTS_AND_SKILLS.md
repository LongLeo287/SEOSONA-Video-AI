# Danh sách Agents và Kỹ năng Python

Tài liệu này liệt kê bộ não nhận thức (Agents) và tay chân thực thi (Skills) của SEOSONA Video.
Nguồn sự thật: `1_AGENTS/ROSTER.md` và `2_SKILLS/README.md`.

## 🤖 Lớp Nhận Thức: 10 AI Agents (`1_AGENTS/`)
Tất cả 10 agent dưới đây đều có code thật và được gọi từ pipeline/workflow.
(Thư mục `personas/` chứa định nghĩa gốc tính cách — không tính là agent.)

<details>
<summary><b>1. Nhóm Điều phối & Điều khiển từ xa (2 Agents)</b></summary>
<br>

- 👑 **`hermes_agent`**: Bot điều khiển từ xa qua Telegram (`telegram_remote.py`) — `/news`, `/publish`, `/trend`, `/status`. Entry độc lập, không nằm trong pipeline dispatch.
- 🔥 **`trend_jacking_agent`**: Rình trend (`trend_tracker.py`) rồi kích hoạt pipeline làm video bám xu hướng. Chạy qua `/trend` hoặc cron.

</details>

<details>
<summary><b>2. Nhóm Nghiên cứu & Nạp liệu (1 Agent)</b></summary>
<br>

- ⛏️ **`scraper_agent`**: Bóc tách HTML/JSON, cào nội dung trang web/tin tức (`scraper.py`, `news_scraper.py`) để dựng kịch bản.

</details>

<details>
<summary><b>3. Nhóm Sáng tạo Nội dung & Kịch bản (4 Agents)</b></summary>
<br>

- 🎯 **`seo_writer_agent`**: Viết kịch bản video khớp hành vi tìm kiếm (`writer.py`).
- 🎠 **`carousel_writer_agent`**: Nội dung dạng trượt (carousel) cho LinkedIn/Instagram.
- 💬 **`social_media_agent`**: Caption MXH theo khung PAS (giật tít, chim mồi).
- ✂️ **`repurposer_agent`**: Cắt video/podcast dài thành shorts/reels (`srt_analyzer.py`, `localizer.py`).

</details>

<details>
<summary><b>4. Nhóm Tối ưu hóa & MXH (2 Agents)</b></summary>
<br>

- 📈 **`seo_optimizer`**: Tối ưu metadata YouTube — title/tags/description + JSON-LD (`youtube_seo.py`).

</details>

<details>
<summary><b>5. Nhóm Kiểm duyệt & Đăng tải (3 Agents)</b></summary>
<br>

- 📊 **`analytics_feedback_agent`**: Phân tích retention, sinh post-mortem (`feedback_generator.py`).
- 🚀 **`publisher_agent`**: Nắm API đăng tải (YouTube/TikTok/FB/Drive) — `publish_dispatch.py`. **Publish cần User cho phép rõ ràng.**

</details>

---

## 🛠️ Lớp Thực Thi: 7 Python Skills (`2_SKILLS/`)
Mỗi skill dưới đây đều được nối vào pipeline/workflow (`2_SKILLS.<name>.<module>`).
9 skill chưa dùng đã được đã gỡ khỏi dự án (xem README ở đó).

<details>
<summary><b>🔊 Âm thanh & Giọng nói (2 Skills)</b></summary>
<br>

- 🗣️ **`voice_cloner`**: Router giọng nói DUY NHẤT (`voice_router.synthesize_voice`) — VieNeu (clone > preset) → fallback edge-tts trung thực (`vi-VN-NamMinhNeural`). Không còn nhánh F5/OmniVoice/Fish.
- 🎙️ **`tts_generator`**: Engine edge-TTS sinh giọng + phụ đề (đóng vai fallback, được `voice_router` gọi).

</details>

<details>
<summary><b>📝 Phụ đề (1 Skill)</b></summary>
<br>

- 📝 **`srt_maker`**: Sinh SRT qua faster-whisper / PhoWhisper (timestamp đến từng chữ cho Karaoke).

</details>

<details>
<summary><b>🎞️ Hình ảnh & Video (3 Skills + templates)</b></summary>
<br>

- ✂️ **`video_clipper`**: Cắt/định dạng clip (gồm short dọc 9:16).
- 🖼️ **`thumbnail_maker`**: Sinh thumbnail HTML.
- ⬇️ **`yt_downloader`**: Tải video nguồn từ YouTube (yt-dlp) — gọi từ `workflow_router`.
- 🎨 **`hf_blueprints`**: Bản vẽ/template cảnh HyperFrames (HTML, không phải skill Python).

</details>

<details>
<summary><b>✍️ Nội dung & Xử lý (2 Skills)</b></summary>
<br>

- 🎠 **`carousel_maker`**: Biến text thành chuỗi ảnh carousel (gọi từ `workflow_social_post`).

</details>

<details>
<summary><b>🗄️ Đã quarantine (9 Skills — không nối vào pipeline)</b></summary>
<br>

`audio_cleaner`, `audio_mixer`, `b_roll_fetcher`, `llm_processor`, `metadata_extractor`,
`script_writer`, `sfx_mixer`, `srt_parser`, `visual_fetcher` — dời sang
(removed). Có code thật nhưng chưa nơi nào gọi; phục hồi khi cần.

</details>
