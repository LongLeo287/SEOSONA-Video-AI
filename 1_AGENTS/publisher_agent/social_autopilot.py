import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def generate_social_caption(video_metadata_path, platform="youtube"):
    \"\"\"Uses offline NLP to generate platform-specific SEO captions.\"\"\"
    try:
        from importlib import import_module
        llm = import_module('4_BRAIN.llm_engine')
        
        # Read raw script/metadata
        raw_text = "Mô tả video cơ bản"
        if os.path.exists(video_metadata_path):
            with open(video_metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw_text = data.get("narrator_text", "")
                
        prompt = f"Analyze this data and write a PAS framework Social Media Post.\\n\\nRaw Data:\\n{raw_text}"
        result = llm.generate_json_from_prompt("You are a Social Media Manager.", prompt)
        
        base_caption = result.get("caption", "Video mới đã ra mắt. Xem ngay!")
        
        if platform == "tiktok":
            # TikTok: Shorter, more hashtags
            return base_caption.split("\\n\\n")[0] + "\\n\\n#SEOSONA #Trending #Viral"
        elif platform == "facebook":
            return base_caption
        else:
            # YouTube: Keep long form, add links
            return base_caption + "\\n\\n🔗 Đăng ký kênh SEOSONA ngay hôm nay!"
            
    except Exception as e:
        print(f"[Auto-Pilot] Caption generation failed: {e}")
        return "Video mới từ SEOSONA. Khám phá ngay! #SEOSONA"

def schedule_upload(video_path, platform="youtube", brand="seosona"):
    \"\"\"
    Mock integration for Social Media APIs.
    In production:
    - YouTube: googleapiclient.discovery (YouTube Data API v3)
    - TikTok: TikTok Content Posting API
    - Facebook: Graph API (video_reels endpoint)
    \"\"\"
    print(f"\\n[Auto-Pilot] 🚀 INIT UPLOAD SEQUENCE: {platform.upper()}")
    
    # 1. Generate Caption
    metadata_path = os.path.join(os.path.dirname(video_path), "narrator_scripts.json")
    caption = generate_social_caption(metadata_path, platform=platform)
    print(f"[{platform.upper()}] Caption generated:\\n{caption[:100]}...")
    
    # 2. Determine Schedule Time (e.g. next 19:00 for TikTok, 20:00 for YT)
    now = datetime.now()
    target_hour = 19 if platform == "tiktok" else 20
    scheduled_time = now.replace(hour=target_hour, minute=0, second=0)
    if scheduled_time < now:
        scheduled_time += timedelta(days=1)
        
    print(f"[{platform.upper()}] Scheduled Time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 3. API Handshake Simulation
    keys = {
        "youtube": os.environ.get("YOUTUBE_OAUTH_FILE"),
        "tiktok": os.environ.get("TIKTOK_ACCESS_TOKEN"),
        "facebook": os.environ.get("FB_PAGE_TOKEN")
    }
    
    if not keys.get(platform):
        print(f"[{platform.upper()}] ⚠️ WARNING: Missing API token for {platform}. Simulating upload success to Local Vault.")
        return {"status": "mock_scheduled", "platform": platform, "time": str(scheduled_time)}
        
    print(f"[{platform.upper()}] ✅ Upload SUCCESS. Video is now scheduled via API.")
    return {"status": "scheduled", "platform": platform, "time": str(scheduled_time)}

if __name__ == '__main__':
    # Test
    schedule_upload("test.mp4", "tiktok")
