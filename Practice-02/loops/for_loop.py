# Example 1: Continue to next iteration if i is 3
i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)

# Example 2: else block in while loop
i = 1
while i < 6:
    print(i)
    i += 1
else:
    print("i is no longer less than 6")
