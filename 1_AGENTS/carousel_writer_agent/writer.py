import os
import sys
from typing import Dict

# Import the new LLM Engine
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

class CarouselWriterAgent:
    """
    Agent specialized in converting long-form content/SRT into Facebook Carousel Slides.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.system_prompt = get_carousel_prompt()
        self.system_prompt += """
        
        CRITICAL: Analyze the provided content and extract a sequence of 5 to 10 slides for a Facebook Carousel.
        OUTPUT STRICT JSON ARRAY FORMAT:
        [
            {
                "type": "cover",
                "pill": "MẸO DÙNG AI",
                "title": "CÁCH DÙNG GPT-4",
                "highlight": "GPT-4",
                "desc": "Bí mật tối ưu prompt",
                "dots": "1/5"
            },
            {
                "type": "content",
                "slide_number": "02",
                "heading": "Bước 1...",
                "heading_highlight": "Bước 1",
                "body": ["Đầu tiên bạn cần...", "Sau đó..."],
                "closing": "Nhớ lưu lại!",
                "closing_highlight": "lưu lại"
            }
        ]
        """
        
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
            
        # Fallback mock if API keys missing
        return [
            {
                "type": "cover",
                "pill": "BẢN TIN AI",
                "title": "CÁCH TẠO CAROUSEL TỰ ĐỘNG",
                "highlight": "TỰ ĐỘNG",
                "desc": "Biến bài viết thành ảnh tĩnh trong 1 nốt nhạc",
                "dots": "1/3"
            },
            {
                "type": "content",
                "slide_number": "02",
                "heading": "Sử Dụng LLM",
                "heading_highlight": "LLM",
                "body": ["Phân tích nội dung gốc.", "Trích xuất câu từ ngắn gọn."],
                "closing": "Áp dụng ngay!",
                "closing_highlight": "Áp dụng"
            },
            {
                "type": "content",
                "slide_number": "03",
                "heading": "Sử Dụng Playwright",
                "heading_highlight": "Playwright",
                "body": ["Render HTML thành PNG.", "Thiết kế chuẩn màu SEOSONA."],
                "closing": "SEOSONA.com",
                "closing_highlight": "SEOSONA"
            }
        ]

if __name__ == "__main__":
    agent = CarouselWriterAgent()
    print(agent.generate_slides("Nội dung thử nghiệm về cách dùng AI tạo ảnh tĩnh."))
