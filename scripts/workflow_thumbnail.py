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

    # 1. Khởi tạo Agents
    try:
        from importlib import import_module
        llm_mod = import_module("4_BRAIN.llm_engine")
        thumb_mod = import_module("2_SKILLS.thumbnail_maker.thumbnail_generator")
    except Exception as e:
        print(f"Lỗi import modules: {e}")
        sys.exit(1)

    # Lấy variables từ NLP (Smart Router tự nhận diện prompt có chữ 'thumbnail')
    print("\n[1/3] Đang phân tích NLP để lấy Thumbnail Layout & Text...")
    prompt = f"Analyze this text to extract variables for a thumbnail layout_type.\n\n{title_hook}"
    try:
        thumb_data = llm_mod.generate_json_from_prompt("Bạn là Thumbnail Designer", prompt)
    except Exception as e:
        print(f"Lỗi lấy NLP Thumbnail: {e}")
        sys.exit(1)

    top_label = thumb_data.get("top_label", "VIDEO")
    main_title = thumb_data.get("main_title", title_hook)
    hook_str = thumb_data.get("hook", "")
    cta = thumb_data.get("cta", "XEM NGAY")

    # 2. Render Thumbnail 9:16
    print("\n[2/3] Đang thiết kế Thumbnail Dọc (9:16) cho Reels/Tiktok/Shorts...")
    try:
        path_9x16 = os.path.join(out_dir, f"Thumbnail_{brand.upper()}_9x16.png")
        thumb_mod.generate_html_thumbnail(
            output_path=path_9x16,
            top_label=top_label, main_title=main_title, hook=hook_str, cta=cta,
            aspect_ratio="9:16", brand=brand, layout_type="auto"
        )
    except Exception as e:
        print(f"Lỗi Render 9:16: {e}")

    # 3. Render Thumbnail 16:9 (3 layout variations)
    print("\n[3/3] Đang thiết kế Thumbnail Ngang (16:9) — 3 biến thể layout...")
    variations = []
    layouts = ["auto", "split", "center"]

    for i, layout in enumerate(layouts):
        path_var = os.path.join(out_dir, f"Thumbnail_var{i+1}.png")
        try:
            thumb_mod.generate_html_thumbnail(
                output_path=path_var,
                top_label=top_label, main_title=main_title, hook=hook_str, cta=cta,
                aspect_ratio="16:9", brand=brand, layout_type=layout
            )
            variations.append(path_var)
        except Exception as e:
            print(f"Lỗi Render biến thể {i+1}: {e}")

    # Pick the first (primary "auto") layout as the final 16:9. The AI A/B tester was
    # retired (lean profile); choose by hand from the variations if needed.
    if variations:
        import shutil
        final_path = os.path.join(out_dir, f"Thumbnail_{brand.upper()}_16x9.png")
        shutil.copy(variations[0], final_path)
        print(f"Bản chính 16:9: {final_path} (chọn tay từ {len(variations)} biến thể nếu cần)")

    sep("HOÀN TẤT QUY TRÌNH VIDEO PACKAGING")
    print(f"Hình ảnh đã được lưu tại thư mục: {out_dir}")

if __name__ == "__main__":
    main()
