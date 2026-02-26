# 1️ Generator that generates squares up to N
def generate_squares(n):
    for i in range(n + 1):
        yield i * i


print("Squares up to N:")
n = int(input("Enter N: "))
for square in generate_squares(n):
    print(square)


# 2️ Print even numbers between 0 and n (comma separated)
def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i


print("\nEven numbers:")
n = int(input("Enter n: "))
print(",".join(str(num) for num in even_numbers(n)))


# 3️ Numbers divisible by 3 and 4 between 0 and n
def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i


print("\nNumbers divisible by 3 and 4:")
n = int(input("Enter n: "))
for num in divisible_by_3_and_4(n):
    print(num)


# 4️ Generator squares from a to b
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i


print("\nSquares from a to b:")
a = int(input("Enter a: "))
b = int(input("Enter b: "))
for value in squares(a, b):
    print(value)


# 5️ Generator from n down to 0
def countdown(n):
    while n >= 0:
        yield n
        n -= 1


print("\nCountdown:")
n = int(input("Enter n: "))
for number in countdown(n):
    print(number)
