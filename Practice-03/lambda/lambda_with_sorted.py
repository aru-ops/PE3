# Example 4: Sort a list of dictionaries

students = [
    {"name": "Alice", "age": 20},
    {"name": "Bob", "age": 19},
    {"name": "Charlie", "age": 18}
]

# Сортируем по возрасту по возрастанию
sorted_students = sorted(students, key=lambda s: s["age"])

print("Students sorted by age (ascending):")
for s in sorted_students:
    print(s)
    
