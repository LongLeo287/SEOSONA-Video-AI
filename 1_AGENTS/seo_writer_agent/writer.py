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
        self.system_prompt = """
        You are the SEOSONA Video Script Writer Agent.
        Task: Convert raw article/data into a short (Shorts/Reels) or long (Youtube) video script.

        SEO E-E-A-T & AI CITATION STANDARDS (Based on claude-seo):
        1. Experience & Expertise: Must retain and emphasize stats, citations, expert names from the original article.
        2. Strong Hook: The first 3 seconds must hit the viewer's insight ("Why does it exist?").
        3. AI Citation Readiness: Logical script structure, providing "Answer-first formatting" to be easily cited by Google AI Overviews.
        4. B-roll Keywords: For each dialog line, provide 1-2 concise English keywords for the Auto B-roll system to find background videos.

        IMPORTANT: THE FINAL OUTPUT SCRIPT MUST BE IN VIETNAMESE.

        OUTPUT FORMAT (Strict JSON):
        {
            "title": "Optimized Video Title",
            "seo_score_estimate": 95,
            "scenes": [
                {
                    "narrator_text": "Chào mừng các bạn đến với bản tin SEOSONA...",
                    "search_terms": ["news anchor", "technology matrix"]
                }
            ]
        }
        """
        
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
