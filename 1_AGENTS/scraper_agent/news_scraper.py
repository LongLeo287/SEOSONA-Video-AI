import os
import json
from typing import List, Dict, Optional
try:
    from scrapling.fetchers import StealthyFetcher
    HAS_SCRAPLING = True
except ImportError:
    HAS_SCRAPLING = False

class NewsScraperAgent:
    """
    Agent chuyên cào dữ liệu tự động, sử dụng Scrapling để vượt rào Anti-bot (Cloudflare, v.v.)
    Thu thập nội dung bài viết gốc để đưa cho SEO Writer Agent tạo kịch bản.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        
    def fetch_article(self, url: str, content_selector: str = "article, main, .content, .post-content") -> Optional[Dict]:
        """
        Lấy nội dung của một bài báo/blog.
        
        Args:
            url (str): Link bài báo
            content_selector (str): CSS selector để tìm phần thân bài viết.
            
        Returns:
            Dict chứa tiêu đề, nội dung, hoặc None nếu thất bại.
        """
        if not HAS_SCRAPLING:
            print("System log")
            return {"title": f"Mock Title for {url}", "content": "Mock content. Please install scrapling.", "url": url}
            
        print(f"System log")
        try:
            StealthyFetcher.adaptive = True
            
            page = StealthyFetcher.fetch(url, headless=self.headless, network_idle=True)
            
            title_node = page.css('h1::text')
            title = title_node.get() if title_node else "Unknown Title"
            
            content_nodes = page.css(content_selector)
            
            if not content_nodes:
                content_nodes = page.css('p')
                
            paragraphs = []
            for node in content_nodes:
                text = node.css('::text').getall()
                if text:
                    paragraphs.extend([t.strip() for t in text if t.strip()])
                    
            content = "\\n".join(paragraphs)
            
            return {
                "title": title.strip() if isinstance(title, str) else str(title),
                "content": content,
                "url": url
            }
            
        except Exception as e:
            print(f"System log")
            return None

if __name__ == "__main__":
    # Test
    agent = NewsScraperAgent()
    # url = "https://vnexpress.net/khoa-hoc"
    # data = agent.fetch_article(url)
    # print(data)
    pass
