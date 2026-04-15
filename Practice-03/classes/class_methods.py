# Example: Calculate the area of a circle using a class

class Circle:
    pi = 3.1416  # class variable for PI

    def __init__(self, radius):
        self.radius = radius  # instance variable for circle radius

    def area(self):
        """Calculate the area of the circle"""
        return Circle.pi * self.radius ** 2

# Create a circle object
circle1 = Circle(5)
print("Area:", circle1.area())
