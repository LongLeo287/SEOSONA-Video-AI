"""
WORKFLOW: SOCIAL CAMPAIGN PIPELINE
===================================
Quy trình chuyên biệt xử lý bài viết (Text/Markdown/URL) thành các ấn phẩm
mạng xã hội (Social Media Post & Carousel).

Đầu vào (Input): Text thô, File txt, bài viết Blog.
Đầu ra (Output): Carousel PNGs + Caption chuẩn PAS.

Usage:
    python scripts/workflow_social_post.py "Nội dung bài viết hoặc đường dẫn file .txt"
"""
import os
import sys
import json
import time
import io
from importlib import import_module

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ---- Paths Setup ----
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

ASSETS    = os.path.join(ROOT, "7_ASSETS")
LOGO_SEO  = os.path.join(ASSETS, "logos", "Seosona_Logo.png")
LOGO_CQA  = os.path.join(ASSETS, "logos", "Chi Quyet Academy Mascot Logo.png")
WORKSPACE = os.path.join(ROOT, "8_WORKSPACE", "Social_Campaigns")

def sep(title): print(f"\n{'='*60}\n  {title}\n{'='*60}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/workflow_social_post.py <text_or_file_path>")
        sys.exit(1)

    input_arg = " ".join(sys.argv[1:])

    # Đọc input (nếu là file thì đọc nội dung, nếu là text thì giữ nguyên)
    if os.path.isfile(input_arg):
        with open(input_arg, "r", encoding="utf-8") as f:
            raw_content = f.read()
        print(f"[Workflow] Đã nạp nội dung từ file: {input_arg}")
    else:
        raw_content = input_arg
        print(f"[Workflow] Đã nạp nội dung Text trực tiếp.")

    if len(raw_content.strip()) < 20:
        print("Lỗi: Nội dung đầu vào quá ngắn. Vui lòng cung cấp bài viết đầy đủ.")
        sys.exit(1)

    # Xác định Brand (Mặc định SEOSONA, nếu có nhắc đến cqa thì chọn CQA)
    brand = "cqa" if "cqa" in raw_content.lower() else "seosona"
    logo = LOGO_CQA if brand == "cqa" else LOGO_SEO

    # Tạo thư mục Output chuyên biệt cho Social Campaign
    timestamp = int(time.time())
    out_dir = os.path.join(WORKSPACE, f"Campaign_{brand.upper()}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    sep(f"SOCIAL CAMPAIGN PIPELINE — BRAND: {brand.upper()}")

    # 1. Khởi tạo Agents
    try:
        carousel_agent_mod = import_module("1_AGENTS.carousel_writer_agent.writer")
        writer = carousel_agent_mod.CarouselWriterAgent()

        social_mod = import_module("1_AGENTS.social_media_agent.writer")
        social_agent = social_mod.SocialMediaAgent()
    except Exception as e:
        print(f"Lỗi khởi tạo Agents: {e}")
        sys.exit(1)

    # 2. Sinh nội dung Carousel (Kế hoạch JSON)
    print("[1/3] Generating Carousel JSON Plan...")
    slide_data = writer.generate_slides(raw_content)
    plan_file = os.path.join(out_dir, "carousel_plan.json")
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(slide_data, f, ensure_ascii=False, indent=2)
    print(f"  -> Đã lưu kế hoạch Carousel: {plan_file}")

    # 3. Viết Caption chuẩn PAS
    print("\n[2/3] Writing Facebook Caption (PAS Framework)...")
    caption = social_agent.write_facebook_caption(raw_content, brand=brand)
    caption_file = os.path.join(out_dir, "facebook_caption.md")
    with open(caption_file, "w", encoding="utf-8") as f:
        f.write(f"# Facebook Caption — {brand.upper()}\n\n")
        f.write(caption)
    print(f"  -> Đã lưu bài viết Caption: {caption_file}")

    # 4. Render Layout ra PNG
    print("\n[3/3] Rendering Carousel Slides via Playwright...")
    try:
        carousel_maker = import_module("2_SKILLS.carousel_maker.carousel_generator")
        carousel_maker.generate_carousel_slides(
            slide_data, out_dir, logo_path=logo, brand=brand
        )
        pngs = sorted([f for f in os.listdir(out_dir) if f.endswith(".png")])
        print(f"  -> Đã Render thành công {len(pngs)} slides ảnh PNG.")
    except Exception as e:
        print(f"Lỗi Render Carousel: {e}")
        import traceback; traceback.print_exc()

    sep("HOÀN TẤT QUY TRÌNH SOCIAL CAMPAIGN")
    print(f"Đầu ra đã được lưu tại: {out_dir}")

if __name__ == "__main__":
    main()
