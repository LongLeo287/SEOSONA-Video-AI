"""
WORKFLOW: VIDEO PACKAGING PIPELINE (THUMBNAIL)
================================================
Quy trình chuyên biệt thiết kế hình ảnh Thumbnail (16:9 & 9:16) để bọc gói
Video trước khi upload lên YouTube, TikTok, Facebook, Shorts.

Đầu vào (Input): Tiêu đề (Title), Hook ngắn, hoặc Concept Video.
Đầu ra (Output): Ảnh Thumbnail 16:9 và 9:16.

Usage:
    python scripts/workflow_thumbnail.py "Tiêu đề hoặc Concept Video"
"""
import os
import sys
import time
import io
from importlib import import_module

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ---- Paths Setup ----
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

WORKSPACE = os.path.join(ROOT, "8_WORKSPACE", "Video_Thumbnails")

def sep(title): print(f"\n{'='*60}\n  {title}\n{'='*60}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/workflow_thumbnail.py <Title_or_Hook_string>")
        sys.exit(1)

    title_hook = " ".join(sys.argv[1:])
    if len(title_hook.strip()) < 5:
        print("Lỗi: Tiêu đề hoặc Hook quá ngắn.")
        sys.exit(1)

    # Xác định Brand (Mặc định SEOSONA, nếu có nhắc đến cqa thì chọn CQA)
    brand = "cqa" if "cqa" in title_hook.lower() else "seosona"

    # Tạo thư mục Output chuyên biệt cho Video Thumbnail
    timestamp = int(time.time())
    # Lấy 3 chữ đầu của title làm tên thư mục cho dễ nhớ
    safe_title = "_".join(title_hook.split()[:3]).replace(":", "").replace("?", "").replace("/", "")
    out_dir = os.path.join(WORKSPACE, f"{brand.upper()}_{safe_title}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    sep(f"VIDEO PACKAGING PIPELINE — BRAND: {brand.upper()}")
    print(f"Concept/Tiêu đề Input: '{title_hook}'")

    # Single entry point: content → NLP (key-normalized) → highlight tuples → branded PNG.
    try:
        from importlib import import_module
        tm = import_module("2_SKILLS.thumbnail_maker.thumbnail_maker")
    except Exception as e:
        print(f"Lỗi import thumbnail_maker: {e}")
        sys.exit(1)

    # 1. Render Thumbnail 9:16 (Reels / TikTok / Shorts)
    print("\n[1/2] Đang thiết kế Thumbnail Dọc (9:16) cho Reels/Tiktok/Shorts...")
    path_9x16 = os.path.join(out_dir, f"Thumbnail_{brand.upper()}_9x16.png")
    try:
        tm.make_thumbnail(title_hook, path_9x16, aspect_ratio="9:16", brand=brand)
    except Exception as e:
        print(f"Lỗi Render 9:16: {e}")

    # 2. Render Thumbnail 16:9 (YouTube / Facebook)
    print("\n[2/2] Đang thiết kế Thumbnail Ngang (16:9) cho YouTube/Facebook...")
    path_16x9 = os.path.join(out_dir, f"Thumbnail_{brand.upper()}_16x9.png")
    try:
        tm.make_thumbnail(title_hook, path_16x9, aspect_ratio="16:9", brand=brand)
    except Exception as e:
        print(f"Lỗi Render 16:9: {e}")

    sep("HOÀN TẤT QUY TRÌNH VIDEO PACKAGING")
    print(f"Hình ảnh đã được lưu tại thư mục: {out_dir}")

if __name__ == "__main__":
    main()
