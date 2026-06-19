import os
import re
import urllib.parse
from playwright.sync_api import sync_playwright

def extract_keyword(text):
    """
    Simulate basic NLP to extract the most important keyword from a string.
    Returns (prefix, keyword, suffix).
    """
    words = text.split()
    if not words:
        return "", "", ""
        
    # Just take the last 1-2 words as the keyword for simplicity, 
    # or the longest word. Let's just highlight the longest word if no explicit marker.
    if len(words) <= 2:
        return "", " ".join(words), ""
        
    # Find longest word to be the keyword
    longest_word = max(words, key=len)
    idx = words.index(longest_word)
    
    prefix = " ".join(words[:idx])
    keyword = words[idx]
    suffix = " ".join(words[idx+1:])
    
    return prefix, keyword, suffix

def generate_html_thumbnail(output_path, top_label, main_title, hook, cta, portrait_path=None, watermark="SEO", manual_title=None, manual_cta=None):
    """
    Generates a 1080x1920 thumbnail by rendering the HTML template using Playwright.
    """
    print("Generating HTML-based Thumbnail...")
    
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '5_FRAMEWORK', 'html_renderer', 'templates', 'seosona_thumbnail_v1.html'))
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '7_ASSETS', 'logos', 'Seosona_Logo.png'))
    
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
    else:
        portrait_uri = ""

    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Replace variables
    html_content = html_content.replace('{{LOGO_PATH}}', logo_uri)
    html_content = html_content.replace('{{PORTRAIT_PATH}}', portrait_uri)
    html_content = html_content.replace('{{WATERMARK}}', watermark)
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
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        
        file_uri = "file:///" + os.path.abspath(temp_html_path).replace("\\", "/")
        file_uri = "file:///" + os.path.abspath(temp_html_path).replace("\\", "/")
        page.goto(file_uri)
        page.wait_for_load_state("networkidle")
        
        # Take screenshot of exact 1080x1920 area
        page.screenshot(
            path=output_path,
            clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1920}
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
    # Quick Test
    generate_html_thumbnail(
        "Thumbnail_Test.png",
        top_label="BÍ MẬT TRAFFIC 2026",
        main_title="CÚ ĐẢO NGƯỢC THUẬT TOÁN GOOGLE",
        hook="", # Hidden in HTML anyway
        cta="GIẢI MÃ BÍ MẬT NGAY",
        portrait_path=r"D:\SEOSONA Video\PTP_8811_nobg.png",
        watermark="AI 2026",
        manual_title=("CÚ ĐẢO NGƯỢC", "THUẬT TOÁN", "GOOGLE"),
        manual_cta=("GIẢI MÃ", "BÍ MẬT", "NGAY")
    )
