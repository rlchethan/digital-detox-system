import os
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta

_DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "detox.db")


@contextmanager
def get_connection():
    conn = sqlite3.connect(_DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate_usage_logs(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(usage_logs)")
    cols = {row[1] for row in cur.fetchall()}
    if "logged_date" not in cols:
        cur.execute("ALTER TABLE usage_logs ADD COLUMN logged_date TEXT")


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                usage_minutes INTEGER NOT NULL
            )
            """
        )
        _migrate_usage_logs(conn)
        cur.execute(
            """
            UPDATE usage_logs SET logged_date = date('now') WHERE logged_date IS NULL OR logged_date = ''
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS detox_settings(
                id INTEGER PRIMARY KEY CHECK (id = 1),
                daily_goal_minutes INTEGER NOT NULL DEFAULT 120
            )
            """
        )
        cur.execute(
            """
            INSERT OR IGNORE INTO detox_settings (id, daily_goal_minutes) VALUES (1, 120)
            """
        )


def add_usage(app_name: str, minutes: int, logged_date: str | None = None) -> None:
    date_val = logged_date or date.today().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO usage_logs(app_name, usage_minutes, logged_date)
            VALUES (?, ?, ?)
            """,
            (app_name.strip(), int(minutes), date_val),
        )


def delete_usage(entry_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM usage_logs WHERE id = ?", (entry_id,))
        return cur.rowcount > 0


def list_recent_usage(limit: int = 50):
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT id, app_name, usage_minutes, logged_date
            FROM usage_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]


def get_daily_goal_minutes() -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT daily_goal_minutes FROM detox_settings WHERE id = 1"
        )
        row = cur.fetchone()
        return int(row[0]) if row else 120


def set_daily_goal_minutes(minutes: int) -> None:
    m = max(1, int(minutes))
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE detox_settings SET daily_goal_minutes = ? WHERE id = 1
            """,
            (m,),
        )


def today_total_minutes() -> int:
    d = date.today().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT COALESCE(SUM(usage_minutes), 0)
            FROM usage_logs WHERE logged_date = ?
            """,
            (d,),
        )
        return int(cur.fetchone()[0])


def weekly_app_totals(limit: int = 8):
    start = (date.today() - timedelta(days=6)).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT app_name, SUM(usage_minutes) AS total
            FROM usage_logs
            WHERE logged_date >= ?
            GROUP BY app_name
            ORDER BY total DESC
            LIMIT ?
            """,
            (start, limit),
        )
        return [{"app_name": row["app_name"], "total": int(row["total"])} for row in cur]


def all_usage_rows_for_cli():
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT id, app_name, usage_minutes, logged_date FROM usage_logs ORDER BY id
            """
        )
        return cur.fetchall()


if __name__ == "__main__":
    init_db()
    print("Database created successfully")
