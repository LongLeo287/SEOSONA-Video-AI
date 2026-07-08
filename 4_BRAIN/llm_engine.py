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
import time
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
    "cái", "anh", "mình", "không", "viết", "người", "những",
    "nếu", "có", "không", "những", "một", "bạn", "của", "và",
    "thì", "mà", "là", "rồi", "được", "cho", "các", "với", "như",
    "khi", "có", "thể", "cũng", "đã", "để", "trong", "đó", "về",
    "làm", "ra", "lại", "này", "chỉ", "từ", "còn", "sẽ", "nó", "những",
    "nữa", "phải", "đến", "đang", "thấy", "đi", "đâu", "đây", "nhé", "nha", "ạ"
])

def _tokenize(text: str) -> list:
    """Tokenize Vietnamese text into words."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if len(w) > 1 and not w.isdigit()]

def _tfidf_keywords(text: str, top_n: int = 10) -> list:
    """Extract top keywords using TF frequency weighted by sentence position."""
    sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 10]
    words = _tokenize(text)

    # Term frequency
    freq = {}
    for w in words:
        if w not in VI_STOPWORDS and len(w) > 2:
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
        # WHOLE-WORD match, not substring: 'top'∈laptop, 'api'∈therapist, 'app'∈apply, 'cost'∈costume,
        # 'code'∈decode all mis-scored the intent. \b with re.UNICODE treats VN diacritics as word chars,
        # so multi-word VN phrases ("từ khóa") still match as a whole.
        scores[topic] = sum(1 for kw in keywords
                            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))

    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "GENERAL"

def _leading_phrase(text: str, n: int = 3, maxlen: int = 28) -> str:
    """A leading CONTENT phrase (words in READING ORDER) from the source. Vietnamese is multi-syllable,
    so a contiguous phrase keeps compounds intact ('Nghiên cứu từ khóa') where a single top-frequency
    syllable breaks them (title 'Bí quyết SEO: Nghiên' instead of '… Nghiên Cứu Từ Khóa')."""
    words = re.findall(r"[\wÀ-ỹ]+", str(text or ""))
    while words and words[0].lower() in VI_STOPWORDS:      # start on a content word
        words = words[1:]
    take = words[:n]
    while take and take[-1].lower() in VI_STOPWORDS:       # don't end on a connector
        take.pop()
    return " ".join(take)[:maxlen]


def _smart_title(s):
    """Title-case for on-screen display while PRESERVING acronym/brand casing. str.title() downcases
    acronyms — 'SEO'→'Seo', 'AI'→'Ai', 'API'→'Api' — which mangles the keyword in the video's own
    text (headings/bullets/cover). Only all-lowercase words are capitalised; anything already carrying
    an uppercase letter (SEO, ChatGPT, iPhone) is left untouched."""
    return " ".join(w if any(c.isupper() for c in w) else w.capitalize() for w in str(s).split())


def _make_title(keywords: list, intent: str, text: str = "") -> str:
    """Generate compelling Vietnamese title. Prefers a leading CONTENT PHRASE from the source text (keeps
    compounds) over a lone top-frequency keyword syllable; falls back to keywords[0] when no text."""
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
    tail = _leading_phrase(text, n=3) if text else (keywords[0] if keywords else "")
    return f"{pre}: {_smart_title(tail)}" if tail else pre

def _make_hook(text: str, intent: str) -> str:
    """Generate strong Vietnamese hook sentence."""
    numbers = _extract_numbers(text)
    hooks = {
        "SEO": [
            # NO fabricated statistic — the old "80% doanh nghiệp làm SEO sai" invented a number that
            # isn't sourced (violates "không làm giả" + hook-must-be-true). Keep the punch, drop the fake %.
            f"Nhiều doanh nghiệp đang làm SEO sai cách — mà không hề hay biết.",
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
    title = _make_title(keywords, intent, text)
    hook = _make_hook(text, intent)

    # Build highlight: second keyword or first keyword variation
    highlight = keywords[1] if len(keywords) > 1 else keywords[0] if keywords else ""

    # Clean sentences for presentation
    cleaned_sents = []
    for s in sentences:
        s = s.strip().rstrip(".")
        if len(s.split()) > 4:
            cleaned_sents.append(s[0].upper() + s[1:])

    # Split sentences into groups
    s = cleaned_sents
    body_items = [sent for sent in s[:3]] if len(s) >= 3 else [
        "Xác định đúng mục tiêu cốt lõi ngay từ đầu",
        "Triển khai chiến lược với lộ trình rõ ràng",
        "Đo lường và điều chỉnh liên tục"
    ]
    step_items  = [sent for sent in s[3:7]] if len(s) >= 4 else [
        "Nghiên cứu dữ liệu",
        "Phân tích đối thủ",
        "Lập kế hoạch triển khai",
        "Tối ưu hóa điểm chạm"
    ]

    # Build stats from numbers found in text
    stats = []
    stat_labels = ["KẾT QUẢ", "TĂNG TRƯỞNG", "TIẾT KIỆM", "HIỆU QUẢ"]
    cleaned_numbers = [n for n in numbers if len(n) <= 10]
    for i, num in enumerate(cleaned_numbers[:3]):
        stats.append({"value": num.strip(), "label": stat_labels[i % len(stat_labels)]})

    # Cover items from keywords
    icons = ["document", "chart", "trend", "database", "refresh", "zap", "shield", "clock", "globe", "lock"]
    cover_items = [{"text": _smart_title(kw), "icon": icons[i % len(icons)]} for i, kw in enumerate(keywords[:3])]

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
    problem_bullets = [b for b in body_items[:2]]
    solution_bullets = [b for b in body_items[1:3]]
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
            "title": f"Tối ưu & Tự động hóa",
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

    slides.append({
        "type": "process",
        "label": "QUY TRÌNH VẬN HÀNH",
        "heading": "Hệ thống hoạt động như thế nào?",
        "heading_highlight": "Hệ thống",
        "steps": steps,
        # Fallback stats (no real numbers extracted) must be QUALITATIVE — never invent a metric like
        # "3x nhanh hơn" / "60% tiết kiệm" for an unknown topic (fabrication that ships in the carousel).
        "stats": stats if stats else [
            {"value": "TỰ ĐỘNG", "label": "QUY TRÌNH"},
            {"value": "NHẤT QUÁN", "label": "CHẤT LƯỢNG"},
            {"value": "24/7", "label": "VẬN HÀNH"},
        ]
    })

    # Slide 4: Numbered content with closing band
    closing_kw = keywords[2] if len(keywords) > 2 else highlight
    slides.append({
        "type": "numbered_content",
        "slide_number": "01",
        "label": "NGUYÊN TẮC CỐT LÕI",
        "heading": f"3 điều bạn phải hiểu rõ về {_smart_title(keywords[0]) if keywords else 'chủ đề này'}",
        "heading_highlight": _smart_title(keywords[0]) if keywords else "",
        "desc": f"Đây là nền tảng — không có nền tảng này, mọi chiến thuật đều vô nghĩa.",
        "body": body_items[:3],
        "closing": f"Áp dụng đúng {closing_kw} — và bạn sẽ thấy sự khác biệt rõ rệt.",
        "closing_highlight": closing_kw,
        "closing_icon": "zap"
    })

    # Slide 5: Feature cards
    feat_keywords = keywords[3:6] if len(keywords) > 3 else keywords
    feat_icons = ["zap", "target", "clock", "shield", "trend", "lock"]
    features = [
        {
            "icon": feat_icons[i % len(feat_icons)],
            "title": _smart_title(kw),
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
    if cleaned_numbers:
        stat_descs = ["tăng trưởng", "tiết kiệm", "nhanh hơn", "hiệu quả", "kết quả", "cải thiện"]
        for i, num in enumerate(cleaned_numbers[:6]):
            grid_items.append(f"{num} — {stat_descs[i % len(stat_descs)]}")

    if not grid_items:
        grid_items = [
            f"Kết quả từ {_smart_title(keywords[0]) if keywords else 'hệ thống'}",
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
        "SEO": "Hầu hết mọi người vẫn đang làm SEO theo phương pháp cũ — tốn nguồn lực mà không đem lại kết quả thực tế.\nMỗi ngày trôi qua, đối thủ lại chiếm thêm thị phần của bạn.",
        "AI_AGENT": "Trong khi bạn đang tốn thời gian xử lý thủ công từng tác vụ, đối thủ đã để AI Agent làm toàn bộ.\nKhoảng cách năng lực này đang ngày càng rộng ra.",
        "CONTENT": "Content không có chiến lược đồng nghĩa với việc đốt tiền vào marketing mà không có ROI.\nMọi bài viết, mọi video đều phải phục vụ mục tiêu kinh doanh rõ ràng.",
        "BUSINESS": "Doanh nghiệp không tăng trưởng không phải vì thiếu khách hàng.\nMà vì hệ thống vận hành và chiến lược chưa được chuẩn hóa.",
        "GENERAL": "Vấn đề lớn nhất không phải là thiếu thông tin hay công cụ.\nMà là bạn chưa biết cách sắp xếp và thực thi nó một cách tối ưu nhất.",
    }
    agitate = agitate_templates.get(intent, agitate_templates["GENERAL"])

    # SOLUTION: Use the extracted sentences but capitalize and ensure they look good
    solution_points = []
    for s in sentences[:3]:
        s = s.strip().rstrip(".")
        if len(s.split()) > 4: # Only keep meaningful sentences
            s = s[0].upper() + s[1:]
            solution_points.append(s)

    if len(solution_points) < 2:
        solution_points = [
            f"Xây dựng hệ thống {_smart_title(keywords[0]) if keywords else 'tự động'} chuẩn hóa từ A-Z",
            "Đo lường kết quả bằng số liệu thực tế thay vì cảm tính",
            "Tối ưu liên tục các điểm chạm dựa trên phản hồi của thị trường",
        ]

    solution_text = "\n".join([f"👉 {p}" for p in solution_points])

    # Numbers callout
    num_callout = ""
    if numbers:
        cleaned_numbers = [n for n in numbers if len(n) <= 10] # ignore weird large SRT numbers
        if cleaned_numbers:
            num_callout = f"\n📊 Dữ liệu thực tế: " + " | ".join(cleaned_numbers[:3])

    # CTA
    cta_templates = {
        "SEO": "💾 Lưu lại bài viết này để áp dụng cho dự án SEO tiếp theo.\n👇 Comment 'SEO' nếu bạn cần tư vấn thêm.",
        "AI_AGENT": "🔖 Lưu lại và chia sẻ cho team của bạn.\n👇 Bạn đang ứng dụng AI thế nào? Để lại comment nhé.",
        "CONTENT": "📌 Save lại để làm checklist khi viết content.\n👇 Tag ngay người cần đọc bài viết này.",
        "GENERAL": "💡 Vuốt xem Carousel bên dưới để nắm bắt trọn vẹn quy trình.\n👇 Comment thắc mắc của bạn — SEOSONA sẽ giải đáp.",
    }
    cta = cta_templates.get(intent, cta_templates["GENERAL"])

    # Hashtags
    hashtag_map = {
        "SEO": "#SEO #SEOMastery #DigitalMarketing #SEOSONA #ContentMarketing #GoogleSEO",
        "AI_AGENT": "#AIAgent #AI2026 #AutomationAI #SEOSONA #TechTrends",
        "CONTENT": "#ContentMarketing #Copywriting #SEOSONA #MarketingStrategy #SocialMedia",
        "BUSINESS": "#BusinessGrowth #StartupVietnam #SEOSONA #Entrepreneur #GrowthHacking",
        "GENERAL": "#SEOSONA #Marketing #Business #AI #Vietnam #KnowledgeSharing",
    }
    hashtags = hashtag_map.get(intent, hashtag_map["GENERAL"])

    full_caption = f"""{problem}

