import os
import sys
import base64
import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def score_thumbnails(image_paths, brand="seosona"):
    # Simulated scoring for now, as Vision API might be expensive/slow
    # In a real production environment, you'd send base64 to OpenAI GPT-4o
    print(f"[Thumbnail Tester] Evaluating {len(image_paths)} variations for {brand}...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and len(openai_key) > 10:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            
            content = [{"type": "text", "text": "Score these thumbnails for YouTube CTR (0-100). Return JSON with a 'scores' array matching the image order, and 'winner_index'."}]
            for path in image_paths:
                base64_img = encode_image(path)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                })
                
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a YouTube CTR expert. Analyze these thumbnails."},
                    {"role": "user", "content": content}
                ]
            )
            result = json.loads(response.choices[0].message.content)
            winner_index = result.get("winner_index", 0)
            print(f"[Thumbnail Tester] AI selected variation {winner_index+1} as the winner!")
            return winner_index
        except Exception as e:
            print(f"[Thumbnail Tester] Vision API failed: {e}. Falling back to heuristic.")
    
    # Fallback heuristic: Randomly pick variation 2 (usually has the most balanced text)
    import random
    winner_index = random.randint(0, len(image_paths) - 1)
    print(f"[Thumbnail Tester] Offline fallback: Selected variation {winner_index+1}.")
    return winner_index

if __name__ == "__main__":
    pass
