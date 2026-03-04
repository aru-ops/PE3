# Example 2: Using super() to call parent method

class Person:
    def __init__(self, name):
        self.name = name

    def info(self):
        print(f"Person Name: {self.name}")

class Student(Person):
    def __init__(self, name, grade):
        super().__init__(name)  # call parent constructor
        self.grade = grade

    def info(self):
        super().info()  # call parent method
        print(f"Grade: {self.grade}")

# Create object
student1 = Student("Aru", 19)
student1.info()
