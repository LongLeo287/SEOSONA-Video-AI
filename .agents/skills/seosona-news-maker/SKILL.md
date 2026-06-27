---
name: seosona-news-maker
description: >
  Làm video SEOSONA dạng SYNTHESIZED (tự sinh) — tin tức, giải thích kiến thức, repo/tool
  showcase — 9:16 (mặc định) hoặc 16:9, light-mode, giọng AI (VieNeu clone), phụ đề karaoke (RULE #1),
  component (bignum/repo/compare/terminal/steps/badges/stats/quote/tip/feature/chart/mockup/
  gittree/cta), SFX + BGM ducked. Dùng khi user nói "làm video tin tức / giải thích /
  giới thiệu repo / làm video từ link GitHub / từ kịch bản". Engine: video_engine → native_composer.
  (Edit footage tự quay / talking-head → dùng skill `talking-head-video-editor`.)
metadata:
  type: skill
  author: SEOSONA AI
  version: "2.0"
---

# 🎬 seosona-news-maker — video SEOSONA tự sinh (synthesized)

Skill cho **engine synthesized**: sinh cảnh từ nội dung (text / GitHub repo / news brief),
giọng AI VieNeu, render brand-native bằng HyperFrames. Đây là 1 trong 2 engine làm video:

- **Skill này (synthesized)** — máy tự dựng cảnh + giọng AI. → tin tức, giải thích, showcase.
- **`talking-head-video-editor`** — edit footage tự quay/screen-rec, giọng THẬT. → review/hướng dẫn/giới thiệu bằng người quay.

## 0. Engine + lệnh (đã verify chạy thật)

| Việc | Lệnh |
|---|---|
| GitHub repo → video (auto template) | `npm run make:video -- <github_url_or_owner/name>` |
| Ngang 16:9 (YouTube) | `npm run make:video -- <url> --aspect 16:9` |
| Batch news (nhiều repo, xoay template) | `python 4_BRAIN/make_video.py --news urls.txt` |
| Từ kịch bản tiếng Việt / website URL | `npm run video:news -- "<script_or_url>" [project] [ratio]` |

**Tỉ lệ:** mặc định 9:16; đặt `"aspect":"16:9"` trong template JSON hoặc `--aspect 16:9` (CLI) để ra ngang (1920×1080). Hỗ trợ `9:16` · `16:9` · `1:1`.

**Đầu ra** (`8_WORKSPACE/<project>/`): `*.mp4` + `*.srt` (trong `_captions_upload/`, tránh player auto-load đè karaoke) + `Thumbnail/thumbnail.png` + `publish_report.json` (nếu bật `SEOSONA_PUBLISH`) → tất cả qua quality gate.

**Lõi:** `4_BRAIN/video_engine.py` (định tuyến + quality gate) → `4_BRAIN/native_composer.py`
(voice qua `voice_router` VieNeu, timing qua `srt_maker/asr_router`, render HyperFrames CLI,
mix SFX+BGM). Profile brand/giọng/logo đọc từ `system_config.yaml`.

## 1. Nội dung (content) — 2 cách

- **Tự động (1 lệnh):** `make_video.py` tự lấy data GitHub thật + điền prose tiếng Việt theo template.
- **Chất lượng cao (agent):** dùng skill **`scene-composer`** để soạn `content` (segments + 2-tone heading + scene_data) rồi gọi:
  - `native_composer.make_video_from_template(template, content, project_dir)` — theo 1 trong các template JSON.
  - `native_composer.make_video_custom(project_dir, scenes_spec)` — tự lắp cảnh tự do từ 14 component.

## 2. Template JSON (`7_ASSETS/templates/*.json`) — cấu trúc cảnh (component + accent + kicker)

`ai-news-flash` · `benchmark-news` · `data-news` (tin/số liệu) · `insight-explainer` ·
`opinion-insight` · `seo-explainer` · `tutorial-gittree` (kiến thức/giải thích) ·
`repo-showcase` · `tool-walkthrough` · `resource-list` (repo/tool/kho).
Lưu render đẹp thành template mới: `native_composer.extract_template(...)`.

## 3. Component (14) cho mỗi cảnh
`bignum` (số to) · `repo` (repo card) · `compare` (2 cột) · `terminal` (lệnh) · `steps` (bước) ·
`badges` · `stats` (3 thẻ số) · `quote` · `tip` (💡) · `feature` · `chart` (bar) · `mockup` (browser) ·
`gittree` (git log) · `cta`. Accent: `blue` `green` `orange` (light-mode, palette brand).

## 🔴 RULE CỨNG
1. **TEXT/PHỤ ĐỀ = DẠNG HIỂN THỊ, KHÔNG PHIÊN ÂM**: viết `AI` `24/7` `GitHub` đúng trên màn; cách ĐỌC xử lý riêng bằng `lexicon` (native_composer dùng `news_video_standards.PRONUNCIATION_LEXICON`). Caption hiển thị DISPLAY word, không phải âm.
2. **HOOK ĐỦ Ở FRAME 0**: cảnh 0 hiện đủ kicker + heading ngay giây 0 (frame 0 = thumbnail nền tảng).
3. **KARAOKE vùng an toàn**: từ đang nói tô vàng, keyword tô accent; không sát đáy.
4. **LIGHT MODE ONLY**: không nền tối; palette brand (blue `#2A5BDA`, coral `#E2724D`, green `#16A34A`). Cảnh crossfade — không khung trắng.
5. **GIỌNG**: VieNeu (clone > preset "Trọng Hữu") → fallback edge-tts; nam miền Nam. KHÔNG ghi phiên âm vào text.
6. **SFX đa dạng** + **BGM ducked** dưới giọng (đã tự động trong native_composer).
7. **VERIFY trước khi giao** (dữ liệu thật, không bịa): frame không đen (YAVG>12), loudness ~-16 LUFS, duration đúng brief, caption đúng chính tả brand/số liệu, component không rỗng.

## Không làm trong skill này
- Không edit footage tự quay / talking-head ở đây → dùng skill `talking-head-video-editor`.
- Engine DUY NHẤT là `native_composer` — đừng tạo lại pipeline render cũ.

*Skill độc quyền SEOSONA AI. Engine: video_engine → native_composer (HyperFrames-native, không phụ thuộc pipeline ngoài).*
