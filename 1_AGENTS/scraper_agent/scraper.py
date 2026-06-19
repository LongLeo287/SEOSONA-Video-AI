"""
Scraper Agent — Extracts content from web articles for script writing.
Inherits Anti-Scraping & Data Engineering principles from SEOSONA OS (data-scraper.md).
"""
import requests
from bs4 import BeautifulSoup
import random
import time

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
]

def scrape_article(url, timeout=20, max_retries=3):
    """
    Scrapes a web article and extracts structured content.
    Includes rate-limit avoidance, UA rotation, and smart noise filtering.
    """
    print(f"[Scraper Agent] Scraping target: {url}")
    
    for attempt in range(max_retries):
        try:
            # 1. Anti-Scraping Headers Rotation
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Throttling
            if attempt > 0:
                delay = random.uniform(2.0, 5.0) * attempt
                print(f"[Scraper Agent] Retry {attempt}/{max_retries}. Sleeping for {delay:.1f}s...")
                time.sleep(delay)

            response = requests.get(url, headers=headers, timeout=timeout)
            
            # Xử lý các mã lỗi Anti-bot phổ biến
            if response.status_code in [403, 429]:
                print(f"[Scraper Agent] Anti-bot triggered (Status {response.status_code}).")
                continue
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 2. Smart Noise Decomposition
            noise_selectors = [
                'script', 'style', 'nav', 'footer', 'header', 'aside', 
                '.ad', '.advertisement', '#cookie-banner', '.popup', '.sidebar'
            ]
            for selector in noise_selectors:
                for tag in soup.select(selector):
                    tag.decompose()
            for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()

            # 3. Extraction
            title_tag = soup.find('h1')
            title = title_tag.get_text().strip() if title_tag else soup.title.get_text().strip() if soup.title else "Untitled"

            headings = []
            for h in soup.find_all(['h2', 'h3']):
                text = h.get_text().strip()
                if text and len(text) > 5:
                    headings.append(text)

            paragraphs = soup.find_all('p')
            body_text = '\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])

            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')

            result = {
                "url": url,
                "title": title,
                "meta_description": meta_desc,
                "key_points": headings[:15],
                "content": body_text[:8000],  # Lấy nhiều content hơn
                "word_count": len(body_text.split())
            }

            print(f"[Scraper Agent] ✓ Extracted: '{title}' ({result['word_count']} words)")
            return result

        except requests.exceptions.Timeout:
            print(f"[Scraper Agent] ✗ Timeout after {timeout}s")
        except requests.exceptions.RequestException as e:
            print(f"[Scraper Agent] ✗ Request failed: {e}")
            
    print(f"[Scraper Agent] ✗ Failed to scrape {url} after {max_retries} attempts.")
    return None

def scrape_multiple(urls):
    results = []
    for url in urls:
        result = scrape_article(url)
        if result:
            results.append(result)
        time.sleep(random.uniform(1.0, 3.0)) # Polite scraping delay between URLs
    print(f"[Scraper Agent] Scraped {len(results)}/{len(urls)} articles successfully.")
    return results
