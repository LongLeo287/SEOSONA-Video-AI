import os
import random
import requests
from urllib.parse import urlencode

# Proxy if needed
PROXIES = None 
# Disable TLS verify in case of proxy issues, but True is recommended
TLS_VERIFY = True

# We can set default keys or load from system_config.yaml in the future
API_KEYS = {
    "pexels": os.environ.get("PEXELS_API_KEY", ""),
    "pixabay": os.environ.get("PIXABAY_API_KEY", "")
}

def search_videos_pexels(search_term: str, min_duration: int = 5, orientation: str = "portrait") -> list:
    api_key = API_KEYS.get("pexels")
    if not api_key:
        print("PEXELS_API_KEY is not set.")
        return []
        
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    params = {"query": search_term, "per_page": 20, "orientation": orientation}
    query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
    
    try:
        r = requests.get(query_url, headers=headers, proxies=PROXIES, verify=TLS_VERIFY, timeout=30)
        response = r.json()
        video_items = []
        if "videos" not in response:
            return video_items
            
        for v in response["videos"]:
            duration = v["duration"]
            if duration < min_duration:
                continue
            # Get highest resolution matching orientation roughly
            # Pexels provides multiple video files
            for video in v["video_files"]:
                # Default selection logic (can be improved for exact resolutions)
                if (orientation == "portrait" and video["height"] > video["width"]) or \
                   (orientation == "landscape" and video["width"] > video["height"]):
                    video_items.append({
                        "provider": "pexels",
                        "url": video["link"],
                        "duration": duration
                    })
                    break
        return video_items
    except Exception as e:
        print(f"Error searching Pexels: {e}")
        return []

def save_video(video_url: str, save_dir: str) -> str:
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
        
    import hashlib
    url_hash = hashlib.md5(video_url.split("?")[0].encode('utf-8')).hexdigest()
    video_path = os.path.join(save_dir, f"vid_{url_hash}.mp4")
    
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        return video_path
        
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(video_url, headers=headers, proxies=PROXIES, verify=TLS_VERIFY, stream=True, timeout=60)
        with open(video_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return video_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return ""

def fetch_b_rolls(search_terms: list, total_duration_needed: float, save_dir: str, source: str = "pexels") -> list:
    """
    Tìm và tải B-roll theo thứ tự từ khóa kịch bản (Script-Order matching).
    Giúp video có hình ảnh sát nghĩa với nội dung từng đoạn.
    """
    print(f"Fetching B-rolls for terms: {search_terms}")
    search_func = search_videos_pexels if source == "pexels" else None # Add pixabay later
    if not search_func:
        return []
        
    candidate_groups = []
    valid_video_urls = set()
    found_duration = 0.0
    
    for term in search_terms:
        items = search_func(term)
        term_items = []
        for item in items:
            if item["url"] not in valid_video_urls:
                term_items.append(item)
                valid_video_urls.add(item["url"])
                found_duration += item["duration"]
        if term_items:
            candidate_groups.append((term, term_items))
            
    video_paths = []
    current_duration = 0.0
    candidate_index = 0
    
    while candidate_groups and current_duration <= total_duration_needed:
        has_candidate = False
        for term, items in candidate_groups:
            if candidate_index >= len(items):
                continue
            has_candidate = True
            item = items[candidate_index]
            print(f"Downloading B-roll for '{term}'...")
            path = save_video(item["url"], save_dir)
            if path:
                video_paths.append(path)
                current_duration += min(5.0, item["duration"]) # Assume max clip usage is 5s
                if current_duration >= total_duration_needed:
                    break
        if not has_candidate:
            break
        candidate_index += 1
        
    return video_paths

if __name__ == "__main__":
    # Test
    # os.environ["PEXELS_API_KEY"] = "YOUR_KEY"
    # paths = fetch_b_rolls(["technology", "artificial intelligence"], 10.0, "./test_brolls")
    # print(paths)
    pass
