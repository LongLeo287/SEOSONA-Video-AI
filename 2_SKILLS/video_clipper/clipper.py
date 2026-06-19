import os
from moviepy.editor import VideoFileClip

def crop_to_vertical(clip):
    """
    Takes a 16:9 clip and crops it to 9:16 vertical format (centering the action).
    """
    target_ratio = 9 / 16.0
    current_ratio = clip.w / clip.h
    
    if current_ratio > target_ratio:
        # It's wider (like 16:9), so we crop the sides
        new_w = int(clip.h * target_ratio)
        x_center = clip.w / 2
        clip = clip.crop(x_center=x_center, y_center=clip.h/2, width=new_w, height=clip.h)
    
    # Resize to standard TikTok size
    clip = clip.resize((1080, 1920))
    return clip

def cut_and_format_short(input_video_path, start_time, end_time, output_path):
    """
    Slices a long video and converts it into a 9:16 vertical short.
    """
    print(f"Clipping video from {start_time}s to {end_time}s...")
    try:
        with VideoFileClip(input_video_path) as video:
            subclip = video.subclip(start_time, end_time)
            
            # Auto-crop to 9:16
            vertical_clip = crop_to_vertical(subclip)
            
            print(f"Exporting Short Video to {output_path}...")
            vertical_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            return output_path
            
    except Exception as e:
        print(f"Error cutting video: {e}")
        return None
