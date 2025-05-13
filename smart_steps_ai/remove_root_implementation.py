import shutil
from pathlib import Path
import os

# Define paths
base_dir = Path(r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai")
root_impl = base_dir / "smart_steps_ai"
backup_dir = base_dir / "backup" / "root_implementation"

# Create backup directory if it doesn't exist
os.makedirs(backup_dir, exist_ok=True)

# 1. Backup the root implementation
print("Step 1: Backing up root implementation...")
if root_impl.exists() and root_impl.is_dir():
    # Create a directory in backup for all files
    for item in root_impl.glob("**/*"):
        if item.is_file():
            rel_path = item.relative_to(root_impl)
            dest_path = backup_dir / rel_path
            os.makedirs(dest_path.parent, exist_ok=True)
            shutil.copy2(item, dest_path)
            print(f"  Backed up: {rel_path}")
    print("Root implementation backed up successfully")
else:
    print("Root implementation directory not found, skipping backup")

# 2. Remove the root implementation
print("\nStep 2: Removing root implementation...")
if root_impl.exists() and root_impl.is_dir():
    try:
        shutil.rmtree(root_impl)
        print("Root implementation removed successfully")
    except Exception as e:
        print(f"Error removing root implementation: {e}")
        print("You may need to manually delete the directory:")
        print(f"  {root_impl}")
else:
    print("Root implementation directory not found, skipping removal")

print("\nCleanup completed. Steps to use the cleaned system:")
print("1. Run 'reinstall.bat' to reinstall the package from the src directory")
print("2. Run 'run_api_server.bat' to start the API server")
