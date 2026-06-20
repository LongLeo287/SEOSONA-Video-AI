import os
import subprocess
from typing import List, Optional


class YouTubePublisherAgent:
    """
    Publishes videos to YouTube through the yutu CLI.

    Requirements:
    - yutu must be installed and available on PATH, or passed as yutu_bin.
    - OAuth credentials must already be configured for yutu.
    """

    def __init__(self, yutu_bin: str = "yutu"):
        self.yutu_bin = yutu_bin

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        category_id: str = "22",
        privacy: str = "private",
        thumbnail_path: Optional[str] = None,
    ) -> bool:
        """Upload a local video file to YouTube."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        tags_str = ",".join(tags) if tags else ""
        cmd = [
            self.yutu_bin,
            "video",
            "insert",
            "--file",
            video_path,
            "--title",
            title,
            "--categoryId",
            category_id,
            "--privacy",
            privacy,
        ]

        if description:
            cmd.extend(["--description", description])
        if tags_str:
            cmd.extend(["--tags", tags_str])
        if thumbnail_path and os.path.exists(thumbnail_path):
            cmd.extend(["--thumbnail", thumbnail_path])

        try:
            print(f"[YouTubePublisher] Running yutu upload for: {video_path}")
            result = subprocess.run(
                cmd,
                input="y\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0),
            )

            if result.returncode != 0:
                print(f"[YouTubePublisher] Upload failed with exit code {result.returncode}.")
                if result.stderr:
                    print(result.stderr.strip())
                return False

            print("[YouTubePublisher] Upload completed.")
            return True

        except FileNotFoundError:
            print(f"[YouTubePublisher] yutu binary not found: {self.yutu_bin}")
            return False
        except Exception as exc:
            print(f"[YouTubePublisher] Upload failed: {exc}")
            return False


if __name__ == "__main__":
    pass
