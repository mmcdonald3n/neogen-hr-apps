import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional

DB_PATH = Path("data/interview_feedback.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requisition TEXT,
        candidate TEXT,
        interviewer TEXT,
        rating INTEGER,
        comments TEXT,
        attachments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def insert_feedback(req: str, cand: str, interviewer: str, rating: int, comments: str, attachments: str = "") -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO feedback (requisition, candidate, interviewer, rating, comments, attachments)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (req, cand, interviewer, rating, comments, attachments))
    conn.commit()
    row_id = c.lastrowid
    conn.close()
    return row_id


def fetch_all() -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, requisition, candidate, interviewer, rating, comments, attachments, created_at FROM feedback ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows
