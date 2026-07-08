# Quy trình NẠP → HỌC → TẠO cho 3 thư viện (template · component · block)

Đây KHÔNG phải vòng lặp mới — nó là **Self-Improvement Loop** (`6_SOP/SELF_IMPROVEMENT_LOOP.md`, 9 stage)
áp riêng cho 3 thư viện HyperFrames. Một câu: **nguồn (repo/video/web/design) → trích PATTERN, không lấy
artifact → đúc thành 1 entry brand-thuần → đăng ký vào selector → ship trong video kế tiếp.**

```
NẠP (ingest)            HỌC (learn)              TẠO (create)
SIL 1-3                 SIL 4-5                  SIL 6-9
DISCOVER→ANALYZE→SEC    DECIDE→ADAPT(brand)      BUILD→VERIFY→WIRE→RECORD
```

---

## 🟢 NẠP — đưa nguồn vào (SIL 1-3)
| Bước | Làm gì | Tool |
|---|---|---|
| **DISCOVER** | Tìm nguồn: repo hay, video clone, mẫu web/design | `REPO_WATCHLIST.md`, `.agents/skills/video-discovery`, daemon `3_MEMORY/ingestion_queue.json`, `scripts/source_footage.py` (yt-dlp) |
| **ANALYZE** | Clone + đọc SOURCE thật (không đọc README), trích "viên ngọc" hình ảnh/cấu trúc. Repo to → `gitingest`/`markitdown` + fan-out | OS UAP `02_auditor`, Explore agent |
| **SECURITY** | `npm run security:scan <repo>` → SAFE/CAUTION/DO_NOT_ADOPT | `scripts/security_scan.py` |

Clone tham khảo nằm gitignored ở `2_KNOWLEDGE/external_toolkits/` (đã có daemon tự nạp).

## 🟡 HỌC — chắt lọc + chuyển sang brand (SIL 4-5)
| Bước | Làm gì |
|---|---|
| **DECIDE** | Cổng 7 bước (relevance·license·quality·**dedup**·security·location·connect) → INGEST / REFERENCE / SKIP. Lọc: free/local, license thoáng, **brand-fit**, **không trùng** cái đã có (`REPO_VETTING_SOP.md`) |
| **ADAPT** | **Lấy PATTERN, không lấy artifact.** Re-skin về brand: light-mode, `brand_kit` blue/coral, Be Vietnam Pro. Dark/neon → bỏ |

→ Câu hỏi chốt mỗi nguồn: *"cái này thành TEMPLATE (kịch bản), COMPONENT (mảnh), hay BLOCK (cảnh)?"*

## 🔵 TẠO — đúc + đăng ký (SIL 6-9), tự động hoá bằng `grow_library`
Một entry point: **`npm run library -- <template|block|component> ...`** (hoặc `python scripts/grow_library.py`).

### → TEMPLATE (kịch bản scene)
1. **BUILD**: `npm run library -- template "Top 7 lỗi SEO" --scenes 7` (hoặc tay: copy 1 JSON, sửa `scenes`).
   Generator `template_generator.py` lắp arc từ component cues, validate, ghi `7_ASSETS/templates/<slug>.json`.
2. **WIRE**: thêm 1 rule keyword→tên vào `4_BRAIN/template_picker.py._RULES` → tự chọn theo nội dung.
3. **VERIFY+RECORD**: `gen_catalog.py` tự chạy (cập nhật CATALOG); ghi `INGESTION_LOG.md` nếu từ nguồn học.

### → BLOCK (cảnh đúc sẵn)
1. **BUILD**: thả `<name>/` (`<name>.html` + assets + `registry-item.json`) vào `registry/blocks/`
   (hoặc `npx hyperframes add <name>`).
2. **VERIFY**: `npm run library -- block <name>` → render preview clip + check rule (auto brand-skin).
3. **WIRE**: thêm rule keyword→`<name>` vào `4_BRAIN/block_picker.py._RULES` → tự overlay (budget 4/video).

### → COMPONENT (mảnh: caption-style / effect)
1. **BUILD**: *registry* → thả `<name>/` (`<name>.html` + `demo.html` + `registry-item.json`) vào `registry/components/`.
   *hand-built brand* → thêm nhánh `kind` trong `native_composer._component()`.
2. **VERIFY**: `npm run library -- component <name>` → render demo + lấy snippet.
3. **WIRE**: effect → nhúng snippet vào stage; caption-style → nối ASR word-timing (như caption tự build).

---

## Xem trạng thái bất cứ lúc nào
```
npm run library:status
  TEMPLATE : 20 archetypes  · template_picker (15 rules)
  BLOCK    : 97 blocks       · block_picker (15 rules) · budget 4/video
  COMPONENT: 25 (16 caption + 9 effect)
```

## Nguyên tắc bất biến (từ SIL + brand law)
- **Lấy PATTERN không lấy artifact** · **brand-first** (light-mode, brand_kit) · **không trùng** (dedup trước khi thêm)
- **Không orphan**: mỗi entry mới PHẢI vào selector (picker) + catalog, nếu không nó nằm chết
- **VERIFY bằng bằng chứng**: trích frame `ffmpeg -ss` rồi NHÌN, hoặc `npm run eval` — không claim suông
- **RECORD**: `INGESTION_LOG.md` + memory → không bao giờ re-vet/quên

Chi tiết "add recipe" từng layer: [`LIBRARY_GROWTH.md`](LIBRARY_GROWTH.md). Vòng tổng: [`6_SOP/SELF_IMPROVEMENT_LOOP.md`](../../6_SOP/SELF_IMPROVEMENT_LOOP.md).
