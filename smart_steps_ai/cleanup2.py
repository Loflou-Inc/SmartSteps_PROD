import os
import shutil

# Get base directory
root_dir = r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai"

# List of directories and files to keep
to_keep = [
    "working_components",
    "README_FIRST.md",
    "backup_before_cleanup",
    "cleanup.py",
    "cleanup2.py"
]

print("Starting final cleanup...")

# Delete everything except what we want to keep
for item in os.listdir(root_dir):
    if item not in to_keep:
        item_path = os.path.join(root_dir, item)
        print(f"Removing: {item_path}")
        
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            print(f"Error removing {item_path}: {e}")

print("Cleanup complete!")
