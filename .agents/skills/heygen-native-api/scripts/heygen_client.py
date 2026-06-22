import os
import sys
import json
import time
import requests
from dotenv import load_dotenv

def main():
    if len(sys.argv) < 3:
        print("Usage: python heygen_client.py <endpoint> <payload_file.json>")
        sys.exit(1)

    endpoint = sys.argv[1]
    payload_file = sys.argv[2]

    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))
    api_key = os.environ.get("HEYGEN_API_KEY")
    if not api_key:
        print("Error: HEYGEN_API_KEY not found in .env")
        sys.exit(1)

    # Read payload
    with open(payload_file, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    print(f"[*] Dispatching POST request to {endpoint}...")
    try:
        res = requests.post(endpoint, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()
        
        # Check v2 API response structure
        if "data" in data and "video_id" in data["data"]:
            video_id = data["data"]["video_id"]
        elif "data" in data and "translation_id" in data["data"]:
            video_id = data["data"]["translation_id"] # Polling logic works similarly
        else:
            print("[*] Operation successful, but no video_id returned. Response:")
            print(json.dumps(data, indent=2))
            sys.exit(0)
            
        print(f"[*] Task accepted. ID: {video_id}")
        
    except requests.exceptions.HTTPError as e:
        print(f"[!] API Error: {e.response.status_code} - {e.response.text}")
        sys.exit(1)

    # Polling loop
    print("[*] Polling for completion...")
    status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    
    while True:
        try:
            status_res = requests.get(status_url, headers=headers)
            status_res.raise_for_status()
            status_data = status_res.json()
            
            state = status_data.get("data", {}).get("status")
            if state == "completed":
                video_url = status_data["data"]["video_url"]
                print(f"[*] Render completed! Downloading from {video_url}...")
                
                # Download video
                vid_res = requests.get(video_url, stream=True)
                vid_res.raise_for_status()
                
                out_path = os.path.abspath(f"heygen_output_{video_id}.mp4")
                with open(out_path, 'wb') as vf:
                    for chunk in vid_res.iter_content(chunk_size=8192):
                        vf.write(chunk)
                
                print(f"[+] Download saved to: {out_path}")
                break
                
            elif state in ["failed", "error"]:
                err_msg = status_data.get("data", {}).get("error", "Unknown error")
                print(f"[!] Task failed on HeyGen side. Error: {err_msg}")
                sys.exit(1)
                
            else:
                print(f"[-] Status: {state}... waiting 10s")
                time.sleep(10)
                
        except requests.exceptions.HTTPError as e:
            print(f"[!] Polling Error: {e.response.status_code} - {e.response.text}")
            time.sleep(10) # Wait and retry instead of crashing immediately

if __name__ == "__main__":
    main()
