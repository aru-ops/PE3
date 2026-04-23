# This script demonstrates file modes: w, a, and x.
# It also shows why the with statement is useful.

from pathlib import Path

file_path = Path("sample_write.txt")
exclusive_file = Path("exclusive_file.txt")

# Mode "w" creates a new file or overwrites an existing one
with open(file_path, "w", encoding="utf-8") as file:
    file.write("This line is written using mode 'w'.\n")
    file.write("Old content is replaced in this mode.\n")

# Mode "a" adds new text to the end of the file
with open(file_path, "a", encoding="utf-8") as file:
    file.write("This line is appended using mode 'a'.\n")

# Read the file to verify the final content
with open(file_path, "r", encoding="utf-8") as file:
    print("Content after writing and appending:")
    print(file.read())

# Mode "x" creates a file only if it does not already exist
if not exclusive_file.exists():
    with open(exclusive_file, "x", encoding="utf-8") as file:
        file.write("This file was created using mode 'x'.\n")
    print(f"{exclusive_file} was created successfully.")
else:
    print(f"{exclusive_file} already exists, so mode 'x' is skipped")