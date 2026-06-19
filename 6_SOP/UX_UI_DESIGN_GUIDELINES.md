# SEOSONA Video: UX/UI Design Guidelines

> Nguồn trích xuất: `Website SEOSONA/DESIGN.md` và `SEOSONA OS/4_AGENTS/personas/ui-ux-designer.md`

## 1. Triết lý Thiết kế (Design Philosophy)
SEOSONA Video tuân thủ tiêu chuẩn B2B Premium:
- Không gian (Whitespace): Luôn sử dụng khoảng trắng lớn (generous whitespace) để tạo cảm giác sang trọng.
- Hiển thị (Typography): Ưu tiên cấu trúc Typography rõ ràng, dễ đọc trên di động.
- Tính nhất quán (Consistency): Không sử dụng các gam màu "Neon", "Cyberpunk" lòe loẹt. Tập trung vào sự tin cậy, dữ liệu, kỹ thuật.

## 2. Token Màu sắc (Color System)
Khi khởi tạo Video có chủ đề Sáng (Light Theme):
- **Background Base (Trắng tinh):** `#FFFFFF`
- **Background Surface:** `#F8FAFC`
- **Text Headers (Mực đậm):** `#04091A` (Tuyệt đối không dùng `#000000`)
- **Text Body:** `#64748B`
- **Primary Accent (Xanh Signal):** `#1D4ED8`

Khi khởi tạo Video có chủ đề Tối (Navy Theme - Kế thừa từ Video Legacy):
- **Background Base:** `#1A2DB5` (Navy Brand)
- **Primary Accent:** `#FFD54F` (Yellow)
- **Text:** `#FFFFFF`

## 3. Quy tắc Hình khối (Geometry & Layout)
- **Bo góc (Border Radius):** Mềm mại (Soft), từ `16px` đến `40px` cho các khối thẻ (Cards/Mockups). Tuyệt đối KHÔNG dùng góc nhọn.
- **Đổ bóng (Shadows):** 
  - Đổ bóng nhẹ cho Box Logo: `box-shadow: 0 10px 30px rgba(0,0,0,0.2)`
  - Đổ bóng cho Mockup 3D: Lên tới `0 40px 100px rgba(0,0,0,0.3)`
- **Hiệu ứng Animation (GSAP):**
  - Text & UI xuất hiện: Nên dùng `back.out(1.4)` hoặc `expo.out` để tạo cảm giác "nảy" tự nhiên.
  - Mockup đa tầng (Multi-layered): Hình nền phụ luôn bị mờ `filter: blur(2px)` và giảm Opacity, trong khi hình chính `z-index` cao nhất và sắc nét nhất.

## 4. Typography
- **Heading Font:** `Be Vietnam Pro` (Khuyến nghị `font-weight: 800-900`, `letter-spacing: -1.5px` để tạo độ nén hiện đại).
- **Body Font:** `Be Vietnam Pro` (`font-weight: 500`, `line-height: 1.5`).

## 5. Review Criteria (Quy trình duyệt giao diện)
Trước khi Pipeline Render Video, Agent cần kiểm tra:
1. Độ tương phản của Text (Text Contrast) so với Background.
2. Logo Brand có bị chìm không (Bắt buộc dùng `White pill box` nếu nền tối).
3. Text có bị tràn đè lên vùng Ảnh Mockup không (Bắt buộc phải tách Container riêng biệt).
