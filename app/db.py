import sqlite3
from typing import List, Dict

DB_FILE = "db/tasks.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def save_task(title: str, due_date: str, details: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, due_date, details) VALUES (?, ?, ?)",
        (title, due_date, details),
    )
    conn.commit()
    conn.close()


def get_all_tasks() -> List[Dict]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, due_date, details, created_at FROM tasks ORDER BY due_date"
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "title": r[1],
            "due_date": r[2],
            "details": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]
