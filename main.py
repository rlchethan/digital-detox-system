import sqlite3

def add_usage():
    app = input("Enter app name: ")
    minutes = int(input("Usage minutes: "))

    conn = sqlite3.connect("detox.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usage_logs(app_name, usage_minutes) VALUES (?, ?)",
        (app, minutes)
    )

    conn.commit()
    conn.close()

    print("Usage logged")

def view_usage():
    conn = sqlite3.connect("detox.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usage_logs")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

while True:
    print("\n1. Add Usage")
    print("2. View Usage")
    print("3. Exit")

    choice = input("Choose: ")

    if choice == "1":
        add_usage()
    elif choice == "2":
        view_usage()
    elif choice == "3":
        break