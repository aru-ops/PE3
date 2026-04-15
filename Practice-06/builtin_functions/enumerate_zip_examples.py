# This script demonstrates enumerate(), zip(),
# type checking, and type conversion functions.

names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate() gives both index and value
print("Using enumerate():")
for index, name in enumerate(names, start=1):
    print(f"{index}. {name}")

# zip() combines values from multiple lists
print("\nUsing zip():")
for name, score in zip(names, scores):
    print(f"{name} scored {score}")

# Type checking
value = "123"
print("\nType checking:")
print("Value:", value)
print("Type of value:", type(value))

# Type conversion
converted_int = int(value)
converted_float = float(value)
converted_str = str(converted_int)
converted_list = list(names)

print("\nType conversion examples:")
print("Integer:", converted_int)
print("Float:", converted_float)
print("String:", converted_str)
print("List:", converted_list)