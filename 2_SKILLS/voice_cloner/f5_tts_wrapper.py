import os
import sys

F5_TTS_REPO_PATH = os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "3_MEMORY", "raw_data", "repos", "F5-TTS", "src"
)
F5_TTS_REPO_PATH = os.path.abspath(F5_TTS_REPO_PATH)

if F5_TTS_REPO_PATH not in sys.path:
    sys.path.append(F5_TTS_REPO_PATH)

try:
    from f5_tts.api import F5TTS
    HAS_F5_TTS = True
except ImportError as e:
    HAS_F5_TTS = False
    print(f"[F5-TTS] Package not available: {e}")

class F5VoiceCloner:
    """
    F5-TTS adapter for SEOSONA Video voice cloning.
    Supports zero-shot voice cloning from a short approved reference sample.
    """
    
    def __init__(self, model_version: str = "F5TTS_v1_Base", device: str = None):
        """
        Initialize the F5-TTS engine.
        On the first run it may download the model or use the local cache.
        """
        self.model_version = model_version
        self.device = device
        self._engine = None
        
    def _initialize_engine(self):
        if not HAS_F5_TTS:
            raise RuntimeError("F5-TTS is not installed or could not be imported.")
        if self._engine is None:
            device_label = self.device or "auto"
            print(f"[F5-TTS] Initializing model={self.model_version}, device={device_label}")
            self._engine = F5TTS(model=self.model_version, device=self.device)
            
    def generate_voice(
        self, 
        text: str, 
        output_path: str, 
        ref_audio_path: str, 
        ref_text: str = ""
    ) -> str:
        """
        Generate speech from text using the supplied reference audio.
        
        Args:
            text (str): Text to synthesize.
            output_path (str): Output audio path (.wav).
            ref_audio_path (str): Reference voice audio path.
            ref_text (str): Transcript of the reference audio when available.
            
        Returns:
            str: Output path on success.
        """
        self._initialize_engine()
        
        if not os.path.exists(ref_audio_path):
            raise FileNotFoundError(f"Reference audio not found: {ref_audio_path}")
            
        print(f"[F5-TTS] Generating cloned voice: {output_path}")
        
        wav, sr, spec = self._engine.infer(
            ref_file=ref_audio_path,
            ref_text=ref_text,
            gen_text=text,
            file_wave=output_path,
            remove_silence=True
        )
        
        print(f"[F5-TTS] Saved: {output_path}")
        return output_path

if __name__ == "__main__":
    # Test
    # cloner = F5VoiceCloner()
    # cloner.generate_voice(
    #     output_path="test_f5_clone.wav",
    #     ref_audio_path="duong_dan_den_file_mau.wav",
    # )
    pass
