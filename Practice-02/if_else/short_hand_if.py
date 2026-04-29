# 1. One-line if
a = 5
b = 2
if a > b: print("a is greater than b")

# 2. One-line if-else
a = 2
b = 330
print("A") if a > b else print("B")

# 3. Assign value with one-line if-else
a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

# 4. Multiple conditions in one line
a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")

# 5. Default value with short-hand
username = ""
display_name = username if username else "Guest"
print("Welcome,", display_name)
