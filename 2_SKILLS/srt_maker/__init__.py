from .whisper_engine import group_words_to_segments
from .asr_router import transcribe_words

__all__ = ["transcribe_words", "group_words_to_segments", "transcribe_audio"]


def transcribe_audio(audio_path, model_name="base"):
    # Backward-compatible shim → the single ASR path (PhoWhisper-large via faster-whisper).
    return transcribe_words(audio_path)
