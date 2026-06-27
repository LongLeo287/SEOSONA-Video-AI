# Giải phẫu Phần Hồn: Não bộ, Ký ức và Kiến thức

Nếu các Luồng (Workflows) là "Tay chân", thì đây chính là "Phần Hồn" giúp SEOSONA Video có khả năng tự tư duy và tiến hóa theo thời gian.

## 🧠 1. Hệ thần kinh trung ương (`4_BRAIN/`)
Nơi chứa các lõi Xử lý Ngôn ngữ và Phân tích Logic tĩnh (Chưa đụng đến Render). Nhấn vào để xem chi tiết các lõi:

<details open>
<summary><b>⚙️ Các Engine Tư Duy Cốt Lõi</b></summary>
<br>

- 🧠 **`llm_engine.py` (29.6KB)**: Quả tim của hệ thống. Chứa các thuật toán gọi API, quản lý Context Window, Rate Limit, và Retry Logic khi giao tiếp với các mô hình ngôn ngữ lớn (OpenAI, Anthropic).
- 🚉 **`video_engine.py`**: Cửa ngõ thống nhất của pipeline render (`run_pipeline(script_text, brand, mode, aspect_ratio, project_name)`). Quyết định file dữ liệu nào đi vào đường ống nào và điều phối toàn bộ tiến trình.
- 🎨 **`native_composer.py`**: Trình kết xuất thực sự — giọng nói + phụ đề RULE #1 + render native HyperFrames + trộn BGM-ducking/SFX. Cũng quản lý template JSON qua `fill_template` / `list/load/save/extract_template`.
- 🧩 **`scene_composer.py`**: Bộ não nội dung, chọn và sắp xếp các cảnh trước khi đưa vào `native_composer`.
- 🔀 **`workflow_router.py`**: Định tuyến công việc, bọc `video_engine` trong SuperGraph DAG + quality gate. Nó đọc các dữ kiện truyền vào và quyết định: *"À, đây là bài bóc tách code, hãy gọi luồng PR-to-Video"*.
- 🎯 **`intent_router.py`**: Bộ định tuyến "Ý định". Cố gắng hiểu người dùng hoặc hệ thống mẹ thực sự muốn gì thông qua các luồng văn bản không rõ ràng.
- 💯 **`quality_scorer.py`**: Máy chấm điểm tàn nhẫn. Trả về điểm số (Scale 0-10) xem kịch bản hoặc khung hình có đạt yêu cầu chất lượng hay không.

> [!NOTE]
> `pipeline_manager.py`, `video_capability_bridge.py` và `video_template_factory.py` đã NGHỈ HƯU và được đã gỡ khỏi dự án. Render nay đi qua `video_engine.py` → `native_composer.py`; template là file JSON trong `7_ASSETS/templates/` quản lý qua `native_composer.extract_template/save_template` + skill `scene-composer`.

</details>

---

## 💾 2. Không gian Lưu trữ Ký ức (`3_MEMORY/`)
Hệ thống không bị mất trí nhớ sau khi tắt máy. Nó lưu lại mọi kinh nghiệm vào thư mục này.

<details>
<summary><b>📂 Cấu trúc Ký ức Dài hạn</b></summary>
<br>

- 🧬 **`chroma_db/`**: Cơ sở dữ liệu Vector (Vector Database). Lưu trữ hàng nghìn Embeddings (Tọa độ không gian ngữ nghĩa). Khi Agent cần tìm một dự án cũ, nó sẽ tìm trong này bằng cách đo khoảng cách Cosine.
- 🕸️ **`knowledge_graph/`**: Đồ thị tri thức. Bản đồ nhện liên kết các thực thể với nhau (Ví dụ: "Video A" `được làm bằng` "Luồng B" `dựa trên` "Trend C").
- 🏦 **`context_bank/`**: Ngân hàng Bối cảnh. Lưu lại các bối cảnh, prompt thành công để tái sử dụng.
- 📚 **`project_log/` & `video_history/`**: Nhật ký lịch sử của từng đoạn video đã xuất xưởng.
- 🚨 **`error_log/`**: Nơi lưu giữ các lỗi rớt mạng, tràn RAM để hệ thống tự phân tích và sửa sai ở lần chạy sau.

</details>

---

## 📖 3. Tàng Kinh Các (`2_KNOWLEDGE/`)
Nơi chứa các luật nạp Dữ liệu đầu vào (Ingestion).

<details>
<summary><b>📥 Nguồn Nạp Liệu</b></summary>
<br>

- 📑 **`INGESTION_INDEX.md`**: Quy tắc tối cao về việc nạp dữ liệu từ bên ngoài (Web, PDF, Notion, Github) vào hệ thống sao cho an toàn và không bị nhiễm độc thông tin.
- 📦 **`raw_data/`**: Nơi tập kết các đống dữ liệu thô (HTML rác, file Text chưa dọn dẹp) trước khi bị `scraper_agent` / `trend_jacking_agent` phân tích.
- 🐙 **`repos/`**: Chứa mã nguồn của các Github Repository được clone về để chuẩn bị làm nguyên liệu cho luồng `PR-to-Video`.

</details>
