import os
import shutil

def cleanup_temp_folders(root_dir):
    temp_folders = ['.temp', 'temp_frames']
    cleaned_bytes = 0
    
    for folder in temp_folders:
        path = os.path.join(root_dir, folder)
        if os.path.exists(path) and os.path.isdir(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    size = os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                        cleaned_bytes += size
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Failed to delete {item_path}. Reason: {e}")
                    
    return cleaned_bytes

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    freed = cleanup_temp_folders(root)
    print(f"Cleanup complete. Freed {freed / (1024*1024):.2f} MB of temp data.")
