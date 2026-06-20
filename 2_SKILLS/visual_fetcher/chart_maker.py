import os
import urllib.parse
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

# Shared Palette
PALETTE = {
    "seosona": {"bg": "#FFFFFF", "bar": "#1565C0", "text": "#0E1633", "text_sub": "#5A6588", "axis": "#E5EAF2"},
    "cqa": {"bg": "#FFFFFF", "bar": "#3B82F6", "text": "#0E1633", "text_sub": "#3A4A6B", "axis": "#E8EDF5"}
}

def _build_html(data: dict, chart_type: str, brand: str) -> str:
    p = PALETTE.get(brand, PALETTE["seosona"])
    
    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
        width: 800px; height: 600px;
        font-family: 'Be Vietnam Pro', sans-serif;
        background: {p['bg']};
        display: flex; flex-direction: column; justify-content: flex-end;
        padding: 40px;
    }}
    .chart-container {{
        display: flex; align-items: flex-end; justify-content: center; gap: 60px;
        height: 100%; border-bottom: 3px solid {p['axis']};
        padding-bottom: 20px;
        padding-left: 40px;
        padding-right: 40px;
    }}
    .bar-group {{
        display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
        height: 100%; width: 140px; gap: 16px;
    }}
    .bar {{
        width: 140px; background: {p['bar']}; border-radius: 12px 12px 0 0;
        display: flex; align-items: flex-start; justify-content: center;
        padding-top: 16px; transition: height 0.3s;
    }}
    .bar-value {{ font-size: 32px; font-weight: 800; color: white; width: 100%; text-align: center; }}
    .bar-label {{ font-size: 24px; font-weight: 700; color: {p['text']}; text-align: center; }}
    """

    if not data:
        return f"<html><head><style>{css}</style></head><body>No Data</body></html>"

    max_val = max(float(v) for v in data.values()) if data else 1
    if max_val == 0: max_val = 1

    bars_html = ""
    for label, val in data.items():
        height_pct = (float(val) / max_val) * 100
        # Enforce minimum height for visibility
        height_pct = max(height_pct, 15)
        
        bars_html += f"""
        <div class="bar-group">
            <div class="bar" style="height: {height_pct}%;">
                <span class="bar-value">{val}</span>
            </div>
            <div class="bar-label">{label}</div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head><style>{css}</style></head>
    <body>
        <div class="chart-container">
            {bars_html}
        </div>
    </body>
    </html>
    """

def draw_chart(data: dict, output_path: str, chart_type: str = "bar", brand: str = "seosona") -> str:
    """
    Renders a bar chart from data dict (label -> value) and saves as PNG.
    Returns the absolute path to the saved image.
    """
    html_content = _build_html(data, chart_type, brand)
    
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        temp_html = output_path + ".temp.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 800, "height": 600}, device_scale_factor=2)
            page.goto(f"file:///{os.path.abspath(temp_html).replace(chr(92), '/')}")
            page.screenshot(path=output_path, omit_background=True)
            browser.close()
            
        if os.path.exists(temp_html):
            os.remove(temp_html)
            
        return os.path.abspath(output_path)
    except Exception as e:
        print(f"[Chart Maker] Failed to generate chart: {e}")
        return ""

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 2:
        data = json.loads(sys.argv[1])
        draw_chart(data, sys.argv[2])
    else:
        print("Testing chart generation...")
        test_data = {"Truyền thống": 20, "AI": 85}
        draw_chart(test_data, "./test_chart.png", brand="seosona")
        print("Generated test_chart.png")
