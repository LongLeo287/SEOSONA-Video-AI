"""
Publisher Agent — Prepares publishing metadata for each platform.
"""
import os
import json

def prepare_publish_package(project_dir, project_name, brand_profile, platform="youtube"):
    """
    Creates a publish_ready.json inside the project folder
    containing all metadata needed to publish the video.
    """
    platforms_config = {
        "youtube": {
            "video_file": f"{project_name}.mp4",
            "thumbnail_file": f"Thumbnail/{project_name}_Thumbnail.jpg",
            "srt_file": f"SRT/{project_name}.srt",
            "aspect_ratio": "16:9",
            "max_duration": None,
            "required_fields": ["title", "description", "tags", "thumbnail"]
        },
        "youtube_shorts": {
            "video_file": f"{project_name}.mp4",
            "thumbnail_file": f"Thumbnail/{project_name}_Thumbnail.jpg",
            "aspect_ratio": "9:16",
            "max_duration": 60,
            "required_fields": ["title", "description", "hashtags"]
        },
        "tiktok": {
            "video_file": f"{project_name}.mp4",
            "thumbnail_file": f"Thumbnail/{project_name}_Thumbnail.jpg",
            "aspect_ratio": "9:16",
            "max_duration": 60,
            "required_fields": ["caption", "hashtags"]
        },
        "reels": {
            "video_file": f"{project_name}.mp4",
            "thumbnail_file": f"Thumbnail/{project_name}_Thumbnail.jpg",
            "aspect_ratio": "9:16",
            "max_duration": 90,
            "required_fields": ["caption", "hashtags"]
        }
    }

    platform_spec = platforms_config.get(platform, platforms_config["youtube"])

    package = {
        "project_name": project_name,
        "brand": brand_profile.get('description', ''),
        "platform": platform,
        "files": {
            "video": os.path.join(project_dir, platform_spec["video_file"]),
            "thumbnail": os.path.join(project_dir, platform_spec["thumbnail_file"]),
        },
        "spec": platform_spec,
        "status": "ready_for_review"
    }

    # Check if files exist
    for key, path in package["files"].items():
        if not os.path.exists(path):
            package["status"] = "missing_files"
            print(f"[Publisher] WARNING: {key} file not found at {path}")

    # Save package
    output_path = os.path.join(project_dir, f"publish_ready_{platform}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(package, f, ensure_ascii=False, indent=4)

    print(f"[Publisher] Package for {platform.upper()} saved to {output_path}")
    return package
