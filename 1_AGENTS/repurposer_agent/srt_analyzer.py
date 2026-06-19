import os
import json

def get_repurpose_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), 'srt_analyzer_prompt.md')
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Error: Prompt file not found."

def analyze_srt_for_hooks(srt_path):
    """
    Simulates an LLM agent analyzing a long SRT file to find the best hooks.
    In production, this sends the `srt_analyzer_prompt.md` + SRT text to an LLM.
    """
    print(f"Agent 'SRT Analyzer' scanning {srt_path} using Expert Prompt...")
    
    # Simulate the matrix output from the LLM
    print("Matrix Table Generated: HOOK -> NỖI ĐAU -> TIP/TRICK -> CASE STUDY -> ĐÚC KẾT")
    
    # Dummy data extracted from the simulated Matrix
    hooks = [
        {"id": 1, "start": 15.0, "end": 45.0, "hook_text": "Bí mật đằng sau thuật toán AI của Google"},
        {"id": 2, "start": 120.0, "end": 160.0, "hook_text": "Tại sao SEO truyền thống đã chết?"},
        {"id": 3, "start": 300.0, "end": 350.0, "hook_text": "Cách dùng Chat GPT để qua mặt đối thủ"}
    ]
    
    return hooks
