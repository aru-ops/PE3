# Example: Class variable vs instance variable

class Employee:
    company = "Tech Corp"  # class variable shared by all employees

    def __init__(self, name, salary):
        self.name = name      # instance variable
        self.salary = salary  # instance variable

    def info(self):
        print(f"{self.name} works at {Employee.company} with salary {self.salary}")

# Create objects
emp1 = Employee("Alice", 5000)
emp2 = Employee("Bob", 6000)

emp1.info()
emp2.info()

# Update class variable
Employee.company = "SuperTech"
emp1.info()
emp2.info()
