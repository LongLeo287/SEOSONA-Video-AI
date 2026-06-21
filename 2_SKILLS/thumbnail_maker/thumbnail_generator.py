import os
import urllib.parse
from playwright.sync_api import sync_playwright

BRAND_PALETTES = {
    "seosona": {
        "navy": "#1A2DB5",
        "blue": "#1565C0",
        "light_blue": "#BBDEFB",
        "yellow": "#FFD54F",
        "logo_path": "7_ASSETS/logos/Seosona_Logo.png",
        "watermark": "SEO",
        "brand_name": "SEOSONA",
        "brand_tagline": "Share to be shared more",
        "brand_tagline_upper": "SHARE TO BE SHARED MORE"
    },
    "cqa": {
        "navy": "#1B3A8A",
        "blue": "#2B5EA7",
        "light_blue": "#BBDEFB",
        "yellow": "#FFD54F",
        "logo_path": "7_ASSETS/logos/CQA_Logo.png",
        "watermark": "CQA",
        "brand_name": "CHÍ QUYẾT ACADEMY",
        "brand_tagline": "",
        "brand_tagline_upper": ""
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

def generate_html_thumbnail(
    output_path,
    top_label,
    main_title,
    hook,
    cta,
    portrait_path=None,
    manual_title=None,
    manual_cta=None,
    aspect_ratio="9:16",
    brand="seosona",
    subtext_italic="",
    layout_type="auto"
):
    """
    Generates a thumbnail by rendering the HTML template using Playwright.
    
    Args:
        output_path: Output PNG file path.
        top_label: Pill label text (e.g., "CHIẾN LƯỢC SEO 2026").
        main_title: Full title text for auto keyword extraction.
        hook: Short hook text (currently unused in template).
        cta: CTA text for auto keyword extraction.
        portrait_path: Path to cutout portrait image (None for text-only).
        manual_title: Tuple (prefix, keyword, suffix) to override auto extraction.
        manual_cta: Tuple (prefix, keyword, suffix) to override auto extraction.
        aspect_ratio: "16:9" or "9:16".
        brand: "seosona" or "cqa".
        subtext_italic: Italic philosophical text below portrait.
        layout_type: "auto", "portrait", "text_only", or "card".
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

    # Format logo path
    if os.path.exists(logo_path):
        logo_uri = "file:///" + logo_path.replace("\\", "/")
    else:
        logo_uri = ""

    # Extract title parts
    if manual_title:
        title_1, title_kw, title_2 = manual_title
    else:
        title_1, title_kw, title_2 = extract_keyword(main_title)

    # Extract CTA parts
    if manual_cta:
        cta_1, cta_kw, cta_2 = manual_cta
    else:
        cta_1, cta_kw, cta_2 = extract_keyword(cta)
    
    # Determine layout type
    if layout_type == "auto":
        if portrait_path and os.path.exists(portrait_path):
            layout_type = "portrait"
        else:
            layout_type = "text_only"
    
    # Format portrait path
    if layout_type == "portrait" and portrait_path and os.path.exists(portrait_path):
        portrait_uri = "file:///" + os.path.abspath(portrait_path).replace("\\", "/")
        portrait_style = ""
        text_align_class = ""
        title_class = ""
    elif layout_type == "card":
        portrait_uri = ""
        portrait_style = "display: none;"
        text_align_class = ""
        title_class = ""
    else:  # text_only
        portrait_uri = ""
        portrait_style = "display: none;"
        text_align_class = "center-full"
        title_class = "center-full"

    # Subtext
    subtext_style = "" if subtext_italic else "display: none;"
    
    # Card content (for flowchart/mockup layout)
    card_style = "display: none;"
    card_content = ""

    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Replace brand colors
    html_content = html_content.replace('{{COLOR_NAVY}}', palette["navy"])
    html_content = html_content.replace('{{COLOR_BLUE}}', palette["blue"])
    html_content = html_content.replace('{{COLOR_LIGHT_BLUE}}', palette["light_blue"])
    html_content = html_content.replace('{{COLOR_YELLOW}}', palette["yellow"])
    
    # Replace layout classes
    html_content = html_content.replace('{{TEXT_ALIGN_CLASS}}', text_align_class)
    html_content = html_content.replace('{{TITLE_CLASS}}', title_class)
    html_content = html_content.replace('{{PORTRAIT_STYLE}}', portrait_style)
    html_content = html_content.replace('{{SUBTEXT_STYLE}}', subtext_style)
    html_content = html_content.replace('{{CARD_STYLE}}', card_style)
    html_content = html_content.replace('{{CARD_CONTENT}}', card_content)
    
    # Replace content
    html_content = html_content.replace('{{LOGO_PATH}}', logo_uri)
    html_content = html_content.replace('{{PORTRAIT_PATH}}', portrait_uri)
    html_content = html_content.replace('{{WATERMARK}}', palette["watermark"])
    html_content = html_content.replace('{{BRAND_NAME}}', palette["brand_name"])
    html_content = html_content.replace('{{BRAND_TAGLINE}}', palette["brand_tagline"])
    html_content = html_content.replace('{{BRAND_TAGLINE_UPPER}}', palette["brand_tagline_upper"])
    html_content = html_content.replace('{{TOP_LABEL}}', top_label)
    html_content = html_content.replace('{{MAIN_TITLE_1}}', title_1)
    html_content = html_content.replace('{{MAIN_TITLE_KW}}', title_kw)
    html_content = html_content.replace('{{MAIN_TITLE_2}}', title_2)
    html_content = html_content.replace('{{CTA_1}}', cta_1)
    html_content = html_content.replace('{{CTA_KW}}', cta_kw)
    html_content = html_content.replace('{{CTA_2}}', cta_2)
    html_content = html_content.replace('{{SUBTEXT_ITALIC}}', subtext_italic)
    html_content = html_content.replace('{{HOOK}}', hook)

    # Write temp HTML
    temp_html = os.path.join(os.path.dirname(output_path), "_temp_thumbnail.html")
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Render with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto(f"file:///{temp_html.replace(chr(92), '/')}", wait_until="networkidle")
        page.screenshot(path=output_path, type="png")
        browser.close()

    # Cleanup temp
    if os.path.exists(temp_html):
        os.remove(temp_html)

    print(f"Thumbnail successfully saved to {output_path}")
    return output_path

if __name__ == "__main__":
    # Test 1: SEOSONA 9:16 with Portrait
    generate_html_thumbnail(
        "Thumbnail_Test_SEOSONA_9x16.png",
        top_label="CHIẾN LƯỢC SEO 2026",
        main_title="ĐẶT CƯỢC VÀO AI AGENT",
        hook="",
        cta="XEM 6 BƯỚC NÂNG CẤP MODEL",
        portrait_path=None,
        manual_title=("ĐẶT CƯỢC VÀO", "AI AGENT", ""),
        manual_cta=("XEM", "6 BƯỚC", "NÂNG CẤP MODEL"),
        aspect_ratio="9:16",
        brand="seosona",
        subtext_italic="Dùng AI để tăng hiệu suất, không phải để rảnh hơn"
    )
    
    # Test 2: CQA 16:9, Text Only
    generate_html_thumbnail(
        "Thumbnail_Test_CQA_16x9_TextOnly.png",
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
    
    # Test 3: SEOSONA 9:16, Text Only
    generate_html_thumbnail(
        "Thumbnail_Test_SEOSONA_9x16_TextOnly.png",
        top_label="SEO 2026",
        main_title="TẠI SAO TÔI ĐẶT CƯỢC SEO VÀO AI AGENT",
        hook="",
        cta="NHÌN CÁCH TẬP ĐOÀN LỚN TRIỂN KHAI",
        portrait_path=None,
        manual_title=("TẠI SAO TÔI ĐẶT CƯỢC SEO VÀO", "AI AGENT", ""),
        manual_cta=("NHÌN CÁCH", "TẬP ĐOÀN LỚN", "TRIỂN KHAI"),
        aspect_ratio="9:16",
        brand="seosona",
        subtext_italic="AI không để rảnh hơn — mà để tối ưu hiệu suất"
    )
