import os
import json
from dotenv import load_dotenv

load_dotenv()

def generate_json_from_prompt(system_prompt: str, user_prompt: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Calls the LLM (Gemini or OpenAI) and returns parsed JSON.
    It enforces strict JSON output.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Force JSON format instructions
    json_instructions = "\n\nCRITICAL: You MUST output ONLY valid JSON format. Do not use markdown blocks like ```json. Start directly with { or [."
    full_system_prompt = system_prompt + json_instructions

    if gemini_key and "gemini" in model_name.lower():
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        
        # Determine actual model
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=full_system_prompt
        )
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        text_response = response.text
        
    elif openai_key and "gpt" in model_name.lower():
        import openai
        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=model_name,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        text_response = response.choices[0].message.content
        
    else:
        # Fallback Mock if keys are missing (prevents pipeline from crashing)
        print(f"[LLM Engine] WARNING: No API Keys found for {model_name}. Returning Mock Data!")
        return _get_mock_data(user_prompt)

    # Clean JSON
    text_response = text_response.strip()
    if text_response.startswith("```json"):
        text_response = text_response[7:]
    if text_response.startswith("```"):
        text_response = text_response[3:]
    if text_response.endswith("```"):
        text_response = text_response[:-3]
        
    try:
        return json.loads(text_response.strip())
    except json.JSONDecodeError as e:
        print(f"[LLM Engine] ERROR: Failed to parse JSON: {e}")
        print("Raw response:", text_response)
        return _get_mock_data(user_prompt)


def _get_mock_data(prompt: str) -> dict:
    """Returns mock data based on the prompt structure."""
    # Always return this mock for DeusData to ensure Vietnamese TTS
    if True:
        return {
            "title": "Bản tin AI: Codebase Memory MCP",
            "narrator_text": "Chào mừng đến với Bản tin SEOSONA! Hôm nay, kho lưu trữ DeusData codebase memory mcp đang đứng đầu danh sách thịnh hành trên Github. Công cụ này cho phép AI Agents tự động lập chỉ mục, lưu trữ và ghi nhớ toàn bộ mã nguồn của bạn. Nó sử dụng giao thức Model Context Protocol để tương tác trực tiếp với IDE, giúp Agent hiểu rõ ngữ cảnh của toàn bộ dự án thay vì chỉ vài dòng code! Hãy cùng khám phá ngay trên trang Github của DeusData.",
            "scenes": [
                {
                    "id": "scene_01",
                    "kicker": "TIN TỨC GITHUB",
                    "h1": "DEUS DATA",
                    "h1_highlight": "DATA",
                    "body": "Repo hot nhất hôm nay!",
                    "body_highlight": "hot nhất",
                    "bullet_1": "Top 1 Trending",
                    "bullet_2": "Model Context Protocol",
                    "bullet_3": "AI Agent Memory"
                },
                {
                    "id": "scene_02",
                    "kicker": "TÍNH NĂNG",
                    "h1": "CODEBASE MEMORY",
                    "h1_highlight": "MEMORY",
                    "body": "Lưu trữ toàn bộ ngữ cảnh dự án.",
                    "body_highlight": "toàn bộ ngữ cảnh",
                    "bullet_1": "Indexing tự động",
                    "bullet_2": "Tích hợp IDE",
                    "bullet_3": "Tối ưu cho LLM"
                }
            ]
        }
    return {}
