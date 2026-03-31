# This file stores PostgreSQL connection settings.
import psycopg2

def config():
    return {
        "host": "localhost",
        "database": "phonebook",
        "user": "postgres",
        "password": "1234",   # Change this to your PostgreSQL password
        "port": 5432
    }