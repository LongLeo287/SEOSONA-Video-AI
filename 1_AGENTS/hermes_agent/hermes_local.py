import os
from openai import OpenAI
from dotenv import load_dotenv

# Load local environment variables for SEOSONA Video
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class LocalHermesAgent:
    """
    SEOSONA Video - Local Hermes Agent
    Một Đạo diễn (Director) độc lập dành riêng cho dự án Video, không phụ thuộc vào hệ điều hành gốc.
    Được trang bị để đánh giá kịch bản và cung cấp Insights trước khi Render.
    """
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            print("[WARNING] Local Hermes Agent cannot start: OPENAI_API_KEY is missing in .env")
        else:
            self.client = OpenAI(api_key=self.api_key)

    def validate_script(self, script_text, brand="seosona"):
        """Đánh giá kịch bản xem có chuẩn tone and voice của brand không."""
        if not self.api_key:
            return "SKIPPED: Hermes API key missing. (Local Mode)"
            
        system_prompt = (
            f"Bạn là Hermes, Đạo diễn nội dung của hệ thống SEOSONA Video (Brand: {brand.upper()}).\n"
            "Nhiệm vụ của bạn là đọc kịch bản video thô và đưa ra nhận xét ngắn gọn (Tối đa 2-3 câu) "
            "về cấu trúc, giọng điệu, và độ lôi cuốn. Nếu kịch bản có dấu hiệu quá dài dòng hoặc sáo rỗng, hãy cảnh báo."
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Hãy review kịch bản sau:\n{script_text}"}
                ],
                max_tokens=150,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"ERROR: Hermes LLM Engine failed: {e}"

def ask_local_hermes(script_text, brand="seosona"):
    agent = LocalHermesAgent()
    return agent.validate_script(script_text, brand)
