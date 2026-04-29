# Example 1: Skip printing banana
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        continue
    print(x)

# Example 2: else block in for loop
for x in range(6):
    print(x)
else:
    print("Finally finished!")

# Example 3: Nested loop example
adj = ["red", "big", "tasty"]
fruits = ["apple", "banana", "cherry"]
for x in adj:
    for y in fruits:
        print(x, y)

# Example 4: Using pass statement in a for loop
for x in [0, 1, 2]:
    pass
