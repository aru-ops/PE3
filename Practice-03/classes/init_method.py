# Example 2: __init__ constructor and instance variables

class Student:
    def __init__(self, name, age):
        """Initialize a student with name and age"""
        self.name = name  # instance variable for student's name
        self.age = age    # instance variable for student's age

    def info(self):
        """Print student's information"""
        print(f"Student Name: {self.name}, Age: {self.age}")

# Create a student object
student1 = Student("Aru", 19)
student1.info()
