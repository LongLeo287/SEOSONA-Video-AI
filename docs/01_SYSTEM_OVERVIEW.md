# Tổng quan Hệ sinh thái SEOSONA Video

Chào mừng bạn đến với tài liệu cốt lõi của **SEOSONA Video Autonomous Factory**. Đây là một Nhà máy Sản xuất Truyền thông Đa phương tiện hoàn toàn tự động, được thiết kế và làm chủ 100% bởi **SEOSONA AI**. 

## 1. Mục đích Hệ thống
Hệ thống này được sinh ra để loại bỏ hoàn toàn sự can thiệp của con người trong quá trình sản xuất nội dung video. Bằng cách kết hợp Trí tuệ nhân tạo (Agents), Xử lý ngôn ngữ tự nhiên (LLMs), Engine Kết xuất giao diện (Puppeteer/HyperFrames), và các thuật toán thị giác máy tính, SEOSONA Video có khả năng biến 1 dòng ý tưởng thành 1 video viral trên Tiktok, Youtube, Instagram Reels chỉ trong vòng chưa đầy 3 phút.

## 2. Kiến trúc Phân tầng
Hệ thống chia làm 4 lớp (Layers) rõ rệt:
- **Cognitive Layer (Lớp Nhận thức)**: Bao gồm 17 AI Agents chuyên biệt (đóng vai trò tư duy).
- **Execution Layer (Lớp Thực thi)**: Bao gồm 24 Python Skills xử lý file vật lý.
- **Agentic Workflow Layer (Lớp Điều phối)**: Tập hợp 20 đường ống tự động kết nối hai lớp trên.
- **Rendering Layer (Lớp Kết xuất)**: 10 Frameworks đồ họa và âm thanh để đúc thành phẩm cuối cùng.

## 3. Không gian làm việc (Workspaces)
Toàn bộ quá trình đúc video diễn ra tại thư mục `8_WORKSPACE/`. Đây là "công xưởng" tạm thời để lắp ráp các mảnh ghép trước khi xuất xưởng.

```text
8_WORKSPACE/
├── supergraph-news/            : Dự án Video Tin tức tạo bằng công cụ tự động sạch sẽ nhất
├── _drafts/                    : Các ý tưởng và bản nháp kịch bản tạm thời
├── _scripts/                   : Các đoạn script chạy một lần
└── _ARCHIVE/                   : Kho lưu trữ lịch sử và hơn 60 bài test biên dịch cũ
```

## 4. SEOSONA Project Bridge
Là cầu nối CLI (`scripts/seosona-project-bridge.cjs`) giúp kết nối Nhà máy sản xuất này với nhân hệ điều hành trung tâm SEOSONA OS.
