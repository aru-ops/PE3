# This file stores PostgreSQL connection settings.

def config():
    return {
        "host": "localhost",
        "database": "phonebook",
        "user": "postgres",
        "password": "1234",   # Change this to your PostgreSQL password
        "port": 5432
    }