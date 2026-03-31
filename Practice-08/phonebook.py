# This program works with PostgreSQL PhoneBook
# using functions and stored procedures.
import psycopg2
import os
from connect import connect

def create_table():
    # Create contacts table if it does not exist
    query = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        surname VARCHAR(100),
        phone VARCHAR(20)
    );
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    print("Table created successfully.")

def run_sql_file(filename):
    # Execute SQL from a file
    conn = connect()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()
        cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()
    print(f"{filename} executed successfully.")

def upsert_contact():
    # Insert or update one contact
    name = input("Enter name: ")
    surname = input("Enter surname: ")
    phone = input("Enter phone: ")

    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s, %s);", (name, surname, phone))
    conn.commit()
    cur.close()
    conn.close()

    print("Contact inserted/updated successfully.")

def show_all_contacts():
    # Show all contacts from the table
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts ORDER BY id;")
    rows = cur.fetchall()

    print("\n--- CONTACTS ---")
    for row in rows:
        print(row)

    cur.close()
    conn.close()

def search_contacts():
    # Search contacts using PostgreSQL function
    pattern = input("Enter search pattern: ")

    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s);", (pattern,))
    rows = cur.fetchall()

    print("\n--- SEARCH RESULTS ---")
    for row in rows:
        print(row)

    cur.close()
    conn.close()

def paginated_contacts():
    # Show contacts with limit and offset
    limit = int(input("Enter LIMIT: "))
    offset = int(input("Enter OFFSET: "))

    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
    rows = cur.fetchall()

    print("\n--- PAGINATED RESULTS ---")
    for row in rows:
        print(row)

    cur.close()
    conn.close()

def bulk_insert():
    # Run procedure that inserts many contacts
    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL insert_many_contacts();")
    conn.commit()
    cur.close()
    conn.close()

    print("Bulk insert completed. Check PostgreSQL notices for invalid data.")

def delete_contact():
    # Delete contact by name, surname, or phone
    value = input("Enter name, surname, or phone to delete: ")

    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s);", (value,))
    conn.commit()
    cur.close()
    conn.close()

    print("Contact deleted if it existed.")

def menu():
    # Main menu for user actions
    while True:
        print("\n===== PHONEBOOK MENU =====")
        print("1. Create table")
        print("2. Run functions.sql")
        print("3. Run procedures.sql")
        print("4. Insert or update contact")
        print("5. Show all contacts")
        print("6. Search contacts")
        print("7. Show paginated contacts")
        print("8. Bulk insert test data")
        print("9. Delete contact")
        print("10. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            run_sql_file("functions.sql")
        elif choice == "3":
            run_sql_file("procedures.sql")
        elif choice == "4":
            upsert_contact()
        elif choice == "5":
            show_all_contacts()
        elif choice == "6":
            search_contacts()
        elif choice == "7":
            paginated_contacts()
        elif choice == "8":
            bulk_insert()
        elif choice == "9":
            delete_contact()
        elif choice == "10":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    menu()