import os
import json
try:
    import whisper
except ImportError:
    print("Warning: openai-whisper not installed. Subtitle generation will fail.")

def generate_word_level_data(audio_path, model_name="base"):
    """
    Generate word-level timestamp data using OpenAI Whisper.
    Returns a list of dicts: [{"word": "Hello", "start": 0.0, "end": 0.5}, ...]
    """
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path, language="vi", word_timestamps=True)
    
    word_level_data = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            word_info = {
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            }
            if word_info["word"]: # Filter empty words
                word_level_data.append(word_info)
            
    print(f"Extracted {len(word_level_data)} words with timestamps.")
    return word_level_data

def group_words_to_segments(word_level_data, max_words=7, max_duration=2.5):
    """
    VideoLingo-inspired: Groups word-level data into Netflix-style short segments.
    Breaks at punctuation automatically, or when reaching max words/duration.
    """
    segments = []
    current_segment = []
    
    def flush_segment():
        if not current_segment: return
        text = " ".join([w["word"] for w in current_segment])
        segments.append({
            "text": text,
            "start": current_segment[0]["start"],
            "end": current_segment[-1]["end"],
            "words": current_segment.copy()
        })
        current_segment.clear()

    punctuation_marks = ['.', ',', '?', '!', ';', ':', '...', '。', '，', '？', '！']
    
    for w in word_level_data:
        current_segment.append(w)
        
        # Check if we should break
        word_text = w["word"]
        duration = current_segment[-1]["end"] - current_segment[0]["start"]
        
        # break on punctuation at the END of the word (a real sentence/clause boundary), NOT anywhere in it:
        # a bare `'.' in word` split on VN numbers ("1.000.000" thousands-sep, "3.5" decimal, "10:30" time),
        # fragmenting number-heavy captions mid-phrase.
        has_punctuation = word_text.rstrip().endswith(tuple(punctuation_marks))
        too_long = len(current_segment) >= max_words
        too_slow = duration >= max_duration
        
        if has_punctuation or too_long or too_slow:
            flush_segment()
            
    flush_segment()
    return segments
