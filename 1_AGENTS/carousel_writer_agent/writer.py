"""
SEOSONA Carousel Writer Agent v2.0
===================================
Generates structured JSON slide data for 6 archetypes using the LLM engine.
"""
import os
import sys
from typing import List, Dict

from importlib import import_module
llm_engine = import_module('4_BRAIN.llm_engine')
generate_json_from_prompt = llm_engine.generate_json_from_prompt


def get_carousel_prompt():
    prompt_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '7_ASSETS', 'SEOSONA', 'SEOSONA Prompt', 'carousel SEOSONA.txt'
    ))
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are an expert Facebook Carousel Designer."


SLIDE_SCHEMA_PROMPT = """

CRITICAL: Analyze the provided content and create a professional Facebook Carousel.
You MUST output a STRICT JSON ARRAY of slides. Each slide has a "type" field.

AVAILABLE SLIDE TYPES:

1. "cover" — The FIRST slide. Dark navy hero or light intro.
   {
     "type": "cover",
     "tag": "AI AGENT FOR SEO",
     "label": "Đội ngũ AI Agent",
     "title": "5 năng lực thay đổi cách bạn làm SEO",
     "highlight": "thay đổi",
     "desc": "Mô tả ngắn 1-2 dòng.",
     "items": [
       {"text": "Tự động hóa sản xuất nội dung", "icon": "document"},
       {"text": "Tối ưu phân tích SEO", "icon": "chart"}
     ]
   }
   - "items" is OPTIONAL (use for list-type covers).
   - Available icons: document, chart, trend, database, refresh, zap, shield, clock, globe, lock, check, target, link, settings, question, star.

2. "comparison" — Side-by-side contrast (before/after, old/new, A vs B).
   {
     "type": "comparison",
     "slide_number": "01",
     "label": "MỤC TIÊU",
     "heading": "Từ 'Top 10' → Trích dẫn nguồn",
     "heading_highlight": "Trích dẫn nguồn",
     "left": {
       "label": "SEO TRUYỀN THỐNG",
       "title": "Mục tiêu là Top 10 Google",
       "items": ["Lên Top 10 kết quả tìm kiếm.", "Tập trung vào từ khóa volume lớn."]
     },
     "right": {
       "label": "SEO THỜI AI",
       "title": "Mục tiêu là được AI trích dẫn",
       "items": ["Xuất hiện trong AI Overview, ChatGPT...", "Nội dung đủ tin cậy để AI trích dẫn."]
     }
   }

3. "numbered_content" or "content" — Single panel with bullets or grid, optional closing band.
   {
     "type": "numbered_content",
     "slide_number": "01",
     "label": "NGUYÊN TẮC 01",
     "heading": "Đừng để AI tự nhớ, hãy cho AI dữ liệu để đọc",
     "heading_highlight": "tự nhớ",
     "desc": "LLM hoạt động dựa trên xác suất.",
     "body": ["Báo cáo ngành", "File PDF", "Website tham khảo"],
     "closing": "Yêu cầu AI chỉ sử dụng các nguồn này.",
     "closing_highlight": "nguồn này",
     "closing_icon": "lock"
   }
   - For a 2x2 grid, use "grid" instead of "body":
     "grid": [{"text": "Báo cáo ngành", "icon": "document"}, ...]

4. "process" — Numbered step-by-step rows.
   {
     "type": "process",
     "label": "AI AGENT VẬN HÀNH",
     "heading": "Agent làm gì trong 20 phút?",
     "heading_highlight": "20 phút",
     "steps": [
       {"title": "Dữ liệu thô từ công cụ nghiên cứu từ khóa", "icon": "database", "tag": "BƯỚC 1"},
       {"title": "Agent đọc Sitemap của website", "desc": "Quét sitemap.xml → product & category", "icon": "globe"}
     ],
     "stats": [
       {"value": "335", "label": "GIỮ LẠI"},
       {"value": "30", "label": "SAI NGÀNH"}
     ]
   }

5. "feature_cards" — Vertical benefit/feature stack.
   {
     "type": "feature_cards",
     "label": "COST & EFFICIENCY",
     "page_tag": "05 / 05 · AI AGENT FOR SEO",
     "heading": "Tiết kiệm chi phí & tăng hiệu suất",
     "heading_highlight": "chi phí",
     "features": [
       {"icon": "zap", "title": "Nhanh hơn nhiều lần", "desc": "Nghiên cứu từ khóa từ một tuần rút xuống vài giờ."},
       {"icon": "target", "title": "Tối ưu chi phí nhân sự", "desc": "Đội Agent thay tác vụ lặp lại."},
       {"icon": "clock", "title": "Sẵn sàng 24/7", "desc": "Vận hành liên tục."}
     ],
     "footer_cta": "Lưu lại & áp dụng"
   }

6. "grid" — Quote + grid items + closing band.
   {
     "type": "grid",
     "slide_number": "04",
     "label": "HÀNH VI TÌM KIẾM",
     "heading": "Từ Search Intent → Query Fanout",
     "heading_highlight": "Query Fanout",
     "quote": "Làm SEO cho doanh nghiệp B2B như thế nào?",
     "quote_label": "NGƯỜI DÙNG HỎI",
     "grid_label": "AI TỰ TÁCH THÀNH",
     "grid_items": ["Chi phí bao nhiêu?", "Mất bao lâu?", "KPI là gì?", "Case study nào phù hợp?"],
     "closing": "Nội dung trả lời được từng câu hỏi nhỏ → AI chọn bạn làm nguồn tham khảo.",
     "closing_highlight": "nguồn tham khảo",
     "closing_icon": "star"
   }

7. "image_split" — 50/50 split layout. One side text, one side image.
   {
     "type": "image_split",
     "label": "GIAO DIỆN",
     "heading": "Thiết kế trực quan",
     "heading_highlight": "trực quan",
     "desc": "Hiển thị ảnh minh hoạ sinh động thay vì chỉ có text.",
     "body": ["Biểu đồ", "Ảnh chụp màn hình", "Mô hình quy trình"],
     "image": ""
   }
   - "image" is the file path or URL. Leave it empty "" if no specific image is available (a placeholder will be drawn).

8. "mockup_showcase" — A large UI mockup (macOS window) holding an image.
   {
     "type": "mockup_showcase",
     "label": "KẾT QUẢ",
     "heading": "Báo cáo Tự động",
     "heading_highlight": "Báo cáo",
     "desc": "Giao diện dashboard SEO thực tế.",
     "image": ""
   }
   - "image" is the file path or URL. Leave it empty "" for a placeholder.

RULES:
- Generate 5 to 8 slides total.
- The FIRST slide MUST be type "cover".
- The LAST slide should be type "feature_cards" or "numbered_content" as a CTA/summary.
- Mix different types for visual variety. Do NOT make all slides the same type.
- Write ALL content in Vietnamese.
- Keep text concise — each slide is 1 key idea.
- Use "highlight" fields to emphasize 1-2 key phrases per slide.

OUTPUT ONLY THE JSON ARRAY — no markdown, no explanations.
"""


