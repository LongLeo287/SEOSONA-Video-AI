import os
import sys
from typing import Dict

# Import the new LLM Engine
from importlib import import_module
llm_engine = import_module('4_BRAIN.llm_engine')
generate_json_from_prompt = llm_engine.generate_json_from_prompt

class SeoWriterAgent:
    """
    Agent specialized in writing SEO E-E-A-T Video/Blog scripts.
    Integrates analysis core from claude-seo:
    - Ensures Google's "Who/How/Why" Test
    - Optimizes AI Citation Readiness (for Google AI Overviews / Gemini Mode)
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        prompt_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '9_PROMPTS', 'video_scripts', 'seo_writer_prompt.md'
        ))
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = "You are the SEOSONA Video Script Writer Agent."
        
    def generate_script(self, scraped_data: Dict) -> Dict:
        """
        Calls Gemini LLM to generate script from scraped data.
        """
        raw_title = scraped_data.get("title", "No Title")
        raw_content = scraped_data.get("content", "")
        
        user_prompt = f"Analyze this article and generate a high-retention video script.\nTitle: {raw_title}\nContent:\n{raw_content}"
        
        print(f"[Writer Agent] Generating script using {self.model_name}...")
        
        response_json = generate_json_from_prompt(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            model_name=self.model_name
        )
        
        return response_json

if __name__ == "__main__":
    agent = SeoWriterAgent()
    print(agent.generate_script({"title": "Test", "content": "Test nội dung ngắn"}))
