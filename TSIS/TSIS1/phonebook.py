import json
import csv
from connect import get_connection

PAGE_SIZE = 3


def paginate(query, params=()):
    conn = get_connection()
    cur = conn.cursor()

    offset = 0

    while True:
        cur.execute(query + " LIMIT %s OFFSET %s", params + (PAGE_SIZE, offset))
        rows = cur.fetchall()

        if not rows:
            print("No more data")
            break

        for r in rows:
            print(r)

        cmd = input("next / prev / quit: ")

        if cmd == "next":
            offset += PAGE_SIZE
        elif cmd == "prev":
            offset = max(0, offset - PAGE_SIZE)
        else:
            break

    cur.close()
    conn.close()


def sort_contacts():
    field = input("Sort by (name/birthday/date): ")

    mapping = {
        "name": "name",
        "birthday": "birthday",
        "date": "created_at"
    }

    paginate(f"SELECT name, email FROM contacts ORDER BY {mapping[field]}")


def filter_by_group():
    group = input("Group: ")

    paginate("""
        SELECT c.name, c.email
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
    """, (group,))


def search():
    query = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


def export_json():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """)

    contacts = []

    for c in cur.fetchall():
        cid = c[0]

        cur.execute("SELECT phone, type FROM phones WHERE contact_id=%s", (cid,))
        phones = cur.fetchall()

        contacts.append({
            "name": c[1],
            "email": c[2],
            "birthday": str(c[3]),
            "group": c[4],
            "phones": [{"number": p[0], "type": p[1]} for p in phones]
        })

    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)

    print("Exported with phones!")

    cur.close()
    conn.close()


def import_json():
    with open("contacts.json") as f:
        data = json.load(f)

    conn = get_connection()
    cur = conn.cursor()

    for c in data:
        cur.execute("SELECT id FROM contacts WHERE name=%s", (c["name"],))
        exists = cur.fetchone()

        if exists:
            choice = input(f"{c['name']} exists (skip/overwrite): ")
            if choice == "skip":
                continue
            else:
                cur.execute("DELETE FROM contacts WHERE name=%s", (c["name"],))

        cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT DO NOTHING", (c["group"],))
        cur.execute("SELECT id FROM groups WHERE name=%s", (c["group"],))
        gid = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (c["name"], c["email"], c["birthday"], gid))

        cid = cur.fetchone()[0]

        for p in c["phones"]:
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (cid, p["number"], p["type"]))

    conn.commit()
    cur.close()
    conn.close()


def import_csv():
    conn = get_connection()
    cur = conn.cursor()

    import os

    file_path = os.path.join(os.path.dirname(__file__), "contacts.csv")

    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("INSERT INTO groups(name) VALUES (%s) ON CONFLICT DO NOTHING", 
                        (row["group_name"],))

            cur.execute("SELECT id FROM groups WHERE name=%s", (row["group_name"],))
            gid = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (row["name"], row["email"], row["birthday"], gid))

            result = cur.fetchone()

            if result:
                cid = result[0]

                cur.execute("""
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES (%s, %s, %s)
                """, (cid, row["phone"], row["phone_type"]))

    conn.commit()
    print("CSV IMPORT DONE")
    cur.close()
    conn.close()


def menu():
    while True:
        print("""
1. Sort contacts
2. Filter by group
3. Search
4. Export JSON
5. Import JSON
6. Import CSV
0. Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            sort_contacts()
        elif choice == "2":
            filter_by_group()
        elif choice == "3":
            search()
        elif choice == "4":
            export_json()
        elif choice == "5":
            import_json()
        elif choice == "6":
            import_csv()
        elif choice == "0":
            break


if __name__ == "__main__":
    menu()