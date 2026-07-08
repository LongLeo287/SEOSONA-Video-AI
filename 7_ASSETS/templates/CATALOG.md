# Template Catalog (HyperFrames · renderer: native_composer)

Auto-generated from `7_ASSETS/templates/*.json` (regen: `python scripts/gen_catalog.py`).
Each template is a scene sequence; the template owns visual design — you only write
text (`segments` + 2-tone `headings`). Content is validated by `4_BRAIN/script_schema.py`
before render.

> **RULE #1**: on-screen text (`h1`/`h2`/`kicker`) keeps formatting ("5.5", "82%") and
> may use 0–1 emoji; the spoken `segments` (voiceText) must be CLEAN — no emoji / URL /
> `→ % $ #`. Numbers in voiceText are spelled out (handled by news_video_standards).

## Char budgets (poster discipline — checked as warnings)

| Field | Budget | Note |
|---|---|---|
| `kicker` | ≤24 chars | small uppercase pill label |
| `h1` | ≤24 chars | heading line 1 — punchy |
| `h2` | ≤24 chars | the accent-highlighted word/phrase |
| each `segment` | ≤45 words | one idea per scene; longer → split into more scenes |

## Templates (20)

### `ai-news-flash`
*Tin AI nhanh (Seedance, Gemini API...) ~20-25s*

- **aspect:** 9:16 · **scenes:** 6 · **theme:** light
- **scene flow:** — → — → repo → bignum → badges → cta
- **accents:** orange, blue, green

### `benchmark-news`
*Tin có nhiều con số/benchmark (Gemini SQL 80%, Kimi nhanh 6×, MCP -99% token)*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → stats → compare → feature → bignum → badges → cta
- **accents:** orange, blue, green

### `case-study`
*Câu chuyện vấn đề → hành động → kết quả (1 thương hiệu tăng X% nhờ Y).*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → quote → steps → compare → bignum → tip → cta
- **accents:** orange, blue, green

### `data-news`
*Tin/so sánh giàu data-viz — hero hook + biểu đồ cột + mockup dashboard*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → chart → mockup → feature → compare → tip → cta
- **accents:** blue, green, orange

### `deep-tutorial`
*Tutorial nhiều bước — mục tiêu → setup → các bước → kết quả → lưu ý.*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → terminal → steps → mockup → tip → bignum → cta
- **accents:** orange, blue, green

### `faq`
*Trả lời nhanh 3 câu hỏi thường gặp về một chủ đề.*

- **aspect:** 9:16 · **scenes:** 6 · **theme:** light
- **scene flow:** — → feature → feature → tip → bignum → cta
- **accents:** orange, blue, green

### `insight-explainer`
*Giải thích PHÂN TÍCH khái niệm — so sánh + các bước hoạt động (RAG fusion, essay AI). Khác opinion-insight (góc nhìn có trích dẫn).*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → — → compare → steps → bignum → — → cta
- **accents:** orange, blue, green

### `launch`
*Công bố sản phẩm/tính năng mới — tính năng + giao diện + so với cũ + thông số.*

- **aspect:** 9:16 · **scenes:** 6 · **theme:** light
- **scene flow:** bignum → feature → mockup → compare → stats → cta
- **accents:** orange, blue, green

### `listicle-top5`
*Liệt kê N công cụ/mẹo (Top 5 công cụ AI, 7 thủ thuật). Hook → từng mục → cách dùng → chốt.*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → — → chart → feature → steps → bignum → cta
- **accents:** orange, blue, green

### `myth-buster`
*Lầm tưởng phổ biến → sự thật + bằng chứng (SEO đã chết? AI thay lập trình viên?).*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → quote → compare → feature → tip → bignum → cta
- **accents:** orange, blue, green

### `opinion-insight`
*Bài GÓC NHÌN có trích dẫn — quote + điểm chính + ghi nhớ (Khi AI lấy trí tuệ, LOOP là gì). Khác insight-explainer (phân tích: so sánh + các bước).*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → — → quote → feature → tip → bignum → cta
- **accents:** orange, blue, green

### `quick-tip`
*Một thủ thuật gọn — mẹo → cách làm → lợi ích. Video ngắn 15-20s.*

- **aspect:** 9:16 · **scenes:** 5 · **theme:** light
- **scene flow:** — → tip → steps → bignum → cta
- **accents:** orange, blue, green

### `repo-showcase`
*Showcase 1 dự án GitHub — sao/tags + so sánh + benchmark. Để GIỚI THIỆU dự án (không dạy cách dùng).*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → repo → compare → terminal → bignum → badges → cta
- **accents:** orange, blue, green

### `resource-list`
*Kho tài nguyên/list (System Prompts, FreeLLMAPI...)*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** — → — → repo → steps → terminal → bignum → badges → cta
- **accents:** orange, blue, green

### `seo-explainer`
*Tin & kiến thức SEO/Marketing (Google update, SEO thời AI, GEO/AEO, ranking)*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → compare → steps → feature → tip → bignum → cta
- **accents:** orange, blue, green

### `tool-walkthrough`
*Hướng dẫn DÙNG 1 CLI/tool — có bước steps (cách dùng). Khác repo-showcase (chỉ giới thiệu, không steps).*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → repo → terminal → steps → compare → badges → cta
- **accents:** orange, blue, green

### `transformation`
*Hành trình thay đổi — trước → các bước → sau + cảm nhận.*

- **aspect:** 9:16 · **scenes:** 6 · **theme:** light
- **scene flow:** — → compare → steps → bignum → quote → cta
- **accents:** orange, blue, green

### `trend-alert`
*Xu hướng mới nổi — số liệu + vì sao + cách đón đầu (GEO/AEO, AI agents).*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** bignum → — → stats → feature → steps → tip → cta
- **accents:** orange, blue, green

### `tutorial-gittree`
*Giới thiệu công cụ học/trực quan (vd học Git, Skills, tool)*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** — → — → gittree → repo → terminal → steps → bignum → cta
- **accents:** green, blue, orange

### `versus-deep`
*Đối đầu 2 lựa chọn — thông số + khác biệt + nên chọn gì (ChatGPT vs Claude, SEO vs GEO).*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → compare → stats → compare → feature → bignum → cta
- **accents:** orange, blue, green
