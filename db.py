import sqlite3

DB_NAME = "vault.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS passwords(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            site TEXT,
            username TEXT,
            password TEXT,
            category TEXT,
            favorite INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            site TEXT,
            username TEXT,
            password TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_password(user_id, site, username, password, category="", favorite=0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO passwords(user_id, site, username, password, category, favorite) VALUES(?,?,?,?,?,?)",
              (user_id, site, username, password, category, favorite))
    conn.commit()
    conn.close()

def get_passwords(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM passwords WHERE user_id = ?", (user_id,))
    data = c.fetchall()
    conn.close()
    return data

def delete_password(password_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM passwords WHERE id = ? AND user_id = ?", (password_id, user_id))
    conn.commit()
    conn.close()

def toggle_favorite(password_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT favorite FROM passwords WHERE id=? AND user_id=?", (password_id, user_id))
    fav = c.fetchone()[0]
    fav = 0 if fav == 1 else 1
    c.execute("UPDATE passwords SET favorite=? WHERE id=? AND user_id=?", (fav, password_id, user_id))
    conn.commit()
    conn.close()

def get_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM passwords WHERE user_id=?", (user_id,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM passwords WHERE user_id=? AND length(password)<8", (user_id,))
    weak = c.fetchone()[0]
    conn.close()
    return total, weak

def add_to_history(user_id, site, username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history(user_id, site, username, password) VALUES(?,?,?,?)",
              (user_id, site, username, password))
    conn.commit()
    conn.close()
