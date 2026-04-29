# Example 2: Using lambda with map() for transformations

numbers = [1, 2, 3, 4, 5]

# Convert each number to its square plus 1
transformed = list(map(lambda x: x**2 + 1, numbers))

print("Original:", numbers)
print("Transformed (x^2 + 1):", transformed)
