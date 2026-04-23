import psycopg2
from config import config


def connect():
    """Connect to PostgreSQL database"""
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        print("Connected to PostgreSQL successfully!")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print("Connection error:", error)
        return None