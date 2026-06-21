"""Extract key frames from the local LOOP reference video for analysis."""
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "7_ASSETS" / "404" / "LOOP.mp4"
OUT = ROOT / "8_WORKSPACE" / "Video_Frame_Analysis"
OUT.mkdir(parents=True, exist_ok=True)

if not VIDEO.exists():
    raise FileNotFoundError(f"Reference video not found: {VIDEO}")

result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(VIDEO)],
    capture_output=True,
    text=True,
    check=True,
)
info = json.loads(result.stdout)

duration = 0.0
for stream in info.get("streams", []):
    if stream.get("codec_type") == "video":
        duration = float(info["format"]["duration"])
        print(
            f"Video: {stream['width']}x{stream['height']}, "
            f"{duration:.1f}s, FPS: {stream.get('r_frame_rate', '?')}"
        )

timestamps = [0, 3, 8, 15, 20, 30, 36, 45, 55, 65, 71, 80, 90, 100]
timestamps = [t for t in timestamps if t < duration]

print(f"\nExtracting {len(timestamps)} key frames...")
for index, timestamp in enumerate(timestamps, start=1):
    out_path = OUT / f"frame_{index:02d}_t{timestamp:03d}s.png"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(timestamp),
            "-i",
            str(VIDEO),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out_path),
        ],
        capture_output=True,
        check=False,
    )
    status = out_path.name if out_path.exists() else "FAILED"
    print(f"  [{index:02d}] t={timestamp}s -> {status}")

print(f"\nDone. Frames saved to: {OUT}")
