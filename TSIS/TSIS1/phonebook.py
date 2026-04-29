import psycopg2
import csv
import json
from datetime import datetime
from connect import connect

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
def get_group_id(conn, group_name):
    """Вернуть id группы, создать если нет"""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
        return cur.fetchone()[0]

def add_contact(conn, first_name, last_name, email=None, birthday=None, group_name=None):
    group_id = get_group_id(conn, group_name) if group_name else None
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (first_name, last_name, email, birthday, group_id))
        contact_id = cur.fetchone()[0]
        conn.commit()
        return contact_id

def delete_contact_by_name(conn, first_name, last_name):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE first_name = %s AND COALESCE(last_name,'') = COALESCE(%s,'')",
                    (first_name, last_name))
        conn.commit()
        return cur.rowcount

# ---------- ИМПОРТ / ЭКСПОРТ ----------
def export_to_json(conn, filename):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.first_name, c.last_name, c.email, c.birthday, g.name AS group_name,
                   json_agg(json_build_object('phone', p.phone, 'type', p.type)) AS phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            GROUP BY c.id, g.name
            ORDER BY c.first_name
        """)
        rows = cur.fetchall()
    data = []
    for row in rows:
        contact = {
            "first_name": row[0],
            "last_name": row[1],
            "email": row[2],
            "birthday": str(row[3]) if row[3] else None,
            "group": row[4],
            "phones": row[5] if row[5] else []
        }
        data.append(contact)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(data)} contacts to {filename}")

def import_from_json(conn, filename):
    with open(filename, 'r', encoding='utf-8') as f:
        contacts = json.load(f)
    for contact in contacts:
        first = contact['first_name']
        last = contact.get('last_name', '')
        # проверка существования
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE first_name = %s AND COALESCE(last_name,'') = %s",
                        (first, last or ''))
            exists = cur.fetchone()
        if exists:
            ans = input(f"Contact {first} {last} exists. Overwrite? (y/n/skip all): ").lower()
            if ans == 'skip all':
                break
            if ans != 'y':
                continue
            # удаляем старый
            delete_contact_by_name(conn, first, last)
        # добавляем новый
        group = contact.get('group')
        group_id = get_group_id(conn, group) if group else None
        birthday = contact.get('birthday')
        if birthday:
            birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (first, last, contact.get('email'), birthday, group_id))
            cid = cur.fetchone()[0]
            for ph in contact.get('phones', []):
                cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (cid, ph['phone'], ph['type']))
            conn.commit()
        print(f"Imported {first} {last}")

def import_csv_extended(conn, filepath):
    """CSV с колонками: first_name,last_name,phone,email,birthday,group,phone_type"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                first = row['first_name']
                last = row.get('last_name', '')
                phone = row.get('phone')
                email = row.get('email')
                birthday = row.get('birthday')
                group = row.get('group')
                phone_type = row.get('phone_type', 'mobile')
                # проверяем дубликат
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM contacts WHERE first_name = %s AND COALESCE(last_name,'') = %s",
                                (first, last or ''))
                    exists = cur.fetchone()
                if exists:
                    ans = input(f"Contact {first} {last} exists. Overwrite? (y/n): ").lower()
                    if ans != 'y':
                        continue
                    delete_contact_by_name(conn, first, last)
                # вставка
                group_id = get_group_id(conn, group) if group else None
                bday = datetime.strptime(birthday, '%Y-%m-%d').date() if birthday else None
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id
                    """, (first, last, email, bday, group_id))
                    cid = cur.fetchone()[0]
                    if phone:
                        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                    (cid, phone, phone_type))
                    conn.commit()
                print(f"Imported {first} {last}")
    except Exception as e:
        print(f"CSV error: {e}")

# ---------- КОНСОЛЬНЫЕ ФУНКЦИИ (НОВЫЕ) ----------
def filter_by_group(conn):
    groups = []
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM groups ORDER BY name")
        groups = [row[0] for row in cur.fetchall()]
    if not groups:
        print("No groups found.")
        return
    print("Available groups:", ', '.join(groups))
    group_name = input("Enter group name: ")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.first_name, c.last_name, c.email, c.birthday,
                   (SELECT string_agg(phone || ' (' || type || ')', ', ') FROM phones WHERE contact_id = c.id) AS phones
            FROM contacts c
            JOIN groups g ON c.group_id = g.id
            WHERE g.name = %s
        """, (group_name,))
        rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"{r[0]} {r[1]} | {r[2]} | BD: {r[3]} | Phones: {r[4]}")
    else:
        print("No contacts in this group.")

