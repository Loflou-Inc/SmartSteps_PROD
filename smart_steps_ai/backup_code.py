import os
import shutil
from pathlib import Path

# Define paths - use raw strings to handle spaces in paths
base_dir = Path(r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai")
root_impl = base_dir / "smart_steps_ai"
src_impl = base_dir / "src" / "smart_steps_ai"
backup_dir = base_dir / "backup"
root_backup = backup_dir / "root_implementation"
src_backup = backup_dir / "src_implementation"

# Create backup directories
os.makedirs(root_backup, exist_ok=True)
os.makedirs(src_backup, exist_ok=True)

# Backup root implementation
print(f"Backing up root implementation to {root_backup}")
for item in root_impl.glob("**/*"):
    if item.is_file():
        rel_path = item.relative_to(root_impl)
        dest_path = root_backup / rel_path
        os.makedirs(dest_path.parent, exist_ok=True)
        shutil.copy2(item, dest_path)
        print(f"Backed up: {rel_path}")

# Backup src implementation
print(f"Backing up src implementation to {src_backup}")
for item in src_impl.glob("**/*"):
    if item.is_file():
        rel_path = item.relative_to(src_impl)
        dest_path = src_backup / rel_path
        os.makedirs(dest_path.parent, exist_ok=True)
        shutil.copy2(item, dest_path)
        print(f"Backed up: {rel_path}")

print("Backup completed successfully!")
