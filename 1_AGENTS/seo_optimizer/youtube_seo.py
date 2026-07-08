"""
SEO Optimizer Agent — Generates YouTube-optimized metadata.
Inherits knowledge from SEOSONA OS Skill: seo_marketing/video_content and Website SEOSONA.
"""
import json
from datetime import datetime


def _smart_title(s):
    """Title-case for display while PRESERVING acronym/brand casing. Python's str.title() downcases
    acronyms — 'SEO' → 'Seo', 'AI' → 'Ai' — which mangles the exact-match primary keyword in the public
    title. Only all-lowercase words are capitalised; anything already carrying an uppercase letter
    (SEO, ChatGPT, iPhone) is left untouched."""
    return " ".join(w if any(c.isupper() for c in w) else w.capitalize() for w in str(s).split())


def _mmss(seconds):
    """Format seconds as MM:SS for YouTube chapter markers. A plain `00:{seconds}` breaks for any
    video ≥ 60s (e.g. '00:72'), and YouTube then rejects the whole chapter list — carry the minutes."""
    s = max(0, int(seconds))
    return f"{s // 60:02d}:{s % 60:02d}"


def generate_youtube_metadata(hook_text, keywords, brand_profile, video_duration=60):
    """
    Generates Title, Description, Tags, Hashtags, and JSON-LD for YouTube upload.
    Based on SEOSONA OS video_content SKILL.md and SEO Specialist persona.
    """
    brand_tone = brand_profile.get('brand_tone', 'Chuyên gia, đáng tin cậy')
    target = brand_profile.get('target_audience', 'Người làm SEO, Marketing')
    
    # 1. Expand LSI keywords — deterministic offline heuristic (NOT an LLM call)
    lsi_keywords = keywords.copy()
    if "SEO" in [k.upper() for k in keywords]:
        lsi_keywords.extend(["Tối ưu công cụ tìm kiếm", "Website chuẩn SEO", "Digital Marketing"])
    
    # 2. Title: [Primary Keyword] — [Benefit/Outcome] ([Year])
    # Tối ưu CTR theo chuẩn OS
    primary_kw = keywords[0] if keywords else "Marketing"
    title = f"{_smart_title(primary_kw)} | Hướng Dẫn Tối Ưu Toàn Diện ({datetime.now().year})"
    if len(title) > 65:
        title = title[:62] + "..."

    # 3. Description (chuẩn AIDA & Timestamps)
    description = f"""🔥 {hook_text}

Video này phân tích chuyên sâu về {', '.join(keywords[:3])} dành riêng cho {target}. 
Giải pháp thực tế, bám sát thuật toán mới nhất giúp bạn tăng trưởng traffic bền vững.

📌 TIMESTAMPS (CHƯƠNG VIDEO)
00:00 — Giới thiệu & Vấn đề cốt lõi
{_mmss(video_duration*0.3)} — Phân tích kỹ thuật chuyên sâu
{_mmss(video_duration*0.6)} — Ứng dụng & Case Study
{_mmss(video_duration*0.9)} — Tổng kết & Giải pháp

🔗 TÀI NGUYÊN HỮU ÍCH
- Website chính thức: https://seosona.com
- Đăng ký tư vấn: https://seosona.com/lien-he

🔔 SUBSCRIBE kênh để không bỏ lỡ các kiến thức chuyên ngành mới nhất!

{' '.join([f"#{kw.replace(' ', '')}" for kw in keywords[:5]])}
"""

    # 4. Tags (Phân bổ theo đối thủ & biến thể)
    # Order-preserving, case-insensitive dedupe — PRIMARY keywords first. A plain list(set(...)) reorders by
    # hash, so the primary keyword could be buried past the 15-tag cap or dropped entirely; YouTube weights
    # earlier tags, so order matters for discovery.
    seen, tags = set(), []
    for kw in keywords + lsi_keywords:
        k = (kw or "").strip()
        if k and k.lower() not in seen:
            seen.add(k.lower())
            tags.append(k)
    tags = tags[:15]

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

    # Áp dụng Hook trực tiếp vào caption. Truncate only the HOOK, never the tail — the OLD code capped the
    # WHOLE caption (and at a wrong 150 vs TikTok's ~2200), which sliced the hashtags off the end and killed
    # discovery. Reserve room for the CTA + hashtags so they always survive.
    tail = f"\n\n👉 Click link ở Bio để tìm hiểu thêm!\n\n{' '.join(hashtags)}"
    max_len = 2200                                    # TikTok / Reels caption limit
    hook = hook_text.strip()
    room = max_len - len(tail) - 2                    # 2 = "🚨 " prefix
    if len(hook) > room:
        hook = hook[:max(0, room - 3)].rstrip() + "..."
    caption = f"🚨 {hook}{tail}"

    return {"caption": caption, "hashtags": hashtags}
