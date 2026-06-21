"""Preview 3 Spatial Flow templates (Light Mode) with real SEOSONA data."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES = os.path.join(ROOT, "5_FRAMEWORK", "html_renderer", "templates")
OUT = os.path.join(ROOT, "8_WORKSPACE", "Spatial_Flow_Preview")
LOGO = "file:///" + os.path.join(ROOT, "7_ASSETS", "logos", "Seosona_Logo.png").replace("\\", "/")
os.makedirs(OUT, exist_ok=True)

def render(template_name, replacements, output_name):
    path = os.path.join(TEMPLATES, template_name)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    for k, v in replacements.items():
        html = html.replace(k, v)
    temp = os.path.join(OUT, f"_temp_{output_name}.html")
    with open(temp, "w", encoding="utf-8") as f:
        f.write(html)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
        page.goto(f"file:///{temp.replace(chr(92), '/')}", wait_until="networkidle")
        out_path = os.path.join(OUT, f"{output_name}.png")
        page.screenshot(path=out_path, type="png")
        browser.close()
    os.remove(temp)
    print(f"  -> {out_path}")

print("=== RENDERING SPATIAL FLOW (LIGHT MODE) ===\n")

# 1. Comparison
print("[1/3] spatial_comparison.html")
render("spatial_comparison.html", {
    "{{LOGO_PATH}}": LOGO,
    "{{TAG}}": "VẤN ĐỀ VS GIẢI PHÁP",
    "{{HEADING_1}}": "SEO Truyền Thống vs",
    "{{HEADING_HL}}": "AI-Powered SEO",
    "{{HEADING_2}}": "",
    "{{LEFT_BADGE}}": "CÁCH CŨ",
    "{{LEFT_TITLE}}": "SEO Thủ Công Truyền Thống",
    "{{LEFT_ITEM_1}}": "Nghiên cứu từ khóa bằng cảm tính",
    "{{LEFT_ITEM_2}}": "Viết content không có dữ liệu thực tế",
    "{{LEFT_ITEM_3}}": "Tối ưu on-page theo checklist cũ",
    "{{LEFT_STAT}}": "30%",
    "{{RIGHT_BADGE}}": "CÁCH MỚI",
    "{{RIGHT_TITLE}}": "AI Agent Tự Động Hóa",
    "{{RIGHT_ITEM_1}}": "Phân tích Search Intent bằng AI",
    "{{RIGHT_ITEM_2}}": "Content được tạo từ dữ liệu doanh nghiệp",
    "{{RIGHT_ITEM_3}}": "Tối ưu liên tục dựa trên phản hồi thực",
    "{{RIGHT_STAT}}": "85%",
}, "01_comparison")

# 2. Process (7 steps + highlight)
print("[2/3] spatial_process.html")
render("spatial_process.html", {
    "{{LOGO_PATH}}": LOGO,
    "{{TAG}}": "FRAMEWORK 7 BƯỚC",
    "{{HEADING_1}}": "Agent càng chạy",
    "{{HEADING_HL}}": "càng khôn.",
    "{{HEADING_2}}": "",
    "{{STEP_1_TITLE}}": "Xây luồng & chạy",
    "{{STEP_2_TITLE}}": "Đánh giá đầu ra",
    "{{STEP_3_TITLE}}": "Ghi lại case tốt & tệ",
    "{{STEP_4_TITLE}}": "Tìm điểm chung của các lỗi",
    "{{STEP_5_TITLE}}": "Cập nhật tiêu chí đánh giá",
    "{{STEP_6_TITLE}}": 'Cập nhật kiến thức theo quy tắc <span class="hl">80/20</span>',
    "{{STEP_7_TITLE}}": "Lưu lịch sử cập nhật của hệ thống",
    "{{HL_LABEL}}": "LẶP LẠI",
    "{{HL_TITLE}}": "Vòng lặp phản hồi",
}, "02_process")

# 3. Feature Grid
print("[3/3] spatial_feature_grid.html")
render("spatial_feature_grid.html", {
    "{{LOGO_PATH}}": LOGO,
    "{{TAG}}": "NĂNG LỰC CỐT LÕI",
    "{{HEADING_1}}": "4 Module Sức Mạnh Của",
    "{{HEADING_HL}}": "AI Agent",
    "{{HEADING_2}}": "",
    "{{FEAT_1_ICON}}": "🔍",
    "{{FEAT_1_TITLE}}": "Đọc & Phân Tích Sitemap",
    "{{FEAT_1_DESC}}": "Agent tự crawl toàn bộ cấu trúc website, phát hiện lỗi kỹ thuật và cơ hội tối ưu.",
    "{{FEAT_1_TAG}}": "TECHNICAL SEO",
    "{{FEAT_2_ICON}}": "⚡",
    "{{FEAT_2_TITLE}}": "Viết Content Tự Động",
    "{{FEAT_2_DESC}}": "Tạo bài viết chuẩn EEAT từ dữ liệu thực tế của doanh nghiệp, không phải template chung.",
    "{{FEAT_2_TAG}}": "CONTENT AI",
    "{{FEAT_3_ICON}}": "📊",
    "{{FEAT_3_TITLE}}": "Đo Lường & Tối Ưu",
    "{{FEAT_3_DESC}}": "Theo dõi ranking realtime, tự điều chỉnh chiến lược dựa trên dữ liệu Search Console.",
    "{{FEAT_3_TAG}}": "ANALYTICS",
    "{{FEAT_4_ICON}}": "🔄",
    "{{FEAT_4_TITLE}}": "Vòng Lặp Feedback",
    "{{FEAT_4_DESC}}": "AI tạo → Con người duyệt → AI học thêm. Chất lượng tăng dần theo thời gian.",
    "{{FEAT_4_TAG}}": "AUTOMATION",
}, "03_feature_grid")

print("\n=== DONE ===")
print(f"Output: {OUT}")
