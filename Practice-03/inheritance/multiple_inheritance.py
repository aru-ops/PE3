# Example 4: Multiple inheritance

class Mother:
    def skills(self):
        print("Mother's skill: Cooking")

class Father:
    def skills(self):
        print("Father's skill: Driving")

class Child(Mother, Father):
    pass

child1 = Child()
child1.skills()  # Calls Mother's method (first in inheritance order)
