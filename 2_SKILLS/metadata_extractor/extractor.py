"""
Metadata Extractor Skill — Extracts technical metadata from video/audio files using ffprobe.
"""
import subprocess
import json

def extract_metadata(file_path):
    """
    Uses ffprobe to extract technical metadata from a media file.
    Returns dict with duration, resolution, codec, etc.
    """
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        file_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            fmt = data.get("format", {})
            streams = data.get("streams", [])

            video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

            metadata = {
                "filename": fmt.get("filename", ""),
                "duration": float(fmt.get("duration", 0)),
                "size_mb": round(int(fmt.get("size", 0)) / (1024 * 1024), 2),
                "format": fmt.get("format_long_name", ""),
            }

            if video_stream:
                metadata["video"] = {
                    "codec": video_stream.get("codec_name", ""),
                    "width": video_stream.get("width", 0),
                    "height": video_stream.get("height", 0),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                }

            if audio_stream:
                metadata["audio"] = {
                    "codec": audio_stream.get("codec_name", ""),
                    "sample_rate": audio_stream.get("sample_rate", ""),
                    "channels": audio_stream.get("channels", 0),
                }

            print(f"[Metadata] {metadata['filename']} — {metadata['duration']:.1f}s, {metadata['size_mb']}MB")
            return metadata
    except FileNotFoundError:
        print("[Metadata] ffprobe not found. Install ffmpeg and add to PATH.")
    except Exception as e:
        print(f"[Metadata] Error: {e}")

    return None
