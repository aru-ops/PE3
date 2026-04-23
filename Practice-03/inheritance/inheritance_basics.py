# Example 1: Basic inheritance (Parent -> Child)

class Animal:
    """Parent class representing an animal"""
    def speak(self):
        print("The animal makes a sound")

class Dog(Animal):
    """Child class inheriting from Animal"""
    pass

# Create object of child class
dog1 = Dog()
dog1.speak()  # Inherited method from parent
