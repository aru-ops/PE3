# This script demonstrates how to read data from a text file
# using read(), readline(), and readlines().

from pathlib import Path

# Create a sample file path
file_path = Path("sample_read.txt")

# Write sample text into the file first
with open(file_path, "w", encoding="utf-8") as file:
    # We create a file with several lines for reading examples
    file.write("Python is easy to learn.\n")
    file.write("File handling is very useful.\n")
    file.write("Practice makes programming better.\n")

# Read the whole file at once
with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()
    print("Using read():")
    print(content)

# Read only one line
with open(file_path, "r", encoding="utf-8") as file:
    first_line = file.readline()
    print("Using readline():")
    print(first_line)

# Read all lines into a list
with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()
    print("Using readlines():")
    print(lines)