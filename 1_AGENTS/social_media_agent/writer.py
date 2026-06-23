"""
SEOSONA Social Media Agent v2.0
================================
Viết caption Facebook/LinkedIn/TikTok theo framework PAS (Problem-Agitate-Solution).
Hoạt động hoàn toàn không cần API key nhờ LLM Engine Smart Offline NLP.
"""
import os
import sys
from typing import Dict
from importlib import import_module

llm_engine = import_module('4_BRAIN.llm_engine')
generate_json_from_prompt = llm_engine.generate_json_from_prompt
generate_text_from_prompt = llm_engine.generate_text_from_prompt


def get_system_prompt():
    prompt_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '9_PROMPTS', 'social_media', 'pas_caption_prompt.md'
    ))
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Bạn là SEOSONA Social Media Strategist."

SYSTEM_PROMPT = get_system_prompt()

HASHTAG_SETS = {
    "SEO":       "#SEO #SEO2026 #DigitalMarketing #SEOSONA #ContentMarketing #GoogleSEO",
    "AI_AGENT":  "#AIAgent #AI2026 #AutomationAI #SEOSONA #TechVietnam #AIMarketing",
    "CONTENT":   "#ContentMarketing #ContentStrategy #SEOSONA #Copywriting #SocialMedia",
    "BUSINESS":  "#BusinessGrowth #StartupVietnam #SEOSONA #Entrepreneur #GrowthHacking",
    "MARKETING": "#Marketing #DigitalMarketing #SEOSONA #BrandStrategy #GrowthHacking",
    "TECH":      "#Tech #Developer #SEOSONA #AITool #TechVietnam #OpenSource",
    "GENERAL":   "#SEOSONA #Marketing #Business #AI #Vietnam #KnowledgeSharing",
}


class SocialMediaAgent:
    """
    Agent chuyên viết nội dung Social Media cho SEOSONA & Chí Quyết Academy.
    Hỗ trợ Facebook, LinkedIn, TikTok caption.
    Không cần API key — Smart Offline NLP Engine đảm nhận khi không có key.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name

    def generate_post(self, raw_data: str) -> Dict:
        """
        Generate a full PAS social media post from raw content.
        Returns dict with 'hook' and 'caption' keys.
        """
        user_prompt = (
            f"Analyze this data and write a PAS framework Social Media Post.\n\n"
            f"Raw Data:\n{raw_data}"
        )
        print(f"[Social Media Agent] Writing caption via {self.model_name}...")
        return generate_json_from_prompt(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model_name=self.model_name
        )

    def _caption_from_unexpected_result(self, raw_content: str, result) -> str:
        """
        Keep the image workflow alive if a provider returns slide JSON instead of
        the expected PAS caption object.
        """
        offline_social_generator = getattr(llm_engine, "_generate_social_post_offline", None)
        if callable(offline_social_generator):
            fallback_prompt = (
                "Analyze this data and write a PAS framework Social Media Post.\n\n"
                f"Raw Data:\n{raw_content}"
            )
            fallback = offline_social_generator(fallback_prompt)
            if isinstance(fallback, dict) and fallback.get("caption"):
                return fallback["caption"]

        if isinstance(result, list):
            slide_titles = []
            for slide in result:
                if not isinstance(slide, dict):
                    continue
                title = slide.get("title") or slide.get("heading") or slide.get("label")
                if title:
                    slide_titles.append(str(title).strip())
            if slide_titles:
                return "\n".join([
                    "SEOSONA ghi lại những điểm quan trọng:",
                    *[f"- {title}" for title in slide_titles[:5]],
                    "",
                    "#SEOSONA #AI #Marketing #Vietnam",
                ])

        return raw_content[:600].strip()

    def write_facebook_caption(self, raw_content: str, brand: str = "seosona") -> str:
        """
        Convenience method: returns the full caption string directly.
        Used in pipeline and test scripts.
        """
        result = self.generate_post(raw_content)
        if not isinstance(result, dict):
            return self._caption_from_unexpected_result(raw_content, result)

        caption = result.get("caption", "")
        if not caption:
            caption = result.get("hook", raw_content[:200])
        return caption

    def write_multi_platform(self, raw_content: str, platforms: list = None) -> Dict:
        """
        Generate captions for multiple platforms simultaneously.
        Each platform gets adapted tone/length/hashtags.
        """
        platforms = platforms or ["facebook", "linkedin", "tiktok"]
        results = {}

        platform_modifiers = {
            "facebook": "Phong cách: thân thiện, cộng đồng. Độ dài: 200-400 từ.",
            "linkedin": "Phong cách: chuyên nghiệp, B2B, thought leadership. Độ dài: 150-300 từ.",
            "tiktok": "Phong cách: ngắn gọn, trẻ trung, viral. Độ dài: 50-100 từ. Nhiều hashtag trend.",
        }

        for platform in platforms:
            modifier = platform_modifiers.get(platform, "")
            modified_prompt = f"{raw_content}\n\n[PLATFORM: {platform.upper()}]\n{modifier}"
            result = self.generate_post(modified_prompt)
            if isinstance(result, dict):
                results[platform] = result.get("caption", "")
            else:
                results[platform] = self._caption_from_unexpected_result(modified_prompt, result)

        return results

    def write_comment_thread(self, main_caption: str, num_comments: int = 3) -> list:
        """
        Generate follow-up comment thread (for seeding engagement).
        """
        system = """
        Tạo chuỗi comment tự nhiên để seed engagement cho post Facebook.
        Mỗi comment: 1-3 câu, tự nhiên như người thật comment.
        Xen kẽ giữa câu hỏi, chia sẻ kinh nghiệm, và đồng tình.
        OUTPUT: JSON array of strings.
        """
        user_p = f"Tạo {num_comments} comment tự nhiên cho post này:\n\n{main_caption}"
        result = generate_json_from_prompt(system, user_p, self.model_name)
        if isinstance(result, list):
            return result
        # Offline fallback
        return [
            "Hay quá! Mình đang gặp đúng vấn đề này. Cảm ơn anh đã chia sẻ!",
            "Thực ra mình cũng thử cách này rồi, kết quả tốt hơn nhiều so với cách cũ.",
            "Câu hỏi: vậy nếu doanh nghiệp nhỏ thì bắt đầu từ đâu trước ạ?",
        ][:num_comments]


if __name__ == "__main__":
    agent = SocialMediaAgent()
    
    test_content = """
    AI Agent trong SEO 2026: 80% doanh nghiep dang lam sai.
    335 tu khoa duoc phan loai trong 20 phut thay vi 3 ngay thu cong.
    Ty le len top Google tang 47%. Chi phi content giam 60%.
    """
    
    print("=== Social Media Agent Test ===\n")
    post = agent.generate_post(test_content)
    print("HOOK:", post.get("hook"))
    print("\nFULL CAPTION:")
    print(post.get("caption"))
    
    print("\n=== Facebook Caption (direct) ===")
    caption = agent.write_facebook_caption(test_content)
    print(caption[:300], "...")
