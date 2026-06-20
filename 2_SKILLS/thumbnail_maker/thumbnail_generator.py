import os
import re
import urllib.parse
from playwright.sync_api import sync_playwright

BRAND_PALETTES = {
    "seosona": {
        "navy": "#1A2DB5",
        "blue": "#1565C0",
        "light_blue": "#BBDEFB",
        "yellow": "#FFD54F",
        "logo_path": "7_ASSETS/logos/Seosona_Logo.png",
        "watermark": "SEO"
    },
    "cqa": {
        "navy": "#1B3A8A",
        "blue": "#2B5EA7",
        "light_blue": "#BBDEFB",
        "yellow": "#FFD54F",
        "logo_path": "7_ASSETS/logos/CQA_Logo.png",
        "watermark": "CQA"
    }
}

def extract_keyword(text):
    """
    Simulate basic NLP to extract the most important keyword from a string.
    Returns (prefix, keyword, suffix).
    """
    words = text.split()
    if not words:
        return "", "", ""
        
    if len(words) <= 2:
        return "", " ".join(words), ""
        
    longest_word = max(words, key=len)
    idx = words.index(longest_word)
    
    prefix = " ".join(words[:idx])
    keyword = words[idx]
    suffix = " ".join(words[idx+1:])
    
    return prefix, keyword, suffix

def generate_html_thumbnail(output_path, top_label, main_title, hook, cta, portrait_path=None, manual_title=None, manual_cta=None, aspect_ratio="16:9", brand="seosona"):
    """
    Generates a thumbnail by rendering the HTML template using Playwright.
    Supports 16:9 (1920x1080) and 9:16 (1080x1920) aspect ratios.
    """
    print(f"Generating HTML-based Thumbnail ({aspect_ratio} | {brand})...")
    
    palette = BRAND_PALETTES.get(brand.lower(), BRAND_PALETTES["seosona"])
    
    if aspect_ratio == "16:9":
        template_name = 'seosona_thumbnail_16x9.html'
        width, height = 1920, 1080
    else:
        template_name = 'seosona_thumbnail_v1.html'
        width, height = 1080, 1920
        
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '5_FRAMEWORK', 'html_renderer', 'templates', template_name))
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', palette["logo_path"]))
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")
        
    # Format logo path for HTML src
    logo_uri = "file:///" + logo_path.replace("\\", "/")
    
    # NLP extraction
    if manual_title:
        title_1, title_kw, title_2 = manual_title
    else:
        title_1, title_kw, title_2 = extract_keyword(main_title)
    
    if manual_cta:
        cta_1, cta_kw, cta_2 = manual_cta
    else:
        cta_1, cta_kw, cta_2 = extract_keyword(cta)
    
    # Format portrait path
    if portrait_path and os.path.exists(portrait_path):
        portrait_uri = "file:///" + os.path.abspath(portrait_path).replace("\\", "/")
        text_align_class = ""
        portrait_style = ""
    else:
        portrait_uri = ""
        text_align_class = "center-align"
        portrait_style = "display: none;"

    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Replace variables
    html_content = html_content.replace('{{COLOR_NAVY}}', palette["navy"])
    html_content = html_content.replace('{{COLOR_BLUE}}', palette["blue"])
    html_content = html_content.replace('{{COLOR_LIGHT_BLUE}}', palette["light_blue"])
    html_content = html_content.replace('{{COLOR_YELLOW}}', palette["yellow"])
    
    html_content = html_content.replace('{{TEXT_ALIGN_CLASS}}', text_align_class)
    html_content = html_content.replace('{{PORTRAIT_STYLE}}', portrait_style)
    
    html_content = html_content.replace('{{LOGO_PATH}}', logo_uri)
    html_content = html_content.replace('{{PORTRAIT_PATH}}', portrait_uri)
    html_content = html_content.replace('{{WATERMARK}}', palette["watermark"])
    html_content = html_content.replace('{{TOP_LABEL}}', top_label)
    html_content = html_content.replace('{{MAIN_TITLE_1}}', title_1)
    html_content = html_content.replace('{{MAIN_TITLE_KW}}', title_kw)
    html_content = html_content.replace('{{MAIN_TITLE_2}}', title_2)
    html_content = html_content.replace('{{HOOK}}', hook)
    html_content = html_content.replace('{{CTA_1}}', cta_1)
    html_content = html_content.replace('{{CTA_KW}}', cta_kw)
    html_content = html_content.replace('{{CTA_2}}', cta_2)
    
    # We save a temporary filled html file to render
    temp_html_path = output_path + ".temp.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    # Render with playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        
        file_uri = "file:///" + os.path.abspath(temp_html_path).replace("\\", "/")
        page.goto(file_uri)
        page.wait_for_load_state("networkidle")
        
        # Take screenshot of exact area
        page.screenshot(
            path=output_path,
            clip={'x': 0, 'y': 0, 'width': width, 'height': height}
        )
        
        browser.close()
        
    # Cleanup temp
    try:
        os.remove(temp_html_path)
    except:
        pass
        
    print(f"Thumbnail successfully saved to {output_path}")
    return output_path

if __name__ == "__main__":
    # Quick Test SEOSONA 9:16 (With Portrait)
    generate_html_thumbnail(
        "Thumbnail_Test_SEOSONA_9x16.png",
        top_label="BÍ MẬT TRAFFIC 2026",
        main_title="CÚ ĐẢO NGƯỢC THUẬT TOÁN GOOGLE",
        hook="", # Hidden in HTML anyway
        cta="GIẢI MÃ BÍ MẬT NGAY",
        portrait_path=r"D:\SEOSONA Video\PTP_8811_nobg.png",
        manual_title=("CÚ ĐẢO NGƯỢC", "THUẬT TOÁN", "GOOGLE"),
        manual_cta=("GIẢI MÃ", "BÍ MẬT", "NGAY"),
        aspect_ratio="9:16",
        brand="seosona"
    )
    
    # Quick Test CQA 16:9 (Text Only - No Portrait)
    generate_html_thumbnail(
        "Thumbnail_Test_CQA_16x9_NoPortrait.png",
        top_label="HƯỚNG DẪN CHI TIẾT",
        main_title="XÂY DỰNG HỆ THỐNG MARKETING TỰ ĐỘNG",
        hook="", 
        cta="XEM NGAY BÍ KÍP",
        portrait_path=None,
        manual_title=("XÂY DỰNG HỆ THỐNG", "MARKETING", "TỰ ĐỘNG"),
        manual_cta=("XEM NGAY", "BÍ KÍP", ""),
        aspect_ratio="16:9",
        brand="cqa"
    )
