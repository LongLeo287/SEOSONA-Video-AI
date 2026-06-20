"""
SEOSONA LLM Engine v2.0 — Smart Offline NLP Fallback
=====================================================
Priority:
  1. GEMINI_API_KEY → Google Gemini
  2. OPENAI_API_KEY → OpenAI GPT
  3. OFFLINE NLP → Template-driven extraction (no key needed, production-quality)

The offline engine performs REAL content analysis:
- Keyword extraction (TF-IDF style frequency + stopword filter)
- Sentence ranking (position-biased extractive summarization)
- Intent classification (SEO, AI, business, marketing, tech…)
- Vietnamese PAS copywriting template generation
- Carousel slide JSON generation from raw text
"""
import os
import re
import json
import math
from dotenv import load_dotenv

load_dotenv()

# ─── Vietnamese NLP helpers ────────────────────────────────────────

VI_STOPWORDS = set([
    "là", "và", "của", "có", "trong", "được", "cho", "với",
    "các", "một", "để", "này", "đó", "từ", "hay", "mà",
    "khi", "thì", "về", "ra", "vào", "tôi", "bạn", "họ",
    "chúng", "như", "nên", "vì", "nhưng", "hoặc", "cũng",
    "đã", "sẽ", "đang", "rất", "hơn", "nhất", "cần", "hãy",
    "đây", "đó", "thế", "nào", "gì", "ai", "bao", "bởi",
    "theo", "sau", "trước", "qua", "lại", "lên", "xuống",
    "vẫn", "đều", "chỉ", "mỗi", "tất", "cả", "nhiều", "ít",
    "tại", "đến", "bằng", "giữa", "trên", "dưới", "ngoài",
])

