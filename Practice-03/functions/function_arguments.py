# Example 2: Function arguments

def calculate_discount(price, discount=0.1):
    """
    price - product price
    discount - discount percent (default 10%)
    """
    final_price = price - price * discount
    return final_price


print(calculate_discount(100))
print(calculate_discount(100, 0.2))

