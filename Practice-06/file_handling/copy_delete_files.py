# This script demonstrates how to copy files,
# create a backup, and delete files safely.

import os
import shutil
from pathlib import Path

source_file = Path("original.txt")
copy_file = Path("copied.txt")
backup_dir = Path("backup")
backup_file = backup_dir / "original_backup.txt"

# Create the source file with sample content
with open(source_file, "w", encoding="utf-8") as file:
    file.write("This is the original file.\n")
    file.write("It will be copied and backed up.\n")

# Copy the file to a new file
shutil.copy(source_file, copy_file)
print(f"File copied to {copy_file}")

# Create a backup directory if it does not exist
backup_dir.mkdir(exist_ok=True)

# Copy the file into the backup folder
shutil.copy(source_file, backup_file)
print(f"Backup created at {backup_file}")

# Delete the copied file safely
if os.path.exists(copy_file):
    os.remove(copy_file)
    print(f"{copy_file} was deleted.")
else:
    print(f"{copy_file} does not exist.")

# Delete the source file safely
if os.path.exists(source_file):
    os.remove(source_file)
    print(f"{source_file} was deleted.")
else:
    print(f"{source_file} does not exist.")