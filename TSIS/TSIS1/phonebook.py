import psycopg2
import csv
import json
import os
from config import DB_CONFIG

def connect():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Run SQL scripts to create tables and procedures."""
    conn = connect()
    cur = conn.cursor()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        cur.execute(f.read())
    with open('procedures.sql', 'r', encoding='utf-8') as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")

def display_contacts(contacts, page, total_pages):
    """Display contacts with pagination."""
    print(f"\n--- Page {page}/{total_pages} ---")
    if not contacts:
        print("No contacts found.")
        return
    for c in contacts:
        print(f"ID: {c[0]}, Name: {c[1]}, Email: {c[2] or '-'}, Birthday: {c[3] or '-'}, Group: {c[4] or '-'}")
        print(f"   Phones: {c[5] or '-'}")
    print("--------------------------------")

def paginated_display(rows, per_page=5):
    """Generic pagination for a list of rows."""
    total = len(rows)
    if total == 0:
        print("No contacts found.")
        return
    total_pages = (total + per_page - 1) // per_page
    page = 1
    while True:
        start = (page-1)*per_page
        end = start+per_page
        display_contacts(rows[start:end], page, total_pages)
        if total_pages == 1:
            break
        action = input("[n] next, [p] previous, [q] quit: ").lower()
        if action == 'n' and page < total_pages:
            page += 1
        elif action == 'p' and page > 1:
            page -= 1
        elif action == 'q':
            break

def main_menu():
    print("\n=== PHONEBOOK ===")
    print("1. Show all contacts (paginated)")
    print("2. Search by name/phone/email (paginated)")
    print("3. Filter by group (paginated)")
    print("4. Sort (by name, birthday, date added)")
    print("5. Add phone to contact (stored procedure)")
    print("6. Move contact to group (stored procedure)")
    print("7. Export to JSON")
    print("8. Import from JSON")
    print("9. Import CSV (with new fields)")
    print("0. Exit")
    return input("Choose an action: ")

def get_sorted_contacts(cursor, sort_by):
    if sort_by == 'name':
        order = "c.name"
    elif sort_by == 'birthday':
        order = "c.birthday NULLS LAST"
    elif sort_by == 'date_added':
        order = "c.id"  # assuming id increments by insertion order
    else:
        order = "c.name"
    query = f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS group_name,
               string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones_str
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
        ORDER BY {order}
    """
    cursor.execute(query)
    return cursor.fetchall()

def export_to_json():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.phone, c.email, c.birthday, g.name AS group_name,
               json_agg(json_build_object('phone', p.phone, 'type', p.type)) AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
    """)
    contacts = []
    for row in cur.fetchall():
        contacts.append({
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'email': row[3],
            'birthday': str(row[4]) if row[4] else None,
            'group': row[5],
            'phones': row[6] if row[6] else []
        })
    with open('contacts_export.json', 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print("Export completed to contacts_export.json")
    cur.close()
    conn.close()

def import_from_json():
    if not os.path.exists('contacts_export.json'):
        print("File contacts_export.json not found.")
        return
    with open('contacts_export.json', 'r', encoding='utf-8') as f:
        contacts = json.load(f)
    conn = connect()
    cur = conn.cursor()
    for c in contacts:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (c['name'],))
        existing = cur.fetchone()
        if existing:
            ans = input(f"Contact '{c['name']}' already exists. [s]kip / [o]verwrite? ").lower()
            if ans == 's':
                continue
            elif ans == 'o':
                cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
        cur.execute("""
            INSERT INTO contacts (name, phone, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, (SELECT id FROM groups WHERE name = %s))
            RETURNING id
        """, (c['name'], c.get('phone'), c.get('email'), c.get('birthday'), c.get('group')))
        contact_id = cur.fetchone()[0]
        for ph in c.get('phones', []):
            cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, ph['phone'], ph['type']))
    conn.commit()
    print("Import completed.")
    cur.close()
    conn.close()

def import_csv_with_new_fields():
    filename = input("Enter CSV filename (e.g., contacts.csv): ")
    if not os.path.exists(filename):
        print("File not found.")
        return
    conn = connect()
    cur = conn.cursor()
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # expecting: name, phone, email, birthday, group, phone2, phone2_type, ...
        for row in reader:
            if len(row) < 5:
                continue
            name, phone, email, birthday, group = row[0], row[1], row[2], row[3], row[4]
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            if cur.fetchone():
                ans = input(f"Contact '{name}' already exists. [s]kip / [o]verwrite? ").lower()
                if ans == 's':
                    continue
                elif ans == 'o':
                    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
            cur.execute("""
                INSERT INTO contacts (name, phone, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, (SELECT id FROM groups WHERE name = %s))
            """, (name, phone, email, birthday, group))
            # additional phones (columns 5,6; 7,8; ...)
            for i in range(5, len(row), 2):
                if i+1 < len(row) and row[i] and row[i+1]:
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES ((SELECT id FROM contacts WHERE name = %s), %s, %s)",
                                (name, row[i], row[i+1]))
    conn.commit()
    print("CSV import completed.")
    cur.close()
    conn.close()

def main():
    # Uncomment the line below only once to initialize database
    # init_db()
    conn = connect()
    cur = conn.cursor()
    while True:
        choice = main_menu()
        if choice == '0':
            break
        elif choice == '1':
            rows = get_sorted_contacts(cur, 'name')
            paginated_display(rows)
        elif choice == '2':
            query = input("Enter search text: ")
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
            paginated_display(rows)
        elif choice == '3':
            groups = ["Family","Work","Friend","Other"]
            print("Available groups:", ", ".join(groups))
            group = input("Enter group name: ")
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name,
                       string_agg(p.phone || ' (' || p.type || ')', ', ')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                WHERE g.name = %s
                GROUP BY c.id, g.name
            """, (group,))
            rows = cur.fetchall()
            paginated_display(rows)
        elif choice == '4':
            print("Sort by: 1 - name, 2 - birthday, 3 - date added")
            sort_choice = input("Choose: ")
            if sort_choice == '1':
                rows = get_sorted_contacts(cur, 'name')
            elif sort_choice == '2':
                rows = get_sorted_contacts(cur, 'birthday')
            elif sort_choice == '3':
                rows = get_sorted_contacts(cur, 'date_added')
            else:
                continue
            paginated_display(rows)
        elif choice == '5':
            name = input("Contact name: ")
            phone = input("Phone number: ")
            ptype = input("Type (home/work/mobile): ")
            try:
                cur.callproc('add_phone', (name, phone, ptype))
                conn.commit()
                print("Phone added.")
            except psycopg2.Error as e:
                print(f"Error: {e}")
                conn.rollback()
        elif choice == '6':
            name = input("Contact name: ")
            group = input("Group name: ")
            try:
                cur.callproc('move_to_group', (name, group))
                conn.commit()
                print("Contact moved.")
            except psycopg2.Error as e:
                print(f"Error: {e}")
                conn.rollback()
        elif choice == '7':
            export_to_json()
        elif choice == '8':
            import_from_json()
        elif choice == '9':
            import_csv_with_new_fields()
        else:
            print("Invalid choice.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()