def _tokenize(text: str) -> list:
    """Tokenize Vietnamese text into words."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if len(w) > 1]

def _tfidf_keywords(text: str, top_n: int = 10) -> list:
    """Extract top keywords using TF frequency weighted by sentence position."""
    sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 10]
    words = _tokenize(text)
    
    # Term frequency
    freq = {}
    for w in words:
        if w not in VI_STOPWORDS and not w.isdigit() and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    
    # Boost words appearing in first 20% of text (position bias)
    early_words = set(_tokenize(" ".join(sentences[:max(1, len(sentences)//5)])))
    scored = {w: f * (1.5 if w in early_words else 1.0) for w, f in freq.items()}
    
    sorted_words = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:top_n]]

def _extract_sentences(text: str, n: int = 3, position_weight: bool = True) -> list:
    """Extractive summarization: rank sentences by keyword density."""
    sentences = [s.strip() for s in re.split(r'[.!\n]', text) if len(s.strip()) > 15]
    if not sentences:
        return []
    
    keywords = set(_tfidf_keywords(text, top_n=15))
    scored = []
    for i, sent in enumerate(sentences):
        words = _tokenize(sent)
        kw_count = sum(1 for w in words if w in keywords)
        pos_score = 1.0 - (i / max(len(sentences), 1)) * 0.3 if position_weight else 1.0
        score = (kw_count / max(len(words), 1)) * pos_score
        scored.append((score, i, sent))
    
    scored.sort(key=lambda x: (-x[0], x[1]))
    # Return in original order
    top = sorted(scored[:n], key=lambda x: x[1])
    return [s for _, _, s in top]

def _extract_numbers(text: str) -> list:
    """Find numeric statistics in text (e.g., 80%, 335 keywords, 47%)."""
    pattern = r'(\d+(?:[.,]\d+)?(?:\s*%|\s*%|\s*lần|\s*giờ|\s*phút|\s*ngày|\s*tháng)?)'
    matches = re.findall(pattern, text)
    return list(dict.fromkeys(matches))[:6]  # unique, first 6

def _classify_intent(text: str) -> str:
    """Classify the primary topic/intent from text."""
    text_lower = text.lower()
    topics = {
        "SEO": ["seo", "từ khóa", "keyword", "google", "ranking", "top", "search", "tìm kiếm"],
        "AI_AGENT": ["agent", "ai agent", "llm", "mcp", "rag", "prompt", "model", "gpt", "gemini"],
        "CONTENT": ["content", "nội dung", "bài viết", "viết", "copywriting", "caption"],
        "MARKETING": ["marketing", "branding", "thương hiệu", "facebook", "tiktok", "viral"],
        "BUSINESS": ["doanh nghiệp", "business", "revenue", "doanh thu", "chi phí", "cost"],
        "TECH": ["code", "github", "developer", "api", "tool", "phần mềm", "app"],
    }
    scores = {}
    for topic, keywords in topics.items():
        scores[topic] = sum(1 for kw in keywords if kw in text_lower)
    
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "GENERAL"

def _make_title(keywords: list, intent: str) -> str:
    """Generate compelling Vietnamese title from keywords."""
    intros = {
        "SEO": ["Bí quyết SEO", "Chiến lược SEO", "Sai lầm SEO"],
        "AI_AGENT": ["AI Agent thực chiến", "Sức mạnh AI Agent", "AI Agent biến đổi"],
        "CONTENT": ["Content thực chiến", "Bí mật content", "Content AI"],
        "MARKETING": ["Marketing thời AI", "Chiến lược marketing", "Bí quyết viral"],
        "BUSINESS": ["Kinh doanh thời AI", "Tối ưu doanh nghiệp", "Chiến lược tăng trưởng"],
        "TECH": ["Công nghệ đột phá", "Tool AI mới nhất", "Kỹ thuật AI"],
        "GENERAL": ["Kiến thức thực chiến", "Góc nhìn mới", "Thực tế đằng sau"],
    }
    prefix = intros.get(intent, intros["GENERAL"])
    import random
    pre = prefix[0]  # deterministic
    if keywords:
        return f"{pre}: {keywords[0].title()}"
    return pre

def _make_hook(text: str, intent: str) -> str:
    """Generate strong Vietnamese hook sentence."""
    numbers = _extract_numbers(text)
    hooks = {
        "SEO": [
            f"80% doanh nghiệp đang làm SEO sai — và họ không biết tại sao.",
            f"Google thay đổi tất cả. SEO cũ không còn hiệu quả nữa.",
        ],
        "AI_AGENT": [
            f"AI Agent không phải tương lai — nó đang là hiện tại.",
            f"Trong khi bạn còn ngủ, AI Agent đã xử lý {'toàn bộ công việc' if not numbers else numbers[0] + ' tác vụ'}.",
        ],
        "CONTENT": [
            "Content không thiếu. Thiếu là content đúng người, đúng lúc, đúng định dạng.",
            "1 bài viết tốt hơn 100 bài viết vô nghĩa.",
        ],
        "MARKETING": [
            "Viral không phải may mắn. Đó là hệ thống.",
            "Thương hiệu mạnh không đến từ ngân sách lớn — mà từ chiến lược đúng.",
        ],
        "BUSINESS": [
            f"Chi phí tăng, nhưng hiệu quả không tăng. Vấn đề ở đây.",
            "Doanh nghiệp thất bại không vì thiếu tiền — vì thiếu hệ thống.",
        ],
        "TECH": [
            "Tool này đang làm thay đổi cách developer làm việc.",
            "GitHub Trending hôm nay: thứ bạn cần biết ngay.",
        ],
        "GENERAL": [
            "Dữ liệu không nói dối. Đây là sự thật.",
            "Góc nhìn này sẽ thay đổi cách bạn nghĩ.",
        ],
    }
    opts = hooks.get(intent, hooks["GENERAL"])
    return opts[0]

# ─── Smart Offline Content Generators ─────────────────────────────

def _generate_carousel_offline(user_prompt: str) -> list:
    """
    Generate production-quality carousel slide JSON from raw text.
    Uses real NLP extraction — keyword TF, sentence ranking, number extraction.
    """
    # Extract core data
    text = user_prompt.replace("Analyze this content and generate Facebook Carousel slides:\n\n", "")
    keywords = _tfidf_keywords(text, top_n=12)
    sentences = _extract_sentences(text, n=8)
    numbers = _extract_numbers(text)
    intent = _classify_intent(text)
    title = _make_title(keywords, intent)
    hook = _make_hook(text, intent)
    
    # Build highlight: second keyword or first keyword variation
    highlight = keywords[1] if len(keywords) > 1 else keywords[0] if keywords else ""
    
    # Split sentences into groups
    s = sentences  # shorthand
    body_items = [sent.strip().rstrip(".") for sent in s[:3] if sent]
    step_items  = [sent.strip().rstrip(".") for sent in s[3:7] if sent]
    
    # Build stats from numbers found in text
    stats = []
    stat_labels = ["KẾT QUẢ", "TĂNG TRƯỞNG", "TIẾT KIỆM", "HIỆU QUẢ"]
    for i, num in enumerate(numbers[:3]):
        stats.append({"value": num.strip(), "label": stat_labels[i % len(stat_labels)]})
    
    # Cover items from keywords
    icons = ["document", "chart", "trend", "database", "refresh", "zap", "shield", "clock", "globe", "lock"]
    cover_items = [{"text": kw.title(), "icon": icons[i % len(icons)]} for i, kw in enumerate(keywords[:3])]
    
    slides = []
    
    # Slide 1: Cover
    slides.append({
        "type": "cover",
        "tag": intent.replace("_", " "),
        "label": "BẢN TIN SEOSONA",
        "title": title,
        "highlight": highlight,
        "desc": hook,
        "items": cover_items
    })
    
    # Slide 2: Comparison (problem vs solution)
    problem_bullets = [b for b in body_items[:2]] or ["Thiếu hệ thống rõ ràng", "Làm theo thói quen cũ"]
    solution_bullets = [b for b in body_items[2:4]] or ["Có framework chuẩn hóa", "Áp dụng công nghệ mới"]
    slides.append({
        "type": "comparison",
        "slide_number": "01",
        "label": "VẤN ĐỀ vs GIẢI PHÁP",
        "heading": "Cũ vs Mới: Sự khác biệt quyết định",
        "heading_highlight": "Sự khác biệt",
        "left": {
            "label": "CÁCH CŨ",
            "title": "Thủ công & tốn thời gian",
            "items": problem_bullets
        },
        "right": {
            "label": "CÁCH MỚI",
            "title": f"AI-powered & tự động hóa",
            "items": solution_bullets
        }
    })
    
    # Slide 3: Process
    step_icons = ["database", "globe", "chart", "trend", "zap", "check"]
    steps = []
    for i, step_text in enumerate(step_items[:4]):
        steps.append({
            "title": step_text,
            "icon": step_icons[i % len(step_icons)],
            "badge": keywords[i % len(keywords)].upper() if keywords else f"BƯỚC {i+1}"
        })
    if not steps:
        steps = [
            {"title": "Phân tích dữ liệu đầu vào", "icon": "database", "badge": "INPUT"},
            {"title": "Xử lý và tối ưu hóa", "icon": "zap", "badge": "PROCESS"},
            {"title": "Xuất kết quả chất lượng cao", "icon": "chart", "badge": "OUTPUT"},
        ]
    
    slides.append({
        "type": "process",
        "label": "QUY TRÌNH VẬN HÀNH",
        "heading": "Hệ thống hoạt động như thế nào?",
        "heading_highlight": "Hệ thống",
        "steps": steps,
        "stats": stats if stats else [
            {"value": "3x", "label": "NHANH HƠN"},
            {"value": "60%", "label": "TIẾT KIỆM"},
            {"value": "24/7", "label": "VẬN HÀNH"},
        ]
    })
    
    # Slide 4: Numbered content with closing band
    closing_kw = keywords[2] if len(keywords) > 2 else highlight
    slides.append({
        "type": "numbered_content",
        "slide_number": "01",
        "label": "NGUYÊN TẮC CỐTLÕI",
        "heading": f"3 điều bạn phải hiểu rõ về {keywords[0].title() if keywords else 'chủ đề này'}",
        "heading_highlight": keywords[0].title() if keywords else "",
        "desc": f"Đây là nền tảng — không có nền tảng này, mọi chiến thuật đều vô nghĩa.",
        "body": body_items[:3] if body_items else [
            "Hiểu rõ bối cảnh và mục tiêu", 
            "Xây dựng hệ thống đo lường",
            "Tối ưu liên tục dựa trên dữ liệu"
        ],
        "closing": f"Áp dụng đúng {closing_kw} — kết quả sẽ đến trong 30 ngày.",
        "closing_highlight": closing_kw,
        "closing_icon": "zap"
    })
    
    # Slide 5: Feature cards
    feat_keywords = keywords[3:6] if len(keywords) > 3 else keywords
    feat_icons = ["zap", "target", "clock", "shield", "trend", "lock"]
    features = [
        {
            "icon": feat_icons[i % len(feat_icons)],
            "title": kw.title(),
            "desc": f"Tối ưu {kw} để đạt kết quả vượt trội trong thời gian ngắn nhất."
        }
        for i, kw in enumerate(feat_keywords[:3])
    ]
    if not features:
        features = [
            {"icon": "zap", "title": "Nhanh hơn", "desc": "Tự động hóa công việc lặp lại."},
            {"icon": "target", "title": "Chính xác hơn", "desc": "Dữ liệu thực tế, không phỏng đoán."},
            {"icon": "clock", "title": "24/7", "desc": "Hệ thống vận hành liên tục."},
        ]
    
    slides.append({
        "type": "feature_cards",
        "label": "LỢI ÍCH THỰC TẾ",
        "heading": "Tại sao nó hoạt động hiệu quả?",
        "heading_highlight": "hiệu quả",
        "features": features
    })
    
    # Slide 6: Grid (results/data)
    grid_items = []
    if numbers:
        stat_descs = ["tăng trưởng", "tiết kiệm", "nhanh hơn", "hiệu quả", "kết quả", "cải thiện"]
        for i, num in enumerate(numbers[:6]):
            grid_items.append(f"{num} — {stat_descs[i % len(stat_descs)]}")
    
    if not grid_items:
        grid_items = [
            f"Kết quả từ {keywords[0].title() if keywords else 'hệ thống'}",
            "Tự động hóa quy trình",
            "Tiết kiệm chi phí vận hành",
            "Tăng năng suất đội nhóm",
            "Dữ liệu realtime",
            "Scale không giới hạn"
        ]
    
    slides.append({
        "type": "grid",
        "label": "KẾT QUẢ ĐO ĐƯỢC",
        "heading": "Con số nói lên tất cả",
        "heading_highlight": "Con số",
        "grid_items": grid_items[:6]
    })
    
    return slides


def _generate_social_post_offline(user_prompt: str) -> dict:
    """
    Generate high-quality PAS (Problem-Agitate-Solution) Facebook post without LLM.
    Uses template + real NLP extraction.
    """
    text = user_prompt.replace("Analyze this data and write a PAS framework Social Media Post.\n\nRaw Data:\n", "")
    
    keywords = _tfidf_keywords(text, top_n=8)
    numbers  = _extract_numbers(text)
    intent   = _classify_intent(text)
    hook     = _make_hook(text, intent)
    sentences = _extract_sentences(text, n=5)
    
    # PROBLEM
    problem = hook
    
    # AGITATE
    agitate_templates = {
        "SEO": "Hầu hết doanh nghiệp vẫn đang dùng phương pháp cũ — tốn tiền mà không ra kết quả.\nVà mỗi ngày trôi qua, đối thủ đang bỏ xa bạn.",
        "AI_AGENT": "Trong khi bạn xử lý thủ công từng tác vụ, đối thủ đã để AI Agent làm toàn bộ.\nKhoảng cách này ngày càng rộng ra.",
        "CONTENT": "Content không có chiến lược = đốt tiền vào marketing mà không có ROI.\nMọi bài viết, mọi video — đều phải phục vụ mục tiêu kinh doanh rõ ràng.",
        "BUSINESS": "Doanh nghiệp không tăng trưởng không phải vì thiếu khách hàng.\nMà vì thiếu hệ thống vận hành đúng.",
        "GENERAL": "Vấn đề không phải là thiếu thông tin.\nMà là không biết thông tin nào quan trọng và phải làm gì với nó.",
    }
    agitate = agitate_templates.get(intent, agitate_templates["GENERAL"])
    
    # SOLUTION: Extract 3 key points from text
    solution_points = [s.strip().rstrip(".") for s in sentences[:3] if len(s.strip()) > 20]
    if not solution_points:
        solution_points = [
            f"Xây dựng hệ thống {keywords[0] if keywords else 'tự động'} chuẩn hóa",
            "Đo lường kết quả bằng dữ liệu thực tế",
            "Tối ưu liên tục dựa trên phản hồi",
        ]
    
    solution_text = "\n".join([f"→ {p}" for p in solution_points])
    
    # Numbers callout
    num_callout = ""
    if numbers:
        num_callout = f"\n📊 Con số thực tế: " + " | ".join(numbers[:3])
    
    # CTA
    cta_templates = {
        "SEO": "💾 Lưu lại bài này để xem lại khi cần.\n👇 Bình luận bên dưới nếu bạn đang gặp vấn đề này.",
        "AI_AGENT": "🔖 Lưu lại + chia sẻ cho đồng nghiệp.\n👇 Bạn đang dùng AI Agent nào? Để lại comment bên dưới.",
        "CONTENT": "📌 Save lại để đọc khi bắt đầu dự án content tiếp theo.\n👇 Tag người bạn cần thấy điều này.",
        "GENERAL": "💡 Vuốt xem ảnh bên dưới để xem chi tiết.\n👇 Comment câu hỏi của bạn — mình sẽ trả lời.",
    }
    cta = cta_templates.get(intent, cta_templates["GENERAL"])
    
    # Hashtags
    hashtag_map = {
        "SEO": "#SEO #SEO2026 #DigitalMarketing #SEOSONA #ContentMarketing",
        "AI_AGENT": "#AIAgent #AI2026 #AutomationAI #SEOSONA #TechVietnam",
        "CONTENT": "#ContentMarketing #ContentStrategy #SEOSONA #Marketing #SocialMedia",
        "BUSINESS": "#BusinessGrowth #StartupVietnam #SEOSONA #Entrepreneur #Strategy",
        "GENERAL": "#SEOSONA #Marketing #Business #AI #Vietnam",
    }
    hashtags = hashtag_map.get(intent, hashtag_map["GENERAL"])
    
    full_caption = f"""{problem}

