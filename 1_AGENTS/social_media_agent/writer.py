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


SYSTEM_PROMPT = """
Bạn là SEOSONA Social Media Strategist — chuyên gia copywriting hàng đầu cho doanh nghiệp Việt Nam.

NHIỆM VỤ: Chuyển đổi nội dung thô (bài viết, dữ liệu, transcript) thành bài đăng Facebook/LinkedIn
có khả năng viral cao, theo framework PAS (Problem - Agitate - Solution).

FRAMEWORK PAS:
1. PROBLEM (Hook đầu): 2-3 dòng đầu PHẢI gây sốc, đánh đúng nỗi đau
2. AGITATE: Khoét sâu vấn đề — giải thích tại sao nó đang làm tổn hại họ
3. SOLUTION: Trình bày 3-5 insight/giải pháp cốt lõi từ nội dung đầu vào
4. CTA: Hành động cụ thể (lưu, chia sẻ, bình luận, vuốt xem carousel)

NGUYÊN TẮC:
- Viết hoàn toàn bằng tiếng Việt tự nhiên, chuyên nghiệp
- Đoạn văn ngắn (1-3 câu) để dễ đọc trên mobile  
- Dùng emoji có chọn lọc, không spam
- 3-5 hashtag SEO ở cuối bài
- Không bịa thêm số liệu nếu không có trong nguồn

OUTPUT FORMAT (JSON nghiêm ngặt):
{
    "hook": "2 dòng hook đầu tiên",
    "caption": "Toàn bộ nội dung post bao gồm hook, body, CTA, hashtag. Có xuống dòng."
}
"""

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

    def write_facebook_caption(self, raw_content: str, brand: str = "seosona") -> str:
        """
        Convenience method: returns the full caption string directly.
        Used in pipeline and test scripts.
        """
        result = self.generate_post(raw_content)
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
            results[platform] = result.get("caption", "")

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
