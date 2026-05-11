import sqlite3

conn = sqlite3.connect("detox.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usage_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT,
    usage_minutes INTEGER
)
""")

conn.commit()
conn.close()

print("Database created successfully")