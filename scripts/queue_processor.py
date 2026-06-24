import os
import sys
import yaml
import shutil
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = ROOT_DIR / "0_INPUT_INBOX"
QUEUE_FILE = INBOX_DIR / "production_queue.yaml"
PENDING_DIR = INBOX_DIR / "pending_files"
DONE_DIR = INBOX_DIR / "done"

# Ensure directories exist
PENDING_DIR.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)

# Command mapping
COMMAND_MAP = {
    "news_videos": ["npm", "run", "video:news", "--"],
    "course_videos": ["npm", "run", "video:course", "--"],
    "carousels": ["npm", "run", "post:image", "--"],
    "thumbnails": ["npm", "run", "thumbnail:create", "--"]
}

def load_queue():
    if not QUEUE_FILE.exists():
        print(f"[-] Cannot find queue file: {QUEUE_FILE}")
        return None
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_queue(queue_data):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        yaml.dump(queue_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def run_command(command_prefix, input_val):
    cmd = command_prefix + [input_val]
    # For Windows, we might need shell=True for npm
    print(f"[*] Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT_DIR, shell=(os.name == 'nt'))
    return result.returncode == 0

def process_queue():
    print("=" * 50)
    print("🚀 SEOSONA VIDEO - INBOX QUEUE PROCESSOR 🚀")
    print("=" * 50)

    queue_data = load_queue()
    if not queue_data:
        return

    processed_count = 0
    
    # Iterate through each category
    for category, cmd_prefix in COMMAND_MAP.items():
        if category not in queue_data or not queue_data[category]:
            continue
            
        items = queue_data[category]
        remaining_items = []
        
        for item in items:
            # Skip empty entries
            if not item or str(item).strip() == "":
                remaining_items.append(item)
                continue
                
            input_str = str(item).strip()
            
            # Check if it's a local file in pending_files
            is_local_file = False
            file_path = None
            
            if input_str.startswith("pending_files/") or input_str.startswith("pending_files\\"):
                file_name = input_str.split("/")[-1].split("\\")[-1]
                file_path = PENDING_DIR / file_name
                if file_path.exists():
                    is_local_file = True
                    input_str = str(file_path.absolute())
                else:
                    print(f"[!] Warning: File not found {file_path}")
                    remaining_items.append(item)
                    continue

            print(f"\n[+] Processing [{category}]: {item}")
            
            # Execute command
            success = run_command(cmd_prefix, input_str)
            
            if success:
                print(f"[✓] Successfully processed: {item}")
                processed_count += 1
                
                # Move file to done if it's a local file
                if is_local_file and file_path and file_path.exists():
                    try:
                        done_path = DONE_DIR / file_path.name
                        # If file already exists in done, remove it first
                        if done_path.exists():
                            done_path.unlink()
                        shutil.move(str(file_path), str(done_path))
                        print(f"    -> Moved file to done: {done_path.name}")
                    except Exception as e:
                        print(f"    -> [!] Could not move file: {e}")
                
                # We do NOT add this item to remaining_items (it gets removed from queue)
            else:
                print(f"[x] Failed to process: {item}. Keeping in queue.")
                remaining_items.append(item)
                
        # Update queue with only remaining items
        queue_data[category] = remaining_items
        
    # Save updated queue back to file
    save_queue(queue_data)
    
    print("\n" + "=" * 50)
    print(f"✅ Processing Complete! Total processed: {processed_count}")
    print("=" * 50)

if __name__ == "__main__":
    process_queue()
