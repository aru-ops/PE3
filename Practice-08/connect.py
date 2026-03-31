# -*- coding: utf-8 -*-
import psycopg2

def connect():
    """
    Подключение к PostgreSQL через DSN.
    Это безопасный способ на Windows, чтобы избежать UnicodeDecodeError.
    """
    # DSN — строка с параметрами подключения
    dsn = "host=localhost dbname=phonebook user=postgres password=12345678 port=5432"
    
    # создаём подключение
    conn = psycopg2.connect(dsn)
    return conn

# Простейший тест подключения
if __name__ == "__main__":
    try:
        conn = connect()
        print("Connected successfully!")
        conn.close()
    except Exception as e:
        print("Error connecting:", e)