# TÀI LIỆU VẬN HÀNH CHUẨN (MASTER OPERATION)
*Cập nhật: 2026-06-19 — Phiên bản v3.0 (HyperFrames Engine)*

Hệ thống hoạt động theo **Trình tự Tuyến tính (Linear Pipeline)** đi từ Router (`4_BRAIN/workflow_router.py`) ra Workspace (`8_WORKSPACE/`).

## ENTRY POINT

```
python 4_BRAIN/workflow_router.py "<input>" [brand] [ratio] [project_name]
```

Router tự động nhận diện đầu vào:
- **YouTube URL** → Mode `download` (yt-dlp → repurpose)
- **Website URL** → Mode `scrape` (scraper_agent → TTS → render)
- **File .srt/.mp4** → Mode `repurpose` (clipper → shorts)
- **Text/Script** → Mode `create` (TTS → render)

---

## THỨ TỰ VẬN HÀNH TỔNG QUÁT (END-TO-END)

### BƯỚC 1: SCRIPTING / DATA INTAKE
- **Mode `create`:** Nhận script text trực tiếp.
- **Mode `scrape`:** `1_AGENTS/scraper_agent/scraper.py` cào nội dung từ URL.
- **Mode `repurpose`:** `1_AGENTS/repurposer_agent/srt_analyzer.py` phân tích file SRT/MP4.

### BƯỚC 2: TỔNG HỢP GIỌNG NÓI (TTS)
- **Lexicon Filter:** `_apply_lexicon_filter()` ngầm dịch từ khóa tiếng Anh sang phiên âm Việt.
- **Engine:** `2_SKILLS/voice_cloner/fish_audio_api.py` (fallback: Edge-TTS `vi-VN-HoaiMyNeural`).
- **Đầu ra:** `8_WORKSPACE/<ProjectName>/.temp/voice.mp3`

### BƯỚC 3: NHẬN DIỆN TIMESTAMPS
- Ưu tiên: TTS native word boundaries.
- Fallback: `_estimate_word_level_data_from_script()` (phân bổ theo trọng lượng từ).
- Dự phòng: `2_SKILLS/srt_maker/whisper_engine.py` (ASR).
- **Đầu ra:** `8_WORKSPACE/<ProjectName>/SRT/<ProjectName>.srt`

### BƯỚC 4: ASSET GATHERING & SCENE GENERATION
- `_make_news_scene_copy()` phân tích câu → tự chọn component mode:
  - `dashboard`: Khi phát hiện con số/phần trăm.
  - `source-card`: Khi nhắc đến nguồn báo cáo.
  - `screenshot`: Mặc định (khung Browser mockup).
- SFX tự sinh: `sfx_whoosh.wav` (chuyển cảnh) + `sfx_pop.wav` (hiện chữ).
- BGM tự sinh: `bgm_news.mp3` (3 sóng sine trộn).

### BƯỚC 5: VIDEO RENDER (HyperFrames Core)
- `_write_hyperframes_render_project()` sinh toàn bộ HTML/CSS/GSAP.
- Render: `npx hyperframes@0.6.112 render --format mp4 --output <path>`
- **Frame 0 Hook:** Kicker + H1 luôn opacity 100% ngay giây 0.

### BƯỚC 6: THUMBNAIL
- `2_SKILLS/thumbnail_maker/thumbnail_generator.py` → HTML → Playwright → PNG.
- Text lấy động từ `script_text`, không hardcode.
- **Đầu ra:** `8_WORKSPACE/<ProjectName>/Thumbnail/<ProjectName>_Thumbnail.png`

---

## CẤU TRÚC OUTPUT

```
8_WORKSPACE/<ProjectName>/
├── <ProjectName>.mp4          → Video chính
├── SRT/<ProjectName>.srt      → Phụ đề
├── Thumbnail/<ProjectName>_Thumbnail.png  → Ảnh bìa
└── .temp/                     → File tạm (voice, hf_render/)
```

## CƠ CHẾ BẢO MẬT

- API Keys: Lưu trong `.env` (root), load bởi `python-dotenv`.
- Config: `system_config.yaml` dùng `${VAR}` placeholder.
- `.gitignore`: Chặn `.env`, `8_WORKSPACE/*`, `3_MEMORY/*`, media files.
