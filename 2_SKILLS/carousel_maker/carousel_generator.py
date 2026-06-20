import os
import json
import uuid
import urllib.parse

# Using Playwright to capture the HTML as images
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

def _html_escape(text: str) -> str:
    """Safely escape text for HTML."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;")

def highlight_text(text: str, highlight: str, highlight_color: str) -> str:
    if not highlight or highlight not in text:
        return _html_escape(text)
    
    escaped_text = _html_escape(text)
    escaped_hl = _html_escape(highlight)
    
    return escaped_text.replace(escaped_hl, f'<span style="color: {highlight_color}">{escaped_hl}</span>')

def generate_carousel_slides(slide_data: list, output_dir: str, logo_path: str = None):
    """
    Generates PNG images for each slide in the slide_data array using Playwright.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if logo_path and os.path.exists(logo_path):
        logo_uri = "file:///" + urllib.parse.quote(logo_path.replace('\\', '/'))
    else:
        logo_uri = ""
        
    # Standard SEOSONA Carousel Colors
    COLOR_NAVY = "#1A2DB5"
    COLOR_BLUE = "#1565C0"
    COLOR_LIGHTBLUE = "#BBDEFB"
    COLOR_BG = "#F3F6FA"
    COLOR_YELLOW = "#FFD54F"
    
    base_html = f"""
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0; padding: 0;
            width: 1080px; height: 1080px;
            font-family: 'Be Vietnam Pro', sans-serif;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
        }}
        .logo {{
            position: absolute;
            top: 60px; left: 60px;
            height: 60px;
            z-index: 100;
        }}
        .footer {{
            position: absolute;
            bottom: 50px; left: 60px; right: 60px;
            border-top: 2px solid #E2E8F2;
            padding-top: 20px;
            font-size: 24px;
            color: #5A6588;
            display: flex;
            justify-content: space-between;
            font-weight: 600;
        }}
        
        /* COVER SLIDE */
        .cover-slide {{
            background-color: {COLOR_NAVY};
            width: 100%; height: 100%;
            display: flex; flex-direction: column;
            justify-content: center;
            padding: 100px;
            box-sizing: border-box;
            background-image: radial-gradient(rgba(255,255,255,0.1) 2px, transparent 2px);
            background-size: 30px 30px;
        }}
        .cover-pill {{
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50px;
            color: white;
            padding: 15px 40px;
            font-size: 30px;
            font-weight: 700;
            width: fit-content;
            margin-bottom: 40px;
        }}
        .cover-title {{
            color: white;
            font-size: 100px;
            font-weight: 800;
            line-height: 1.1;
            margin: 0;
            margin-bottom: 40px;
            text-transform: uppercase;
        }}
        .cover-desc {{
            color: rgba(255,255,255,0.8);
            font-size: 40px;
            font-weight: 400;
            border-left: 6px solid {COLOR_YELLOW};
            padding-left: 30px;
        }}
        
        /* CONTENT SLIDE */
        .content-slide {{
            background-color: {COLOR_BG};
            width: 100%; height: 100%;
            padding: 160px 80px 120px 80px;
            box-sizing: border-box;
            background-image: radial-gradient(rgba(0,0,0,0.03) 2px, transparent 2px);
            background-size: 30px 30px;
        }}
        .content-header {{
            display: flex; align-items: center; margin-bottom: 40px;
        }}
        .content-number {{
            font-size: 120px; font-weight: 800; color: {COLOR_NAVY};
            line-height: 1; margin-right: 30px;
        }}
        .content-heading {{
            font-size: 60px; font-weight: 800; color: #0E1633;
            line-height: 1.2;
        }}
        .content-panel {{
            background: white;
            border-radius: 30px;
            padding: 60px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.05);
            border: 2px solid #E2E8F2;
            font-size: 36px;
            color: #5A6588;
            line-height: 1.6;
        }}
        .content-panel ul {{ margin: 0; padding-left: 40px; }}
        .content-panel li {{ margin-bottom: 20px; }}
        .closing-band {{
            background: {COLOR_NAVY};
            border-radius: 20px;
            padding: 30px;
            color: white;
            font-size: 36px;
            font-weight: 700;
            margin-top: 40px;
            text-align: center;
        }}
    </style>
    </head>
    <body>
        <div id="slide-container"></div>
    </body>
    </html>
    """

    # We will generate one HTML file that Playwright can open, then we replace #slide-container content and screenshot
    temp_html_path = os.path.join(output_dir, "temp_carousel.html")
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(base_html)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
            page.goto(f"file:///{temp_html_path.replace(chr(92), '/')}")

            for idx, slide in enumerate(slide_data):
                slide_type = slide.get("type", "content")
                
                if slide_type == "cover":
                    title_html = highlight_text(slide.get("title", ""), slide.get("highlight", ""), COLOR_LIGHTBLUE)
                    slide_html = f"""
                    <div class="cover-slide">
                        <img src="{logo_uri}" class="logo" style="filter: brightness(0) invert(1);" />
                        <div class="cover-pill">{_html_escape(slide.get("pill", ""))}</div>
                        <h1 class="cover-title">{title_html}</h1>
                        <div class="cover-desc">{_html_escape(slide.get("desc", ""))}</div>
                    </div>
                    """
                else:
                    heading_html = highlight_text(slide.get("heading", ""), slide.get("heading_highlight", ""), COLOR_BLUE)
                    body_items = slide.get("body", [])
                    if isinstance(body_items, str):
                        body_items = [body_items]
                    
                    body_html = "<ul>" + "".join([f"<li>{_html_escape(item)}</li>" for item in body_items]) + "</ul>"
                    
                    closing_html = ""
                    if slide.get("closing"):
                        cl_text = highlight_text(slide.get("closing", ""), slide.get("closing_highlight", ""), COLOR_YELLOW)
                        closing_html = f'<div class="closing-band">{cl_text}</div>'
                        
                    slide_html = f"""
                    <div class="content-slide">
                        <img src="{logo_uri}" class="logo" />
                        <div class="content-header">
                            <div class="content-number">{_html_escape(slide.get("slide_number", f"0{idx}"))}</div>
                            <div class="content-heading">{heading_html}</div>
                        </div>
                        <div class="content-panel">
                            {body_html}
                        </div>
                        {closing_html}
                        
                        <div class="footer">
                            <span>SEOSONA &middot; Share to be shared more</span>
                            <span>{_html_escape(slide.get("slide_number", f"0{idx}"))}/{len(slide_data)-1}</span>
                        </div>
                    </div>
                    """
                
                # Evaluate and inject the HTML into the container
                page.evaluate(f'document.getElementById("slide-container").innerHTML = `{slide_html}`')
                
                # Take screenshot
                out_file = os.path.join(output_dir, f"slide_{idx+1:02d}.png")
                page.screenshot(path=out_file)
                print(f"[Carousel Generator] Rendered {out_file}")

            browser.close()
            
    except Exception as e:
        print(f"[Carousel Generator] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    dummy_data = [
        {"type": "cover", "pill": "TIN TỨC AI", "title": "BÍ MẬT CAROUSEL", "highlight": "CAROUSEL", "desc": "Cách tạo ảnh hàng loạt bằng Python"},
        {"type": "content", "slide_number": "01", "heading": "Sử dụng Playwright", "heading_highlight": "Playwright", "body": ["Render mã HTML tĩnh", "Chụp ảnh kích thước 1080x1080"], "closing": "Siêu Nhanh", "closing_highlight": "Nhanh"}
    ]
    generate_carousel_slides(dummy_data, "./test_carousel")
