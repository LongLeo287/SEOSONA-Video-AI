# Hệ sinh thái Thư Viện & Models AI

Nhà máy SEOSONA Video tận dụng tối đa mã nguồn mở và các mô hình AI tiên tiến nhất hiện tại, kết hợp giữa JavaScript và Python để cân bằng giữa Tốc độ Xử lý Đồ họa và Sức mạnh Xử lý Dữ liệu.

## 📦 1. JavaScript Ecosystem (Đồ họa & Dựng hình)
*(Khai báo đầy đủ trong file `package.json` gốc của dự án)*

- **`puppeteer-core` / `playwright`**: Thư viện điều khiển trình duyệt Chrome/Edge không đầu (headless). Là hạt nhân của Framework `html_renderer`, cung cấp khả năng chạy file HTML của HyperFrames và liên tục "bắn" ảnh chụp màn hình cực kỳ chuẩn xác.
- **`fluent-ffmpeg` / `ffmpeg-static` / `ffprobe-static`**: Trình bao bọc mã nguồn cho phép gọi lệnh FFmpeg từ NodeJS để ráp nối ảnh thành video.
- **`sharp` / `jimp`**: Thư viện thao tác, nén, nới rộng tỷ lệ khung hình (Aspect Ratio), và resize ảnh tốc độ cao (chủ yếu dùng cho việc tạo thumbnail hoặc nén dung lượng b-roll trước khi render).
- **`cheerio`**: Phiên bản tinh gọn của JQuery cho server. Dùng để bóc tách siêu tốc (Scrape) dữ liệu văn bản từ các trang web HTML rác.
- **`axios`**: Trình xử lý các yêu cầu mạng, bắn API tới các dịch vụ LLM.

## 🧠 2. Python Ecosystem & AI Models (Xử lý Âm thanh, Hình ảnh)
*(Khai báo đầy đủ trong file `requirements.txt` gốc của dự án)*

- **`F5-TTS`**: Mô hình chuyển văn bản thành giọng nói (TTS) kiến trúc phi tự hồi quy (Non-autoregressive). Khả năng clone giọng người thực (Zero-shot) chỉ bằng 1 đoạn audio mẫu dài 5 giây mà vẫn giữ được cảm xúc, sự biểu cảm cực mạnh.
- **`OmniVoice`**: Engine tạo âm thanh tổng quát, dùng cho các giọng đọc nhanh, rành mạch.
- **`VieNeu-TTS`**: Mô hình sinh giọng nói chuyên biệt dành riêng cho tiếng Việt, phát âm tròn vành rõ chữ.
- **`OpenAI-Whisper` (bản `faster-whisper`)**: Mô hình nhận diện giọng nói tự động (ASR). Cực kỳ quan trọng trong bước Forced-Alignment để xuất file `words.json` chứa timestamp cho phép đập nhịp Karaoke.
- **`moviepy`**: Trình biên tập video bằng mã code Python. Dùng để ghép các khối Video + Audio, và chèn Subtitle cứng.
- **`edge-tts`**: Mô hình sinh giọng nói đám mây của Microsoft Edge, dùng làm phương án dự phòng (fallback) nếu card đồ họa không chịu tải được F5-TTS.
- **`yt-dlp`**: Siêu trộm đa nền tảng, dùng để tải bất kỳ video/audio nào từ YouTube, Twitter, TikTok không bị chặn.
- **`Pillow` / `BeautifulSoup4`**: Bộ công cụ Python chuyên dụng để thao tác chỉnh sửa hình ảnh mảng (Pixel Arrays) và cào dữ liệu DOM.
