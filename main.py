import database as db


def add_usage():
    app = input("Enter app name: ").strip()
    if not app:
        print("App name is required.")
        return
    try:
        minutes = int(input("Usage minutes: "))
        if minutes < 0:
            raise ValueError
    except ValueError:
        print("Minutes must be a non-negative whole number.")
        return
    db.add_usage(app, minutes)
    print("Usage logged")


def view_usage():
    rows = db.all_usage_rows_for_cli()
    if not rows:
        print("(no entries)")
        return
    for row in rows:
        print(f"{row['id']}: {row['app_name']} — {row['usage_minutes']} min ({row['logged_date']})")


def main():
    db.init_db()
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


if __name__ == "__main__":
    main()
