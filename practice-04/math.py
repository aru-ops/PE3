import math

# 1️ Convert degree to radian
degree = float(input("Input degree: "))
radian = math.radians(degree)  # convert degrees to radians
print("Radian:", radian)


# 2️ Area of a trapezoid
height = float(input("\nHeight: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))
area_trapezoid = 0.5 * (base1 + base2) * height  # formula: 0.5 * (a+b) * h
print("Area of trapezoid:", area_trapezoid)


# 3️ Area of a regular polygon
n_sides = int(input("\nInput number of sides: "))
side_length = float(input("Input the length of a side: "))
# formula: (n * s^2) / (4 * tan(pi/n))
area_polygon = (n_sides * side_length ** 2) / (4 * math.tan(math.pi / n_sides))
print("The area of the polygon is:", area_polygon)


# 4️ Area of a parallelogram
base = float(input("\nLength of base: "))
height = float(input("Height of parallelogram: "))
area_parallelogram = base * height  # formula: base * height
print("Area of parallelogram:", area_parallelogram)
