# 1. Class with __len__ method returning 0
class myclass():
    def __len__(self):
        return 0
myobj = myclass()
print(bool(myobj))  # False

# 2. Function returning True
def myFunction():
    return True
print(myFunction())

# 3. Execute code based on function
if myFunction():
    print("YES!")
else:
    print("NO!")

# 4. isinstance check
x = 200
print(isinstance(x, int))  # True

# 5. Simple boolean expressions
print(5 > 2)       # True
print(5 == 5)      # True
print(3 < 1)       # False
