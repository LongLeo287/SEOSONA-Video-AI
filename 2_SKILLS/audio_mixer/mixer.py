import os
import subprocess

class AudioMixer:
    """
    Kỹ năng chuyên xử lý âm thanh: Trộn Voice (giọng đọc) với BGM (nhạc nền) và SFX.
    Sử dụng FFmpeg để đảm bảo hiệu suất tốt nhất.
    """
    
    def __init__(self):
        pass
        
    def mix_voice_and_bgm(
        self, 
        voice_path: str, 
        bgm_path: str, 
        output_path: str, 
        bgm_volume: float = 0.1,
        fade_out_duration: int = 3
    ) -> str:
        """
        Trộn giọng đọc chính với nhạc nền.
        - Nhạc nền sẽ tự động cắt cho vừa với độ dài giọng đọc.
        - Nhạc nền sẽ có hiệu ứng Fade Out ở cuối.
        - Âm lượng BGM được giảm xuống (mặc định 10%) để không lấn át giọng đọc.
        """
        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"System log")
            
        if not bgm_path or not os.path.exists(bgm_path):
            print("System log")
            return voice_path
            
        print(f"System log")
        
        # 1. -i voice_path -i bgm_path
        # 2. filter_complex: 
        
        v_path = voice_path.replace("\\", "/")
        b_path = bgm_path.replace("\\", "/")
        o_path = output_path.replace("\\", "/")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", v_path,
            "-stream_loop", "-1", "-i", b_path,
            "-filter_complex", 
            f"[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition={fade_out_duration}[aout]",
            "-map", "[aout]",
            "-c:a", "aac",
            "-b:a", "192k",
            o_path
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                creationflags=(getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
            )
            if result.returncode != 0:
                print(f"System log")
                return voice_path
            
            print(f"System log")
            return o_path
            
        except Exception as e:
            print(f"System log")
            return voice_path

if __name__ == "__main__":
    # Test
    # mixer = AudioMixer()
    # mixer.mix_voice_and_bgm("voice.wav", "music.mp3", "final_audio.wav")
    pass
