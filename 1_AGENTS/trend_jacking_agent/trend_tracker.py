import os
import sys
import xml.etree.ElementTree as ET
import urllib.request
import subprocess

def fetch_latest_trend():
    print("[Trend Tracker] Fetching latest SEO news from SearchEngineLand...")
    url = 'https://searchengineland.com/feed'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        for item in root.findall('.//item'):
            title = item.find('title').text
            if title:
                print(f"[Trend Tracker] Found Hot Trend: {title}")
                return title
    except Exception as e:
        print(f"[Trend Tracker] Failed to fetch RSS: {e}")
        return "Google Update thuật toán cốt lõi mới nhất" # Fallback
        
def trigger_pipeline(trend_topic):
    print(f"\\n{'='*50}")
    print(f"🔥 KÍCH HOẠT AUTO-TREND PIPELINE: {trend_topic}")
    print(f"{'='*50}\\n")
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    router_script = os.path.join(root_dir, 'scripts', 'workflow_video_news.py')
    
    # Run the router. We assume workflow_video_news.py takes the topic as arguments
    # To prevent spamming heavy renders in dev, we will just simulate if --dry-run is passed
    if '--dry-run' in sys.argv:
        print("[Dry Run] Would execute:")
        print(f"python {router_script} \\"{trend_topic}\\"")
    else:
        subprocess.run([sys.executable, router_script, trend_topic], cwd=root_dir)

if __name__ == '__main__':
    hot_topic = fetch_latest_trend()
    trigger_pipeline(hot_topic)
