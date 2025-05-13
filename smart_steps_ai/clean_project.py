import os
import shutil
from pathlib import Path

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
else:
    print("Root implementation directory not found, skipping removal")

# 3. Replace setup.py with the new version
print("\nStep 3: Updating setup.py...")
setup_new = base_dir / "setup.py.new"
setup_old = base_dir / "setup.py"
setup_backup = backup_dir / "setup.py"

if setup_old.exists() and setup_old.is_file():
    # Backup the original setup.py
    shutil.copy2(setup_old, setup_backup)
    print("Original setup.py backed up")
    
    # Replace with new setup.py
    if setup_new.exists() and setup_new.is_file():
        shutil.copy2(setup_new, setup_old)
        print("setup.py updated successfully")
    else:
        print("New setup.py not found, skipping update")
else:
    print("Original setup.py not found, skipping update")

# 4. Replace run_api_server.bat with the new version
print("\nStep 4: Updating run_api_server.bat...")
bat_new = base_dir / "run_api_server.bat.new"
bat_old = base_dir / "run_api_server.bat"
bat_backup = backup_dir / "run_api_server.bat"

if bat_old.exists() and bat_old.is_file():
    # Backup the original bat file
    shutil.copy2(bat_old, bat_backup)
    print("Original run_api_server.bat backed up")
    
    # Replace with new bat file
    if bat_new.exists() and bat_new.is_file():
        shutil.copy2(bat_new, bat_old)
        print("run_api_server.bat updated successfully")
    else:
        print("New run_api_server.bat not found, skipping update")
else:
    print("Original run_api_server.bat not found, skipping update")

# 5. Create a cleanup script for the venv
print("\nStep 5: Creating reinstall script...")
reinstall_script = base_dir / "reinstall.bat"
with open(reinstall_script, 'w') as f:
    f.write('@echo off\n')
    f.write('echo Reinstalling Smart Steps AI...\n')
    f.write('echo.\n')
    f.write('echo Deactivating virtual environment...\n')
    f.write('call venv\\Scripts\\deactivate.bat\n')
    f.write('echo.\n')
    f.write('echo Removing old installation...\n')
    f.write('pip uninstall -y smart_steps_ai\n')
    f.write('echo.\n')
    f.write('echo Installing in development mode...\n')
    f.write('pip install -e .\n')
    f.write('echo.\n')
    f.write('echo Installation complete!\n')
    f.write('echo.\n')
    f.write('echo You can now run the API server with run_api_server.bat\n')
print(f"Created reinstall script at {reinstall_script}")

print("\nCleanup complete! Run the following steps to complete the process:")
print("1. Run 'reinstall.bat' to reinstall the package from the src directory")
print("2. Run 'run_api_server.bat' to start the API server")
