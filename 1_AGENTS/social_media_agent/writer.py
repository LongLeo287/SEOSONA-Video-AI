import os
import sys
from typing import Dict
from importlib import import_module

llm_engine = import_module('4_BRAIN.llm_engine')
generate_json_from_prompt = llm_engine.generate_json_from_prompt

class SocialMediaAgent:
    """
    Agent specialized in writing SEO-optimized Social Media Posts (Facebook/LinkedIn).
    Applies the PAS (Problem - Agitate - Solution) framework.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.model_name = model_name
        self.system_prompt = """
        You are the SEOSONA Social Media Strategist and Copywriter.
        Task: Convert raw article/data or transcripts into a high-converting, SEO-optimized Facebook/LinkedIn Post.

        COPYWRITING FRAMEWORK: PAS (Problem - Agitate - Solution)
        1. PROBLEM (The Hook): Start with a strong, relatable problem or a shocking statement in the first 2-3 lines.
        2. AGITATE: Twist the knife. Explain why this problem is costing them time, money, or effort.
        3. SOLUTION: Present the core insights from the input data as the definitive solution.
        4. CTA (Call to Action): Tell them exactly what to do next (e.g., read the images below, leave a comment).

        SEO & FORMATTING RULES:
        - Use engaging emojis, but don't overdo it.
        - Break text into short, readable paragraphs (1-3 sentences max).
        - Include 3-5 highly relevant SEO hashtags at the bottom (e.g., #SEOSONA #Marketing #SEO).
        - The output MUST be in natural, professional VIETNAMESE.

        OUTPUT FORMAT (Strict JSON):
        {
            "hook": "The first catchy 2 lines",
            "caption": "The FULL complete post text including Hook, Body, CTA, and Hashtags. This must be formatted with newlines."
        }
        """
        
    def generate_post(self, raw_data: str) -> Dict:
        """
        Calls Gemini LLM to generate a social media post from raw data.
        """
        user_prompt = f"Analyze this data and write a PAS framework Social Media Post.\n\nRaw Data:\n{raw_data}"
        
        print(f"[Social Media Agent] Writing SEO Caption using {self.model_name}...")
        
        response_json = generate_json_from_prompt(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            model_name=self.model_name
        )
        
        return response_json

if __name__ == "__main__":
    agent = SocialMediaAgent()
    res = agent.generate_post("SEO truyền thống mất 6 tháng, SEO AI mất 1 tháng nhưng ít người biết cách làm.")
    print(res.get("caption"))
