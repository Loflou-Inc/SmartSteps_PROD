import os
import shutil
import sys

def delete_file_or_directory(path):
    """Delete a file or directory recursively."""
    try:
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return
        
        if os.path.isdir(path):
            print(f"Deleting directory: {path}")
            shutil.rmtree(path)
            print(f"Directory deleted: {path}")
        else:
            print(f"Deleting file: {path}")
            os.remove(path)
            print(f"File deleted: {path}")
    except Exception as e:
        print(f"Error with {path}: {str(e)}")

# Get base directory
root_dir = r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai"

# Paths to keep
to_keep = [
    os.path.join(root_dir, "working_components"),
    os.path.join(root_dir, "README_FIRST.md"),
    os.path.join(root_dir, "backup_before_cleanup"),
    os.path.join(root_dir, "cleanup.py")  # Keep this script
]

# Function to check if a path should be kept
def should_keep(check_path):
    return any(check_path.startswith(keep_path) for keep_path in to_keep)

print("Starting cleanup...")
print("Keeping:", ", ".join(to_keep))

# Delete everything except what we want to keep
for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    
    # Skip the items we want to keep
    if should_keep(item_path):
        print(f"Keeping: {item_path}")
        continue
    
    print(f"Processing: {item_path}")
    delete_file_or_directory(item_path)

print("Cleanup complete!")
