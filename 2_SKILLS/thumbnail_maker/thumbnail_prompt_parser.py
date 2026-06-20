import os
import sys

# Import the new LLM Engine
from importlib import import_module
llm_engine = import_module('4_BRAIN.llm_engine')
generate_json_from_prompt = llm_engine.generate_json_from_prompt

def get_thumbnail_prompt():
    prompt_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '7_ASSETS', 'SEOSONA', 'SEOSONA Prompt', 'Thumbnail SEOSONA 2.txt'
    ))
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are a Thumbnail UX Designer."

def extract_thumbnail_data_from_script(script_content: str) -> dict:
    """
    Calls the LLM using the Thumbnail SEOSONA 2.txt prompt to compress the raw script
    into high-impact thumbnail text components.
    """
    print(f"[Thumbnail Parser] Extracting high-impact texts using LLM...")
    
    system_prompt = get_thumbnail_prompt()
    
    # Force JSON output format
    json_instructions = """
    CRITICAL: You MUST extract the requested variables and output them in the following strict JSON format:
    {
        "PILL_LABEL": "...",
        "MAIN_TITLE": "...",
        "TITLE_HIGHLIGHT_KEYWORD": "...",
        "SHORT_HOOK": "...",
        "CTA_TEXT": "...",
        "CTA_HIGHLIGHT_KEYWORD": "...",
        "SUBTEXT_ITALIC": "A short philosophical or inspiring italic subtext (1 line). Example: 'Dùng AI để tăng hiệu suất, không phải để rảnh hơn'. Leave empty if not appropriate.",
        "LAYOUT_TYPE": "portrait or text_only. Use 'portrait' if the content references a person/speaker. Use 'text_only' for pure topic/data thumbnails."
    }
    """

    system_prompt += json_instructions
    
    user_prompt = f"Analyze the following [RAW_VIDEO_CONTENT] and extract the thumbnail variables:\n\n{script_content}"
    
    response_json = generate_json_from_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model_name="gemini-2.5-flash"
    )
    
    return response_json

if __name__ == "__main__":
    test_script = "Làm sao để nhân bản video ngắn tự động bằng AI và kéo 1 triệu view TikTok chỉ trong vòng 1 tháng."
    print(extract_thumbnail_data_from_script(test_script))
