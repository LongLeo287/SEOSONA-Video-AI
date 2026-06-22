# Luồng Công Việc và Khung Đồ Họa

Tài liệu này liệt kê các hệ thống điều phối (Workflows) cấp cao và các Framework dựng hình của SEOSONA Video.

## 🧠 20 Agentic Workflows (`.agents/skills/`)
Sự kết hợp giữa Agents (Lớp 1) và Python Skills (Lớp 2) tạo thành các cỗ máy tự động từ A-Z.

1. **`embedded-captions`**: Dán phụ đề dính chặt vào video có sẵn (hiệu ứng Cinematic/Karaoke).
2. **`faceless-explainer`**: Quy trình làm video tin tức/giải thích hoàn toàn không lộ mặt.
3. **`general-video`**: Công cụ render dự phòng cho mọi trường hợp video tùy biến.
4. **`graphic-overlays`**: Dán các thẻ thông tin (Card, Lower-third) bay lượn lên video gốc.
5. **`heygen-native-api`**: Gọi API của HeyGen v2 để sinh Avatar người ảo nói chuyện.
6. **`heygen-skills`**: Các lệnh tinh chỉnh Avatar HeyGen (Vị trí, Phông xanh, Trang phục).
7. **`hyperframes`**: Trạm kiểm soát trung tâm của Engine HyperFrames.
8. **`hyperframes-animation`**: Kho hiệu ứng chuyển động, nảy, xoay (GSAP, CSS Keyframes).
9. **`hyperframes-cli`**: Bộ công cụ dòng lệnh (init, render, publish, lint).
10. **`hyperframes-core`**: Khế ước cấu trúc HTML/CSS buộc mọi file phải tuân thủ.
11. **`hyperframes-creative`**: Giám đốc nghệ thuật (quyết định bảng màu, font chữ, bố cục).
12. **`hyperframes-media`**: Trạm trung chuyển mài giũa tài nguyên trước khi đưa vào khuôn đúc.
13. **`hyperframes-registry`**: Quản lý các block/component UI (như component thẻ mã code, thẻ thống kê).
14. **`seosona-news-maker`**: Siêu Pipeline Native tạo video tin tức TikTok 9:16 cực nhanh và sạch.
15. **`motion-graphics`**: Trình tạo hình ảnh Kinetic Typography và Data-Visualization bay nhảy.
16. **`pr-to-video`**: Biến một dòng code mới (Github Pull Request) thành video giải thích tính năng.
17. **`product-launch-video`**: Dựng video quảng cáo sản phẩm với hiệu ứng hào nhoáng.
18. **`remotion-to-hyperframes`**: Dịch ngược mã React của Remotion thành mã HTML của HyperFrames.
19. **`seosona-video-operator`**: Mạch điều khiển trung tâm ra lệnh cho toàn bộ các luồng còn lại.
20. **`website-to-video`**: Đi dạo một vòng trang web bất kỳ và tự quay lại màn hình làm thành video.

---

## 🎨 10 Frameworks Đồ Họa (`5_FRAMEWORK/`)
Nơi những file HTML tĩnh biến thành những siêu phẩm 60 Frame/giây.

1. **`_Archived_HTML_Mockups`**: Các bản vẽ nháp HTML đã được lưu trữ.
2. **`hf_cards`**: Bộ sưu tập các thẻ Component 3D (Thẻ thông báo, Thẻ số liệu...).
3. **`hf_core`**: Lõi quy định thẻ DOM (Document Object Model) của HyperFrames.
4. **`hf_engine`**: Đầu não dịch các dòng lệnh HTML sang tọa độ điểm ảnh.
5. **`html_renderer`**: Súng ngắm Puppeteer, có nhiệm vụ "bắn" ảnh màn hình liên tục.
6. **`hyperframes`**: Registry cục bộ lưu trữ các biến thể khung hình.
7. **`loop-source-seosona-clone`**: Mã nguồn hiệu ứng vòng lặp (Loop animation).
8. **`moviepy_wrapper`**: Bọc Python để ra lệnh cho phần mềm ghép video.
9. **`news_loop_path_hyperframes`**: Background động chạy vòng lặp vô tận cho video tin tức.
10. **`news_spatial_hyperframes`**: Không gian 3D giả lập cho video tỷ lệ dọc 9:16.
