import psycopg2
from connect import config

try:
    conn = psycopg2.connect(**config())
    print("Connection successful")
    conn.close()
except Exception as e:
    print("Error:", e)