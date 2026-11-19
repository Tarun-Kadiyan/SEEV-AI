import sqlite3, hashlib, os, json
from pathlib import Path

DB_PATH = Path(__file__).with_name("seev.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def _hash(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000)
    return salt.hex() + "$" + digest.hex()

def _verify(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        return _hash(password, bytes.fromhex(salt_hex)).split("$",1)[1] == digest_hex
    except Exception:
        return False

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, role TEXT NOT NULL, company TEXT, created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, mode TEXT NOT NULL,
            filename TEXT, job_title TEXT, score REAL, jd_text TEXT, result_json TEXT, created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id))""")
        con.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, analysis_id INTEGER,
            feedback TEXT, created_at TEXT NOT NULL)""")

def create_user(name, email, password, role, company=""):
    try:
        with connect() as con:
            con.execute("INSERT INTO users(name,email,password_hash,role,company,created_at) VALUES(?,?,?,?,?,datetime('now'))",
                        (name.strip(), email.strip().lower(), _hash(password), role, company))
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

def authenticate_user(email, password):
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if row and _verify(password, row["password_hash"]):
        return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"], "company": row["company"]}
    return None

def save_analysis(user_id, mode, filename, score, jd_text, result, job_title=""):
    with connect() as con:
        cur = con.execute("""INSERT INTO analyses(user_id,mode,filename,job_title,score,jd_text,result_json,created_at)
            VALUES(?,?,?,?,?,?,?,datetime('now'))""",
            (user_id, mode, filename, job_title, score, jd_text, json.dumps(result)))
        return cur.lastrowid

def get_user_history(user_id):
    with connect() as con:
        rows = con.execute("SELECT id,mode,filename,job_title,score,created_at FROM analyses WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    return [dict(r) for r in rows]

def get_company_analyses(user_id):
    with connect() as con:
        rows = con.execute("SELECT filename AS Candidate, job_title AS Role, score AS Match, created_at AS Date FROM analyses WHERE user_id=? AND mode='Company' ORDER BY id DESC LIMIT 100", (user_id,)).fetchall()
    return [dict(r) for r in rows]

def save_feedback(user_id, analysis_id, feedback):
    with connect() as con:
        con.execute("INSERT INTO feedback(user_id,analysis_id,feedback,created_at) VALUES(?,?,?,datetime('now'))",
                    (user_id, analysis_id, feedback))

def get_analysis_details(user_id, analysis_id):
    with connect() as con:
        row=con.execute('SELECT * FROM analyses WHERE user_id=? AND id=?',(user_id,analysis_id)).fetchone()
    if not row: return None
    record=dict(row)
    try: record['result']=json.loads(record.get('result_json') or '{}')
    except (ValueError,TypeError): record['result']={}
    return record

def get_history_details(user_id, mode=None):
    with connect() as con:
        if mode:
            rows=con.execute('SELECT * FROM analyses WHERE user_id=? AND mode=? ORDER BY id DESC',(user_id,mode)).fetchall()
        else:
            rows=con.execute('SELECT * FROM analyses WHERE user_id=? ORDER BY id DESC',(user_id,)).fetchall()
    return [dict(row) for row in rows]
