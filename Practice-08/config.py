# This file stores PostgreSQL connection settings.
import psycopg2

def config():
    return {
        "host": "localhost",
        "database": "phonebook",
        "user": "postgres",
        "password": "12345678",  
        "port": 5432
    }

def connect():
    return psycopg2.connect(**config())