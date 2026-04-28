# This script demonstrates directory creation,
# listing files and folders, and working with paths.

import os
from pathlib import Path

# Show the current working directory
print("Current working directory:")
print(os.getcwd())

# Create nested directories
nested_dir = Path("practice_folder/subfolder/example")
nested_dir.mkdir(parents=True, exist_ok=True)
print(f"Created nested directory: {nested_dir}")

# Create a sample file inside the directory
sample_file = nested_dir / "notes.txt"
with open(sample_file, "w", encoding="utf-8") as file:
    file.write("This file is inside a nested directory.\n")

# List items in the main folder
print("\nItems in the current directory:")
for item in os.listdir():
    print(item)

# Change the current working directory
os.chdir("practice_folder")
print("\nChanged working directory:")
print(os.getcwd())

# List items in the new current directory
print("\nItems inside 'practice_folder':")
for item in os.listdir():
    print(item)