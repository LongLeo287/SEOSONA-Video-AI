from .whisper_engine import generate_word_level_data, group_words_to_segments


def transcribe_audio(audio_path, model_name="base"):
    return generate_word_level_data(audio_path, model_name=model_name)
