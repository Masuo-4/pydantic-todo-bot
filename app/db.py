import sqlite3
from typing import List, Dict
from datetime import datetime

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
    cur.execute("INSERT INTO tasks (title, due_date, details) VALUES (?, ?, ?)", (title, due_date, details))
    conn.commit()
    conn.close()

def get_all_tasks(sort: str = "due") -> List[Dict]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    if sort == "created":
        order = "created_at DESC"
    elif sort == "created_asc":
        order = "created_at ASC"
    else:
        order = "due_date IS NULL, due_date ASC"

    cur.execute(f"SELECT id, title, due_date, details, created_at FROM tasks ORDER BY {order}")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "due_date": r[2],
            "details": r[3],
            "created_at": r[4],
            "is_expired": bool(r[2]) and datetime.now() > datetime.strptime(r[2], "%Y-%m-%d %H:%M")
        }
        for r in rows
    ]

def delete_task(task_id: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
