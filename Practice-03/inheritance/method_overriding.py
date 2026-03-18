# Example 3: Method overriding

class Vehicle:
    def start(self):
        print("Vehicle is starting")

class Car(Vehicle):
    def start(self):
        # Overriding the parent method
        print("Car engine is starting")

vehicle1 = Vehicle()
vehicle1.start()

car1 = Car()
car1.start()
