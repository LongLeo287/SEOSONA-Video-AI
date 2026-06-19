import requests
import random

def get_pexels_video(query, api_key, output_path, orientation="portrait"):
    """
    Fetch a vertical stock video from Pexels API
    """
    url = f"https://api.pexels.com/videos/search?query={query}&orientation={orientation}&size=medium&per_page=15"
    headers = {"Authorization": api_key}
    
    print(f"Searching Pexels for: {query}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("videos"):
                video = random.choice(data["videos"])
                video_files = video["video_files"]
                best_file = max(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0))
                link = best_file["link"]
                
                print(f"Downloading video from {link}...")
                video_data = requests.get(link).content
                with open(output_path, "wb") as f:
                    f.write(video_data)
                print(f"Video saved to {output_path}")
                return output_path
    except Exception as e:
        print(f"Pexels fetch failed: {e}")
        
    print("Failed to fetch from Pexels. Returning None.")
    return None
