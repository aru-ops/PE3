# This script demonstrates how to find files by extension
# and move or copy them between directories.

import shutil
from pathlib import Path

source_dir = Path("source_files")
destination_dir = Path("destination_files")

# Create directories for the example
source_dir.mkdir(exist_ok=True)
destination_dir.mkdir(exist_ok=True)

# Create sample files
(source_dir / "file1.txt").write_text("Text file number 1", encoding="utf-8")
(source_dir / "file2.txt").write_text("Text file number 2", encoding="utf-8")
(source_dir / "image.png").write_text("This is not a real image", encoding="utf-8")

# Find all .txt files in the source directory
txt_files = list(source_dir.glob("*.txt"))
print("Found .txt files:")
for file in txt_files:
    print(file.name)

# Copy .txt files to the destination directory
for file in txt_files:
    shutil.copy(file, destination_dir / file.name)
    print(f"Copied {file.name} to {destination_dir}")

# Move one file as an extra example
file_to_move = source_dir / "file1.txt"
moved_path = destination_dir / "moved_file1.txt"

if file_to_move.exists():
    shutil.move(str(file_to_move), str(moved_path))
    print(f"Moved {file_to_move.name} to {moved_path.name}")