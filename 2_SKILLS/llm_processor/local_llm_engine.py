import os
import traceback
import json

def process_script_with_llm(prompt, system_prompt="You are a helpful AI assistant for video creation."):
    """
    Process text/script using Local LLM via Nvidia NIM or Ollama API.
    By default, tries to use Nvidia NIM if NVIDIA_NIM_API_KEY is in .env.
    """
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Check for Nvidia NIM
        nim_api_key = os.getenv("NVIDIA_NIM_API_KEY")
        if nim_api_key:
            print("[Local LLM Engine] Using Nvidia NIM API (Llama 3 8B Instruct)...")
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=nim_api_key
            )
            model = "meta/llama3-8b-instruct"
        else:
            # Fallback to local Ollama
            print("[Local LLM Engine] Using Local Ollama (http://localhost:11434)...")
            client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama" # required but ignored
            )
            model = "llama3" # Default ollama model

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"[Local LLM Engine] Error: {e}")
        traceback.print_exc()
        return None
