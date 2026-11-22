import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "test_cases.db"

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS generation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement TEXT NOT NULL,
                feature_summary TEXT DEFAULT '',
                assumptions_json TEXT DEFAULT '[]',
                test_cases_json TEXT NOT NULL,
                model TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

def save_run(requirement, feature_summary, assumptions, test_cases, model=""):
    with connect() as conn:
        cur = conn.execute("""
            INSERT INTO generation_runs
            (requirement, feature_summary, assumptions_json, test_cases_json, model)
            VALUES (?, ?, ?, ?, ?)
        """, (requirement, feature_summary, json.dumps(assumptions, ensure_ascii=False),
              json.dumps(test_cases, ensure_ascii=False), model))
        conn.commit()
        return cur.lastrowid

def list_runs():
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, requirement, feature_summary, model, created_at
            FROM generation_runs ORDER BY id DESC
        """).fetchall()
        return [dict(r) for r in rows]

def get_run(run_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM generation_runs WHERE id=?", (run_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["assumptions"] = json.loads(item.pop("assumptions_json") or "[]")
        item["test_cases"] = json.loads(item.pop("test_cases_json") or "[]")
        return item

def delete_run(run_id):
    with connect() as conn:
        conn.execute("DELETE FROM generation_runs WHERE id=?", (run_id,))
        conn.commit()
