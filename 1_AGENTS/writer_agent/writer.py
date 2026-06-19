"""
Writer Agent — Generates video scripts using LLM with system prompt.
"""
import os

def load_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_script(topic, brand_profile, duration_seconds=60):
    """
    Builds the full LLM prompt by combining system_prompt.txt with topic and brand context.
    In production: sends this to OpenAI/Claude API.
    """
    system_prompt = load_system_prompt()
    brand_tone = brand_profile.get('brand_tone', 'Professional')
    target = brand_profile.get('target_audience', 'Target Audience')

    full_prompt = system_prompt.replace("{TOPIC}", topic)
    full_prompt += f"\nStyle: {brand_tone}"
    full_prompt += f"\nAudience: {target}"
    full_prompt += f"\nTarget duration: {duration_seconds} seconds"

    print(f"[Writer Agent] Script prompt built for topic: '{topic}'")
    print(f"[Writer Agent] Brand tone: {brand_tone}")
    print(f"[Writer Agent] Target audience: {target}")

    # Simulated script output (in production: call LLM API)
    script = f"""[HOOK]
Bạn có biết 90% người làm {topic} đều mắc sai lầm nghiêm trọng này?

[BODY]
Hôm nay tôi sẽ chia sẻ với bạn 3 bí quyết quan trọng nhất về {topic}.

Bí quyết số 1: Phân tích dữ liệu trước khi hành động.
Bí quyết số 2: Tập trung vào chất lượng thay vì số lượng.
Bí quyết số 3: Liên tục cập nhật xu hướng mới nhất.

[CALL TO ACTION]
Theo dõi kênh để nhận thêm kiến thức mỗi tuần. Comment cho tôi biết bạn thấy tip nào hữu ích nhất!
"""

    return {"prompt": full_prompt, "script": script, "word_count": len(script.split())}
