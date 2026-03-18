# Example 4: *args and **kwargs

def student_info(*subjects, **info):
    """
    subjects - tuple of subjects
    info - dictionary with student info
    """

    print("Subjects:")
    for sub in subjects:
        print(sub)

    print("\nStudent Info:")
    for key, value in info.items():
        print(f"{key}: {value}")


student_info(
    "Math",
    "Python",
    "Physics",
    name="Aru",
    age=19,
    city="Almaty"
)

