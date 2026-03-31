# This file creates a connection to PostgreSQL.

import psycopg2
from config import config

def connect():
    # Return a database connection using settings from config.py
    return psycopg2.connect(**config())