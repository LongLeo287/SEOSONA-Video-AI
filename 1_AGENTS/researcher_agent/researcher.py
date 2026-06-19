"""
Researcher Agent — Finds trending topics and suggests video ideas.
"""
import requests
from bs4 import BeautifulSoup

def search_trending_topics(niche="SEO", num_results=5):
    """
    Searches Google Trends-style topics for video ideas.
    In production, this would use Google Trends API or scrape news sites.
    """
    print(f"[Researcher] Searching trending topics for niche: {niche}...")

    # Simulated trending topics (in production: scrape from news/trends)
    trending = {
        "SEO": [
            "Google Algorithm Update tháng 6/2026",
            "AI Overviews thay đổi cách làm SEO",
            "E-E-A-T mới nhất: Google đánh giá uy tín tác giả",
            "Core Web Vitals 2026: Interaction to Next Paint",
            "Zero-Click Search tăng 65%: SEO cần thay đổi gì?"
        ],
        "AI": [
            "Claude 4.6 Opus vs GPT-5: So sánh chi tiết",
            "AI Agent tự động hóa quy trình doanh nghiệp",
            "Veo 3.1: Google ra mắt AI tạo video chất lượng điện ảnh",
            "MCP Protocol: Chuẩn mới cho AI Agents",
            "AI trong SEO: Cơ hội hay mối đe dọa?"
        ],
        "Marketing": [
            "Content Marketing 2026: Xu hướng mới",
            "Short-form Video tiếp tục thống trị",
            "Email Marketing vẫn cho ROI cao nhất",
            "Influencer Marketing B2B đang tăng mạnh",
            "Social Commerce: Bán hàng trực tiếp trên mạng xã hội"
        ]
    }

    results = trending.get(niche, trending["SEO"])[:num_results]
    print(f"[Researcher] Found {len(results)} trending topics.")
    return results

def scrape_article_for_script(url):
    """
    Scrapes a web article and extracts key points for script writing.
    """
    print(f"[Researcher] Scraping article: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else "Untitled"

        # Extract paragraphs
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])

        # Extract headings for key points
        headings = [h.get_text().strip() for h in soup.find_all(['h2', 'h3']) if h.get_text().strip()]

        return {
            "title": title_text,
            "key_points": headings[:7],
            "full_text": content[:3000],
            "word_count": len(content.split())
        }
    except Exception as e:
        print(f"[Researcher] Scrape failed: {e}")
        return None

def generate_video_ideas_from_keywords(keywords):
    """
    Converts SEO keywords into video topic ideas.
    From SEOSONA OS video_content SKILL: Keyword Research → Video Topics.
    """
    ideas = []
    for kw in keywords:
        ideas.append(f"Hướng dẫn {kw} từ A-Z cho người mới")
        ideas.append(f"{kw}: 5 Sai lầm phổ biến nhất (và cách sửa)")
        ideas.append(f"So sánh: {kw} miễn phí vs trả phí — Cái nào tốt hơn?")
    return ideas
