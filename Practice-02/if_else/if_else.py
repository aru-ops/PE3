# 1. Simple if-else
a = 200
b = 33
if b > a:
    print("b is greater than a")
else:
    print("b is not greater than a")

# 2. Even or odd number
number = 7
if number % 2 == 0:
    print("The number is even")
else:
    print("The number is odd")

# 3. Validate user input
username = "Emil"
if len(username) > 0:
    print(f"Welcome, {username}!")
else:
    print("Error: Username cannot be empty")

# 4. Assign value with if-else
a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

# 5. Short-hand if-else
a = 2
b = 330
print("A") if a > b else print("B")
