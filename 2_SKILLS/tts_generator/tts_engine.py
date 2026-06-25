"""
TTS Engine — Text-to-Speech using Microsoft Edge TTS.
Used as default engine for SEOSONA and fallback for CQA.
"""
import asyncio
import os

def generate_voice(text, output_path, voice="vi-VN-NamMinhNeural"):
    """
    Generate voice using edge-tts Python API.
    Returns output file path on success, None on failure.
    """
    try:
        import edge_tts
    except ImportError:
        print("[TTS Engine] edge-tts not installed. Run: pip install edge-tts")
        return None

    print(f"[TTS Engine] Generating voice ({voice})...")
    print(f"[TTS Engine] Text: {text[:80]}...")

    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    try:
        asyncio.run(_generate())
        size_kb = os.path.getsize(output_path) // 1024
        print(f"[TTS Engine] Saved: {os.path.basename(output_path)} ({size_kb}KB)")
        return output_path
    except Exception as e:
        print(f"[TTS Engine] Error: {e}")
        return None

def generate_voice_with_subtitles(text, output_path, voice="vi-VN-NamMinhNeural"):
    """
    Generate voice AND extract word-level timestamps for subtitle sync.
    Returns: (audio_path, subtitle_data)
    """
    try:
        import edge_tts
    except ImportError:
        print("[TTS Engine] edge-tts not installed.")
        return None, []

    subtitle_data = []

    async def _generate():
        # SINGLE request: write audio chunks AND collect word boundaries in one pass.
        # (The old code made two separate edge requests — stream() then save() — which
        # intermittently tripped edge-tts "No audio was received" throttling and yielded
        # 0 word boundaries. One pass is reliable and gives real timestamps.)
        communicate = edge_tts.Communicate(text, voice)
        subs = []
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk.get("offset", 0) / 10_000_000
                    duration = chunk.get("duration", 0) / 10_000_000
                    subs.append({
                        "word": chunk.get("text", ""),
                        "start": start,
                        "duration": duration if duration > 0 else 0.25,
                    })
        return subs

    # Retry transient edge-tts failures ("No audio was received" under throttling).
    last_err = None
    for attempt in range(1, 4):
        try:
            subtitle_data = asyncio.run(_generate())
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                raise RuntimeError("edge-tts produced no/too-little audio")
            size_kb = os.path.getsize(output_path) // 1024
            print(f"[TTS Engine] Audio: {os.path.basename(output_path)} ({size_kb}KB)")
            print(f"[TTS Engine] Subtitles: {len(subtitle_data)} word boundaries")
            return output_path, subtitle_data
        except Exception as e:
            last_err = e
            print(f"[TTS Engine] Attempt {attempt}/3 failed: {e}")
            import time
            time.sleep(1.5 * attempt)
    print(f"[TTS Engine] Error: {last_err}")
    return None, []

# Available Vietnamese voices
VOICES = {
    "seosona_male": "vi-VN-NamMinhNeural",    # Required male Vietnamese fallback
    "cqa_male": "vi-VN-NamMinhNeural",        # Energetic male fallback
}

if __name__ == "__main__":
    # Quick test
    test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "8_WORKSPACE")
    os.makedirs(test_dir, exist_ok=True)
    test_out = os.path.join(test_dir, "tts_test.mp3")
    generate_voice("Xin chao, day la he thong TTS cua SEOSONA Video Factory.", test_out)
