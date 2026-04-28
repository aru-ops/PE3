import psycopg2
import os
from connect import connect   # Import DB connection function from connect.py


# CREATE TABLE
def create_table():
    conn = connect()
    if conn is None:
        return   # Stop if connection failed

    try:
        cur = conn.cursor()   # Cursor is used to execute SQL queries

        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                contact_id SERIAL PRIMARY KEY,   -- Auto-increment unique ID
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                phone_number VARCHAR(20) UNIQUE NOT NULL   -- UNIQUE prevents duplicates
            )
        """)

        conn.commit()   # Save table creation in database
        cur.close()
        print("Table created successfully.")

    except Exception as e:
        print("Error creating table:", e)

    finally:
        conn.close()   # Always close DB connection



# EXECUTE SQL FILES

def execute_sql_file(filename):
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # Get the folder where this Python file is located
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Build full path to functions.sql or procedures.sql
        file_path = os.path.join(base_dir, filename)

        # Open SQL file and read all SQL code as one string
        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()

            # Execute SQL code inside PostgreSQL
            # Used to create functions and procedures from file
            cur.execute(sql)

        conn.commit()
        cur.close()
        print(f"{filename} executed successfully.")

    except Exception as e:
        print(f"Error executing {filename}:", e)

    finally:
        conn.close()



# UPSERT ONE CONTACT

def upsert_contact():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    phone = input("Enter phone number: ")

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # CALL is used for PostgreSQL procedures
        # This procedure inserts a new contact or updates existing one
        cur.execute("CALL upsert_contact(%s, %s, %s)", (first_name, last_name, phone))

        conn.commit()
        cur.close()
        print("Contact inserted/updated successfully.")

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# SEARCH CONTACTS BY PATTERN

def search_contacts():
    pattern = input("Enter pattern to search: ")

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # SELECT is used for functions because functions return data
        # %s is a safe placeholder for user input
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))

        rows = cur.fetchall()   # Get all returned rows from function

        if rows:
            print("\n--- Search Results ---")
            for row in rows:
                print(f"ID: {row[0]}, First Name: {row[1]}, Last Name: {row[2]}, Phone: {row[3]}")
        else:
            print("No matching contacts found.")

        cur.close()

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# PAGINATION

def get_paginated_contacts():
    # Convert input to int because LIMIT and OFFSET must be numbers
    limit_count = int(input("Enter LIMIT: "))
    offset_count = int(input("Enter OFFSET: "))

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # Calls PostgreSQL function that returns contacts in parts
        # LIMIT = how many rows to show
        # OFFSET = how many rows to skip
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (limit_count, offset_count)
        )

        rows = cur.fetchall()

        if rows:
            print("\n--- Paginated Contacts ---")
            for row in rows:
                print(f"ID: {row[0]}, First Name: {row[1]}, Last Name: {row[2]}, Phone: {row[3]}")
        else:
            print("No contacts found.")

        cur.close()

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# DELETE CONTACT

def delete_contact():
    value = input("Enter first name, last name, or phone to delete: ")

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # CALL delete procedure from PostgreSQL
        # The procedure deletes by first_name, last_name, or phone_number
        cur.execute("CALL delete_contact(%s)", (value,))

        conn.commit()
        cur.close()
        print("Contact(s) deleted successfully.")

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# INSERT MANY CONTACTS

def insert_many_contacts():
    n = int(input("How many contacts do you want to insert? "))

    # Python lists will be sent to PostgreSQL as arrays
    first_names = []
    last_names = []
    phones = []

    for i in range(n):
        print(f"\nContact {i+1}")
        first_names.append(input("First name: "))
        last_names.append(input("Last name: "))
        phones.append(input("Phone number: "))

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # Sends 3 Python lists into PostgreSQL procedure
        # Procedure will validate phones and insert/update contacts
        cur.execute("CALL insert_many_contacts(%s, %s, %s)", (first_names, last_names, phones))

        conn.commit()
        cur.close()
        print("Bulk insert completed.")

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# SHOW ALL CONTACTS

def show_all_contacts():
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # ORDER BY makes output neat and sorted by insertion order
        cur.execute("SELECT * FROM phonebook ORDER BY contact_id")

        rows = cur.fetchall()

        if rows:
            print("\n--- All Contacts ---")
            for row in rows:
                print(f"ID: {row[0]}, First Name: {row[1]}, Last Name: {row[2]}, Phone: {row[3]}")
        else:
            print("Phonebook is empty.")

        cur.close()

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# SHOW INVALID CONTACTS

def show_invalid_contacts():
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        # This table stores contacts with incorrect phone format
        cur.execute("SELECT * FROM invalid_contacts ORDER BY id")

        rows = cur.fetchall()

        if rows:
            print("\n--- Invalid Contacts ---")
            for row in rows:
                print(f"ID: {row[0]}, First Name: {row[1]}, Last Name: {row[2]}, Phone: {row[3]}, Error: {row[4]}")
        else:
            print("No invalid contacts found.")

        cur.close()

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()



# MENU

def menu():
    while True:
        print("\n===== PHONEBOOK MENU =====")
        print("1. Create table")
        print("2. Load functions.sql")
        print("3. Load procedures.sql")
        print("4. Insert/Update one contact")
        print("5. Search contacts by pattern")
        print("6. Show contacts with pagination")
        print("7. Delete contact")
        print("8. Insert many contacts")
        print("9. Show all contacts")
        print("10. Show invalid contacts")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_table()

        elif choice == "2":
            # Load SQL functions into PostgreSQL
            execute_sql_file("functions.sql")

        elif choice == "3":
            # Load SQL procedures into PostgreSQL
            execute_sql_file("procedures.sql")

        elif choice == "4":
            upsert_contact()

        elif choice == "5":
            search_contacts()

        elif choice == "6":
            get_paginated_contacts()

        elif choice == "7":
            delete_contact()

        elif choice == "8":
            insert_many_contacts()

        elif choice == "9":
            show_all_contacts()

        elif choice == "10":
            show_invalid_contacts()

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    # Start the program only if this file is run directly
    menu()
