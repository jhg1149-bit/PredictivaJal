import sqlite3, json
from pathlib import Path
DB=Path(__file__).resolve().parent.parent/"predictivajal.db"

def _conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS evaluations (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, machine_id TEXT, machine_type TEXT, irf REAL, level TEXT, payload TEXT)")
def save_result(result):
    init_db()
    with _conn() as c:
        c.execute("INSERT INTO evaluations(machine_id,machine_type,irf,level,payload) VALUES(?,?,?,?,?)",(result["machine_id"],result["machine_type"],result["irf"],result["level"],json.dumps(result,ensure_ascii=False)))
def get_history(limit=500):
    init_db()
    with _conn() as c: rows=c.execute("SELECT * FROM evaluations ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return [dict(r) for r in rows]
def clear_history():
    init_db()
    with _conn() as c: c.execute("DELETE FROM evaluations")