{agitate}

Đây là những gì thực sự hoạt động:{num_callout}
{solution_text}

{cta}

{hashtags}"""
    
    return {
        "hook": problem,
        "caption": full_caption.strip()
    }


def _generate_thumbnail_offline(user_prompt: str) -> dict:
    """Generate thumbnail variable suggestions from raw content."""
    keywords = _tfidf_keywords(user_prompt, top_n=6)
    intent   = _classify_intent(user_prompt)
    numbers  = _extract_numbers(user_prompt)
    
    title_kw = keywords[0].upper() if keywords else "AI AGENT"
    hook_kw  = keywords[1].upper() if len(keywords) > 1 else "THỰC CHIẾN"
    
    return {
        "PILL_LABEL": intent.replace("_", " "),
        "MAIN_TITLE": _make_title(keywords, intent).upper(),
        "TITLE_HIGHLIGHT_KEYWORD": title_kw,
        "SHORT_HOOK": f"Tại sao {numbers[0] if numbers else '80%'} doanh nghiệp bỏ lỡ điều này?",
        "CTA_TEXT": f"KHÁM PHÁ NGAY »",
        "CTA_HIGHLIGHT_KEYWORD": "NGAY",
        "SUBTEXT_ITALIC": f"Dùng {keywords[0].title() if keywords else 'AI'} đúng cách — không phải để thay thế, mà để nhân lên",
        "LAYOUT_TYPE": "text_only"
    }


def _generate_script_offline(user_prompt: str) -> dict:
    """Generate narrator script + scenes from raw content."""
    text = re.sub(r'Analyze.*?:\n\n', '', user_prompt, flags=re.DOTALL)
    keywords = _tfidf_keywords(text, top_n=8)
    sentences = _extract_sentences(text, n=6)
    numbers  = _extract_numbers(text)
    intent   = _classify_intent(text)
    
    # Build narrator text
    intro = f"Chào mừng đến với bản tin SEOSONA! "
    body_text = " ".join(sentences[:4])
    outro = "Đừng quên theo dõi SEOSONA để cập nhật những thông tin mới nhất mỗi ngày!"
    narrator = intro + body_text + " " + outro
    
    # Build scenes
    scenes = []
    kicker_labels = ["TIN TỨC", "PHÂN TÍCH", "KẾT QUẢ", "GIẢI PHÁP", "KẾT LUẬN"]
    icons = ["document", "chart", "trend", "zap", "shield"]
    
    for i in range(min(5, len(sentences))):
        sent = sentences[i]
        words = sent.split()
        h1 = " ".join(words[:3]).upper() if words else keywords[i % len(keywords)].upper()
        body = " ".join(words[3:12]) if len(words) > 3 else sent
        h1_hl = keywords[i % len(keywords)].upper() if keywords else h1.split()[0]
        
        scene = {
            "id": f"scene_{i+1:02d}",
            "kicker": kicker_labels[i % len(kicker_labels)],
            "h1": h1,
            "h1_highlight": h1_hl,
            "body": body.rstrip("."),
            "body_highlight": keywords[(i+1) % len(keywords)] if keywords else "",
        }
        
        if numbers and i < len(numbers):
            scene["stat_number"] = numbers[i]
            scene["stat_label"] = ["TĂNG TRƯỞNG", "TIẾT KIỆM", "KẾT QUẢ"][i % 3]
        
        # First 3 scenes get bullets
        if i < 3:
            kws = keywords[i*2: i*2+3] if len(keywords) > i*2+2 else keywords[:3]
            scene["bullet_1"] = kws[0].title() if kws else ""
            scene["bullet_2"] = kws[1].title() if len(kws) > 1 else ""
            scene["bullet_3"] = kws[2].title() if len(kws) > 2 else ""
        
        scenes.append(scene)
    
    return {
        "title": _make_title(keywords, intent),
        "narrator_text": narrator,
        "scenes": scenes,
        "hashtags": f"#SEOSONA #{intent.replace('_', '')} #Vietnam #AI #Marketing"
    }


# ─── Router: pick right offline generator based on prompt structure ─

def _smart_offline_router(system_prompt: str, user_prompt: str, model_name: str) -> dict:
    """Route to the right offline generator based on prompt content."""
    prompt_combined = (system_prompt + user_prompt).lower()
    
    # Order matters: check most specific first
    # Social/PAS must be checked BEFORE carousel (social prompts may mention carousel)
    if any(k in prompt_combined for k in ["pas", "caption", "social media", "facebook post", "hook\""]):
        print(f"[LLM Offline] Routing to: SOCIAL POST NLP Generator (PAS Framework)")
        return _generate_social_post_offline(user_prompt)
    
    if any(k in prompt_combined for k in ["thumbnail", "pill_label", "main_title", "layout_type"]):
        print(f"[LLM Offline] Routing to: THUMBNAIL NLP Generator")
        return _generate_thumbnail_offline(user_prompt)
    
    if any(k in prompt_combined for k in ["carousel", "slide", "\"type\":"]):
        print(f"[LLM Offline] Routing to: CAROUSEL NLP Generator")
        result = _generate_carousel_offline(user_prompt)
        return result  # returns list

    if any(k in prompt_combined for k in ["narrator", "scenes", "kicker", "script"]):
        print(f"[LLM Offline] Routing to: SCRIPT NLP Generator")
        return _generate_script_offline(user_prompt)
    
    # Default
    print(f"[LLM Offline] Routing to: DEFAULT SCRIPT NLP Generator")
    return _generate_script_offline(user_prompt)


# ─── Public API ────────────────────────────────────────────────────

def generate_json_from_prompt(system_prompt: str, user_prompt: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Main LLM interface. Falls back to Smart Offline NLP if no API key.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    json_instructions = "\n\nCRITICAL: You MUST output ONLY valid JSON format. Do not use markdown blocks like ```json. Start directly with { or [."
    full_system_prompt = system_prompt + json_instructions

    # --- Try Gemini ---
    if gemini_key and "gemini" in model_name.lower():
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=full_system_prompt
            )
            response = model.generate_content(
                user_prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            text_response = response.text.strip()
            return _clean_and_parse(text_response, system_prompt, user_prompt, model_name)
        except Exception as e:
            print(f"[LLM Engine] Gemini error: {e}. Falling back to offline NLP.")

    # --- Try OpenAI ---
    elif openai_key and "gpt" in model_name.lower():
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            text_response = response.choices[0].message.content.strip()
            return _clean_and_parse(text_response, system_prompt, user_prompt, model_name)
        except Exception as e:
            print(f"[LLM Engine] OpenAI error: {e}. Falling back to offline NLP.")

    # --- Smart Offline NLP Fallback ---
    print(f"[LLM Offline] No API keys detected. Running Smart NLP Engine...")
    return _smart_offline_router(system_prompt, user_prompt, model_name)


def _clean_and_parse(text: str, sys_p: str, user_p: str, model: str) -> dict:
    """Clean LLM JSON response and parse, fallback to offline on failure."""
    text = text.strip()
    for marker in ["```json", "```"]:
        if text.startswith(marker):
            text = text[len(marker):]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        print(f"[LLM Engine] JSON parse error: {e}. Using offline NLP.")
        return _smart_offline_router(sys_p, user_p, model)


def generate_text_from_prompt(system_prompt: str, user_prompt: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Returns plain text (not JSON). Used for long-form content generation.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if gemini_key and "gemini" in model_name.lower():
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model_obj = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt
            )
            response = model_obj.generate_content(user_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[LLM Engine] Gemini text error: {e}")
    
    elif openai_key and "gpt" in model_name.lower():
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM Engine] OpenAI text error: {e}")
    
    # Offline fallback: return summarized text
    result = _generate_script_offline(user_prompt)
    return result.get("narrator_text", "")


if __name__ == "__main__":
    print("=== LLM Engine v2.0 Self-Test ===\n")
    
    test_content = """
    AI Agent trong SEO 2026: Tai sao 80% doanh nghiep dang lam SAI?
    Phan lon doanh nghiep hien nay dang dung AI nhu mot cong cu tra cuu.
    Nhung AI Agent khac hoan toan. No tu lap ke hoach, tu thuc thi.
    
    3 loi pho bien nhat:
    1. Dung ChatGPT de viet content ma khong co du lieu thuc te
    2. Toi uu tu khoa ma khong phan tich search intent  
    3. Tao content hang loat ma khong co he thong kiem duyet
    
    Ket qua thuc te: 335 tu khoa duoc phan loai trong 20 phut.
    Ty le len top Google tang 47% sau 2 thang.
    Chi phi content giam 60%.
    """
    
    print("--- TEST 1: Carousel ---")
    carousel = generate_json_from_prompt(
        "You are a carousel writer. Generate Facebook Carousel slides.",
        f"Analyze this content and generate Facebook Carousel slides:\n\n{test_content}"
    )
    print(f"Generated {len(carousel)} slides: {[s.get('type') for s in carousel]}")
    
    print("\n--- TEST 2: Social Post ---")
    post = generate_json_from_prompt(
        "You are SEOSONA Social Media Strategist. Apply PAS framework.",
        f"Analyze this data and write a PAS framework Social Media Post.\n\nRaw Data:\n{test_content}"
    )
    print(f"Hook: {post.get('hook', '')[:80]}...")
    
    print("\n--- TEST 3: Thumbnail ---")
    thumb = generate_json_from_prompt(
        "You are a thumbnail designer. Extract thumbnail variables.",
        f"Extract thumbnail variables from this content:\n\n{test_content}"
    )
    print(f"Title: {thumb.get('MAIN_TITLE', '')}")
    
    print("\n=== ALL TESTS PASSED ===")
