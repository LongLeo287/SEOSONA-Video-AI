from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_text_with_shadow(draw, text, position, font, text_color, shadow_color="#0F172A"):
    x, y = position
    
    # Modern Text Rendering: Stroke (Outline) + Shadow
    # Vẽ bóng (Drop shadow)
    shadow_offset = 8
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    
    # Vẽ text chính với viền dày (Stroke)
    stroke_width = 5
    stroke_color = "#FFFFFF" if text_color == hex_to_rgb("#0F172A") else "#0F172A"
    
    draw.text((x, y), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

def create_thumbnail(hook_text, output_path, brand_profile, bg_image_path=None, logo_path=None, aspect_ratio="9:16"):
    """
    Creates a rich YouTube/TikTok thumbnail with Aspect Ratio support.
    """
    print(f"Generating Rich Thumbnail ({aspect_ratio})...")
    
    # 1. Determine Dimensions
    if aspect_ratio == "16:9":
        W, H = 1920, 1080
        wrap_width = 25 # Wider text wrap
        font_size = 140
        logo_pos = (150, 80) # Top left
    else: # 9:16 default
        W, H = 1080, 1920
        wrap_width = 15
        font_size = 120
        logo_pos = (50, 50)
        
    text_hex = brand_profile['colors']['text']
    highlight_hex = brand_profile['colors']['highlight']
    
    # 2. Prepare Background
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            img = Image.open(bg_image_path).convert('RGB')
            img_ratio = img.width / img.height
            target_ratio = W / H
            if img_ratio > target_ratio:
                new_w = int(img.height * target_ratio)
                left = (img.width - new_w) // 2
                img = img.crop((left, 0, left + new_w, img.height))
            else:
                new_h = int(img.width / target_ratio)
                top = (img.height - new_h) // 2
                img = img.crop((0, top, img.width, top + new_h))
                
            img = img.resize((W, H))
            img = img.filter(ImageFilter.GaussianBlur(10))
        except Exception as e:
            img = Image.new('RGB', (W, H), color=hex_to_rgb(brand_profile['colors']['background']))
    else:
        # Tự động tạo Gradient Background nếu không có ảnh tĩnh
        img = Image.new('RGB', (W, H))
        draw_bg = ImageDraw.Draw(img)
        color_top = hex_to_rgb(brand_profile['colors']['primary'])
        color_bottom = hex_to_rgb(brand_profile['colors']['secondary'])
        for y in range(H):
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / H)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / H)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / H)
            draw_bg.line([(0, y), (W, y)], fill=(r, g, b))

    # Gradient Tối góc dưới (Vignette) để nổi chữ
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(H//2, H):
        alpha = int(200 * (y - H//2) / (H//2))
        overlay_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # 3. Add Logo
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            l_w = 300 if aspect_ratio == "16:9" else 250
            l_h = int(logo.height * (l_w / logo.width))
            logo = logo.resize((l_w, l_h))
            img.paste(logo, logo_pos, logo)
        except Exception as e:
            pass

    # 4. Prepare Font
    try:
        font_path = "D:/SEOSONA Video/7_ASSETS/fonts/Montserrat-Black.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # 5. Wrap and Draw Text
    lines = textwrap.wrap(hook_text, width=wrap_width)
    line_height = int(font_size * 1.3)
    total_height = len(lines) * line_height
    y_text = (H - total_height) // 2
    
    for i, line in enumerate(lines):
        color_to_use = hex_to_rgb(highlight_hex) if i % 2 == 0 else hex_to_rgb(text_hex)
        
        try:
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
        except Exception:
            text_width = len(line) * (font_size // 2)
            
        # Layout Logic
        if aspect_ratio == "16:9":
            # Align Left for YouTube standard
            x_text = 150
        else:
            # Center for TikTok
            x_text = (W - text_width) // 2
            
        draw_text_with_shadow(draw, line, (x_text, y_text), font, color_to_use)
        y_text += line_height

    img.save(output_path, quality=95)
    print(f"Thumbnail ({aspect_ratio}) saved to {output_path}")
    return output_path
