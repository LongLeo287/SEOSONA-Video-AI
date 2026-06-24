from .whisper_engine import generate_word_level_data, group_words_to_segments
from .asr_router import transcribe_words

__all__ = ["transcribe_words", "generate_word_level_data", "group_words_to_segments", "transcribe_audio"]


def transcribe_audio(audio_path, model_name="base"):
    # Backward-compatible shim → now goes through the switchable ASR router
    # (PhoWhisper primary, faster-whisper / openai-whisper backups).
    return transcribe_words(audio_path)
