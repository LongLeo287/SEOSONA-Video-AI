"""
Trình chuyển đổi Subtitle Style từ VideoCaptioner sang CSS cho HyperFrames.
"""
def convert_to_css(style_dict: dict) -> str:
    """
    Chuyển đổi dictionary cấu hình style (giống VideoCaptioner) thành mã CSS.
    """
    css_rules = []
    
    font_name = style_dict.get("font_name", "Inter")
    font_size = style_dict.get("font_size", 42)
    css_rules.append(f"font-family: '{font_name}', sans-serif;")
    css_rules.append(f"font-size: {font_size}px;")
    css_rules.append("text-align: center;")
    css_rules.append("position: absolute;")
    css_rules.append("left: 50%;")
    css_rules.append("transform: translateX(-50%);")
    
    mode = style_dict.get("mode", "ass")
    
    if mode == "rounded":
        text_color = style_dict.get("text_color", "#000000")
        bg_color = style_dict.get("bg_color", "rgba(13, 227, 255, 0.9)")
        corner_radius = style_dict.get("corner_radius", 14)
        padding_h = style_dict.get("padding_h", 24)
        padding_v = style_dict.get("padding_v", 18)
        margin_bottom = style_dict.get("margin_bottom", 40)
        
        css_rules.append(f"color: {text_color};")
        css_rules.append(f"background-color: {bg_color};")
        css_rules.append(f"border-radius: {corner_radius}px;")
        css_rules.append(f"padding: {padding_v}px {padding_h}px;")
        css_rules.append(f"bottom: {margin_bottom}px;")
        css_rules.append("display: inline-block;")
        
    else: # mode == "ass"
        primary_color = style_dict.get("primary_color", "#65ff5a")
        outline_color = style_dict.get("outline_color", "#000000")
        outline_width = style_dict.get("outline_width", 2.0)
        margin_bottom = style_dict.get("margin_bottom", 30)
        is_bold = style_dict.get("bold", True)
        
        css_rules.append(f"color: {primary_color};")
        css_rules.append(f"bottom: {margin_bottom}px;")
        if is_bold:
            css_rules.append("font-weight: bold;")
            
        ow = outline_width
        oc = outline_color
        css_rules.append(f"""text-shadow: 
            -{ow}px -{ow}px 0 {oc},
             {ow}px -{ow}px 0 {oc},
            -{ow}px  {ow}px 0 {oc},
             {ow}px  {ow}px 0 {oc};""")
             
    return "\n".join(css_rules)

if __name__ == "__main__":
    test_rounded_style = {
        "mode": "rounded",
        "font_size": 48,
        "bg_color": "rgba(255, 255, 255, 0.8)",
        "text_color": "#ff0000",
        "corner_radius": 20
    }
    print("System log")
    print(".subtitle-container {")
    print(convert_to_css(test_rounded_style))
    print("}")