def search_by_email(conn):
    pattern = input("Enter email pattern (e.g., '@gmail.com'): ")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT first_name, last_name, email FROM contacts
            WHERE email ILIKE %s
        """, (f'%{pattern}%',))
        rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"{r[0]} {r[1]} - {r[2]}")
    else:
        print("No matching emails.")

def paginated_navigation(conn):
    """Интерактивная навигация с сортировкой"""
    print("Sort by: first_name, birthday, created_at")
    sort_by = input("Sort field [first_name]: ") or 'first_name'
    if sort_by not in ('first_name', 'birthday', 'created_at'):
        sort_by = 'first_name'
    order = input("Order (ASC/DESC) [ASC]: ").upper() or 'ASC'
    if order not in ('ASC', 'DESC'):
        order = 'ASC'
    per_page = int(input("Contacts per page [5]: ") or "5")
    page = 1
    while True:
        offset = (page - 1) * per_page
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM contacts")
            total = cur.fetchone()[0]
            cur.execute("SELECT * FROM paginate_contacts_ext(%s, %s, %s, %s)",
                        (per_page, offset, sort_by, order))
            rows = cur.fetchall()
        if not rows:
            print("No contacts.")
            break
        print(f"\n--- Page {page} (total {total}) ---")
        for r in rows:
            print(f"{r[1]} {r[2]} | Email: {r[3]} | BD: {r[4]} | Group: {r[5]} | Phones: {r[7]}")
        print(f"[N]ext  [P]rev  [Q]uit")
        cmd = input().lower()
        if cmd == 'n' and page * per_page < total:
            page += 1
        elif cmd == 'p' and page > 1:
            page -= 1
        elif cmd == 'q':
            break
        else:
            print("Invalid command")

def call_add_phone(conn):
    first = input("First name: ")
    last = input("Last name: ")
    phone = input("Phone number: ")
    ptype = input("Type (home/work/mobile) [mobile]: ") or 'mobile'
    with conn.cursor() as cur:
        cur.callproc('add_phone', (first, last, phone, ptype))
        conn.commit()
    print("Phone added.")

def call_move_to_group(conn):
    first = input("First name: ")
    last = input("Last name: ")
    group = input("Group name: ")
    with conn.cursor() as cur:
        cur.callproc('move_to_group', (first, last, group))
        conn.commit()
    print(f"Moved to group '{group}'.")

def enhanced_search(conn):
    pattern = input("Search pattern (name/email/phone): ")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts_enhanced(%s)", (pattern,))
        rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"{r[1]} {r[2]} | Email: {r[3]} | BD: {r[4]} | Group: {r[5]} | Phones: {r[6]}")
    else:
        print("No matches.")

# ---------- МЕНЮ (ОБНОВЛЁННОЕ) ----------
def menu():
    conn = connect()
    if conn is None:
        return
    while True:
        print("\n===== EXTENDED PHONEBOOK =====")
        print("1. Add contact (console)")
        print("2. Show all contacts (paginated, sortable)")
        print("3. Filter by group")
        print("4. Search by email pattern")
        print("5. Enhanced search (name/email/phone)")
        print("6. Add phone to existing contact")
        print("7. Move contact to group")
        print("8. Import from CSV (extended)")
        print("9. Export to JSON")
        print("10. Import from JSON")
        print("11. Run old functions (upsert, bulk insert, delete)")
        print("0. Exit")
        choice = input("Option: ")

        if choice == "1":
            first = input("First name: ")
            last = input("Last name: ")
            email = input("Email: ") or None
            birthday = input("Birthday (YYYY-MM-DD): ") or None
            if birthday:
                birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
            group = input("Group: ") or None
            contact_id = add_contact(conn, first, last, email, birthday, group)
            add_phone = input("Add phone now? (y/n): ").lower()
            if add_phone == 'y':
                phone = input("Phone number: ")
                ptype = input("Type: ")
                with conn.cursor() as cur:
                    cur.callproc('add_phone', (first, last, phone, ptype))
                    conn.commit()
            print(f"Contact added with ID {contact_id}")
        elif choice == "2":
            paginated_navigation(conn)
        elif choice == "3":
            filter_by_group(conn)
        elif choice == "4":
            search_by_email(conn)
        elif choice == "5":
            enhanced_search(conn)
        elif choice == "6":
            call_add_phone(conn)
        elif choice == "7":
            call_move_to_group(conn)
        elif choice == "8":
            path = input("CSV file path: ")
            import_csv_extended(conn, path)
        elif choice == "9":
            path = input("JSON export path: ")
            export_to_json(conn, path)
        elif choice == "10":
            path = input("JSON import path: ")
            import_from_json(conn, path)
        elif choice == "11":
            # Подменю для старых функций (адаптированных под новую схему)
            print("\n--- Legacy functions ---")
            print("a. Upsert contact (insert or update)")
            print("b. Insert many contacts (with validation)")
            print("c. Delete contact by name")
            sub = input("Choice: ")
            if sub == 'a':
                first = input("First name: ")
                last = input("Last name: ")
                phone = input("Phone: ")
                with conn.cursor() as cur:
                    # используем существующую процедуру upsert_contact (она работала со старой таблицей)
                    # но теперь она не подходит, поэтому напишем простой upsert напрямую
                    cur.execute("""
                        INSERT INTO contacts (first_name, last_name) VALUES (%s, %s)
                        ON CONFLICT (first_name, COALESCE(last_name,'')) DO UPDATE SET first_name = EXCLUDED.first_name
                        RETURNING id
                    """, (first, last))
                    cid = cur.fetchone()[0]
                    # удаляем старые телефоны? по заданию upsert обновляет только первое имя/фамилию? Не будем усложнять
                    # добавим телефон если нет
                    cur.execute("SELECT 1 FROM phones WHERE contact_id = %s", (cid,))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, 'mobile')", (cid, phone))
                    conn.commit()
                print("Upsert done.")
            elif sub == 'b':
                # вызываем старую процедуру insert_many_contacts, но она работает со старой таблицей phonebook
                # для новой схемы нужно переписать, но это выходит за рамки TSIS1
                print("Please implement bulk insert for new schema if needed (skipped).")
            elif sub == 'c':
                first = input("First name: ")
                last = input("Last name: ")
                delete_contact_by_name(conn, first, last)
                print("Deleted.")
        elif choice == "0":
            break
        else:
            print("Invalid option")
    conn.close()

if __name__ == "__main__":
    menu()