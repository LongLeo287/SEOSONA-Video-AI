# Tích hợp Hệ Điều Hành (SEOSONA OS Integration)

Repository này không phải là một ứng dụng trôi nổi độc lập. Nó được ràng buộc chặt chẽ và tuân theo mọi Mệnh lệnh từ "Trái tim" của Hệ điều hành **SEOSONA OS** (Định vị tại `~/.seosona` hoặc `D:/SEOSONA OS`).

## 🔗 1. Hệ thống Cầu nối (The Bridge Scripts)
Nằm trong thư mục `scripts/`, đây là những "Sợi cáp" liên lạc giữa Video Factory và OS.

<details open>
<summary><b>🔀 Mở rộng Sợi cáp Giao tiếp</b></summary>
<br>

- 🔌 **`seosona-project-bridge.cjs`**: Cáp mạng chính. Giúp OS nhận diện được Repository này có những Workflow gì và ra lệnh khởi chạy luồng Node.js tương ứng.
- 🐍 **`seosona-python.cjs`**: Cáp Python. Giúp môi trường Node.js gọi các lệnh Python (Whisper, VieNeu-TTS) một cách trơn tru mà không bị lỗi biến môi trường.
- 🏥 **`seosona_doctor.py` & `seosona-project-audit.cjs`**: Bộ đôi bác sĩ. Luôn chạy kiểm tra sức khỏe của dự án (Check xem thiếu thư viện không, Node version có chuẩn không) trước khi bấm nút Render.
- 🏗️ **`4_BRAIN/native_composer.py`**: Engine render native — tự sinh HTML/CSS/GSAP, dựng cảnh + phụ đề karaoke và render HyperFrames cho luồng video synthesized (thay `build_news_project.mjs` cũ đã nghỉ hưu).

</details>

> [!CAUTION]
> **ĐỘC QUYỀN UAP (Universal Autonomous Process)**
> 
> Toàn bộ quy trình *Review Repo -> Clone Repo -> Phân tích, học hỏi -> Nạp, tạo, nâng cấp -> Clear Repo* là đặc quyền tối thượng của hệ điều hành SEOSONA OS dùng để tự tiến hóa. 
> Dự án SEOSONA Video **bị cấm tuyệt đối** việc sở hữu, thực thi, hoặc mô phỏng quy trình này (như đặt tên thư mục `repo_analyzer`) nhằm tránh đụng độ và chồng chéo chức năng ở mức OS.

---

## 📜 2. Khế ước Khởi động (Startup Contracts)
Mỗi khi khởi động, hệ thống bắt buộc phải đọc và tuân thủ các file Hiến pháp Mẹ. 

<details open>
<summary><b>⚖️ Các Điều Luật Cốt Lõi</b></summary>
<br>

- 🆔 **`seosona.project.json` (Project Manifest)**: 
  Căn cước công dân của dự án. Khai báo rõ ràng: Không gian bộ nhớ thuộc về `seosona-video`, Mức độ tự chủ là `project_edit`. Việc đăng video lên nền tảng (Publish) bắt buộc phải có sự cho phép của User.
- 🧠 **`AGENTS.md` (SEOSONA OS Rules)**:
  Bản hợp đồng yêu cầu bất cứ AI Agent nào đi vào dự án này cũng phải trỏ về SEOSONA OS để đọc linh hồn (`1_CORE/SOUL.md`) và kiến thức (`2_KNOWLEDGE/MASTER_INDEX.md`) trước khi làm việc.
- ✨ **`GEMINI.md` / `.clauderules` / `.cursorrules`**:
  Các bộ luật riêng biệt ép các mô hình AI (như Gemini, Claude, Cursor) khi code trong repo này phải tuân thủ nghiêm ngặt chuẩn mực của SEOSONA:
  - Phải dùng skill `seosona-task-intake` khi nhận task.
  - Phải tạo `implementation_plan.md` trước khi code.
  - Phải viết `walkthrough.md` sau khi hoàn thành.

</details>

> [!WARNING]
> Bất cứ sửa đổi mã nguồn nào phá vỡ sự kết nối của các file `Bridge` hoặc vi phạm các `Khế Ước` trên, toàn bộ Nhà máy SEOSONA Video sẽ bị văng ra khỏi Hệ sinh thái SEOSONA OS và tê liệt hoàn toàn.
