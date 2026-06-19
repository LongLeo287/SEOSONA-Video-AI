"""
SEO Optimizer Agent — Generates YouTube-optimized metadata.
Inherits knowledge from SEOSONA OS Skill: seo_marketing/video_content and Website SEOSONA.
"""
import json
from datetime import datetime

def generate_youtube_metadata(hook_text, keywords, brand_profile, video_duration=60):
    """
    Generates Title, Description, Tags, Hashtags, and JSON-LD for YouTube upload.
    Based on SEOSONA OS video_content SKILL.md and SEO Specialist persona.
    """
    brand_tone = brand_profile.get('brand_tone', 'Chuyên gia, đáng tin cậy')
    target = brand_profile.get('target_audience', 'Người làm SEO, Marketing')
    
    # 1. Expand LSI Keywords (Simulated)
    lsi_keywords = keywords.copy()
    if "SEO" in [k.upper() for k in keywords]:
        lsi_keywords.extend(["Tối ưu công cụ tìm kiếm", "Website chuẩn SEO", "Digital Marketing"])
    
    # 2. Title: [Primary Keyword] — [Benefit/Outcome] ([Year])
    # Tối ưu CTR theo chuẩn OS
    primary_kw = keywords[0] if keywords else "Marketing"
    title = f"{primary_kw.title()} | Hướng Dẫn Tối Ưu Toàn Diện ({datetime.now().year})"
    if len(title) > 65:
        title = title[:62] + "..."

    # 3. Description (chuẩn AIDA & Timestamps)
    description = f"""🔥 {hook_text}

Video này phân tích chuyên sâu về {', '.join(keywords[:3])} dành riêng cho {target}. 
Giải pháp thực tế, bám sát thuật toán mới nhất giúp bạn tăng trưởng traffic bền vững.

📌 TIMESTAMPS (CHƯƠNG VIDEO)
00:00 — Giới thiệu & Vấn đề cốt lõi
{f"00:{int(video_duration*0.3):02d}"} — Phân tích kỹ thuật chuyên sâu
{f"00:{int(video_duration*0.6):02d}"} — Ứng dụng & Case Study
{f"00:{int(video_duration*0.9):02d}"} — Tổng kết & Giải pháp

🔗 TÀI NGUYÊN HỮU ÍCH
- Website chính thức: https://seosona.com
- Đăng ký tư vấn: https://seosona.com/lien-he

🔔 SUBSCRIBE kênh để không bỏ lỡ các kiến thức chuyên ngành mới nhất!

{' '.join([f"#{kw.replace(' ', '')}" for kw in keywords[:5]])}
"""

    # 4. Tags (Phân bổ theo đối thủ & biến thể)
    tags = list(set(keywords + lsi_keywords))[:15]

    # 5. Hashtags (Tối đa 3 cho Title)
    hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords[:3]]
    
    # 6. JSON-LD (VideoObject Schema) cho website nhúng
    schema_markup = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": title,
        "description": hook_text,
        "thumbnailUrl": [
            "https://seosona.com/assets/default-video-thumbnail.jpg"
        ],
        "uploadDate": datetime.now().isoformat(),
        "duration": f"PT{int(video_duration)}S",
        "publisher": {
            "@type": "Organization",
            "name": "SEOSONA",
            "logo": {
                "@type": "ImageObject",
                "url": "https://seosona.com/logo.png"
            }
        }
    }

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "hashtags": hashtags,
        "json_ld": json.dumps(schema_markup, ensure_ascii=False, indent=2)
    }

def generate_tiktok_metadata(hook_text, keywords):
    """
    Generates caption + hashtags for TikTok/Reels/Shorts.
    """
    hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords[:5]]
    hashtags += ["#seosona", "#seo", "#digitalmarketing", "#tips"]

    # Áp dụng Hook trực tiếp vào caption
    caption = f"🚨 {hook_text}\n\n👉 Click link ở Bio để tìm hiểu thêm!\n\n{' '.join(hashtags)}"
    if len(caption) > 150:
        caption = caption[:147] + "..."

    return {"caption": caption, "hashtags": hashtags}
