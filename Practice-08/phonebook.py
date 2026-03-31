import psycopg2
import os
from connect import connect



# =========================================
# CREATE TABLE
# =========================================
def create_table():
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                contact_id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                phone_number VARCHAR(20) UNIQUE NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        print("Table created successfully.")
    except Exception as e:
        print("Error creating table:", e)
    finally:
        conn.close()


# =========================================
# EXECUTE SQL FILES
# =========================================
import os

def execute_sql_file(filename):
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)

        conn.commit()
        cur.close()
        print(f"{filename} executed successfully.")
    except Exception as e:
        print(f"Error executing {filename}:", e)
    finally:
        conn.close()


# =========================================
# UPSERT ONE CONTACT
# =========================================
def upsert_contact():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    phone = input("Enter phone number: ")

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL upsert_contact(%s, %s, %s)", (first_name, last_name, phone))
        conn.commit()
        cur.close()
        print("Contact inserted/updated successfully.")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


# =========================================
# SEARCH CONTACTS BY PATTERN
# =========================================
def search_contacts():
    pattern = input("Enter pattern to search: ")

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()

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


# =========================================
# PAGINATION
# =========================================
def get_paginated_contacts():
    limit_count = int(input("Enter LIMIT: "))
    offset_count = int(input("Enter OFFSET: "))

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit_count, offset_count))
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


# =========================================
# DELETE CONTACT
# =========================================
def delete_contact():
    value = input("Enter first name, last name, or phone to delete: ")

    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("CALL delete_contact(%s)", (value,))
        conn.commit()
        cur.close()
        print("Contact(s) deleted successfully.")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


# =========================================
# INSERT MANY CONTACTS
# =========================================
def insert_many_contacts():
    n = int(input("How many contacts do you want to insert? "))

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
        cur.execute("CALL insert_many_contacts(%s, %s, %s)", (first_names, last_names, phones))
        conn.commit()
        cur.close()
        print("Bulk insert completed.")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


# =========================================
# SHOW ALL CONTACTS
# =========================================
def show_all_contacts():
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
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


# =========================================
# SHOW INVALID CONTACTS
# =========================================
def show_invalid_contacts():
    conn = connect()
    if conn is None:
        return

    try:
        cur = conn.cursor()
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


# =========================================
# MENU
# =========================================
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
            execute_sql_file("functions.sql")
        elif choice == "3":
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
    menu()