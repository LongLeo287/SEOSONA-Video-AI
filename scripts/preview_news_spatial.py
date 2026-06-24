"""Preview 4 scenes of the Spatial Flow News template — force visible."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "5_FRAMEWORK" / "html_renderer" / "templates" / "seosona_spatial_flow_news.html"
OUT = ROOT / "8_WORKSPACE" / "Spatial_Flow_News_Preview"
LOGO = (ROOT / "7_ASSETS" / "brand" / "logos" / "Seosona_Logo.png").as_uri()
os.makedirs(OUT, exist_ok=True)

with open(TEMPLATE, "r", encoding="utf-8") as f:
    html_base = f.read()

replacements = {
    "{{LOGO_PATH}}": LOGO,
    "{{DURATION}}": "60",
    "{{WATERMARK}}": "01",
    "{{TOTAL_POINTS}}": "04",
    "{{SUBTITLE}}": "",
    "{{S1_TAG}}": "BẢN TIN SEOSONA",
    "{{S1_HEADING}}": "AI Search đang đổi",
    "{{S1_HL}}": "luật chơi SEO",
    "{{S1_SUB}}": "Tự vận hành · Tự kiểm tra · Tự sửa sai",
    "{{S2_TAG}}": "TÍN HIỆU XẾP HẠNG",
    "{{S2_HEADING}}": "Entity Authority",
    "{{S2_HL}}": "quyết định tất cả",
    "{{S2_STAT1_VAL}}": "84",
    "{{S2_STAT1_LBL}}": "ENTITY",
    "{{S2_STAT2_VAL}}": "72",
    "{{S2_STAT2_LBL}}": "CITATION",
    "{{S2_STAT3_VAL}}": "91",
    "{{S2_STAT3_LBL}}": "TRUST",
    "{{S3_TAG}}": "KẾT LUẬN",
    "{{S3_HEADING}}": "AI-First SEO",
    "{{S3_SUB}}": "Kiên trì đi đến tận cùng mục tiêu",
    "{{S4_TAG}}": "NĂNG LỰC CỐT LÕI",
    "{{S4_HEADING}}": "Biết khi nào",
    "{{S4_HL}}": "đã đủ",
    "{{S4_F1}}": "Definition of Done",
    "{{S4_F2}}": "Context Window",
    "{{S4_F3}}": "Error Handling",
    "{{S4_F4}}": "Termination Logic",
}

html = html_base
for k, v in replacements.items():
    html = html.replace(k, v)

# Remove the entire <script> block so GSAP doesn't hide scenes
import re
html_no_script = re.sub(r'<script>.*?</script>', '', html, flags=re.DOTALL)

scenes = [
    ("scene_1_headline", "scene-1"),
    ("scene_2_stats",    "scene-2"),
    ("scene_3_conclusion","scene-3"),
    ("scene_4_features", "scene-4"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    for name, scene_id in scenes:
        # Set the target scene opacity=1, others opacity=0
        modified = html_no_script.replace(
            f'id="{scene_id}" class="scene"',
            f'id="{scene_id}" class="scene" style="opacity:1"'
        )

        temp = os.path.join(OUT, f"_temp_{name}.html")
        with open(temp, "w", encoding="utf-8") as f:
            f.write(modified)

        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page.goto(f"file:///{temp.replace(chr(92), '/')}", wait_until="networkidle")
        page.wait_for_timeout(300)

        out_path = os.path.join(OUT, f"{name}.png")
        page.screenshot(path=out_path, type="png")
        page.close()
        os.remove(temp)
        print(f"  [{name}] -> {out_path}")

    browser.close()

print(f"\nDone! Output: {OUT}")
