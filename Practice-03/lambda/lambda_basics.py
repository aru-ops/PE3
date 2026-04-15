# Example 1: Basic lambda function

# Lambda to calculate area of rectangle
area = lambda length, width: length * width

print("Area of 5x3 rectangle:", area(5, 3))

# Lambda to check if number is positive
is_positive = lambda x: x > 0
print("Is -4 positive?", is_positive(-4))
