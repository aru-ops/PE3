# 1. Logical and
a = 200
b = 33
c = 500
if a > b and c > a:
    print("Both conditions are True")

# 2. Logical or
if a > b or a > c:
    print("At least one of the conditions is True")

# 3. Logical not
if not a > b:
    print("a is NOT greater than b")

# 4. Combining multiple logical operators
age = 25
is_student = False
has_discount_code = True
if (age < 18 or age > 65) and not is_student or has_discount_code:
    print("Discount applies!")

# 5. Parentheses for clarity
temperature = 25
is_raining = False
is_weekend = True
if (temperature > 20 and not is_raining) or is_weekend:
    print("Great day for outdoor activities!")
