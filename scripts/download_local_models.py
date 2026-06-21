import os
import sys
from huggingface_hub import hf_hub_download, snapshot_download

def setup_directories():
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    models_dir = os.path.join(workspace_dir, "7_ASSETS", "models")
    kokoro_dir = os.path.join(models_dir, "kokoro")
    llm_dir = os.path.join(models_dir, "llm")

    os.makedirs(kokoro_dir, exist_ok=True)
    os.makedirs(llm_dir, exist_ok=True)
    return models_dir, kokoro_dir, llm_dir

def download_kokoro(kokoro_dir):
    print("🚀 Đang kéo model Kokoro-82M từ HuggingFace (Chạy Local TTS)...")
    repo_id = "hexgrad/Kokoro-82M"

    # Download weights
    try:
        pth_path = hf_hub_download(repo_id=repo_id, filename="kokoro-v1_0.pth", local_dir=kokoro_dir)
        print(f"✅ Đã tải xong Model Weights: {pth_path}")

        # Download config
        json_path = hf_hub_download(repo_id=repo_id, filename="config.json", local_dir=kokoro_dir)
        print(f"✅ Đã tải xong Config: {json_path}")

        # Download voices
        voices_dir = os.path.join(kokoro_dir, "voices")
        os.makedirs(voices_dir, exist_ok=True)
        print("Đang tải các giọng (Voice packs)...")
        # Download a default voice (e.g., af_bella.pt)
        voice_path = hf_hub_download(repo_id=repo_id, filename="voices/af_bella.pt", local_dir=kokoro_dir)
        print(f"✅ Đã tải xong Default Voice: {voice_path}")

    except Exception as e:
        print(f"❌ Lỗi khi tải Kokoro: {e}")

def setup_nvidia_nim():
    print("\n🚀 Cấu hình Nvidia NIM (Local LLM via API)...")
    print("Nvidia NIM đã hỗ trợ API tương thích OpenAI. Hãy thêm cấu hình sau vào .env của bạn:")
    print("NVIDIA_NIM_API_KEY=nvapi-...")
    print("Và engine local_llm_engine.py sẽ tự động sử dụng nó để xử lý kịch bản.\n")

if __name__ == "__main__":
    models_dir, kokoro_dir, llm_dir = setup_directories()
    download_kokoro(kokoro_dir)
    setup_nvidia_nim()
    print("Hoàn tất thiết lập Local Models!")
