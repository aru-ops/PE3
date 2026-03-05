import re

# 1. 'a' followed by zero or more 'b'
text1 = "abbb"
if re.search(r"ab*", text1):
    print("1: Match found")

# 2. 'a' followed by 2 to 3 'b'
text2 = "abbb"
if re.search(r"ab{2,3}", text2):
    print("2: Match found")

# 3. Find sequences of lowercase letters joined with underscore
text3 = "hello_world test_string Invalid_Test"
matches3 = re.findall(r"[a-z]+_[a-z]+", text3)
print("3:", matches3)

# 4. One uppercase letter followed by lowercase letters
text4 = "Hello World PYTHON"
matches4 = re.findall(r"[A-Z][a-z]+", text4)
print("4:", matches4)

# 5. 'a' followed by anything ending in 'b'
text5 = "axxxb"
if re.search(r"a.*b", text5):
    print("5: Match found")

# 6. Replace space, comma, dot with colon
text6 = "Hello, world. Python is great"
result6 = re.sub(r"[ ,\.]", ":", text6)
print("6:", result6)

# 7. Convert snake_case to camelCase
def snake_to_camel(text):
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), text)

print("7:", snake_to_camel("hello_world_python"))

# 8. Split string at uppercase letters
text8 = "HelloWorldPython"
result8 = re.split(r"(?=[A-Z])", text8)
print("8:", result8)

# 9. Insert spaces between words starting with capital letters
text9 = "HelloWorldPython"
result9 = re.sub(r"([A-Z])", r" \1", text9).strip()
print("9:", result9)

# 10. Convert camelCase to snake_case
def camel_to_snake(text):
    return re.sub(r"([A-Z])", r"_\1", text).lower().lstrip("_")

print("10:", camel_to_snake("helloWorldPython"))