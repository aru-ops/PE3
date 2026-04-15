# This script demonstrates map(), filter(), and reduce()
# with simple number examples.

from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# map() applies a function to every item
squared_numbers = list(map(lambda x: x ** 2, numbers))
print("Squared numbers using map():")
print(squared_numbers)

# filter() keeps only items that match a condition
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print("\nEven numbers using filter():")
print(even_numbers)

# reduce() combines all items into one result
sum_of_numbers = reduce(lambda a, b: a + b, numbers)
print("\nSum of numbers using reduce():")
print(sum_of_numbers)

# Some other useful built-in functions
print("\nOther built-in function examples:")
print("Length:", len(numbers))
print("Sum:", sum(numbers))
print("Minimum:", min(numbers))
print("Maximum:", max(numbers))
print("Sorted descending:", sorted(numbers, reverse=True))