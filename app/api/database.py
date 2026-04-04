import sqlite3
import sqlite_vec
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent / "db" / "database.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                creation_date TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES cases(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                text_content TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES cases(id)
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks USING vec0(
                chunk_id INTEGER PRIMARY KEY,
                document_id INTEGER,
                case_id INTEGER,
                text_content TEXT,
                embedding float[768]
            )
        """)
        conn.commit()

def insert_case(title: str, creation_date: str) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cases (title, creation_date) VALUES (?, ?)", (title, creation_date))
        conn.commit()
        return {"id": cursor.lastrowid, "title": title, "creation_date": creation_date}

def get_cases() -> list[dict]:
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM cases ORDER BY id ASC").fetchall()]

def insert_message(case_id: int, role: str, content: str) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (case_id, role, content) VALUES (?, ?, ?)", (case_id, role, content))
        conn.commit()
        return {"id": cursor.lastrowid, "case_id": case_id, "role": role, "content": content}

def get_messages(case_id: int) -> list[dict]:
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM messages WHERE case_id = ? ORDER BY id ASC", (case_id,)).fetchall()]