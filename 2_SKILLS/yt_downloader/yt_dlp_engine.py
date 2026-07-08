"""
YouTube Downloader Skill — Uses yt-dlp for media ingestion.
Inherited from SEOSONA OS Skill: multimedia_production/video_audio_ingestion.
"""
import subprocess
import os

def download_audio(url, output_dir, archive_file=None):
    """
    Download audio only in m4a format (Whisper-friendly).
    From SEOSONA OS: yt-dlp --ignore-config -x --audio-format m4a
    """
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(title).120B [%(id)s].%(ext)s")

    cmd = [
        "yt-dlp", "--ignore-config", "--no-playlist",
        "--write-info-json",
        "--write-subs", "--write-auto-subs", "--sub-langs", "en,vi",
        "-x", "--audio-format", "m4a",
        "-o", output_template,
        url
    ]

    if archive_file:
        cmd.extend(["--download-archive", archive_file])

    print(f"[yt-dlp] Downloading audio from: {url}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("[yt-dlp] Download complete.")
            return True
        else:
            print(f"[yt-dlp] Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"[yt-dlp] Failed: {e}")
    return False

def download_video(url, output_dir, quality="best"):
    """
    Download full video for repurposing.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(title).120B [%(id)s].%(ext)s")

    cmd = [
        "yt-dlp", "--ignore-config", "--no-playlist",
        "-f", quality,
        "--write-info-json",
        "--write-subs", "--write-auto-subs", "--sub-langs", "en,vi",
        "-o", output_template,
        url
    ]

    print(f"[yt-dlp] Downloading video from: {url}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("[yt-dlp] Download complete.")
            return True
        else:
            print(f"[yt-dlp] Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"[yt-dlp] Failed: {e}")
    return False
