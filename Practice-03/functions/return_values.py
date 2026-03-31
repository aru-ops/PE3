# Example 3: Return multiple values

def find_min_max(numbers):
    """
    Takes list of numbers
    Returns minimum and maximum values
    """
    return min(numbers), max(numbers)


nums = [5, 2, 9, 1, 7]

minimum, maximum = find_min_max(nums)

print("Min:", minimum)
print("Max:", maximum)