class CarouselWriterAgent:
    """Agent that converts content into structured carousel slide JSON."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.system_prompt = get_carousel_prompt() + SLIDE_SCHEMA_PROMPT

    def generate_slides(self, raw_content: str) -> list:
        print(f"[Carousel Writer] Generating Facebook Carousel using {self.model_name}...")
        user_prompt = f"Analyze this content and generate Facebook Carousel slides:\n\n{raw_content}"

        response_json = generate_json_from_prompt(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            model_name=self.model_name
        )

        if isinstance(response_json, list) and len(response_json) > 0:
            return response_json

        # Fallback mock data demonstrating multiple archetypes
        return [
            {
                "type": "cover",
                "tag": "BẢN TIN AI",
                "label": "Tin Tức Công Nghệ",
                "title": "Cách tạo Carousel tự động bằng AI",
                "highlight": "tự động",
                "desc": "Biến bài viết thành ảnh carousel chuyên nghiệp chỉ trong 1 phút.",
                "items": [
                    {"text": "Phân tích nội dung bằng LLM", "icon": "document"},
                    {"text": "Render HTML sang PNG", "icon": "chart"},
                    {"text": "Xuất bản đa nền tảng", "icon": "globe"},
                ]
            },
            {
                "type": "numbered_content",
                "slide_number": "01",
                "label": "BƯỚC 1",
                "heading": "Phân tích nội dung nguồn bằng AI",
                "heading_highlight": "AI",
                "desc": "LLM đọc toàn bộ nội dung và trích xuất ý chính.",
                "body": [
                    "Trích xuất câu từ ngắn gọn.",
                    "Phân loại theo chủ đề.",
                    "Tạo tiêu đề hấp dẫn cho mỗi slide."
                ],
                "closing": "AI xử lý trong vài giây — nhanh hơn 100x so với con người.",
                "closing_highlight": "100x",
                "closing_icon": "zap"
            },
            {
                "type": "feature_cards",
                "label": "KẾT QUẢ",
                "page_tag": "03 / 03",
                "heading": "Tại sao nên dùng carousel tự động?",
                "heading_highlight": "tự động",
                "features": [
                    {"icon": "zap", "title": "Tiết kiệm thời gian", "desc": "Từ 2 giờ thiết kế xuống còn 1 phút."},
                    {"icon": "check", "title": "Nhất quán thương hiệu", "desc": "Đúng màu, đúng font, đúng layout mọi lúc."},
                    {"icon": "trend", "title": "Tăng tương tác", "desc": "Carousel có CTR cao hơn 3x so với ảnh đơn."},
                ],
                "footer_cta": "Áp dụng ngay →"
            }
        ]


if __name__ == "__main__":
    agent = CarouselWriterAgent()
    import json
    result = agent.generate_slides("Nội dung thử nghiệm về cách dùng AI tạo ảnh carousel cho Facebook.")
    print(json.dumps(result, indent=2, ensure_ascii=False))
