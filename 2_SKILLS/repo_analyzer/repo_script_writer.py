import sys
import os

# Add paths to access local_llm_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'llm_processor')))

def generate_repo_script(readme_content, repo_url):
    """
    Uses Local LLM to analyze the README and generate a Vietnamese video script.
    """
    try:
        from local_llm_engine import process_script_with_llm
    except ImportError:
        print("[Repo Script Writer] local_llm_engine not found.")
        return None
        
    print(f"[Repo Script Writer] Analyzing README ({len(readme_content)} chars) with Local LLM...")
    
    system_prompt = """Bạn là một chuyên gia Review mã nguồn mở trên Github cho một kênh YouTube công nghệ.
Hãy đọc README của Repository sau đây và viết ra một kịch bản giới thiệu CỰC KỲ HẤP DẪN, RÕ RÀNG bằng TIẾNG VIỆT.
Cấu trúc kịch bản phải nói tự nhiên, thân thiện. Giới hạn khoảng 100-150 chữ (để video dài khoảng 30-40 giây).
Đừng dùng các ký tự đặc biệt khó đọc như markdown, chỉ viết chữ thuần để phần mềm đọc Voice (TTS) có thể đọc trơn tru."""

    prompt = f"System log"
    
    script_result = process_script_with_llm(prompt, system_prompt)
    if script_result:
        # Clean up any quotes or markdown blocks that the LLM might have returned
        script_result = script_result.replace("```text", "").replace("```", "").strip()
        print("[Repo Script Writer] Script generated successfully!")
        return script_result
    else:
        print("[Repo Script Writer] Failed to connect to LLM. Using fallback dummy script for testing...")
        fallback = f"System log"
        return fallback
