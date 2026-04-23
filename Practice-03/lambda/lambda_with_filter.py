# Example 3: Using lambda with filter() for selection

numbers = [10, 15, 20, 25, 30]

# Keep numbers divisible by 5 but greater than 15
filtered = list(filter(lambda x: x % 5 == 0 and x > 15, numbers))

print("Numbers divisible by 5 and > 15:", filtered)
