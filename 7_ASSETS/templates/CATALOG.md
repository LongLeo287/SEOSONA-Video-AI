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

## Templates (10)

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

### `data-news`
*Tin/so sánh giàu data-viz — hero hook + biểu đồ cột + mockup dashboard*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → chart → mockup → feature → compare → tip → cta
- **accents:** blue, green, orange

### `insight-explainer`
*Giải thích khái niệm/góc nhìn (RAG fusion, essay AI...)*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → — → compare → steps → bignum → — → cta
- **accents:** orange, blue, green

### `opinion-insight`
*Bài góc nhìn/khái niệm (Khi AI lấy trí tuệ, LOOP là gì, RAG fusion)*

- **aspect:** 9:16 · **scenes:** 7 · **theme:** light
- **scene flow:** — → — → quote → feature → tip → bignum → cta
- **accents:** orange, blue, green

### `repo-showcase`
*Giới thiệu 1 dự án/tool mã nguồn mở GitHub*

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
*Giới thiệu + hướng dẫn dùng 1 tool (Prettier, cc-switch, Voicebox...)*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** bignum → — → repo → terminal → steps → compare → badges → cta
- **accents:** orange, blue, green

### `tutorial-gittree`
*Giới thiệu công cụ học/trực quan (vd học Git, Skills, tool)*

- **aspect:** 9:16 · **scenes:** 8 · **theme:** light
- **scene flow:** — → — → gittree → repo → terminal → steps → bignum → cta
- **accents:** green, blue, orange