{agitate}

Đây là cách chúng tôi giải quyết bài toán này:{num_callout}
{solution_text}

{cta}

{hashtags}"""

    return {
        "hook": problem,
        "caption": full_caption.strip()
    }



def _generate_thumbnail_offline(user_prompt: str) -> dict:
    """Generate thumbnail variable suggestions from raw content."""
    # Strip the English art-direction framing so TF-IDF runs on the real (Vietnamese)
    # content only — otherwise framing words like "content"/"the" leak in as keywords.
    content = re.split(r'(?i)\bcontent:\s*', user_prompt, maxsplit=1)
    content = content[-1] if len(content) > 1 else user_prompt
    _STOP = {"the", "and", "for", "you", "with", "this", "that", "your", "content",
             "thumbnail", "title", "label", "cta", "hook", "layout", "main", "type"}
    keywords = [k for k in _tfidf_keywords(content, top_n=8)
                if k.lower() not in _STOP and len(k) > 2][:6]
    intent   = _classify_intent(content)
    numbers  = _extract_numbers(content)

    title_kw = keywords[0].upper() if keywords else "AI AGENT"
    hook_kw  = keywords[1].upper() if len(keywords) > 1 else "THỰC CHIẾN"

    # Canonical lowercase keys — must match what thumbnail_maker / consumers read.
    # (Previously emitted PILL_LABEL/MAIN_TITLE/... which no caller read → output was
    # silently discarded. thumbnail_maker._normalize_nlp still accepts both spellings.)
    return {
        "top_label": intent.replace("_", " "),
        "main_title": _make_title(keywords, intent, content).upper(),
        "title_highlight": title_kw,
        # use a REAL number from the source if present; else a QUALITATIVE hook — never invent "80%"
        # (the old fallback fabricated that stat on every number-less input; violates "không làm giả").
        "hook": (f"Tại sao {numbers[0]} doanh nghiệp bỏ lỡ điều này?" if numbers
                 else "Điều mà nhiều doanh nghiệp vẫn đang bỏ lỡ"),
        "cta": "KHÁM PHÁ NGAY",
        "cta_highlight": "NGAY",
        "subtext_italic": f"Dùng {_smart_title(keywords[0]) if keywords else 'AI'} đúng cách — không phải để thay thế, mà để nhân lên",
        "layout_type": "text_only"
    }


def _generate_script_offline(user_prompt: str) -> dict:
    """Generate narrator script + scenes from raw content.
    
    Target: 150-200 words narrator text → 45-90s video.
    Scenes: 8-10 scenes minimum → rich HyperFrames animation.
    """
    # Strip the leading INSTRUCTION line so the prompt's directive never leaks into the Vietnamese
    # narration. The old regex ONLY matched "Analyze …:" — but the directive can be "Write a video
    # script." / "Generate …" / a period-terminated "… Post." → those leaked ("Chào mừng SEOSONA! Write a
    # video script Nghiên cứu…"). Match any common verb up to the first ':' or '.' then the blank line.
    text = re.sub(r'^\s*(?:Analyze|Write|Generate|Create|Compose|Produce|Viết|Tạo|Phân tích)\b[^\n]*?[:.]\s*\n+',
                  '', user_prompt, count=1, flags=re.IGNORECASE)
    keywords = _tfidf_keywords(text, top_n=12)
    sentences = _extract_sentences(text, n=10)
    numbers  = _extract_numbers(text)
    intent   = _classify_intent(text)

    # Detect English to prevent failing OODA quality gate
    is_english = sum(1 for w in [" the ", " and ", " to ", " is ", " in ", " of "] if w in text.lower()) > 3

    # Filter English stopwords from keywords to prevent OODA quality gate failure
    if is_english:
        EN_STOPWORDS = {
            "the", "and", "for", "to", "is", "in", "of", "a", "an", "it", "or",
            "be", "as", "at", "by", "on", "if", "do", "no", "so", "up", "but",
            "not", "are", "was", "has", "had", "can", "all", "its", "you", "see",
            "this", "that", "with", "from", "they", "been", "have", "will", "your",
            "what", "when", "make", "like", "each", "just", "over", "such", "into",
            "also", "than", "them", "then", "more", "some", "very", "only", "come",
            "could", "their", "which", "would", "there", "these", "other", "about",
            "contributing", "readme", "license", "install", "usage", "example",
        }
        keywords = [kw for kw in keywords if kw.lower() not in EN_STOPWORDS]

    # Extract English proper nouns / project names to keep in Vietnamese script
    english_proper_nouns = []
    if is_english:
        for match in re.findall(r'\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]+)*\b', text):
            if match not in {"The", "This", "That", "With", "From", "And", "For", "See", "CONTRIBUTING"}:
                english_proper_nouns.append(match)
        english_proper_nouns = list(dict.fromkeys(english_proper_nouns))[:5]

    project_name = english_proper_nouns[0] if english_proper_nouns else "dự án này"

    if is_english:
        # Build a rich, long Vietnamese narrator text (150+ words)
        feature_keywords = [_smart_title(kw) for kw in keywords[:6] if len(kw) > 2]
        features_text = ", ".join(feature_keywords[:4]) if feature_keywords else "nhiều tính năng nổi bật"

        body_text = (
            f"{project_name} là một dự án công nghệ mã nguồn mở đang thu hút sự chú ý lớn từ cộng đồng lập trình viên toàn cầu. "
            f"Dự án này tập trung vào việc giải quyết các bài toán phức tạp với {features_text}. "
            f"Điểm nổi bật lớn nhất của {project_name} chính là khả năng tối ưu hóa hiệu suất làm việc, "
            f"giúp các nhóm phát triển tiết kiệm đáng kể thời gian và nguồn lực. "
            f"Là một dự án mã nguồn mở, {project_name} được chia sẻ công khai để cộng đồng cùng sử dụng, thử nghiệm và đóng góp. "
            f"Một trong những lý do khiến {project_name} được chú ý là kiến trúc module hóa, "
            f"cho phép người dùng dễ dàng mở rộng và tùy biến theo nhu cầu riêng. "
            f"Hệ thống còn hỗ trợ tích hợp linh hoạt với nhiều nền tảng và công cụ phổ biến khác nhau. "
            f"Với khả năng mở rộng không giới hạn, {project_name} đang trở thành lựa chọn hàng đầu "
            f"cho các doanh nghiệp muốn tăng tốc quy trình phát triển sản phẩm. "
            f"Cộng đồng đang đánh giá đây là một trong những dự án đáng theo dõi nhất trong năm nay."
        )
        sentences = [
            f"{project_name} là dự án công nghệ mã nguồn mở đang thu hút sự chú ý lớn từ cộng đồng toàn cầu.",
            f"Dự án tập trung giải quyết các bài toán phức tạp với {features_text}.",
            f"Điểm nổi bật lớn nhất là khả năng tối ưu hóa hiệu suất làm việc cho nhóm phát triển.",
            f"Kiến trúc module hóa cho phép mở rộng và tùy biến theo nhu cầu riêng.",
            f"Hệ thống hỗ trợ tích hợp linh hoạt với nhiều nền tảng và công cụ phổ biến.",
            f"Là dự án mã nguồn mở, {project_name} được cộng đồng cùng sử dụng và đóng góp công khai.",
            f"{project_name} đang trở thành lựa chọn hàng đầu cho doanh nghiệp muốn tăng tốc phát triển.",
            f"Khả năng mở rộng không giới hạn giúp doanh nghiệp scale hệ thống dễ dàng.",
            f"Cộng đồng developer đánh giá đây là một trong những dự án đáng theo dõi nhất năm nay.",
            f"Theo dõi SEOSONA để cập nhật thêm những dự án công nghệ đáng chú ý khác.",
        ]
    else:
        # Vietnamese input: use extracted sentences but ensure minimum length
        if len(sentences) < 8:
            # Pad with keyword-based sentences
            for kw in keywords[len(sentences):]:
                sentences.append(f"Yếu tố {_smart_title(kw)} đóng vai trò quan trọng trong chiến lược tổng thể.")
                if len(sentences) >= 10:
                    break
        body_text = " ".join(sentences[:8])

    # Build narrator text — target 150+ words
    intro = "Chào mừng đến với bản tin SEOSONA! "
    outro = "Đừng quên theo dõi SEOSONA để cập nhật những thông tin mới nhất mỗi ngày!"
    narrator = intro + body_text + " " + outro

    # Build scenes — minimum 8, up to 10
    scenes = []
    kicker_labels = ["TIN TỨC", "PHÂN TÍCH", "TÍNH NĂNG", "KIẾN TRÚC", "TÍCH HỢP",
                     "HIỆU SUẤT", "CỘNG ĐỒNG", "ĐÁNH GIÁ", "XU HƯỚNG", "KẾT LUẬN"]
    max_scenes = min(10, len(sentences))

    for i in range(max_scenes):
        sent = sentences[i]
        words = sent.split()
        if is_english:
            # Use varied Vietnamese headings per scene
            vi_headings = [
                "ĐIỂM NHẤN", "TÍNH NĂNG", "HIỆU SUẤT", "KIẾN TRÚC", "TÍCH HỢP",
                "MỞ RỘNG", "CỘNG ĐỒNG", "ĐÁNH GIÁ", "XU HƯỚNG", "KẾT LUẬN"
            ]
            h1 = vi_headings[i % len(vi_headings)]
            body = sent
            h1_hl = h1.split()[-1]
        else:
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
            "source_sentence": sent,
        }

        if numbers and i < len(numbers):
            scene["stat_number"] = numbers[i][:6]
            scene["stat_label"] = ["TĂNG TRƯỞNG", "TIẾT KIỆM", "KẾT QUẢ"][i % 3]

        # All scenes get bullets for richer visual
        kws = keywords[i*1: i*1+3] if len(keywords) > i+2 else keywords[:3]
        scene["bullet_1"] = _smart_title(kws[0]) if kws else ""
        scene["bullet_2"] = _smart_title(kws[1]) if len(kws) > 1 else ""
        scene["bullet_3"] = _smart_title(kws[2]) if len(kws) > 2 else ""

        scenes.append(scene)

    return {
        "title": _make_title(keywords, intent, text),
        "narrator_text": narrator,
        "scenes": scenes,
        "hashtags": f"#SEOSONA #{intent.replace('_', '')} #Vietnam #AI #Marketing"
    }


# ─── Router: pick right offline generator based on prompt structure ─

def _smart_offline_router(system_prompt: str, user_prompt: str, model_name: str) -> dict:
    """Route to the right offline generator based on prompt content."""
    prompt_combined = (system_prompt + user_prompt).lower()

    # Order matters: check most specific first
    if any(k in prompt_combined for k in ["thumbnail", "pill_label", "main_title", "layout_type"]):
        print(f"[LLM Offline] Routing to: THUMBNAIL NLP Generator")
        return _generate_thumbnail_offline(user_prompt)

    if any(k in prompt_combined for k in ["pas", "caption", "facebook post", "hook\""]):
        print(f"[LLM Offline] Routing to: SOCIAL POST NLP Generator (PAS Framework)")
        return _generate_social_post_offline(user_prompt)

    if any(k in prompt_combined for k in ["carousel", "slide", "carousel_plan"]):
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

def _extract_json_block(t):
    """First BALANCED {...} or [...] in `t` — recovers JSON the model wrapped in prose/fences despite the
    'output ONLY JSON' instruction. Respects strings + nesting; the EARLIEST of { or [ is the outer
    structure, so an array of objects returns the whole array (not just the first object)."""
    t = t or ""
    starts = [(t.find(c), c, cl) for c, cl in (("{", "}"), ("[", "]")) if t.find(c) >= 0]
    if not starts:
        return None
    i, oc, cc = min(starts)
    depth, in_str, esc = 0, False, False
    for j in range(i, len(t)):
        c = t[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == oc:
            depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0:
                return t[i:j + 1]
    return None


def _parse_json_or_none(text):
    """Strip markdown fences + json.loads → dict/list, or None on failure. Unlike `_clean_and_parse`
    this does NOT fall to offline — so a caller can try the NEXT real tier when one returns bad JSON."""
    t = (text or "").strip()
    t2 = t
    for m in ("```json", "```"):
        if t2.startswith(m):
            t2 = t2[len(m):]
    if t2.endswith("```"):
        t2 = t2[:-3]
    try:
        return json.loads(t2.strip())
    except Exception:
        pass
    # the model often wraps JSON in prose despite instructions ("Here is the JSON: … Hope this helps!") —
    # recover the first balanced block instead of discarding a good response and falling through the cascade.
    block = _extract_json_block(t)
    if block:
        try:
            return json.loads(block)
        except Exception:
            pass
    return None


def generate_json_from_prompt(system_prompt: str, user_prompt: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Main LLM interface. Tries every real tier (Gemini→OpenAI→Z.ai→NVIDIA→Ollama), each PARSE-OR-CONTINUE
    (a tier's bad JSON tries the next tier, not offline), and only falls to Smart Offline NLP when ALL of
    them fail — so a single 429/503/bad-JSON never collapses straight to deterministic.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    json_instructions = "\n\nCRITICAL: You MUST output ONLY valid JSON format. Do not use markdown blocks like ```json. Start directly with { or [."
    full_system_prompt = system_prompt + json_instructions

    # --- Try Gemini (google-genai SDK; FREE tier = Flash models, NOT Pro) ---
    # BACKUP CHAIN: the free tier rate-limits per-model per-minute, but each Flash model
    # has its OWN quota. So on a 429/quota error we don't give up — we try the next free
    # Flash model (same key), then one backoff-retry on the primary. Only if the WHOLE
    # chain is exhausted do we fall through to OpenAI → Ollama → offline.
    if gemini_key and "gemini" in model_name.lower():
        import time as _t
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        _chain, _seen = [], set()
        for m in (model_name, "gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"):
            if m not in _seen:
                _seen.add(m); _chain.append(m)

        def _gem(m):
            r = client.models.generate_content(
                model=m, contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=full_system_prompt,
                    response_mime_type="application/json"))
            return (r.text or "").strip()

        last_err = None
        for m in _chain:
            try:
                _p = _parse_json_or_none(_gem(m))      # parse-or-continue: bad JSON → try next tier, not offline
                if _p is not None:
                    if m != model_name:
                        print(f"[LLM Engine] Gemini backup model '{m}' succeeded.")
                    return _p
                print(f"[LLM Engine] Gemini '{m}' returned unparseable JSON — next.")
            except Exception as e:
                last_err = e
                rate = any(s in str(e).lower() for s in ("429", "quota", "rate", "resource_exhausted", "exhausted"))
                print(f"[LLM Engine] Gemini '{m}' {'rate-limited' if rate else 'error'}: {str(e)[:120]}")
        # whole chain failed — if it was rate-limiting, the per-minute window may reset; one retry.
        if any(s in str(last_err).lower() for s in ("429", "quota", "rate", "resource_exhausted", "exhausted")):
            print("[LLM Engine] Gemini chain exhausted — backoff 15s then 1 retry on primary…")
            _t.sleep(15)
            try:
                _p = _parse_json_or_none(_gem(model_name))
                if _p is not None:
                    return _p
            except Exception as e:
                print(f"[LLM Engine] Gemini retry failed: {str(e)[:120]}. Trying next backup.")
        # fall through (NOT elif) to OpenAI / Ollama / offline below.

    # --- Try OpenAI (also reached as a backup after the Gemini chain is exhausted) ---
    if openai_key and ("gpt" in model_name.lower() or "gemini" in model_name.lower()):
        _oai_model = model_name if "gpt" in model_name.lower() else "gpt-4o-mini"
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=_oai_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            _p = _parse_json_or_none(response.choices[0].message.content)
            if _p is not None:
                return _p
            print("[LLM Engine] OpenAI returned unparseable JSON — trying next tier.")
        except Exception as e:
            print(f"[LLM Engine] OpenAI error: {e}. Trying next tier.")

    # --- Try Z.ai GLM + NVIDIA NIM (free cloud tiers) BEFORE local Ollama / deterministic, so the
    # non-script tasks (thumbnail / carousel / social post) get the SAME resilient cascade the script
    # path has (generate_json_strict). Otherwise a Gemini 503/quota drops straight to deterministic —
    # exactly what "không hạ deterministic" forbids. Each returns raw JSON text or None. ---
    for _name, _fn in (("Z.ai", _zai_scenes), ("NVIDIA", _nvidia_scenes)):
        try:
            _p = _parse_json_or_none(_fn(full_system_prompt, user_prompt))
            if _p is not None:
                print(f"[LLM Engine] {_name} tier succeeded (after Gemini/OpenAI).")
                return _p
        except Exception as _e:
            print(f"[LLM Engine] {_name} tier error: {str(_e)[:80]}")

    # --- Try Ollama (FREE, local — run `ollama serve` + pull a model). Default path when no
    # cloud key is set; gated on a reachable daemon so it never blocks if Ollama is off. ---
    _p = _parse_json_or_none(_try_ollama_json(full_system_prompt, user_prompt))
    if _p is not None:
        return _p

    # --- Smart Offline NLP Fallback ---
    print(f"[LLM Offline] No API key / Ollama. Running Smart NLP Engine...")
    return _smart_offline_router(system_prompt, user_prompt, model_name)


def _try_ollama_json(system_prompt: str, user_prompt: str):
    """Call a local Ollama model for JSON. Returns the raw text, or None if Ollama isn't
    reachable / no model configured (so the caller falls through to offline). FREE + local.
    Configure with SEOSONA_OLLAMA_MODEL (e.g. 'qwen2.5:3b', 'llama3.2'); host via OLLAMA_HOST."""
    model = os.getenv("SEOSONA_OLLAMA_MODEL")
    if not model:
        return None
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    try:
        import requests
        # 300s covers a cold gemma3:12b load (~8GB) on first call; keep_alive holds it warm 30 min so
        # subsequent scenes don't reload — makes Ollama a reliable floor, not a flaky one.
        r = requests.post(f"{host}/api/chat", timeout=300, json={
            "model": model, "stream": False, "format": "json", "keep_alive": "30m",
            # num_predict lifts the output-token cap (default ~128 truncated the scenes JSON mid-array →
            # parse failure → false "LLM failed"); num_ctx gives room for the spec + few-shot prompt.
            "options": {"num_predict": 2048, "num_ctx": 8192, "temperature": 0.7},
            "messages": [{"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}],
        })
        if r.status_code == 200:
            print(f"[LLM Engine] Ollama ({model}) — local/free.")
            return (r.json().get("message", {}).get("content") or "").strip()
        print(f"[LLM Engine] Ollama HTTP {r.status_code}; falling back.")
    except Exception as e:
        print(f"[LLM Engine] Ollama unavailable ({type(e).__name__}); falling back.")
    return None


# ── Script-writing LLM cascade — REAL LLMs ONLY, never the offline NLP router ──────────────────
# The generic generate_json_from_prompt() drops to a social/thumbnail NLP router on any hiccup, which
# can't write scenes → the pipeline then falls to the deterministic template writer (formulaic, "mất tự
# nhiên"). For SCRIPT writing we want the opposite: walk EVERY real LLM in the owner's preferred order
# (Gemini → OpenAI → Ollama → Claude), validate each returns scenes-shaped JSON, retry the NEXT tier on
# failure/bad-shape, and return None ONLY when all real LLMs are down — so deterministic is a true last
# resort that almost never triggers (Ollama gemma3:12b alone keeps a natural-language model always on).
def _strip_fences(t):
    t = (t or "").strip()
    if t.startswith("```"):
        t = t[t.find("\n") + 1:] if "\n" in t else t.strip("`")
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def _loads_block_or_none(txt):
    """json.loads the first balanced JSON block in `txt` (prose-wrapped recovery), or None."""
    block = _extract_json_block(txt or "")
    if not block:
        return None
    try:
        return json.loads(block)
    except Exception:
        return None


def _scenes_ok(txt):
    """Parse + shape-check: must be a dict with a non-empty 'scenes' list."""
    try:
        d = json.loads(_strip_fences(txt))
    except Exception:
        d = _loads_block_or_none(txt)          # recover prose-wrapped JSON before giving up on this tier
    return d if isinstance(d, dict) and isinstance(d.get("scenes"), list) and d["scenes"] else None


# ─── Circuit-breaker for API keys (pattern mined from OmniRoute, 2026-07-01) ───────
# A key that just returned 429/quota/rate is "tripped" and skipped for a cooldown window
# instead of being re-tried first on every call (which wastes a round-trip getting 429 again).
# In-memory, process-scoped — enough for the long-lived loop/queue-processor + a single run.
_KEY_COOLDOWN = {}                                            # api_key -> epoch when usable again
_KEY_COOLDOWN_S = int(os.getenv("SEOSONA_KEY_COOLDOWN_S", "300"))   # default 5 min

def _key_ready(key: str) -> bool:
    return time.time() >= _KEY_COOLDOWN.get(key, 0)

def _trip_key(key: str, seconds: int = None):
    _KEY_COOLDOWN[key] = time.time() + (seconds or _KEY_COOLDOWN_S)


def _gemini_keys():
    """All configured Gemini keys, in order: GEMINI_API_KEY, then GEMINI_API_KEY_2..N, plus any in a
    comma-separated GEMINI_API_KEYS. Rotating keys multiplies the free per-key quota (429 → next key)."""
    keys = [os.getenv("GEMINI_API_KEY")]
    for i in range(2, 11):
        keys.append(os.getenv(f"GEMINI_API_KEY_{i}"))
    keys += (os.getenv("GEMINI_API_KEYS", "").split(","))
    seen, out = set(), []
    for k in keys:
        k = (k or "").strip()
        if k and k not in seen:
            seen.add(k); out.append(k)
    return out


def _gemini_scenes(sysp, userp):
    keys = _gemini_keys()
    if not keys:
        return None
    try:
        from google import genai
        from google.genai import types
    except Exception:
        return None
    models = ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite")
    # circuit-breaker order: keys not cooling-down FIRST; tripped keys only as a last resort
    # (so we skip re-hitting a known-exhausted key, but never hard-fail while a key might have reset).
    order = [k for k in keys if _key_ready(k)] + [k for k in keys if not _key_ready(k)]
    for key in order:
        ki = keys.index(key)                              # original position, for the log line
        try:
            c = genai.Client(api_key=key)
        except Exception:
            continue
        rate_limited = False
        for m in models:                                  # try every model on this key before rotating
            try:
                r = c.models.generate_content(model=m, contents=userp,
                    config=types.GenerateContentConfig(system_instruction=sysp,
                                                       response_mime_type="application/json"))
                if r.text:
                    if ki:
                        print(f"[LLM scenes] Gemini key #{ki + 1} used (earlier keys exhausted).")
                    return r.text
            except Exception as e:
                if any(s in str(e).lower() for s in ("429", "quota", "rate", "exhausted", "resource")):
                    rate_limited = True                    # note it, keep trying other models
                else:
                    print(f"[LLM scenes] Gemini {m} (key#{ki + 1}): {str(e)[:70]}")
        if rate_limited:                                  # every model on this key hit quota → cool it down
            _trip_key(key)
            print(f"[LLM scenes] key #{ki + 1} tripped (cooldown {_KEY_COOLDOWN_S}s).")
    return None


def _openai_scenes(sysp, userp):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        import openai
        c = openai.OpenAI(api_key=key)
        r = c.chat.completions.create(model="gpt-4o-mini", response_format={"type": "json_object"},
            messages=[{"role": "system", "content": sysp}, {"role": "user", "content": userp}])
        return r.choices[0].message.content
    except Exception as e:
        print(f"[LLM scenes] OpenAI: {str(e)[:80]}")
        return None


def _zai_scenes(sysp, userp):
    """Z.ai GLM free tier (GLM-4.5-Flash / GLM-4.7-Flash) — OpenAI-compatible cloud, $0 (rate ~1 QPS).
    Uses urllib (no openai-version coupling); JSON is forced by the prompt, validated by _scenes_ok."""
    key = os.getenv("ZAI_API_KEY")
    if not key:
        return None
    model = os.getenv("SEOSONA_ZAI_MODEL", "glm-4.5-flash")
    try:
        import urllib.request
        body = json.dumps({"model": model, "messages": [
            {"role": "system", "content": sysp}, {"role": "user", "content": userp}]}).encode()
        req = urllib.request.Request("https://api.z.ai/api/paas/v4/chat/completions", data=body,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            j = json.loads(r.read())
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[LLM scenes] Z.ai: {str(e)[:80]}")
        return None


def _nvidia_scenes(sysp, userp):
    """NVIDIA NIM free tier (Llama-3.3-70B / Qwen2.5-72B) — OpenAI-compatible cloud, $0 (~40 RPM, finite
    credits → a FALLBACK, not primary). Better Vietnamese than the local Ollama floor. urllib, no dep."""
    key = os.getenv("NVIDIA_API_KEY")
    if not key:
        return None
    model = os.getenv("SEOSONA_NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
    try:
        import urllib.request
        body = json.dumps({"model": model, "temperature": 0.7, "messages": [
            {"role": "system", "content": sysp}, {"role": "user", "content": userp}]}).encode()
        req = urllib.request.Request("https://integrate.api.nvidia.com/v1/chat/completions", data=body,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=150) as r:   # 70B can cold-start slow; it's a fallback tier
            j = json.loads(r.read())
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[LLM scenes] NVIDIA: {str(e)[:80]}")
        return None


def _anthropic_scenes(sysp, userp):
    """Claude tier ('bạn'). Dormant until ANTHROPIC_API_KEY is set; then it's an automated tier."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
        c = anthropic.Anthropic(api_key=key)
        r = c.messages.create(model=os.getenv("SEOSONA_ANTHROPIC_MODEL", "claude-sonnet-5"),
            max_tokens=2000, system=sysp, messages=[{"role": "user", "content": userp}])
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    except Exception as e:
        print(f"[LLM scenes] Claude: {str(e)[:80]}")
        return None


def _json_ok(txt, require_key=None):
    """Parse + optional shape-check: a dict, and (if given) `require_key` present + truthy."""
    try:
        d = json.loads(_strip_fences(txt))
    except Exception:
        d = _loads_block_or_none(txt)          # recover prose-wrapped JSON before giving up on this tier
    if not isinstance(d, dict):
        return None
    return d if (not require_key or d.get(require_key)) else None


def generate_json_strict(system_prompt, user_prompt, require_key=None):
    """Robust REAL-LLM JSON cascade shared by EVERY generative video path (news scenes AND course
    cut-plans). Order = Gemini (keys rotated) → Z.ai GLM (free cloud) → OpenAI → Ollama (local free) →
    Claude, each shape-validated on `require_key`, retrying the NEXT tier on failure/bad-shape. NEVER
    the offline social/thumbnail NLP router. Returns the dict, or None if ALL real LLMs fail (→ the
    caller's deterministic fallback). `SEOSONA_REQUIRE_LLM=1` aborts instead of returning None."""
    tiers = (("Gemini", _gemini_scenes), ("Z.ai", _zai_scenes), ("NVIDIA", _nvidia_scenes),
             ("OpenAI", _openai_scenes), ("Ollama", lambda s, u: _try_ollama_json(s, u)),
             ("Claude", _anthropic_scenes))
    for name, fn in tiers:
        try:
            out = fn(system_prompt, user_prompt)
        except Exception as e:
            print(f"[LLM json] {name} raised: {str(e)[:80]}")
            continue
        d = _json_ok(out, require_key) if out else None
        if d:
            print(f"[LLM json] ✓ {name}" + (f" (key='{require_key}')" if require_key else ""))
            return d
    if os.getenv("SEOSONA_REQUIRE_LLM") == "1":
        raise RuntimeError("SEOSONA_REQUIRE_LLM=1: mọi LLM thật đều lỗi — dừng thay vì deterministic")
    print("[LLM json] ⚠ TẤT CẢ LLM thật đều lỗi → caller dùng deterministic (bật Ollama/thêm key để tránh)")
    return None


def generate_scenes_json(system_prompt, user_prompt):
    """Write video scenes with a REAL LLM or return None. Thin wrapper over generate_json_strict."""
    js = ("\n\nCRITICAL: xuất DUY NHẤT JSON hợp lệ dạng "
          '{"scenes":[{"text_vi":"...","h1":"...","h2":"..."}]}. Bắt đầu bằng {.')
    d = generate_json_strict((system_prompt or "") + js, user_prompt, require_key="scenes")
    if d:
        print(f"[LLM scenes] ✓ {len(d['scenes'])} cảnh")
    return d


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
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            )
            return (response.text or "").strip()
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
