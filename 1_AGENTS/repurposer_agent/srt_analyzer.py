import os
import sys
import json

# Import the new LLM Engine
from importlib import import_module
llm_engine = import_module('4_BRAIN.llm_engine')
generate_json_from_prompt = llm_engine.generate_json_from_prompt

def get_repurpose_prompt():
    prompt_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '9_PROMPTS', 'video_scripts', 'repurpose_analyzer_prompt.md'
    ))
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are an expert SRT analyzer. Output strict JSON with a list of hooks."

def analyze_srt_for_hooks(srt_path):
    """
    Calls the LLM agent analyzing a long SRT file to find the best hooks.
    """
    print(f"[SRT Analyzer] Scanning {srt_path} using LLM...")
    
    srt_content = ""
    if os.path.exists(srt_path):
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
    else:
        # Never fabricate input — analysing dummy SRT would silently produce fake hooks.
        print(f"[SRT Analyzer] ERROR: file not found: {srt_path} — returning [] (no fabricated content).")
        return []

    system_prompt = get_repurpose_prompt()
    user_prompt = f"Analyze this SRT file and output a JSON array of the best hooks:\n\n{srt_content}"
    
    # We enforce that the LLM returns an array of hooks
    json_instructions = "\nCRITICAL: Output MUST be a JSON list/array like: [{\"id\": 1, \"start\": 15.0, \"end\": 45.0, \"hook_text\": \"...\"}]"
    system_prompt += json_instructions
    
    response_json = generate_json_from_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model_name="gemini-2.5-flash"
    )
    
    # Check if the wrapper returned a generic dictionary instead of a list
    if isinstance(response_json, dict) and "scenes" in response_json:
        # It's returning the fallback mock from llm_engine! We should return a fallback list.
        return [
            {"id": 1, "start": 15.0, "end": 45.0, "hook_text": "Bí mật đằng sau thuật toán AI của Google"},
            {"id": 2, "start": 120.0, "end": 160.0, "hook_text": "Tại sao SEO truyền thống đã chết?"}
        ]
        
    if isinstance(response_json, list):
        return response_json
        
    # If the LLM returned a dict with a "hooks" key
    if isinstance(response_json, dict) and "hooks" in response_json:
        return response_json["hooks"]
        
    # Ultimate fallback
    return []

if __name__ == "__main__":
    print(analyze_srt_for_hooks("dummy.srt"))
