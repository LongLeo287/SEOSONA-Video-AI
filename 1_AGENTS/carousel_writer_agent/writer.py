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


def get_carousel_master_prompt():
    prompt_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '9_PROMPTS', 'social_media', 'carousel_master_prompt.md'
    ))
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are an expert Facebook Carousel Designer."

class CarouselWriterAgent:
    """Agent that converts content into structured carousel slide JSON."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.system_prompt = get_carousel_master_prompt()

    @staticmethod
    def _safety_review(slides):
        """Carousels are outward-facing (Facebook) but had NO content-safety gate — a slide could ship an
        off-platform CTA / unsafe-or-absolute claim / fabricated social-proof uncaught. Run the SAME
        content_moderation gate the video path uses and SURFACE issues loudly for review before posting."""
        try:
            import sys as _sys, os as _os
            _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "..", "4_BRAIN"))
            cm = __import__("content_moderation")

            def _strings(x):
                if isinstance(x, str):
                    return [x]
                if isinstance(x, dict):
                    return [s for v in x.values() for s in _strings(v)]
                if isinstance(x, (list, tuple)):
                    return [s for v in x for s in _strings(v)]
                return []

            v = cm.moderate(" ".join(_strings(slides)), record=False)
            blocks = [f for f in v.get("flags", []) if f.get("severity") == "block"]
            if blocks:
                print("[Carousel Writer] ⛔ CONTENT-SAFETY — REVIEW BEFORE POSTING: "
                      + "; ".join(f"{f.get('kind')}: {f.get('detail')}" for f in blocks))
            elif v.get("flags"):
                print("[Carousel Writer] ⚠ content-safety (advisory): "
                      + ", ".join(f.get("kind") for f in v["flags"]))
        except Exception as _e:
            print(f"[Carousel Writer] content-safety check skipped ({_e})")

    def generate_slides(self, raw_content: str) -> list:
        print(f"[Carousel Writer] Generating Facebook Carousel using {self.model_name}...")
        user_prompt = f"Analyze this content and generate Facebook Carousel slides:\n\n{raw_content}"

        response_json = generate_json_from_prompt(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            model_name=self.model_name
        )

        if isinstance(response_json, list) and len(response_json) > 0:
            self._safety_review(response_json)
            return response_json

        # Offline placeholder (LLM returned nothing / no API key). Logged loudly so this
        # demo content is never mistaken for generated output.
        print("[Carousel Writer] WARNING: LLM unavailable — returning OFFLINE PLACEHOLDER carousel (not real content).")
        placeholder = [
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
                "closing": "AI xử lý trong vài giây — nhanh hơn hẳn so với làm thủ công.",
                "closing_highlight": "vài giây",
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
                    {"icon": "trend", "title": "Tăng tương tác", "desc": "Carousel thường có CTR cao hơn ảnh đơn."},
                ],
                "footer_cta": "Áp dụng ngay →"
            }
        ]
        self._safety_review(placeholder)   # gate the placeholder too — so NO return path skips content-safety
        return placeholder


if __name__ == "__main__":
    agent = CarouselWriterAgent()
    import json
    result = agent.generate_slides("Nội dung thử nghiệm về cách dùng AI tạo ảnh carousel cho Facebook.")
    print(json.dumps(result, indent=2, ensure_ascii=False))
