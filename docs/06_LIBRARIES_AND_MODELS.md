# Hệ sinh thái Thư Viện & Models AI

Nhà máy SEOSONA Video tận dụng tối đa mã nguồn mở và các mô hình AI tiên tiến nhất hiện tại, kết hợp giữa JavaScript và Python để cân bằng giữa Tốc độ Xử lý Đồ họa và Sức mạnh Xử lý Dữ liệu.

## 📦 1. JavaScript Ecosystem (Đồ họa & Dựng hình)

| Thư viện | Nhiệm vụ chính | Phân tích chức năng |
| :--- | :--- | :--- |
| 🌐 **`puppeteer-core`** / **`playwright`** | Trình duyệt ảo | Là hạt nhân của Framework `html_renderer`, cung cấp khả năng chạy file HTML của HyperFrames và liên tục "bắn" ảnh chụp màn hình cực kỳ chuẩn xác. |
| 🎞️ **`fluent-ffmpeg`** / **`ffmpeg-static`** | Xử lý Video | Trình bao bọc mã nguồn cho phép gọi lệnh FFmpeg từ NodeJS để ráp nối hàng nghìn ảnh tĩnh thành video chuyển động. |
| 🖼️ **`sharp`** / **`jimp`** | Xử lý Hình ảnh | Thao tác nén, nới rộng tỷ lệ khung hình (Aspect Ratio), và resize ảnh tốc độ cao (chủ yếu dùng tạo thumbnail hoặc nén b-roll). |
| 🕸️ **`cheerio`** | Cào dữ liệu | Dùng để bóc tách siêu tốc (Scrape) dữ liệu văn bản từ các trang web HTML rác mà không cần bật trình duyệt. |
| 🔌 **`axios`** | Giao tiếp mạng | Trình xử lý các yêu cầu mạng, bắn API tới các dịch vụ LLM. |

## 🧠 2. Python Ecosystem & AI Models (Âm thanh, Trí tuệ)

| Mô hình / Thư viện | Phân loại | Đánh giá Năng lực |
| :--- | :--- | :--- |
| 🇻🇳 **`VieNeu-TTS`** | AI Voice (Local · **engine chính**) | Mô hình sinh giọng chuyên biệt tiếng Việt, clone từ mẫu 3-5s, code-switch Vi+En, chạy CPU/ONNX. Là engine giọng nói DUY NHẤT, qua `voice_router.py`. |
| ⏱️ **`OpenAI-Whisper`** | Phân tích AI (ASR) | Bản `faster-whisper`. Quan trọng bậc nhất trong bước Forced-Alignment để xuất file `words.json` chứa timestamp mili-giây cho Karaoke. |
| 🎬 **`moviepy`** | Trình biên tập Video | Ghép các khối Video + Audio bằng mã code Python tĩnh. Dùng kết hợp với FFmpeg. |
| ☁️ **`edge-tts`** | AI Voice (Cloud) | Mô hình sinh giọng đám mây dự phòng (Fallback) khi Card đồ họa quá tải. |
| 🕵️ **`yt-dlp`** | Công cụ Tải xuống | Siêu trộm đa nền tảng, bòn rút mã nguồn Video/Audio từ Youtube, Tiktok, X không bị chặn. |
| 🐍 **`Pillow` / `BeautifulSoup4`** | Thao tác Dữ liệu | Xử lý mảng Điểm ảnh (Pixel Arrays) và bóc tách cây DOM HTML. |
