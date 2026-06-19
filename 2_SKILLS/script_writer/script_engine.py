"""
Script Writer Skill — Generates video scripts using the 5-Part Structure.
Inherited from SEOSONA OS Skill: seo_marketing/video_content.
"""

def get_script_prompt(topic, brand_profile, duration_seconds=60):
    """
    Returns an LLM prompt to generate a video script.
    Based on SEOSONA OS video_content SKILL.md 5-Part Script Structure.
    """
    brand_tone = brand_profile.get('brand_tone', 'Professional')
    target = brand_profile.get('target_audience', 'Target Audience')

    prompt = f"""
Bạn là một chuyên gia viết kịch bản Video Short (Shorts/TikTok/Reels) chuyên ngành SEO & Digital Marketing.
Viết một kịch bản video dài khoảng {duration_seconds} giây về chủ đề: "{topic}"

Đối tượng mục tiêu: {target}
Phong cách giọng điệu: {brand_tone}

Tuân thủ cấu trúc 5 phần bắt buộc:

[HOOK] — 5-10 giây đầu tiên — Dừng cuộn (Stop the scroll)
  - Pattern interrupt: Câu gây sốc, thống kê bất ngờ, hoặc câu hỏi đau
  - Preview payoff: "Trong video này tôi sẽ chỉ cho bạn..."
  - TUYỆT ĐỐI KHÔNG bắt đầu bằng "Xin chào các bạn..."

[INTRO] — 10-15 giây — Tại sao phải xem video này?
  - Credibility signal: Bạn là ai, tại sao bạn đủ tư cách nói về chủ đề này
  - Đặt vấn đề / câu hỏi chính

[VALUE DELIVERY] — 60-80% thời lượng — Nội dung chính
  - 3 điểm chính (số lẻ cảm giác đầy đủ hơn)
  - Mỗi điểm: Concept → Ví dụ → Ứng dụng
  - Gợi ý B-roll ở mỗi điểm chuyển cảnh

[RETENTION HOOK] — Giữ chân giữa video
  - "Trước khi đến tip số 3 (quan trọng nhất)..."
  - Mở một loop, đóng lại sau

[CTA] — 10-15 giây cuối — Một hành động duy nhất
  - Một CTA chính: Subscribe / Comment / Link
  - Mention video tiếp theo

Trả kết quả dưới dạng kịch bản thuần túy (chỉ có lời thoại), không cần giải thích thêm.
"""
    return prompt

HOOK_TEMPLATES = [
    "94% marketer nói rằng {topic} là quan trọng, nhưng chỉ 12% thực sự làm đúng.",
    "Tôi đã rank #1 cho {keyword} với 0 backlink. Đây là cách.",
    "Điều gì xảy ra nếu bạn có thể {benefit} mà không cần {pain}?",
    "3 tháng trước traffic của tôi giảm 70%. Đây là những gì tôi đã làm.",
    "Lời khuyên mà ai cũng đưa về {topic} hoàn toàn sai."
]
