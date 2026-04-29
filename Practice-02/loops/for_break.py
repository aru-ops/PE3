# Example 1: Break after printing banana
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)
    if x == "banana":
        break

# Example 2: Break before printing banana
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        break
    print(x)

# Example 3: Break with else block (else won't run)
for x in range(6):
    if x == 3: break
    print(x)
